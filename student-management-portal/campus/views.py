from django.shortcuts import render

from . import data


def dashboard(request):
    active_students = [s for s in data.STUDENTS if s["status"] == "active"]
    context = {
        "page_title": "Dashboard",
        "page_subtitle": "Campus overview and recent activity",
        "stats": [
            {"label": "Students", "value": len(data.STUDENTS), "hint": f"{len(active_students)} active", "tone": "teal"},
            {"label": "Courses", "value": len(data.COURSES), "hint": "This term", "tone": "ink"},
            {"label": "Lecturers", "value": len(data.LECTURERS), "hint": "Across faculties", "tone": "amber"},
            {"label": "Departments", "value": len(data.DEPARTMENTS), "hint": "Campus-wide", "tone": "slate"},
        ],
        "recent_activity": data.RECENT_ACTIVITY,
        "students_preview": data.STUDENTS[:4],
        "courses_preview": data.COURSES[:4],
    }
    return render(request, "campus/dashboard.html", context)


def students(request):
    context = {
        "page_title": "Students",
        "page_subtitle": "Enrolment records and academic standing",
        "students": data.STUDENTS,
        "active_count": sum(1 for s in data.STUDENTS if s["status"] == "active"),
        "probation_count": sum(1 for s in data.STUDENTS if s["status"] == "probation"),
    }
    return render(request, "campus/students.html", context)


def courses(request):
    context = {
        "page_title": "Courses",
        "page_subtitle": "Catalogue, capacity, and teaching staff",
        "courses": data.COURSES,
        "total_enrolled": sum(c["enrolled"] for c in data.COURSES),
        "total_capacity": sum(c["capacity"] for c in data.COURSES),
    }
    return render(request, "campus/courses.html", context)


def lecturers(request):
    context = {
        "page_title": "Lecturers",
        "page_subtitle": "Faculty directory and teaching load",
        "lecturers": data.LECTURERS,
        "full_time": sum(1 for l in data.LECTURERS if l["status"] == "full-time"),
        "part_time": sum(1 for l in data.LECTURERS if l["status"] == "part-time"),
    }
    return render(request, "campus/lecturers.html", context)


def departments(request):
    context = {
        "page_title": "Departments",
        "page_subtitle": "Faculties, heads of department, and headcount",
        "departments": data.DEPARTMENTS,
        "total_students": sum(d["students"] for d in data.DEPARTMENTS),
    }
    return render(request, "campus/departments.html", context)


def profile(request):
    context = {
        "page_title": "Profile",
        "page_subtitle": "Your account details",
        "profile": data.CURRENT_USER,
    }
    return render(request, "campus/profile.html", context)


def settings(request):
    context = {
        "page_title": "Settings",
        "page_subtitle": "Preferences for the CampusLink portal",
        "settings": data.SETTINGS,
    }
    return render(request, "campus/settings.html", context)
