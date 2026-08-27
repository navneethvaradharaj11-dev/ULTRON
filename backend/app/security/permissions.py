from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Permission

PermissionLevel = Literal["allow", "deny", "require_approval"]

# Default tool permission levels
SENSITIVE_TOOLS = {"filesystem_write", "shell_execution", "external_api_call", "delete_file"}


class PermissionManager:
    """Manages tool execution permissions for users."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_permission(self, user_id: str, tool_name: str) -> PermissionLevel:
        """Check user permission level for a given tool."""
        stmt = select(Permission).where(
            Permission.user_id == user_id,
            Permission.tool_name == tool_name
        )
        result = await self.db.execute(stmt)
        perm = result.scalars().first()

        if perm:
            return perm.permission_level  # type: ignore

        # Default rules if no explicit override exists
        if tool_name in SENSITIVE_TOOLS:
            return "require_approval"
        return "allow"

    async def set_permission(self, user_id: str, tool_name: str, level: PermissionLevel) -> Permission:
        stmt = select(Permission).where(
            Permission.user_id == user_id,
            Permission.tool_name == tool_name
        )
        result = await self.db.execute(stmt)
        perm = result.scalars().first()

        if perm:
            perm.permission_level = level
        else:
            perm = Permission(user_id=user_id, tool_name=tool_name, permission_level=level)
            self.db.add(perm)

        await self.db.commit()
        await self.db.refresh(perm)
        return perm
