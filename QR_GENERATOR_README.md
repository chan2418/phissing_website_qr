# URL to QR Code Generator

A standalone Python script to convert URLs/links into QR code images with customization options.

## Features

✨ **Single QR Code Generation** - Convert one URL to a QR code  
🔄 **Batch Processing** - Generate multiple QR codes at once  
🎨 **Custom Styling** - Choose colors, sizes, and styles  
🛡️ **Error Correction** - Multiple error correction levels  
📁 **Auto Organization** - Saves all QR codes to a dedicated folder  

## Installation

1. Install required dependencies:
```bash
pip install -r qr_requirements.txt
```

Or install manually:
```bash
pip install qrcode[pil] Pillow
```

## Usage

### Run the Script
```bash
python url_to_qr.py
```

### Menu Options

#### 1. Generate Single QR Code
- Enter a URL
- Optionally provide a custom filename
- QR code is generated with default settings

**Example:**
```
Enter URL: https://example.com
Enter filename (press Enter for auto-generated): my_website
```

#### 2. Generate Batch QR Codes
- Enter multiple URLs (one per line)
- Press Enter twice when done
- All QR codes are generated with sequential numbering

**Example:**
```
Enter URLs (one per line, press Enter twice when done):
https://google.com
https://github.com
https://stackoverflow.com

Enter filename prefix (default: 'qr'): website
```
Output: `website_1.png`, `website_2.png`, `website_3.png`

#### 3. Generate Custom Styled QR Code
Customize your QR code with:
- **Size**: 1-40 (default: 10)
- **Error Correction**: L, M, Q, H (default: H)
- **Colors**: Any color name or hex code
- **Style**: Square or Rounded

**Example:**
```
Enter URL: https://mysite.com
QR code size (1-40, default: 10): 15
Error correction (L/M/Q/H, default: H): H
QR code color (default: black): blue
Background color (default: white): yellow
Choose style (1/2): 2
Enter filename: custom_qr
```

## Error Correction Levels

| Level | Correction | Use Case |
|-------|-----------|----------|
| **L** | ~7% | Clean environments, larger data capacity |
| **M** | ~15% | Normal use cases |
| **Q** | ~25% | Outdoor use, potential damage |
| **H** | ~30% | Maximum reliability (recommended) |

## Output

All QR codes are saved to the `qr_codes/` directory in PNG format.

**Default naming:**
- Single: `qr_YYYYMMDD_HHMMSS.png`
- Batch: `qr_1.png`, `qr_2.png`, etc.
- Custom: Your specified filename

## Examples

### Basic Usage
```bash
python url_to_qr.py
# Select option 1
# Enter: https://example.com
# Result: qr_codes/qr_20251222_142530.png
```

### Batch Generation
```bash
python url_to_qr.py
# Select option 2
# Enter multiple URLs
# Result: qr_codes/qr_1.png, qr_2.png, qr_3.png
```

### Custom Colored QR Code
```bash
python url_to_qr.py
# Select option 3
# URL: https://mywebsite.com
# Size: 12
# Error: H
# Fill color: darkblue
# Back color: lightgray
# Style: Rounded
# Result: Beautiful custom QR code
```

## Color Options

You can use:
- **Color names**: `black`, `white`, `red`, `blue`, `green`, etc.
- **Hex codes**: `#FF0000`, `#00FF00`, `#0000FF`
- **RGB tuples**: `(255, 0, 0)`, `(0, 255, 0)`

## Tips

💡 **Use High Error Correction (H)** for QR codes that will be printed or displayed outdoors  
💡 **Larger sizes** create higher resolution images  
💡 **Rounded style** looks more modern and professional  
💡 **Batch processing** is perfect for creating QR codes for multiple products/links  

## Troubleshooting

**Issue**: Module not found error  
**Solution**: Install dependencies with `pip install qrcode[pil] Pillow`

**Issue**: QR code not scanning  
**Solution**: Increase size or use higher error correction level

**Issue**: Invalid color  
**Solution**: Use standard color names or valid hex codes

## Integration with Flask App

This script is **separate** from the Flask phishing detection app. It's a utility tool for:
- Creating test QR codes for the detection system
- Generating QR codes for legitimate websites
- Batch creating QR codes for testing purposes

## License

Free to use for personal and commercial projects.

## Support

For issues or questions, refer to the script's inline documentation or modify the code to suit your needs.
