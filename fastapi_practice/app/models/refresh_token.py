from datetime import datetime
from typing import TYPE_CHECKING, Optional

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
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    is_revoked: bool = Field(default=False)  # For logout
