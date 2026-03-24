"""
Database models for the application
"""

# Import all models to make them accessible via: from app.models import User, Task, Project
from app.models.user import User
from app.models.task import Task
from app.models.project import Project

# __all__ defines the public API - what gets imported when using "from app.models import *"
# Helps IDEs with autocomplete and makes code intent clear
__all__ = ["User", "Task", "Project"]
