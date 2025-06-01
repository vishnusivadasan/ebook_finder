from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
from typing import List, Optional
from ebook_search import EbookSearcher
import json

app = FastAPI(title="Ebook Search System", description="A lightweight ebook search system")

# Setup templates (static directory created in Dockerfile)
templates = Jinja2Templates(directory="templates")

# Mount static files (directory already exists from Dockerfile)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize searcher
searcher = EbookSearcher()

# Global state for directories (in production, use Redis/database)
search_directories = searcher.get_common_ebook_directories()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page with search interface"""
    valid_dirs = [d for d in search_directories if os.path.exists(d)]
    invalid_dirs = [d for d in search_directories if not os.path.exists(d)]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "valid_dirs": valid_dirs,
        "invalid_dirs": invalid_dirs,
        "total_dirs": len(search_directories)
    })

@app.post("/search")
async def search_books(
    query: str = Form(""),
    similarity_threshold: int = Form(60)
):
    """Search for ebooks"""
    try:
        # Get valid directories
        valid_search_directories = [d for d in search_directories if os.path.exists(d)]
        
        if not valid_search_directories:
            return JSONResponse({
                "success": False,
                "message": "No valid search directories configured",
                "results": []
            })
        
        # Find all ebook files
        all_books = searcher.find_ebook_files(valid_search_directories)
        
        if not all_books:
            return JSONResponse({
                "success": False,
                "message": "No ebook files found in the specified directories",
                "results": []
            })
        
        # Search for matching books
        if query.strip():
            results = searcher.search_books(query, all_books, similarity_threshold)
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
        
        # Calculate statistics
        total_size = sum(book["size_mb"] for book in all_books)
        extensions = set(book["extension"] for book in all_books)
        directories = set(book["directory"] for book in all_books)
        
        return JSONResponse({
            "success": True,
            "results": formatted_results,
            "stats": {
                "total_books": len(all_books),
                "total_size_mb": round(total_size, 1),
                "file_types": len(extensions),
                "directories": len(directories),
                "results_count": len(formatted_results)
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Search error: {str(e)}",
            "results": []
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