from fastapi import APIRouter, Query, HTTPException
import requests
import os
import imaplib
import email
from email.header import decode_header
from config.config import *
from config.database import *
from typing import List, Dict

route = APIRouter(prefix="/email", tags=["Email"])

def get_and_store_emails(max_results: int = 10) -> Dict:
    """
    Get emails from Gmail using IMAP and store them in Supabase
    Returns success status and stored data
    """
    try:
        # Connect to IMAP server
        if EMAIL["USE_SSL"]:
            mail = imaplib.IMAP4_SSL(EMAIL["IMAP_SERVER"], EMAIL["IMAP_PORT"])
        else:
            mail = imaplib.IMAP4(EMAIL["IMAP_SERVER"], EMAIL["IMAP_PORT"])
        
        # Login
        mail.login(EMAIL["EMAIL_ADDRESS"], EMAIL["EMAIL_PASSWORD"])
        
        # Select inbox
        mail.select("INBOX")
        
        # Search for emails
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        # Get the latest emails (limit by max_results)
        latest_emails = email_ids[-max_results:] if len(email_ids) >= max_results else email_ids
        
        email_data = []
        for email_id in latest_emails:
            # Fetch email
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            
            if status == "OK":
                # Parse email
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Get sender and recipient
                from_email = msg.get("From", "Unknown Sender")
                to_email = msg.get("To", EMAIL["EMAIL_ADDRESS"])  # Default to our email
                
                # Get date and parse it
                date_str = msg.get("Date", "")
                received_at = None
                if date_str:
                    try:
                        from email.utils import parsedate_to_datetime
                        received_at = parsedate_to_datetime(date_str).time().strftime('%H:%M:%S')
                    except:
                        received_at = None
                
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # Prepare data for Supabase (matching table schema)
                email_record = {
                    'to_emai': to_email,  # Note: keeping the typo as per your schema
                    'from_email': from_email,
                    'body': body,
                    'received_at': received_at
                }
                
                email_data.append(email_record)
        
        # Close IMAP connection
        mail.close()
        mail.logout()
        
        # Store in Supabase
        if email_data:
            result = supabase_client.table("email_data").insert(email_data).execute()
            return {
                "success": True,
                "message": f"Successfully fetched and stored {len(email_data)} emails",
                "data": result.data
            }
        else:
            return {
                "success": False,
                "message": "No emails found to store"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching and storing emails: {str(e)}")

@route.post("/sync-emails")
async def sync_emails(max_results: int = Query(10, description="Maximum number of emails to fetch and store")):
    """Fetch emails from Gmail and store them in Supabase"""
    result = get_and_store_emails(max_results)
    return result

@route.get("/emails")
async def get_stored_emails(limit: int = Query(10, description="Maximum number of stored emails to retrieve")):
    """Get stored emails from Supabase"""
    try:
        result = supabase_client.table("email_data").select("*").order("created_at", desc=True).limit(limit).execute()
        return {
            "success": True,
            "emails": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emails: {str(e)}")
