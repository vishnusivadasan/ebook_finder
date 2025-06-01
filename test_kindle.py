#!/usr/bin/env python3
"""
Test script for Kindle email functionality
"""

import requests
import json
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8501"
TEST_FILE_PATH = "/Users/vishnusivadasan/Documents/Devrepos/kindle_web/dummy_books/test.pdf"  # You'll need to create this

def test_kindle_info():
    """Test getting Kindle configuration info"""
    print("Testing Kindle info endpoint...")
    response = requests.get(f"{BASE_URL}/kindle/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_file_validation():
    """Test file validation for Kindle"""
    print("Testing file validation...")
    
    # Test with a valid file path (even if file doesn't exist)
    data = {"file_path": TEST_FILE_PATH}
    response = requests.post(f"{BASE_URL}/kindle/validate", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_set_password():
    """Test setting Gmail app password"""
    print("Testing password setting...")
    
    # Test with invalid password length
    data = {"app_password": "short"}
    response = requests.post(f"{BASE_URL}/kindle/set-password", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test with valid password format (dummy password)
    data = {"app_password": "abcd1234efgh5678"}
    response = requests.post(f"{BASE_URL}/kindle/set-password", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_send_to_kindle():
    """Test sending file to Kindle (will fail without real credentials)"""
    print("Testing send to Kindle...")
    
    data = {"file_path": TEST_FILE_PATH}
    response = requests.post(f"{BASE_URL}/kindle/send", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("Testing Kindle Email Functionality")
    print("=" * 40)
    
    try:
        test_kindle_info()
        test_file_validation()
        test_set_password()
        test_send_to_kindle()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the application. Make sure it's running on http://localhost:8501")
    except Exception as e:
        print(f"Error: {e}") 