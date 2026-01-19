"""
URL to QR Code Generator
========================
A standalone script to convert URLs/links into QR code images.

Usage:
    python url_to_qr.py

Features:
    - Interactive URL input
    - Customizable QR code size and colors
    - Error correction levels
    - Save QR codes as PNG images
    - Batch processing support
"""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import os
from datetime import datetime


class URLToQRConverter:
    """Convert URLs to QR codes with customization options"""
    
    def __init__(self, output_dir="qr_codes"):
        """
        Initialize the converter
        
        Args:
            output_dir (str): Directory to save QR code images
        """
        self.output_dir = output_dir
        self.create_output_directory()
    
    def create_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ Created output directory: {self.output_dir}")
    
    def generate_qr_code(self, url, filename=None, size=10, error_correction='H',
                        fill_color='black', back_color='white', style='square'):
        """
        Generate a QR code from a URL
        
        Args:
            url (str): The URL to encode
            filename (str): Output filename (without extension)
            size (int): Size of the QR code (1-40)
            error_correction (str): Error correction level ('L', 'M', 'Q', 'H')
            fill_color (str): QR code color
            back_color (str): Background color
            style (str): QR code style ('square' or 'rounded')
        
        Returns:
            str: Path to the saved QR code image
        """
        # Error correction mapping
        error_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,  # ~7% correction
            'M': qrcode.constants.ERROR_CORRECT_M,  # ~15% correction
            'Q': qrcode.constants.ERROR_CORRECT_Q,  # ~25% correction
            'H': qrcode.constants.ERROR_CORRECT_H   # ~30% correction
        }
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=None,  # Auto-detect version
            error_correction=error_levels.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_H),
            box_size=size,
            border=4,
        )
        
        # Add URL data
        qr.add_data(url)
        qr.make(fit=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qr_{timestamp}"
        
        # Create image based on style
        if style.lower() == 'rounded':
            # For rounded style, use simple fill colors
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                fill_color=fill_color,
                back_color=back_color
            )
        else:
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Save image
        filepath = os.path.join(self.output_dir, f"{filename}.png")
        img.save(filepath)
        
        return filepath
    
    def generate_batch(self, urls, prefix="qr"):
        """
        Generate QR codes for multiple URLs
        
        Args:
            urls (list): List of URLs to convert
            prefix (str): Prefix for output filenames
        
        Returns:
            list: Paths to saved QR code images
        """
        filepaths = []
        for i, url in enumerate(urls, 1):
            filename = f"{prefix}_{i}"
            filepath = self.generate_qr_code(url, filename=filename)
            filepaths.append(filepath)
            print(f"✓ Generated QR code {i}/{len(urls)}: {filename}.png")
        
        return filepaths


def display_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("           URL to QR Code Generator")
    print("="*60)
    print("\n1. Generate Single QR Code")
    print("2. Generate Batch QR Codes")
    print("3. Generate Custom Styled QR Code")
    print("4. Exit")
    print("\n" + "-"*60)


def get_url_input():
    """Get URL input from user with validation"""
    while True:
        url = input("\nEnter URL: ").strip()
        if url:
            # Add http:// if no protocol specified
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            return url
        print("⚠ URL cannot be empty. Please try again.")


def generate_single_qr(converter):
    """Generate a single QR code"""
    print("\n--- Generate Single QR Code ---")
    url = get_url_input()
    
    # Optional filename
    filename = input("Enter filename (press Enter for auto-generated): ").strip()
    if not filename:
        filename = None
    
    try:
        filepath = converter.generate_qr_code(url, filename=filename)
        print(f"\n✓ QR code generated successfully!")
        print(f"  Saved to: {filepath}")
        print(f"  URL encoded: {url}")
    except Exception as e:
        print(f"\n✗ Error generating QR code: {e}")


def generate_batch_qr(converter):
    """Generate multiple QR codes"""
    print("\n--- Generate Batch QR Codes ---")
    print("Enter URLs (one per line, press Enter twice when done):")
    
    urls = []
    while True:
        url = input().strip()
        if not url:
            if urls:
                break
            else:
                print("⚠ Please enter at least one URL")
                continue
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        urls.append(url)
    
    prefix = input("\nEnter filename prefix (default: 'qr'): ").strip() or "qr"
    
    try:
        print(f"\nGenerating {len(urls)} QR codes...")
        filepaths = converter.generate_batch(urls, prefix=prefix)
        print(f"\n✓ Successfully generated {len(filepaths)} QR codes!")
        print(f"  Saved to: {converter.output_dir}/")
    except Exception as e:
        print(f"\n✗ Error generating QR codes: {e}")


def generate_custom_qr(converter):
    """Generate a custom styled QR code"""
    print("\n--- Generate Custom Styled QR Code ---")
    url = get_url_input()
    
    # Get customization options
    print("\nCustomization Options:")
    
    # Size
    size_input = input("QR code size (1-40, default: 10): ").strip()
    size = int(size_input) if size_input.isdigit() else 10
    
    # Error correction
    print("\nError Correction Levels:")
    print("  L - Low (~7% correction)")
    print("  M - Medium (~15% correction)")
    print("  Q - Quartile (~25% correction)")
    print("  H - High (~30% correction)")
    error = input("Error correction (L/M/Q/H, default: H): ").strip().upper() or 'H'
    
    # Colors
    fill_color = input("QR code color (default: black): ").strip() or 'black'
    back_color = input("Background color (default: white): ").strip() or 'white'
    
    # Style
    print("\nStyles:")
    print("  1. Square (default)")
    print("  2. Rounded")
    style_choice = input("Choose style (1/2): ").strip()
    style = 'rounded' if style_choice == '2' else 'square'
    
    # Filename
    filename = input("\nEnter filename (press Enter for auto-generated): ").strip() or None
    
    try:
        filepath = converter.generate_qr_code(
            url, 
            filename=filename,
            size=size,
            error_correction=error,
            fill_color=fill_color,
            back_color=back_color,
            style=style
        )
        print(f"\n✓ Custom QR code generated successfully!")
        print(f"  Saved to: {filepath}")
        print(f"  URL encoded: {url}")
    except Exception as e:
        print(f"\n✗ Error generating QR code: {e}")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("  Welcome to URL to QR Code Generator!")
    print("="*60)
    
    # Initialize converter
    converter = URLToQRConverter()
    
    while True:
        display_menu()
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            generate_single_qr(converter)
        elif choice == '2':
            generate_batch_qr(converter)
        elif choice == '3':
            generate_custom_qr(converter)
        elif choice == '4':
            print("\n👋 Thank you for using URL to QR Code Generator!")
            print("="*60 + "\n")
            break
        else:
            print("\n⚠ Invalid option. Please select 1-4.")
        
        # Ask to continue
        if choice in ['1', '2', '3']:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Program interrupted by user.")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("="*60 + "\n")
