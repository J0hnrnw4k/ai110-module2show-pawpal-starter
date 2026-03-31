# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- I designed four classes: Task, Pet, Owner, and Scheduler. Task holds all activity data including description, time, category, frequency, and due date. Pet manages a list of tasks for one animal and handles adding, removing, and filtering them. Owner aggregates multiple pets and provides cross-pet task access through a single interface. Scheduler is the logic brain — it sorts tasks by time, filters by pet or category, detects conflicts, and handles recurring task rescheduling. It holds no data of its own, only behavior.

**b. Design changes**

- Yes, two things changed. I originally planned for conflict detection to live inside Pet,
but moved it to Scheduler because it needs visibility across all pets simultaneously.
I also moved time_as_minutes() into Task so the sort key would be cleaner and independently testable.---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler considers time (HH:MM format), due date, and frequency (once, daily, weekly). Time mattered most because overlapping tasks cause real problems for a pet owner — you cannot walk two dogs at the exact same moment.

**b. Tradeoffs**

- Conflict detection uses exact-minute matching rather than duration awareness. This means a 60-minute vet appointment will not flag a conflict with a task scheduled 30 minutes later. This tradeoff keeps the logic simple and fast while still catching the most obvious scheduling errors.

## 3. AI Collaboration

**a. How you used AI**

- HI used AI for initial class scaffolding, generating test cases, and refactoring sorting logic. The most helpful prompts were specific ones like "how should Scheduler retrieve tasks from Owner's pets" rather than vague open-ended ones. Using separate chat sessions for design, implementation, algorithms, and testing
kept each interaction focused and prevented earlier context from biasing later suggestions.

**b. Judgment and verification**

- The AI suggested using a dictionary keyed by (pet_name, time) for conflict detection.
I rejected this because it only catches exact duplicates for the same pet and misses
cross-pet conflicts entirely. I verified my own approach by manually tracing through
the logic with two pets scheduled at the same time and confirming the warning appeared.
---

## 4. Testing and Verification

**a. What you tested**

- I tested task completion status changes, recurring task rescheduling for both daily
and weekly frequencies, conflict detection for same-pet and cross-pet clashes,
chronological sort order, and filtering by pet name, status, and category.
These tests were important because they cover both the happy path and edge cases
like empty lists and duplicate times.
**b. Confidence**

- Very confident — 28 tests pass covering all core behaviors and edge cases.
If I had more time I would test tasks that span midnight, owners with zero pets,
and adding duplicate pet names.

---

## 5. Reflection

**a. What went well**

- The separation between Scheduler (logic only) and Pet/Owner (data only) made
testing clean and kept each class focused on one responsibility.
This made debugging fast because failures pointed directly to the right class.

**b. What you would improve**

- I would add a duration_minutes field to Task so conflict detection could catch
overlapping time windows rather than just exact-minute clashes.

**c. Key takeaway**

- AI is a fast implementer but a poor architect. Every suggestion still required
evaluation against the actual design goals. The human judgment step — deciding
which tradeoffs matter for this specific use case — is where the real engineering happens.
