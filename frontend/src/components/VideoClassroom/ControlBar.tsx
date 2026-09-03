import { useLocalParticipant } from '@livekit/components-react';
import { useLiveSessionStore, useUIStore } from '../../store';

interface ControlBarProps {
  userRole: 'teacher' | 'student';
}

export function ControlBar({ userRole }: ControlBarProps) {
  const { isRecording, toggleRecording, launchMCQ } = useLiveSessionStore();
  const { toggleChat, toggleParticipants } = useUIStore();
  const localParticipant = useLocalParticipant();

  return (
    <div className="control-bar">
      {/* Mic Toggle */}
      <button 
        onClick={() => localParticipant?.setMicrophoneEnabled(!localParticipant.isMicrophoneEnabled)}
        className={`btn-control ${localParticipant?.isMicrophoneEnabled ? 'btn-primary' : 'btn-danger'}`}
      >
        {localParticipant?.isMicrophoneEnabled ? '🎤 Mic On' : '🔇 Mic Off'}
      </button>

      {/* Camera Toggle */}
      <button 
        onClick={() => localParticipant?.setCameraEnabled(!localParticipant.isCameraEnabled)}
        className={`btn-control ${localParticipant?.isCameraEnabled ? 'btn-primary' : 'btn-danger'}`}
      >
        {localParticipant?.isCameraEnabled ? '📹 Cam On' : '📷 Cam Off'}
      </button>

      {/* Teacher Only Controls */}
      {userRole === 'teacher' && (
        <>
          <button 
            onClick={toggleRecording}
            className={`btn-control ${isRecording ? 'btn-danger' : 'btn-primary'}`}
          >
            {isRecording ? '⏹ Stop Recording' : '⏺ Start Recording'}
          </button>
          
          <button 
            onClick={() => launchMCQ(1)}
            className="btn-control btn-secondary"
          >
            📝 Launch Quiz
          </button>
          
          <button className="btn-control btn-secondary">
            👥 Mute All Students
          </button>
        </>
      )}

      {/* Chat & Participants */}
      <button onClick={toggleChat} className="btn-control btn-secondary">
        💬 Chat
      </button>
      
      <button onClick={toggleParticipants} className="btn-control btn-secondary">
        👥 Participants
      </button>

      {/* Leave Button */}
      <button className="btn-control btn-danger">
        📞 Leave Class
      </button>
    </div>
  );
}
