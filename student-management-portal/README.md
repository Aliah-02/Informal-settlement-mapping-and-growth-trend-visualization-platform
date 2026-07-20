# CampusLink — Student Management Portal

A teaching-focused Django project that demonstrates **advanced Django templates and template reusability** through a working Student Management Portal interface.

## Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| 1 | Complete source code (GitHub) | This repository folder: `student-management-portal/` |
| 2 | Presentation slides | [`docs/presentation.html`](docs/presentation.html) — open in a browser; use ←/→ keys |
| 3 | Teaching notes / handout | [`TEACHING_NOTES.md`](TEACHING_NOTES.md) |
| 4 | README (setup + description) | This file |
| 5 | Live demonstration | Run the portal locally and walk through the checklist below (or see recorded demo in the PR) |

## Project description

CampusLink is a Student Management Portal used to **teach and demonstrate** Django template concepts:

- Template inheritance, base templates, and blocks
- Extending vs including templates
- Built-in tags and filters
- Conditionals, loops, `{% url %}`, and `{% static %}`
- Shared navbar, sidebar, header, and footer
- Dynamic tables, statistics cards, and navigation highlighting

### Pages

| Page | URL name | Path |
|------|----------|------|
| Dashboard | `dashboard` | `/` |
| Students | `students` | `/students/` |
| Courses | `courses` | `/courses/` |
| Lecturers | `lecturers` | `/lecturers/` |
| Departments | `departments` | `/departments/` |
| Profile | `profile` | `/profile/` |
| Settings | `settings` | `/settings/` |

Sample data is **hardcoded** in `campus/data.py` (database optional).

## Setup instructions

### Requirements

- Python 3.10+ (3.12 recommended)
- `pip` and a virtual environment

### Install and run

```bash
cd student-management-portal
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Presentation slides

```bash
# macOS
open docs/presentation.html

# Linux
xdg-open docs/presentation.html

# Or simply open the file in Chrome / Firefox / Edge
```

Navigate with **arrow keys**, **Space**, or the on-screen Prev/Next buttons.

## Live demonstration checklist

Demonstrate these features in the running app:

1. **Base template / inheritance** — every page shares the same shell; only the content area changes
2. **Shared navbar, sidebar, header, footer** — visible on all pages (`templates/includes/`)
3. **Includes** — stats cards reuse `includes/stats_card.html`
4. **Static CSS / JS / images** — styled UI, mobile menu JS, logo + avatar SVGs
5. **Dynamic statistics cards** — Dashboard and list pages
6. **Dynamic tables** — Students, Courses, Lecturers, Departments
7. **Navigation highlighting** — active sidebar link updates as you navigate
8. **Filters** — GPA `floatformat`, enrolment `date`, name `upper` / email `lower`
9. **Template tags** — `{% url %}` links, `{% static %}` assets, `{% if %}` / `{% for %}`
10. **Code view (optional)** — open `templates/base.html` and show that one layout serves all pages

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
│   └── campus/             # Page templates that {% extends %} base
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/             # logo.svg, avatar.svg
├── docs/
│   └── presentation.html   # Presentation slides
├── manage.py
├── requirements.txt
├── TEACHING_NOTES.md       # Teaching notes / handout
└── README.md
```

### Static files configuration (`config/settings.py`)

| Setting | Purpose |
|---------|---------|
| `STATIC_URL` | URL prefix (`/static/`) |
| `STATICFILES_DIRS` | Project-level static folder used in development |
| `STATIC_ROOT` | Destination for `collectstatic` in production |

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.svg' %}" alt="Logo">
```

## Peer teaching

See [`TEACHING_NOTES.md`](TEACHING_NOTES.md) for theory (inheritance vs include, tags, filters, folder layout) and a timed demo script. Use [`docs/presentation.html`](docs/presentation.html) for the slide talk track.
