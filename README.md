# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## 📸 Demo

<a href="pawpal_screenshot.png" target="_blank">
  <img src='pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' />
</a>

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ includes four algorithmic features that make scheduling intelligent:

- **Sort by time** — Tasks always display in chronological order using Python's `sorted()` with a `lambda` key that converts HH:MM strings to total minutes for accurate numeric comparison.
- **Filter by pet / status / category** — Chainable filters let you narrow any task list instantly without rewriting logic.
- **Recurring tasks** — Marking a `daily` task complete automatically creates the next occurrence using `timedelta(days=1)`. Weekly tasks advance by 7 days the same way.
- **Conflict detection** — Scans the sorted task list for exact same-time clashes (same pet = hard conflict, different pets = warning) and flags tasks within 5 minutes of each other for the same pet.

## Testing PawPal+

Run the full test suite with:
```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test Class | Coverage |
|------------|---------|
| `TestTask` | Creation, validation, mark_complete(), unique IDs, time_as_minutes() |
| `TestRecurrence` | Daily +1 day, weekly +7 days, once returns None, scheduler integration |
| `TestPet` | Add/remove tasks, pending task filtering |
| `TestOwner` | Add pets, case-insensitive lookup, all_tasks() aggregation |
| `TestSorting` | Chronological order, empty list edge case |
| `TestFiltering` | Status, pet name, category filters, today's schedule |
| `TestConflictDetection` | No conflict, exact-time same pet, exact-time cross-pet, 5-min window |

### Confidence Level: ⭐⭐⭐⭐⭐ (5/5)

All 28 tests pass covering happy paths and edge cases.