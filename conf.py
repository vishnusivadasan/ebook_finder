"""
Configuration file for Kindle Web Application

This file centralizes all configuration settings for email and Kindle functionality.
Environment variables can be used to override default values via a .env file.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class EmailConfig:
    """Email configuration settings"""
    
    def __init__(self):
        # Gmail configuration
        self.gmail_address: str = os.getenv('GMAIL_ADDRESS', 'mysterious.18.vishnu@gmail.com')
        self.gmail_app_password: Optional[str] = os.getenv('GMAIL_APP_PASSWORD')
        
        # Kindle configuration  
        self.kindle_email: str = os.getenv('KINDLE_EMAIL', 'auoasismit987@kindle.com')
        
        # SMTP configuration
        self.smtp_server: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
        
        # Email limits and validation
        self.max_attachment_size_mb: int = int(os.getenv('MAX_ATTACHMENT_SIZE_MB', '50'))
        
        # Supported file formats for Kindle
        self.supported_formats: set = {'.pdf', '.mobi', '.epub', '.azw', '.azw3', '.txt', '.doc', '.docx'}
    
    def is_gmail_configured(self) -> bool:
        """Check if Gmail is properly configured"""
        return bool(self.gmail_address and self.gmail_app_password)
    
    def is_kindle_configured(self) -> bool:
        """Check if Kindle email is configured"""
        return bool(self.kindle_email)
    
    def is_fully_configured(self) -> bool:
        """Check if all email configuration is complete"""
        return self.is_gmail_configured() and self.is_kindle_configured()
    
    def get_config_summary(self) -> dict:
        """Get a summary of current configuration (without sensitive data)"""
        return {
            'gmail_address': self.gmail_address,
            'kindle_email': self.kindle_email,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'max_attachment_size_mb': self.max_attachment_size_mb,
            'gmail_configured': self.is_gmail_configured(),
            'kindle_configured': self.is_kindle_configured(),
            'fully_configured': self.is_fully_configured(),
            'supported_formats': sorted(list(self.supported_formats))
        }


# Global configuration instance
email_config = EmailConfig() 