"""
Integrations Management Service
Handles storing and retrieving integration credentials and status
"""

import json
import secrets
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Integration types
INTEGRATION_TYPES = {
    "salesforce": {"name": "Salesforce CRM", "requires": ["api_key", "api_secret"]},
    "quickbooks": {"name": "QuickBooks", "requires": ["realm_id", "access_token"]},
    "google_sheets": {"name": "Google Sheets", "requires": ["sheet_id", "api_key"]},
    "slack": {"name": "Slack", "requires": ["webhook_url"]},
}

DEFAULT_INTEGRATIONS = {
    "salesforce": {"status": "disconnected", "error": None},
    "quickbooks": {"status": "disconnected", "error": None},
    "google_sheets": {"status": "disconnected", "error": None},
    "slack": {"status": "disconnected", "error": None},
}


async def _ensure_schema(session: AsyncSession) -> None:
    """Create integrations table if not exists"""
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS integrations (
            id SERIAL PRIMARY KEY,
            integration_type VARCHAR(50) NOT NULL UNIQUE,
            status VARCHAR(20) DEFAULT 'disconnected',
            credentials JSONB NOT NULL DEFAULT '{}',
            last_sync TIMESTAMP,
            last_error VARCHAR(500),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            updated_by VARCHAR(100)
        )
    """))
    await session.commit()


async def _get_integrations_raw(session: AsyncSession) -> Dict[str, Any]:
    """Get raw integrations data from database"""
    await _ensure_schema(session)
    
    result = await session.execute(text("SELECT integration_type, status, last_sync, last_error FROM integrations"))
    rows = result.fetchall()
    
    integrations = DEFAULT_INTEGRATIONS.copy()
    for row in rows:
        integration_type = row[0]
        integrations[integration_type] = {
            "status": row[1],
            "last_sync": row[2].isoformat() if row[2] else None,
            "error": row[3]
        }
    
    return integrations


async def get_integrations(session: AsyncSession) -> Dict[str, Any]:
    """
    Get all integrations status
    
    Returns:
        Dict with integration statuses
    """
    integrations = await _get_integrations_raw(session)
    
    # Format response
    connected_systems = []
    for type_key, data in integrations.items():
        if type_key in INTEGRATION_TYPES:
            system_info = INTEGRATION_TYPES[type_key].copy()
            system_info["status"] = data.get("status", "disconnected")
            system_info["last_sync"] = data.get("last_sync", "Never")
            system_info["error"] = data.get("error")
            connected_systems.append(system_info)
    
    return {
        "connected_systems": connected_systems,
        "total_connected": sum(1 for s in connected_systems if s["status"] == "connected"),
        "total_integrations": len(connected_systems),
        "timestamp": datetime.utcnow().isoformat()
    }


async def connect_integration(
    session: AsyncSession,
    integration_type: str,
    credentials: Dict[str, Any],
    updated_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Connect an integration with credentials
    
    Args:
        session: Database session
        integration_type: Type of integration (salesforce, quickbooks, etc)
        credentials: Integration credentials
        updated_by: User who made the change
        
    Returns:
        Result with status
    """
    await _ensure_schema(session)
    
    if integration_type not in INTEGRATION_TYPES:
        raise ValueError(f"Unknown integration type: {integration_type}")
    
    # Validate required fields
    required_fields = INTEGRATION_TYPES[integration_type]["requires"]
    missing_fields = [f for f in required_fields if f not in credentials]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    # Test connection (simulate)
    connection_test = await _test_integration_connection(integration_type, credentials)
    
    if not connection_test.get("success"):
        await session.execute(text("""
            INSERT INTO integrations (integration_type, status, last_error, updated_by)
            VALUES (:type, 'error', :error, :updated_by)
            ON CONFLICT (integration_type)
            DO UPDATE SET status = 'error', last_error = :error, updated_by = :updated_by, updated_at = NOW()
        """), {
            "type": integration_type,
            "error": connection_test.get("error", "Connection failed"),
            "updated_by": updated_by
        })
        await session.commit()
        return {"success": False, "error": connection_test.get("error")}
    
    # Store credentials securely (in production, use encryption)
    credentials_json = json.dumps(credentials)
    
    await session.execute(text("""
        INSERT INTO integrations (integration_type, status, credentials, last_sync, updated_by)
        VALUES (:type, 'connected', :credentials, NOW(), :updated_by)
        ON CONFLICT (integration_type)
        DO UPDATE SET status = 'connected', credentials = :credentials, last_sync = NOW(), updated_by = :updated_by, updated_at = NOW()
    """), {
        "type": integration_type,
        "credentials": credentials_json,
        "updated_by": updated_by
    })
    await session.commit()
    
    return {
        "success": True,
        "message": f"{INTEGRATION_TYPES[integration_type]['name']} connected successfully",
        "status": "connected"
    }


async def disconnect_integration(
    session: AsyncSession,
    integration_type: str,
    updated_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Disconnect an integration
    
    Args:
        session: Database session
        integration_type: Type of integration
        updated_by: User who made the change
        
    Returns:
        Result with status
    """
    await _ensure_schema(session)
    
    if integration_type not in INTEGRATION_TYPES:
        raise ValueError(f"Unknown integration type: {integration_type}")
    
    await session.execute(text("""
        UPDATE integrations
        SET status = 'disconnected', credentials = '{}', updated_by = :updated_by, updated_at = NOW()
        WHERE integration_type = :type
    """), {
        "type": integration_type,
        "updated_by": updated_by
    })
    await session.commit()
    
    return {
        "success": True,
        "message": f"{INTEGRATION_TYPES[integration_type]['name']} disconnected",
        "status": "disconnected"
    }


async def _test_integration_connection(
    integration_type: str,
    credentials: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Test if integration can connect with given credentials
    
    Args:
        integration_type: Type of integration
        credentials: Integration credentials
        
    Returns:
        Dict with success status and error message if any
    """
    # Simulate connection test
    if integration_type == "slack":
        # For Slack, just check if webhook_url is valid format
        webhook_url = credentials.get("webhook_url", "")
        if webhook_url.startswith("https://hooks.slack.com/"):
            return {"success": True}
        return {"success": False, "error": "Invalid Slack webhook URL"}
    
    elif integration_type == "salesforce":
        # For Salesforce, check if API credentials are provided
        if credentials.get("api_key") and credentials.get("api_secret"):
            return {"success": True}
        return {"success": False, "error": "Missing Salesforce API credentials"}
    
    elif integration_type == "quickbooks":
        # For QuickBooks, check if realm_id and access_token are provided
        if credentials.get("realm_id") and credentials.get("access_token"):
            return {"success": True}
        return {"success": False, "error": "Missing QuickBooks credentials"}
    
    elif integration_type == "google_sheets":
        # For Google Sheets, check if sheet_id and api_key are provided
        if credentials.get("sheet_id") and credentials.get("api_key"):
            return {"success": True}
        return {"success": False, "error": "Missing Google Sheets credentials"}
    
    return {"success": False, "error": "Unknown integration type"}
