import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    IntegrationModel,
    IntegrationConnectionModel,
    IntegrationCredentialModel,
    IntegrationAuditLogModel
)

logger = logging.getLogger("ULTRON.Repositories.Integration")


class IntegrationRepository:
    """Repository managing integrations, connections, credentials, and audit logs with mandatory user_id tenant isolation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_connections(self, user_id: str) -> List[IntegrationConnectionModel]:
        stmt = select(IntegrationConnectionModel).where(
            IntegrationConnectionModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_connection(self, user_id: str, integration_id: str) -> IntegrationConnectionModel:
        conn = IntegrationConnectionModel(
            user_id=user_id,
            integration_id=integration_id,
            status="CONNECTED"
        )
        self.db.add(conn)
        await self.db.commit()
        await self.db.refresh(conn)
        return conn

    async def disconnect(self, user_id: str, integration_id: str) -> bool:
        stmt = delete(IntegrationConnectionModel).where(
            IntegrationConnectionModel.user_id == user_id,
            IntegrationConnectionModel.integration_id == integration_id
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    async def save_credential(
        self,
        user_id: str,
        integration_id: str,
        encrypted_access_token: Optional[str] = None,
        encrypted_refresh_token: Optional[str] = None,
        encrypted_api_key: Optional[str] = None,
        expires_at: Optional[Any] = None,
        scopes: Optional[List[str]] = None
    ) -> IntegrationCredentialModel:
        stmt = select(IntegrationCredentialModel).where(
            IntegrationCredentialModel.user_id == user_id,
            IntegrationCredentialModel.integration_id == integration_id.lower()
        )
        res = await self.db.execute(stmt)
        cred = res.scalars().first()
        if cred:
            cred.encrypted_access_token = encrypted_access_token
            cred.encrypted_refresh_token = encrypted_refresh_token
            cred.encrypted_api_key = encrypted_api_key
            cred.expires_at = expires_at
            cred.scopes_json = scopes
        else:
            cred = IntegrationCredentialModel(
                user_id=user_id,
                integration_id=integration_id.lower(),
                encrypted_access_token=encrypted_access_token,
                encrypted_refresh_token=encrypted_refresh_token,
                encrypted_api_key=encrypted_api_key,
                expires_at=expires_at,
                scopes_json=scopes
            )
            self.db.add(cred)
        await self.db.commit()
        await self.db.refresh(cred)
        return cred

    async def get_credential(self, user_id: str, integration_id: str) -> Optional[IntegrationCredentialModel]:
        stmt = select(IntegrationCredentialModel).where(
            IntegrationCredentialModel.user_id == user_id,
            IntegrationCredentialModel.integration_id == integration_id.lower()
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def delete_credential(self, user_id: str, integration_id: str) -> bool:
        stmt = delete(IntegrationCredentialModel).where(
            IntegrationCredentialModel.user_id == user_id,
            IntegrationCredentialModel.integration_id == integration_id.lower()
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    async def record_audit_log(
        self,
        user_id: str,
        integration_id: str,
        operation_id: str,
        status: str,
        duration_ms: int = 0,
        details: Optional[str] = None
    ) -> IntegrationAuditLogModel:
        log = IntegrationAuditLogModel(
            user_id=user_id,
            integration_id=integration_id,
            operation_id=operation_id,
            status=status,
            duration_ms=duration_ms,
            details=details
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_audit_logs(self, user_id: str, limit: int = 50) -> List[IntegrationAuditLogModel]:
        stmt = select(IntegrationAuditLogModel).where(
            IntegrationAuditLogModel.user_id == user_id
        ).order_by(IntegrationAuditLogModel.created_at.desc()).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

