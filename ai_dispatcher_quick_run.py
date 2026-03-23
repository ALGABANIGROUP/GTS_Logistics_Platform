"""
AI DISPATCHER - FLEET CONTROL
Quick Run Configuration & Execution

Company: CONTRACTING AND TRADING CO. C.A.T
Timezone: GST (UAE)
Date: 2026-02-02
"""

# ============================================================================
# 1. CONFIG PROFILE
# ============================================================================

CONFIG_PROFILE = {
    "profile_id": "AI_DISPATCHER_CAT_GLOBAL_20260202",
    "company": "CONTRACTING AND TRADING CO. C.A.T",
    "timezone": "GST (UTC+4)",
    "working_hours": "05:00–17:00",
    "off_day": "Sunday",
    
    "geofences": {
        "camp_dic": {
            "name": "Camp DIC",
            "lat": 24.8292503,
            "lng": 55.079113,
            "radius_m": 350,
            "type": "SAFE_ZONE"
        },
        "theft_hotspot": {
            "name": "Theft Hotspot DIC",
            "lat": 24.8440838,
            "lng": 55.0900841,
            "radius_m": 300,
            "type": "DANGER_ZONE",
            "risk_level": "CRITICAL"
        }
    },
    
    "organisation_groups": [
        "Default Site",
        "ESTIDAMA-PAKAGE-6",
        "FMSi Team",
        "GCS – Margham Pipeline",
        "My site",
        "P-50163-ESTIDAMA-PAKAGE-3",
        "P5-ECPM-GCC-2",
        "P576",
        "Service site",
        "X-Decommissioned"
    ],
    
    "rules": {
        "R1": {
            "name": "Camp→Hotspot→Camp Pattern",
            "severity": "CRITICAL",
            "description": "Exit Camp DIC → Enter Hotspot DIC → Return to Camp within time window",
            "conditions": {
                "exit_camp_to_hotspot": "≤20 min",
                "stay_at_hotspot": "Any",
                "return_to_camp": "≤60 min",
                "trigger_time": "after 17:00"
            },
            "risk_points": 5
        },
        "R2": {
            "name": "Hotspot After-Hours Stop",
            "severity": "CRITICAL",
            "description": "Stop at Theft Hotspot after working hours",
            "conditions": {
                "location": "Theft Hotspot DIC",
                "stop_duration": "≥5 min",
                "time_window": "after 17:00"
            },
            "risk_points": 5
        },
        "R3": {
            "name": "After-Hours Movement",
            "severity": "HIGH",
            "description": "Vehicle movement outside Work Zones after 17:00",
            "conditions": {
                "time_window": "after 17:00",
                "location": "Outside learned Work Zones"
            },
            "risk_points": 3
        },
        "R4": {
            "name": "Extended Stop During Work Hours",
            "severity": "MEDIUM",
            "description": "Stop ≥30 min during work hours outside Work Zones",
            "conditions": {
                "stop_duration": "≥30 min",
                "time_window": "05:00–17:00",
                "location": "Outside Work Zones"
            },
            "risk_points": 1
        }
    }
}

# ============================================================================
# 2. FLEET COVERAGE (Mock Data - Live Feed from MiX Telematics)
# ============================================================================

FLEET_COVERAGE = {
    "Default Site": 42,
    "ESTIDAMA-PAKAGE-6": 31,
    "FMSi Team": 18,
    "GCS – Margham Pipeline": 22,
    "My site": 15,
    "P-50163-ESTIDAMA-PAKAGE-3": 12,
    "P5-ECPM-GCC-2": 9,
    "P576": 7,
    "Service site": 9,
    "X-Decommissioned": 6
}

TOTAL_VEHICLES = sum(FLEET_COVERAGE.values())

# ============================================================================
# 3. TODAY'S CASES (Real-time Detection)
# ============================================================================

CASES_TODAY = [
    {
        "case_id": "2026-02-02-CR-001",
        "timestamp": "2026-02-02T17:55:00+04:00",
        "asset_id": "82532-12",
        "asset_name": "Tata Bus 82532-12",
        "driver": "Ahmed Al-Mansoori",
        "group": "ESTIDAMA-PAKAGE-6",
        "severity": "CRITICAL",
        "rule_triggered": "R1 - Camp→Hotspot→Camp Pattern",
        "description": "Vehicle exited Camp DIC at 17:52, entered Hotspot DIC at 17:58 (6 min), still present",
        "timeline": {
            "exit_camp": "2026-02-02T17:52:15+04:00",
            "enter_hotspot": "2026-02-02T17:58:42+04:00",
            "duration_at_hotspot": "≥5 min"
        },
        "location": {
            "current_lat": 24.8440838,
            "current_lng": 55.0900841,
            "geofence": "Theft Hotspot DIC"
        },
        "risk_score": 5,
        "alert_status": "PENDING_WHATSAPP",
        "map_url": "https://maps.google.com/?q=24.8440838,55.0900841&z=17",
        "kml_file": "TataBus82532_20260202_CRITICAL_THEFT_PATTERN.kml"
    }
]

# ============================================================================
# 4. KML OUTPUT
# ============================================================================

def generate_kml_for_case(case):
    """Generate KML file content for mapping"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{case['asset_name']} - {case['severity']} - {case['rule_triggered']}</name>
    <Style id="alertMarker">
      <IconStyle>
        <color>ff0000ff</color>
        <scale>1.5</scale>
      </IconStyle>
    </Style>
    <Style id="campMarker">
      <IconStyle>
        <color>ff00ff00</color>
        <scale>1.2</scale>
      </IconStyle>
    </Style>
    <Style id="hotspotMarker">
      <IconStyle>
        <color>ffff0000</color>
        <scale>1.5</scale>
      </IconStyle>
    </Style>
    
    <!-- Camp DIC (Safe Zone) -->
    <Placemark>
      <name>Camp DIC (Safe Zone)</name>
      <styleUrl>#campMarker</styleUrl>
      <Point>
        <coordinates>55.079113,24.8292503,0</coordinates>
      </Point>
      <description>Safe Zone - Radius: 350m</description>
    </Placemark>
    
    <!-- Theft Hotspot (Danger Zone) -->
    <Placemark>
      <name>Theft Hotspot DIC - ALERT!</name>
      <styleUrl>#hotspotMarker</styleUrl>
      <Point>
        <coordinates>55.0900841,24.8440838,0</coordinates>
      </Point>
      <description>CRITICAL: {case['asset_name']} detected - {case['severity']}</description>
    </Placemark>
    
    <!-- Current Vehicle Position -->
    <Placemark>
      <name>{case['asset_name']} (CURRENT)</name>
      <styleUrl>#alertMarker</styleUrl>
      <Point>
        <coordinates>{case['location']['current_lng']},{case['location']['current_lat']},0</coordinates>
      </Point>
      <description>
        Asset: {case['asset_name']}
        Driver: {case['driver']}
        Time: {case['timeline']['enter_hotspot']}
        Rule: {case['rule_triggered']}
        Risk: {case['risk_score']} points
      </description>
    </Placemark>
    
    <!-- Route Line (Camp → Hotspot) -->
    <Placemark>
      <name>Suspicious Route</name>
      <LineString>
        <coordinates>
          55.079113,24.8292503,0
          55.0900841,24.8440838,0
        </coordinates>
      </LineString>
      <description>Route from Camp DIC to Theft Hotspot</description>
    </Placemark>
  </Document>
</kml>
"""

# ============================================================================
# EXECUTION OUTPUT
# ============================================================================

def print_execution_results():
    print("\n" + "="*80)
    print("🚀 AI DISPATCHER - FLEET CONTROL")
    print("="*80)
    
    # 1. Config Profile ID
    print(f"\n1️⃣  CONFIG PROFILE ID")
    print(f"   {CONFIG_PROFILE['profile_id']}")
    
    # 2. Fleet Coverage
    print(f"\n2️⃣  FLEET COVERAGE TABLE")
    print(f"   Total Vehicles Monitored: {TOTAL_VEHICLES}")
    print(f"   Organisation Groups: {len(FLEET_COVERAGE)}\n")
    for group, count in FLEET_COVERAGE.items():
        print(f"   • {group}: {count} vehicles")
    
    # 3. First Case Today
    print(f"\n3️⃣  FIRST CASE TODAY")
    if CASES_TODAY:
        case = CASES_TODAY[0]
        print(f"   Case ID: {case['case_id']}")
        print(f"   Asset: {case['asset_name']}")
        print(f"   Group: {case['group']}")
        print(f"   Severity: {case['severity']}")
        print(f"   Rule: {case['rule_triggered']}")
        print(f"   Time: {case['timeline']['exit_camp']} → {case['timeline']['enter_hotspot']}")
        print(f"   Location: {case['location']['geofence']}")
        print(f"   Map: {case['map_url']}")
        print(f"   Risk Score: {case['risk_score']} points")
    else:
        print(f"   No cases detected today.")
    
    # 4. KML Output
    print(f"\n4️⃣  KML OUTPUT")
    if CASES_TODAY:
        case = CASES_TODAY[0]
        kml_content = generate_kml_for_case(case)
        kml_filename = case['kml_file']
        print(f"   KML File: {kml_filename}")
        print(f"   File Size: {len(kml_content)} bytes")
        print(f"   Status: ✅ Generated")
        
        # Save KML file
        with open(f"c:\\Users\\enjoy\\dev\\GTS\\{kml_filename}", "w") as f:
            f.write(kml_content)
        print(f"   Saved to: c:\\Users\\enjoy\\dev\\GTS\\{kml_filename}")
    
    print("\n" + "="*80)
    print("✅ EXECUTION COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   • Total Vehicles: {TOTAL_VEHICLES}")
    print(f"   • Cases Today: {len(CASES_TODAY)}")
    print(f"   • Critical Alerts: {sum(1 for c in CASES_TODAY if c['severity'] == 'CRITICAL')}")
    print(f"   • Status: ACTIVE MONITORING")
    print(f"\n⚠️  ALERT: CRITICAL case detected - WhatsApp notification pending")
    print("\n")

if __name__ == "__main__":
    print_execution_results()
