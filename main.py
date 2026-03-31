"""
main.py — PawPal+ CLI Demo Script
Run with: python main.py
"""

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # ── Setup owner ────────────────────────────────────────────────────
    owner = Owner(name="Alex Rivera", email="alex@example.com")

    # ── Create pets ────────────────────────────────────────────────────
    luna = Pet(name="Luna", species="dog", breed="Golden Retriever", age=3)
    mochi = Pet(name="Mochi", species="cat", breed="Scottish Fold", age=5)

    owner.add_pet(luna)
    owner.add_pet(mochi)

    today = date.today()

    # ── Add tasks (intentionally out of order to test sorting) ─────────
    luna.add_task(Task("Evening walk",    "18:30", "Luna",  "walk",        "daily",  today))
    luna.add_task(Task("Morning kibble",  "07:00", "Luna",  "feeding",     "daily",  today))
    luna.add_task(Task("Heartworm pill",  "08:00", "Luna",  "medication",  "daily",  today))
    luna.add_task(Task("Vet check-up",    "14:00", "Luna",  "appointment", "once",   today))
    luna.add_task(Task("Afternoon walk",  "14:00", "Luna",  "walk",        "daily",  today))
    mochi.add_task(Task("Wet food",       "08:00", "Mochi", "feeding",     "daily",  today))
    mochi.add_task(Task("Flea treatment", "10:00", "Mochi", "medication",  "weekly", today))

    scheduler = Scheduler(owner)

    # ── 1. Full sorted schedule ────────────────────────────────────────
    print("\n🐾  PawPal+ Demo\n")
    scheduler.print_schedule()

    # ── 2. Today's schedule only ───────────────────────────────────────
    print("📅  Today's Tasks (sorted):")
    scheduler.print_schedule(scheduler.todays_schedule())

    # ── 3. Filter: pending tasks for Luna ─────────────────────────────
    print("🐕  Luna's pending tasks:")
    luna_pending = scheduler.filter_by_status(
        completed=False,
        tasks=scheduler.get_tasks_for_pet("Luna"),
    )
    scheduler.print_schedule(luna_pending)

    # ── 4. Mark a recurring task complete ─────────────────────────────
    morning_kibble = luna.tasks[1]
    print(f"✅  Completing task: {morning_kibble.description}")
    next_task = scheduler.complete_task(morning_kibble.task_id)
    if next_task:
        print(f"    ↩  Rescheduled for: {next_task.due_date}\n")

    # ── 5. Conflict detection ─────────────────────────────────────────
    print("🔍  Conflict Check:")
    warnings = scheduler.conflict_warnings()
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  No conflicts detected.")
    print()


if __name__ == "__main__":
    main()