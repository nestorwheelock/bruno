# T-003: Star Rounding Fix

**Related Story**: S-005, S-006
**Status**: COMPLETED
**Completed**: 2025-12-19

## Objective
Implement proper rounding for star display on the dashboard so that averages like 4.5 round up to 5 stars, and averages below 4.5 round down to 4 stars.

## Problem Statement
Dashboard was displaying stars based on raw decimal averages. Template comparison `forloop.counter <= 4.2` would only fill 4 stars. User wanted standard rounding:
- 4.5+ rounds to 5 stars
- Below 4.5 rounds to 4 stars

## Solution
1. Add `*_stars` fields to `today_scores` dict in views.py
2. Use Python's `round()` function for proper rounding
3. Update template to use `*_stars` fields for star display
4. Keep raw decimal values for numeric display (e.g., "4.2/5")

## Implementation

### Views.py Changes
```python
today_scores = {
    'mood': None, 'appetite': None, 'energy': None, 'pain': None, 'overall': None,
    'mood_stars': None, 'appetite_stars': None, 'energy_stars': None,
    'pain_stars': None, 'overall_stars': None,
}

if today_entry:
    # Calculate mood average
    mood_valid = [f for f in mood_fields if f is not None]
    if mood_valid:
        avg = sum(mood_valid) / len(mood_valid)
        today_scores['mood'] = round(avg, 1)      # Decimal for display
        today_scores['mood_stars'] = round(avg)    # Integer for stars
```

### Template Changes
```html
<!-- Before -->
{% if forloop.counter <= today_scores.mood|default:0 %}

<!-- After -->
{% if forloop.counter <= today_scores.mood_stars|default:0 %}
```

### Fields Updated
- Status banner: `today_scores.overall_stars`
- Snapshot grid:
  - `today_scores.mood_stars`
  - `today_scores.appetite_stars`
  - `today_scores.energy_stars`
  - `today_scores.pain_stars`

## Testing
- Average 4.5 -> 5 stars displayed
- Average 4.4 -> 4 stars displayed
- Average 3.5 -> 4 stars displayed
- Numeric display still shows "4.5/5"

## Definition of Done
- [x] Views.py updated with *_stars fields
- [x] Dashboard template using *_stars for star comparison
- [x] Numeric values still show decimals
- [x] Deployed to production
