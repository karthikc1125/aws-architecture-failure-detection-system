"""
Authentication and authorization middleware
- API key validation
- User identification
- Permission checks
- Token management
"""

import logging
import hashlib
import secrets
from typing import Optional, Dict, List, Set
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from functools import wraps
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# AUTHENTICATION
# ============================================================================

class UserRole(Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    POWER_USER = "power_user"
    USER = "user"
    GUEST = "guest"


class AuthUser:
    """Authenticated user context"""
    
    def __init__(self, user_id: str, api_key: str, role: UserRole = UserRole.USER):
        self.user_id = user_id
        self.api_key = api_key
        self.role = role
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def is_expired(self, ttl_hours: int = 24) -> bool:
        """Check if session is expired"""
        return (datetime.now() - self.created_at).total_seconds() > ttl_hours * 3600


class AuthManager:
    """Manage authentication and user sessions"""
    
    def __init__(self):
        self.users: Dict[str, AuthUser] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id
        self._init_default_users()
        logger.info("AuthManager initialized with default users")
    
    def _init_default_users(self):
        """Initialize default admin and test users"""
        # Admin user
        admin_key = self._generate_api_key()
        self.users["admin"] = AuthUser("admin", admin_key, UserRole.ADMIN)
        self.api_keys[admin_key] = "admin"
        
        # Test/Demo user
        demo_key = self._generate_api_key()
        self.users["demo"] = AuthUser("demo", demo_key, UserRole.USER)
        self.api_keys[demo_key] = "demo"
        
        logger.info(f"Default users created - Admin Key: {admin_key[:10]}... | Demo Key: {demo_key[:10]}...")
    
    def _generate_api_key(self, prefix: str = "ak_") -> str:
        """Generate a secure API key"""
        return prefix + secrets.token_urlsafe(32)
    
    def create_user(self, user_id: str, role: UserRole = UserRole.USER) -> str:
        """Create a new user and return their API key"""
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        api_key = self._generate_api_key()
        self.users[user_id] = AuthUser(user_id, api_key, role)
        self.api_keys[api_key] = user_id
        
        logger.info(f"User created: {user_id} (role: {role.value})")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[AuthUser]:
        """Validate API key and return user"""
        if api_key not in self.api_keys:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            return None
        
        user_id = self.api_keys[api_key]
        user = self.users.get(user_id)
        
        if not user or not user.is_active:
            logger.warning(f"Inactive user attempted access: {user_id}")
            return None
        
        if user.is_expired():
            user.is_active = False
            logger.warning(f"Session expired for user: {user_id}")
            return None
        
        user.update_activity()
        return user
    
    def revoke_user(self, user_id: str):
        """Revoke a user's access"""
        if user_id in self.users:
            self.users[user_id].is_active = False
            logger.info(f"User revoked: {user_id}")
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        active_users = sum(1 for u in self.users.values() if u.is_active)
        return {
            "total_users": len(self.users),
            "active_users": active_users,
            "inactive_users": len(self.users) - active_users,
        }


# ============================================================================
# AUTHORIZATION
# ============================================================================

class PermissionManager:
    """Manage user permissions and RBAC"""
    
    # Define permissions per role
    ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
        UserRole.ADMIN: {
            "analyze:deployed",
            "analyze:fresh",
            "analyze:validate",
            "admin:view_stats",
            "admin:create_user",
            "admin:revoke_user",
        },
        UserRole.POWER_USER: {
            "analyze:deployed",
            "analyze:fresh",
            "analyze:validate",
            "admin:view_stats",
        },
        UserRole.USER: {
            "analyze:deployed",
            "analyze:fresh",
        },
        UserRole.GUEST: {
            "analyze:validate",
        }
    }
    
    @staticmethod
    def has_permission(user: AuthUser, permission: str) -> bool:
        """Check if user has permission"""
        permissions = PermissionManager.ROLE_PERMISSIONS.get(user.role, set())
        return permission in permissions
    
    @staticmethod
    def require_permission(permission: str):
        """Decorator to require permission"""
        async def permission_check(request: Request):
            user = getattr(request.state, "user", None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            if not PermissionManager.has_permission(user, permission):
                logger.warning(f"Permission denied for {user.user_id}: {permission}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}"
                )
        
        return permission_check


# ============================================================================
# MIDDLEWARE
# ============================================================================

class AuthenticationMiddleware:
    """Middleware for API key authentication"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
    
    async def __call__(self, request: Request, call_next):
        """Process authentication"""
        
        # Allow health check without auth
        if request.url.path == "/health":
            return await call_next(request)
        
        # Allow static files without auth
        if request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Allow root pages without auth (for UI)
        if request.url.path in ["/", "/analyze", "/methodology", "/settings"]:
            return await call_next(request)
        
        # Require API key for API endpoints
        if request.url.path.startswith("/api"):
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            
            if not api_key:
                logger.warning(f"Missing API key: {request.url.path} from {request.client}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing API key (X-API-Key header or ?api_key param)"}
                )
            
            user = self.auth_manager.validate_api_key(api_key)
            if not user:
                logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired API key"}
                )
            
            request.state.user = user
        
        response = await call_next(request)
        return response


# ============================================================================
# AUDIT LOGGING
# ============================================================================

@dataclass
class AuditLog:
    """Audit log entry"""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    status: str
    details: Dict = None
    

class AuditLogger:
    """Log all significant actions for compliance"""
    
    def __init__(self):
        self.logs: List[AuditLog] = []
    
    def log_action(self, user_id: str, action: str, resource: str, status: str = "success", details: Dict = None):
        """Log an action"""
        from dataclasses import dataclass
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {}
        }
        self.logs.append(log_entry)
        
        logger.info(f"[AUDIT] {user_id} - {action}:{resource} - {status}")
    
    def get_logs(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve audit logs"""
        logs = self.logs
        if user_id:
            logs = [l for l in logs if l["user_id"] == user_id]
        return logs[-limit:]


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

auth_manager = AuthManager()
permission_manager = PermissionManager()
audit_logger = AuditLogger()


# ============================================================================
# JSON RESPONSE (imported helper)
# ============================================================================

from fastapi.responses import JSONResponse
