import { useEffect, useState } from 'react';
import {
  LiveKitRoom,
  VideoConference,
} from '@livekit/components-react';
import { useLiveSessionStore, useUIStore } from '../../store';
import { SidePanel } from './SidePanel';
import { MCQOverlay } from './MCQOverlay';
import { ControlBar } from './ControlBar';

interface VideoRoomProps {
  serverUrl: string;
  token: string;
  roomName: string;
  userRole: 'teacher' | 'student';
}

export function VideoRoom({ serverUrl, token, roomName, userRole }: VideoRoomProps) {
  const [isConnected, setIsConnected] = useState(false);
  const { isRecording, isInMCQ, currentMCQ, toggleRecording, launchMCQ, endMCQ } = useLiveSessionStore();
  const { isChatOpen, isParticipantsOpen } = useUIStore();

  const handleConnected = () => {
    setIsConnected(true);
    console.log('Connected to LiveKit room:', roomName);
  };

  const handleDisconnected = () => {
    setIsConnected(false);
    console.log('Disconnected from room');
  };

  return (
    <div className="flex h-screen bg-slate-900 text-white">
      {/* Main Video Area */}
      <div className="flex-1 flex flex-col">
        <LiveKitRoom
          video={true}
          audio={true}
          token={token}
          serverUrl={serverUrl}
          onConnected={handleConnected}
          onDisconnected={handleDisconnected}
          data-lk-theme="default"
          style={{ height: '100%' }}
        >
          {/* Video Grid */}
          <div className="flex-1 p-4 overflow-hidden">
            <VideoConference />
          </div>

          {/* Custom Control Bar */}
          <ControlBar userRole={userRole} />
        </LiveKitRoom>
      </div>

      {/* Side Panel */}
      {(isChatOpen || isParticipantsOpen) && (
        <SidePanel />
      )}

      {/* MCQ Overlay */}
      {isInMCQ && currentMCQ && (
        <MCQOverlay mcqData={currentMCQ} onClose={endMCQ} />
      )}
    </div>
  );
}
