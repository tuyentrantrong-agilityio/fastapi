from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(SQLModel, table=True):
    """Refresh token for JWT token renewal"""

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    user: Optional["User"] = Relationship(
        back_populates="refresh_tokens",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    token_hash: str = Field(unique=True, index=True)  # SHA256 hash of actual token
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    is_revoked: bool = Field(default=False)  # For logout
