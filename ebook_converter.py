import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EbookConverter:
    """Service for converting ebook formats for Kindle compatibility"""
    
    def __init__(self):
        self.temp_dir = None
        self.calibre_available = self._check_calibre_availability()
        
    def _check_calibre_availability(self) -> bool:
        """Check if Calibre's ebook-convert command is available"""
        try:
            result = subprocess.run(['ebook-convert', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _create_temp_dir(self) -> str:
        """Create a temporary directory for conversion operations"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix='ebook_conversion_')
        return self.temp_dir
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            except OSError as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def _get_temp_filename(self, original_path: str, extension: str) -> str:
        """Generate a temporary filename with the given extension"""
        temp_dir = self._create_temp_dir()
        original_name = Path(original_path).stem
        return os.path.join(temp_dir, f"{original_name}_converted{extension}")
    
    def _calibre_convert(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Convert using Calibre's ebook-convert command"""
        try:
            cmd = ['ebook-convert', input_path, output_path]
            
            # Add some optimization flags for better conversion
            input_ext = Path(input_path).suffix.lower()
            output_ext = Path(output_path).suffix.lower()
            
            # Optimize for EPUB to MOBI conversion
            if input_ext == '.epub' and output_ext == '.mobi':
                cmd.extend([
                    '--output-profile', 'kindle',
                    '--mobi-file-type', 'new'  # Use newer MOBI format
                ])
            
            # Optimize for MOBI to EPUB conversion
            elif input_ext == '.mobi' and output_ext == '.epub':
                cmd.extend([
                    '--output-profile', 'tablet',
                    '--epub-version', '2'  # Use EPUB 2 for better compatibility
                ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return True, "Conversion successful"
            else:
                error_msg = result.stderr or result.stdout or "Unknown conversion error"
                return False, f"Calibre conversion failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Conversion timed out (5 minutes)"
        except Exception as e:
            return False, f"Calibre conversion error: {str(e)}"
    
    def _fallback_copy(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Fallback: simply copy the file if conversion is not possible"""
        try:
            shutil.copy2(input_path, output_path)
            return True, "File copied (no conversion performed)"
        except Exception as e:
            return False, f"Failed to copy file: {str(e)}"
    
    def convert_for_kindle_compatibility(self, file_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Convert ebook for Kindle compatibility using the required conversion chain.
        
        Args:
            file_path: Path to the original ebook file
            
        Returns:
            Tuple of (success, message, converted_file_path)
            - success: True if conversion was successful
            - message: Description of what happened
            - converted_file_path: Path to the converted file (or None if failed)
        """
        if not os.path.exists(file_path):
            return False, "Input file does not exist", None
        
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.epub':
                # EPUB → MOBI → EPUB conversion chain
                return self._epub_to_mobi_to_epub_chain(file_path)
            elif file_ext in ['.mobi', '.azw', '.azw3']:
                # MOBI → EPUB conversion
                return self._mobi_to_epub_conversion(file_path)
            else:
                # For other formats, just copy without conversion
                temp_file = self._get_temp_filename(file_path, file_ext)
                success, message = self._fallback_copy(file_path, temp_file)
                return success, f"Unsupported format for conversion: {message}", temp_file if success else None
                
        except Exception as e:
            logger.error(f"Conversion error for {file_path}: {e}")
            return False, f"Conversion failed: {str(e)}", None
    
    def _epub_to_mobi_to_epub_chain(self, epub_path: str) -> Tuple[bool, str, Optional[str]]:
        """Convert EPUB → MOBI → EPUB for Kindle compatibility"""
        try:
            # Step 1: EPUB → MOBI
            temp_mobi = self._get_temp_filename(epub_path, '.mobi')
            success, message = self._calibre_convert(epub_path, temp_mobi)
            
            if not success:
                return False, f"EPUB→MOBI conversion failed: {message}", None
            
            # Step 2: MOBI → EPUB
            final_epub = self._get_temp_filename(epub_path, '_final.epub')
            success, message = self._calibre_convert(temp_mobi, final_epub)
            
            if not success:
                return False, f"MOBI→EPUB conversion failed: {message}", None
            
            return True, "Successfully converted EPUB→MOBI→EPUB for Kindle compatibility", final_epub
            
        except Exception as e:
            return False, f"Conversion chain error: {str(e)}", None
    
    def _mobi_to_epub_conversion(self, mobi_path: str) -> Tuple[bool, str, Optional[str]]:
        """Convert MOBI/AZW → EPUB"""
        try:
            output_epub = self._get_temp_filename(mobi_path, '.epub')
            success, message = self._calibre_convert(mobi_path, output_epub)
            
            if success:
                return True, "Successfully converted MOBI→EPUB for Kindle compatibility", output_epub
            else:
                return False, message, None
                
        except Exception as e:
            return False, f"MOBI conversion error: {str(e)}", None
    
    def cleanup(self):
        """Clean up any temporary files"""
        self._cleanup_temp_dir()
    
    def get_conversion_info(self) -> dict:
        """Get information about available conversion methods"""
        return {
            'calibre_available': self.calibre_available,
            'supported_conversions': {
                'epub_to_mobi_to_epub': self.calibre_available,
                'mobi_to_epub': self.calibre_available,
                'fallback_copy': True
            },
            'temp_dir': self.temp_dir
        }

# Global instance
ebook_converter = EbookConverter() 