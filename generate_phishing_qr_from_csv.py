"""
Analyze url.csv and generate QR codes for PHISHING URLs only
Store all QR codes in the bad_QR folder
"""

import csv
from url_to_qr import URLToQRConverter
import re

# Initialize converter with bad_QR output directory
output_dir = "qr_codes/bad_QR"
converter = URLToQRConverter(output_dir=output_dir)

# Read CSV file and extract phishing URLs
csv_file = "test_data/url.csv"
phishing_urls = []

print("="*70)
print("  Analyzing url.csv for Phishing URLs")
print("="*70)

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row.get('url', '').strip() if row.get('url') else ''
        status = row.get('status', '').strip().lower() if row.get('status') else ''
        
        if status == 'phishing' and url:
            phishing_urls.append(url)
            print(f"✓ Found phishing URL: {url}")

print(f"\nTotal phishing URLs found: {len(phishing_urls)}")
print("\n" + "="*70)
print("  Generating QR Codes for Phishing URLs")
print("="*70 + "\n")

generated_files = []

for i, url in enumerate(phishing_urls, 1):
    try:
        # Create a safe filename from the URL
        # Extract domain or create identifier
        domain_match = re.search(r'://([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1).replace('www.', '').replace('.', '_')
            # Limit filename length
            domain = domain[:30]
            filename = f"phish_{i}_{domain}_qr"
        else:
            filename = f"phish_{i}_qr"
        
        filepath = converter.generate_qr_code(url, filename=filename, size=12, error_correction='H')
        generated_files.append(filepath)
        print(f"✓ [{i}/{len(phishing_urls)}] Generated: {filename}.png")
        print(f"    URL: {url[:60]}{'...' if len(url) > 60 else ''}")
        
    except Exception as e:
        print(f"✗ [{i}/{len(phishing_urls)}] Failed to generate QR for: {url[:50]}")
        print(f"    Error: {e}")

print("\n" + "="*70)
print(f"✓ Successfully generated {len(generated_files)}/{len(phishing_urls)} QR codes")
print(f"  Location: {output_dir}/")
print("="*70)
print("\nAll phishing URLs from url.csv have been converted to QR codes!")
