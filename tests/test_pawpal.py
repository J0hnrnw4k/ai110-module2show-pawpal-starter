"""
tests/test_pawpal.py — Automated test suite for PawPal+
Run with: python -m pytest
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def sample_owner():
    """An owner with two pets and a handful of tasks."""
    owner = Owner(name="Test Owner", email="test@example.com")
    dog = Pet(name="Rex", species="dog", breed="Labrador", age=4)
    cat = Pet(name="Nala", species="cat", breed="Siamese", age=2)

    today = date.today()
    dog.add_task(Task("Morning walk",   "07:30", "Rex",  "walk",        "daily",  today))
    dog.add_task(Task("Vet visit",      "14:00", "Rex",  "appointment", "once",   today))
    dog.add_task(Task("Evening kibble", "18:00", "Rex",  "feeding",     "daily",  today))
    cat.add_task(Task("Wet food",       "08:00", "Nala", "feeding",     "daily",  today))
    cat.add_task(Task("Flea tablet",    "09:00", "Nala", "medication",  "weekly", today))

    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


@pytest.fixture
def scheduler(sample_owner):
    """Scheduler bound to the sample owner."""
    return Scheduler(sample_owner)


# ── Task Tests ─────────────────────────────────────────────────────────────

class TestTask:
    def test_task_creation(self):
        """Task stores all attributes correctly."""
        t = Task("Walk", "09:00", "Rex", "walk", "daily", date.today())
        assert t.description == "Walk"
        assert t.time == "09:00"
        assert t.completed is False

    def test_mark_complete_changes_status(self):
        """mark_complete() should set completed=True."""
        t = Task("Feed", "08:00", "Nala", "feeding", "once", date.today())
        assert t.completed is False
        t.mark_complete()
        assert t.completed is True

    def test_invalid_time_raises(self):
        """Invalid time format should raise ValueError."""
        with pytest.raises(ValueError):
            Task("Bad task", "25:00", "Rex", "walk", "once", date.today())

    def test_invalid_frequency_raises(self):
        """Invalid frequency should raise ValueError."""
        with pytest.raises(ValueError):
            Task("Bad task", "09:00", "Rex", "walk", "monthly", date.today())

    def test_invalid_category_raises(self):
        """Invalid category should raise ValueError."""
        with pytest.raises(ValueError):
            Task("Bad task", "09:00", "Rex", "swimming", "once", date.today())

    def test_time_as_minutes(self):
        """time_as_minutes should convert HH:MM correctly."""
        t = Task("X", "01:30", "Rex", "walk", "once", date.today())
        assert t.time_as_minutes() == 90

    def test_task_has_unique_id(self):
        """Each task should receive a unique ID."""
        t1 = Task("A", "09:00", "Rex", "walk", "once", date.today())
        t2 = Task("B", "09:00", "Rex", "walk", "once", date.today())
        assert t1.task_id != t2.task_id


# ── Recurrence Tests ───────────────────────────────────────────────────────

class TestRecurrence:
    def test_daily_task_creates_next_day(self):
        """Completing a daily task returns a new task for tomorrow."""
        today = date.today()
        t = Task("Morning walk", "07:00", "Rex", "walk", "daily", today)
        next_task = t.mark_complete()
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)
        assert next_task.completed is False

    def test_weekly_task_creates_next_week(self):
        """Completing a weekly task returns a new task 7 days later."""
        today = date.today()
        t = Task("Grooming", "10:00", "Rex", "grooming", "weekly", today)
        next_task = t.mark_complete()
        assert next_task is not None
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_once_task_returns_none(self):
        """Completing a one-time task should NOT create a new task."""
        t = Task("Vet visit", "14:00", "Rex", "appointment", "once", date.today())
        result = t.mark_complete()
        assert result is None

    def test_scheduler_complete_task_adds_recurrence(self, scheduler):
        """Scheduler.complete_task() should add the next occurrence to the pet."""
        dog = scheduler.owner.get_pet("Rex")
        walk = dog.tasks[0]
        original_count = len(dog.tasks)
        scheduler.complete_task(walk.task_id)
        assert len(dog.tasks) == original_count + 1


# ── Pet Tests ──────────────────────────────────────────────────────────────

class TestPet:
    def test_add_task_increases_count(self):
        """Adding a task should increase the pet's task list."""
        pet = Pet("Buddy", "dog")
        assert len(pet.tasks) == 0
        pet.add_task(Task("Walk", "09:00", "Buddy", "walk", "once", date.today()))
        assert len(pet.tasks) == 1

    def test_remove_task(self):
        """remove_task returns True and removes the task."""
        pet = Pet("Buddy", "dog")
        task = Task("Walk", "09:00", "Buddy", "walk", "once", date.today())
        pet.add_task(task)
        result = pet.remove_task(task.task_id)
        assert result is True
        assert len(pet.tasks) == 0

    def test_remove_nonexistent_task(self):
        """remove_task returns False when the task ID doesn't exist."""
        pet = Pet("Buddy", "dog")
        assert pet.remove_task("fakeid") is False

    def test_get_pending_tasks(self):
        """get_pending_tasks returns only incomplete tasks."""
        pet = Pet("Buddy", "dog")
        t1 = Task("Walk", "09:00", "Buddy", "walk", "once", date.today())
        t2 = Task("Feed", "08:00", "Buddy", "feeding", "once", date.today())
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)
        assert len(pet.get_pending_tasks()) == 1


# ── Owner Tests ────────────────────────────────────────────────────────────

class TestOwner:
    def test_add_pet(self):
        """Owner can add pets."""
        owner = Owner("Sam")
        owner.add_pet(Pet("Fluffy", "cat"))
        assert len(owner.pets) == 1

    def test_get_pet_case_insensitive(self):
        """get_pet should be case-insensitive."""
        owner = Owner("Sam")
        owner.add_pet(Pet("Fluffy", "cat"))
        assert owner.get_pet("fluffy") is not None
        assert owner.get_pet("FLUFFY") is not None

    def test_all_tasks_aggregates(self, sample_owner):
        """all_tasks should return combined tasks from all pets."""
        total = sum(len(p.tasks) for p in sample_owner.pets)
        assert len(sample_owner.all_tasks()) == total


# ── Sorting Tests ──────────────────────────────────────────────────────────

class TestSorting:
    def test_sort_by_time_chronological(self, scheduler):
        """Tasks returned by sort_by_time should be in ascending time order."""
        sorted_tasks = scheduler.sort_by_time()
        times = [t.time_as_minutes() for t in sorted_tasks]
        assert times == sorted(times)

    def test_sort_handles_empty_list(self, scheduler):
        """sort_by_time with an empty list returns an empty list."""
        assert scheduler.sort_by_time([]) == []


# ── Filtering Tests ────────────────────────────────────────────────────────

class TestFiltering:
    def test_filter_by_status_pending(self, scheduler):
        """filter_by_status(completed=False) returns only incomplete tasks."""
        pending = scheduler.filter_by_status(completed=False)
        assert all(not t.completed for t in pending)

    def test_filter_by_pet(self, scheduler):
        """filter_by_pet returns tasks only for the named pet."""
        rex_tasks = scheduler.filter_by_pet("Rex")
        assert all(t.pet_name == "Rex" for t in rex_tasks)

    def test_filter_by_category(self, scheduler):
        """filter_by_category returns tasks of the given category."""
        walks = scheduler.filter_by_category("walk")
        assert all(t.category == "walk" for t in walks)

    def test_todays_schedule(self, scheduler):
        """todays_schedule returns only today's tasks sorted by time."""
        today_tasks = scheduler.todays_schedule()
        today = date.today()
        assert all(t.due_date == today for t in today_tasks)
        times = [t.time_as_minutes() for t in today_tasks]
        assert times == sorted(times)


# ── Conflict Detection Tests ───────────────────────────────────────────────

class TestConflictDetection:
    def test_no_conflicts_in_normal_schedule(self, scheduler):
        """A well-spaced schedule should have zero conflicts."""
        conflicts = scheduler.detect_conflicts()
        assert conflicts == []

    def test_exact_same_time_same_pet_is_conflict(self):
        """Two tasks at the exact same time for the same pet are a conflict."""
        owner = Owner("Conflict Tester")
        dog = Pet("Spot", "dog")
        today = date.today()
        dog.add_task(Task("Walk", "10:00", "Spot", "walk",    "once", today))
        dog.add_task(Task("Feed", "10:00", "Spot", "feeding", "once", today))
        owner.add_pet(dog)
        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) >= 1
        assert any("exact same time for same pet" in reason for _, _, reason in conflicts)

    def test_conflict_warnings_returns_strings(self):
        """conflict_warnings() should return a list of non-empty strings."""
        owner = Owner("W Tester")
        dog = Pet("Max", "dog")
        today = date.today()
        dog.add_task(Task("A", "10:00", "Max", "walk",    "once", today))
        dog.add_task(Task("B", "10:00", "Max", "feeding", "once", today))
        owner.add_pet(dog)
        scheduler = Scheduler(owner)
        warnings = scheduler.conflict_warnings()
        assert len(warnings) >= 1
        assert all(isinstance(w, str) and len(w) > 0 for w in warnings)

    def test_close_times_trigger_warning(self):
        """Tasks within 5 minutes for the same pet should trigger a conflict."""
        owner = Owner("Close Timer")
        dog = Pet("Buddy", "dog")
        today = date.today()
        dog.add_task(Task("Task A", "10:00", "Buddy", "walk",    "once", today))
        dog.add_task(Task("Task B", "10:03", "Buddy", "feeding", "once", today))
        owner.add_pet(dog)
        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) >= 1