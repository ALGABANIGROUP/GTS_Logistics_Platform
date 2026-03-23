import os
from openai import AsyncOpenAI
from backend.utils.email_utils import send_email
from backend.database.config import get_db
from backend.models import MessageLog
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import httpx
openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
VOICE_API_URL = 'https://api.example-voice.com/call'

async def log_call_event(db: AsyncSession, message: str, context: str=None):
    log = MessageLog(sender='AI Voice Bot', message=message, timestamp=datetime.utcnow(), context=context)
    db.add(log)
    await db.commit()

async def generate_call_script(event_type: str, customer_name: str, details: dict) -> str:
    """Use GPT to generate personalized voice script."""
    prompt = f'\nYou are a polite virtual assistant working for GTS Logistics. Generate a phone call message based on the event type and customer.\n\nCustomer: {customer_name}\nEvent: {event_type}\nDetails: {details}\n\nGenerate a short professional voice script.\n'
    try:
        response = await openai_client.chat.completions.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': prompt}], temperature=0.5, max_tokens=150)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'Error generating voice message: {str(e)}'

async def initiate_voice_call(customer_phone: str, customer_name: str, event_type: str, details: dict):
    """Main function to generate voice script and initiate call."""
    db = await get_db().__anext__()
    script = await generate_call_script(event_type, customer_name, details)
    await log_call_event(db, message=script, context=f'call:{event_type}:{customer_name}')
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(VOICE_API_URL, json={'to': customer_phone, 'voice_script': script})
            if response.status_code == 200:
                print(f'Call to {customer_name} initiated successfully.')
            else:
                print(f'Voice call failed: {response.text}')
    except Exception as e:
        print(f'Exception in initiating call: {e}')
