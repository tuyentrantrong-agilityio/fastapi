from typing import Dict
from models import UserInDB


fake_users_db: Dict[str, UserInDB] = {}
fake_tasks_db: Dict[int, Dict] = {}
user_id_counter = 0
task_id_counter = 0
