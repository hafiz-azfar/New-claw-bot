import { useState, useEffect } from 'react';
import { useUIStore } from '../../store';
import { messagingService } from '../../services/api';

export function SidePanel() {
  const { isChatOpen, isParticipantsOpen, toggleChat, toggleParticipants } = useUIStore();
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [participants] = useState([
    { id: 1, name: 'Ahmed Hassan', role: 'teacher', isSpeaking: true },
    { id: 2, name: 'Fatima Ali', role: 'student', isSpeaking: false },
    { id: 3, name: 'Omar Khan', role: 'student', isSpeaking: false },
  ]);

  // Load chat history
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        // TODO: Get current course ID from context
        const history = await messagingService.getChatHistory(1);
        setMessages(history);
      } catch (error) {
        console.error('Failed to load chat history:', error);
      }
    };

    if (isChatOpen) {
      loadChatHistory();
    }
  }, [isChatOpen]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      // TODO: Get current course ID from context
      const message = await messagingService.sendMessage(1, newMessage);
      setMessages([...messages, message]);
      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="side-panel">
      {/* Panel Header */}
      <div className="flex justify-between items-center p-4 border-b border-slate-700">
        <h3 className="text-lg font-bold">
          {isChatOpen ? '💬 Class Chat' : '👥 Participants'}
        </h3>
        <button onClick={isChatOpen ? toggleChat : toggleParticipants} className="text-gray-400 hover:text-white">
          ✕
        </button>
      </div>

      {/* Chat Panel */}
      {isChatOpen && (
        <>
          {/* Messages */}
          <div className="chat-messages flex-1 overflow-y-auto">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-center mt-8">No messages yet. Start the conversation!</p>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className="chat-message">
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-semibold text-blue-400">{msg.sender_name}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-gray-200">{msg.content}</p>
                </div>
              ))
            )}
          </div>

          {/* Input Area */}
          <div className="chat-input-area">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
              rows={3}
            />
            <button
              onClick={handleSendMessage}
              disabled={!newMessage.trim()}
              className={`mt-2 w-full btn-control ${
                !newMessage.trim() ? 'opacity-50 cursor-not-allowed' : 'btn-primary'
              }`}
            >
              Send Message
            </button>
            <p className="text-xs text-gray-500 mt-2 text-center">
              ⚠️ All messages are moderated and visible to everyone
            </p>
          </div>
        </>
      )}

      {/* Participants Panel */}
      {isParticipantsOpen && (
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-400 mb-2">HOST</h4>
            {participants
              .filter((p) => p.role === 'teacher')
              .map((p) => (
                <div key={p.id} className="flex items-center gap-3 p-3 bg-slate-800 rounded-lg mb-2">
                  <div className={`w-3 h-3 rounded-full ${p.isSpeaking ? 'bg-green-500' : 'bg-gray-500'}`} />
                  <div>
                    <p className="font-semibold">{p.name}</p>
                    <p className="text-xs text-gray-400">Teacher</p>
                  </div>
                </div>
              ))}
          </div>

          <div>
            <h4 className="text-sm font-semibold text-gray-400 mb-2">STUDENTS ({participants.filter(p => p.role === 'student').length})</h4>
            {participants
              .filter((p) => p.role === 'student')
              .map((p) => (
                <div key={p.id} className="flex items-center gap-3 p-3 bg-slate-800 rounded-lg mb-2">
                  <div className={`w-3 h-3 rounded-full ${p.isSpeaking ? 'bg-green-500' : 'bg-gray-500'}`} />
                  <div>
                    <p className="font-semibold">{p.name}</p>
                    <p className="text-xs text-gray-400">Student</p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
