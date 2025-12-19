# S-006: Dashboard Redesign

**Story Type**: User Story
**Priority**: High
**Status**: COMPLETED

## User Story
**As a** family member monitoring Bruno's health
**I want to** see a comprehensive dashboard with all health data
**So that** I can quickly assess his status and prepare for vet visits

## Acceptance Criteria
- [x] Today's status banner with overall score and stars
- [x] Snapshot grid showing mood, appetite, energy, comfort, meals
- [x] Time range selector (7d, 30d, 90d)
- [x] QoL trends chart with happiness and overall scores
- [x] Treatment response section with lymph node chart
- [x] Nutrition progress bars and supplement checklist
- [x] Medication status with given/due indicators
- [x] Recent adverse events section
- [x] Assessment reminders (CBPI, CORQ, lymph nodes)
- [x] 30-day summary (good/mixed/bad days)
- [x] Mobile-first responsive design
- [x] Collapsible sections for organization

## Definition of Done
- [x] dashboard_view updated with comprehensive context data
- [x] dashboard.html rewritten with all sections
- [x] Chart.js integration for trends
- [x] localStorage for time range persistence
- [x] Deployed to production

## Implementation Details

### Dashboard Sections
1. **Time Range Selector**: 7d/30d/90d pill buttons with localStorage persistence
2. **Status Banner**: Large score, star rating, status message, trend indicator
3. **Snapshot Grid**: 6 mini-cards (mood, appetite, energy, comfort, meals, log button)
4. **QoL Trends**: Line chart with happiness and overall scores
5. **Treatment Response**: Lymph node chart, recent treatment info
6. **Nutrition Today**: Progress bars, macro breakdown, supplement checklist
7. **Medications**: Active meds with given/due status
8. **Recent Events**: Adverse events with grade indicators
9. **Assessments Due**: Reminders with overdue highlighting
10. **30-Day Summary**: Good/mixed/bad day counts

### Category Score Calculation
- **Mood**: Average of tail_body_language, interest_people, interest_environment, enjoyment_favorites, overall_spark
- **Appetite**: Average of appetite, food_enjoyment
- **Energy**: Average of energy_level, willingness_move
- **Comfort**: Average of pain_signs, breathing_comfort (inverted as needed)

### Trend Calculation
- Compare average of last 7 days to previous 7 days
- Improving: +0.3 or more
- Declining: -0.3 or more
- Stable: within +/- 0.3

### Files Modified
- `health/views.py`: Expanded dashboard_view with all context data
- `templates/health/dashboard.html`: Complete rewrite

### Related Tasks
- T-002: Dashboard Implementation
- T-003: Star Rounding Fix
