"""Background email tasks - called by BackgroundTasks.

Phase 1 (Current): Uses FastAPI BackgroundTasks (simple, no setup)
Phase 2 (Future): Migrate to Celery + Redis (scalable, persistent)

Why BackgroundTasks is good for learning:
  - No external dependencies (already in FastAPI)
  - Synchronous code is easier to debug
  - Runs in thread pool on same process

Migration to Celery (Phase 2):
  - Just replace task functions with @celery_app.task decorator
  - Endpoint code stays the same (use dispatcher pattern)
  - See PHASE_2_MIGRATION.md for details
"""

import logging
from typing import Optional

from ..services.email_service import email_service

logger = logging.getLogger(__name__)


async def send_welcome_email_task(
    email: str,
    user_name: str = "User",
) -> None:
    """Send welcome email after user registration.

    Args:
        email: Recipient email address
        user_name: User's name (optional, defaults to "User")

    Note:
        - Called by FastAPI BackgroundTasks
        - Runs asynchronously in thread pool
        - Errors logged but don't block HTTP response
    """
    subject = "Welcome to FastAPI Practice!"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>Welcome, {user_name}! 🎉</h1>
            <p>Thank you for registering with our FastAPI Practice application.</p>
            <p>Your account is ready to use. Start creating tasks and projects!</p>
            <hr />
            <p style="color: #666; font-size: 12px;">
                If you didn't register for this account, please ignore this email.
            </p>
        </body>
    </html>
    """
    plain_content = f"""
Welcome, {user_name}!

Thank you for registering. Your account is ready to use.
Start creating tasks and projects!

Regards,
FastAPI Practice Team
    """

    success = await email_service.send_email(
        to=email,
        subject=subject,
        html_content=html_content,
        plain_content=plain_content,
    )

    if not success:
        logger.warning(f"Failed to send welcome email to {email}, but task completed.")


async def send_password_reset_email_task(
    email: str,
    reset_link: str,
    user_name: str = "User",
) -> None:
    """Send password reset email.

    Args:
        email: Recipient email address
        reset_link: Password reset URL for user to click
        user_name: User's name (optional, defaults to "User")

    # Example usage: Only call from router with background_tasks.add_task
    """
    subject = "Reset Your Password - FastAPI Practice"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>Password Reset Request</h1>
            <p>Hi {user_name},</p>
            <p>We received a request to reset your password.</p>
            <p>
                <a href="{reset_link}" 
                   style="background-color: #4CAF50; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p style="color: #666;">This link expires in 30 minutes.</p>
            <p style="color: #666; font-size: 12px;">
                If you didn't request a password reset, please ignore this email.
            </p>
        </body>
    </html>
    """
    plain_content = f"""
Password Reset Request

Hi {user_name},

Click here to reset your password:
{reset_link}

This link expires in 30 minutes.

Regards,
FastAPI Practice Team
    """

    success = await email_service.send_email(
        to=email,
        subject=subject,
        html_content=html_content,
        plain_content=plain_content,
    )

    if not success:
        logger.warning(
            f"Failed to send password reset email to {email}, but task completed."
        )


async def send_task_assigned_email_task(
    email: str,
    user_name: str,
    task_title: str,
    task_id: int,
    assigned_by: str = "Administrator",
) -> None:
    """Send notification email when task is assigned to user.

    Args:
        email: Recipient email address
        user_name: User's name
        task_title: Title of assigned task
        task_id: ID of the task
        assigned_by: Name of person who assigned (optional)

    # Example usage: Only call from router with background_tasks.add_task
    """
    subject = f"New Task Assigned: {task_title}"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>Task Assigned to You 📋</h1>
            <p>Hi {user_name},</p>
            <p><strong>{assigned_by}</strong> assigned you a new task:</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>{task_title}</h3>
                <p><small>Task ID: {task_id}</small></p>
            </div>
            <p>Log in to the application to view details and update progress.</p>
        </body>
    </html>
    """
    plain_content = f"""
Task Assigned to You

Hi {user_name},

{assigned_by} assigned you a new task:

{task_title}
Task ID: {task_id}

Log in to view details.

Regards,
FastAPI Practice Team
    """

    success = await email_service.send_email(
        to=email,
        subject=subject,
        html_content=html_content,
        plain_content=plain_content,
    )

    if not success:
        logger.warning(
            f"Failed to send task assignment email to {email}, but task completed."
        )
