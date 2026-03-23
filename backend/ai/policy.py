from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

# Correct import for local ai.roles.bot_permissions
from .roles.bot_permissions import (
    BOT_POLICIES,
    BOT_CAPABILITIES,
    VALID_REPORT_FLOWS,
    get_bot_policy,
    get_bot_capabilities,
    can_user_access_bot,
    get_accessible_bots,
    validate_report_flow,
)

# ============================================================
# Role handling & bypass
# ============================================================

BYPASS_ROLES = {"admin", "system_admin", "super_admin", "owner"}

ROLE_ALIASES = {
    "owner": "super_admin",
    "superadmin": "super_admin",
    "super-admin": "super_admin",
    "customer": "subscription_user",
    "client": "subscription_user",
}


def _normalize_role(role: Optional[str]) -> str:
    """Normalize role names and apply aliases."""
    if not role:
        return "user"
    key = str(role).strip().lower().replace(" ", "_")
    return ROLE_ALIASES.get(key, key)


def normalize_role(role: Optional[str]) -> str:
    """Public helper for other modules to normalize role names."""
    return _normalize_role(role)


# ============================================================
# Bot Access Policy
# ============================================================

class BotAccessPolicy:
    """
    Central AI bot access policy wrapper.
    All logic is driven by bot_permissions.py (single source of truth).
    """

    # --------------------------------------------------------
    # Visibility
    # --------------------------------------------------------

    @staticmethod
    def can_see_bot(
        user_role: str,
        user_features: Set[str],
        bot_key: str,
    ) -> Dict[str, Any]:
        normalized_role = _normalize_role(user_role)
        features = set(user_features or set())

        policy = get_bot_policy(bot_key)
        if not policy:
            return {
                "allowed": False,
                "reason": "bot_not_found",
                "message": f"Bot '{bot_key}' not found",
            }

        if getattr(policy, "hidden", False):
            return {
                "allowed": False,
                "reason": "bot_hidden",
                "message": f"Bot '{bot_key}' is hidden",
            }

        allowed_roles = set(getattr(policy, "visible_to_roles", set()))
        if normalized_role not in allowed_roles:
            return {
                "allowed": False,
                "reason": "role_not_allowed",
                "message": f"Role '{normalized_role}' is not allowed for bot '{bot_key}'",
                "required_roles": sorted(allowed_roles),
            }

        required_features = set(getattr(policy, "required_features", set()))
        missing_features = required_features - features

        # If user is not in bypass roles, missing features blocks access
        if missing_features and normalized_role not in BYPASS_ROLES:
            # keep single source-of-truth logic consistent (optional sanity check)
            if not can_user_access_bot(normalized_role, features, bot_key):
                return {
                    "allowed": False,
                    "reason": "feature_missing",
                    "message": f"Missing required features for bot '{bot_key}'",
                    "missing_features": sorted(missing_features),
                }
            return {
                "allowed": False,
                "reason": "feature_missing",
                "message": f"Missing required features for bot '{bot_key}'",
                "missing_features": sorted(missing_features),
            }

        return {
            "allowed": True,
            "reason": "access_granted",
            "message": f"Access granted to bot '{bot_key}'",
            "policy": {
                "visible_to_roles": sorted(allowed_roles),
                "required_features": sorted(required_features),
                "hidden": bool(getattr(policy, "hidden", False)),
            },
        }

    # --------------------------------------------------------
    # Execution
    # --------------------------------------------------------

    @staticmethod
    def can_run_bot(
        user_role: str,
        user_features: Set[str],
        bot_key: str,
        action: str = "run",
    ) -> Dict[str, Any]:
        base = BotAccessPolicy.can_see_bot(user_role, user_features, bot_key)
        if not base.get("allowed"):
            base.update(
                {
                    "action": action,
                    "bot_execution": False,
                }
            )
            return base

        normalized_role = _normalize_role(user_role)

        # Elevated actions require admin-level roles
        if action in {"configure", "monitor"}:
            if normalized_role not in BYPASS_ROLES:
                return {
                    "allowed": False,
                    "reason": "role_not_allowed",
                    "message": f"Action '{action}' requires elevated role",
                    "action": action,
                    "bot_execution": False,
                }

        capabilities = get_bot_capabilities(bot_key) or {}

        return {
            "allowed": True,
            "reason": "execution_granted",
            "message": f"Execution granted for bot '{bot_key}'",
            "action": action,
            "bot_execution": True,
            "bot_info": capabilities,
        }

    # --------------------------------------------------------
    # Listing
    # --------------------------------------------------------

    @staticmethod
    def list_available_bots(
        user_role: str,
        user_features: Set[str],
    ) -> Dict[str, Any]:
        normalized_role = _normalize_role(user_role)
        features = set(user_features or set())

        bots: List[Dict[str, Any]] = []

        for bot_key in BOT_POLICIES.keys():
            decision = BotAccessPolicy.can_see_bot(normalized_role, features, bot_key)
            if not decision.get("allowed"):
                continue

            caps = get_bot_capabilities(bot_key) or {}
            pol = get_bot_policy(bot_key)

            bots.append(
                {
                    "bot_key": bot_key,
                    "name": caps.get("name", bot_key),
                    "description": caps.get("description", ""),
                    "category": caps.get("category", ""),
                    "icon": caps.get("icon", ""),
                    "color": caps.get("color", ""),
                    "policy": {
                        "visible_to_roles": list(getattr(pol, "visible_to_roles", [])) if pol else [],
                        "required_features": list(getattr(pol, "required_features", [])) if pol else [],
                        "hidden": bool(getattr(pol, "hidden", False)) if pol else False,
                    },
                }
            )

        return {
            "user": {
                "role": normalized_role,
                "features": sorted(features),
            },
            "bots": bots,
            "count": len(bots),
        }

    # --------------------------------------------------------
    # Reporting flow validation
    # --------------------------------------------------------

    @staticmethod
    def validate_bot_report(
        sender_bot: str,
        receiver_bot: str,
        user_role: str,
    ) -> Dict[str, Any]:
        _ = user_role  # kept for future checks; currently unused

        if sender_bot not in VALID_REPORT_FLOWS:
            return {
                "valid": False,
                "reason": "sender_not_found",
                "message": f"Unknown sender '{sender_bot}'",
            }

        if not validate_report_flow(sender_bot, receiver_bot):
            return {
                "valid": False,
                "reason": "invalid_flow",
                "message": f"Invalid flow from '{sender_bot}' to '{receiver_bot}'",
                "valid_receivers": VALID_REPORT_FLOWS.get(sender_bot, []),
            }

        return {
            "valid": True,
            "reason": "valid_flow",
            "message": "Valid report flow",
            "flow_info": {
                "sender": sender_bot,
                "receiver": receiver_bot,
                "sender_name": (BOT_CAPABILITIES.get(sender_bot) or {}).get("name", sender_bot),
                "receiver_name": (BOT_CAPABILITIES.get(receiver_bot) or {}).get("name", receiver_bot),
            },
        }

    # --------------------------------------------------------
    # Report flows visible to user
    # --------------------------------------------------------

    @staticmethod
    def get_report_flows_for_user(
        user_role: str,
        user_features: Set[str],
    ) -> Dict[str, Any]:
        normalized_role = _normalize_role(user_role)
        features = set(user_features or set())

        # union of "can_see" evaluation and base helper (defensive)
        accessible_bots = {
            bot_key
            for bot_key in BOT_POLICIES.keys()
            if BotAccessPolicy.can_see_bot(normalized_role, features, bot_key).get("allowed")
        } | set(get_accessible_bots(normalized_role, features))

        flows: Dict[str, List[str]] = {}

        for sender, receivers in VALID_REPORT_FLOWS.items():
            if sender not in accessible_bots:
                continue

            allowed_receivers = [r for r in receivers if (r in accessible_bots) or (r == "human_executive")]
            if allowed_receivers:
                flows[sender] = allowed_receivers

        return {
            "user_role": normalized_role,
            "accessible_bots_count": len(accessible_bots),
            "report_flows": flows,
            "total_flows": sum(len(v) for v in flows.values()),
        }


# Singleton-like instance (import-safe)
bot_access_policy = BotAccessPolicy()
