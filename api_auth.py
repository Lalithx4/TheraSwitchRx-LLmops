import secrets
import hashlib
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os

class APIKeyManager:
    def __init__(self, db_path="api_keys.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the API keys database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT UNIQUE NOT NULL,
                key_hash TEXT NOT NULL,
                user_email TEXT,
                user_name TEXT,
                plan_type TEXT DEFAULT 'free',
                requests_made INTEGER DEFAULT 0,
                request_limit INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                last_used TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT,
                endpoint TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_api_key(self, user_email, user_name, plan_type="free"):
        """Generate a new API key"""
        # Generate a secure random API key
        api_key = f"tsx_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Set limits based on plan
        limits = {
            "free": 100,      # 100 requests per day
            "basic": 1000,    # 1000 requests per day
            "pro": 10000,     # 10000 requests per day
            "enterprise": -1  # Unlimited
        }
        
        request_limit = limits.get(plan_type, 100)
        expires_at = datetime.now() + timedelta(days=365)  # 1 year expiry
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO api_keys 
                (key_id, key_hash, user_email, user_name, plan_type, request_limit, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (api_key[:12], key_hash, user_email, user_name, plan_type, request_limit, expires_at))
            
            conn.commit()
            return {
                "api_key": api_key,
                "plan": plan_type,
                "daily_limit": request_limit,
                "expires_at": expires_at.isoformat()
            }
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def validate_api_key(self, api_key):
        """Validate API key and check limits"""
        if not api_key or not api_key.startswith("tsx_"):
            return {"valid": False, "error": "Invalid API key format"}
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT key_id, user_email, plan_type, requests_made, request_limit, 
                   expires_at, is_active, created_at
            FROM api_keys 
            WHERE key_hash = ?
        ''', (key_hash,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {"valid": False, "error": "API key not found"}
        
        key_id, email, plan, requests_made, limit, expires_at, is_active, created_at = result
        
        # Check if key is active
        if not is_active:
            conn.close()
            return {"valid": False, "error": "API key has been deactivated"}
        
        # Check expiry
        if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
            conn.close()
            return {"valid": False, "error": "API key has expired"}
        
        # Check daily rate limit (reset every 24 hours)
        try:
            created_date = datetime.fromisoformat(created_at).date()
            today = datetime.now().date()
            
            if created_date < today:
                # Reset daily counter
                cursor.execute('UPDATE api_keys SET requests_made = 0 WHERE key_hash = ?', (key_hash,))
                requests_made = 0
        except:
            # Fallback if date parsing fails
            pass
        
        # Check if limit exceeded
        if limit > 0 and requests_made >= limit:
            conn.close()
            return {"valid": False, "error": "Daily API limit exceeded"}
        
        # Update usage
        cursor.execute('''
            UPDATE api_keys 
            SET requests_made = requests_made + 1, last_used = CURRENT_TIMESTAMP
            WHERE key_hash = ?
        ''', (key_hash,))
        
        conn.commit()
        conn.close()
        
        return {
            "valid": True,
            "user_email": email,
            "plan": plan,
            "requests_remaining": max(0, limit - requests_made - 1) if limit > 0 else "unlimited"
        }
    
    def log_usage(self, key_id, endpoint, ip_address, user_agent):
        """Log API usage for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_usage (key_id, endpoint, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (key_id, endpoint, ip_address, user_agent))
        
        conn.commit()
        conn.close()

# Initialize the API key manager
api_manager = APIKeyManager()

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
        
        if api_key and api_key.startswith('Bearer '):
            api_key = api_key.replace('Bearer ', '')
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": "API key required",
                "code": "MISSING_API_KEY",
                "help": "Include your API key in the X-API-Key header"
            }), 401
        
        # Validate the API key
        validation = api_manager.validate_api_key(api_key)
        
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "error": validation["error"],
                "code": "INVALID_API_KEY"
            }), 401
        
        # Log usage
        api_manager.log_usage(
            api_key[:12], 
            request.endpoint,
            request.remote_addr,
            request.headers.get('User-Agent', '')
        )
        
        # Add user info to request context
        request.api_user = validation
        
        return f(*args, **kwargs)
    
    return decorated_function