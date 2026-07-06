import uuid

def generate_uuid() -> str:
    """
    Generates a standard string representation of a UUID4.
    """
    return str(uuid.uuid4())

def mask_email(email: str) -> str:
    """
    Utility helper that masks emails to preserve privacy.
    Example: john.doe@example.com -> j******e@example.com
    """
    if not email or "@" not in email:
        return email
    parts = email.split("@")
    name = parts[0]
    domain = parts[1]
    
    if len(name) <= 2:
        return f"{name[0]}*@{domain}"
    
    return f"{name[0]}{'*' * (len(name) - 2)}{name[-1]}@{domain}"
