# backend/apps/accounts/middleware.py
import json
import re
from django.utils import timezone
from .models import UserActivity, CustomUser

class UserActivityMiddleware:
    """
    Middleware to track user activity across the platform
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URL patterns to track specific activities
        self.url_patterns = [
            (r'^/api/stocks/(?P<symbol>[A-Za-z0-9.]+)/$', 'view_stock'),
            (r'^/api/news/(?P<id>\d+)/$', 'view_news'),
            (r'^/api/watchlist/add/$', 'add_to_watchlist'),
            (r'^/api/watchlist/remove/$', 'remove_from_watchlist'),
            (r'^/api/search/$', 'search'),
            (r'^/api/predictions/', 'view_prediction'),
        ]
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Only track authenticated users
        if not request.user.is_authenticated:
            return response
        
        # Update user's last activity timestamp
        if isinstance(request.user, CustomUser):
            request.user.update_last_activity()
        
        # Don't track admin or static file requests
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return response
        
        # Track specific API endpoints
        try:
            self.track_activity(request)
        except Exception as e:
            # Log the error but don't interrupt the response
            print(f"Error tracking user activity: {str(e)}")
        
        return response
    
    def track_activity(self, request):
        """Track user activity based on the request"""
        activity_type = 'other'
        details = {}
        object_id = ''
        content_type = ''
        
        # Try to determine the activity type from the URL
        for pattern, act_type in self.url_patterns:
            match = re.match(pattern, request.path)
            if match:
                activity_type = act_type
                details.update(match.groupdict())
                break
        
        # Track login/logout events
        if request.path.endswith('/login/'):
            activity_type = 'login'
        elif request.path.endswith('/logout/'):
            activity_type = 'logout'
        
        # Get request details based on method
        if request.method == 'GET':
            # For GET requests, capture query parameters
            if request.GET:
                details.update({key: request.GET.get(key) for key in request.GET.keys()})
                
        elif request.method in ['POST', 'PUT', 'PATCH']:
            # For data-modifying requests, try to parse the body
            try:
                if request.body:
                    # Avoid storing sensitive info like passwords
                    body_data = json.loads(request.body.decode('utf-8'))
                    safe_keys = [k for k in body_data.keys() if k.lower() not in ['password', 'token', 'key', 'secret']]
                    details.update({key: body_data.get(key) for key in safe_keys})
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        # Create activity record
        UserActivity.objects.create(
            user=request.user,
            activity_type=activity_type,
            details=details,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=request.session.session_key or '',
            object_id=object_id,
            content_type=content_type
        )
    
    def get_client_ip(self, request):
        """Get the client IP address from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip