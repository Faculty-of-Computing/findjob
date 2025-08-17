import secrets
import base64
import argparse

def generate_secret_key(length=32):
    """
    Generate a secure random secret key.
    
    Args:
        length (int): Length of the key in bytes (default: 32)
        
    Returns:
        str: A URL-safe base64-encoded secret key
    """
    # Generate random bytes
    random_bytes = secrets.token_bytes(length)
    # Encode to URL-safe base64
    return base64.urlsafe_b64encode(random_bytes).decode('utf-8')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a secure secret key')
    parser.add_argument('--length', type=int, default=32,
                      help='Length of the key in bytes (default: 32)')
    args = parser.parse_args()
    
    secret_key = generate_secret_key(args.length)
    print(f"Generated secret key: {secret_key}")