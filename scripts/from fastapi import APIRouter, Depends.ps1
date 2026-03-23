from fastapi import APIRouter, Depends
from backend.security.jwt_security import JWTSecurity
from backend.security.audit_logger import AuditLogger
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/bots/my-bot", tags=["my_bot"])

class MyNewBot:
"""وصف وظيفة الـ Bot"""
    
@staticmethod
async def process_request(data: dict, current_user = Depends(JWTSecurity.get_current_user)):
"""معالجة الطلب بأمان"""
        
user_id = current_user['sub']
        
# تسجيل العملية
AuditLogger.log_event(
    event_type="API_CALL",
    user_id=user_id,
    action="MY_BOT_PROCESS",
    resource="my_bot"
)
        
# المنطق هنا
result = await my_bot_logic(data)
        
return result

@router.post("/process")
async def process(data: dict, current_user = Depends(JWTSecurity.get_current_user)):
"""Endpoint لمعالجة البيانات"""
return await MyNewBot.process_request(data, current_user)

import React, { useState } from 'react';
import apiClient from '../../../lib/api-client';

export const MyNewBotPanel = () => {
    const [input, setInput] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleProcess = async () => {
        setLoading(true);
        try {
            const response = await apiClient.post('/bots/my-bot/process', {
                    data: input
                });
            setResult(response.data);
        }
        catch (error) {
            console.error('خطأ:', error);
        }
        finally {
            setLoading(false);
        }
    };

    return (
        <div className="bot-panel">
        <h2>My New Bot</h2>
      
        <input
        value= { input }
        onChange= { (e) = > setInput(e.target.value) }
        placeholder="أدخل البيانات"
        />
      
        <button onClick= { handleProcess } disabled= { loading }>
        { loading ? 'جاري المعالجة...' : 'معالجة' }
        </button>
      
        { result && <div> { JSON.stringify(result) }</div> }
        </div>
    );
};