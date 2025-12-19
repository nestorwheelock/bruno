# B-002: Timeline Edit View 500 Error

**Type**: Bug
**Severity**: High
**Status**: RESOLVED
**Discovered**: 2025-12-19
**Resolved**: 2025-12-19

## Bug Description
The timeline edit view (`/journal/<id>/edit/`) returned a 500 Internal Server Error when accessed.

## Root Cause
Template variable mismatch. The `timeline_form.html` template uses `{{ entry.date|date:'Y-m-d'|default:today }}` which requires a `today` variable in the context. The `timeline_edit` view did not pass `today` in the context, while `timeline_create` view did.

Django template resolution attempts to evaluate all parts of a filter expression, including the `default:today` fallback, even when the primary value exists.

## Error Message
```
django.template.base.VariableDoesNotExist: Failed lookup for key [today] in [...]
```

## Affected Files
- `health/views.py` - `timeline_edit` function (line 1477-1485)

## Steps to Reproduce
1. Create a timeline entry
2. Navigate to edit view: `/journal/<id>/edit/`
3. Observe 500 error

## Fix Applied
Added `'today': date.today()` to the context dictionary in `timeline_edit` view.

```python
# health/views.py line 1477-1485
context = {
    'entry': entry,
    'providers': providers,
    'entry_types': TimelineEntry.ENTRY_TYPE_CHOICES,
    'mood_choices': TimelineEntry.MOOD_CHOICES,
    'today': date.today(),  # Added this line
}
```

## Tests Added
Created `TimelineEditViewTests` class with 6 tests:
- `test_edit_requires_login` - Verify authentication required
- `test_edit_form_get` - Verify form loads successfully
- `test_edit_form_context` - Verify correct context data
- `test_edit_entry_post` - Verify editing works correctly
- `test_edit_404_for_other_user` - Verify users can't edit others' entries
- `test_edit_nonexistent_entry` - Verify 404 for invalid entry ID

## Verification
- All 6 new tests pass
- All 94 health tests pass
- Manual verification in production

## Prevention
- Test coverage would have caught this (TDD principle)
- When sharing templates between views, ensure all required context variables are passed
- Consider using template tags or context processors for common variables like `today`

## Commit
```
fix(health): add missing 'today' context to timeline_edit view
Addresses B-002
```
