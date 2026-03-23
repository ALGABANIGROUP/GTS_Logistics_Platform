from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db
from backend.models.customer import Customer
from backend.models.models import Shipment
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Dict
import os
from dotenv import load_dotenv
load_dotenv()
router = APIRouter()
openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class AdPrompt(BaseModel):
    product_or_service: str
    tone: str = 'professional'
    audience: str = 'logistics clients'

@router.post('/ai/marketing/ads/generate')
async def generate_marketing_ad(data: AdPrompt) -> Dict:
    prompt = f'Write a {data.tone} promotional message for a {data.product_or_service} targeted at {data.audience}. End with a call to action.'
    response = await openai_client.chat.completions.create(model='gpt-3.5-turbo', messages=[{'role': 'system', 'content': 'You are a marketing assistant for GTS Logistics.'}, {'role': 'user', 'content': prompt}], temperature=0.7, max_tokens=150)
    ad_text = response.choices[0].message.content.strip()
    return {'ad_text': ad_text}

@router.get('/ai/marketing/insights')
async def get_marketing_insights(db: AsyncSession=Depends(get_db)) -> Dict:
    shipment_result = await db.execute(select(Shipment))
    shipments = shipment_result.scalars().all()
    customer_result = await db.execute(select(Customer))
    customers = customer_result.scalars().all()
    return {'total_customers': len(customers), 'total_shipments': len(shipments), 'active_customers': len([c for c in customers if getattr(c, 'active', False)]), 'insight': 'Consider targeting your top-performing customers for new premium services.'}
