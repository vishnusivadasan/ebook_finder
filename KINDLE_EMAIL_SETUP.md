# Kindle Email Setup Guide

This guide will help you set up the Kindle email functionality to send ebooks directly from the search interface to your Kindle device.

## Prerequisites

1. **Gmail Account**: You need a Gmail account to send emails
2. **Kindle Email Address**: Your Kindle device's email address
3. **Gmail App Password**: A 16-character app password for Gmail

## Step 1: Find Your Kindle Email Address

1. Go to [Amazon's Manage Your Content and Devices](https://www.amazon.com/mn/dcw/myx.html)
2. Click on the **Preferences** tab
3. Scroll down to **Personal Document Settings**
4. Find your Kindle device and note the email address (e.g., `yourname_123@kindle.com`)

## Step 2: Add Approved Email Address

1. In the same **Personal Document Settings** section
2. Under **Approved Personal Document E-mail List**
3. Click **Add a new approved e-mail address**
4. Add your Gmail address: `mysterious.18.vishnu@gmail.com`
5. Click **Add Address**

## Step 3: Generate Gmail App Password

1. Go to your [Google Account settings](https://myaccount.google.com/)
2. Click on **Security** in the left sidebar
3. Under **Signing in to Google**, click **2-Step Verification** (you must have this enabled)
4. Scroll down and click **App passwords**
5. Select **Mail** as the app and **Other** as the device
6. Enter "Kindle Email" as the device name
7. Click **Generate**
8. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

## Step 4: Configure the Application

1. Open the ebook search application in your browser
2. In the sidebar, find the **📱 Kindle Email** section
3. Click **Show** to expand the settings
4. Enter your 16-character Gmail app password (without spaces)
5. Click **Save**
6. The status should change to **Configured**

## Step 5: Update Email Addresses (if needed)

The application is pre-configured with:
- **Gmail**: `mysterious.18.vishnu@gmail.com`
- **Kindle**: `mysterious.18.vishnu4@kindle.com`

If you need to change these, you can modify them in the `kindle_email.py` file:

```python
kindle_sender = KindleEmailSender(
    gmail_address="your-email@gmail.com",
    kindle_email="your-kindle@kindle.com"
)
```

## Using the Feature

1. **Search for books** using the search interface
2. **Find a compatible book** (PDF, MOBI, EPUB, AZW, AZW3, TXT, DOC, DOCX)
3. **Click the "📱 Send to Kindle" button** next to the book
4. **Wait for confirmation** - the button will show "Sending..." then "✓ Sent"
5. **Check your Kindle** - the book should appear in your library within a few minutes

## Supported File Formats

- **PDF** - Documents and ebooks
- **MOBI** - Amazon's ebook format
- **EPUB** - Standard ebook format (converted by Kindle)
- **AZW/AZW3** - Amazon's newer ebook formats
- **TXT** - Plain text files
- **DOC/DOCX** - Microsoft Word documents

## File Size Limits

- Maximum file size: **50 MB** (Kindle email limitation)
- Files larger than 50 MB will be rejected with an error message

## Troubleshooting

### "Gmail app password not configured"
- Make sure you've entered the 16-character app password correctly
- Verify 2-Step Verification is enabled on your Google account

### "Username and Password not accepted"
- Double-check your Gmail app password
- Make sure you're using an app password, not your regular Gmail password
- Try generating a new app password

### "File too large"
- The file exceeds the 50 MB limit
- Try finding a smaller version of the book
- Consider using a different format (e.g., MOBI instead of PDF)

### "Unsupported format"
- The file format is not supported by Kindle
- Convert the file to a supported format using tools like Calibre

### Book doesn't appear on Kindle
- Check that your Gmail address is in the approved senders list
- Verify the Kindle email address is correct
- Check your Kindle's Wi-Fi connection
- Look in the "Documents" section of your Kindle library

## Security Notes

- Your Gmail app password is stored temporarily in the application memory
- For production use, consider setting the `GMAIL_APP_PASSWORD` environment variable
- App passwords are safer than using your main Gmail password
- You can revoke app passwords anytime from your Google Account settings

## Environment Variable Setup (Optional)

Instead of entering the password in the UI, you can set it as an environment variable:

```bash
export GMAIL_APP_PASSWORD="your-16-char-password"
```

Then restart the application. The password will be automatically detected.

## Testing

You can test the functionality using the included test script:

```bash
python test_kindle.py
```

This will verify all API endpoints are working correctly. 