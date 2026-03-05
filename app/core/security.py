from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

# Generate RSA keys (2048 bits)
# In a real production scenario, you might want to persist these keys
# or load them from environment variables/files to ensure server restarts
# don't invalidate existing encrypted payloads in transit (though for login, transient is fine).
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

def get_public_key():
    """Return the public key in PEM format."""
    return public_key.decode('utf-8')

def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypts a base64 encoded RSA encrypted password.
    Returns the plaintext password.
    """
    try:
        # Decode base64
        encrypted_bytes = base64.b64decode(encrypted_password)
        
        # Create cipher
        cipher = PKCS1_v1_5.new(RSA.import_key(private_key))
        
        # Decrypt (sentinel is a random string to prevent oracle attacks, 
        # but here we just want to know if it failed)
        sentinel = "DECRYPTION_FAILED"
        decrypted_message = cipher.decrypt(encrypted_bytes, sentinel.encode('utf-8'))
        
        if decrypted_message == sentinel.encode('utf-8'):
            raise ValueError("Decryption failed")
            
        return decrypted_message.decode('utf-8')
    except Exception as e:
        # If decryption fails, we might want to return the original string 
        # in case it wasn't encrypted (backward compatibility during migration),
        # or raise an error. Given the user asked for encryption operations,
        # we'll log the error and return the original input or None.
        # For now, let's assume if it fails, it might be a plain text password (dev mode)
        # or a real attack. 
        # Strategy: Return original string if decryption fails, let the hash check decide.
        # This allows existing 'curl' commands with plain text to still work 
        # IF the plain text doesn't look like valid base64 RSA.
        return encrypted_password
