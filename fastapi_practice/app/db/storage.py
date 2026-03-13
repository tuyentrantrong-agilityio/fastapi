# In-memory database storage

users_db = {}  # {user_id: user_data}
tasks_db = {}  # {task_id: task_data}
projects_db = {}  # {project_id: project_data}
refresh_tokens_db = {}  # {token_hash: {user_id, expires_at, created_at}} - stores SHA256 hash of refresh tokens

# ID counters - using dict for mutable reference
user_id_counter = {"id": 0}
task_id_counter = {"id": 0}
project_id_counter = {"id": 0}
