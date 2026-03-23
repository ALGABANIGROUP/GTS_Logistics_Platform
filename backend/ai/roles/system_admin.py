from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.admin_control import service
from backend.database.connection import SessionLocal


class SystemAdminBot:
    name = "system_admin"

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = str((payload or {}).get("action") or "").strip().lower()
        data = (payload or {}).get("data") or {}
        meta = (payload or {}).get("_execution_metadata") or {}
        actor_user_id = meta.get("user_id")

        audit_ctx = {
            "actor_user_id": actor_user_id,
            "ip": None,
        }

        handlers = {
            "org_chart_get": self._org_chart_get,
            "org_unit_create": self._org_unit_create,
            "org_unit_move": self._org_unit_move,
            "org_role_library_list": self._org_role_library_list,
            "role_create": self._role_create,
            "role_update": self._role_update,
            "role_assign": self._role_assign,
            "permission_template_list": self._permission_template_list,
            "permission_template_apply": self._permission_template_apply,
            "user_create": self._user_create,
            "user_update": self._user_update,
            "user_deactivate": self._user_deactivate,
            "session_list": self._session_list,
            "session_revoke": self._session_revoke,
            "audit_log_search": self._audit_log_search,
            "activity_summary": self._activity_summary,
            "alert_rule_create": self._alert_rule_create,
            "alert_rule_list": self._alert_rule_list,
        }

        if action not in handlers:
            return self._normalized(
                ok=False,
                action=action or "unknown",
                data={},
                warnings=[f"Unsupported action: {action}"],
                next_steps=["Use a supported action name."],
            )

        async with SessionLocal() as session:
            try:
                result = await handlers[action](session, data, audit_ctx, action)
                return self._normalized(ok=True, action=action, data=result)
            except Exception as exc:
                return self._normalized(
                    ok=False,
                    action=action,
                    data={},
                    warnings=[f"Action failed: {exc}"],
                    next_steps=["Check admin logs and request payload."],
                )

    async def process_message(self, message: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        ctx = context or {}
        payload = {
            "action": ctx.get("action") or "activity_summary",
            "data": ctx.get("data") or {},
            "_execution_metadata": ctx.get("_execution_metadata") or {},
            "message": message,
        }
        return await self.run(payload)

    async def status(self) -> Dict[str, Any]:
        return {
            "name": "AI System Admin",
            "description": "Administrative control bot for org, users, roles, and audit.",
            "status": "active",
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "name": "AI System Admin",
            "actions": [
                "org_chart_get",
                "org_unit_create",
                "org_unit_move",
                "org_role_library_list",
                "role_create",
                "role_update",
                "role_assign",
                "permission_template_list",
                "permission_template_apply",
                "user_create",
                "user_update",
                "user_deactivate",
                "session_list",
                "session_revoke",
                "audit_log_search",
                "activity_summary",
                "alert_rule_create",
                "alert_rule_list",
            ],
        }

    def _normalized(
        self,
        *,
        ok: bool,
        action: str,
        data: Dict[str, Any],
        warnings: Optional[List[str]] = None,
        next_steps: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "ok": ok,
            "action": action,
            "data": data,
            "warnings": warnings or [],
            "next_steps": next_steps or [],
        }

    async def _org_chart_get(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.get_org_tree(db, audit=audit, audit_action=action)

    async def _org_unit_create(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.create_org_unit(db, data, audit=audit, audit_action=action)

    async def _org_unit_move(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        unit_id = int(data.get("unit_id") or 0)
        return await service.move_org_unit(
            db, unit_id, data, audit=audit, audit_action=action
        )

    async def _org_role_library_list(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.list_role_library(db, audit=audit, audit_action=action)

    async def _role_create(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.create_role(db, data, audit=audit, audit_action=action)

    async def _role_update(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        role_id = int(data.get("role_id") or 0)
        return await service.update_role(db, role_id, data, audit=audit, audit_action=action)

    async def _role_assign(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        user_id = int(data.get("user_id") or 0)
        return await service.assign_user_role(db, user_id, data, audit=audit, audit_action=action)

    async def _permission_template_list(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.list_permission_templates(db, audit=audit, audit_action=action)

    async def _permission_template_apply(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        template_id = int(data.get("template_id") or 0)
        return await service.apply_permission_template(
            db, template_id, data, audit=audit, audit_action=action
        )

    async def _user_create(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.create_user(db, data, audit=audit, audit_action=action)

    async def _user_update(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        user_id = int(data.get("user_id") or 0)
        return await service.update_user(db, user_id, data, audit=audit, audit_action=action)

    async def _user_deactivate(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        user_id = int(data.get("user_id") or 0)
        return await service.deactivate_user(db, user_id, data, audit=audit, audit_action=action)

    async def _session_list(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.list_sessions(db, audit=audit, audit_action=action)

    async def _session_revoke(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        session_id = int(data.get("session_id") or 0)
        return await service.revoke_session(db, session_id, data, audit=audit, audit_action=action)

    async def _audit_log_search(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.search_audit_logs(db, data, audit=audit, audit_action=action)

    async def _activity_summary(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.activity_summary(db, audit=audit, audit_action=action)

    async def _alert_rule_create(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.create_alert_rule(db, data, audit=audit, audit_action=action)

    async def _alert_rule_list(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        audit: Dict[str, Any],
        action: str,
    ) -> Dict[str, Any]:
        return await service.list_alert_rules(db, audit=audit, audit_action=action)

