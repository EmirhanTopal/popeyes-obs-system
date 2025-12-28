# outcomes/services.py
from collections import defaultdict

from courses.models import (
    Enrollment,              # Öğrencinin derse kayıtları
    CourseAssessmentComponent,     # Vize/Final/Proje vb.
    CourseGrade,                   # Bileşen notu
    ComponentLearningRelation,     # Component -> LO (%)
    CourseOffering,
)
from outcomes.models import ProgramOutcome, LearningOutcome, StudentProgramOutcomeScore
from courses.models import LearningProgramRelation

def compute_and_save_student_program_outcomes(student):
    results = compute_student_program_outcomes(student)

    for po_id, item in results.items():
        StudentProgramOutcomeScore.objects.update_or_create(
            student=student,
            program_outcome_id=po_id,
            defaults={
                "score": item["score"],
                "coverage": item["coverage"],
            }
        )

    return

def _safe_pct_denominator(total: float) -> float:
    """
    Yüzde toplamları 100'ü geçerse normalize etmek için payda.
    - Toplam <= 100 ise 100 baz alınır (yani artırma yok).
    - Toplam  > 100 ise toplam baz alınır (yani bölünerek normalize edilir).
    """
    try:
        total = float(total or 0.0)
    except Exception:
        total = 0.0
    return 100.0 if total <= 100.0 else total


def compute_student_learning_outcomes(student):
    """
    1) LO skorlarını hesapla.
       Her component için:
         grade * (component->LO_weight / denom)
       (component.weight kullanılmaz)
    Dönen: {lo_id: score_float}
    """
    enrollments = (
        Enrollment.objects
        .filter(student=student, status=Enrollment.Status.ENROLLED)
        .select_related("offering", "offering__course")
    )

    if not enrollments.exists():
        return {}

    grades = CourseGrade.objects.filter(enrollment__in=enrollments)
    grade_map = {(int(g.enrollment_id), int(g.component_id)): float(g.score or 0.0)
                 for g in grades}

    enr_by_offering = {e.offering_id: e for e in enrollments}
    lo_scores = defaultdict(float)

    components = CourseAssessmentComponent.objects.filter(
        course__in=[e.offering.course for e in enrollments]
    )

    for comp in components:
        enr = next(
            (e for e in enrollments if e.offering.course_id == comp.course_id),
            None
        )
        if not enr:
            continue

        grade = grade_map.get((enr.id, comp.id))
        if grade is None:
            continue

        rel_qs = ComponentLearningRelation.objects.filter(component=comp)
        total_lo_w = sum((r.weight or 0.0) for r in rel_qs)
        denom = _safe_pct_denominator(total_lo_w)

        for rel in rel_qs:
            lw_part = float(rel.weight or 0.0) / denom
            lo_scores[rel.learning_outcome_id] += grade * lw_part

    return dict(lo_scores)


def compute_student_program_outcomes(student):

    enrollments = (
        Enrollment.objects
        .filter(student=student, status=Enrollment.Status.ENROLLED)
        .select_related("offering", "offering__course")
    )

    student_departments = student.departments.all()

    if not enrollments.exists():
        return {}

    grades = CourseGrade.objects.filter(enrollment__in=enrollments)
    grade_map = {
        (g.enrollment_id, g.component_id): float(g.score or 0.0)
        for g in grades
    }

    lo_scores = defaultdict(float)
    lo_weights = defaultdict(float)

    for enrollment in enrollments:
        course = enrollment.offering.course

        components = CourseAssessmentComponent.objects.filter(offering=enrollment.offering)

        for comp in components:
            score = grade_map.get((enrollment.id, comp.id))
            if score is None:
                continue

            relations = ComponentLearningRelation.objects.filter(component=comp)

            for rel in relations:
                lw = float(rel.weight or 0.0)
                if lw > 1:
                    lw /= 100.0

                lo_scores[rel.learning_outcome_id] += score * lw
                lo_weights[rel.learning_outcome_id] += lw * 100

    for lo_id, total_w in lo_weights.items():
        if total_w > 100:
            lo_scores[lo_id] /= (total_w / 100.0)

    po_scores = defaultdict(float)
    po_weights = defaultdict(float)

    for lo_id, lo_score in lo_scores.items():
        mappings = LearningProgramRelation.objects.filter(
            learning_outcome_id=lo_id,
            program_outcome__department__in=student_departments
        )

        for m in mappings:
            pw = float(m.weight or 0.0)
            if pw > 1:
                pw /= 100.0

            po_scores[m.program_outcome_id] += lo_score * pw
            po_weights[m.program_outcome_id] += pw * 100

    for po_id, total_w in po_weights.items():
        if total_w > 100:
            po_scores[po_id] /= (total_w / 100.0)

    results = {}
    for po_id, score in po_scores.items():
        po = ProgramOutcome.objects.get(id=po_id)
        results[po_id] = {
            "code": po.code,
            "description": po.description,
            "coverage": round(po_weights[po_id], 2),
            "score": round(score, 2),
        }

    ordered_results = {}
    all_pos = ProgramOutcome.objects.filter(
        department__in=student_departments
    ).order_by("id")

    for po in all_pos:
        ordered_results[po.id] = results.get(po.id, {
            "code": po.code,
            "description": po.description,
            "coverage": 0.0,
            "score": 0.0,
        })

    return ordered_results
