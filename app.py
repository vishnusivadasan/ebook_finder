from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import time
from pathlib import Path
from typing import List, Optional
from ebook_search import EbookSearcher
import json

app = FastAPI(title="Ebook Search System", description="A lightweight ebook search system")

# Setup templates (static directory created in Dockerfile)
templates = Jinja2Templates(directory="templates")

# Mount static files (directory already exists from Dockerfile)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize searcher with catalog
searcher = EbookSearcher()

# Global state for directories (in production, use Redis/database)
search_directories = searcher.get_common_ebook_directories()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page with search interface"""
    valid_dirs = [d for d in search_directories if os.path.exists(d)]
    invalid_dirs = [d for d in search_directories if not os.path.exists(d)]
    
    # Get catalog metadata
    catalog_metadata = searcher.get_catalog_metadata()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "valid_dirs": valid_dirs,
        "invalid_dirs": invalid_dirs,
        "total_dirs": len(search_directories),
        "catalog_metadata": catalog_metadata
    })

@app.post("/search")
async def search_books(
    query: str = Form("")
):
    """Search for ebooks using catalog"""
    search_start_time = time.time()
    
    try:
        # Get all books from catalog (force_refresh=False to use existing catalog)
        all_books = searcher.get_catalog_books(force_refresh=False)
        
        if not all_books:
            return JSONResponse({
                "success": False,
                "message": "No ebook files found in catalog. Try refreshing the catalog.",
                "results": [],
                "search_time_ms": 0
            })
        
        # Search for matching books (no file type filtering here - done on client)
        if query.strip():
            results = searcher.search_books(query, all_books)
        else:
            results = [(book, 100) for book in all_books]
        
        # Format results for JSON response
        formatted_results = []
        for book, score in results:
            formatted_results.append({
                "filename": book["filename"],
                "directory": book["directory"],
                "full_path": book["full_path"],
                "size_mb": book["size_mb"],
                "extension": book["extension"],
                "score": score
            })
        
        # Calculate search time
        search_time_ms = round((time.time() - search_start_time) * 1000, 1)
        
        # Get current stats
        stats = searcher.get_catalog_stats()
        stats["results_count"] = len(formatted_results)
        stats["search_time_ms"] = search_time_ms
        
        return JSONResponse({
            "success": True,
            "results": formatted_results,
            "stats": stats,
            "search_time_ms": search_time_ms
        })
        
    except Exception as e:
        search_time_ms = round((time.time() - search_start_time) * 1000, 1)
        return JSONResponse({
            "success": False,
            "message": f"Search error: {str(e)}",
            "results": [],
            "search_time_ms": search_time_ms
        })

@app.post("/catalog/build")
async def build_catalog(force_refresh: bool = Form(False)):
    """Build or refresh the ebook catalog"""
    try:
        valid_search_directories = [d for d in search_directories if os.path.exists(d)]
        
        if not valid_search_directories:
            return JSONResponse({
                "success": False,
                "message": "No valid search directories configured"
            })
        
        catalog = searcher.build_catalog(valid_search_directories, force_refresh=force_refresh)
        
        return JSONResponse({
            "success": True,
            "message": f"Catalog built successfully with {catalog['metadata']['total_books']} books",
            "metadata": catalog['metadata'],
            "stats": catalog['stats']
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Failed to build catalog: {str(e)}"
        })

@app.post("/catalog/deduplicate")
async def deduplicate_catalog_endpoint():
    """Remove duplicate entries from the existing catalog"""
    try:
        catalog = searcher.deduplicate_catalog()
        
        return JSONResponse({
            "success": True,
            "message": f"Catalog deduplicated successfully, now contains {catalog['metadata']['total_books']} unique books",
            "metadata": catalog['metadata'],
            "stats": catalog['stats']
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Failed to deduplicate catalog: {str(e)}"
        })

@app.get("/catalog/metadata")
async def get_catalog_metadata():
    """Get catalog metadata"""
    try:
        metadata = searcher.get_catalog_metadata()
        return JSONResponse({
            "success": True,
            "metadata": metadata
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Failed to get catalog metadata: {str(e)}"
        })

@app.get("/catalog/stats")
async def get_catalog_stats():
    """Get catalog statistics"""
    try:
        stats = searcher.get_catalog_stats()
        return JSONResponse({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Failed to get catalog stats: {str(e)}"
        })

@app.get("/catalog/file-types")
async def get_file_types():
    """Get available file types from catalog"""
    try:
        stats = searcher.get_catalog_stats()
        file_types = stats.get('file_types', {})
        
        return JSONResponse({
            "success": True,
            "file_types": file_types
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Failed to get file types: {str(e)}"
        })

@app.get("/directories")
async def get_directories():
    """Get current search directories"""
    valid_dirs = [d for d in search_directories if os.path.exists(d)]
    invalid_dirs = [d for d in search_directories if not os.path.exists(d)]
    
    return JSONResponse({
        "valid_dirs": valid_dirs,
        "invalid_dirs": invalid_dirs,
        "total": len(search_directories)
    })

@app.post("/directories/add")
async def add_directory(directory: str = Form(...)):
    """Add a new search directory"""
    global search_directories
    
    if not directory.strip():
        raise HTTPException(status_code=400, detail="Directory path cannot be empty")
    
    if directory in search_directories:
        raise HTTPException(status_code=400, detail="Directory already exists")
    
    if not os.path.exists(directory):
        raise HTTPException(status_code=400, detail="Directory does not exist")
    
    search_directories.append(directory)
    
    return JSONResponse({
        "success": True,
        "message": "Directory added successfully",
        "directory": directory
    })

@app.post("/directories/remove")
async def remove_directory(directory: str = Form(...)):
    """Remove a search directory"""
    global search_directories
    
    if directory not in search_directories:
        raise HTTPException(status_code=400, detail="Directory not found")
    
    search_directories.remove(directory)
    
    return JSONResponse({
        "success": True,
        "message": "Directory removed successfully",
        "directory": directory
    })

@app.post("/directories/reset")
async def reset_directories():
    """Reset to default directories"""
    global search_directories
    search_directories = searcher.get_common_ebook_directories()
    
    return JSONResponse({
        "success": True,
        "message": "Directories reset to defaults",
        "directories": search_directories
    })

@app.post("/directories/clear")
async def clear_directories():
    """Clear all directories"""
    global search_directories
    search_directories = []
    
    return JSONResponse({
        "success": True,
        "message": "All directories cleared",
        "directories": []
    })

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501) 