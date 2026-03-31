# PawPal+ — Final UML Class Diagram

Paste the code block below into [Mermaid Live Editor](https://mermaid.live) to render the diagram.
```mermaid
classDiagram

    class Task {
        +String description
        +String time
        +String pet_name
        +String category
        +String frequency
        +Date due_date
        +Boolean completed
        +String task_id
        +mark_complete() Task|None
        +time_as_minutes() int
    }

    class Pet {
        +String name
        +String species
        +String breed
        +int age
        +List~Task~ tasks
        +add_task(task: Task) None
        +remove_task(task_id: String) bool
        +get_pending_tasks() List~Task~
        +get_completed_tasks() List~Task~
    }

    class Owner {
        +String name
        +String email
        +List~Pet~ pets
        +add_pet(pet: Pet) None
        +remove_pet(pet_name: String) bool
        +get_pet(pet_name: String) Pet|None
        +all_tasks() List~Task~
    }

    class Scheduler {
        +Owner owner
        +get_all_tasks() List~Task~
        +get_tasks_for_pet(pet_name: String) List~Task~
        +sort_by_time(tasks: List~Task~) List~Task~
        +filter_by_status(completed: bool, tasks: List~Task~) List~Task~
        +filter_by_pet(pet_name: String, tasks: List~Task~) List~Task~
        +filter_by_category(category: String, tasks: List~Task~) List~Task~
        +todays_schedule() List~Task~
        +detect_conflicts(tasks: List~Task~) List~Tuple~
        +conflict_warnings(tasks: List~Task~) List~String~
        +complete_task(task_id: String) Task|None
        +print_schedule(tasks: List~Task~) None
    }

    Owner "1" o-- "0..*" Pet : has
    Pet   "1" o-- "0..*" Task : manages
    Scheduler "1" --> "1" Owner : reads/writes
```