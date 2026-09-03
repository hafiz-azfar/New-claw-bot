import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { VideoRoom } from '../components/VideoClassroom/VideoRoom';
import { useLiveSessionStore, useAuthStore } from '../store';
import { liveSessionService } from '../services/api';

export default function ClassroomPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { activeSession, leaveSession } = useLiveSessionStore();
  const { user } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);
  const [serverUrl, setServerUrl] = useState('');
  const [token, setToken] = useState('');
  const [roomName, setRoomName] = useState('');

  useEffect(() => {
    if (!sessionId) {
      navigate('/dashboard');
      return;
    }

    initializeClassroom();

    return () => {
      leaveSession();
    };
  }, [sessionId]);

  const initializeClassroom = async () => {
    try {
      // Join the session and get token
      const tokenData = await liveSessionService.getSessionToken(parseInt(sessionId!));
      
      setServerUrl(tokenData.server_url || import.meta.env.VITE_LIVEKIT_URL || 'ws://localhost:7880');
      setToken(tokenData.token);
      setRoomName(tokenData.room_name);
      
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to initialize classroom:', error);
      navigate('/dashboard');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Joining classroom...</div>
      </div>
    );
  }

  if (!token || !roomName) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">Failed to join classroom</div>
      </div>
    );
  }

  return (
    <VideoRoom
      serverUrl={serverUrl}
      token={token}
      roomName={roomName}
      userRole={user?.role === 'teacher' ? 'teacher' : 'student'}
    />
  );
}
