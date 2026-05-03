"""
StudyFlow v4 — Authentication & User Management
• Email as primary key (unique)
• SHA-256 hashed passwords
• JSON-based organized storage
• OTP-based password reset
• Full student profile with picture (base64 JPEG)
"""

import json
import os
import hashlib
import random
import string
import re
import base64
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Tuple

# ─────────────────────────────────────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────────────────────────────────────
DATA_DIR   = "studyflow_data"
KG_DIR     = os.path.join(DATA_DIR, "kg")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


# ─────────────────────────────────────────────────────────────────────────────
#  INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(KG_DIR,   exist_ok=True)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load() -> Dict:
    """Load users.json — returns { users: {email: {...}}, usernames: {username: email} }"""
    _ensure()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "usernames": {}}


def _save(data: Dict):
    _ensure()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
#  KG PATH HELPER
# ─────────────────────────────────────────────────────────────────────────────
def kg_path(username: str) -> str:
    _ensure()
    return os.path.join(KG_DIR, f"{username}_kg.json")


# ─────────────────────────────────────────────────────────────────────────────
#  REGISTRATION
# ─────────────────────────────────────────────────────────────────────────────
def register(
    email: str,
    password: str,
    confirm_password: str,
    display_name: str,
    username: str,
    hours_per_day: int = 4,
) -> Tuple[bool, str]:

    email        = email.strip().lower()
    username     = username.strip().lower()
    display_name = display_name.strip()

    # ── Validation ──────────────────────────────────────────────────────────
    if not all([email, password, confirm_password, display_name, username]):
        return False, "All fields are required."

    if not re.match(r'^[\w.%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$', email):
        return False, "Invalid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    if not re.match(r'^[a-z0-9_\-]{3,30}$', username):
        return False, "Username: 3-30 chars — letters, numbers, _ or -"

    data = _load()

    if email in data["users"]:
        return False, "This email is already registered. Please log in."

    if username in data["usernames"]:
        return False, "Username already taken. Please choose another."

    # ── Create user record ───────────────────────────────────────────────────
    data["users"][email] = {
        # ── Auth info ─────────────────────────────────────────
        "email":         email,
        "username":      username,
        "password_hash": _hash(password),
        "joined":        datetime.now().strftime("%Y-%m-%d"),

        # ── Basic profile ─────────────────────────────────────
        "display_name":  display_name,
        "hours_per_day": int(hours_per_day),

        # ── Extended student profile ──────────────────────────
        "phone":         "",
        "university":    "",
        "department":    "",
        "semester":      "",
        "bio":           "",

        # ── Profile picture (base64 JPEG string or null) ──────
        "profile_pic":   None,
    }

    # email ↔ username index for fast lookup
    data["usernames"][username] = email

    _save(data)
    return True, "Account created successfully! You can now log in."


# ─────────────────────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────────────────────
def authenticate(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    email = email.strip().lower()

    if not email or not password:
        return False, "Please enter email and password.", None

    data = _load()

    if email not in data["users"]:
        return False, "No account found with this email.", None

    user = data["users"][email]

    if user["password_hash"] != _hash(password):
        return False, "Incorrect password.", None

    return True, "Login successful!", dict(user)


# ─────────────────────────────────────────────────────────────────────────────
#  GETTERS
# ─────────────────────────────────────────────────────────────────────────────
def get_user(email: str) -> Optional[Dict]:
    return _load()["users"].get(email.strip().lower())


def email_exists(email: str) -> bool:
    return email.strip().lower() in _load()["users"]


# ─────────────────────────────────────────────────────────────────────────────
#  PROFILE UPDATE
# ─────────────────────────────────────────────────────────────────────────────
def update_profile(email: str, updates: Dict) -> Tuple[bool, str]:
    email = email.strip().lower()
    data  = _load()

    if email not in data["users"]:
        return False, "User not found."

    user = data["users"][email]

    # ── Handle username change (rename KG file too) ──────────────────────────
    if "username" in updates:
        new_u = updates["username"].strip().lower()
        old_u = user["username"]

        if new_u != old_u:
            if not re.match(r'^[a-z0-9_\-]{3,30}$', new_u):
                return False, "Username: 3-30 chars — letters, numbers, _ or -"

            if new_u in data["usernames"] and data["usernames"][new_u] != email:
                return False, "Username already taken."

            # Rename KG JSON file
            old_path = kg_path(old_u)
            new_path = kg_path(new_u)
            if os.path.exists(old_path):
                with open(old_path, "r", encoding="utf-8") as f:
                    kg_data = json.load(f)
                kg_data["username"] = new_u
                for s in kg_data.get("sessions", []):
                    if s.get("student") == old_u:
                        s["student"] = new_u
                with open(old_path, "w", encoding="utf-8") as f:
                    json.dump(kg_data, f, indent=2, ensure_ascii=False)
                os.rename(old_path, new_path)

            # Update username index
            del data["usernames"][old_u]
            data["usernames"][new_u] = email

    # ── Apply allowed fields ─────────────────────────────────────────────────
    _allowed = [
        "display_name", "username", "hours_per_day",
        "phone", "university", "department", "semester",
        "bio", "profile_pic",
    ]
    for k, v in updates.items():
        if k in _allowed:
            user[k] = v

    data["users"][email] = user
    _save(data)
    return True, "Profile updated successfully!"


# ─────────────────────────────────────────────────────────────────────────────
#  PASSWORD RESET (OTP-based)
# ─────────────────────────────────────────────────────────────────────────────
def generate_otp() -> str:
    """Generate a 6-digit numeric OTP."""
    return "".join(random.choices(string.digits, k=6))


def reset_password(email: str, new_password: str) -> Tuple[bool, str]:
    email = email.strip().lower()

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."

    data = _load()
    if email not in data["users"]:
        return False, "No account found with this email."

    data["users"][email]["password_hash"] = _hash(new_password)
    _save(data)
    return True, "Password reset successfully! Please log in."


# ─────────────────────────────────────────────────────────────────────────────
#  PROFILE PICTURE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def image_to_b64(uploaded_file) -> Optional[str]:
    """Resize uploaded image to 200×200 and return base64 JPEG string."""
    try:
        from PIL import Image
        img = Image.open(uploaded_file)
        img.thumbnail((200, 200), Image.LANCZOS)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None


def b64_img_tag(b64: str, size: int = 56, extra: str = "") -> str:
    """Return an HTML <img> tag for a base64 profile picture."""
    return (
        f'<img src="data:image/jpeg;base64,{b64}" '
        f'style="width:{size}px;height:{size}px;border-radius:50%;'
        f'object-fit:cover;border:2px solid rgba(255,255,255,0.35);{extra}" />'
    )