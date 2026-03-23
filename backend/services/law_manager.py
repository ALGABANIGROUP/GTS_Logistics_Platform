from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..models.transport_laws import (
    LawUpdateRequest,
    TransportLaw,
    TransportType,
    SafetyStandardLevel,
)


class TransportLawManager:
    def __init__(self, data_file: str = "transport_laws.json") -> None:
        self.data_file = Path(data_file)
        self.laws: Dict[str, TransportLaw] = {}
        self._initialize_laws()

    def _initialize_laws(self) -> None:
        sample_laws = [
            TransportLaw(
                id="USA-2023-RD",
                country_code="US",
                country_name="United States",
                title="Federal Motor Carrier Safety Regulations",
                description="FMCSA regulations for commercial vehicle safety",
                transport_type=TransportType.ROAD,
                year=2023,
                safety_standards=SafetyStandardLevel.HIGH,
                next_update_due=datetime(2024, 12, 31),
                tags=["compliance", "fmcsa", "safety", "commercial"],
            ),
            TransportLaw(
                id="KSA-2023-RD",
                country_code="SA",
                country_name="Saudi Arabia",
                title="Saudi Road Transport Safety Regulations",
                description="Comprehensive road safety laws for KSA",
                transport_type=TransportType.ROAD,
                year=2023,
                safety_standards=SafetyStandardLevel.MEDIUM,
                next_update_due=datetime(2024, 6, 30),
                tags=["road", "safety", "gcc", "compliance"],
            ),
            TransportLaw(
                id="UAE-2023-ML",
                country_code="AE",
                country_name="United Arab Emirates",
                title="UAE Multimodal Transport Law",
                description="Regulations for combined transport modes",
                transport_type=TransportType.MULTIMODAL,
                year=2023,
                safety_standards=SafetyStandardLevel.HIGH,
                next_update_due=datetime(2024, 9, 30),
                tags=["multimodal", "logistics", "gcc"],
            ),
            TransportLaw(
                id="CAN-2023-RD",
                country_code="CA",
                country_name="Canada",
                title="Canada Transportation Act",
                description="Federal transportation regulations",
                transport_type=TransportType.ROAD,
                year=2023,
                safety_standards=SafetyStandardLevel.HIGH,
                next_update_due=datetime(2024, 11, 30),
                tags=["federal", "safety", "compliance"],
            ),
            TransportLaw(
                id="GBR-2023-AIR",
                country_code="GB",
                country_name="United Kingdom",
                title="UK Aviation Safety Regulations",
                description="CAA regulations for air transport safety",
                transport_type=TransportType.AIR,
                year=2023,
                safety_standards=SafetyStandardLevel.CRITICAL,
                next_update_due=datetime(2024, 8, 31),
                tags=["aviation", "caa", "safety"],
            ),
            TransportLaw(
                id="JPN-2023-SEA",
                country_code="JP",
                country_name="Japan",
                title="Japanese Maritime Transport Law",
                description="Regulations for sea transport and ports",
                transport_type=TransportType.SEA,
                year=2023,
                safety_standards=SafetyStandardLevel.HIGH,
                next_update_due=datetime(2024, 7, 31),
                tags=["shipping", "ports", "maritime"],
            ),
        ]

        for law in sample_laws:
            self.laws[law.id] = law

    async def check_for_updates(self) -> List[TransportLaw]:
        today = datetime.now()
        return [law for law in self.laws.values() if law.next_update_due <= today]

    async def update_law(self, law_id: str, update_request: LawUpdateRequest) -> Optional[TransportLaw]:
        if law_id not in self.laws:
            return None

        law = self.laws[law_id]
        new_description = update_request.new_content or law.description

        updated_law = TransportLaw(
            id=f"{law.country_code}-{update_request.update_date.year}-{law.transport_type.value.upper()}",
            country_code=law.country_code,
            country_name=law.country_name,
            title=law.title,
            description=new_description,
            transport_type=law.transport_type,
            year=update_request.update_date.year,
            safety_standards=law.safety_standards,
            next_update_due=update_request.update_date + timedelta(days=365),
            document_url=update_request.document_url or law.document_url,
            tags=[*law.tags, "updated"],
        )

        self.laws[updated_law.id] = updated_law
        if "superseded" not in law.tags:
            law.tags.append("superseded")

        return updated_law

    def search_laws(
        self,
        country_code: Optional[str] = None,
        transport_type: Optional[TransportType] = None,
        year: Optional[int] = None,
        safety_level: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[TransportLaw]:
        results = list(self.laws.values())

        if country_code:
            results = [law for law in results if law.country_code == country_code.upper()]

        if transport_type:
            results = [law for law in results if law.transport_type == transport_type]

        if year:
            results = [law for law in results if law.year == year]

        if safety_level:
            results = [law for law in results if law.safety_standards == safety_level]

        if tags:
            results = [law for law in results if any(tag in law.tags for tag in tags)]

        return sorted(results, key=lambda x: (x.country_name, x.year), reverse=True)

    def get_law_comparison(self, law_ids: List[str]) -> Dict:
        laws_to_compare = [self.laws[lid] for lid in law_ids if lid in self.laws]

        return {
            "count": len(laws_to_compare),
            "laws": laws_to_compare,
            "summary": {
                "countries": list({l.country_name for l in laws_to_compare}),
                "years": list({l.year for l in laws_to_compare}),
                "transport_types": list({l.transport_type.value for l in laws_to_compare}),
                "safety_levels": list({l.safety_standards for l in laws_to_compare}),
            },
        }

    def export_to_json(self, filepath: str = "transport_laws_export.json") -> str:
        laws_data = [law.model_dump() for law in self.laws.values()]

        with open(filepath, "w", encoding="utf-8") as f:
            import json

            json.dump(laws_data, f, indent=2, default=str)

        return filepath
