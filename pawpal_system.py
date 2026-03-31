"""
PawPal+ System — Core Logic Layer
Manages Owners, Pets, Tasks, and smart Scheduling.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
import uuid


VALID_FREQUENCIES = ("once", "daily", "weekly")
VALID_CATEGORIES = ("feeding", "walk", "medication", "appointment", "grooming", "other")


@dataclass
class Task:
    """Represents a single pet-care activity."""

    description: str
    time: str
    pet_name: str
    category: str = "other"
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __post_init__(self) -> None:
        """Validate time format, frequency, and category on creation."""
        parts = self.time.split(":")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Time must be HH:MM format, got '{self.time}'")
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError(f"Invalid time value: {self.time}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Frequency must be one of {VALID_FREQUENCIES}")
        if self.category not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of {VALID_CATEGORIES}")

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task complete and return next occurrence if recurring."""
        self.completed = True
        if self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                pet_name=self.pet_name,
                category=self.category,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                pet_name=self.pet_name,
                category=self.category,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None

    def time_as_minutes(self) -> int:
        """Convert HH:MM string to total minutes for comparison."""
        h, m = map(int, self.time.split(":"))
        return h * 60 + m

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        return (
            f"[{status}] {self.time} | {self.category.upper():11s} | "
            f"{self.description} ({self.pet_name}) [{self.frequency}]"
        )


@dataclass
class Pet:
    """Represents a single pet belonging to an owner."""

    name: str
    species: str
    breed: str = "Unknown"
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by its ID. Returns True if found and removed."""
        original_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        return len(self.tasks) < original_len

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return all completed tasks for this pet."""
        return [t for t in self.tasks if t.completed]

    def __repr__(self) -> str:
        return f"{self.name} ({self.species}, {self.breed}, age {self.age})"


@dataclass
class Owner:
    """Represents a pet owner who may have multiple pets."""

    name: str
    email: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Returns True if found and removed."""
        original_len = len(self.pets)
        self.pets = [p for p in self.pets if p.name.lower() != pet_name.lower()]
        return len(self.pets) < original_len

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Retrieve a pet by name (case-insensitive)."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def all_tasks(self) -> list[Task]:
        """Aggregate and return every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def __repr__(self) -> str:
        return f"Owner({self.name}, {len(self.pets)} pets)"


class Scheduler:
    """The scheduling brain of PawPal+."""

    def __init__(self, owner: Owner) -> None:
        """Initialise the Scheduler with an Owner instance."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across every pet."""
        return self.owner.all_tasks()

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks for a specific pet by name."""
        pet = self.owner.get_pet(pet_name)
        return pet.tasks if pet else []

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted chronologically by their HH:MM time."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time_as_minutes())

    def filter_by_status(self, completed: bool = False, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Filter tasks by completion status."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Filter tasks to only those belonging to the named pet."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.pet_name.lower() == pet_name.lower()]

    def filter_by_category(self, category: str, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Filter tasks by category."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.category.lower() == category.lower()]

    def todays_schedule(self) -> list[Task]:
        """Return all tasks due today, sorted by time."""
        today = date.today()
        tasks = [t for t in self.get_all_tasks() if t.due_date == today]
        return self.sort_by_time(tasks)

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[tuple[Task, Task, str]]:
        """Detect scheduling conflicts between tasks."""
        tasks = self.sort_by_time(tasks if tasks is not None else self.get_all_tasks())
        conflicts: list[tuple[Task, Task, str]] = []
        for i, a in enumerate(tasks):
            for b in tasks[i + 1:]:
                diff = abs(a.time_as_minutes() - b.time_as_minutes())
                if diff > 5:
                    break
                same_pet = a.pet_name.lower() == b.pet_name.lower()
                if diff == 0 and same_pet:
                    conflicts.append((a, b, "exact same time for same pet"))
                elif diff == 0:
                    conflicts.append((a, b, "exact same time across pets"))
                elif diff <= 5 and same_pet:
                    conflicts.append((a, b, f"only {diff} min apart for same pet"))
        return conflicts

    def conflict_warnings(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """Return human-readable conflict warning strings."""
        warnings = []
        for a, b, reason in self.detect_conflicts(tasks):
            warnings.append(
                f"⚠️  CONFLICT ({reason}): "
                f"'{a.description}' ({a.pet_name} @ {a.time}) vs "
                f"'{b.description}' ({b.pet_name} @ {b.time})"
            )
        return warnings

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task complete and handle recurrence."""
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.task_id == task_id:
                    next_task = task.mark_complete()
                    if next_task:
                        pet.add_task(next_task)
                    return next_task
        return None

    def print_schedule(self, tasks: Optional[list[Task]] = None) -> None:
        """Pretty-print a schedule to the terminal."""
        tasks = tasks if tasks is not None else self.sort_by_time()
        print("\n" + "═" * 60)
        print(f"  Schedule for {self.owner.name}")
        print("═" * 60)
        if not tasks:
            print("  (no tasks scheduled)")
        for t in tasks:
            print(f"  {t}")
        warnings = self.conflict_warnings(tasks)
        if warnings:
            print()
            for w in warnings:
                print(f"  {w}")
        print("═" * 60 + "\n")