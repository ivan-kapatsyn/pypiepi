import bcrypt
import base64

class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return base64.b64encode(hashed).decode('utf-8')  # Bytes to base64 string

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        decoded_hash = base64.b64decode(stored_hash)  # Base64 string to bytes
        return bcrypt.checkpw(password.encode('utf-8'), decoded_hash)
