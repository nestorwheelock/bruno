# B-001: Blank Pages Fix (CBPI, CORQ, Events, Treatments)

**Type**: Bug
**Severity**: Critical
**Status**: RESOLVED
**Discovered**: 2025-12-19
**Resolved**: 2025-12-19

## Bug Description
Multiple health tracking pages (CBPI, CORQ, Events, Treatments) displayed blank content when accessed from the dashboard or navigation.

## Root Cause
Template block name mismatch. The affected templates used `{% block content %}` but the base template `base_health.html` expects `{% block main_content %}`.

## Affected Files
- `templates/health/cbpi.html`
- `templates/health/corq.html`
- `templates/health/events.html`
- `templates/health/treatments.html`

## Steps to Reproduce
1. Navigate to https://helpbruno.com/dashboard/
2. Click on "CBPI Pain" in Assessments Due section
3. Observe blank page

## Fix Applied
Changed `{% block content %}` to `{% block main_content %}` in all affected templates.

Also ensured that `{% endblock %}` for title and extra_css blocks were not incorrectly modified.

### cbpi.html
```diff
- {% block content %}
+ {% block main_content %}
...
- {% endblock %}
+ {% endblock main_content %}
```

### corq.html, events.html, treatments.html
Same pattern - changed content block to main_content block.

## Verification
- All pages now render correctly
- Forms functional
- History tables display

## Prevention
- Added to code review checklist: verify block names match base template
- All templates should use `{% block main_content %}` for page content
