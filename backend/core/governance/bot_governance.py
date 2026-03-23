from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib


class BotStatus(Enum):
    """Bot status lifecycle."""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class AccessLevel(Enum):
    """Access levels for bot capabilities."""

    READ_ONLY = "read_only"
    LIMITED = "limited"
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class BotPermission:
    id: str
    name: str
    description: str
    resource: str  # e.g., customers, invoices, system
    action: str  # e.g., read, write, delete, execute
    risk_level: int  # 1-5


@dataclass
class BotManifest:
    bot_id: str
    name: str
    version: str
    description: str
    author: str
    created_at: datetime
    updated_at: datetime
    required_permissions: List[BotPermission]
    external_apis: List[Dict[str, Any]]
    database_access: List[str]
    constraints: Dict[str, Any]
    code_hash: str
    config_hash: str
    signature: Optional[str]


class BotGovernanceSystem:
    """In-memory bot governance registry and workflows.

    This provides validation, approval, and activation workflows.
    Persistence can be added later via SQLAlchemy models if needed.
    """

    def __init__(self) -> None:
        self.bot_registry: Dict[str, Dict[str, Any]] = {}
        self.permission_matrix = self._load_permission_matrix()
        self.approval_workflow = self._setup_approval_workflow()

    def _load_permission_matrix(self) -> Dict[str, Any]:
        """Static permission matrix; replace with DB/policy later."""
        return {
            "sales_bot": {
                "allowed_resources": ["customers", "leads", "deals", "products"],
                "allowed_actions": ["read", "create", "update"],
                "denied_actions": ["delete", "export", "admin"],
                "access_level": AccessLevel.STANDARD,
            },
            "security_bot": {
                "allowed_resources": ["logs", "users", "sessions", "alerts"],
                "allowed_actions": ["read", "monitor", "alert"],
                "denied_actions": ["modify_users", "delete_logs"],
                "access_level": AccessLevel.ELEVATED,
            },
            "finance_bot": {
                "allowed_resources": ["invoices", "payments", "transactions"],
                "allowed_actions": ["read", "create", "update", "export"],
                "access_level": AccessLevel.STANDARD,
                "requires_approval": True,
            },
        }

    def _setup_approval_workflow(self) -> Dict[str, Any]:
        return {"required_roles": ["security_team", "operations", "management"], "min_approvals": 2}

    def _validate_permissions(self, manifest: BotManifest) -> Dict[str, Any]:
        violations: List[Dict[str, Any]] = []
        matrix = self.permission_matrix.get(manifest.name)
        if not matrix:
            return {"valid": False, "violations": ["bot not found in matrix"]}
        for perm in manifest.required_permissions:
            if perm.action in matrix.get("denied_actions", []):
                violations.append({"permission": perm.name, "reason": "action denied"})
        return {"valid": len(violations) == 0, "violations": violations}

    def _verify_security_signatures(self, manifest: BotManifest) -> Dict[str, Any]:
        issues: List[str] = []
        if not manifest.code_hash or not manifest.config_hash:
            issues.append("missing hashes")
        # Placeholder: verify signature if provided
        return {"valid": len(issues) == 0, "issues": issues}

    def _check_compatibility(self, manifest: BotManifest) -> Dict[str, Any]:
        return {"valid": True, "incompatibilities": []}

    def _initiate_review_workflow(self, bot_id: str) -> None:
        # Placeholder: could enqueue a task/notification
        return None

    def _all_approvals_received(self, bot_id: str) -> bool:
        bot = self.bot_registry[bot_id]
        return len(bot.get("approvals", [])) >= self.approval_workflow["min_approvals"]

    def _get_pending_approvals(self, bot_id: str) -> List[str]:
        return ["operations", "management"]

    def _generate_activation_keys(self, bot_id: str) -> Dict[str, str]:
        return {"key_id": hashlib.md5(bot_id.encode()).hexdigest()}

    def _assign_resources(self, bot_id: str, environment: str) -> Dict[str, Any]:
        return {"db": f"{environment}_db", "cache": f"{environment}_redis"}

    def _setup_monitoring(self, bot_id: str, environment: str) -> Dict[str, Any]:
        return {"alerts": True, "dashboard": f"/bots/{bot_id}"}

    def _generate_access_credentials(self, bot_id: str, environment: str) -> Dict[str, str]:
        token = hashlib.sha256(f"{bot_id}:{environment}".encode()).hexdigest()
        return {"token": token}

    def register_bot(self, manifest: BotManifest) -> Dict[str, Any]:
        perm_check = self._validate_permissions(manifest)
        if not perm_check["valid"]:
            return {"success": False, "error": "permissions not allowed", "details": perm_check["violations"]}

        sec_check = self._verify_security_signatures(manifest)
        if not sec_check["valid"]:
            return {"success": False, "error": "security verification failed", "details": sec_check["issues"]}

        compat_check = self._check_compatibility(manifest)
        if not compat_check["valid"]:
            return {"success": False, "error": "incompatible with system", "details": compat_check["incompatibilities"]}

        record = {
            "manifest": manifest,
            "status": BotStatus.UNDER_REVIEW,
            "registration_date": datetime.utcnow(),
            "review_history": [],
            "approvals": [],
            "activity_log": [],
        }
        self.bot_registry[manifest.bot_id] = record
        self._initiate_review_workflow(manifest.bot_id)
        return {"success": True, "bot_id": manifest.bot_id, "status": BotStatus.UNDER_REVIEW.value,
                "next_step": "waiting for security team review"}

    def approve_bot(self, bot_id: str, approver: str, comments: str = "") -> Dict[str, Any]:
        if bot_id not in self.bot_registry:
            return {"success": False, "error": "bot not registered"}
        bot = self.bot_registry[bot_id]
        if bot["status"] != BotStatus.UNDER_REVIEW:
            return {"success": False, "error": "bot not under review"}
        approval = {
            "approver": approver,
            "role": "security_team",
            "timestamp": datetime.utcnow(),
            "comments": comments,
            "decision": "approved",
        }
        bot["approvals"].append(approval)
        bot["review_history"].append({"action": "approval", "by": approver, "timestamp": datetime.utcnow(), "details": approval})
        if self._all_approvals_received(bot_id):
            bot["status"] = BotStatus.APPROVED
            activation_keys = self._generate_activation_keys(bot_id)
            return {"success": True, "message": "bot approved", "status": BotStatus.APPROVED.value,
                    "activation_keys": activation_keys,
                    "next_steps": ["activate bot", "configure monitoring", "production testing"]}
        return {"success": True, "message": "approval recorded; awaiting additional approvals",
                "pending_approvals": self._get_pending_approvals(bot_id)}

    def activate_bot(self, bot_id: str, environment: str) -> Dict[str, Any]:
        if bot_id not in self.bot_registry:
            return {"success": False, "error": "bot not registered"}
        bot = self.bot_registry[bot_id]
        if bot["status"] != BotStatus.APPROVED:
            return {"success": False, "error": f"bot not approved for activation. status: {bot['status'].value}"}
        if environment not in ("development", "staging", "production"):
            return {"success": False, "error": f"unsupported environment: {environment}"}
        activation_record = {
            "bot_id": bot_id,
            "environment": environment,
            "activated_at": datetime.utcnow(),
            "activated_by": "system",
            "status": "active",
            "resources_assigned": self._assign_resources(bot_id, environment),
            "monitoring_config": self._setup_monitoring(bot_id, environment),
        }
        if environment == "production":
            bot["status"] = BotStatus.ACTIVE
        bot["activity_log"].append({"action": "activation", "environment": environment, "timestamp": datetime.utcnow(), "details": activation_record})
        return {"success": True, "message": f"bot activated in {environment}",
                "activation_id": hashlib.md5(f"{bot_id}{environment}{datetime.utcnow()}".encode()).hexdigest(),
                "monitoring_dashboard": f"https://monitoring.company.com/bots/{bot_id}",
                "access_credentials": self._generate_access_credentials(bot_id, environment)}


# Singleton accessor
_GOVERNANCE: Optional[BotGovernanceSystem] = None


def get_governance() -> BotGovernanceSystem:
    global _GOVERNANCE
    if _GOVERNANCE is None:
        _GOVERNANCE = BotGovernanceSystem()
    return _GOVERNANCE
