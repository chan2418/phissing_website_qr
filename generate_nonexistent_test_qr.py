"""
Generate QR Code for Non-Existent Test Site URL
"""

from url_to_qr import URLToQRConverter

# Initialize converter
converter = URLToQRConverter()

# Generate QR code for non-existent test site
url = "https://this-site-does-not-exist.test"
filename = "nonexistent_test_qr"

print(f"Generating QR code for: {url}")
filepath = converter.generate_qr_code(url, filename=filename, size=12, error_correction='H')
print(f"✓ QR code generated successfully!")
print(f"  Saved to: {filepath}")
print(f"  URL encoded: {url}")
