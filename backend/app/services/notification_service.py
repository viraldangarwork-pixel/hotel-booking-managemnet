"""Notification service for email and alerts."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session

from app.core.config import settings


class NotificationService:
    """Service class for sending notifications."""

    def __init__(self, db: Session):
        self.db = db
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email notification."""
        if not self.smtp_host or not self.smtp_user:
            print("Email not configured, skipping...")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to

            # Plain text version
            part1 = MIMEText(body, "plain")
            msg.attach(part1)

            # HTML version if provided
            if html_body:
                part2 = MIMEText(html_body, "html")
                msg.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to, msg.as_string())

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_booking_confirmation_email(
        self,
        to: str,
        guest_name: str,
        booking_ref: str,
        check_in_date: str,
        check_out_date: str,
        room_type: str,
        total_amount: float,
        hotel_name: str,
    ) -> bool:
        """Send booking confirmation email."""
        subject = f"Booking Confirmation - {booking_ref}"

        body = f"""
Dear {guest_name},

Thank you for your booking at {hotel_name}!

Your booking has been confirmed with the following details:

Booking Reference: {booking_ref}
Check-in Date: {check_in_date}
Check-out Date: {check_out_date}
Room Type: {room_type}
Total Amount: ₹{total_amount:.2f}

Please present this confirmation at the front desk during check-in.

We look forward to welcoming you!

Best regards,
{hotel_name}
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f8f9fa; }}
        .details {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Booking Confirmed!</h1>
        </div>
        <div class="content">
            <p>Dear {guest_name},</p>
            <p>Thank you for your booking at <strong>{hotel_name}</strong>!</p>

            <div class="details">
                <div class="detail-row">
                    <span>Booking Reference:</span>
                    <strong>{booking_ref}</strong>
                </div>
                <div class="detail-row">
                    <span>Check-in:</span>
                    <strong>{check_in_date}</strong>
                </div>
                <div class="detail-row">
                    <span>Check-out:</span>
                    <strong>{check_out_date}</strong>
                </div>
                <div class="detail-row">
                    <span>Room Type:</span>
                    <strong>{room_type}</strong>
                </div>
                <div class="detail-row">
                    <span>Total Amount:</span>
                    <strong>₹{total_amount:.2f}</strong>
                </div>
            </div>

            <p>Please present this confirmation at the front desk during check-in.</p>
            <p>We look forward to welcoming you!</p>
        </div>
        <div class="footer">
            <p>{hotel_name}</p>
        </div>
    </div>
</body>
</html>
"""

        return self.send_email(to, subject, body, html_body)

    def send_check_in_reminder_email(
        self,
        to: str,
        guest_name: str,
        booking_ref: str,
        check_in_date: str,
        check_in_time: str,
        hotel_name: str,
        hotel_address: str,
    ) -> bool:
        """Send check-in reminder email."""
        subject = f"Check-in Reminder - {booking_ref}"

        body = f"""
Dear {guest_name},

This is a friendly reminder that your check-in at {hotel_name} is tomorrow!

Booking Reference: {booking_ref}
Check-in Date: {check_in_date}
Check-in Time: {check_in_time}

Hotel Address: {hotel_address}

Please bring a valid ID for check-in.

We look forward to seeing you!

Best regards,
{hotel_name}
"""

        return self.send_email(to, subject, body)

    def send_checkout_receipt_email(
        self,
        to: str,
        guest_name: str,
        booking_ref: str,
        invoice_data: Dict[str, Any],
        hotel_name: str,
    ) -> bool:
        """Send checkout receipt email."""
        subject = f"Thank You for Staying - Receipt {booking_ref}"

        body = f"""
Dear {guest_name},

Thank you for staying at {hotel_name}!

Your stay details:
Booking Reference: {booking_ref}
Check-in: {invoice_data['stay']['check_in']}
Check-out: {invoice_data['stay']['check_out']}
Total Paid: ₹{invoice_data['charges']['total']:.2f}

We hope you had a pleasant stay. We look forward to welcoming you again!

Best regards,
{hotel_name}
"""

        return self.send_email(to, subject, body)

    def notify_staff_vip_arrival(
        self,
        staff_emails: List[str],
        guest_name: str,
        room_number: str,
        check_in_date: str,
        special_requests: Optional[str] = None,
    ) -> int:
        """Notify staff about VIP arrival."""
        subject = f"VIP Arrival Alert - {guest_name}"

        body = f"""
VIP ARRIVAL ALERT

Guest: {guest_name}
Room: {room_number}
Check-in Date: {check_in_date}

{"Special Requests: " + special_requests if special_requests else "No special requests."}

Please ensure all arrangements are in place.
"""

        sent_count = 0
        for email in staff_emails:
            if self.send_email(email, subject, body):
                sent_count += 1

        return sent_count

    def notify_maintenance_required(
        self,
        staff_emails: List[str],
        room_number: str,
        issue: str,
        priority: str = "normal",
    ) -> int:
        """Notify maintenance staff about room issues."""
        subject = f"Maintenance Required - Room {room_number} [{priority.upper()}]"

        body = f"""
MAINTENANCE REQUEST

Room: {room_number}
Priority: {priority.upper()}
Issue: {issue}
Reported: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please attend to this as soon as possible.
"""

        sent_count = 0
        for email in staff_emails:
            if self.send_email(email, subject, body):
                sent_count += 1

        return sent_count
