"""
Authentication and User Management Utilities
Handles PIN-based login, user data, and permissions.
"""

import os
import pandas as pd
from typing import Optional, Dict


def ensure_users_file():
    """Create users.xlsx if it doesn't exist with default admin user."""
    os.makedirs("data", exist_ok=True)
    path = "data/users.xlsx"
    if not os.path.exists(path):
        default_users = pd.DataFrame([
            {
                "name": "Admin",
                "pin": "1234",
                "role": "admin",
                "allowed_pages": "dashboard,quotation,invoice,receipt,customers,products,reports,settings"
            },
            {
                "name": "Staff",
                "pin": "5678",
                "role": "staff",
                "allowed_pages": "dashboard,quotation,invoice,customers"
            },
            {
                "name": "Viewer",
                "pin": "9999",
                "role": "viewer",
                "allowed_pages": "dashboard,reports"
            }
        ])
        default_users.to_excel(path, index=False)


def load_users() -> pd.DataFrame:
    """
    Load users from data/users.xlsx.
    Returns DataFrame with columns: name, pin, role, allowed_pages
    """
    ensure_users_file()
    try:
        df = pd.read_excel("data/users.xlsx")
        df.columns = [c.strip().lower() for c in df.columns]
        for col in ["name", "pin", "role", "allowed_pages"]:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception as e:
        print(f"Error loading users: {e}")
        return pd.DataFrame(columns=["name", "pin", "role", "allowed_pages"])


def save_users(df: pd.DataFrame):
    """
    Save users DataFrame to data/users.xlsx.
    """
    try:
        os.makedirs("data", exist_ok=True)
        df.to_excel("data/users.xlsx", index=False)
    except Exception as e:
        print(f"Error saving users: {e}")


def validate_pin(pin: str) -> Optional[Dict]:
    """
    Validate PIN and return user record.
    
    Args:
        pin: 4-6 digit PIN string
    
    Returns:
        Dict with user data if valid, None otherwise
        Keys: name, pin, role, allowed_pages (list)
    """
    if not pin or len(pin) < 4:
        return None
    
    users = load_users()
    if users.empty:
        return None
    
    # Find user by PIN
    match = users[users["pin"].astype(str) == str(pin)]
    if match.empty:
        return None
    
    user_row = match.iloc[0]
    
    # Parse allowed_pages CSV to list
    pages_str = str(user_row.get("allowed_pages", ""))
    allowed = [p.strip() for p in pages_str.split(",") if p.strip()]
    
    return {
        "name": str(user_row.get("name", "Unknown")),
        "pin": str(user_row.get("pin", "")),
        "role": str(user_row.get("role", "viewer")),
        "allowed_pages": allowed
    }


def is_admin(user: Optional[Dict]) -> bool:
    """Check if user has admin role."""
    if not user:
        return False
    return user.get("role", "").lower() == "admin"


def can_access_page(user: Optional[Dict], page: str) -> bool:
    """
    Check if user can access a specific page.
    Admin bypasses all restrictions.
    """
    if not user:
        return False
    if is_admin(user):
        return True
    return page in user.get("allowed_pages", [])
