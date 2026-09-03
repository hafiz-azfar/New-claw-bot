"""
LiveKit integration service for Al-Uloom Academy.
Provides superior video conferencing to beat Zoom/MS Teams.
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from livekit import api as lkapi


class LiveKitService:
    """
    Service for interacting with LiveKit SFU.
    Features that beat Zoom/Teams:
    - Self-hosted (data sovereignty)
    - Unlimited session duration
    - Auto-recording with Egress
    - Lower latency (<500ms)
    - Better scalability (SFU architecture)
    - No per-host pricing
    """

    def __init__(self):
        self.url = settings.LIVEKIT_URL
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        
        if self.api_key and self.api_secret:
            self.client = lkapi.LiveKitAPI(
                self.url,
                self.api_key,
                self.api_secret
            )
        else:
            self.client = None

    def create_room(self, room_name: str, metadata: dict = None) -> dict:
        """
        Create a LiveKit room for a session.
        
        Args:
            room_name: Unique room identifier
            metadata: Optional room metadata
            
        Returns:
            Room configuration dict
        """
        if not self.client:
            # Mock mode for development
            return {
                'name': room_name,
                'url': self.url,
                'metadata': metadata or {}
            }
        
        try:
            room = lkapi.CreateRoomRequest(
                name=room_name,
                empty_timeout=300,  # 5 minutes
                max_participants=100,
                metadata=metadata or {}
            )
            
            created_room = self.client.room.create_room(room)
            
            return {
                'name': created_room.name,
                'sid': created_room.sid,
                'url': self.url,
                'metadata': created_room.metadata
            }
        except Exception as e:
            raise Exception(f"Failed to create LiveKit room: {str(e)}")

    def generate_token(
        self, 
        room_name: str, 
        user_id: str, 
        user_name: str,
        role: str = 'subscriber',
        can_publish: bool = True,
        can_subscribe: bool = True,
        expiry_minutes: int = 60
    ) -> str:
        """
        Generate a JWT token for joining a LiveKit room.
        
        Args:
            room_name: Room to join
            user_id: User identifier
            user_name: Display name
            role: 'publisher' (teacher) or 'subscriber' (student)
            can_publish: Can publish audio/video
            can_subscribe: Can subscribe to others' streams
            expiry_minutes: Token validity period
            
        Returns:
            JWT token string
        """
        if not self.api_secret:
            # Mock token for development
            return f"mock_token_{user_id}_{room_name}"
        
        # Set permissions based on role
        if role == 'publisher':
            # Teacher: full publishing rights
            video_track = lkapi.VideoTrack(name='camera')
            audio_track = lkapi.AudioTrack(name='microphone')
            
            grant = lkapi.VideoGrant(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
                hidden=False,
                recorder=False,
            )
        else:
            # Student: limited publishing (audio only for questions)
            grant = lkapi.VideoGrant(
                room_join=True,
                room=room_name,
                can_publish=can_publish,  # Usually True for audio
                can_subscribe=True,
                can_publish_data=True,
                hidden=False,
                recorder=False,
            )
        
        # Create token
        token = lkapi.AccessToken(self.api_key, self.api_secret)
        token.with_grant(grant)
        token.with_identity(user_id)
        token.with_name(user_name)
        token.with_ttl(timedelta(minutes=expiry_minutes))
        
        return token.to_jwt()

    async def start_recording(self, room_name: str, session_id: str) -> dict:
        """
        Start recording a LiveKit room using Egress.
        
        Args:
            room_name: Room to record
            session_id: Session identifier for file naming
            
        Returns:
            Egress info dict
        """
        if not self.client:
            return {'egress_id': f'mock_egress_{session_id}'}
        
        try:
            # Configure S3 output (MinIO)
            s3_output = lkapi.S3FileOutput(
                bucket=settings.MINIO_BUCKET,
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret=settings.MINIO_SECRET_KEY,
                filepath=f'recordings/{session_id}/{{time}}.m3u8',
            )
            
            # Create room composite egress (records all participants)
            request = lkapi.RoomCompositeEgressRequest(
                room_name=room_name,
                file_outputs=[s3_output],
                layout='speaker-light',  # Professional layout
                audio_only=False,
            )
            
            egress_info = await self.client.egress.start_room_composite_egress(request)
            
            return {
                'egress_id': egress_info.egress_id,
                'status': 'starting',
                'room_name': room_name
            }
        except Exception as e:
            raise Exception(f"Failed to start recording: {str(e)}")

    async def stop_recording(self, egress_id: str) -> dict:
        """
        Stop an ongoing recording.
        
        Args:
            egress_id: Egress ID to stop
            
        Returns:
            Updated egress info
        """
        if not self.client:
            return {'egress_id': egress_id, 'status': 'stopped'}
        
        try:
            egress_info = await self.client.egress.stop_egress(
                lkapi.StopEgressRequest(egress_id=egress_id)
            )
            
            return {
                'egress_id': egress_info.egress_id,
                'status': 'ending'
            }
        except Exception as e:
            raise Exception(f"Failed to stop recording: {str(e)}")

    async def get_room_info(self, room_name: str) -> dict:
        """Get information about a room."""
        if not self.client:
            return {'name': room_name, 'participants': []}
        
        try:
            room = await self.client.room.get_room(lkapi.GetRoomRequest(name=room_name))
            participants = await self.client.room.list_participants(
                lkapi.ListParticipantsRequest(room=room_name)
            )
            
            return {
                'name': room.name,
                'sid': room.sid,
                'participant_count': room.num_participants,
                'participants': [
                    {
                        'identity': p.identity,
                        'name': p.name,
                        'state': p.state,
                        'joined_at': p.joined_at
                    }
                    for p in participants.participants
                ]
            }
        except Exception:
            return {'name': room_name, 'exists': False}

    async def delete_room(self, room_name: str) -> bool:
        """Delete a room (force disconnect all participants)."""
        if not self.client:
            return True
        
        try:
            await self.client.room.delete_room(lkapi.DeleteRoomRequest(room=room_name))
            return True
        except Exception:
            return False

    @staticmethod
    def get_webhook_verification_token() -> str:
        """Get the webhook verification token from settings."""
        return getattr(settings, 'LIVEKIT_WEBHOOK_TOKEN', '')


# Singleton instance
livekit_service = LiveKitService()
