import bcrypt
import base64
import re
from typing import List


class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return base64.b64encode(hashed).decode('utf-8')  # Bytes to base64 string

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        decoded_hash = base64.b64decode(stored_hash)  # Base64 string to bytes
        return bcrypt.checkpw(password.encode('utf-8'), decoded_hash)

    @staticmethod
    def validate_password(password: str) -> List[str]:
        """
        Returns a list of issues, if the password is valid returns an empty list.

        Rules:
        - Minimum 8 characters.
        - Maximum 64 characters.
        - Must contain only English characters.
        - Must include at least one uppercase letter, one lowercase letter,
          one number, and one special character.
        """
        min_length = 8
        max_length = 64

        issues = []

        if len(password) < min_length:
            issues.append(f"Password must be at least {min_length} characters long.")
        if len(password) > max_length:
            issues.append(f"Password must not exceed {max_length} characters.")

        if not all(ord(char) < 128 for char in password):
            issues.append(f"Password must contain only English characters.")

        if not re.search(r'[A-Z]', password):
            issues.append("Password must include at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            issues.append("Password must include at least one lowercase letter.")

        if not re.search(r'\d', password):
            issues.append("Password must include at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must include at least one special character.")

        return issues

    @staticmethod
    def generate_reset_token():
        # TODO if needed, placeholder for reset token generation
        pass
