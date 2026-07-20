# CampusLink Teaching Notes / Handout

**Topic:** Advanced Django Templates & Template Reusability  
**Project:** CampusLink Student Management Portal  
**Audience:** Peer teaching / classroom handout

Use this handout while presenting, studying, or marking the practical demo.

---

## Learning objectives

By the end of this session you should be able to:

1. Explain why template inheritance reduces duplication
2. Distinguish `{% extends %}` from `{% include %}`
3. Use blocks, loops, conditionals, filters, and the `{% url %}` / `{% static %}` tags
4. Organize templates and static files in a production-friendly layout
5. Point to working examples in CampusLink

---

## 1. Why template inheritance is important

Without inheritance, every page repeats the same `<html>` shell, sidebar, navbar, footer, and asset links. That causes:

| Problem | Result |
|---------|--------|
| Duplication | One design change requires editing many files |
| Inconsistency | Pages slowly drift apart |
| Slow onboarding | New pages start from copy-paste |

**Inheritance fix:** define the shared layout once in `templates/base.html`. Each page only fills unique regions with `{% block content %}`.

**CampusLink demo:** change brand text in `templates/includes/sidebar.html` → every page updates.

---

## 2. Base templates, blocks, and extending

| Concept | In CampusLink |
|---------|----------------|
| Base template | `templates/base.html` |
| Blocks | `title`, `content`, `extra_css`, `extra_js` |
| Extending | `{% extends "base.html" %}` on every page |

```django
{% extends "base.html" %}

{% block content %}
  <!-- page-specific markup only -->
{% endblock %}
```

**Rules**

1. `{% extends %}` must be the **first** template tag
2. Children override blocks — they do not rebuild the whole document
3. Empty blocks in the base are optional extension points

---

## 3. Difference between include and extend

| | `{% extends %}` | `{% include %}` |
|--|-----------------|-----------------|
| Purpose | Inherit a full page skeleton | Insert a reusable fragment |
| Relationship | Child *is a* specialized page | Parent *embeds* a partial |
| Typical use | Whole pages | Navbar, sidebar, footer, cards |
| Blocks | Child fills `{% block %}` regions | Included file is inserted as-is |
| CampusLink | `templates/campus/*.html` | `templates/includes/*.html` |

**Analogy:** `extends` ≈ subclassing a layout · `include` ≈ calling a component.

---

## 4. How includes improve maintainability

Shared partials in `templates/includes/`:

- `navbar.html` — top bar
- `sidebar.html` — primary navigation + brand
- `header.html` — page title / subtitle
- `footer.html` — copyright
- `stats_card.html` — reusable KPI card

```django
{% include "includes/stats_card.html" with label="Students" value=12 tone="teal" %}
```

Update once → reuse everywhere.

---

## 5. Common built-in template tags

| Tag | Role | Where to see it |
|-----|------|-----------------|
| `extends` / `block` | Inheritance | All campus pages |
| `include` | Partials | `base.html`, dashboard |
| `load` | Enable libraries | `{% load static %}`, `{% load humanize %}` |
| `static` | Asset URLs | CSS, JS, images |
| `url` | Reverse named routes | Sidebar / links |
| `if` / `elif` / `else` | Conditionals | Status badges |
| `for` / `empty` | Loops | Tables |
| `now` | Current date/time | Header, footer |
| `widthratio` | Proportional width | Course enrolment meters |

---

## 6. Common template filters

Filters transform values with `|`.

| Filter | Effect | Example |
|--------|--------|---------|
| `title` | Title case | Page headings |
| `upper` / `lower` | Case change | Student names / emails |
| `date` | Format dates | Enrolment column |
| `floatformat` | Round decimals | GPA |
| `truncatewords` / `truncatechars` | Shorten text | Bio, titles |
| `default` | Fallback | Header title |
| `length` | Count | `{{ students\|length }}` |
| `intcomma` | Thousands separators | Department totals |

---

## 7. Conditionals and loops

```django
{% if student.status == "active" %}
  <span class="badge badge-active">Active</span>
{% elif student.status == "probation" %}
  <span class="badge badge-probation">Probation</span>
{% else %}
  <span class="badge badge-inactive">Inactive</span>
{% endif %}
```

```django
{% for student in students %}
  <tr>…</tr>
{% empty %}
  <tr><td>No students found.</td></tr>
{% endfor %}
```

---

## 8. The `{% url %}` tag and navigation highlighting

Named routes in `campus/urls.py` keep templates free of hardcoded paths:

```django
<a href="{% url 'students' %}">Students</a>
```

CampusLink sets `active_nav` in `campus/context_processors.py` and highlights the current link:

```django
<a class="nav-link {% if active_nav == 'students' %}is-active{% endif %}"
   href="{% url 'students' %}">Students</a>
```

---

## 9. Static files — CSS, JavaScript, images

**Settings (`config/settings.py`)**

| Setting | Purpose |
|---------|---------|
| `STATIC_URL` | URL prefix (`/static/`) |
| `STATICFILES_DIRS` | Project static folder (development) |
| `STATIC_ROOT` | `collectstatic` destination (production) |

**Templates**

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.svg' %}" alt="CampusLink logo">
```

**Production:** run `python manage.py collectstatic` and serve `STATIC_ROOT` with Nginx/CDN.

---

## 10. Production folder organization

```
student-management-portal/
  config/                 # settings, root urls
  campus/                 # views, urls, data, context processor
  templates/
    base.html             # inheritance root
    includes/             # shared partials
    campus/               # pages that extend base
  static/css|js|images
  docs/presentation.html  # slides
  TEACHING_NOTES.md       # this handout
  README.md
```

**Guidelines**

1. One project-level `base.html`
2. Reusable fragments under `includes/`
3. Keep page templates thin — logic in views
4. Group static assets by type
5. Use a context processor for data needed on every page

---

## 11. Live demonstration script (~10 minutes)

1. Start the server and open the Dashboard (shared shell + stats cards)
2. Click through Students → Courses → Lecturers (nav highlighting)
3. On Students, point out loops, `floatformat`, `date`, and status conditionals
4. On Courses, show enrolment meters (`widthratio`)
5. Open Profile (static avatar image) and Settings
6. In the editor, open `base.html` and an include — show one change updates all pages
7. Show `{% url %}` in the sidebar and the matching names in `campus/urls.py`

---

## 12. Concept checklist

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

---

## Quick reference — run the project

```bash
cd student-management-portal
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

- Portal: http://127.0.0.1:8000/  
- Slides: open `docs/presentation.html` in a browser  
- Full setup: see `README.md`
