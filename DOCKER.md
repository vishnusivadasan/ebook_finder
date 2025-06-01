# 🐳 Docker Deployment Guide

This guide shows how to deploy the Ebook Search System using Docker for easy portability across any system.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

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

### Option 2: Using Docker Commands

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

## Volume Mounting Explained

The container needs access to your host file system to search for ebooks. This is done through **volume mounts**.

### Syntax
```
-v "host_path:container_path:permissions"
```

- `host_path`: Directory on your local machine
- `container_path`: Directory inside the container (use `/mnt/` prefix)
- `permissions`: `ro` (read-only) or `rw` (read-write)

### Common Examples

**macOS/Linux:**
```bash
# Mount Documents folder
-v "$HOME/Documents:/mnt/documents:ro"

# Mount external drive
-v "/Volumes/ExternalDrive/Books:/mnt/external:ro"

# Mount specific ebook folder
-v "/path/to/my/ebooks:/mnt/ebooks:ro"
```

**Windows (PowerShell):**
```powershell
# Mount Documents folder
-v "${env:USERPROFILE}\Documents:/mnt/documents:ro"

# Mount D: drive
-v "D:\Books:/mnt/books:ro"
```

**Windows (Command Prompt):**
```cmd
# Mount Documents folder
-v "%USERPROFILE%\Documents:/mnt/documents:ro"
```

## Customizing Your Setup

### 1. Edit docker-compose.yml

Modify the volumes section to match your system:

```yaml
volumes:
  # Standard directories
  - "${HOME}/Documents:/mnt/documents:ro"
  - "${HOME}/Downloads:/mnt/downloads:ro"
  - "${HOME}/Books:/mnt/books:ro"
  
  # Custom directories - add your own paths
  - "/path/to/your/ebooks:/mnt/ebooks:ro"
  - "/Volumes/ExternalDrive:/mnt/external:ro"
  - "/mnt/nas/books:/mnt/nas:ro"
```

### 2. Multiple Mount Points

You can mount as many directories as needed:

```bash
docker run -d \
  --name ebook-search-app \
  -p 8501:8501 \
  -v "$HOME/Documents:/mnt/documents:ro" \
  -v "$HOME/Downloads:/mnt/downloads:ro" \
  -v "$HOME/Books:/mnt/books:ro" \
  -v "$HOME/Desktop:/mnt/desktop:ro" \
  -v "/Volumes/ExternalDrive/Books:/mnt/external:ro" \
  -v "/path/to/calibre/library:/mnt/calibre:ro" \
  ebook-search
```

## Platform-Specific Instructions

### macOS
```bash
# Example: Mount common macOS locations
docker run -d \
  --name ebook-search-app \
  -p 8501:8501 \
  -v "$HOME/Documents:/mnt/documents:ro" \
  -v "$HOME/Downloads:/mnt/downloads:ro" \
  -v "$HOME/Books:/mnt/books:ro" \
  -v "/Volumes:/mnt/volumes:ro" \
  ebook-search
```

### Windows
```powershell
# Example: Mount common Windows locations
docker run -d `
  --name ebook-search-app `
  -p 8501:8501 `
  -v "${env:USERPROFILE}\Documents:/mnt/documents:ro" `
  -v "${env:USERPROFILE}\Downloads:/mnt/downloads:ro" `
  -v "C:\Books:/mnt/books:ro" `
  ebook-search
```

### Linux
```bash
# Example: Mount common Linux locations
docker run -d \
  --name ebook-search-app \
  -p 8501:8501 \
  -v "$HOME/Documents:/mnt/documents:ro" \
  -v "$HOME/Downloads:/mnt/downloads:ro" \
  -v "/media:/mnt/media:ro" \
  -v "/mnt:/mnt/system:ro" \
  ebook-search
```

## Using the Application

1. **Access the web interface** at `http://localhost:8501`

2. **The container automatically detects mounted directories** - they'll appear as `/mnt/documents`, `/mnt/books`, etc.

3. **Add custom directories** in the web interface by using the mounted paths:
   - Use paths like `/mnt/documents`, `/mnt/ebooks`, etc.
   - These correspond to your host directories that you mounted

4. **Search and browse** your ebooks as normal!

## Troubleshooting

### No books found?
- **Check volume mounts**: Ensure your ebook directories are properly mounted
- **Verify paths**: Use the directory management in the app to see what paths are available
- **Check permissions**: Make sure Docker has access to your directories

### Permission issues?
- **macOS**: You might need to give Docker access to your folders in System Preferences
- **Linux**: Ensure the user has read permissions on mounted directories
- **Windows**: Make sure the drive is shared with Docker

### Port conflicts?
If port 8501 is in use, change the port mapping:
```bash
-p 8502:8501  # Use port 8502 instead
```

## Advanced Usage

### Custom Configuration
You can override the default Streamlit configuration by mounting a config file:

```bash
-v "/path/to/your/config.toml:/app/.streamlit/config.toml:ro"
```

### Running with Different Port
```bash
docker run -d \
  --name ebook-search-app \
  -p 8080:8501 \
  -v "$HOME/Books:/mnt/books:ro" \
  ebook-search
```
Access at: `http://localhost:8080`

### Running in Background
The `-d` flag runs the container in detached mode (background).

To see logs:
```bash
docker logs ebook-search-app
```

To stop:
```bash
docker stop ebook-search-app
```

To remove:
```bash
docker rm ebook-search-app
```

## Pre-built Image (Future)

Once available, you can use a pre-built image instead of building locally:

```bash
docker run -d \
  --name ebook-search-app \
  -p 8501:8501 \
  -v "$HOME/Books:/mnt/books:ro" \
  username/ebook-search:latest
```

This eliminates the need to build the image locally! 