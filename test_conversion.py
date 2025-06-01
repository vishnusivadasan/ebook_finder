#!/usr/bin/env python3
"""
Test script for ebook conversion functionality
"""

import os
import sys
from pathlib import Path
from ebook_converter import ebook_converter

def test_conversion_info():
    """Test getting conversion information"""
    print("=== Testing Conversion Info ===")
    info = ebook_converter.get_conversion_info()
    print(f"Calibre available: {info['calibre_available']}")
    print(f"Supported conversions: {info['supported_conversions']}")
    print(f"Temp directory: {info['temp_dir']}")
    print()

def test_conversion_with_sample_file():
    """Test conversion with a sample file (if available)"""
    print("=== Testing Conversion Process ===")
    
    # Look for any epub or mobi files in common directories
    test_dirs = [
        ".",
        str(Path.home() / "Documents"),
        str(Path.home() / "Downloads"),
        "/mnt/books",
        "/mnt/documents"
    ]
    
    test_file = None
    
    for directory in test_dirs:
        if not os.path.exists(directory):
            continue
            
        for ext in ['.epub', '.mobi']:
            pattern = f"**/*{ext}"
            import glob
            files = glob.glob(os.path.join(directory, pattern), recursive=True)
            if files:
                test_file = files[0]
                break
        
        if test_file:
            break
    
    if test_file:
        print(f"Found test file: {test_file}")
        
        # Test conversion
        success, message, converted_file = ebook_converter.convert_for_kindle_compatibility(test_file)
        
        print(f"Conversion success: {success}")
        print(f"Conversion message: {message}")
        if converted_file:
            print(f"Converted file: {converted_file}")
            print(f"Converted file exists: {os.path.exists(converted_file)}")
            if os.path.exists(converted_file):
                size_mb = os.path.getsize(converted_file) / (1024 * 1024)
                print(f"Converted file size: {size_mb:.2f} MB")
        
        # Cleanup
        ebook_converter.cleanup()
        print("Cleanup completed")
    else:
        print("No test files found. Please place an .epub or .mobi file in one of these directories:")
        for d in test_dirs:
            if os.path.exists(d):
                print(f"  - {d}")
    
    print()

def test_calibre_detection():
    """Test Calibre detection"""
    print("=== Testing Calibre Detection ===")
    
    # Try to run ebook-convert command
    import subprocess
    try:
        result = subprocess.run(['ebook-convert', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Calibre ebook-convert is available")
            print(f"Version info: {result.stdout.strip()}")
        else:
            print("✗ Calibre ebook-convert command failed")
            print(f"Error: {result.stderr}")
    except subprocess.SubprocessError as e:
        print(f"✗ Calibre subprocess error: {e}")
    except FileNotFoundError:
        print("✗ Calibre ebook-convert command not found")
        print("\nTo install Calibre:")
        print("  macOS: brew install calibre")
        print("  Ubuntu/Debian: sudo apt-get install calibre")
        print("  Or download from: https://calibre-ebook.com/download")
    
    print()

if __name__ == "__main__":
    print("Ebook Conversion Test Script")
    print("="*40)
    
    test_calibre_detection()
    test_conversion_info()
    test_conversion_with_sample_file()
    
    print("Test completed!") 