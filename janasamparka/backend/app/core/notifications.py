"""
Notification service for sending emails and in-app notifications
"""
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
# TODO: Uncomment when implementing production email notifications
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.core.config import settings

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.department import Department
    from app.models.user import User


class NotificationService:
    """Service for sending notifications via email and in-app"""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email notification
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        # TODO: Implement actual email sending
        # For now, just log the notification
        print(f"""
        ====== EMAIL NOTIFICATION ======
        To: {to_email}
        Subject: {subject}
        Body: {body}
        ================================
        """)
        
        # In production, use SMTP or email service like SendGrid
        # Example with SMTP:
        # try:
        #     msg = MIMEMultipart('alternative')
        #     msg['Subject'] = subject
        #     msg['From'] = settings.EMAIL_FROM
        #     msg['To'] = to_email
        #     
        #     msg.attach(MIMEText(body, 'plain'))
        #     if html_body:
        #         msg.attach(MIMEText(html_body, 'html'))
        #     
        #     with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        #         server.starttls()
        #         server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        #         server.send_message(msg)
        #     
        #     return True
        # except Exception as e:
        #     print(f"Email send error: {e}")
        #     return False
        
        return True
    
    @staticmethod
    async def send_sms(phone: str, message: str) -> bool:
        """
        Send SMS notification
        
        Args:
            phone: Recipient phone number
            message: SMS message text
        
        Returns:
            True if sent successfully, False otherwise
        """
        # TODO: Implement actual SMS sending
        print(f"""
        ====== SMS NOTIFICATION ======
        To: {phone}
        Message: {message}
        ==============================
        """)
        
        # In production, use Twilio or AWS SNS
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     body=message,
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=phone
        # )
        
        return True


class ComplaintNotifications:
    """Complaint-specific notification templates and logic"""
    
    @staticmethod
    async def notify_complaint_created(complaint: "Complaint", user: "User") -> None:
        """Notify when a new complaint is created"""
        notification = NotificationService()
        
        # Notify citizen via SMS
        if user.phone:
            await notification.send_sms(
                user.phone,
                f"Complaint #{str(complaint.id)[:8]} registered. Track status on Janasamparka portal."
            )
    
    @staticmethod
    async def notify_complaint_assigned(complaint: "Complaint", department: "Department", officer: "User") -> None:
        """Notify when complaint is assigned"""
        notification = NotificationService()
        
        # Notify department officer via SMS
        if officer and officer.phone:
            await notification.send_sms(
                officer.phone,
                f"New complaint assigned: {complaint.title[:50]}"
            )
    
    @staticmethod
    async def notify_status_changed(complaint: "Complaint", old_status: str, new_status: str, citizen: "User") -> None:
        """Notify when complaint status changes"""
        notification = NotificationService()
        
        # Notify citizen via SMS
        if citizen and citizen.phone:
            await notification.send_sms(
                citizen.phone,
                f"Complaint #{str(complaint.id)[:8]} status: {new_status}"
            )
    
    @staticmethod
    async def notify_work_approved(complaint: "Complaint", citizen: "User") -> None:
        """Notify when work is approved"""
        notification = NotificationService()
        
        # Notify citizen via SMS
        if citizen and citizen.phone:
            await notification.send_sms(
                citizen.phone,
                f"Complaint #{str(complaint.id)[:8]} approved & closed. Thank you!"
            )
    
    @staticmethod
    async def notify_work_rejected(complaint: "Complaint", reason: str, officer: "User") -> None:
        """Notify when work is rejected and rework needed"""
        notification = NotificationService()
        
        # Notify officer via SMS
        if officer and officer.phone:
            await notification.send_sms(
                officer.phone,
                f"Complaint #{str(complaint.id)[:8]} needs rework. Check portal for details."
            )
    
    @staticmethod
    async def notify_escalation(complaint: "Complaint", escalated_to: "User") -> None:
        """Notify when complaint is escalated"""
        notification = NotificationService()
        
        # Notify escalated user via SMS
        if escalated_to and escalated_to.phone:
            await notification.send_sms(
                escalated_to.phone,
                f"ESCALATION: Complaint #{str(complaint.id)[:8]} requires immediate attention"
            )


# Email templates
EMAIL_TEMPLATES = {
    "complaint_created": """
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Complaint Registered Successfully</h2>
                <p>Dear {citizen_name},</p>
                <p>Your complaint has been registered in the Janasamparka system.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Complaint ID:</strong> {complaint_id}</p>
                    <p><strong>Title:</strong> {complaint_title}</p>
                    <p><strong>Category:</strong> {complaint_category}</p>
                    <p><strong>Status:</strong> <span style="color: #2563eb;">{complaint_status}</span></p>
                </div>
                
                <p>You will receive updates as your complaint progresses through our system.</p>
                
                <p>Thank you for using Janasamparka.</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="font-size: 12px; color: #6b7280;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
    """,
    
    "status_update": """
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Complaint Status Update</h2>
                <p>Dear {citizen_name},</p>
                <p>There has been an update to your complaint.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Complaint ID:</strong> {complaint_id}</p>
                    <p><strong>Title:</strong> {complaint_title}</p>
                    <p><strong>Previous Status:</strong> {old_status}</p>
                    <p><strong>New Status:</strong> <span style="color: #16a34a;">{new_status}</span></p>
                    {note}
                </div>
                
                <p>Track your complaint progress on the Janasamparka portal.</p>
                
                <p>Thank you for your patience.</p>
            </div>
        </body>
        </html>
    """
}
