import re

def extract_account_id(text):
    match = re.search(r"\b\d{6,12}\b", text)
    return match.group() if match else None

def extract_amount(text):
    match = re.search(r"(₹?\s?\d+)", text)
    return match.group() if match else None