"""
Information Coordinator Bot
Single source of truth, conflict detection, and cross-bot data coordination.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import copy
import hashlib
import json
import re


class InformationCoordinatorBot:
    """Coordinates shared data quality and consistency across the AI bot system."""

    def __init__(self) -> None:
        self.name = "information_coordinator"
        self.display_name = "AI Information Coordinator"
        self.description = "Coordinates shared data, validates records, and resolves conflicts"
        self.version = "2.0.0"
        self.mode = "single_source_of_truth"
        self.is_active = True

        now = datetime.now(timezone.utc)
        self.data_sources: List[Dict[str, Any]] = [
            {
                "source_code": "CUSTOMER_SERVICE",
                "source_name": "AI Customer Service",
                "source_type": "internal_bot",
                "data_categories": ["customers", "tickets", "feedback"],
                "update_frequency": "real_time",
                "priority": 3,
                "reliability_score": 9.5,
                "is_active": True,
                "last_sync": (now - timedelta(minutes=7)).isoformat(),
            },
            {
                "source_code": "DISPATCHER",
                "source_name": "AI Dispatcher",
                "source_type": "internal_bot",
                "data_categories": ["shipments", "drivers", "routes"],
                "update_frequency": "real_time",
                "priority": 2,
                "reliability_score": 9.1,
                "is_active": True,
                "last_sync": (now - timedelta(minutes=5)).isoformat(),
            },
            {
                "source_code": "SALES",
                "source_name": "AI Sales Bot",
                "source_type": "internal_bot",
                "data_categories": ["customers", "deals", "pricing"],
                "update_frequency": "hourly",
                "priority": 1,
                "reliability_score": 8.8,
                "is_active": True,
                "last_sync": (now - timedelta(minutes=22)).isoformat(),
            },
            {
                "source_code": "FINANCE",
                "source_name": "AI Finance Bot",
                "source_type": "internal_bot",
                "data_categories": ["invoices", "payments", "partners"],
                "update_frequency": "hourly",
                "priority": 1,
                "reliability_score": 9.8,
                "is_active": True,
                "last_sync": (now - timedelta(minutes=14)).isoformat(),
            },
            {
                "source_code": "MAPLELOAD",
                "source_name": "AI MapleLoad Canada",
                "source_type": "internal_bot",
                "data_categories": ["international", "carriers", "expansion"],
                "update_frequency": "daily",
                "priority": 5,
                "reliability_score": 8.9,
                "is_active": True,
                "last_sync": (now - timedelta(hours=3)).isoformat(),
            },
        ]
        self.unified_entities: List[Dict[str, Any]] = [
            {
                "entity_type": "customer",
                "entity_id": "CUST001",
                "data": {
                    "name": "Al Amal Co.",
                    "email": "info@alamal.com",
                    "phone": "+966501111111",
                    "tier": "gold",
                    "city": "Riyadh",
                    "last_updated": (now - timedelta(hours=4)).isoformat(),
                },
                "sources_used": ["SALES", "CUSTOMER_SERVICE"],
                "confidence": {
                    "overall": 93.0,
                    "by_field": {
                        "name": 100.0,
                        "email": 100.0,
                        "phone": 66.7,
                        "tier": 100.0,
                        "city": 100.0,
                    },
                },
                "source_of_truth": "SALES",
                "last_verified": (now - timedelta(hours=2)).isoformat(),
                "created_at": (now - timedelta(days=30)).isoformat(),
            },
            {
                "entity_type": "shipment",
                "entity_id": "SHP1001",
                "data": {
                    "shipment_number": "SHP1001",
                    "customer_id": "CUST001",
                    "origin_city": "Riyadh",
                    "destination_city": "Jeddah",
                    "status": "in_transit",
                    "driver": "Driver-24",
                    "last_updated": (now - timedelta(minutes=42)).isoformat(),
                },
                "sources_used": ["DISPATCHER", "OPERATIONS_MANAGER"],
                "confidence": {
                    "overall": 96.0,
                    "by_field": {
                        "shipment_number": 100.0,
                        "customer_id": 100.0,
                        "origin_city": 100.0,
                        "destination_city": 100.0,
                        "status": 100.0,
                        "driver": 76.0,
                    },
                },
                "source_of_truth": "DISPATCHER",
                "last_verified": (now - timedelta(minutes=18)).isoformat(),
                "created_at": (now - timedelta(days=4)).isoformat(),
            },
        ]
        self.conflicts: List[Dict[str, Any]] = [
            {
                "conflict_id": "CONF001",
                "entity_type": "customer",
                "entity_identifier": "CUST001",
                "field_name": "phone",
                "values_from_sources": {
                    "SALES": "+966501111111",
                    "CUSTOMER_SERVICE": "+966502222222",
                },
                "detected_at": (now - timedelta(hours=6)).isoformat(),
                "severity": "high",
                "status": "open",
                "resolution_method": None,
                "resolved_value": None,
                "resolved_by": None,
                "resolved_at": None,
            }
        ]
        self.audit_logs: List[Dict[str, Any]] = [
            {
                "log_id": "LOG001",
                "timestamp": (now - timedelta(hours=5)).isoformat(),
                "entity_type": "customer",
                "entity_id": "CUST001",
                "field": "email",
                "old_value": "sales@alamal.com",
                "new_value": "info@alamal.com",
                "changed_by": "system",
                "source_bot": "SALES",
                "reason": "Normalized canonical customer email",
            },
            {
                "log_id": "LOG002",
                "timestamp": (now - timedelta(hours=2, minutes=15)).isoformat(),
                "entity_type": "shipment",
                "entity_id": "SHP1001",
                "field": "status",
                "old_value": "booked",
                "new_value": "in_transit",
                "changed_by": "dispatcher_sync",
                "source_bot": "DISPATCHER",
                "reason": "Route execution update",
            },
        ]
        self.unified_reports: List[Dict[str, Any]] = []
        self.info_requests: List[Dict[str, Any]] = []

    async def run(self, payload: dict) -> dict:
        """Main shared-runtime entrypoint."""
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or payload.get("meta", {}).get("action") or "status"

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "data_sources":
            return await self.get_data_sources()
        if action == "receive_data":
            source = str(context.get("source") or payload.get("source") or "unknown")
            data = context.get("data") or payload.get("data") or {}
            return await self.receive_data(source, data)
        if action == "request_data":
            entity_type = str(context.get("entity_type") or payload.get("entity_type") or "")
            entity_id = str(context.get("entity_id") or payload.get("entity_id") or "")
            fields = context.get("fields") or payload.get("fields")
            return await self.request_data(entity_type, entity_id, fields)
        if action == "validate_data":
            data = context.get("data") or payload.get("data") or {}
            schema = context.get("schema") or payload.get("schema") or {}
            return await self.validate_data(data, schema)
        if action == "get_conflicts":
            status = str(context.get("status") or payload.get("status") or "open")
            return await self.get_conflicts(status)
        if action == "detect_conflicts":
            items = context.get("records") or payload.get("records") or []
            return await self.detect_conflicts(items)
        if action == "resolve_conflict":
            conflict_id = str(context.get("conflict_id") or payload.get("conflict_id") or "")
            strategy = str(context.get("strategy") or payload.get("strategy") or "")
            return await self.resolve_conflict(conflict_id, strategy)
        if action == "conflict_suggestions":
            conflict_id = str(context.get("conflict_id") or payload.get("conflict_id") or "")
            return await self.get_resolution_suggestions(conflict_id)
        if action == "unified_entity":
            entity_type = str(context.get("entity_type") or payload.get("entity_type") or "customer")
            entity_id = str(context.get("entity_id") or payload.get("entity_id") or "")
            records = context.get("records") or payload.get("records") or []
            return await self.create_unified_entity(entity_type, entity_id, records)
        if action == "entity_history":
            entity_type = str(context.get("entity_type") or payload.get("entity_type") or "")
            entity_id = str(context.get("entity_id") or payload.get("entity_id") or "")
            return await self.get_entity_history(entity_type, entity_id)
        if action == "audit_log":
            days = int(context.get("days") or payload.get("days") or 7)
            return await self.get_audit_log(days)
        if action == "audit_report":
            days = int(context.get("days") or payload.get("days") or 30)
            return await self.generate_audit_report(days)
        if action == "data_quality":
            data = context.get("data") or payload.get("data")
            entity_type = context.get("entity_type") or payload.get("entity_type")
            if isinstance(data, dict):
                return await self.assess_data_quality(data)
            return await self.check_data_quality(entity_type)
        if action == "integrity_checks":
            return await self.get_integrity_checks()
        if action == "search_entities":
            criteria = context.get("criteria") or payload.get("criteria") or {}
            return await self.search_entities(criteria)
        if action == "search":
            query = str(context.get("query") or payload.get("query") or "")
            entity_type = context.get("entity_type") or payload.get("entity_type")
            return await self.search(query, entity_type)
        if action == "generate_report":
            report_type = str(context.get("report_type") or payload.get("report_type") or "daily")
            return await self.generate_report(report_type)
        return {"ok": False, "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Handle explicit context actions and basic natural-language requests."""
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})

        message_lower = (message or "").lower()
        if "dashboard" in message_lower or "overview" in message_lower:
            return await self.get_dashboard()
        if "source" in message_lower:
            return await self.get_data_sources()
        if "conflict" in message_lower:
            return await self.detect_conflicts([])
        if "audit" in message_lower or "history" in message_lower:
            return await self.generate_audit_report(30)
        if "quality" in message_lower:
            return await self.get_integrity_checks()
        return await self.status()

    async def status(self) -> dict:
        """Return current runtime status."""
        open_conflicts = len([item for item in self.conflicts if item["status"] == "open"])
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "data_sources": len(self.data_sources),
            "unified_entities": len(self.unified_entities),
            "open_conflicts": open_conflicts,
            "audit_events": len(self.audit_logs),
            "message": "Information coordination is active",
        }

    async def config(self) -> dict:
        """Return supported capabilities."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "data_sources",
                "receive_data",
                "request_data",
                "validate_data",
                "get_conflicts",
                "detect_conflicts",
                "resolve_conflict",
                "conflict_suggestions",
                "unified_entity",
                "entity_history",
                "audit_log",
                "audit_report",
                "data_quality",
                "integrity_checks",
                "search",
                "search_entities",
                "generate_report",
            ],
        }

    async def get_dashboard(self) -> dict:
        """Return the main coordination dashboard."""
        active_sources = [source for source in self.data_sources if source["is_active"]]
        open_conflicts = [conflict for conflict in self.conflicts if conflict["status"] == "open"]
        avg_quality = round(
            sum(entity["confidence"]["overall"] for entity in self.unified_entities) / max(1, len(self.unified_entities)),
            2,
        )

        return {
            "ok": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overview": {
                "active_sources": len(active_sources),
                "unified_entities": len(self.unified_entities),
                "open_conflicts": len(open_conflicts),
                "data_quality_score": avg_quality,
                "single_source_of_truth": True,
            },
            "source_health": copy.deepcopy(active_sources),
            "conflicts": copy.deepcopy(open_conflicts[:10]),
            "entity_summary": self._entity_summary(),
            "total_entities": len(self.unified_entities),
            "integrity_checks": (await self.get_integrity_checks())["checks"],
            "data_quality": (await self.check_data_quality()).get("average_quality", 0.0),
            "info_requests": len(self.info_requests),
            "recent_audit_activity": copy.deepcopy(self.audit_logs[:8]),
        }

    async def get_data_sources(self) -> dict:
        """Return active source registry."""
        sorted_sources = sorted(
            self.data_sources,
            key=lambda item: (item["priority"], -float(item["reliability_score"])),
        )
        return {"ok": True, "sources": copy.deepcopy(sorted_sources)}

    async def receive_data(self, source: str, data: Dict[str, Any]) -> dict:
        """Receive source data, validate it, update entities, and log the receipt."""
        schema = self._get_schema_for_source(source)
        validation_result = await self.validate_data(data, schema)
        if not validation_result["valid"]:
            return {
                "ok": False,
                "received": False,
                "source": source,
                "errors": validation_result["errors"],
            }

        entity_result = await self._update_unified_entities(source, validation_result["validated_data"] or data)
        self._audit_data_receipt(source, data, entity_result)

        source_record = next((item for item in self.data_sources if item["source_code"] == source), None)
        if source_record:
            source_record["last_sync"] = datetime.now(timezone.utc).isoformat()

        return {
            "ok": True,
            "received": True,
            "source": source,
            "entities_updated": entity_result["updated"],
            "conflicts_detected": entity_result["conflicts"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def request_data(self, entity_type: str, entity_id: str, fields: Optional[List[str]] = None) -> dict:
        """Request a filtered unified entity payload."""
        entity = self._get_unified_entity(entity_type, entity_id)
        if not entity:
            return {"ok": False, "found": False, "message": "Entity not found"}

        filtered_data = entity["data"]
        if fields:
            filtered_data = {key: value for key, value in entity["data"].items() if key in fields}

        request_record = {
            "request_id": f"REQ-{len(self.info_requests) + 101}",
            "requested_by": "shared_runtime",
            "request_type": "entity_lookup",
            "parameters": {"entity_type": entity_type, "entity_id": entity_id, "fields": fields or []},
            "status": "completed",
            "response_data": {"entity_type": entity_type, "entity_id": entity_id},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.info_requests.insert(0, request_record)

        return {
            "ok": True,
            "found": True,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": filtered_data,
            "confidence": entity.get("confidence"),
            "sources": entity.get("sources_used"),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    async def validate_data(self, data: Dict[str, Any], schema: Dict[str, Any]) -> dict:
        """Validate a payload using a lightweight schema."""
        errors: List[str] = []
        validated_data: Dict[str, Any] = {}

        for field, rules in schema.items():
            value = data.get(field)
            if rules.get("required") and value in (None, ""):
                errors.append(f"{field} is required")
                continue
            if value in (None, ""):
                continue

            field_errors = self._validate_field(field, value, rules)
            if field_errors:
                errors.extend(field_errors)
                continue
            validated_data[field] = value

        confidence = max(0, 100 - len(errors) * 10)
        return {
            "ok": True,
            "valid": not errors,
            "validated_data": validated_data,
            "errors": errors,
            "warnings": [],
            "confidence": confidence,
        }

    async def get_conflicts(self, status: str = "open") -> dict:
        """Return conflicts filtered by status."""
        normalized = status.lower().replace(" ", "_")
        if normalized == "all":
            items = self.conflicts
        else:
            items = [item for item in self.conflicts if item["status"] == normalized]
        return {
            "ok": True,
            "status": normalized,
            "conflicts": copy.deepcopy(items),
            "count": len(items),
        }

    async def detect_conflicts(self, records: List[Dict[str, Any]]) -> dict:
        """Detect conflicts in supplied records or return tracked conflicts."""
        if not records:
            return {
                "ok": True,
                "conflicts": copy.deepcopy(self.conflicts),
                "open_conflicts": len([item for item in self.conflicts if item["status"] == "open"]),
            }

        grouped: Dict[str, Dict[str, Any]] = {}
        for record in records:
            source = record.get("source") or "unknown"
            entity_type = record.get("entity_type") or "entity"
            entity_id = record.get("entity_id") or record.get("id") or "unknown"
            data = record.get("data", {})
            group_key = f"{entity_type}:{entity_id}"
            if group_key not in grouped:
                grouped[group_key] = {"entity_type": entity_type, "entity_id": entity_id, "values": {}}
            for field, value in data.items():
                grouped[group_key]["values"].setdefault(field, {})
                grouped[group_key]["values"][field][source] = value

        detected: List[Dict[str, Any]] = []
        for grouped_item in grouped.values():
            for field, values in grouped_item["values"].items():
                unique_values = {json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value) for value in values.values()}
                if len(unique_values) > 1:
                    detected.append(
                        {
                            "conflict_id": f"CONF{len(self.conflicts) + len(detected) + 1:03d}",
                            "entity_type": grouped_item["entity_type"],
                            "entity_identifier": grouped_item["entity_id"],
                            "field_name": field,
                            "values_from_sources": values,
                            "detected_at": datetime.now(timezone.utc).isoformat(),
                            "severity": self._determine_conflict_severity(field, values),
                            "status": "open",
                            "resolution_method": None,
                            "resolved_value": None,
                            "resolved_by": None,
                            "resolved_at": None,
                        }
                    )

        self.conflicts = detected + self.conflicts
        return {"ok": True, "conflicts": detected, "detected_count": len(detected)}

    async def resolve_conflict(self, conflict_id: str, strategy: str = "") -> dict:
        """Resolve a tracked conflict."""
        conflict = next((item for item in self.conflicts if item["conflict_id"] == conflict_id), None)
        if not conflict:
            return {"ok": False, "error": f"Conflict '{conflict_id}' not found"}

        chosen_strategy = strategy or self._default_strategy_for_conflict(conflict)
        resolved_value, selected_source = self._resolve_values(conflict["values_from_sources"], chosen_strategy)

        conflict["status"] = "resolved"
        conflict["resolution_method"] = chosen_strategy
        conflict["resolved_value"] = resolved_value
        conflict["resolved_by"] = "information_coordinator"
        conflict["resolved_at"] = datetime.now(timezone.utc).isoformat()

        return {
            "ok": True,
            "conflict_id": conflict_id,
            "strategy_used": chosen_strategy,
            "resolved_value": resolved_value,
            "selected_source": selected_source,
            "conflict": copy.deepcopy(conflict),
        }

    async def get_resolution_suggestions(self, conflict_id: str) -> dict:
        """Return suggested resolution strategies for a conflict."""
        conflict = next((item for item in self.conflicts if item["conflict_id"] == conflict_id), None)
        if not conflict:
            return {"ok": False, "error": f"Conflict '{conflict_id}' not found"}

        values = conflict["values_from_sources"]
        suggestions: List[Dict[str, Any]] = []
        counter: Dict[str, int] = {}
        reverse_lookup: Dict[str, Any] = {}

        for value in values.values():
            serialized = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
            counter[serialized] = counter.get(serialized, 0) + 1
            reverse_lookup[serialized] = value

        if counter:
            winner = max(counter.items(), key=lambda item: item[1])
            suggestions.append(
                {
                    "method": "majority",
                    "value": reverse_lookup[winner[0]],
                    "confidence": round((winner[1] / len(values)) * 100, 2),
                }
            )

        best_source = self._best_source(list(values.keys()))
        suggestions.append(
            {
                "method": "source_reliability",
                "value": values.get(best_source),
                "selected_source": best_source,
                "confidence": 85.0,
            }
        )
        suggestions.append(
            {
                "method": "timestamp",
                "value": values[list(values.keys())[-1]],
                "confidence": 72.0,
            }
        )
        return {"ok": True, "conflict_id": conflict_id, "suggestions": suggestions}

    async def create_unified_entity(
        self,
        entity_type: str,
        entity_id: str,
        records: List[Dict[str, Any]],
    ) -> dict:
        """Create or refresh a unified entity model from multiple records."""
        if not entity_id:
            return {"ok": False, "error": "entity_id is required"}
        if not records:
            existing = next(
                (item for item in self.unified_entities if item["entity_type"] == entity_type and item["entity_id"] == entity_id),
                None,
            )
            if existing:
                return {"ok": True, "entity": copy.deepcopy(existing)}
            return {"ok": False, "error": "No records supplied for entity creation"}

        merged_values: Dict[str, List[Dict[str, Any]]] = {}
        source_order: List[str] = []
        for record in records:
            source = record.get("source") or "unknown"
            source_order.append(source)
            for field, value in (record.get("data") or {}).items():
                merged_values.setdefault(field, []).append({"source": source, "value": value})

        entity_data: Dict[str, Any] = {}
        confidence_by_field: Dict[str, float] = {}
        for field, values in merged_values.items():
            best_value, confidence = self._select_best_value(values)
            entity_data[field] = best_value
            confidence_by_field[field] = confidence

        entity = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": entity_data,
            "sources_used": sorted(set(source_order)),
            "confidence": {
                "overall": round(sum(confidence_by_field.values()) / max(1, len(confidence_by_field)), 2),
                "by_field": confidence_by_field,
            },
            "source_of_truth": self._best_source(sorted(set(source_order))),
            "last_verified": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.unified_entities = [
            item
            for item in self.unified_entities
            if not (item["entity_type"] == entity_type and item["entity_id"] == entity_id)
        ]
        self.unified_entities.insert(0, entity)
        return {"ok": True, "entity": copy.deepcopy(entity)}

    async def get_entity_history(self, entity_type: str, entity_id: str) -> dict:
        """Return audit history for an entity."""
        history = [
            item
            for item in self.audit_logs
            if item["entity_type"] == entity_type and item["entity_id"] == entity_id
        ]
        history.sort(key=lambda item: item["timestamp"])
        return {
            "ok": True,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "history": history,
            "total_changes": len(history),
        }

    async def generate_audit_report(self, days: int) -> dict:
        """Return a compact audit report."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        relevant_logs = [
            item
            for item in self.audit_logs
            if datetime.fromisoformat(item["timestamp"]) >= cutoff
        ]
        changes_by_source: Dict[str, int] = {}
        changes_by_entity: Dict[str, int] = {}
        for item in relevant_logs:
            source = item.get("source_bot") or "unknown"
            changes_by_source[source] = changes_by_source.get(source, 0) + 1
            entity_key = f'{item["entity_type"]}:{item["entity_id"]}'
            changes_by_entity[entity_key] = changes_by_entity.get(entity_key, 0) + 1

        return {
            "ok": True,
            "period_days": days,
            "total_changes": len(relevant_logs),
            "changes_by_source": changes_by_source,
            "changes_by_entity": changes_by_entity,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_audit_log(self, days: int = 7) -> dict:
        """Return recent audit events."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        logs = [
            copy.deepcopy(item)
            for item in self.audit_logs
            if datetime.fromisoformat(item["timestamp"]) >= cutoff
        ]
        return {"ok": True, "days": days, "logs": logs, "count": len(logs)}

    async def assess_data_quality(self, data: Dict[str, Any]) -> dict:
        """Score completeness and freshness of a record."""
        fields = list(data.keys())
        complete_fields = len([field for field in fields if data.get(field) not in (None, "")])
        completeness = round((complete_fields / max(1, len(fields))) * 100, 2) if fields else 0.0
        accuracy = 95.0 if data else 0.0

        timeliness = 75.0
        if data.get("last_updated"):
            last_updated = datetime.fromisoformat(str(data["last_updated"]))
            age_hours = max(0.0, (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600)
            timeliness = max(0.0, round(100 - age_hours * 2.5, 2))

        overall = round((completeness * 0.4) + (accuracy * 0.4) + (timeliness * 0.2), 2)
        return {
            "ok": True,
            "completeness": completeness,
            "accuracy": accuracy,
            "timeliness": timeliness,
            "overall_score": overall,
            "grade": self._grade(overall),
        }

    async def check_data_quality(self, entity_type: Optional[str] = None) -> dict:
        """Score all entities or a filtered entity type."""
        entities = self.unified_entities
        if entity_type:
            entities = [item for item in entities if item["entity_type"] == entity_type]
        if not entities:
            return {"ok": True, "message": "No data available", "entity_count": 0}

        scores: List[float] = []
        for entity in entities:
            quality = await self.assess_data_quality(entity["data"])
            scores.append(float(quality["overall_score"]))

        return {
            "ok": True,
            "entity_count": len(entities),
            "average_quality": round(sum(scores) / len(scores), 2),
            "quality_distribution": {
                "excellent": len([score for score in scores if score >= 90]),
                "good": len([score for score in scores if 75 <= score < 90]),
                "fair": len([score for score in scores if 60 <= score < 75]),
                "poor": len([score for score in scores if score < 60]),
            },
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_integrity_checks(self) -> dict:
        """Return integrity and consistency checks."""
        open_conflicts = len([item for item in self.conflicts if item["status"] == "open"])
        checks = [
            {
                "check_id": "CHK001",
                "check_type": "consistency",
                "status": "warning" if open_conflicts else "passed",
                "score": 88.0,
                "issues_found": [f"{open_conflicts} open conflicts"] if open_conflicts else [],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "check_id": "CHK002",
                "check_type": "completeness",
                "status": "passed",
                "score": 94.0,
                "issues_found": [],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "check_id": "CHK003",
                "check_type": "timeliness",
                "status": "passed",
                "score": 91.0,
                "issues_found": [],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        return {"ok": True, "checks": checks}

    async def search_entities(self, criteria: Dict[str, Any]) -> dict:
        """Search unified entities using simple equality or contains matching."""
        results: List[Dict[str, Any]] = []
        for entity in self.unified_entities:
            matched = True
            for key, value in criteria.items():
                candidate = entity["data"].get(key)
                if isinstance(value, str):
                    if value.lower() not in str(candidate).lower():
                        matched = False
                        break
                elif candidate != value:
                    matched = False
                    break
            if matched:
                results.append(copy.deepcopy(entity))
        return {"ok": True, "results": results, "count": len(results)}

    async def search(self, query: str, entity_type: Optional[str] = None) -> dict:
        """Run a text search across unified entities."""
        results: List[Dict[str, Any]] = []
        query_lower = query.lower()
        for entity in self.unified_entities:
            if entity_type and entity["entity_type"] != entity_type:
                continue
            data_str = json.dumps(entity["data"]).lower()
            if query_lower in data_str or query_lower in entity["entity_id"].lower():
                results.append(
                    {
                        "entity_type": entity["entity_type"],
                        "entity_id": entity["entity_id"],
                        "data": copy.deepcopy(entity["data"]),
                        "relevance": 90,
                    }
                )
        return {"ok": True, "query": query, "results": results[:20], "count": len(results[:20])}

    async def generate_report(self, report_type: str) -> dict:
        """Generate a unified information report."""
        report = {
            "report_id": f"INFO-{len(self.unified_reports) + 101}",
            "report_type": report_type,
            "report_date": datetime.now(timezone.utc).date().isoformat(),
            "summary": {
                "active_sources": len([source for source in self.data_sources if source["is_active"]]),
                "unified_entities": len(self.unified_entities),
                "open_conflicts": len([item for item in self.conflicts if item["status"] == "open"]),
                "audit_events": len(self.audit_logs),
            },
            "sources_used": [source["source_code"] for source in self.data_sources if source["is_active"]],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.unified_reports.insert(0, report)
        return {"ok": True, "report": report}

    def _entity_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for entity in self.unified_entities:
            summary[entity["entity_type"]] = summary.get(entity["entity_type"], 0) + 1
        return summary

    def _audit_data_receipt(self, source: str, data: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Record incoming data activity in the audit log."""
        log_entry = {
            "log_id": f"LOG{len(self.audit_logs) + 100:03d}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity_type": "system",
            "entity_id": "data_receipt",
            "field": "received_data",
            "old_value": None,
            "new_value": json.dumps({"source": source, "data": data}, sort_keys=True)[:240],
            "changed_by": "system",
            "source_bot": source,
            "reason": f"Data received from {source}",
            "result": result,
        }
        self.audit_logs.insert(0, log_entry)

    async def _update_unified_entities(self, source: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update canonical entities from incoming source data."""
        updated: List[str] = []
        conflicts_detected: List[Dict[str, Any]] = []
        entities = self._extract_entities(data)

        for entity in entities:
            entity_type = entity["type"]
            entity_id = entity["id"]
            entity_data = entity["data"]
            existing = self._get_unified_entity(entity_type, entity_id)

            if existing:
                merged, conflicts = self._merge_entity_data(existing, source, entity_data)
                self.unified_entities = [
                    item
                    for item in self.unified_entities
                    if not (item["entity_type"] == entity_type and item["entity_id"] == entity_id)
                ]
                self.unified_entities.insert(0, merged)
                updated.append(f"{entity_type}:{entity_id}")
                conflicts_detected.extend(conflicts)
                self.conflicts = conflicts + self.conflicts
            else:
                created = {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "data": entity_data,
                    "sources_used": [source],
                    "confidence": {"overall": 90.0, "by_field": {key: 90.0 for key in entity_data.keys()}},
                    "source_of_truth": source,
                    "last_verified": datetime.now(timezone.utc).isoformat(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                self.unified_entities.insert(0, created)
                updated.append(f"{entity_type}:{entity_id} (new)")

        return {"updated": updated, "conflicts": conflicts_detected}

    def _get_unified_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        return next(
            (
                copy.deepcopy(item)
                for item in self.unified_entities
                if item["entity_type"] == entity_type and item["entity_id"] == entity_id
            ),
            None,
        )

    def _merge_entity_data(self, existing: Dict[str, Any], source: str, new_data: Dict[str, Any]) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Merge incoming fields into an existing unified entity."""
        merged = copy.deepcopy(existing)
        conflicts: List[Dict[str, Any]] = []

        for field, new_value in new_data.items():
            old_value = merged["data"].get(field)
            if old_value is not None and old_value != new_value:
                conflict = {
                    "conflict_id": f"CONF{len(self.conflicts) + len(conflicts) + 1:03d}",
                    "entity_type": existing["entity_type"],
                    "entity_identifier": existing["entity_id"],
                    "field_name": field,
                    "values_from_sources": {
                        existing["source_of_truth"]: old_value,
                        source: new_value,
                    },
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "severity": self._determine_conflict_level(field, old_value, new_value),
                    "status": "open",
                    "resolution_method": None,
                    "resolved_value": None,
                    "resolved_by": None,
                    "resolved_at": None,
                }
                conflicts.append(conflict)
            else:
                merged["data"][field] = new_value
                merged["confidence"]["by_field"][field] = 92.0

        if source not in merged["sources_used"]:
            merged["sources_used"].append(source)
        merged["confidence"]["overall"] = self._calculate_confidence(existing, source, len(new_data), len(conflicts))
        merged["last_verified"] = datetime.now(timezone.utc).isoformat()
        return merged, conflicts

    def _extract_entities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract canonical entities from raw source payloads."""
        entities: List[Dict[str, Any]] = []
        entity_map = {
            "customer": ("customer", "id"),
            "shipment": ("shipment", "shipment_number"),
            "driver": ("driver", "id"),
            "partner": ("partner", "partner_id"),
            "carrier": ("carrier", "carrier_id"),
        }
        for key, (entity_type, preferred_id) in entity_map.items():
            entity_payload = data.get(key)
            if not isinstance(entity_payload, dict):
                continue
            entity_id = entity_payload.get(preferred_id) or entity_payload.get("id") or entity_payload.get("code")
            if entity_id:
                entities.append({"type": entity_type, "id": str(entity_id), "data": entity_payload})
        return entities

    def _determine_conflict_level(self, field: str, old_value: Any, new_value: Any) -> str:
        """Determine severity from two conflicting values."""
        if field in {"customer_id", "amount", "date", "phone", "email"}:
            return "critical"
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)) and old_value:
            diff_percent = abs(new_value - old_value) / old_value * 100
            if diff_percent > 20:
                return "high"
            if diff_percent > 10:
                return "medium"
        return "low"

    def _calculate_confidence(self, existing: Dict[str, Any], new_source: str, new_fields_count: int, conflict_count: int = 0) -> float:
        """Recalculate confidence after a merge."""
        current = float(existing.get("confidence", {}).get("overall", 90.0))
        source_bonus = 2.0 if new_source not in existing.get("sources_used", []) else 0.5
        conflict_penalty = float(conflict_count * 6)
        field_bonus = min(4.0, float(new_fields_count) * 0.5)
        return round(max(0.0, min(100.0, current + source_bonus + field_bonus - conflict_penalty)), 2)

    def _get_schema_for_source(self, source: str) -> Dict[str, Any]:
        """Return source-specific validation schema."""
        schemas = {
            "SALES": {
                "customer": {"required": True},
                "amount": {"type": "float", "min": 0},
            },
            "CUSTOMER_SERVICE": {
                "customer": {"required": True},
                "ticket": {"required": False},
            },
            "DISPATCHER": {
                "shipment": {"required": True},
                "driver": {"required": False},
            },
        }
        return schemas.get(source, {})

    def _validate_field(self, field: str, value: Any, rules: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        expected_type = rules.get("type")
        type_map = {"str": str, "int": int, "float": float, "bool": bool}
        if expected_type in type_map and not isinstance(value, type_map[expected_type]):
            errors.append(f"{field} must be of type {expected_type}")

        pattern = rules.get("pattern")
        if pattern and isinstance(value, str) and re.match(pattern, value) is None:
            errors.append(f"{field} does not match the required pattern")

        if isinstance(value, (int, float)):
            if "min" in rules and value < rules["min"]:
                errors.append(f"{field} is below the minimum value {rules['min']}")
            if "max" in rules and value > rules["max"]:
                errors.append(f"{field} is above the maximum value {rules['max']}")

        date_format = rules.get("date_format")
        if date_format and isinstance(value, str):
            try:
                datetime.strptime(value, date_format)
            except ValueError:
                errors.append(f"{field} must match date format {date_format}")

        return errors

    def _determine_conflict_severity(self, field: str, values: Dict[str, Any]) -> str:
        if field in {"customer_id", "shipment_id", "amount", "status"}:
            return "high"

        numeric_values = [value for value in values.values() if isinstance(value, (int, float))]
        if len(numeric_values) > 1:
            highest = max(numeric_values)
            lowest = min(numeric_values)
            if highest > 0 and (highest - lowest) / highest > 0.2:
                return "high"
        return "medium"

    def _default_strategy_for_conflict(self, conflict: Dict[str, Any]) -> str:
        if conflict.get("severity") == "critical":
            return "manual"
        if conflict.get("severity") == "high":
            return "source_reliability"
        return "majority"

    def _resolve_values(self, values_from_sources: Dict[str, Any], strategy: str) -> tuple[Any, Optional[str]]:
        if not values_from_sources:
            return None, None
        if strategy == "majority":
            counter: Dict[str, int] = {}
            reverse_lookup: Dict[str, Any] = {}
            for source, value in values_from_sources.items():
                serialized = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
                counter[serialized] = counter.get(serialized, 0) + 1
                reverse_lookup[serialized] = value
            winner = max(counter.items(), key=lambda item: item[1])[0]
            selected_value = reverse_lookup[winner]
            selected_source = next((source for source, value in values_from_sources.items() if value == selected_value), None)
            return selected_value, selected_source

        if strategy == "timestamp":
            selected_source = list(values_from_sources.keys())[-1]
            return values_from_sources[selected_source], selected_source

        if strategy in {"source_reliability", "priority"}:
            best_source = self._best_source(list(values_from_sources.keys()))
            return values_from_sources.get(best_source), best_source

        first_source = next(iter(values_from_sources.keys()))
        return values_from_sources[first_source], first_source

    def _best_source(self, sources: List[str]) -> Optional[str]:
        source_map = {item["source_code"]: item for item in self.data_sources}
        ranked = sorted(
            sources,
            key=lambda source: (
                source_map.get(source, {}).get("priority", 99),
                -float(source_map.get(source, {}).get("reliability_score", 0.0)),
            ),
        )
        return ranked[0] if ranked else None

    def _select_best_value(self, values: List[Dict[str, Any]]) -> tuple[Any, float]:
        if not values:
            return None, 0.0
        if len(values) == 1:
            return values[0]["value"], 100.0

        counts: Dict[str, int] = {}
        value_lookup: Dict[str, Any] = {}
        for value_info in values:
            serialized = json.dumps(value_info["value"], sort_keys=True) if isinstance(value_info["value"], (dict, list)) else str(value_info["value"])
            counts[serialized] = counts.get(serialized, 0) + 1
            value_lookup[serialized] = value_info["value"]

        winner = max(counts.items(), key=lambda item: item[1])
        confidence = round((winner[1] / len(values)) * 100, 2)
        return value_lookup[winner[0]], confidence

    def _grade(self, score: float) -> str:
        if score >= 95:
            return "A"
        if score >= 85:
            return "B"
        if score >= 70:
            return "C"
        if score >= 50:
            return "D"
        return "F"

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
