"""
Generate QR Code for Khan Academy Website URL
"""

from url_to_qr import URLToQRConverter

# Initialize converter
converter = URLToQRConverter()

# Generate QR code for Khan Academy website
url = "https://www.khanacademy.org"
filename = "khanacademy_main_qr"

print(f"Generating QR code for: {url}")
filepath = converter.generate_qr_code(url, filename=filename, size=12, error_correction='H')
print(f"✓ QR code generated successfully!")
print(f"  Saved to: {filepath}")
print(f"  URL encoded: {url}")
print(f"\nNote: A Khan Academy QR code also exists in Good_QR folder")
