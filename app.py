"""
app.py — PawPal+ Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, VALID_CATEGORIES, VALID_FREQUENCIES

# ── Page config ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Space+Mono&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.block-container { padding-top: 1.5rem; }
h1, h2, h3 { font-family: 'Nunito', sans-serif; font-weight: 800; }

.paw-header {
    background: linear-gradient(135deg, #ff7043 0%, #ff8f00 100%);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
}
.paw-header h1 { color: white; margin: 0; font-size: 2rem; }
.paw-header p  { color: rgba(255,255,255,.85); margin: .3rem 0 0; font-size: 1rem; }

.task-card {
    background: white;
    border-radius: 12px;
    padding: .8rem 1.2rem;
    margin: .4rem 0;
    border-left: 5px solid #ff7043;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    font-family: 'Space Mono', monospace;
    font-size: .82rem;
}
.task-card.done { border-left-color: #66bb6a; opacity: .6; }

.pill {
    display: inline-block;
    border-radius: 20px;
    padding: .15rem .55rem;
    font-size: .72rem;
    font-weight: 700;
    margin-left: .4rem;
    text-transform: uppercase;
}
.pill-feeding     { background:#fff3e0; color:#e65100; }
.pill-walk        { background:#e8f5e9; color:#2e7d32; }
.pill-medication  { background:#fce4ec; color:#880e4f; }
.pill-appointment { background:#e3f2fd; color:#0d47a1; }
.pill-grooming    { background:#f3e5f5; color:#6a1b9a; }
.pill-other       { background:#f5f5f5; color:#424242; }

.conflict-box {
    background: #fff3f3;
    border: 1.5px solid #ef9a9a;
    border-radius: 10px;
    padding: .7rem 1rem;
    margin: .4rem 0;
    font-size: .85rem;
}
.stat-card {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
}
.stat-card .num { font-size: 2rem; font-weight: 800; color: #ff7043; }
.stat-card .lbl { font-size: .8rem; color: #888; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Session State Bootstrap ────────────────────────────────────────────────

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="My Household", email="")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ── Helpers ────────────────────────────────────────────────────────────────

CATEGORY_ICONS = {
    "feeding": "🍽️", "walk": "🦮", "medication": "💊",
    "appointment": "🏥", "grooming": "✂️", "other": "📌",
}

def pill(category: str) -> str:
    """Return an HTML pill badge for a task category."""
    icon = CATEGORY_ICONS.get(category, "📌")
    return f'<span class="pill pill-{category}">{icon} {category}</span>'

def render_task_card(task: Task, show_complete_btn: bool = True) -> None:
    """Render a single task as a styled card with an optional complete button."""
    status_class = "done" if task.completed else ""
    check = "✅" if task.completed else "○"
    cols = st.columns([5, 1])
    with cols[0]:
        st.markdown(
            f'<div class="task-card {status_class}">'
            f'<b>{task.time}</b>  {check}  {task.description} '
            f'— <i>{task.pet_name}</i>'
            f'{pill(task.category)}'
            f'<span class="pill" style="background:#ede7f6;color:#4527a0">'
            f'🔁 {task.frequency}</span>'
            f'  <small style="color:#aaa">📅 {task.due_date}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with cols[1]:
        if show_complete_btn and not task.completed:
            if st.button("✅ Done", key=f"done_{task.task_id}"):
                next_task = scheduler.complete_task(task.task_id)
                if next_task:
                    st.success(
                        f"Rescheduled '{next_task.description}' → {next_task.due_date}"
                    )
                st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🐾 PawPal+")
    st.markdown(f"**Owner:** {owner.name}")
    st.markdown("---")

    with st.expander("✏️ Edit Owner Name"):
        new_name = st.text_input("Owner name", value=owner.name, key="owner_name")
        if st.button("Save"):
            owner.name = new_name
            st.success("Saved!")

    with st.expander("➕ Add a Pet"):
        pet_name  = st.text_input("Pet name", key="add_pet_name")
        species   = st.selectbox(
            "Species", ["dog", "cat", "rabbit", "bird", "fish", "other"],
            key="add_pet_species"
        )
        breed     = st.text_input("Breed (optional)", key="add_pet_breed")
        age       = st.number_input("Age (years)", min_value=0, max_value=30,
                                    key="add_pet_age")
        if st.button("Add Pet"):
            if not pet_name.strip():
                st.warning("Please enter a pet name.")
            elif owner.get_pet(pet_name):
                st.warning(f"A pet named '{pet_name}' already exists.")
            else:
                owner.add_pet(Pet(
                    name=pet_name.strip(),
                    species=species,
                    breed=breed.strip() or "Unknown",
                    age=int(age),
                ))
                st.success(f"Added {pet_name}! 🐾")
                st.rerun()

    st.markdown("### 🐶 Your Pets")
    if not owner.pets:
        st.info("No pets yet. Add one above!")
    for pet in owner.pets:
        st.markdown(
            f"**{pet.name}** · {pet.species} · {pet.breed} · age {pet.age}  "
            f"({len(pet.tasks)} tasks)"
        )

# ── Main Header ────────────────────────────────────────────────────────────

st.markdown(
    '<div class="paw-header">'
    '<h1>🐾 PawPal+</h1>'
    '<p>Smart pet care management — scheduling, reminders, and conflict detection</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Stats ──────────────────────────────────────────────────────────────────

all_tasks   = scheduler.get_all_tasks()
pending     = scheduler.filter_by_status(completed=False)
done        = scheduler.filter_by_status(completed=True)
conflicts   = scheduler.detect_conflicts()
today_tasks = scheduler.todays_schedule()

c1, c2, c3, c4, c5 = st.columns(5)
for col, num, lbl in [
    (c1, len(owner.pets),  "Pets"),
    (c2, len(all_tasks),   "Total Tasks"),
    (c3, len(pending),     "Pending"),
    (c4, len(done),        "Completed"),
    (c5, len(conflicts),   "Conflicts"),
]:
    col.markdown(
        f'<div class="stat-card"><div class="num">{num}</div>'
        f'<div class="lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Today's Schedule", "📋 All Tasks", "➕ Add Task", "⚠️ Conflicts"
])

# ---- Tab 1: Today --------------------------------------------------------
with tab1:
    st.subheader(f"📅 Today — {date.today().strftime('%A, %B %d %Y')}")
    if not today_tasks:
        st.info("Nothing scheduled for today. Enjoy the day! 🌟")
    else:
        for task in today_tasks:
            render_task_card(task)

    today_conflicts = scheduler.conflict_warnings(today_tasks)
    if today_conflicts:
        st.markdown("#### ⚠️ Today's Conflicts")
        for w in today_conflicts:
            st.markdown(
                f'<div class="conflict-box">{w}</div>',
                unsafe_allow_html=True
            )

# ---- Tab 2: All Tasks ----------------------------------------------------
with tab2:
    st.subheader("📋 All Tasks")

    f1, f2, f3 = st.columns(3)
    with f1:
        pet_options = ["All pets"] + [p.name for p in owner.pets]
        pet_filter = st.selectbox("Filter by pet", pet_options, key="filter_pet")
    with f2:
        status_filter = st.selectbox(
            "Filter by status", ["All", "Pending", "Completed"], key="filter_status"
        )
    with f3:
        cat_options = ["All categories"] + list(VALID_CATEGORIES)
        cat_filter = st.selectbox("Filter by category", cat_options, key="filter_cat")

    filtered = scheduler.sort_by_time()
    if pet_filter != "All pets":
        filtered = scheduler.filter_by_pet(pet_filter, filtered)
    if status_filter == "Pending":
        filtered = scheduler.filter_by_status(completed=False, tasks=filtered)
    elif status_filter == "Completed":
        filtered = scheduler.filter_by_status(completed=True, tasks=filtered)
    if cat_filter != "All categories":
        filtered = scheduler.filter_by_category(cat_filter, filtered)

    if not filtered:
        st.info("No tasks match the current filters.")
    else:
        for task in filtered:
            render_task_card(task)

# ---- Tab 3: Add Task -----------------------------------------------------
with tab3:
    st.subheader("➕ Schedule a New Task")

    if not owner.pets:
        st.warning("Add a pet first using the sidebar before scheduling tasks.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            t_description = st.text_input(
                "Task description", placeholder="e.g. Morning walk"
            )
            t_pet = st.selectbox(
                "For which pet?", [p.name for p in owner.pets], key="task_pet"
            )
            t_category = st.selectbox(
                "Category", list(VALID_CATEGORIES), key="task_cat"
            )
        with col_b:
            t_time = st.time_input("Time", key="task_time")
            t_frequency = st.selectbox(
                "Frequency", list(VALID_FREQUENCIES), key="task_freq"
            )
            t_due = st.date_input("Due date", value=date.today(), key="task_due")

        if st.button("Schedule Task 🗓️", type="primary"):
            if not t_description.strip():
                st.warning("Please enter a task description.")
            else:
                time_str = t_time.strftime("%H:%M")
                pet = owner.get_pet(t_pet)
                new_task = Task(
                    description=t_description.strip(),
                    time=time_str,
                    pet_name=t_pet,
                    category=t_category,
                    frequency=t_frequency,
                    due_date=t_due,
                )
                pet.add_task(new_task)
                st.success(
                    f"✅ Scheduled '{t_description}' for {t_pet} at {time_str}!"
                )
                new_conflicts = scheduler.conflict_warnings()
                if new_conflicts:
                    st.warning("⚠️ New conflicts detected:")
                    for w in new_conflicts:
                        st.markdown(
                            f'<div class="conflict-box">{w}</div>',
                            unsafe_allow_html=True
                        )
                st.rerun()

# ---- Tab 4: Conflicts ----------------------------------------------------
with tab4:
    st.subheader("⚠️ Conflict Report")
    all_conflicts = scheduler.conflict_warnings()

    if not all_conflicts:
        st.success("✅ No scheduling conflicts detected! Everything looks great.")
    else:
        st.error(f"Found {len(all_conflicts)} conflict(s). Please review:")
        for w in all_conflicts:
            st.markdown(
                f'<div class="conflict-box">{w}</div>',
                unsafe_allow_html=True
            )

    with st.expander("ℹ️ How conflict detection works"):
        st.markdown("""
        PawPal+ flags two types of conflicts:
        - **Exact same time, same pet** — Two tasks at the identical time for one pet.
        - **Exact same time, different pets** — You can't be in two places at once!
        - **Within 5 minutes, same pet** — A tight window that may cause rushed care.

        Resolve conflicts by rescheduling via the **Add Task** tab.
        """)
