# Phishing Website Detection System

A Flask-based web application that detects phishing URLs using Machine Learning. The system supports checking URLs directly and extracting URLs from uploaded QR code images.

## Features
- **User Authentication**: Login, Register, and Email Verification (OTP).
- **Phishing Detection**: ML model to classify URLs as "Safe" or "Phishing".
- **QR Code Support**: Upload a QR code image to scan and analyze the embedded URL.
- **Admin Dashboard**: Manage users and view scan history.

---

## 🚀 Installation Guide

Follow these steps to set up and run the project from scratch.

### 1. Prerequisites
- **Python 3.8** or higher.
- **Git** (to clone the repository).
- **Homebrew** (for Mac users, to install system libraries).

### 2. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/zuptechin-cell/phising_website.git
cd phising_website/phissing_website_qr
```

### 3. Set Up a Virtual Environment (Recommended)
It is good practice to run Python projects in a virtual environment to avoid conflicting dependencies.
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 4. Install Python Dependencies
Install the required libraries using pip:
```bash
pip install -r requirements.txt
```

### 5. Install System Dependencies (For QR Code Support)
The project uses `pyzbar` for reading QR codes. This requires the `zbar` shared library to be installed on your system.

**For Mac Users (Homebrew):**
```bash
brew install zbar
```

**For Ubuntu/Debian Linux:**
```bash
sudo apt-get install libzbar0
```

**For Windows:**
You may need to download the Visual C++ Redistributable packages. Usually, `pip install pyzbar` includes the necessary DLLs, but if it fails, follow the [pyzbar installation guide](https://pypi.org/project/pyzbar/).

---

## ▶️ Running the Application

### 1. Start the Server
Run the following command in your terminal:
```bash
python3 app.py
```

### 2. Access the Website
Open your web browser and go to:
**http://127.0.0.1:5000**

---

## 🛠 Troubleshooting

### "WARNING: pyzbar not found. QR scanning will be disabled."
If you see this message, the application has started, but QR code scanning is disabled because the `zbar` library wasn't found. 

**Fix for Mac (M1/M2/M3 Apple Silicon):**
If you installed `zbar` via Homebrew but it's still not found, try running the app with the library path explicitly set:

```bash
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH python3 app.py
```
*(This helps Python find the library installed by Homebrew in `/opt/homebrew/lib`)*

### "ModuleNotFoundError: No module named..."
Ensure you have activated your virtual environment and installed the requirements:
```bash
pip install -r requirements.txt
```

---

## 📝 Usage Notes

- **Default Admin**: `manigandan` (Password: `boopathi123456`) - *Created automatically on first run*.
- **Register**: You can create a new account via the "Register" page.
- **Test User**:
  - Username: `testuser`
  - Password: `test1234`
  *(If you ran the setup script provided earlier)*