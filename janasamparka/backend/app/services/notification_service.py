"""
Notification Service for Scheduled Broadcasts and Multi-channel Messaging
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.config import settings
from app.core.logging import logger
from app.models.user import User
from app.models.citizen_engagement import (
    ScheduledBroadcast, BroadcastDelivery, BroadcastStatus
)
from app.services.realtime_service import realtime_service


class NotificationChannel:
    """Base class for notification channels"""
    
    async def send(self, recipient: str, message: Dict[str, Any]) -> bool:
        """Send notification through this channel"""
        raise NotImplementedError
    
    async def bulk_send(self, recipients: List[str], message: Dict[str, Any]) -> List[bool]:
        """Send bulk notifications"""
        results = []
        for recipient in recipients:
            result = await self.send(recipient, message)
            results.append(result)
        return results


class PushNotificationChannel(NotificationChannel):
    """Push notification channel"""
    
    def __init__(self):
        self.fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
    
    async def send(self, device_token: str, message: Dict[str, Any]) -> bool:
        """Send push notification via FCM"""
        
        if not self.fcm_server_key:
            logger.warning("FCM server key not configured")
            return False
        
        try:
            import aiohttp
            
            payload = {
                "to": device_token,
                "notification": {
                    "title": message.get("title", ""),
                    "body": message.get("message", ""),
                    "icon": message.get("icon", "/icon.png"),
                    "click_action": message.get("click_action", "/"),
                    "badge": message.get("badge", "1"),
                    "sound": message.get("sound", "default")
                },
                "data": message.get("data", {}),
                "priority": "high"
            }
            
            headers = {
                "Authorization": f"key={self.fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.fcm_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("success", 0) > 0
                    else:
                        error_text = await response.text()
                        logger.error("Push notification failed", error=error_text)
                        return False
                        
        except Exception as e:
            logger.error("Push notification error", error=str(e))
            return False
    
    async def bulk_send(self, device_tokens: List[str], message: Dict[str, Any]) -> List[bool]:
        """Send bulk push notifications"""
        
        # FCM supports multicast to multiple tokens
        if not self.fcm_server_key:
            return [False] * len(device_tokens)
        
        try:
            import aiohttp
            
            # Split into batches of 500 (FCM limit)
            batch_size = 500
            results = []
            
            for i in range(0, len(device_tokens), batch_size):
                batch_tokens = device_tokens[i:i + batch_size]
                
                payload = {
                    "registration_ids": batch_tokens,
                    "notification": {
                        "title": message.get("title", ""),
                        "body": message.get("message", ""),
                        "icon": message.get("icon", "/icon.png"),
                        "click_action": message.get("click_action", "/"),
                        "badge": message.get("badge", "1"),
                        "sound": message.get("sound", "default")
                    },
                    "data": message.get("data", {}),
                    "priority": "high"
                }
                
                headers = {
                    "Authorization": f"key={self.fcm_server_key}",
                    "Content-Type": "application/json"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.fcm_url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            batch_results = [True] * result.get("success", 0)
                            batch_results.extend([False] * result.get("failure", 0))
                            results.extend(batch_results)
                        else:
                            results.extend([False] * len(batch_tokens))
            
            return results
            
        except Exception as e:
            logger.error("Bulk push notification error", error=str(e))
            return [False] * len(device_tokens)


class SMSChannel(NotificationChannel):
    """SMS notification channel"""
    
    def __init__(self):
        self.sms_provider = getattr(settings, 'SMS_PROVIDER', 'twilio')
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    
    async def send(self, phone_number: str, message: Dict[str, Any]) -> bool:
        """Send SMS notification"""
        
        if self.sms_provider == "twilio":
            return await self._send_twilio_sms(phone_number, message)
        else:
            # Mock SMS for development
            logger.info("Mock SMS sent", phone=phone_number, message=message.get("message", ""))
            return True
    
    async def _send_twilio_sms(self, phone_number: str, message: Dict[str, Any]) -> bool:
        """Send SMS via Twilio"""
        
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            logger.warning("Twilio credentials not configured")
            return False
        
        try:
            from twilio.rest import Client
            from twilio.base.exceptions import TwilioRestException
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message_obj = client.messages.create(
                body=message.get("message", ""),
                from_=self.twilio_phone_number,
                to=phone_number
            )
            
            logger.info("SMS sent successfully", 
                       sid=message_obj.sid, to=phone_number)
            return True
            
        except TwilioRestException as e:
            logger.error("Twilio SMS failed", error=str(e))
            return False
        except Exception as e:
            logger.error("SMS sending error", error=str(e))
            return False


class EmailChannel(NotificationChannel):
    """Email notification channel"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', None)
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@janasamparka.in')
    
    async def send(self, email_address: str, message: Dict[str, Any]) -> bool:
        """Send email notification"""
        
        if not self.smtp_server:
            logger.warning("SMTP server not configured")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.get("title", "Janasamparka Notification")
            msg['From'] = self.from_email
            msg['To'] = email_address
            
            # Add text and HTML parts
            text_content = message.get("message", "")
            html_content = message.get("html_message", f"<p>{text_content}</p>")
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Add attachments if any
            for attachment in message.get("attachments", []):
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("Email sent successfully", to=email_address)
            return True
            
        except Exception as e:
            logger.error("Email sending error", error=str(e))
            return False


class WhatsAppChannel(NotificationChannel):
    """WhatsApp notification channel"""
    
    def __init__(self):
        self.whatsapp_provider = getattr(settings, 'WHATSAPP_PROVIDER', 'twilio')
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.twilio_whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
    
    async def send(self, phone_number: str, message: Dict[str, Any]) -> bool:
        """Send WhatsApp message"""
        
        if self.whatsapp_provider == "twilio":
            return await self._send_twilio_whatsapp(phone_number, message)
        else:
            # Mock WhatsApp for development
            logger.info("Mock WhatsApp sent", phone=phone_number, message=message.get("message", ""))
            return True
    
    async def _send_twilio_whatsapp(self, phone_number: str, message: Dict[str, Any]) -> bool:
        """Send WhatsApp via Twilio"""
        
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_whatsapp_number]):
            logger.warning("Twilio WhatsApp credentials not configured")
            return False
        
        try:
            from twilio.rest import Client
            from twilio.base.exceptions import TwilioRestException
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message_obj = client.messages.create(
                body=message.get("message", ""),
                from_=f'whatsapp:{self.twilio_whatsapp_number}',
                to=f'whatsapp:{phone_number}'
            )
            
            logger.info("WhatsApp message sent successfully", 
                       sid=message_obj.sid, to=phone_number)
            return True
            
        except TwilioRestException as e:
            logger.error("Twilio WhatsApp failed", error=str(e))
            return False
        except Exception as e:
            logger.error("WhatsApp sending error", error=str(e))
            return False


class InAppChannel(NotificationChannel):
    """In-app notification channel"""
    
    async def send(self, user_id: str, message: Dict[str, Any]) -> bool:
        """Send in-app notification via WebSocket"""
        
        try:
            await realtime_service.send_to_user(user_id, {
                "type": "broadcast",
                "data": message
            })
            
            logger.info("In-app notification sent", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("In-app notification error", error=str(e))
            return False
    
    async def bulk_send(self, user_ids: List[str], message: Dict[str, Any]) -> List[bool]:
        """Send bulk in-app notifications"""
        
        results = []
        for user_id in user_ids:
            result = await self.send(user_id, message)
            results.append(result)
        return results


class NotificationService:
    """Main notification service for managing multi-channel broadcasts"""
    
    def __init__(self):
        self.channels = {
            'push': PushNotificationChannel(),
            'sms': SMSChannel(),
            'email': EmailChannel(),
            'whatsapp': WhatsAppChannel(),
            'in_app': InAppChannel()
        }
    
    async def send_broadcast(self, broadcast_id: str) -> Dict[str, Any]:
        """Send scheduled broadcast to all target users"""
        
        db = next(get_db())
        try:
            # Get broadcast details
            broadcast = db.query(ScheduledBroadcast).filter(
                ScheduledBroadcast.id == broadcast_id
            ).first()
            
            if not broadcast:
                logger.error("Broadcast not found", broadcast_id=broadcast_id)
                return {"success": False, "error": "Broadcast not found"}
            
            if broadcast.status != BroadcastStatus.SCHEDULED:
                logger.warning("Broadcast already processed", 
                             broadcast_id=broadcast_id, status=broadcast.status.value)
                return {"success": False, "error": "Broadcast already processed"}
            
            # Get target users
            target_users = await self._get_target_users(broadcast, db)
            
            if not target_users:
                logger.warning("No target users found for broadcast", broadcast_id=broadcast_id)
                broadcast.status = BroadcastStatus.FAILED
                db.commit()
                return {"success": False, "error": "No target users found"}
            
            # Prepare message for each channel
            message = self._prepare_message(broadcast)
            
            # Send notifications through each enabled channel
            delivery_results = {}
            total_sent = 0
            
            for channel_name, channel in self.channels.items():
                if getattr(broadcast, f"send_{channel_name}", False) or (channel_name == "in_app" and broadcast.show_in_app):
                    
                    if channel_name == "push":
                        # Send to device tokens
                        device_tokens = [user.device_token for user in target_users if user.device_token]
                        if device_tokens:
                            results = await channel.bulk_send(device_tokens, message)
                            delivery_results[channel_name] = sum(results)
                            total_sent += sum(results)
                    
                    elif channel_name == "sms":
                        # Send to phone numbers
                        phone_numbers = [user.phone for user in target_users if user.phone]
                        if phone_numbers:
                            results = await channel.bulk_send(phone_numbers, message)
                            delivery_results[channel_name] = sum(results)
                            total_sent += sum(results)
                    
                    elif channel_name == "email":
                        # Send to email addresses
                        email_addresses = [user.email for user in target_users if user.email]
                        if email_addresses:
                            results = await channel.bulk_send(email_addresses, message)
                            delivery_results[channel_name] = sum(results)
                            total_sent += sum(results)
                    
                    elif channel_name == "whatsapp":
                        # Send to phone numbers via WhatsApp
                        phone_numbers = [user.phone for user in target_users if user.phone]
                        if phone_numbers:
                            results = await channel.bulk_send(phone_numbers, message)
                            delivery_results[channel_name] = sum(results)
                            total_sent += sum(results)
                    
                    elif channel_name == "in_app":
                        # Send to user IDs
                        user_ids = [user.id for user in target_users]
                        if user_ids:
                            results = await channel.bulk_send(user_ids, message)
                            delivery_results[channel_name] = sum(results)
                            total_sent += sum(results)
            
            # Create delivery records
            await self._create_delivery_records(broadcast, target_users, delivery_results, db)
            
            # Update broadcast status
            broadcast.status = BroadcastStatus.SENT
            broadcast.sent_at = datetime.utcnow()
            broadcast.sent_count = total_sent
            broadcast.delivered_count = total_sent  # Will be updated via webhooks
            
            db.commit()
            
            logger.info("Broadcast sent successfully", 
                       broadcast_id=broadcast_id,
                       total_sent=total_sent,
                       channels=list(delivery_results.keys()))
            
            return {
                "success": True,
                "total_sent": total_sent,
                "delivery_results": delivery_results
            }
            
        except Exception as e:
            logger.error("Failed to send broadcast", 
                        broadcast_id=broadcast_id, error=str(e))
            
            # Update status to failed
            if broadcast:
                broadcast.status = BroadcastStatus.FAILED
                db.commit()
            
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    async def _get_target_users(self, broadcast: ScheduledBroadcast, db: Session) -> List[User]:
        """Get list of target users for broadcast"""
        
        query = db.query(User).filter(User.constituency_id == broadcast.constituency_id)
        
        if not broadcast.target_all:
            # Apply filters
            if broadcast.target_roles:
                target_roles = broadcast.target_roles.split(',')
                query = query.filter(User.role.in_(target_roles))
            
            if broadcast.target_wards:
                target_wards = broadcast.target_wards.split(',')
                query = query.filter(User.ward_id.in_(target_wards))
            
            if broadcast.target_departments:
                target_departments = broadcast.target_departments.split(',')
                query = query.filter(User.department_id.in_(target_departments))
        
        return query.all()
    
    def _prepare_message(self, broadcast: ScheduledBroadcast) -> Dict[str, Any]:
        """Prepare message content for different channels"""
        
        base_message = {
            "title": broadcast.title,
            "message": broadcast.message,
            "data": {
                "broadcast_id": broadcast.id,
                "type": broadcast.broadcast_type.value,
                "priority": broadcast.priority,
                "link_url": broadcast.link_url,
                "video_url": broadcast.video_url
            },
            "click_action": f"/broadcast/{broadcast.id}",
            "icon": "/icon.png",
            "badge": "1"
        }
        
        # Add HTML version for email
        html_message = f"""
        <html>
        <body>
            <h2>{broadcast.title}</h2>
            <p>{broadcast.message}</p>
            {f'<p><a href="{broadcast.link_url}">{broadcast.link_text or "Click here"}</a></p>' if broadcast.link_url else ''}
            {f'<p><a href="{broadcast.video_url}">Watch Video</a></p>' if broadcast.video_url else ''}
            <hr>
            <p><small>Sent via Janasamparka</small></p>
        </body>
        </html>
        """
        
        base_message["html_message"] = html_message
        
        # Add attachments if any
        if broadcast.attachment_urls:
            base_message["attachments"] = []
            for url in broadcast.attachment_urls.split(','):
                base_message["attachments"].append({
                    "filename": url.split('/')[-1],
                    "content": url  # In real implementation, would download and attach
                })
        
        return base_message
    
    async def _create_delivery_records(self, broadcast: ScheduledBroadcast, 
                                     target_users: List[User], 
                                     delivery_results: Dict[str, int], 
                                     db: Session):
        """Create delivery tracking records"""
        
        for user in target_users:
            delivery = BroadcastDelivery(
                id=str(uuid.uuid4()),
                broadcast_id=broadcast.id,
                user_id=user.id,
                push_sent=delivery_results.get('push', 0) > 0,
                sms_sent=delivery_results.get('sms', 0) > 0,
                email_sent=delivery_results.get('email', 0) > 0,
                whatsapp_sent=delivery_results.get('whatsapp', 0) > 0,
                shown_in_app=delivery_results.get('in_app', 0) > 0
            )
            db.add(delivery)
    
    async def schedule_broadcast_reminder(self, broadcast_id: str, reminder_minutes: int = 60):
        """Schedule reminder for upcoming broadcast"""
        
        db = next(get_db())
        try:
            broadcast = db.query(ScheduledBroadcast).filter(
                ScheduledBroadcast.id == broadcast_id
            ).first()
            
            if not broadcast:
                return
            
            # Schedule reminder task
            reminder_time = broadcast.scheduled_at - timedelta(minutes=reminder_minutes)
            
            # In production, this would use a task queue like Celery
            # For now, we'll just log it
            logger.info("Broadcast reminder scheduled", 
                       broadcast_id=broadcast_id,
                       reminder_time=reminder_time)
            
        finally:
            db.close()
    
    async def cancel_broadcast(self, broadcast_id: str) -> bool:
        """Cancel scheduled broadcast"""
        
        db = next(get_db())
        try:
            broadcast = db.query(ScheduledBroadcast).filter(
                ScheduledBroadcast.id == broadcast_id
            ).first()
            
            if not broadcast:
                return False
            
            if broadcast.status == BroadcastStatus.SENT:
                return False  # Cannot cancel sent broadcast
            
            broadcast.status = BroadcastStatus.CANCELLED
            db.commit()
            
            logger.info("Broadcast cancelled", broadcast_id=broadcast_id)
            return True
            
        except Exception as e:
            logger.error("Failed to cancel broadcast", 
                        broadcast_id=broadcast_id, error=str(e))
            return False
        finally:
            db.close()
    
    async def get_broadcast_analytics(self, broadcast_id: str) -> Dict[str, Any]:
        """Get analytics for a broadcast"""
        
        db = next(get_db())
        try:
            broadcast = db.query(ScheduledBroadcast).filter(
                ScheduledBroadcast.id == broadcast_id
            ).first()
            
            if not broadcast:
                return {}
            
            # Get delivery records
            deliveries = db.query(BroadcastDelivery).filter(
                BroadcastDelivery.broadcast_id == broadcast_id
            ).all()
            
            # Calculate metrics
            total_targets = len(deliveries)
            sent_count = sum(1 for d in deliveries if d.push_sent or d.sms_sent or d.email_sent)
            delivered_count = sum(1 for d in deliveries if d.push_delivered or d.sms_delivered or d.email_delivered)
            read_count = sum(1 for d in deliveries if d.push_read or d.email_read)
            click_count = sum(1 for d in deliveries if d.clicked_in_app)
            
            return {
                "broadcast_id": broadcast_id,
                "total_targets": total_targets,
                "sent_count": sent_count,
                "delivered_count": delivered_count,
                "read_count": read_count,
                "click_count": click_count,
                "delivery_rate": (delivered_count / total_targets * 100) if total_targets > 0 else 0,
                "read_rate": (read_count / delivered_count * 100) if delivered_count > 0 else 0,
                "click_rate": (click_count / read_count * 100) if read_count > 0 else 0
            }
            
        finally:
            db.close()


# Global service instance
notification_service = NotificationService()
