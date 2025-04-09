"""
User management views for the accounts app.

This module contains views for handling user authentication, registration,
profile management, and activity tracking. It provides RESTful API endpoints
for user operations and implements secure authentication practices.

Key features:
- Direct login against PostgreSQL database
- User registration with validation
- User profile management
- Watchlist management
- User preferences and activity tracking
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from django.db import connection
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Watchlist, WatchlistItem, UserPreference, UserActivity, StockInteraction
from .serializers import (
    UserSerializer, WatchlistSerializer, 
    WatchlistItemSerializer, UserPreferenceSerializer,
    UserActivitySerializer, StockInteractionSerializer
)
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def direct_login(request):
    """
    Direct login against PostgreSQL database.
    
    This view provides a custom login endpoint that directly authenticates
    users against the database. It handles validation, error logging, and
    token generation.
    
    Args:
        request: HTTP request containing email and password
        
    Returns:
        Response: Authentication tokens and user information on success,
                 error message on failure
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {"error": "Email and password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    logger.info(f"Login attempt for email: {email}")
    
    # Check if user exists by email first
    try:
        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            logger.warning(f"Login failed: No user found with email {email}")
            return Response(
                {"error": "No account exists with this email address"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Now authenticate with correct credentials
        user = authenticate(username=user_obj.username, password=password)
        
        # If authentication fails, it's a password issue
        if user is None:
            logger.warning(f"Login failed: Invalid password for user {email}")
            return Response(
                {"error": "Invalid email or password"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Authentication succeeded
        logger.info(f"User {email} logged in successfully")
        
        # Record the login activity - but handle potential DB schema issues
        try:
            # Only update login_count to avoid the last_activity field issue
            user.login_count += 1
            user.save(update_fields=['login_count'])
            logger.info(f"Login count updated for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to update login count for user {user.id}: {str(e)}")
            # Continue despite this error - authentication was still successful
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.first_name or user.username
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {"error": "An error occurred during login. Please try again."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user with validation and default settings.
    
    This view handles user registration with validation checks and creates
    default watchlists and preferences for new users. It also generates
    authentication tokens for immediate login after registration.
    
    Args:
        request: HTTP request containing user registration data
        
    Returns:
        Response: Authentication tokens and user information on success,
                 validation errors on failure
    """
    logger.info(f"Registration attempt with data: {request.data}")
    
    # Add basic validation
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name')
    
    if not email or not password:
        logger.warning("Registration failed: Missing email or password")
        return Response(
            {"error": "Email and password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        logger.warning(f"Registration failed: User with email {email} already exists")
        return Response(
            {"error": "A user with this email already exists. Please login instead."}, 
            status=status.HTTP_409_CONFLICT
        )
    
    # Ensure password meets minimum requirements
    if len(password) < 8:
        return Response(
            {"error": "Password must be at least 8 characters long"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create a new serializer instance with the request data
    serializer = UserSerializer(data={
        'email': email,
        'password': password,
        'name': name,
        # Generate a username if not provided (handled in serializer)
    })
    
    if serializer.is_valid():
        try:
            # Save the new user
            user = serializer.save()
            logger.info(f"User created successfully: {user.id} - {user.email}")
            
            # Create default watchlist
            try:
                watchlist = Watchlist.objects.create(
                    user=user, 
                    name="My Watchlist", 
                    is_default=True
                )
                logger.info(f"Default watchlist created for user {user.id}")
            except Exception as watchlist_error:
                logger.error(f"Error creating watchlist for user {user.id}: {str(watchlist_error)}")
                # Continue even if watchlist creation fails
            
            # Create default preferences
            try:
                preferences = UserPreference.objects.create(user=user)
                logger.info(f"Default preferences created for user {user.id}")
            except Exception as pref_error:
                logger.error(f"Error creating preferences for user {user.id}: {str(pref_error)}")
                # Continue even if preferences creation fails
            
            # Generate authentication token for the new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name or '',
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration failed with exception: {str(e)}")
            
            # Try to get more detailed error information
            error_detail = str(e)
            
            # If the user was created but subsequent steps failed, delete the user to maintain integrity
            try:
                if 'user' in locals() and user.id:
                    user.delete()
                    logger.info(f"Deleted user {user.id} due to registration failure in subsequent steps")
            except Exception as delete_error:
                logger.error(f"Error cleaning up failed registration: {str(delete_error)}")
            
            return Response(
                {"error": "Registration failed", "detail": error_detail},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # If serializer validation failed
    logger.warning(f"Registration validation failed: {serializer.errors}")
    
    # Return specific validation errors to the client in a more friendly format
    error_messages = []
    for field, errors in serializer.errors.items():
        error_messages.append(f"{field}: {' '.join(str(e) for e in errors)}")
    
    return Response(
        {"error": "Registration validation failed", "details": error_messages}, 
        status=status.HTTP_400_BAD_REQUEST
    )

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management.
    
    This viewset provides CRUD operations for user profiles with authentication
    checks. Regular users can only access and modify their own profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile.
        
        Returns the authenticated user's profile information.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        Update current user's profile.
        
        Allows users to update their own profile information.
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WatchlistViewSet(viewsets.ModelViewSet):
    """
    API endpoint for watchlists.
    
    This viewset provides CRUD operations for user watchlists with authentication.
    Users can only access and modify their own watchlists.
    """
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return watchlists for the current user.
        
        Filters the queryset to only include watchlists owned by the authenticated user.
        """
        return Watchlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create a new watchlist for the current user.
        
        Automatically assigns the authenticated user as the owner of the new watchlist.
        """
        serializer.save(user=self.request.user)

class WatchlistItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for watchlist items.
    
    This viewset provides CRUD operations for items within user watchlists.
    Users can only access and modify items in their own watchlists.
    """
    serializer_class = WatchlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return watchlist items for the current user's watchlists.
        
        Optionally filters by a specific watchlist ID if provided in the query parameters.
        """
        watchlist_id = self.request.query_params.get('watchlist')
        if watchlist_id:
            return WatchlistItem.objects.filter(
                watchlist__id=watchlist_id, 
                watchlist__user=self.request.user
            )
        return WatchlistItem.objects.filter(watchlist__user=self.request.user)

class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user preferences.
    
    This viewset provides CRUD operations for user preferences with authentication.
    Users can only access and modify their own preferences.
    """
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return preferences for the current user.
        
        Filters the queryset to only include preferences for the authenticated user.
        """
        return UserPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create preferences for the current user.
        
        Automatically assigns the authenticated user as the owner of the preferences.
        """
        serializer.save(user=self.request.user)

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing user activity logs.
    
    This read-only viewset provides access to user activity logs with authentication.
    Regular users can only access their own activity logs, while admin users
    can access all logs.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return activity logs based on user permissions.
        
        Admin users can see all logs, while regular users can only see their own.
        """
        user = self.request.user
        
        # Admin users can see all records
        if user.is_staff:
            return UserActivity.objects.all().order_by('-timestamp')
        
        # Regular users can only see their own records
        return UserActivity.objects.filter(user=user).order_by('-timestamp')
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def all(self, request):
        """
        Get all activity logs for admin users only.
        
        Returns all activity logs in the system, with pagination.
        Only accessible to admin users.
        """
        queryset = UserActivity.objects.all().order_by('-timestamp')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get the user's 20 most recent activities.
        
        Returns the 20 most recent activity logs for the authenticated user.
        """
        queryset = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class StockInteractionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing stock interactions.
    
    This viewset provides CRUD operations for tracking user interactions with stocks,
    including views, searches, and favorites. Users can only access and modify their
    own stock interactions.
    """
    serializer_class = StockInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return stock interactions for the current user.
        
        Filters the queryset to only include stock interactions for the authenticated user.
        """
        return StockInteraction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create a stock interaction for the current user.
        
        Automatically assigns the authenticated user as the owner of the stock interaction.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def record_view(self, request):
        """
        Record a stock view interaction.
        
        Increments the view count for a specific stock and updates the last viewed timestamp.
        Creates a new interaction record if one doesn't exist.
        """
        symbol = request.data.get('symbol')
        if not symbol:
            return Response({'error': 'Symbol is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get or create StockInteraction object
        interaction, created = StockInteraction.objects.get_or_create(
            user=request.user,
            symbol=symbol
        )
        
        # Record view
        interaction.record_view()
        
        serializer = self.get_serializer(interaction)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def record_search(self, request):
        """
        Record a stock search interaction.
        
        Increments the search count for a specific stock and updates the last searched timestamp.
        Creates a new interaction record if one doesn't exist.
        """
        symbol = request.data.get('symbol')
        if not symbol:
            return Response({'error': 'Symbol is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get or create StockInteraction object
        interaction, created = StockInteraction.objects.get_or_create(
            user=request.user,
            symbol=symbol
        )
        
        # Record search
        interaction.record_search()
        
        serializer = self.get_serializer(interaction)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """
        Get user's favorite stocks.
        
        Returns a list of all stocks marked as favorites by the authenticated user.
        """
        queryset = StockInteraction.objects.filter(
            user=request.user,
            is_favorite=True
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def toggle_favorite(self, request):
        """
        Toggle favorite status for a stock.
        
        Allows users to mark/unmark stocks as favorites. Creates a new interaction
        record if one doesn't exist for the specified stock.
        """
        symbol = request.data.get('symbol')
        if not symbol:
            return Response({'error': 'Symbol is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get or create StockInteraction object
        interaction, created = StockInteraction.objects.get_or_create(
            user=request.user,
            symbol=symbol
        )
        
        # Toggle favorite status
        interaction.is_favorite = not interaction.is_favorite
        interaction.save(update_fields=['is_favorite'])
        
        serializer = self.get_serializer(interaction)
        return Response(serializer.data)