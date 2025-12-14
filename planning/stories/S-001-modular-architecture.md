# S-001: Modular Django Architecture

**Story Type**: User Story
**Priority**: High
**Status**: PENDING

## User Story
**As a** developer
**I want to** have a modular Django application structure
**So that** code is maintainable, testable, and follows best practices

## Acceptance Criteria
- [ ] Apps are separated by domain (core, fundraiser, tracker, medications, nodes)
- [ ] Each app has its own models, views, urls, and tests
- [ ] Shared utilities are in core app
- [ ] Settings are environment-aware (dev/prod)
- [ ] All tests pass with >95% coverage

## Definition of Done
- [ ] Modular directory structure created
- [ ] All existing functionality preserved
- [ ] Tests written for each module
- [ ] Tests passing
- [ ] Code committed with reference to this story
