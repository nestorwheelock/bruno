# Bruno Health Tracker - Project Charter

## Project Overview

**Project Name:** Bruno Health Tracker
**Version:** 1.0.0
**License:** GPL-3.0 (Copyleft Open Source)
**Repository:** github.com/nestorwheelock/bruno-health-tracker

## What

A Django web application for tracking canine lymphoma treatment quality-of-life metrics. Designed for mobile-first use by family members caring for Bruno, a 6-year-old dog diagnosed with lymphoma.

### Features
1. **Fundraising Landing Page** - Public page to collect donations via GoFundMe
2. **Health Tracker** - Authenticated daily quality-of-life tracking
3. **Medication Tracker** - Record medications and doses given
4. **Lymph Node Measurements** - Track node sizes over time
5. **History & Reporting** - Weekly summaries and export for vet visits

## Why

- Bruno needs cancer treatment that requires ongoing monitoring
- Multiple family members need shared access to track his health
- Quality-of-life metrics help make informed treatment decisions
- Data export helps communicate with veterinary oncologist

## How

### Architecture (Modular Components)

```
bruno/
├── apps/
│   ├── core/           # Shared utilities, base templates
│   ├── fundraiser/     # Public fundraising page
│   ├── tracker/        # Health tracking (daily entries)
│   ├── medications/    # Medication management
│   └── nodes/          # Lymph node measurements
├── config/             # Django settings (modular)
├── templates/          # Global templates
├── static/             # Static assets
└── tests/              # Test suite
```

### Technology Stack
- **Backend:** Django 5.x, Django REST Framework
- **Database:** PostgreSQL 16
- **Server:** Gunicorn + WhiteNoise
- **Container:** Docker + Docker Compose
- **Frontend:** Mobile-first responsive HTML/CSS/JS

## Success Criteria

- [ ] All tests pass (>95% coverage)
- [ ] App accessible on all network IPs (0.0.0.0)
- [ ] Both users can log in and track simultaneously
- [ ] Data persists across container restarts
- [ ] Code is modular and maintainable
- [ ] GPL-3.0 license applied
- [ ] Published to GitHub as open source

## Risks

| Risk | Mitigation |
|------|------------|
| Data loss | PostgreSQL with Docker volume persistence |
| Security | Authentication required for tracker, CSRF protection |
| Usability | Mobile-first design, simple interface |

## Timeline

Single sprint delivery using 23-step TDD cycle.
