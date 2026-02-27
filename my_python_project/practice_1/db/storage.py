# In-memory database storage

users_db = {}  # {user_id: user_data}
tasks_db = {}  # {task_id: task_data}
projects_db = {}  # {project_id: project_data}

# ID counters - using dict for mutable reference
user_id_counter = {"id": 0}
task_id_counter = {"id": 0}
project_id_counter = {"id": 0}
