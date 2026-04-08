from __future__ import annotations

import importlib
import logging
from collections.abc import Iterator
from typing import Any

RouterLoad = tuple[str, str, Any]

ROUTER_SPECS = [
    {"module": "backend.routes.auth", "attrs": ("router",), "prefix": "/api/v1"},
    {"module": "backend.routes.auth_me", "attrs": ("router",), "prefix": "/api/v1"},
    {"module": "backend.routes.legacy_api_compat", "attrs": ("router",)},
    {"module": "backend.routes.auth_reset", "attrs": ("router",), "prefix": "/api/v1"},
    {"module": "backend.routes.legal_consultant_learning", "attrs": ("router",)},
    {"module": "backend.routes.legal_bot", "attrs": ("router",)},
    {"module": "backend.routes.compliance_routes", "attrs": ("router",)},
    {"module": "backend.routes.bot_os", "attrs": ("router",)},
    {"module": "backend.routes.bots_available", "attrs": ("router", "compat_router")},
    {"module": "backend.routes.bots_subscription", "attrs": ("router",)},
    {"module": "backend.routes.frontend_compat_routes", "attrs": ("router",), "prefix": "/api/v1"},
    {"module": "backend.routes.frontend_compat_routes", "attrs": ("router",)},
    {"module": "backend.routes.social_media_routes", "attrs": ("public_router", "router"), "prefix": "/api/v1/social-media"},
    {"module": "backend.routes.social_media_routes", "attrs": ("public_router", "router")},
    {"module": "backend.routes.meta_data_api", "attrs": ("router",)},
    {"module": "backend.routes.excel_upload", "attrs": ("router",)},
    {"module": "backend.routes.integrations_api", "attrs": ("router",)},
    {"module": "backend.routes.emails", "attrs": ("router",)},
    {"module": "backend.routes.email_center", "attrs": ("router",)},
    {"module": "backend.routes.email_ai_stats", "attrs": ("router",)},
    {"module": "backend.routes.ai_documents_manager", "attrs": ("router",), "prefix": ""},
    {"module": "backend.routes.ai_operations_api", "attrs": ("router",), "prefix": "/api/v1"},
    {"module": "backend.routes.ai_dev_bot", "attrs": ("router",)},
    {"module": "backend.routes.documents_upload_routes", "attrs": ("router",)},
    {"module": "backend.routes.financial", "attrs": ("router",)},
    {"module": "backend.routes.finance_routes", "attrs": ("router",)},
    {"module": "backend.routes.finance_reports", "attrs": ("router",)},
    {"module": "backend.routes.unified_finance_routes", "attrs": ("router",)},
    {"module": "backend.routes.fleet_live_routes", "attrs": ("router",)},
    {"module": "backend.routes.transport_tracking_api", "attrs": ("router",)},
    {"module": "backend.routes.webhooks", "attrs": ("router",)},
    {"module": "backend.routes.channels_webhooks", "attrs": ("router",)},
    {"module": "backend.routes.stripe_webhooks", "attrs": ("router",)},
    {"module": "backend.routes.wise_webhooks", "attrs": ("router",)},
    {"module": "backend.routes.quo_webhooks", "attrs": ("router",), "prefix": "/api/v1/webhooks/quo"},
    {"module": "backend.routes.call_webhooks", "attrs": ("router",)},
    {"module": "backend.webhooks.payment_webhooks", "attrs": ("router",)},
    {"module": "backend.routes.loadboards_routes", "attrs": ("router",)},
    {"module": "backend.routes.truckerpath_routes", "attrs": ("router", "compat_router")},
    {"module": "backend.routes.truckerpath_webhook", "attrs": ("router",)},
    {"module": "backend.routes.support_routes", "attrs": ("router",)},
    {"module": "backend.api.routes.live_support", "attrs": ("router",)},
    {"module": "backend.routes.customer_service_api", "attrs": ("router",)},
    {"module": "backend.routes.customer_service_ws", "attrs": ("router",)},
    {"module": "backend.routes.admin_audit", "attrs": ("router",)},
    {"module": "backend.routes.admin_api_connections", "attrs": ("router",), "prefix": "/api/v1/admin/api-connections"},
    {"module": "backend.routes.admin_data_sources", "attrs": ("router",)},
    {"module": "backend.routes.admin_platform_settings", "attrs": ("router", "public_router")},
    {"module": "backend.routes.admin_portal_requests", "attrs": ("portal_router_v1", "router")},
    {"module": "backend.routes.portal_requests", "attrs": ("router",)},
    {"module": "backend.routes.admin_unified", "attrs": ("router",)},
    {"module": "backend.routes.admin_users", "attrs": ("router",), "prefix": "/api/v1/admin/users"},
    {"module": "backend.routes.tenants", "attrs": ("router",), "prefix": "/api/v1/tenants"},
    {"module": "backend.routes.partners", "attrs": ("router",)},
    {"module": "backend.routes.tenant_admin", "attrs": ("router",)},
    {"module": "backend.routes.tms_requests_admin", "attrs": ("router",)},
    {"module": "backend.routes.social_media_routes", "attrs": ("router",), "prefix": "/api/v1/admin/social-media"},
    {"module": "backend.billing.routes", "attrs": ("router", "admin_router")},
    {"module": "backend.routes.notification_routes", "attrs": ("router",)},
    {"module": "backend.routes.platform_expenses_routes", "attrs": ("router",)},
    {"module": "backend.routes.payment_routes", "attrs": ("router",)},
    {"module": "backend.routes.payment_gateway", "attrs": ("router",)},
    {"module": "backend.routes.sales_bot", "attrs": ("router",), "prefix": "/api/v1"},
    {"module": "backend.routes.security_bot", "attrs": ("router",), "prefix": "/api/v1"},
    {"module": "backend.routes.system_admin_bot", "attrs": ("router",), "prefix": "/api/v1/system-admin"},
    {"module": "backend.routes.system_manager_bot", "attrs": ("router",), "prefix": "/api/v1/system-manager"},
    {"module": "backend.routes.marketing_bot", "attrs": ("router",)},
    {"module": "backend.routes.maintenance_center", "attrs": ("router",)},
    {"module": "backend.routes.trainer_bot", "attrs": ("router",)},
    {"module": "backend.routes.shipments_pg_api", "attrs": ("router",)},
    {"module": "backend.routes.carriers", "attrs": ("router",)},
    {"module": "backend.routes.shippers", "attrs": ("router",)},
    {"module": "backend.routes.users_routes", "attrs": ("router",)},
]


def iter_registered_routers(logger: logging.Logger | None = None) -> Iterator[RouterLoad]:
    active_logger = logger or logging.getLogger(__name__)
    for spec in ROUTER_SPECS:
        module_name = spec["module"]
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            active_logger.warning("Skipping router module %s: %s", module_name, exc)
            continue

        for attr_name in spec["attrs"]:
            router = getattr(module, attr_name, None)
            if router is not None:
                prefix = spec.get("prefix")
                if prefix is None:
                    router_prefix = str(getattr(router, "prefix", "") or "").strip()
                    if router_prefix:
                        prefix = ""
                    else:
                        prefix = f"/api/v1/{'admin' if 'admin' in spec['module'] else 'api'}"
                yield f"{module_name}.{attr_name}", prefix, router
