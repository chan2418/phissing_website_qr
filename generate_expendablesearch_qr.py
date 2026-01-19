"""
Generate QR Code for Suspicious URL: expendablesearch.com
Store in bad_QR folder for phishing detection testing
"""

from url_to_qr import URLToQRConverter

# Initialize converter with bad_QR output directory
output_dir = "qr_codes/bad_QR"
converter = URLToQRConverter(output_dir=output_dir)

# Generate QR code for suspicious URL
url = "http://expendablesearch.com/search.php?q=joint+infection"
filename = "expendablesearch_phish_qr"

print(f"Generating QR code for: {url}")
filepath = converter.generate_qr_code(url, filename=filename, size=12, error_correction='H')
print(f"✓ QR code generated successfully!")
print(f"  Saved to: {filepath}")
print(f"  URL encoded: {url}")
print(f"\nNote: This URL has suspicious characteristics:")
print(f"  - Suspicious domain name (expendablesearch)")
print(f"  - No HTTPS (insecure)")
print(f"  - Search redirect pattern (common in phishing)")
print(f"  - Query parameters that could be malicious")
