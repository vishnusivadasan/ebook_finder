# 📚 Ebook Search System

A web-based ebook search system built with Streamlit that helps you find and organize your digital book collection.

## Features

- 🔍 **Smart Search**: Fuzzy search with partial matching for book titles and filenames
- 📁 **Multi-Directory Support**: Searches common ebook locations automatically
- 🎯 **Configurable Similarity**: Adjustable search sensitivity
- 📊 **File Statistics**: View your collection metrics
- 🖥️ **Cross-Platform**: Works on macOS, Windows, and Linux
- 📂 **Quick Access**: Open file locations directly from the interface
- 🐳 **Docker Ready**: Easy deployment with Docker containers

## Supported Formats

- PDF (.pdf)
- EPUB (.epub)
- MOBI (.mobi)
- Kindle (.azw, .azw3)
- DjVu (.djvu)
- FictionBook (.fb2)
- Plain Text (.txt)

## Installation & Deployment

Choose your preferred method:

### 🐳 Option 1: Docker Deployment (Recommended)

Docker provides the easiest way to deploy this application with consistent behavior across all systems.

#### Quick Start with Docker Compose

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd kindle_web
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Open your browser and go to `http://localhost:8501`

#### Manual Docker Commands

1. **Build the image:**
   ```bash
   docker build -t ebook-search .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name ebook-search-app \
     -p 8501:8501 \
     -v "$HOME/Documents:/mnt/documents:ro" \
     -v "$HOME/Downloads:/mnt/downloads:ro" \
     -v "$HOME/Books:/mnt/books:ro" \
     ebook-search
   ```

#### Volume Mounting Explained

The container needs access to your host file system to search for ebooks. This is done through **volume mounts**.

**Syntax:**
```
-v "host_path:container_path:permissions"
```

**Examples:**

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

**Windows (Command Prompt):**
```cmd
-v "%USERPROFILE%\Documents:/mnt/documents:ro"
```

#### Customizing Docker Setup

Edit `docker-compose.yml` to add your specific directories:

```yaml
volumes:
  - "${HOME}/Documents:/mnt/documents:ro"
  - "${HOME}/Downloads:/mnt/downloads:ro"
  - "${HOME}/Books:/mnt/books:ro"
  - "/path/to/your/ebooks:/mnt/ebooks:ro"
  - "/Volumes/ExternalDrive:/mnt/external:ro"
```

### 💻 Option 2: Local Installation

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the application:**
   ```bash
   streamlit run app.py
   ```
4. **Open your browser** and navigate to `http://localhost:8501`

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
4. **Click "Open Folder"** to navigate directly to any ebook's location

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

**Docker Container:**
- `/mnt/documents` (mounted from host)
- `/mnt/downloads` (mounted from host)
- `/mnt/books` (mounted from host)
- `/mnt/ebooks` (mounted from host)
- Plus any additional mounted directories

## Configuration

### Similarity Threshold
- **High (80-100)**: Only very close matches
- **Medium (60-80)**: Moderate similarity required
- **Low (0-60)**: More lenient matching

### Custom Directories
Add additional search locations in the sidebar by entering directory paths.

## Docker Management

### Useful Docker Commands

**Check running containers:**
```bash
docker ps
```

**View logs:**
```bash
docker logs ebook-search-app
```

**Stop the container:**
```bash
docker stop ebook-search-app
```

**Remove the container:**
```bash
docker rm ebook-search-app
```

**Update the application:**
```bash
docker-compose down
docker-compose up -d --build
```

### Troubleshooting Docker

**No books found?**
- Check volume mounts in `docker-compose.yml`
- Ensure directories exist on your host system
- Verify Docker has access to your directories

**Permission issues?**
- **macOS**: Allow Docker access in System Preferences → Security & Privacy
- **Linux**: Ensure proper directory permissions
- **Windows**: Make sure drives are shared with Docker

**Port conflicts?**
Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Use port 8502 instead
```

## Tips for Better Results

1. **Use descriptive keywords**: Try author names, series titles, or key terms from the book title
2. **Adjust similarity threshold**: Lower it if you're getting too few results
3. **Check file naming**: The search works best with properly named files
4. **Add custom directories**: Include any folder where you store ebooks
5. **Use Docker for consistency**: Docker deployment ensures the same behavior across all systems

## Technical Details

- **Backend**: Python with fuzzy string matching (fuzzywuzzy)
- **Frontend**: Streamlit web framework
- **Search Algorithm**: Combines partial ratio and token sorting for optimal matching
- **File Discovery**: Recursive glob pattern matching for supported formats
- **Containerization**: Docker with volume mounting for file system access

## Troubleshooting

**No books found?**
- Check if your ebooks are in supported formats
- Add custom directories in the sidebar
- Verify file permissions for the directories being searched

**Search not working well?**
- Try different keywords or partial titles
- Lower the similarity threshold
- Ensure your ebook files have descriptive names

**Container issues?**
- Check Docker logs: `docker logs ebook-search-app`
- Verify volume mounts are correct
- Ensure directories exist on host system

## License

This project is open source and available under the MIT License. 