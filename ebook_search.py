import os
import glob
from pathlib import Path
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
import re

class EbookSearcher:
    def __init__(self):
        self.supported_formats = ['.pdf', '.epub', '.mobi', '.azw', '.azw3', '.djvu', '.fb2', '.txt']
        
    def get_common_ebook_directories(self) -> List[str]:
        """Get common directories where ebooks might be stored"""
        home = Path.home()
        common_dirs = []
        
        # Check if we're running in a container (mounted volumes)
        container_dirs = [
            "/mnt/documents",
            "/mnt/downloads", 
            "/mnt/books",
            "/mnt/desktop",
            "/mnt/ebooks",
            "/mnt/calibre",
            "/mnt/kindle"  # Add the mounted Kindle directory
        ]
        
        # Add container mount points if they exist
        for container_dir in container_dirs:
            if os.path.exists(container_dir):
                common_dirs.append(container_dir)
        
        # Add traditional local directories
        local_dirs = [
            str(home / "Documents"),
            str(home / "Downloads"), 
            str(home / "Books"),
            str(home / "Desktop"),
            str(home / "Library" / "Application Support" / "Kindle"),
            "/Applications/Kindle.app/Contents/Resources",
            str(home / "Calibre Library"),
            "/Users/vishnusivadasan/smbshare/Books/Kindle"  # Add the new Kindle books directory
        ]
        
        common_dirs.extend(local_dirs)
        
        # Add current directory and subdirectories
        current_dir = Path.cwd()
        common_dirs.extend([
            str(current_dir),
            str(current_dir / "books"),
            str(current_dir / "ebooks"),
        ])
        
        # Filter to only existing directories
        return [d for d in common_dirs if os.path.exists(d)]
    
    def find_ebook_files(self, search_directories: List[str] = None) -> List[Dict[str, str]]:
        """Find all ebook files in specified directories"""
        if search_directories is None:
            search_directories = self.get_common_ebook_directories()
        
        ebook_files = []
        
        for directory in search_directories:
            try:
                for ext in self.supported_formats:
                    # Search recursively for files with ebook extensions
                    pattern = os.path.join(directory, '**', f'*{ext}')
                    files = glob.glob(pattern, recursive=True)
                    
                    for file_path in files:
                        file_info = {
                            'filename': os.path.basename(file_path),
                            'full_path': file_path,
                            'directory': os.path.dirname(file_path),
                            'extension': ext,
                            'size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2)
                        }
                        ebook_files.append(file_info)
            except (PermissionError, OSError) as e:
                # Skip directories we can't access
                continue
                
        return ebook_files
    
    def search_books(self, query: str, ebook_files: List[Dict[str, str]], 
                    similarity_threshold: int = 60) -> List[Tuple[Dict[str, str], int]]:
        """Search for books matching the query"""
        if not query.strip():
            return [(book, 100) for book in ebook_files]
        
        results = []
        query_lower = query.lower()
        
        for book in ebook_files:
            filename_no_ext = os.path.splitext(book['filename'])[0].lower()
            
            # Calculate similarity scores
            exact_match = query_lower in filename_no_ext
            fuzzy_score = fuzz.partial_ratio(query_lower, filename_no_ext)
            token_score = fuzz.token_sort_ratio(query_lower, filename_no_ext)
            
            # Use the highest score
            best_score = max(fuzzy_score, token_score)
            
            # Boost score for exact matches
            if exact_match:
                best_score = min(100, best_score + 20)
            
            # Only include results above threshold
            if best_score >= similarity_threshold:
                results.append((book, best_score))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_file_metadata(self, file_path: str) -> Dict[str, str]:
        """Extract basic metadata from file"""
        try:
            stat = os.stat(file_path)
            return {
                'size': f"{stat.st_size / (1024*1024):.2f} MB",
                'modified': str(stat.st_mtime),
                'created': str(stat.st_ctime)
            }
        except:
            return {} 