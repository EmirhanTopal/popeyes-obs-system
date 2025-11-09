from django.shortcuts import render, redirect
from accounts.models import SimpleUser
from departments.models import Department, DepartmentCourse, DepartmentStatistic
from courses.models import Course

def dashboard(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    # HOD hangi bölümün başkanı?
    department = Department.objects.filter(head_user__username=username).first()
    if not department:
        return render(request, "hod/no_department.html")

    # ders ekleme
    if request.method == "POST":
        course_id = request.POST.get("course")
        semester = request.POST.get("semester") or 1
        is_mandatory = True if request.POST.get("is_mandatory") == "on" else False
        if course_id:
            DepartmentCourse.objects.create(
                department=department,
                course_id=course_id,
                semester=semester,
                is_mandatory=is_mandatory
            )
        return redirect("hod:dashboard")

    stats, _ = DepartmentStatistic.objects.get_or_create(department=department)
    courses = Course.objects.all()
    dept_courses = DepartmentCourse.objects.filter(department=department).select_related("course")

    return render(request, "hod/dashboard.html", {
        "username": username,
        "department": department,
        "stats": stats,
        "courses": courses,
        "dept_courses": dept_courses,
    })
