def extract_text_from_txt(txt_bytes: bytes) -> str:
    """
    Extracts text content from a TXT file provided as bytes.
    Assumes UTF-8 encoding.
    """
    try:
        return txt_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback to another encoding if needed, or handle the error
        try:
            return txt_bytes.decode('latin-1')
        except Exception as e:
            print(f"Error decoding TXT file: {e}")
            return ""
    except Exception as e:
        print("Error reading TXT file: {e}")
        return ""