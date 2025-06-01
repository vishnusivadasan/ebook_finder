import smtplib
import os
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional
import logging
from conf import email_config

logger = logging.getLogger(__name__)

class KindleEmailSender:
    """Service for sending ebooks to Kindle via email"""
    
    def __init__(self):
        # Use configuration from conf.py
        self.gmail_address = email_config.gmail_address
        self.kindle_email = email_config.kindle_email
        self.smtp_server = email_config.smtp_server
        self.smtp_port = email_config.smtp_port
        self.max_attachment_size_mb = email_config.max_attachment_size_mb
        self.supported_formats = email_config.supported_formats
        self.gmail_app_password = None  # Will be set from environment or user input
    
    def set_gmail_app_password(self, app_password: str):
        """Set the Gmail app password for authentication"""
        self.gmail_app_password = app_password
    
    def get_gmail_app_password_from_env(self) -> Optional[str]:
        """Try to get Gmail app password from environment variable"""
        return email_config.gmail_app_password
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if the file format is supported by Kindle"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats
    
    def get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)
        except OSError:
            return 0.0
    
    def validate_file_for_kindle(self, file_path: str) -> dict:
        """Validate if file can be sent to Kindle"""
        result = {
            'valid': False,
            'reason': '',
            'file_size_mb': 0.0
        }
        
        if not os.path.exists(file_path):
            result['reason'] = 'File does not exist'
            return result
        
        if not self.is_supported_format(file_path):
            file_ext = Path(file_path).suffix.lower()
            result['reason'] = f'Unsupported format: {file_ext}. Supported formats: {", ".join(self.supported_formats)}'
            return result
        
        file_size_mb = self.get_file_size_mb(file_path)
        result['file_size_mb'] = file_size_mb
        
        # Use configured size limit instead of hardcoded 50MB
        if file_size_mb > self.max_attachment_size_mb:
            result['reason'] = f'File too large: {file_size_mb}MB. Kindle email limit is {self.max_attachment_size_mb}MB'
            return result
        
        result['valid'] = True
        result['reason'] = 'File is valid for Kindle'
        return result
    
    def send_book_to_kindle(self, file_path: str, custom_subject: str = None) -> dict:
        """Send a book file to Kindle via email"""
        result = {
            'success': False,
            'message': '',
            'file_path': file_path
        }
        
        # Validate file first
        validation = self.validate_file_for_kindle(file_path)
        if not validation['valid']:
            result['message'] = validation['reason']
            return result
        
        # Check if we have Gmail app password
        app_password = self.gmail_app_password or self.get_gmail_app_password_from_env()
        if not app_password:
            result['message'] = 'Gmail app password not configured. Please set GMAIL_APP_PASSWORD environment variable or provide it via API.'
            return result
        
        try:
            # Prepare email
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = self.kindle_email
            
            # Set subject
            filename = Path(file_path).name
            if custom_subject:
                msg['Subject'] = custom_subject
            else:
                msg['Subject'] = f'Book: {filename}'
            
            # Email body
            body = f"""
This book was sent automatically from your Ebook Search System.

Book: {filename}
Size: {validation['file_size_mb']} MB

Enjoy reading!
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach the book file
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
            
            # Send email using configured SMTP settings
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.gmail_address, app_password)
            
            text = msg.as_string()
            server.sendmail(self.gmail_address, self.kindle_email, text)
            server.quit()
            
            result['success'] = True
            result['message'] = f'Successfully sent "{filename}" to Kindle ({self.kindle_email})'
            logger.info(f"Successfully sent {filename} to Kindle")
            
        except Exception as e:
            error_msg = f'Failed to send email: {str(e)}'
            result['message'] = error_msg
            logger.error(f"Failed to send {filename} to Kindle: {e}")
        
        return result
    
    def get_kindle_info(self) -> dict:
        """Get current Kindle email configuration"""
        return {
            'gmail_address': self.gmail_address,
            'kindle_email': self.kindle_email,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'max_attachment_size_mb': self.max_attachment_size_mb,
            'app_password_configured': bool(self.gmail_app_password or self.get_gmail_app_password_from_env()),
            'supported_formats': list(self.supported_formats)
        }

# Global instance
kindle_sender = KindleEmailSender() 