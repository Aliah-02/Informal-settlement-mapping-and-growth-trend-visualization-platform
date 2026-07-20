"""
Hardcoded sample data for the CampusLink portal.

Database usage is optional for this teaching project — views pass these
lists/dicts into templates so students can focus on template inheritance,
includes, filters, tags, loops, and conditionals.
"""

from datetime import date

CURRENT_USER = {
    "name": "Amina Mwinyi",
    "role": "Registrar",
    "email": "amina.mwinyi@campuslink.edu",
    "department": "Academic Affairs",
    "phone": "+255 713 456 789",
    "joined": date(2019, 3, 12),
    "bio": "Coordinates student records, course catalogues, and faculty onboarding across campus faculties.",
}

STUDENTS = [
    {
        "id": "STU-2401",
        "name": "Juma Hassan",
        "email": "juma.hassan@student.campuslink.edu",
        "department": "Computer Science",
        "year": 3,
        "gpa": 3.72,
        "status": "active",
        "enrolled": date(2023, 9, 4),
    },
    {
        "id": "STU-2402",
        "name": "Neema Kimaro",
        "email": "neema.kimaro@student.campuslink.edu",
        "department": "Business Administration",
        "year": 2,
        "gpa": 3.41,
        "status": "active",
        "enrolled": date(2024, 9, 2),
    },
    {
        "id": "STU-2403",
        "name": "Daniel Okello",
        "email": "daniel.okello@student.campuslink.edu",
        "department": "Civil Engineering",
        "year": 4,
        "gpa": 2.95,
        "status": "probation",
        "enrolled": date(2022, 9, 5),
    },
    {
        "id": "STU-2404",
        "name": "Fatuma Said",
        "email": "fatuma.said@student.campuslink.edu",
        "department": "Public Health",
        "year": 1,
        "gpa": 3.88,
        "status": "active",
        "enrolled": date(2025, 9, 1),
    },
    {
        "id": "STU-2405",
        "name": "Brian Mwangi",
        "email": "brian.mwangi@student.campuslink.edu",
        "department": "Computer Science",
        "year": 2,
        "gpa": 3.15,
        "status": "inactive",
        "enrolled": date(2024, 9, 2),
    },
    {
        "id": "STU-2406",
        "name": "Grace Lyimo",
        "email": "grace.lyimo@student.campuslink.edu",
        "department": "Education",
        "year": 3,
        "gpa": 3.56,
        "status": "active",
        "enrolled": date(2023, 9, 4),
    },
]

COURSES = [
    {
        "code": "CS301",
        "title": "Advanced Web Frameworks",
        "department": "Computer Science",
        "credits": 4,
        "lecturer": "Dr. Halima Nyerere",
        "enrolled": 48,
        "capacity": 60,
        "term": "Semester 1",
    },
    {
        "code": "BA210",
        "title": "Organizational Behaviour",
        "department": "Business Administration",
        "credits": 3,
        "lecturer": "Prof. Joseph Kitange",
        "enrolled": 72,
        "capacity": 80,
        "term": "Semester 1",
    },
    {
        "code": "CE405",
        "title": "Structural Analysis II",
        "department": "Civil Engineering",
        "credits": 4,
        "lecturer": "Eng. Patricia Moyo",
        "enrolled": 35,
        "capacity": 40,
        "term": "Semester 2",
    },
    {
        "code": "PH120",
        "title": "Epidemiology Foundations",
        "department": "Public Health",
        "credits": 3,
        "lecturer": "Dr. Samuel Chirwa",
        "enrolled": 55,
        "capacity": 70,
        "term": "Semester 1",
    },
    {
        "code": "ED330",
        "title": "Curriculum Design",
        "department": "Education",
        "credits": 3,
        "lecturer": "Dr. Rose Kibwana",
        "enrolled": 40,
        "capacity": 45,
        "term": "Semester 2",
    },
]

LECTURERS = [
    {
        "id": "LEC-101",
        "name": "Dr. Halima Nyerere",
        "email": "h.nyerere@campuslink.edu",
        "department": "Computer Science",
        "courses": 3,
        "office": "Block C · 214",
        "status": "full-time",
    },
    {
        "id": "LEC-102",
        "name": "Prof. Joseph Kitange",
        "email": "j.kitange@campuslink.edu",
        "department": "Business Administration",
        "courses": 2,
        "office": "Block A · 108",
        "status": "full-time",
    },
    {
        "id": "LEC-103",
        "name": "Eng. Patricia Moyo",
        "email": "p.moyo@campuslink.edu",
        "department": "Civil Engineering",
        "courses": 4,
        "office": "Block E · 301",
        "status": "full-time",
    },
    {
        "id": "LEC-104",
        "name": "Dr. Samuel Chirwa",
        "email": "s.chirwa@campuslink.edu",
        "department": "Public Health",
        "courses": 2,
        "office": "Block B · 012",
        "status": "part-time",
    },
    {
        "id": "LEC-105",
        "name": "Dr. Rose Kibwana",
        "email": "r.kibwana@campuslink.edu",
        "department": "Education",
        "courses": 3,
        "office": "Block D · 220",
        "status": "full-time",
    },
]

DEPARTMENTS = [
    {
        "code": "CS",
        "name": "Computer Science",
        "faculty": "Science & Technology",
        "students": 420,
        "lecturers": 18,
        "courses": 36,
        "head": "Dr. Halima Nyerere",
    },
    {
        "code": "BA",
        "name": "Business Administration",
        "faculty": "Business & Economics",
        "students": 510,
        "lecturers": 22,
        "courses": 28,
        "head": "Prof. Joseph Kitange",
    },
    {
        "code": "CE",
        "name": "Civil Engineering",
        "faculty": "Engineering",
        "students": 310,
        "lecturers": 15,
        "courses": 32,
        "head": "Eng. Patricia Moyo",
    },
    {
        "code": "PH",
        "name": "Public Health",
        "faculty": "Health Sciences",
        "students": 280,
        "lecturers": 12,
        "courses": 24,
        "head": "Dr. Samuel Chirwa",
    },
    {
        "code": "ED",
        "name": "Education",
        "faculty": "Humanities",
        "students": 360,
        "lecturers": 16,
        "courses": 22,
        "head": "Dr. Rose Kibwana",
    },
]

RECENT_ACTIVITY = [
    {"actor": "Juma Hassan", "action": "enrolled in", "target": "CS301", "when": "2 hours ago"},
    {"actor": "Dr. Halima Nyerere", "action": "updated grades for", "target": "CS301", "when": "5 hours ago"},
    {"actor": "Neema Kimaro", "action": "submitted appeal for", "target": "BA210", "when": "Yesterday"},
    {"actor": "Academic Affairs", "action": "published timetable for", "target": "Semester 1", "when": "2 days ago"},
]

SETTINGS = {
    "notifications_email": True,
    "notifications_sms": False,
    "theme": "campus",
    "language": "English",
    "timezone": "Africa/Dar_es_Salaam",
    "records_per_page": 25,
}
