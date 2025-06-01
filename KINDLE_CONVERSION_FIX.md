# Kindle Conversion Fix

This feature implements an automatic ebook format conversion system to fix compatibility issues when sending books to Kindle devices via email.

## Problem

Kindle devices sometimes have issues with certain EPUB files, even though EPUB is officially supported. This can result in books not displaying correctly or failing to open.

## Solution

We implement a conversion chain that processes ebooks before sending them to Kindle:

### For EPUB files:
1. **EPUB → MOBI**: Convert the original EPUB to MOBI format
2. **MOBI → EPUB**: Convert the MOBI back to EPUB format

This double conversion process cleans up any formatting issues and ensures maximum Kindle compatibility.

### For MOBI/AZW files:
1. **MOBI → EPUB**: Convert directly to EPUB format

## Implementation

### Core Components

1. **`ebook_converter.py`**: Main conversion module
   - Handles format detection and conversion logic
   - Uses Calibre's `ebook-convert` command-line tool
   - Manages temporary files and cleanup
   - Provides fallback mechanisms

2. **`kindle_email.py`**: Enhanced email sender
   - Integrates conversion before sending
   - Maintains original filename for user experience
   - Includes conversion status in email body and API responses

3. **API Endpoints**:
   - `/kindle/send`: Enhanced to include conversion information
   - `/kindle/conversion-info`: New endpoint to check conversion capabilities

### Dependencies

- **Calibre**: Primary conversion engine (recommended)
  - Install: `brew install calibre` (macOS) or `apt-get install calibre` (Ubuntu)
- **ebooklib**: Python library for ebook handling (fallback/future use)

## Usage

### Automatic Conversion

When you send a book to Kindle via the web interface or API, the conversion happens automatically:

```python
# The conversion is transparent to the user
result = kindle_sender.send_book_to_kindle("/path/to/book.epub")

# Result includes conversion information
print(f"Conversion performed: {result['conversion_performed']}")
print(f"Conversion message: {result['conversion_message']}")
```

### API Response

The `/kindle/send` endpoint now returns additional information:

```json
{
    "success": true,
    "message": "Successfully sent 'book.epub' to Kindle with conversion: Successfully converted EPUB→MOBI→EPUB",
    "file_path": "/path/to/book.epub",
    "conversion_performed": true,
    "conversion_message": "Successfully converted EPUB→MOBI→EPUB for Kindle compatibility"
}
```

### Checking Conversion Capabilities

Use the new endpoint to verify conversion setup:

```bash
curl http://localhost:8501/kindle/conversion-info
```

Response:
```json
{
    "success": true,
    "conversion_info": {
        "calibre_available": true,
        "supported_conversions": {
            "epub_to_mobi_to_epub": true,
            "mobi_to_epub": true,
            "fallback_copy": true
        },
        "temp_dir": "/tmp/ebook_conversion_xyz"
    }
}
```

## Testing

Run the test script to verify the conversion setup:

```bash
python test_conversion.py
```

This will:
1. Check if Calibre is properly installed
2. Test conversion capabilities
3. Attempt conversion with sample files (if available)

## File Flow

### Original Process
```
Book File → Email → Kindle
```

### New Process with Conversion
```
EPUB File → Convert to MOBI → Convert to EPUB → Email → Kindle
MOBI File → Convert to EPUB → Email → Kindle
Other Files → Copy → Email → Kindle
```

## Benefits

1. **Improved Compatibility**: Fixes formatting issues that cause display problems
2. **Transparent**: Users don't need to manually convert files
3. **Fallback Safe**: If conversion fails, sends original file
4. **Status Reporting**: Users know what conversions were performed
5. **Clean Cleanup**: Temporary files are automatically removed

## Configuration

The conversion process is automatic and requires no user configuration. However, you can:

1. **Install Calibre** for best conversion quality
2. **Check conversion status** via the API
3. **Monitor logs** for conversion details

## Troubleshooting

### Calibre Not Found
```bash
# macOS
brew install calibre

# Ubuntu/Debian
sudo apt-get install calibre

# Or download from https://calibre-ebook.com/download
```

### Conversion Fails
- The system will fall back to sending the original file
- Check logs for specific error messages
- Verify file permissions and disk space

### Large Files
- Conversions may take time for large files (timeout: 5 minutes)
- Ensure adequate disk space for temporary files
- Monitor the temp directory for cleanup

## Development

### Adding New Formats

To support additional formats, modify `ebook_converter.py`:

1. Add format detection in `convert_for_kindle_compatibility()`
2. Implement conversion logic
3. Add appropriate Calibre flags for optimization

### Custom Conversion Logic

The converter supports different conversion strategies:
- Chain conversions (EPUB→MOBI→EPUB)
- Direct conversions (MOBI→EPUB)
- Fallback copying (unsupported formats)

## Future Enhancements

1. **Format Detection**: Better detection of problematic files
2. **Conversion Options**: User-configurable conversion parameters
3. **Batch Processing**: Convert multiple files at once
4. **Alternative Tools**: Support for additional conversion engines
5. **Caching**: Cache converted files for repeated sends 