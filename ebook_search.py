import os
import glob
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
import re

class EbookSearcher:
    def __init__(self, catalog_file: str = "ebook_catalog.json", fast_search_mode: bool = False):
        self.supported_formats = ['.pdf', '.epub', '.mobi', '.azw', '.azw3', '.djvu', '.fb2', '.txt']
        self.catalog_file = catalog_file
        self.catalog_max_age_days = 7  # Refresh catalog if older than 7 days
        self.daily_refresh_hour = 3    # Auto-refresh at 3 AM if container running
        self.fast_search_mode = fast_search_mode  # Enable fast search for Raspberry Pi
        
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
    
    def search_books_fast(self, query: str, ebook_files: List[Dict[str, str]]) -> List[Tuple[Dict[str, str], int]]:
        """Fast search using simple string matching - optimized for Raspberry Pi"""
        if not query.strip():
            return [(book, 100) for book in ebook_files]
        
        results = []
        query_terms = query.lower().split()  # Split query into words
        
        for book in ebook_files:
            filename_no_ext = os.path.splitext(book['filename'])[0].lower()
            
            # Simple scoring based on word matches
            score = 0
            
            # Check for exact phrase match (highest score)
            if query.lower() in filename_no_ext:
                score = 100
            else:
                # Count matching words
                matching_words = 0
                for term in query_terms:
                    if term in filename_no_ext:
                        matching_words += 1
                
                # Score based on percentage of words found
                if matching_words > 0:
                    score = int((matching_words / len(query_terms)) * 90)
                    
                    # Bonus for word starts (e.g., "har" matches "harry")
                    for term in query_terms:
                        if any(word.startswith(term) for word in filename_no_ext.split()):
                            score += 5
                    
                    score = min(100, score)
            
            # Only include results with some relevance
            if score > 0:
                results.append((book, score))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def search_books(self, query: str, ebook_files: List[Dict[str, str]], 
                    similarity_threshold: int = 60) -> List[Tuple[Dict[str, str], int]]:
        """Search for books matching the query"""
        # Use fast search mode if enabled
        if self.fast_search_mode:
            return self.search_books_fast(query, ebook_files)
            
        # Original fuzzy search (slower but more accurate)
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
    
    def _should_refresh_catalog(self) -> bool:
        """Check if catalog needs to be refreshed"""
        if not os.path.exists(self.catalog_file):
            return True
            
        try:
            with open(self.catalog_file, 'r') as f:
                catalog = json.load(f)
            
            last_refresh = catalog.get('metadata', {}).get('last_refresh', 0)
            last_refresh_date = datetime.fromtimestamp(last_refresh)
            
            # Check if catalog is older than max age
            if datetime.now() - last_refresh_date > timedelta(days=self.catalog_max_age_days):
                return True
                
            # Check if it's time for daily refresh (if container has been running long enough)
            now = datetime.now()
            if (now.hour == self.daily_refresh_hour and 
                now - last_refresh_date > timedelta(hours=23)):  # At least 23 hours since last refresh
                return True
                
            return False
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            return True
    
    def build_catalog(self, search_directories: List[str] = None, force_refresh: bool = False) -> Dict:
        """Build or refresh the ebook catalog"""
        if not force_refresh and not self._should_refresh_catalog():
            return self.load_catalog()
            
        if search_directories is None:
            search_directories = self.get_common_ebook_directories()
        
        print(f"Building catalog from {len(search_directories)} directories...")
        start_time = time.time()
        
        # Find all ebook files
        all_books = self.find_ebook_files(search_directories)
        
        # Build catalog structure
        catalog = {
            'metadata': {
                'last_refresh': time.time(),
                'refresh_date': datetime.now().isoformat(),
                'total_books': len(all_books),
                'search_directories': search_directories,
                'build_time_seconds': 0
            },
            'books': all_books,
            'stats': self._calculate_stats(all_books)
        }
        
        build_time = time.time() - start_time
        catalog['metadata']['build_time_seconds'] = round(build_time, 2)
        
        # Save catalog
        try:
            with open(self.catalog_file, 'w') as f:
                json.dump(catalog, f, indent=2)
            print(f"Catalog built successfully in {build_time:.2f}s with {len(all_books)} books")
        except OSError as e:
            print(f"Warning: Could not save catalog to {self.catalog_file}: {e}")
        
        return catalog
    
    def load_catalog(self) -> Dict:
        """Load existing catalog or build new one if not found"""
        if os.path.exists(self.catalog_file):
            try:
                with open(self.catalog_file, 'r') as f:
                    catalog = json.load(f)
                    
                # Validate catalog structure
                if 'books' in catalog and 'metadata' in catalog:
                    return catalog
            except (json.JSONDecodeError, OSError):
                pass
        
        # Build new catalog if loading failed
        return self.build_catalog()
    
    def get_catalog_books(self, force_refresh: bool = False) -> List[Dict[str, str]]:
        """Get all books from catalog"""
        if force_refresh or self._should_refresh_catalog():
            catalog = self.build_catalog(force_refresh=force_refresh)
        else:
            catalog = self.load_catalog()
        
        return catalog.get('books', [])
    
    def get_catalog_stats(self) -> Dict:
        """Get catalog statistics"""
        catalog = self.load_catalog()
        return catalog.get('stats', {})
    
    def get_catalog_metadata(self) -> Dict:
        """Get catalog metadata"""
        catalog = self.load_catalog()
        return catalog.get('metadata', {})
    
    def _calculate_stats(self, books: List[Dict[str, str]]) -> Dict:
        """Calculate statistics for the book collection"""
        if not books:
            return {}
            
        total_size = sum(book.get("size_mb", 0) for book in books)
        extensions = {}
        directories = set()
        
        for book in books:
            ext = book.get("extension", "").lower()
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
            if book.get("directory"):
                directories.add(book["directory"])
        
        return {
            "total_books": len(books),
            "total_size_mb": round(total_size, 1),
            "total_size_gb": round(total_size / 1024, 2),
            "file_types": extensions,
            "unique_directories": len(directories),
            "largest_book": max(books, key=lambda x: x.get("size_mb", 0)) if books else None,
            "average_size_mb": round(total_size / len(books), 2) if books else 0
        } 