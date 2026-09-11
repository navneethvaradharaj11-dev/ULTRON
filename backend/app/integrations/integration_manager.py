import time
import logging
from typing import Dict, Any, Optional

from app.integrations.contracts import IntegrationExecutionRequest, IntegrationExecutionResponse
from app.integrations.integration_registry import integration_registry
from app.integrations.credential_manager import credential_manager
from app.integrations.integration_policy import IntegrationPolicy
from app.integrations.integration_security import IntegrationSecurity
from app.integrations.rate_limiter import integration_rate_limiter, IntegrationRateLimitedError
from app.integrations.health_manager import health_manager

logger = logging.getLogger("ULTRON.Integrations.Manager")


class IntegrationManager:
    """Central integration execution manager processing scope validation, security policies, approval gates,
    rate limits, execution, payload sanitization, and audit logging.
    """

    def __init__(self, adapters: Optional[Dict[str, Any]] = None):
        self.adapters = adapters or {}

    def register_adapter(self, integration_id: str, adapter_instance: Any) -> None:
        self.adapters[integration_id.lower()] = adapter_instance

    async def execute_operation(self, request: IntegrationExecutionRequest) -> IntegrationExecutionResponse:
        start_t = time.time()
        integ_id = request.integration_id.lower()
        op_id = request.operation_id.lower()

        # 1. Resolve Integration & Descriptor
        descriptor = integration_registry.get(integ_id)
        if not descriptor:
            return IntegrationExecutionResponse(
                status="FAILED",
                error_message=f"INTEGRATION_NOT_FOUND: Integration '{integ_id}' is not registered.",
                duration_ms=0
            )

        operation = descriptor.supported_operations.get(op_id)
        if not operation:
            return IntegrationExecutionResponse(
                status="FAILED",
                error_message=f"OPERATION_NOT_FOUND: Operation '{op_id}' is not supported by integration '{integ_id}'.",
                duration_ms=0
            )

        # 2. Rate Limiting Check
        try:
            integration_rate_limiter.check_rate_limit(request.user_id, integ_id, op_id)
        except IntegrationRateLimitedError as err:
            health_manager.set_status(integ_id, "RATE_LIMITED")
            return IntegrationExecutionResponse(
                status="RATE_LIMITED",
                error_message=str(err),
                duration_ms=int((time.time() - start_t) * 1000)
            )

        # 3. Credential & Scope Check
        cred = credential_manager.get_decrypted_credential(request.user_id, integ_id)
        granted_scopes = cred.scopes if (cred and cred.scopes is not None) else operation.required_scopes

        is_allowed, requires_approval, reason = IntegrationPolicy.evaluate_operation_policy(
            integration_id=integ_id,
            operation_id=op_id,
            required_scopes=operation.required_scopes,
            granted_scopes=granted_scopes
        )


        if not is_allowed:
            return IntegrationExecutionResponse(
                status="FAILED",
                error_message=reason,
                duration_ms=int((time.time() - start_t) * 1000)
            )

        if requires_approval or operation.requires_approval:
            return IntegrationExecutionResponse(
                status="REQUIRES_APPROVAL",
                error_message=f"APPROVAL_REQUIRED: Operation '{op_id}' on '{integ_id}' requires explicit human approval.",
                duration_ms=int((time.time() - start_t) * 1000)
            )

        # 4. Resolve Adapter & Execute
        adapter = self.adapters.get(integ_id)
        if not adapter:
            return IntegrationExecutionResponse(
                status="FAILED",
                error_message=f"ADAPTER_UNAVAILABLE: Adapter instance for '{integ_id}' is not initialized.",
                duration_ms=int((time.time() - start_t) * 1000)
            )

        try:
            raw_result = await adapter.execute(op_id, request.parameters)
            duration_ms = int((time.time() - start_t) * 1000)

            # 5. Sanitize Output Data
            sanitized_result = self._sanitize_response_payload(raw_result, integ_id)

            return IntegrationExecutionResponse(
                status="SUCCESS",
                result=sanitized_result,
                duration_ms=duration_ms
            )

        except Exception as exc:
            duration_ms = int((time.time() - start_t) * 1000)
            logger.error("Integration execution error on '%s.%s': %s", integ_id, op_id, exc)
            return IntegrationExecutionResponse(
                status="FAILED",
                error_message=f"EXECUTION_ERROR: {str(exc)}",
                duration_ms=duration_ms
            )

    def _sanitize_response_payload(self, data: Any, provider: str) -> Any:
        if isinstance(data, dict):
            return {k: self._sanitize_response_payload(v, provider) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_response_payload(item, provider) for item in data]
        elif isinstance(data, str):
            return IntegrationSecurity.mask_secrets(data)
        return data
