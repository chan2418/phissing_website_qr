"""
Generate 10 Bad/Suspicious QR Codes for Phishing Detection Testing
These URLs simulate potential phishing attempts with suspicious patterns
"""

from url_to_qr import URLToQRConverter
import os

# Initialize converter with bad_QR output directory
output_dir = "qr_codes/bad_QR"
converter = URLToQRConverter(output_dir=output_dir)

# List of suspicious/bad URLs for testing
bad_urls = [
    ("https://paypa1-secure-login.com", "paypal_phish_qr"),
    ("https://amazon-account-verify.tk", "amazon_phish_qr"),
    ("https://google-security-alert.ml", "google_phish_qr"),
    ("https://apple-id-unlock.ga", "apple_phish_qr"),
    ("https://microsoft-support-team.cf", "microsoft_phish_qr"),
    ("https://facebook-security-check.gq", "facebook_phish_qr"),
    ("https://netflix-payment-update.tk", "netflix_phish_qr"),
    ("https://bank-of-america-verify.ml", "bank_phish_qr"),
    ("https://instagram-copyright-notice.ga", "instagram_phish_qr"),
    ("https://linkedin-premium-free.cf", "linkedin_phish_qr"),
]

print("="*60)
print("  Generating 10 Bad/Suspicious QR Codes")
print("="*60)
print(f"\nOutput directory: {output_dir}\n")

generated_files = []

for i, (url, filename) in enumerate(bad_urls, 1):
    try:
        filepath = converter.generate_qr_code(url, filename=filename, size=12, error_correction='H')
        generated_files.append(filepath)
        print(f"✓ [{i}/10] Generated: {filename}.png")
        print(f"    URL: {url}")
    except Exception as e:
        print(f"✗ [{i}/10] Failed to generate {filename}: {e}")

print("\n" + "="*60)
print(f"✓ Successfully generated {len(generated_files)}/10 bad QR codes")
print(f"  Location: {output_dir}/")
print("="*60)
print("\nThese QR codes contain suspicious URLs that simulate:")
print("  - Typosquatting (paypa1 instead of paypal)")
print("  - Suspicious TLDs (.tk, .ml, .ga, .cf, .gq)")
print("  - Phishing keywords (verify, secure, unlock, alert)")
print("  - Brand impersonation")
print("\nUse these to test your phishing detection model!")
