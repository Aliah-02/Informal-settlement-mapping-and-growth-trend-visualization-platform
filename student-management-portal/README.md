# CampusLink — Student Management Portal

A teaching-focused Django project that demonstrates **advanced Django templates and template reusability** through a working Student Management Portal interface.

## Pages

| Page | URL name | Path |
|------|----------|------|
| Dashboard | `dashboard` | `/` |
| Students | `students` | `/students/` |
| Courses | `courses` | `/courses/` |
| Lecturers | `lecturers` | `/lecturers/` |
| Departments | `departments` | `/departments/` |
| Profile | `profile` | `/profile/` |
| Settings | `settings` | `/settings/` |

## What this project demonstrates

- **Base template** (`templates/base.html`) — shared HTML shell
- **Template inheritance** — every page uses `{% extends "base.html" %}`
- **Blocks** — `{% block title %}`, `{% block content %}`, `{% block extra_css %}`, `{% block extra_js %}`
- **Includes** — shared navbar, sidebar, header, footer, and stats cards
- **Static CSS / JavaScript / images** — under `static/`
- **Dynamic tables & statistics cards** — rendered with loops and includes
- **Navigation highlighting** — active link based on the current URL name
- **Template filters & tags** — `date`, `floatformat`, `title`, `truncatewords`, `url`, `static`, `now`, conditionals, loops

Sample data is **hardcoded** in `campus/data.py` (database optional).

## Quick start

```bash
cd student-management-portal
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Folder organization (production-style)

```
student-management-portal/
├── config/                 # Project settings & root URLconf
│   ├── settings.py         # TEMPLATES DIRS, STATICFILES_DIRS, STATIC_ROOT
│   └── urls.py
├── campus/                 # App: views, urls, sample data, context processor
├── templates/
│   ├── base.html           # Base template (inheritance root)
│   ├── includes/           # Reusable partials ({% include %})
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── header.html
│   │   ├── footer.html
│   │   └── stats_card.html
│   └── campus/             # Page templates that {% extends %} base
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/             # logo.svg, avatar.svg
├── manage.py
├── requirements.txt
├── TEACHING_NOTES.md       # Peer-teaching explanations
└── README.md
```

### Static files configuration (see `config/settings.py`)

| Setting | Purpose |
|---------|---------|
| `STATIC_URL` | URL prefix (`/static/`) |
| `STATICFILES_DIRS` | Project-level static folder used in development |
| `STATIC_ROOT` | Destination for `collectstatic` in production |

In templates:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.svg' %}" alt="Logo">
```

## Peer teaching

See [`TEACHING_NOTES.md`](TEACHING_NOTES.md) for explanations of inheritance vs include, common tags/filters, and why this structure reduces duplication.
