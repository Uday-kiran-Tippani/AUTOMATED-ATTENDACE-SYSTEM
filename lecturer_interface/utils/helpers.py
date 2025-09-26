# utils/helpers.py
import re

def email_to_key(email: str) -> str:
    """Sanitize email to store as Firebase key"""
    return email.replace("@", "_at_").replace(".", "_dot_")

def chunk_list(lst, n):
    """Split a list into chunks of size n."""
    return [lst[i:i+n] for i in range(0, len(lst), n)]
