from openai import OpenAI
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ExternalLoadBoardAgent:
    @staticmethod
    def fetch(source: str = "ai", preferences: Dict[str, str] = {}) -> List[Dict]:
        if source == "ai":
            prompt = ExternalLoadBoardAgent.build_prompt(preferences)

            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a freight broker AI agent that analyzes and suggests profitable load shipments."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.5
                )

                content = response.choices[0].message.content
                return ExternalLoadBoardAgent.parse_response(content or "")
            except Exception as e:
                print("❌ GPT Error:", str(e))
                return []
        else:
            return ExternalLoadBoardAgent.mock_loads()

    @staticmethod
    def build_prompt(preferences: Dict[str, str]) -> str:
        origin = preferences.get("origin", "Los Angeles, CA")
        destination = preferences.get("destination", "Dallas, TX")
        trailer_type = preferences.get("equipment_type", "Dry Van")
        goal = preferences.get("goal", "highest paying loads with lowest deadhead")

        return (
            f"Suggest 5 FTL shipments from {origin} to {destination} using {trailer_type}. "
            f"Prioritize {goal}. Each load should include: origin, destination, rate (USD), "
            f"equipment_type, weight (lbs), length (ft), latitude, longitude, and a short description."
        )

    @staticmethod
    def parse_response(content: str) -> List[Dict]:
        loads = []
        entries = content.split("\n")

        for entry in entries:
            if entry.strip() and ":" in entry:
                try:
                    parts = entry.split(":", 1)[1].strip().split(",")
                    load = {
                        "origin": parts[0].strip(),
                        "destination": parts[1].strip(),
                        "rate": float(parts[2].strip().replace("$", "")),
                        "equipment_type": parts[3].strip(),
                        "weight": int(parts[4].strip().replace("lbs", "")),
                        "length": int(parts[5].strip().replace("ft", "")),
                        "latitude": float(parts[6].strip()),
                        "longitude": float(parts[7].strip()),
                        "description": parts[8].strip() if len(parts) > 8 else ""
                    }
                    loads.append(load)
                except Exception as e:
                    print("❌ Parse Error:", e)
        return loads

    @staticmethod
    def mock_loads() -> List[Dict]:
        return [
            {
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "rate": 3200.0,
                "equipment_type": "Dry Van",
                "weight": 43000,
                "length": 53,
                "latitude": 34.0522,
                "longitude": -118.2437,
                "description": "General goods, no special requirements"
            }
        ]
