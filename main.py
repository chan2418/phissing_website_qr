import qrcode

def url_to_qr(url: str, filename: str = "qrcode.png"):
    # Create QR object with some basic settings
    qr = qrcode.QRCode(
        version=1,  # size of the QR (1–40); higher = bigger
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,  # pixel size of each box
        border=4,     # thickness of border (boxes)
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"✅ QR code saved as {filename}")

if __name__ == "__main__":
    url = "https://www.google.com/"
    if not url:
        print("⚠️ URL is empty, please run again and enter a valid URL.")
    else:
        url_to_qr(url, "url_qr.png")
