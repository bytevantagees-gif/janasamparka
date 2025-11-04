import { useState, useEffect, useRef } from 'react';
import { Send, ThumbsUp, Pin, Check, X, MessageSquare, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const ConferenceChat = ({ conferenceId, isModerator = false }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [pendingMessages, setPendingMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isQuestion, setIsQuestion] = useState(false);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Fetch approved messages (visible to all)
  const fetchMessages = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/chat/conferences/${conferenceId}/chat`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setMessages(data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  // Fetch pending messages (moderators only)
  const fetchPendingMessages = async () => {
    if (!isModerator) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/chat/conferences/${conferenceId}/chat/pending`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setPendingMessages(data);
    } catch (error) {
      console.error('Failed to fetch pending messages:', error);
    }
  };

  // Send message
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/chat/conferences/${conferenceId}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: newMessage,
          message_type: 'text',
          is_question: isQuestion
        })
      });

      if (response.ok) {
        setNewMessage('');
        setIsQuestion(false);
        // If moderator, refresh pending queue
        if (isModerator) {
          fetchPendingMessages();
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  // Moderate message (approve/reject)
  const moderateMessage = async (messageId, action, rejectionReason = null) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_BASE}/api/chat/conferences/${conferenceId}/chat/${messageId}/moderate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action, rejection_reason: rejectionReason })
      });

      // Refresh both lists
      fetchMessages();
      fetchPendingMessages();
    } catch (error) {
      console.error('Failed to moderate message:', error);
    }
  };

  // Pin message
  const pinMessage = async (messageId) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_BASE}/api/chat/conferences/${conferenceId}/chat/${messageId}/pin`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchMessages();
    } catch (error) {
      console.error('Failed to pin message:', error);
    }
  };

  // Auto-refresh messages every 5 seconds
  useEffect(() => {
    fetchMessages();
    if (isModerator) {
      fetchPendingMessages();
    }

    const interval = setInterval(() => {
      fetchMessages();
      if (isModerator) {
        fetchPendingMessages();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [conferenceId, isModerator]);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Moderator Panel - Pending Messages */}
      {isModerator && pendingMessages.length > 0 && (
        <div className="bg-yellow-50 border-b-2 border-yellow-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-yellow-900 flex items-center">
              <AlertCircle className="w-4 h-4 mr-2" />
              {pendingMessages.length} Messages Awaiting Approval
            </h3>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {pendingMessages.map((msg) => (
              <div key={msg.id} className="bg-white rounded p-3 border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{msg.sender_name}</p>
                    <p className="text-sm text-gray-700 mt-1">{msg.message}</p>
                    {msg.is_question && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 mt-2">
                        Question
                      </span>
                    )}
                  </div>
                  <div className="flex space-x-2 ml-3">
                    <button
                      onClick={() => moderateMessage(msg.id, 'approve')}
                      className="p-1 text-green-600 hover:bg-green-50 rounded"
                      title="Approve"
                    >
                      <Check className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => moderateMessage(msg.id, 'reject', 'Inappropriate content')}
                      className="p-1 text-red-600 hover:bg-red-50 rounded"
                      title="Reject"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <MessageSquare className="w-5 h-5 mr-2" />
          Live Chat
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          {isModerator ? 'Moderating chat messages' : 'Messages are moderated before appearing'}
        </p>
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ maxHeight: '400px' }}>
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <MessageSquare className="w-12 h-12 mx-auto text-gray-300 mb-2" />
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-3 rounded-lg ${
                msg.is_pinned
                  ? 'bg-blue-50 border-2 border-blue-200'
                  : msg.sender_role === 'admin' || msg.sender_role === 'mla'
                  ? 'bg-purple-50 border border-purple-200'
                  : 'bg-gray-50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-gray-900">{msg.sender_name}</span>
                    {msg.is_pinned && (
                      <Pin className="w-3 h-3 text-blue-600" />
                    )}
                    {msg.is_question && (
                      <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-800 rounded-full">
                        Q&A
                      </span>
                    )}
                    {msg.is_answered && (
                      <span className="text-xs px-2 py-0.5 bg-green-100 text-green-800 rounded-full">
                        ✓ Answered
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{msg.message}</p>
                  <div className="flex items-center space-x-3 mt-2">
                    <button className="text-xs text-gray-500 hover:text-blue-600 flex items-center">
                      <ThumbsUp className="w-3 h-3 mr-1" />
                      {msg.likes_count || 0}
                    </button>
                    <span className="text-xs text-gray-400">
                      {new Date(msg.sent_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                {isModerator && !msg.is_pinned && (
                  <button
                    onClick={() => pinMessage(msg.id)}
                    className="ml-2 p-1 text-gray-400 hover:text-blue-600"
                    title="Pin message"
                  >
                    <Pin className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Message Input */}
      <form onSubmit={sendMessage} className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2 mb-2">
          <label className="flex items-center text-sm text-gray-600">
            <input
              type="checkbox"
              checked={isQuestion}
              onChange={(e) => setIsQuestion(e.target.checked)}
              className="mr-2"
            />
            Mark as Q&A Question
          </label>
        </div>
        <div className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={isModerator ? "Send a message..." : "Your message will be reviewed before posting..."}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !newMessage.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
          >
            <Send className="w-4 h-4 mr-1" />
            Send
          </button>
        </div>
        {!isModerator && (
          <p className="text-xs text-gray-500 mt-2">
            Your message will appear after moderator approval
          </p>
        )}
      </form>
    </div>
  );
};

export default ConferenceChat;
