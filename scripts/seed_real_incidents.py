import asyncio
import random
from datetime import datetime, timedelta
from backend.database import async_session
from backend.models.safety_enhanced import Incident, IncidentSeverity, IncidentStatus

async def seed_real_incidents():
    """
    إدخال بيانات حوادث حقيقية (محاكاة لحوادث فعلية)
    """
    async with async_session() as session:
        # بيانات حوادث حقيقية (محاكاة)
        incidents_data = [
            {
                "incident_number": "INC-2026-001",
                "incident_date": datetime.now() - timedelta(days=5),
                "incident_type": "accident",
                "driver_id": 1,
                "vehicle_id": 1,
                "location": "طريق الرياض - جدة، الكيلو 350",
                "description": "تصادم خلفي مع شاحنة أخرى بسبب الأمطار الغزيرة",
                "severity": IncidentSeverity.HIGH,
                "actions_taken": "إسعاف فوري، إبلاغ الشرطة، سحب المركبة",
                "status": IncidentStatus.CLOSED,
                "police_report": "POL-2026-001",
                "weather_conditions": "heavy_rain",
                "road_conditions": "wet",
                "estimated_damage": 15000
            },
            {
                "incident_number": "INC-2026-002",
                "incident_date": datetime.now() - timedelta(days=3),
                "incident_type": "breakdown",
                "driver_id": 2,
                "vehicle_id": 2,
                "location": "طريق الدمام - الخبر",
                "description": "عطل في نظام التبريد",
                "severity": IncidentSeverity.MEDIUM,
                "actions_taken": "سحب المركبة للصيانة",
                "status": IncidentStatus.INVESTIGATING,
                "estimated_damage": 5000
            },
            {
                "incident_number": "INC-2026-003",
                "incident_date": datetime.now() - timedelta(days=1),
                "incident_type": "injury",
                "driver_id": 3,
                "vehicle_id": 3,
                "location": "مستودع الرياض",
                "description": "إصابة أثناء التحميل بسبب سوء الأحوال الجوية",
                "severity": IncidentSeverity.HIGH,
                "actions_taken": "نقل للمستشفى، إبلاغ المشرف",
                "status": IncidentStatus.OPEN,
                "weather_conditions": "strong_winds",
                "injuries_count": 1
            }
        ]

        for data in incidents_data:
            incident = Incident(**data)
            session.add(incident)

        await session.commit()
        print(f"✅ تم إضافة {len(incidents_data)} حوادث حقيقية")

if __name__ == "__main__":
    asyncio.run(seed_real_incidents())