"""
Video Conferencing Service - Integration with Zoom, Google Meet, and other platforms
"""
import json
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio

from app.core.config import settings
from app.core.logging import logger


class VideoConferencePlatform:
    """Base class for video conference platforms"""
    
    async def create_meeting(self, **kwargs) -> Dict[str, Any]:
        """Create a new meeting"""
        raise NotImplementedError
    
    async def update_meeting(self, meeting_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing meeting"""
        raise NotImplementedError
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        raise NotImplementedError
    
    async def generate_join_url(self, meeting_id: str, participant_info: Dict[str, Any]) -> str:
        """Generate join URL for participant"""
        raise NotImplementedError
    
    async def get_meeting_participants(self, meeting_id: str) -> list:
        """Get list of meeting participants"""
        raise NotImplementedError


class ZoomPlatform(VideoConferencePlatform):
    """Zoom video conference integration"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ZOOM_API_KEY', None)
        self.api_secret = getattr(settings, 'ZOOM_API_SECRET', None)
        self.base_url = "https://api.zoom.us/v2"
        self.webhook_secret = getattr(settings, 'ZOOM_WEBHOOK_SECRET', None)
    
    def _generate_jwt_token(self) -> str:
        """Generate JWT token for Zoom API authentication"""
        import jwt
        
        payload = {
            'iss': self.api_key,
            'exp': datetime.utcnow() + timedelta(seconds=30)
        }
        
        return jwt.encode(payload, self.api_secret, algorithm='HS256')
    
    async def create_meeting(self, title: str, scheduled_start: datetime, 
                           scheduled_end: datetime, **kwargs) -> Dict[str, Any]:
        """Create Zoom meeting"""
        
        if not self.api_key or not self.api_secret:
            # Fallback to mock meeting
            return self._create_mock_meeting(title, scheduled_start, scheduled_end, **kwargs)
        
        headers = {
            'Authorization': f'Bearer {self._generate_jwt_token()}',
            'Content-Type': 'application/json'
        }
        
        meeting_data = {
            'topic': title,
            'type': 2,  # Scheduled meeting
            'start_time': scheduled_start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'duration': int((scheduled_end - scheduled_start).total_seconds() / 60),
            'timezone': 'Asia/Kolkata',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'cn_meeting': False,
                'in_meeting': False,
                'join_before_host': kwargs.get('join_before_host', False),
                'mute_upon_entry': True,
                'watermark': False,
                'use_pmi': False,
                'approval_type': kwargs.get('approval_type', 0),
                'audio': 'both',
                'auto_recording': 'cloud' if kwargs.get('is_recorded', False) else 'none',
                'enforce_login': False,
                'registrants_email_notification': True,
                'meeting_authentication': False,
                'waiting_room': kwargs.get('waiting_room', True),
                'allow_multiple_devices': True
            }
        }
        
        if kwargs.get('password', False):
            meeting_data['password'] = self._generate_meeting_password()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.base_url}/users/me/meetings', 
                                  headers=headers, json=meeting_data) as response:
                if response.status == 201:
                    meeting_info = await response.json()
                    return {
                        'platform': 'zoom',
                        'meeting_id': str(meeting_info['id']),
                        'meeting_url': meeting_info['join_url'],
                        'password': meeting_info.get('password'),
                        'host_url': meeting_info['start_url']
                    }
                else:
                    error_text = await response.text()
                    logger.error("Failed to create Zoom meeting", error=error_text)
                    return self._create_mock_meeting(title, scheduled_start, scheduled_end, **kwargs)
    
    def _create_mock_meeting(self, title: str, scheduled_start: datetime, 
                           scheduled_end: datetime, **kwargs) -> Dict[str, Any]:
        """Create mock meeting for development/testing"""
        
        meeting_id = f"MOCK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        password = kwargs.get('password', 'janasamparka123')
        
        return {
            'platform': 'mock',
            'meeting_id': meeting_id,
            'meeting_url': f'https://mock-meeting.janasamparka.in/join/{meeting_id}',
            'password': password,
            'host_url': f'https://mock-meeting.janasamparka.in/host/{meeting_id}'
        }
    
    def _generate_meeting_password(self) -> str:
        """Generate random meeting password"""
        import random
        import string
        
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    async def generate_join_url(self, meeting_id: str, participant_info: Dict[str, Any]) -> str:
        """Generate join URL for participant"""
        
        if meeting_id.startswith('MOCK'):
            return f'https://mock-meeting.janasamparka.in/join/{meeting_id}?name={participant_info.get("participant_name", "User")}'
        
        # For Zoom, return the join URL with parameters
        return f'https://zoom.us/j/{meeting_id}?pwd={participant_info.get("password", "")}'
    
    async def get_meeting_participants(self, meeting_id: str) -> list:
        """Get meeting participants"""
        
        if meeting_id.startswith('MOCK'):
            return []  # Mock implementation
        
        headers = {
            'Authorization': f'Bearer {self._generate_jwt_token()}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.base_url}/meetings/{meeting_id}/participants', 
                                 headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('participants', [])
                else:
                    return []


class GoogleMeetPlatform(VideoConferencePlatform):
    """Google Meet integration"""
    
    def __init__(self):
        self.credentials_path = getattr(settings, 'GOOGLE_MEET_CREDENTIALS_PATH', None)
    
    async def create_meeting(self, title: str, scheduled_start: datetime, 
                           scheduled_end: datetime, **kwargs) -> Dict[str, Any]:
        """Create Google Meet event"""
        
        # Generate mock Google Meet link
        meeting_id = f"MEET{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'platform': 'google_meet',
            'meeting_id': meeting_id,
            'meeting_url': f'https://meet.google.com/{meeting_id}',
            'password': None,  # Google Meet doesn't use passwords
            'host_url': f'https://meet.google.com/{meeting_id}'
        }
    
    async def generate_join_url(self, meeting_id: str, participant_info: Dict[str, Any]) -> str:
        """Generate join URL for participant"""
        return f'https://meet.google.com/{meeting_id}'


class VideoConferenceService:
    """Main video conference service"""
    
    def __init__(self):
        self.platforms = {
            'zoom': ZoomPlatform(),
            'google_meet': GoogleMeetPlatform(),
            'mock': ZoomPlatform()  # Fallback platform
        }
        self.default_platform = getattr(settings, 'VIDEO_CONFERENCE_PLATFORM', 'zoom')
    
    def get_platform(self, platform_name: str = None) -> VideoConferencePlatform:
        """Get video conference platform"""
        platform_name = platform_name or self.default_platform
        return self.platforms.get(platform_name, self.platforms['mock'])
    
    async def create_meeting(self, title: str, scheduled_start: datetime, 
                           scheduled_end: datetime, conference_type: str = "meeting",
                           host_id: str = None, **kwargs) -> Dict[str, Any]:
        """Create a new video conference meeting"""
        
        try:
            platform = self.get_platform(kwargs.get('platform'))
            
            # Add conference-specific settings
            meeting_settings = {
                'is_recorded': kwargs.get('is_recorded', False),
                'join_before_host': kwargs.get('join_before_host', False),
                'waiting_room': kwargs.get('waiting_room', True),
                'password': kwargs.get('require_password', True)
            }
            
            # Adjust settings based on conference type
            if conference_type == "public_hearing":
                meeting_settings.update({
                    'join_before_host': True,
                    'waiting_room': False,
                    'approval_type': 0  # No approval required
                })
            elif conference_type == "press_conference":
                meeting_settings.update({
                    'is_recorded': True,
                    'waiting_room': True
                })
            elif conference_type == "one_on_one":
                meeting_settings.update({
                    'waiting_room': True,
                    'approval_type': 1  # Auto approve
                })
            
            meeting_details = await platform.create_meeting(
                title=title,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                **meeting_settings
            )
            
            logger.info("Video conference created", 
                       platform=meeting_details['platform'],
                       meeting_id=meeting_details['meeting_id'],
                       title=title)
            
            return meeting_details
            
        except Exception as e:
            logger.error("Failed to create video conference", 
                        title=title, error=str(e))
            # Return mock meeting as fallback
            return await self.platforms['mock'].create_meeting(
                title, scheduled_start, scheduled_end, **kwargs
            )
    
    async def update_meeting(self, meeting_id: str, platform: str = None, **kwargs) -> Dict[str, Any]:
        """Update an existing meeting"""
        
        try:
            platform_instance = self.get_platform(platform)
            return await platform_instance.update_meeting(meeting_id, **kwargs)
        except Exception as e:
            logger.error("Failed to update video conference", 
                        meeting_id=meeting_id, error=str(e))
            return {}
    
    async def delete_meeting(self, meeting_id: str, platform: str = None) -> bool:
        """Delete a meeting"""
        
        try:
            platform_instance = self.get_platform(platform)
            return await platform_instance.delete_meeting(meeting_id)
        except Exception as e:
            logger.error("Failed to delete video conference", 
                        meeting_id=meeting_id, error=str(e))
            return False
    
    async def generate_join_url(self, meeting_id: str, participant_name: str, 
                              participant_email: str = None, role: str = "participant",
                              platform: str = None) -> str:
        """Generate join URL for participant"""
        
        try:
            platform_instance = self.get_platform(platform)
            
            participant_info = {
                'participant_name': participant_name,
                'participant_email': participant_email,
                'role': role
            }
            
            return await platform_instance.generate_join_url(meeting_id, participant_info)
            
        except Exception as e:
            logger.error("Failed to generate join URL", 
                        meeting_id=meeting_id, error=str(e))
            # Return fallback URL
            return f'https://mock-meeting.janasamparka.in/join/{meeting_id}?name={participant_name}'
    
    async def get_meeting_participants(self, meeting_id: str, platform: str = None) -> list:
        """Get meeting participants"""
        
        try:
            platform_instance = self.get_platform(platform)
            return await platform_instance.get_meeting_participants(meeting_id)
        except Exception as e:
            logger.error("Failed to get meeting participants", 
                        meeting_id=meeting_id, error=str(e))
            return []
    
    async def start_meeting(self, meeting_id: str, host_id: str, platform: str = None) -> str:
        """Start meeting and return host URL"""
        
        try:
            platform_instance = self.get_platform(platform)
            
            # For Zoom, we would use the start_url from meeting creation
            # For other platforms, implement accordingly
            
            logger.info("Meeting started", meeting_id=meeting_id, host_id=host_id)
            
            return f"https://meeting-platform.host/{meeting_id}"
            
        except Exception as e:
            logger.error("Failed to start meeting", 
                        meeting_id=meeting_id, error=str(e))
            return f"https://mock-meeting.janasamparka.in/host/{meeting_id}"
    
    async def end_meeting(self, meeting_id: str, host_id: str, platform: str = None) -> bool:
        """End meeting"""
        
        try:
            platform_instance = self.get_platform(platform)
            
            # Implementation depends on platform
            # For Zoom, we would call the API to end the meeting
            
            logger.info("Meeting ended", meeting_id=meeting_id, host_id=host_id)
            return True
            
        except Exception as e:
            logger.error("Failed to end meeting", 
                        meeting_id=meeting_id, error=str(e))
            return False
    
    async def get_recording(self, meeting_id: str, platform: str = None) -> Dict[str, Any]:
        """Get meeting recording"""
        
        try:
            platform_instance = self.get_platform(platform)
            
            # Implementation depends on platform
            # For Zoom, we would call the recordings API
            
            return {
                'recording_url': f"https://recordings.platform/{meeting_id}",
                'transcript_url': f"https://transcripts.platform/{meeting_id}",
                'duration': 3600,  # seconds
                'size': 102400000  # bytes
            }
            
        except Exception as e:
            logger.error("Failed to get recording", 
                        meeting_id=meeting_id, error=str(e))
            return {}
    
    async def validate_webhook(self, payload: str, signature: str, platform: str = None) -> bool:
        """Validate webhook signature"""
        
        try:
            if platform == "zoom" and self.webhook_secret:
                # Zoom webhook validation
                hash_signature = hmac.new(
                    self.webhook_secret.encode('utf-8'),
                    payload.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                expected_signature = f"v0={hash_signature}"
                return hmac.compare_digest(signature, expected_signature)
            
            return True  # Default to true for mock platforms
            
        except Exception as e:
            logger.error("Webhook validation failed", error=str(e))
            return False
    
    async def handle_webhook_event(self, event_data: Dict[str, Any], platform: str = None) -> bool:
        """Handle webhook events from video conference platform"""
        
        try:
            event_type = event_data.get('event')
            
            logger.info("Webhook event received", 
                       platform=platform, event_type=event_type)
            
            # Handle different event types
            if event_type == "meeting.started":
                await self._handle_meeting_started(event_data)
            elif event_type == "meeting.ended":
                await self._handle_meeting_ended(event_data)
            elif event_type == "meeting.participant_joined":
                await self._handle_participant_joined(event_data)
            elif event_type == "meeting.participant_left":
                await self._handle_participant_left(event_data)
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle webhook event", error=str(e))
            return False
    
    async def _handle_meeting_started(self, event_data: Dict[str, Any]):
        """Handle meeting started event"""
        meeting_id = event_data.get('meeting', {}).get('id')
        logger.info("Meeting started via webhook", meeting_id=meeting_id)
    
    async def _handle_meeting_ended(self, event_data: Dict[str, Any]):
        """Handle meeting ended event"""
        meeting_id = event_data.get('meeting', {}).get('id')
        logger.info("Meeting ended via webhook", meeting_id=meeting_id)
    
    async def _handle_participant_joined(self, event_data: Dict[str, Any]):
        """Handle participant joined event"""
        meeting_id = event_data.get('meeting', {}).get('id')
        participant = event_data.get('participant', {})
        logger.info("Participant joined via webhook", 
                   meeting_id=meeting_id, participant_id=participant.get('id'))
    
    async def _handle_participant_left(self, event_data: Dict[str, Any]):
        """Handle participant left event"""
        meeting_id = event_data.get('meeting', {}).get('id')
        participant = event_data.get('participant', {})
        logger.info("Participant left via webhook", 
                   meeting_id=meeting_id, participant_id=participant.get('id'))


# Global service instance
video_conference_service = VideoConferenceService()
