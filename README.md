# 📚 Ebook Search System

A lightweight, web-based ebook search system that helps you find and organize your digital book collection. Built with FastAPI for optimal performance and minimal resource usage.

## Features

- 🔍 **Smart Search**: Fuzzy search with partial matching for book titles and filenames
- 📁 **Multi-Directory Support**: Searches common ebook locations automatically
- 🎯 **Configurable Similarity**: Adjustable search sensitivity
- 📊 **File Statistics**: View your collection metrics
- 🖥️ **Cross-Platform**: Works on macOS, Windows, and Linux
- 📂 **Quick Access**: Open file locations directly from the interface
- 🐳 **Docker Ready**: Optimized deployment with minimal footprint
- ⚡ **High Performance**: FastAPI backend for speed and efficiency

## Supported Formats

- PDF (.pdf)
- EPUB (.epub)
- MOBI (.mobi)
- Kindle (.azw, .azw3)
- DjVu (.djvu)
- FictionBook (.fb2)
- Plain Text (.txt)

## How to Run

### 🎯 Method 1: Docker Compose (Easiest)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd kindle_web
   ```

2. **Start the application:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Open your browser and go to `http://localhost:8501`

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

### 🐳 Method 2: Docker Run (Custom Setup)

1. **Build the Docker image:**
   ```bash
   docker build -t ebook-search .
   ```

2. **Run the container with your ebook directories:**
   ```bash
   # macOS/Linux
   docker run -d \
     --name ebook-search \
     -p 8501:8501 \
     -v "$HOME/Documents:/mnt/documents:ro" \
     -v "$HOME/Books:/mnt/books:ro" \
     -v "$HOME/Downloads:/mnt/downloads:ro" \
     ebook-search
   
   # Windows (PowerShell)
   docker run -d `
     --name ebook-search `
     -p 8501:8501 `
     -v "${env:USERPROFILE}\Documents:/mnt/documents:ro" `
     -v "${env:USERPROFILE}\Downloads:/mnt/downloads:ro" `
     ebook-search
   ```

3. **Access the application:**
   Open your browser and go to `http://localhost:8501`

### 💻 Method 3: Local Development (No Docker)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd kindle_web
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and go to `http://localhost:8501`

### 🔧 Quick Setup Verification

After starting the application:

1. **Check if it's running:**
   - Visit `http://localhost:8501` in your browser
   - You should see the Ebook Search interface

2. **Configure directories:**
   - Use the sidebar to add your ebook directories
   - For Docker: Use mounted paths like `/mnt/documents`
   - For local: Use your actual directory paths like `/Users/yourname/Books`

3. **Test search:**
   - Try searching for a book title or author
   - Adjust similarity threshold if needed

## Installation & Deployment

### 🚀 Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd kindle_web

# Start the application
docker-compose up -d

# Access at http://localhost:8501
```

### 🐳 Manual Docker Setup

```bash
# Build the image
docker build -t ebook-search .

# Run with your ebook directories
docker run -d \
  --name ebook-search \
  -p 8501:8501 \
  -v "$HOME/Documents:/mnt/documents:ro" \
  -v "$HOME/Books:/mnt/books:ro" \
  ebook-search
```

### 💻 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:8501
```

## Docker Image Details

- **Size**: ~226MB (highly optimized)
- **Base**: Python 3.11 Alpine Linux
- **Startup**: ~2 seconds
- **Memory**: ~50MB runtime usage
- **Dependencies**: 5 core packages

## Usage

### Initial Setup

1. **Access the web interface** at `http://localhost:8501`
2. **Configure search directories** in the sidebar:
   - For Docker: Use mounted paths like `/mnt/documents`, `/mnt/books`
   - For local: Use your actual directory paths
3. **Add or remove directories** as needed using the directory management interface

### Searching for Ebooks

1. **Enter keywords, book titles, or author names** in the search box
2. **Adjust the similarity threshold** in the sidebar for more/less strict matching
3. **View results** with match percentages and file information
4. **Click book items** to see detailed information

### Directory Management

- ✅ **Add directories**: Enter paths and click "Add"
- 🗑️ **Remove directories**: Click the trash icon next to any directory
- 🔄 **Reset to defaults**: Restore original default directories
- 🗑️ **Clear all**: Remove all directories to start fresh

## Default Search Locations

The system automatically searches these common directories:

**Local Installation:**
- `~/Documents`
- `~/Downloads`
- `~/Books`
- `~/Desktop`
- `~/Library/Application Support/Kindle` (macOS)
- `~/Calibre Library`
- `/Users/vishnusivadasan/smbshare/Books/Kindle`

**Docker Container:**
- `/mnt/documents` (mounted from host)
- `/mnt/downloads` (mounted from host)
- `/mnt/books` (mounted from host)
- `/mnt/ebooks` (mounted from host)
- Plus any additional mounted directories

## Advanced Configuration

### Volume Mounting Examples

**macOS/Linux:**
```bash
-v "$HOME/Documents:/mnt/documents:ro"
-v "/Volumes/ExternalDrive/Books:/mnt/external:ro"
```

**Windows (PowerShell):**
```powershell
-v "${env:USERPROFILE}\Documents:/mnt/documents:ro"
-v "D:\Books:/mnt/books:ro"
```

### Customizing Docker Setup

Edit the `docker-compose.yml` file:

```yaml
volumes:
  - "${HOME}/Documents:/mnt/documents:ro"
  - "${HOME}/Downloads:/mnt/downloads:ro"
  - "${HOME}/Books:/mnt/books:ro"
  - "/path/to/your/ebooks:/mnt/ebooks:ro"
```

## Docker Management

### Useful Commands

**Check running containers:**
```bash
docker ps
```

**View application logs:**
```bash
docker logs ebook-search
```

**Stop and remove:**
```bash
docker-compose down
```

**Check image sizes:**
```bash
docker images | grep ebook-search
```

## Documentation

- **[FastAPI Optimization Guide](FASTAPI_OPTIMIZATION.md)** - Complete optimization details and implementation notes

## Performance

| Metric | Value |
|--------|-------|
| Docker Image Size | 226MB |
| Startup Time | ~2 seconds |
| Memory Usage | ~50MB |
| Dependencies | 5 packages |
| Base Image | Python 3.11 Alpine |

## Troubleshooting

### Common Issues

1. **Port 8501 already in use**: Stop other containers or change port in docker-compose.yml
2. **No books found**: Check volume mounts and directory permissions
3. **Slow search**: Reduce similarity threshold or limit search directories
4. **Container won't start**: Check logs with `docker logs ebook-search`

### Getting Help

1. Check the logs: `docker logs ebook-search`
2. Verify volume mounts are correct
3. Ensure directories contain ebook files
4. Check that ports are not in use by other applications

## License

This project is open source and available under the MIT License. 