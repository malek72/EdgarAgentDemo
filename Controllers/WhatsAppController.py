from fastapi import APIRouter, Query, HTTPException, Request
import requests
import os
import logging
from config.config import *
from config.database import *
from typing import List, Dict
import json
from datetime import datetime
from Agents.core.pipeline_complete import main as run_single_complete_pipeline_test

route = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Logger setup
logger = logging.getLogger("whatsapp")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [whatsapp] %(message)s")

def receive_and_store_message(message_data: Dict) -> Dict:
    """
    Receive WhatsApp message and store it in Supabase
    Returns success status and stored data
    """
    try:
        logger.info("Webhook payload received")
        # Extract message details from WhatsApp webhook payload
        entry_list = message_data.get('entry') or []
        entry = entry_list[0] if entry_list else {}
        changes_list = entry.get('changes') or []
        changes = changes_list[0] if changes_list else {}
        value = changes.get('value', {}) or {}

        # Support both inbound messages and message echoes
        inbound_messages = value.get('messages') or []
        echo_messages = value.get('message_echoes') or []
        logger.info(f"Parsed payload: inbound_count={len(inbound_messages)}, echo_count={len(echo_messages)}")
        
        # Choose first available message from either list
        msg = None
        is_echo = False
        if inbound_messages:
            msg = inbound_messages[0]
            is_echo = False
        elif echo_messages:
            msg = echo_messages[0]
            is_echo = True
        else:
            # Nothing to process; return early to avoid 500
            logger.info("No messages found in payload; nothing to process")
            return {"success": True, "message": "No messages to process", "data": []}

        # Extract message details
        from_number = msg.get('from', '')
        # If echo, WhatsApp sometimes provides 'to' explicitly
        to_number = msg.get('to', '') or value.get('metadata', {}).get('phone_number_id', '')
        message_id = msg.get('id', '')
        timestamp = msg.get('timestamp', '')
        logger.info(f"Selected message: id={message_id}, is_echo={is_echo}, from={from_number}, to={to_number}")

        # Extract message body
        body = ''
        if 'text' in msg:
            body = (msg.get('text') or {}).get('body', '')
        elif 'image' in msg:
            body = f"[Image: {(msg.get('image') or {}).get('caption', 'No caption')}]"
        elif 'document' in msg:
            body = f"[Document: {(msg.get('document') or {}).get('filename', 'Unknown file')}]"
        elif 'audio' in msg:
            body = "[Audio message]"
        elif 'video' in msg:
            body = f"[Video: {(msg.get('video') or {}).get('caption', 'No caption')}]"
        else:
            body = "[Unsupported message type]"
        run_single_complete_pipeline_test(body,'whatesapp')
        # Parse timestamp
        received_at = None
        if timestamp:
            try:
                # Convert WhatsApp timestamp to time format
                dt = datetime.fromtimestamp(int(timestamp))
                received_at = dt.time().strftime('%H:%M:%S')
            except:
                received_at = None
        
        # Prepare data for Supabase (matching table schema)
        whatsapp_record = {
            'from_number': from_number,
            'to_number': to_number,
            'message_body': body,
            'message_sid': message_id,
            'received_at': received_at
        }
        logger.info(f"Prepared DB record: {json.dumps(whatsapp_record, default=str)[:500]}")

        # Store in Supabase
        result = supabase_client.table("whatsapp_messages").insert([whatsapp_record]).execute()
        logger.info(f"DB insert success: rows={len(result.data) if getattr(result, 'data', None) else 0}")
        
        return {
            "success": True,
            "message": "WhatsApp message received and stored successfully",
            "data": result.data
        }
        
    except Exception as e:
        logger.exception("Error in receive_and_store_message")
        raise HTTPException(status_code=500, detail=f"Error receiving and storing WhatsApp message: {str(e)}")

@route.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Webhook endpoint to receive WhatsApp messages"""
    try:
        # Get JSON data from WhatsApp webhook
        body = await request.json()
        logger.info(f"POST /webhook received: {json.dumps(body)[:1000]}")
        
        # Store the message
        result = receive_and_store_message(body)
        logger.info("POST /webhook processed successfully")
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.exception("POST /webhook error")
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

@route.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Webhook verification endpoint for WhatsApp"""
    logger.info(f"GET /webhook verify attempt mode={hub_mode} token={hub_verify_token} challenge={hub_challenge}")
    logger.info(f"Expected token: {WHATSAPP['WEBHOOK_VERIFY_TOKEN']}")
    
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP["WEBHOOK_VERIFY_TOKEN"]:
        logger.info("Verification successful")
        return int(hub_challenge)
    else:
        logger.warning("Verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@route.get("/test-webhook")
async def test_webhook_verification():
    """Test endpoint to check webhook configuration"""
    return {
        "webhook_verify_token": WHATSAPP["WEBHOOK_VERIFY_TOKEN"],
        "phone_number_id": WHATSAPP["PHONE_NUMBER_ID"],
        "api_version": WHATSAPP["API_VERSION"],
        "webhook_url": "https://yourdomain.com/whatsapp/webhook",
        "verification_url": "https://yourdomain.com/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=YOUR_VERIFY_TOKEN"
    }

@route.get("/messages")
async def get_whatsapp_messages(limit: int = Query(10, description="Maximum number of messages to retrieve")):
    """Get stored WhatsApp messages from Supabase"""
    try:
        result = supabase_client.table("whatsapp_messages").select("*").order("created_at", desc=True).limit(limit).execute()
        return {
            "success": True,
            "messages": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving WhatsApp messages: {str(e)}")

@route.post("/send-message")
async def send_whatsapp_message(
    to_number: str,
    message_body: str
):
    """Send WhatsApp message via WhatsApp Business API"""
    try:
        url = f"https://graph.facebook.com/v22.0/825008867364772/messages"
        
        headers = {
        'Authorization': 'Bearer EAAaWMHy2p3IBPssjbx9QFEmqDgkJEPNjUFt9MJrQjUnhjnHgIrCmQnZCdjXcsXTDewj90kENgcYOexFrDXh4Tpq1T5K8utNHBmMKNuRZAqZCc7Nx6eKUuUi9X7IUt7z4D8NzRyykDIO9Fpxlc4lh6SZCPLYROBXihR9TBKaifRwBGZAnIN4I7Y4yZAgpDL2klhb2TzrR0I0PRQw3dG2ki7hLa4HbLlQEoTKEGFY7je6JReJNyZA1t8eZAXSRM82ZBAAZDZD',
        'Content-Type': 'application/json'
        }
        
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": f"91{to_number}",
            "type": "text",
            "text": {
                "body": message_body
            }
        })
        logger.info(f"Sending message: to=91{to_number} body_len={len(message_body)}")
        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(f"Send response: status={response.status_code} body={(response.text or '')[:500]}")
        if response.status_code == 200:
            return {
                "success": True,
                "message": "WhatsApp message sent successfully",
                "response": response.json()
            }
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
    except Exception as e:
        logger.exception("Error in send_whatsapp_message")
        raise HTTPException(status_code=500, detail=f"Error sending WhatsApp message: {str(e)}")
