"""
Quick Example: URL to QR Code Generator
========================================
This is a simple example showing how to use the url_to_qr module programmatically.
"""

from url_to_qr import URLToQRConverter

# Example 1: Generate a simple QR code
print("Example 1: Generating a simple QR code...")
converter = URLToQRConverter()
filepath = converter.generate_qr_code("https://www.google.com", filename="google_qr")
print(f"✓ QR code saved to: {filepath}\n")

# Example 2: Generate a custom styled QR code
print("Example 2: Generating a custom blue QR code...")
filepath = converter.generate_qr_code(
    url="https://github.com",
    filename="github_qr",
    size=15,
    fill_color="darkblue",
    back_color="lightgray",
    style="rounded"
)
print(f"✓ Custom QR code saved to: {filepath}\n")

# Example 3: Generate multiple QR codes
print("Example 3: Generating batch QR codes...")
urls = [
    "https://www.python.org",
    "https://www.stackoverflow.com",
    "https://www.github.com"
]
filepaths = converter.generate_batch(urls, prefix="example")
print(f"✓ Generated {len(filepaths)} QR codes\n")

print("All examples completed! Check the 'qr_codes' folder.")
