"""
Account app serializers module.

This module defines serializers for the account app models used to convert
complex data types to native Python datatypes that can be easily rendered
into JSON or other content types. It handles user, watchlist, user preferences,
and activity data serialization.

Key serializers:
- UserSerializer: Handles user registration, profile management
- WatchlistSerializer: Manages user stock watchlists 
- UserPreferenceSerializer: Handles user preferences and settings
- UserActivitySerializer: Tracks user activity for analytics
- StockInteractionSerializer: Records user interactions with stocks
"""

# backend/apps/accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Watchlist, WatchlistItem, UserPreference, UserActivity, StockInteraction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom user model.
    
    Handles user creation, update, and detail representation with password hashing.
    Provides special handling for the 'name' field from frontend that maps to
    first_name in the backend model.
    
    Attributes:
        password: Write-only field for user password
        name: Write-only field for combined user name
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    name = serializers.CharField(required=False, write_only=True)  # For handling the 'name' field from the frontend
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'name', 'first_name', 'last_name', 
                 'profile_picture', 'bio', 'date_of_birth', 'phone_number',
                 'dark_mode', 'notification_enabled', 'last_activity', 'login_count']
        read_only_fields = ['id', 'last_activity', 'login_count']
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        
        Handles the creation of a new user with proper password hashing and
        generates a username from email if not provided. Maps the 'name' field
        to first_name if applicable.
        
        Args:
            validated_data: Dictionary of validated user data
            
        Returns:
            User: The newly created user instance
        """
        # Extract 'name' field if present
        name = validated_data.pop('name', None)
        
        # If username is not provided, generate one from email
        if 'username' not in validated_data or not validated_data['username']:
            email = validated_data.get('email', '')
            username = email.split('@')[0] if '@' in email else 'user'
            
            # Make sure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            validated_data['username'] = username
        
        # If name is provided but first_name isn't, use name as first_name
        if name and 'first_name' not in validated_data:
            validated_data['first_name'] = name
            
        # Get the password from validated_data
        password = validated_data.pop('password')
        
        # Create user without password
        user = User.objects.create(**validated_data)
        
        # Set password separately to ensure it's hashed
        user.set_password(password)
        user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """
        Update a user, setting the password correctly if needed.
        
        Handles user profile updates with special handling for the password field
        to ensure proper hashing and the 'name' field mapping to first_name.
        
        Args:
            instance: The user instance to update
            validated_data: Dictionary of validated user data
            
        Returns:
            User: The updated user instance
        """
        # Handle 'name' field if present
        name = validated_data.pop('name', None)
        if name and 'first_name' not in validated_data:
            validated_data['first_name'] = name
            
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user

class WatchlistItemSerializer(serializers.ModelSerializer):
    """
    Serializer for watchlist items.
    
    Represents stock symbols that are part of a user's watchlist.
    
    Attributes:
        id: The watchlist item's unique identifier
        watchlist: The ID of the parent watchlist
        symbol: The stock symbol (e.g., AAPL, MSFT)
        added_at: Timestamp when the item was added
        notes: Optional user notes about the stock
    """
    class Meta:
        model = WatchlistItem
        fields = ['id', 'watchlist', 'symbol', 'added_at', 'notes']
        read_only_fields = ['id', 'added_at']

class WatchlistSerializer(serializers.ModelSerializer):
    """
    Serializer for watchlists.
    
    Represents a collection of stocks that a user is watching, with nested
    representation of the watchlist items.
    
    Attributes:
        items: Nested serializer for watchlist items
        is_default: Whether this is the user's default watchlist
    """
    items = WatchlistItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'items', 'is_default']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences.
    
    Handles user-specific settings and preferences for the application.
    
    Attributes:
        preferred_news_categories: User's preferred categories for news
        email_notifications: Whether email notifications are enabled
        sms_notifications: Whether SMS notifications are enabled
        price_alert_threshold: Threshold percentage for price change alerts
    """
    class Meta:
        model = UserPreference
        fields = ['id', 'preferred_news_categories', 'email_notifications', 
                  'sms_notifications', 'price_alert_threshold']
        read_only_fields = ['id']

class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity logs.
    
    Tracks and represents user actions within the application for analytics
    and user behavior tracking.
    
    Attributes:
        username: The user's username (derived from related user)
        activity_type_display: Human-readable activity type
    """
    username = serializers.CharField(source='user.username', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ['id', 'username', 'user', 'activity_type', 'activity_type_display', 
                  'timestamp', 'details', 'ip_address', 'user_agent', 'session_id',
                  'object_id', 'content_type']
        read_only_fields = ['id', 'username', 'user', 'timestamp', 'ip_address', 
                           'user_agent', 'session_id']

class StockInteractionSerializer(serializers.ModelSerializer):
    """
    Serializer for user's stock interactions.
    
    Tracks and represents how users interact with specific stocks, including
    view counts, search counts, and favorites.
    
    Attributes:
        username: The user's username (derived from related user)
        view_count: Number of times the user has viewed this stock
        search_count: Number of times the user has searched for this stock
        is_favorite: Whether the user has marked this stock as a favorite
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StockInteraction
        fields = ['id', 'username', 'user', 'symbol', 'view_count', 'last_viewed', 
                  'search_count', 'last_searched', 'total_view_time', 'is_favorite', 'notes']
        read_only_fields = ['id', 'username', 'user', 'view_count', 'last_viewed', 
                           'search_count', 'last_searched', 'total_view_time']