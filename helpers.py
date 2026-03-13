import os
import json
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
INVOICE_NUM_FILE = os.path.join(SCRIPT_DIR, "invoice_number.txt")

def load_config():
    """Load business and banking details from config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(data):
    """Save business and banking details to config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_next_invoice_number():
    """
    Generate invoice number in format INV-YYYY-XXX.
    XXX is an incrementing serial number.
    """
    current_year = datetime.now().year
    serial = 1000
    
    if os.path.exists(INVOICE_NUM_FILE):
        try:
            with open(INVOICE_NUM_FILE, "r") as f:
                serial = int(f.read().strip())
        except:
            pass
            
    next_serial = serial + 1
    
    # Save the decimal serial for next time
    with open(INVOICE_NUM_FILE, "w") as f:
        f.write(str(next_serial))
        
    return f"INV-{current_year}-{next_serial}"

def calculate_taxes(amount, cgst_rate, sgst_rate):
    """Calculate CGST, SGST and total payable."""
    cgst_amount = round(amount * (cgst_rate / 100), 2)
    sgst_amount = round(amount * (sgst_rate / 100), 2)
    total = round(amount + cgst_amount + sgst_amount, 2)
    return {
        "cgst": cgst_amount,
        "sgst": sgst_amount,
        "total": total
    }

def validate_gstin(gstin):
    """Validate GSTIN is exactly 15 characters."""
    return len(gstin.strip()) == 15

def is_numeric(val):
    """Check if a string is a valid positive number."""
    try:
        num = float(val)
        return num >= 0
    except ValueError:
        return False

def format_currency(amount):
    """Format float as currency string."""
    return f"{amount:,.2f}"
