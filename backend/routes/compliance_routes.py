from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException

from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])

COUNTRY_ALIASES = {
    "us": "us",
    "usa": "us",
    "united_states": "us",
    "united states": "us",
    "ca": "ca",
    "canada": "ca",
    "mx": "mx",
    "mexico": "mx",
    "uae": "uae",
    "united arab emirates": "uae",
    "ae": "uae",
    "sa": "sa",
    "saudi": "sa",
    "saudi arabia": "sa",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


OFFICIAL_SOURCES: Dict[str, Dict[str, Any]] = {
    "us": {
        "country": "United States",
        "sources": [
            {
                "name": "FMCSA QCMobile API",
                "url": "https://mobile.fmcsa.dot.gov/QCDevsite/docs/qcApi",
                "notes": "Real-time carrier and safety data. Requires FMCSA webKey.",
            },
            {
                "name": "FMCSA API Access",
                "url": "https://mobile.fmcsa.dot.gov/QCDevsite/docs/apiAccess",
                "notes": "Developer access instructions for obtaining a webKey.",
            },
            {
                "name": "U.S. DOT Open Data",
                "url": "https://data.transportation.gov/",
                "notes": "Transportation datasets and dataset descriptions.",
            },
        ],
    },
    "ca": {
        "country": "Canada",
        "sources": [
            {
                "name": "CBSA CARM",
                "url": "https://www.cbsa-asfc.gc.ca/services/carm-gcra/menu-eng.html",
                "notes": "Commercial accounting and revenue management program.",
            },
            {
                "name": "CBSA Memorandum D-2-7-1",
                "url": "https://www.cbsa-asfc.gc.ca/publications/dm-md/d2/d2-7-1-eng.html",
                "notes": "Advance Passenger Information guidance.",
            },
            {
                "name": "CBSA Memorandum D-2-7-2",
                "url": "https://www.cbsa-asfc.gc.ca/publications/dm-md/d2/d2-7-2-eng.html",
                "notes": "Passenger Name Record guidance.",
            },
            {
                "name": "Transport Canada TDG",
                "url": "https://www.tc.canada.ca/en/dangerous-goods/transportation-dangerous-goods-canada",
                "notes": "Dangerous goods regulations and program information.",
            },
            {
                "name": "DriveBC Open511",
                "url": "https://api.open511.gov.bc.ca/events",
                "notes": "Public real-time British Columbia road events feed.",
            },
        ],
    },
    "mx": {
        "country": "Mexico",
        "sources": [
            {
                "name": "DOF PROY-NOM-011-SICT2/2025",
                "url": "https://www.dof.gob.mx/2026/SICT/PROY-NOM-011-SICT2.pdf",
                "notes": "Draft standard for limited-quantity dangerous goods transport.",
            },
            {
                "name": "DOF public consultation notice",
                "url": "https://www.dof.gob.mx/normasOficiales/9538/sict/sict.html",
                "notes": "Public consultation notice stating a 60-day comment period.",
            },
            {
                "name": "PLATIICA consultation portal",
                "url": "https://platiica.economia.gob.mx/proyectos-de-nom/",
                "notes": "Consultation platform referenced by the notice.",
            },
        ],
    },
    "uae": {
        "country": "United Arab Emirates",
        "sources": [
            {
                "name": "UAE roadways portal",
                "url": "https://u.ae/information-and-services/transportation/roadways",
                "notes": "Federal law and UAE toll-system overview.",
            },
            {
                "name": "Federal Law No. 9 of 2011 on Land Transport",
                "url": "https://u.ae/-/media/Documents-2022/transportation-Law-English.pdf",
                "notes": "Legal framework for paid land transport services.",
            },
            {
                "name": "MOI heavy vehicle permit guide",
                "url": "https://moi.gov.ae/DataFolder/portal-Service-Card/user_manual/2024/IssuanceofPermitForHeavyVehicleToPass_Portal_EN.pdf",
                "notes": "Service manual for heavy vehicle pass permits.",
            },
            {
                "name": "Salik official portal",
                "url": "https://www.salik.ae/en/about",
                "notes": "Dubai toll system overview.",
            },
            {
                "name": "Salik variable toll rates",
                "url": "https://www.salik.ae/en/news/salik-announces-implementation-of-variable-toll-pricing-effective-january-31-2025",
                "notes": "Official Salik announcement on variable pricing.",
            },
        ],
    },
    "sa": {
        "country": "Saudi Arabia",
        "sources": [
            {
                "name": "Transport General Authority",
                "url": "https://www.tga.gov.sa/",
                "notes": "Primary official transport regulator portal.",
            },
            {
                "name": "TGA regulations",
                "url": "https://www.tga.gov.sa/Regulations?lang=en",
                "notes": "Official regulations and legislative materials page.",
            },
            {
                "name": "Logisti platform",
                "url": "https://iam.logisti.sa/",
                "notes": "Official Logisti access portal.",
            },
            {
                "name": "TGA national address enforcement notice",
                "url": "https://www.tga.gov.sa/en/MediaCenter/TGANewsDetails/194",
                "notes": "Official TGA notice about national address enforcement for shipments.",
            },
            {
                "name": "TGA open data",
                "url": "https://www.tga.gov.sa/en/KnowledgeCenter/OpenData",
                "notes": "Open-data entry point for regulator datasets.",
            },
        ],
    },
}


async def _fetch_open511(limit: int = 10) -> List[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get("https://api.open511.gov.bc.ca/events")
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return []

    events = payload.get("events") if isinstance(payload, dict) else []
    normalized: List[Dict[str, Any]] = []
    for event in events[:limit]:
        road = (event.get("roads") or [{}])[0]
        normalized.append(
            {
                "id": event.get("id"),
                "headline": event.get("headline") or event.get("event_type"),
                "status": event.get("status"),
                "severity": event.get("severity"),
                "description": event.get("description"),
                "updated": event.get("updated") or event.get("created"),
                "road": road.get("name"),
                "url": event.get("url"),
            }
        )
    return normalized


async def _fetch_fmcsa(path: str) -> Dict[str, Any]:
    web_key = os.getenv("FMCSA_WEBKEY", "").strip()
    if not web_key:
        return {
            "live_enabled": False,
            "requires_api_key": True,
            "message": "Set FMCSA_WEBKEY to enable live FMCSA carrier queries.",
            "docs": OFFICIAL_SOURCES["us"]["sources"][:2],
        }

    url = f"https://mobile.fmcsa.dot.gov/qc/services/{path}"
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, params={"webKey": web_key})
            response.raise_for_status()
            return {
                "live_enabled": True,
                "source": "FMCSA QCMobile API",
                "queried_at": _utcnow(),
                "data": response.json(),
            }
    except Exception as exc:
        return {
            "live_enabled": False,
            "requires_api_key": True,
            "message": f"FMCSA query failed: {exc}",
            "docs": OFFICIAL_SOURCES["us"]["sources"][:2],
        }


def _normalize_country_code(country: str) -> str:
    normalized = str(country or "").strip().lower().replace("-", " ").replace("_", " ")
    code = COUNTRY_ALIASES.get(normalized)
    if not code:
        raise HTTPException(status_code=404, detail=f"Unsupported country '{country}'")
    return code


async def _build_country_overview(country_code: str) -> Dict[str, Any]:
    if country_code == "us":
        return {
            "country_code": "us",
            "country": OFFICIAL_SOURCES["us"]["country"],
            "sources": OFFICIAL_SOURCES["us"]["sources"],
            "sections": [
                {
                    "id": "inspections",
                    "title": "Inspection and safety references",
                    "endpoint": "/api/v1/compliance/us/inspections",
                    "live_enabled": False,
                    "summary": "Official FMCSA and DOT references for inspections, carrier safety, and developer access.",
                },
                {
                    "id": "carrier_lookup",
                    "title": "Carrier lookup",
                    "endpoint": "/api/v1/compliance/us/carrier/{dot}",
                    "live_enabled": bool(os.getenv("FMCSA_WEBKEY", "").strip()),
                    "summary": "Live carrier data becomes available when FMCSA_WEBKEY is configured.",
                },
            ],
            "generated_at": _utcnow(),
        }

    if country_code == "ca":
        road_events = await _fetch_open511(limit=6)
        return {
            "country_code": "ca",
            "country": OFFICIAL_SOURCES["ca"]["country"],
            "sources": OFFICIAL_SOURCES["ca"]["sources"],
            "sections": [
                {
                    "id": "cbsa_api",
                    "title": "CBSA API and customs references",
                    "endpoint": "/api/v1/compliance/ca/api",
                    "summary": "Official CBSA and Transport Canada materials for customs and dangerous goods compliance.",
                },
                {
                    "id": "pnr",
                    "title": "Passenger Name Record guidance",
                    "endpoint": "/api/v1/compliance/ca/pnr",
                    "summary": "Official PNR guidance references from CBSA.",
                },
                {
                    "id": "road_events",
                    "title": "DriveBC road events",
                    "endpoint": "/api/v1/compliance/ca/road/events",
                    "summary": "Public real-time road events from the British Columbia Open511 feed.",
                    "items": road_events,
                },
            ],
            "live_feeds": {
                "open511_events": road_events,
            },
            "generated_at": _utcnow(),
        }

    if country_code == "mx":
        return {
            "country_code": "mx",
            "country": OFFICIAL_SOURCES["mx"]["country"],
            "sources": OFFICIAL_SOURCES["mx"]["sources"],
            "sections": [
                {
                    "id": "nom_011",
                    "title": "PROY-NOM-011-SICT2/2025",
                    "endpoint": "/api/v1/compliance/mx/nom/011",
                    "summary": "Official consultation notice and draft standard references for limited-quantity dangerous goods transport.",
                },
                {
                    "id": "hazmat",
                    "title": "Hazardous materials references",
                    "endpoint": "/api/v1/compliance/mx/hazmat",
                    "summary": "Official transport and hazmat-related references.",
                },
            ],
            "generated_at": _utcnow(),
        }

    if country_code == "uae":
        return {
            "country_code": "uae",
            "country": OFFICIAL_SOURCES["uae"]["country"],
            "sources": OFFICIAL_SOURCES["uae"]["sources"],
            "sections": [
                {
                    "id": "heavy_permit",
                    "title": "Heavy vehicle permit references",
                    "endpoint": "/api/v1/compliance/uae/heavy/permit",
                    "summary": "Official MOI permit guide and federal transport law references.",
                },
                {
                    "id": "darb",
                    "title": "Darb toll references",
                    "endpoint": "/api/v1/compliance/uae/toll/darb",
                    "summary": "Official UAE portal references for Abu Dhabi toll operations.",
                },
                {
                    "id": "salik",
                    "title": "Salik toll references",
                    "endpoint": "/api/v1/compliance/uae/toll/salik",
                    "summary": "Official Salik references and pricing announcement links.",
                },
            ],
            "generated_at": _utcnow(),
        }

    if country_code == "sa":
        return {
            "country_code": "sa",
            "country": OFFICIAL_SOURCES["sa"]["country"],
            "sources": OFFICIAL_SOURCES["sa"]["sources"],
            "sections": [
                {
                    "id": "tga_updates",
                    "title": "TGA official references",
                    "endpoint": "/api/v1/compliance/sa/tga/updates",
                    "summary": "Transport General Authority official references and notices.",
                },
                {
                    "id": "gcc_trucks",
                    "title": "GCC trucking references",
                    "endpoint": "/api/v1/compliance/sa/gcc/trucks",
                    "summary": "Official sources for cross-border and GCC trucking validation.",
                },
                {
                    "id": "logisti",
                    "title": "Logisti platform",
                    "endpoint": "/api/v1/compliance/sa/logisti",
                    "summary": "Official Logisti platform reference for logistics workflows.",
                },
            ],
            "generated_at": _utcnow(),
        }

    raise HTTPException(status_code=404, detail=f"Unsupported country code '{country_code}'")


@router.get("/sources")
async def get_compliance_sources(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "countries": OFFICIAL_SOURCES,
        "generated_at": _utcnow(),
    }


@router.get("/countries")
async def get_compliance_countries(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "countries": [
            {"code": code, "country": payload["country"]}
            for code, payload in OFFICIAL_SOURCES.items()
        ],
        "generated_at": _utcnow(),
    }


@router.get("/overview/{country}")
async def get_compliance_overview(
    country: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    country_code = _normalize_country_code(country)
    return await _build_country_overview(country_code)


@router.get("/us/inspections")
async def get_us_inspections(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "United States",
        "live_enabled": False,
        "update_model": "daily or on-demand depending source",
        "sources": OFFICIAL_SOURCES["us"]["sources"],
        "notes": [
            "FMCSA carrier and safety lookups are available via QCMobile with a webKey.",
            "DOT open datasets can supplement inspection analytics.",
        ],
        "generated_at": _utcnow(),
    }


@router.get("/us/carrier/{dot_number}")
async def get_us_carrier(
    dot_number: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await _fetch_fmcsa(f"carriers/{dot_number}")
    result["dot_number"] = dot_number
    return result


@router.get("/us/safety/{dot_number}")
async def get_us_safety(
    dot_number: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await _fetch_fmcsa(f"carriers/{dot_number}/basics")
    result["dot_number"] = dot_number
    return result


@router.get("/ca/api")
async def get_canada_api_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "Canada",
        "topic": "Advance Passenger Information and CBSA program references",
        "sources": [
            OFFICIAL_SOURCES["ca"]["sources"][0],
            OFFICIAL_SOURCES["ca"]["sources"][1],
            OFFICIAL_SOURCES["ca"]["sources"][3],
        ],
        "generated_at": _utcnow(),
    }


@router.get("/ca/pnr")
async def get_canada_pnr_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "Canada",
        "topic": "Passenger Name Record guidance",
        "public_feed": False,
        "sources": [OFFICIAL_SOURCES["ca"]["sources"][2]],
        "generated_at": _utcnow(),
    }


@router.get("/ca/road/events")
async def get_canada_road_events(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    events = await _fetch_open511()
    return {
        "country": "Canada",
        "source": OFFICIAL_SOURCES["ca"]["sources"][4],
        "events": events,
        "count": len(events),
        "generated_at": _utcnow(),
    }


@router.get("/mx/nom/011")
async def get_mexico_nom_011(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "Mexico",
        "title": "PROY-NOM-011-SICT2/2025",
        "status": "public consultation notice published",
        "sources": OFFICIAL_SOURCES["mx"]["sources"][:2],
        "notes": [
            "The DOF notice states a 60-day natural-day public consultation period.",
            "The proposal covers limited quantities of dangerous goods on federal roads.",
        ],
        "generated_at": _utcnow(),
    }


@router.get("/mx/hazmat")
async def get_mexico_hazmat(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "Mexico",
        "topic": "Hazardous materials transport",
        "sources": OFFICIAL_SOURCES["mx"]["sources"],
        "generated_at": _utcnow(),
    }


@router.get("/uae/heavy/permit")
async def get_uae_heavy_permit(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "United Arab Emirates",
        "topic": "Heavy vehicle pass permit",
        "sources": [
            OFFICIAL_SOURCES["uae"]["sources"][2],
            OFFICIAL_SOURCES["uae"]["sources"][1],
        ],
        "notes": [
            "Use the MOI service manual and current authority channels for operational details.",
            "This endpoint returns official references, not a live permit issuance transaction.",
        ],
        "generated_at": _utcnow(),
    }


@router.get("/uae/toll/darb")
async def get_uae_darb(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "United Arab Emirates",
        "topic": "Abu Dhabi toll system (Darb)",
        "sources": [OFFICIAL_SOURCES["uae"]["sources"][0]],
        "notes": [
            "The UAE official roadways portal states Darb tolls apply during peak hours.",
            "Vehicle identification is plate-based; no windshield tag is required.",
        ],
        "generated_at": _utcnow(),
    }


@router.get("/uae/toll/salik")
async def get_uae_salik(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "United Arab Emirates",
        "topic": "Dubai Salik toll system",
        "sources": [
            OFFICIAL_SOURCES["uae"]["sources"][3],
            OFFICIAL_SOURCES["uae"]["sources"][4],
        ],
        "generated_at": _utcnow(),
    }


@router.get("/sa/tga/updates")
async def get_saudi_tga_updates(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "Saudi Arabia",
        "topic": "Transport General Authority official references",
        "sources": [
            OFFICIAL_SOURCES["sa"]["sources"][0],
            OFFICIAL_SOURCES["sa"]["sources"][1],
            OFFICIAL_SOURCES["sa"]["sources"][3],
        ],
        "notes": [
            "This endpoint uses official TGA references only.",
            "It avoids publishing secondary-media claims as official updates.",
        ],
        "generated_at": _utcnow(),
    }


@router.get("/sa/gcc/trucks")
async def get_saudi_gcc_trucks(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "Saudi Arabia",
        "topic": "Cross-border and GCC trucking references",
        "sources": [
            OFFICIAL_SOURCES["sa"]["sources"][0],
            OFFICIAL_SOURCES["sa"]["sources"][1],
        ],
        "notes": [
            "Review the official TGA portal and regulations before operational use.",
            "Country-specific GCC truck policy updates should be validated against current TGA publications.",
        ],
        "generated_at": _utcnow(),
    }


@router.get("/sa/logisti")
async def get_saudi_logisti(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "country": "Saudi Arabia",
        "topic": "Logisti platform",
        "sources": [OFFICIAL_SOURCES["sa"]["sources"][2]],
        "generated_at": _utcnow(),
    }
