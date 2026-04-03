
try:
    from pyzbar.pyzbar import decode
    print("SUCCESS: pyzbar imported")
    import ctypes.util
    lib = ctypes.util.find_library('zbar')
    print(f"Zbar library found at: {lib}")
except ImportError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")
