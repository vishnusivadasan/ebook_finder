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
from ebook_converter import ebook_converter

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
        """Send a book file to Kindle via email with format conversion for compatibility"""
        result = {
            'success': False,
            'message': '',
            'file_path': file_path,
            'conversion_performed': False,
            'conversion_message': ''
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
        
        # Perform conversion for Kindle compatibility
        file_to_send = file_path
        original_filename = Path(file_path).name
        
        try:
            # Apply Kindle compatibility conversion
            conversion_success, conversion_message, converted_file_path = ebook_converter.convert_for_kindle_compatibility(file_path)
            
            if conversion_success and converted_file_path:
                file_to_send = converted_file_path
                result['conversion_performed'] = True
                result['conversion_message'] = conversion_message
                logger.info(f"Conversion successful for {original_filename}: {conversion_message}")
            else:
                # If conversion fails, still try to send the original file
                result['conversion_performed'] = False
                result['conversion_message'] = f"Conversion failed: {conversion_message}. Sending original file."
                logger.warning(f"Conversion failed for {original_filename}: {conversion_message}")
            
            # Re-validate the file to send (in case conversion changed the size)
            final_validation = self.validate_file_for_kindle(file_to_send)
            if not final_validation['valid']:
                result['message'] = f"Converted file validation failed: {final_validation['reason']}"
                return result
            
            # Prepare email
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = self.kindle_email
            
            # Set subject
            if custom_subject:
                msg['Subject'] = custom_subject
            else:
                msg['Subject'] = f'Book: {original_filename}'
            
            # Email body with conversion info
            conversion_info = f"\nConversion: {result['conversion_message']}" if result['conversion_performed'] else "\nNo conversion performed."
            
            body = f"""
This book was sent automatically from your Ebook Search System.

Original Book: {original_filename}
Final Size: {final_validation['file_size_mb']} MB{conversion_info}

Enjoy reading!
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach the book file (original or converted)
            with open(file_to_send, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            # Always use original filename for attachment
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {original_filename}'
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
            success_msg = f'Successfully sent "{original_filename}" to Kindle ({self.kindle_email})'
            if result['conversion_performed']:
                success_msg += f' with conversion: {result["conversion_message"]}'
            result['message'] = success_msg
            logger.info(f"Successfully sent {original_filename} to Kindle")
            
        except Exception as e:
            error_msg = f'Failed to send email: {str(e)}'
            result['message'] = error_msg
            logger.error(f"Failed to send {original_filename} to Kindle: {e}")
        finally:
            # Clean up any temporary conversion files
            try:
                ebook_converter.cleanup()
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup conversion files: {cleanup_error}")
        
        return result
    
    def get_kindle_info(self) -> dict:
        """Get current Kindle email configuration"""
        converter_info = ebook_converter.get_conversion_info()
        
        return {
            'gmail_address': self.gmail_address,
            'kindle_email': self.kindle_email,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'max_attachment_size_mb': self.max_attachment_size_mb,
            'app_password_configured': bool(self.gmail_app_password or self.get_gmail_app_password_from_env()),
            'supported_formats': list(self.supported_formats),
            'conversion_info': converter_info
        }

# Global instance
kindle_sender = KindleEmailSender() 