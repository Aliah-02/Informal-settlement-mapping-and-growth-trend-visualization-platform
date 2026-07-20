# Peer Teaching Notes — Advanced Django Templates

Use this document when presenting CampusLink. Each section maps to a concept the group must teach, with pointers into this project.

---

## 1. Why template inheritance is important

Without inheritance, every page would repeat the same `<html>`, sidebar, navbar, footer, and CSS/JS links. That causes:

- **Duplication** — one design change means editing many files
- **Inconsistency** — pages drift apart over time
- **Harder onboarding** — new pages must copy-paste large boilerplate

**Inheritance solves this:** define the shared layout once in `templates/base.html`, then let each page fill only the unique parts via `{% block content %}`.

**Demo:** open `templates/base.html` and any page under `templates/campus/`. Show that changing the brand name in the sidebar include updates *every* page.

---

## 2. Base templates, blocks, and extending

| Concept | In this project |
|---------|-----------------|
| **Base template** | `templates/base.html` |
| **Blocks** | `title`, `content`, `extra_css`, `extra_js` |
| **Extending** | `{% extends "base.html" %}` at the top of each page |

Child template pattern:

```django
{% extends "base.html" %}

{% block content %}
  <!-- page-specific markup only -->
{% endblock %}
```

Rules to remember:

1. `{% extends %}` must be the **first** template tag in the file.
2. Child templates should mostly override blocks — avoid redefining the whole document.
3. Empty blocks in the base (`{% block extra_css %}{% endblock %}`) are extension points for optional assets.

---

## 3. Difference between `include` and `extend`

| | `{% extends %}` | `{% include %}` |
|--|-----------------|-----------------|
| **Purpose** | Inherit a full page skeleton | Insert a reusable fragment |
| **Relationship** | Child *is a* specialized version of the base | Parent *embeds* a partial |
| **Typical use** | Whole pages (dashboard, students…) | Navbar, sidebar, footer, cards |
| **Blocks** | Child fills `{% block %}` regions | Included file is inserted as-is |
| **This project** | `templates/campus/*.html` | `templates/includes/*.html` |

**Analogy:** `extends` is like subclassing a layout class; `include` is like calling a helper component.

**Demo:**

- Extends → `templates/campus/students.html`
- Include → `{% include "includes/stats_card.html" with label=... value=... %}`

---

## 4. How includes improve maintainability

Shared pieces live in `templates/includes/`:

- `navbar.html` — top bar
- `sidebar.html` — primary navigation + brand
- `header.html` — page title / subtitle
- `footer.html` — copyright
- `stats_card.html` — reusable KPI card

Update the sidebar once → every page updates. Pass local variables with `with`:

```django
{% include "includes/stats_card.html" with label="Students" value=12 tone="teal" %}
```

---

## 5. Common built-in template tags

| Tag | Role | Example in project |
|-----|------|--------------------|
| `{% extends %}` | Inherit base | All campus pages |
| `{% block %}` | Overridable region | `content` in base |
| `{% include %}` | Embed partial | Sidebar, stats cards |
| `{% load %}` | Load tag/filter library | `{% load static %}`, `{% load humanize %}` |
| `{% static %}` | Resolve static file URL | CSS, JS, images |
| `{% url %}` | Reverse a named URL | Navigation links |
| `{% if %} / {% elif %} / {% else %}` | Conditionals | Student status badges |
| `{% for %} / {% empty %}` | Loops | Tables and activity lists |
| `{% now %}` | Current date/time | Header and footer |
| `{% widthratio %}` | Proportional math | Course enrolment meters |

---

## 6. Common template filters

Filters transform values with the pipe `|` operator.

| Filter | What it does | Example |
|--------|--------------|---------|
| `title` | Title-case text | `{{ page_title\|title }}` |
| `upper` / `lower` | Case transform | Student names / emails |
| `date` | Format dates | `{{ student.enrolled\|date:"M j, Y" }}` |
| `floatformat` | Round decimals | GPA display |
| `truncatewords` / `truncatechars` | Shorten text | Bio, course titles |
| `default` | Fallback if empty | Header title |
| `length` | Count items | `{{ students\|length }}` |
| `intcomma` | Thousands separators | Department headcounts (`humanize`) |
| `add` | Numeric adjust | Near-capacity checks |

**Demo idea:** change `floatformat:2` to `floatformat:1` on the students page and refresh.

---

## 7. Conditional statements and loops

**Conditionals** (`students.html`, `dashboard.html`):

```django
{% if student.status == "active" %}
  <span class="badge badge-active">Active</span>
{% elif student.status == "probation" %}
  <span class="badge badge-probation">Probation</span>
{% else %}
  <span class="badge badge-inactive">Inactive</span>
{% endif %}
```

**Loops** with `{% empty %}` for the zero-results case:

```django
{% for student in students %}
  <tr>…</tr>
{% empty %}
  <tr><td>No students found.</td></tr>
{% endfor %}
```

---

## 8. The `{% url %}` template tag

Named routes live in `campus/urls.py` (`name="students"`, etc.). Templates never hardcode paths:

```django
<a href="{% url 'students' %}">Students</a>
```

Benefits:

- Rename a path in `urls.py` without hunting through HTML
- Avoid broken links when mounting the app under a prefix

**Navigation highlighting** combines `{% url %}` with a context processor (`campus/context_processors.py`) that sets `active_nav` to the current `url_name`. The sidebar compares:

```django
<a class="nav-link {% if active_nav == 'students' %}is-active{% endif %}"
   href="{% url 'students' %}">Students</a>
```

---

## 9. Static files — CSS, JavaScript, images

### Configuration (`config/settings.py`)

```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]   # project-level assets (dev)
STATIC_ROOT = BASE_DIR / "staticfiles"     # collectstatic target (prod)
```

### Loading in templates

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.svg' %}" alt="CampusLink logo">
```

### Production note

In production you typically run:

```bash
python manage.py collectstatic
```

Then serve `STATIC_ROOT` with Nginx/CDN. Never rely on Django’s dev static server in production.

---

## 10. Production folder organization

Recommended layout (what this repo follows):

```
project/
  config/           # settings, root urls, wsgi/asgi
  app_name/         # views, urls, models, context_processors
  templates/
    base.html
    includes/       # shared partials
    app_name/       # pages that extend base
  static/
    css/
    js/
    images/
  manage.py
  requirements.txt
```

Guidelines:

1. Keep **one** project-level `templates/base.html`.
2. Put reusable fragments in `templates/includes/`.
3. Keep page templates thin — logic belongs in views.
4. Group static assets by type (`css/`, `js/`, `images/`).
5. Use a context processor for data needed on *every* page (user, active nav).

---

## 11. Suggested live demonstration script (≈10 minutes)

1. **Duplication problem** — imagine copying the sidebar into 7 pages; then show `base.html` + includes instead.
2. **Blocks** — edit the `content` block of `dashboard.html` only; sidebar stays intact.
3. **Include** — change text in `footer.html`; refresh any page.
4. **Static files** — show `STATICFILES_DIRS` and `{% static %}` in `base.html`.
5. **Filters** — point at GPA `floatformat` and enrol date `date` on Students.
6. **URL tag** — change a path in `campus/urls.py`, show that `{% url %}` links still work after updating the route path (name unchanged).
7. **Nav highlight** — click through Students → Courses and show the `is-active` class.

---

## 12. Concept checklist (for marking / self-review)

- [x] Template inheritance
- [x] Base templates
- [x] Blocks
- [x] Extending templates
- [x] Including templates
- [x] Template filters
- [x] Built-in template tags
- [x] Conditional statements
- [x] Loops
- [x] URL template tag
- [x] Static files
- [x] Loading CSS and JavaScript
- [x] Shared navbar / sidebar / header / footer
- [x] Dynamic tables & statistics cards
- [x] Navigation highlighting
