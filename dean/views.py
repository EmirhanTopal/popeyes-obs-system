import os
from django.db.models import Q
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from departments.models import Department, DepartmentCourse
from courses.models import CourseGrade, ComponentLearningProgramRelation

from students.models import Student
from .models import Dean
from .forms import TeacherForm
from outcomes.models import ProgramOutcome, StudentProgramOutcomeScore
from outcomes.management.commands.import_outcomes import OutcomeImporter
from outcomes.services import compute_and_save_student_program_outcomes

def is_dean_logged(request):
    return request.session.get("role") == "DEAN"

def dekan_dashboard(request):
    if not is_dean_logged(request):
        return redirect("login")

    username = request.session.get("username")
    dean = Dean.objects.filter(teacher__user__username=username).select_related("faculty").first()
    if not dean:
        messages.error(request, "Dekan profili bulunamadı.")
        return redirect("login")

    if request.method == "POST" and request.FILES.get("docx_file"):
        docx_file = request.FILES["docx_file"]
        program_type = request.POST.get("program_type", "auto")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            for chunk in docx_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        importer = OutcomeImporter()

        if program_type == "auto":
            outcomes, detected_program = importer.parse_docx_file(tmp_path)
        else:
            outcomes, detected_program = importer.parse_docx_file(tmp_path, program_type)

        department = Department.objects.filter(
            code__iexact=detected_program,
            faculty=dean.faculty
        ).first()

        if not department:
            messages.error(request, f"❌ '{detected_program}' adlı bölüm bulunamadı.")
        elif not outcomes:
            messages.error(request, "❌ Dosyada geçerli outcome bulunamadı.")
        else:
            count = 0
            for outcome in outcomes:
                ProgramOutcome.objects.update_or_create(
                    department=department,
                    code=outcome["number"],
                    defaults={"description": outcome["description"]}
                )
                count += 1
            messages.success(
                request,
                f"✅ {count} outcome başarıyla yüklendi! ({department.code} - {department.name})"
            )

        os.unlink(tmp_path)
        return redirect("dean:dashboard")

    departments = Department.objects.filter(faculty=dean.faculty)
    department_courses = DepartmentCourse.objects.filter(department__faculty=dean.faculty)

    department_stats = []
    total_outcomes = 0
    for dep in departments:
        count = ProgramOutcome.objects.filter(department=dep).count()
        total_outcomes += count
        department_stats.append({
            "code": dep.code,
            "name": dep.name,
            "count": count
        })

    context = {
        "username": username,
        "dean": dean,
        "departments": departments,
        "department_courses": department_courses,
        "department_stats": department_stats,
        "total_outcomes": total_outcomes,
    }

    return render(request, "dean/dashboard.html", context)



def student_po_report(request, student_id):
    if not is_dean_logged(request):
        return redirect("login")

    student = get_object_or_404(Student, id=student_id)

    compute_and_save_student_program_outcomes(student)

    scores = (
        StudentProgramOutcomeScore.objects
        .filter(student=student)
        .select_related("program_outcome")
        .order_by("program_outcome__id")
    )

    rows = []
    for s in scores:
        rows.append({
            "po_id": s.program_outcome.id,
            "code": s.program_outcome.code,
            "description": s.program_outcome.description,
            "coverage": round(s.coverage, 2),
            "score": round(s.score, 2),
        })

    return render(request, "dean/student_po_report.html", {
        "student": student,
        "rows": rows,
    })

def student_list(request):
    if not is_dean_logged(request):
        return redirect("login")

    username = request.session.get("username")
    dean = Dean.objects.filter(teacher__user__username=username).select_related("faculty").first()
    if not dean:
        messages.error(request, "Dekan profili bulunamadı.")
        return redirect("login")

    dept_id = request.GET.get("department")
    q = request.GET.get("q", "").strip()

    qs = (
        Student.objects
        .filter(departments__faculty=dean.faculty)
        .distinct()
    )

    if dept_id:
        qs = qs.filter(departments__id=dept_id)

    
    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(student_no__icontains=q)
        )

    departments = Department.objects.filter(faculty=dean.faculty)
    selected_department = Department.objects.filter(id=dept_id).first() if dept_id else None

    context = {
        "username": username,
        "dean": dean,
        "departments": departments,
        "selected_department": selected_department,
        "students": qs,
        "q": q,
        "department_courses": [],
        "department_stats": [],
        "total_outcomes": ProgramOutcome.objects.filter(department__faculty=dean.faculty).count(),
    }
    print("STUDENT COUNT:", qs.count())

    return render(request, "dean/dashboard.html", context)

def add_teacher(request):
    if not is_dean_logged(request):
        return redirect("login")

    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.save()
            messages.success(request, "Öğretmen başarıyla eklendi.")
            return redirect("dean:add_teacher")
    else:
        form = TeacherForm()

    return render(request, "dean/add_teacher.html", {"form": form})


def compute_student_po_scores(student, normalize=True):

    results = {}

    all_pos = ProgramOutcome.objects.filter(department__in=student.departments.all())
    for po in all_pos:
        results[po.id] = {
            "code": po.code,
            "description": po.description,
            "weight_sum": 0.0,
            "score_sum": 0.0,
            "score": 0.0,
        }

    grades = CourseGrade.objects.filter(enrollment__student=student).select_related(
        "component", "component__course"
    )

    for grade in grades:
        comp = grade.component
        score = float(grade.score or 0)

        relations = ComponentLearningProgramRelation.objects.filter(component=comp).select_related(
            "learning_outcome", "program_outcome"
        )

        for rel in relations:
            po = rel.program_outcome
            if not po:
                continue

            if po.id not in results:
                results[po.id] = {
                    "code": po.code,
                    "description": po.description,
                    "weight_sum": 0.0,
                    "score_sum": 0.0,
                    "score": 0.0,
                }


            effective_weight = (rel.learning_weight / 100.0) * (rel.program_weight / 100.0)


            component_weight = comp.weight / 100.0
            combined_weight = effective_weight * component_weight

            results[po.id]["weight_sum"] += combined_weight
            results[po.id]["score_sum"] += score * combined_weight

    for po_id, item in results.items():
        total_weight = item["weight_sum"]
        if total_weight > 0:
            normalized_score = (item["score_sum"] / total_weight)
            item["score"] = round(normalized_score if not normalize else normalized_score, 2)
            item["weight_sum"] = round(total_weight * 100, 2)
        else:
            item["score"] = 0.0
            item["weight_sum"] = 0.0

    return results
