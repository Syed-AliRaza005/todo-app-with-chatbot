from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class RevokedToken(SQLModel, table=True):
    """Revoked JWT token for server-side logout functionality"""

    token_jti: str = Field(primary_key=True, max_length=255)
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False
    )
    expires_at: datetime = Field(nullable=False)

    def __repr__(self) -> str:
        return f"<RevokedToken(jti={self.token_jti}, user_id={self.user_id})>"
