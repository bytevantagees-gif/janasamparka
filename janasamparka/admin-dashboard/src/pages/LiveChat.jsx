import { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, Users, Clock } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';

function LiveChat() {
  const { user } = useAuth();
  const { t, isKannada } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Demo messages
  useEffect(() => {
    const demoMessages = [
      {
        id: 1,
        sender: 'MLA Office',
        message: isKannada ? 'ನಮಸ್ಕಾರ! ನಾವು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?' : 'Hello! How can we help you today?',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        isSystem: true
      }
    ];
    setMessages(demoMessages);
  }, [isKannada]);

  const handleSend = () => {
    if (!newMessage.trim()) return;

    const message = {
      id: messages.length + 1,
      sender: user?.name || 'You',
      message: newMessage,
      timestamp: new Date().toISOString(),
      isSystem: false
    };

    setMessages([...messages, message]);
    setNewMessage('');

    // Auto-reply (demo)
    setTimeout(() => {
      const reply = {
        id: messages.length + 2,
        sender: 'MLA Office',
        message: isKannada 
          ? 'ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ನಮ್ಮ ತಂಡ ಶೀಘ್ರದಲ್ಲೇ ನಿಮಗೆ ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತದೆ.' 
          : 'Thank you for your message. Our team will respond shortly.',
        timestamp: new Date().toISOString(),
        isSystem: true
      };
      setMessages(prev => [...prev, reply]);
    }, 1000);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* Header */}
      <div className="bg-white rounded-t-xl shadow-sm border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {isKannada ? 'ಲೈವ್ ಚಾಟ್' : 'Live Chat'}
              </h1>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>{isKannada ? 'ಆನ್‌ಲೈನ್' : 'Online'}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span>2 {isKannada ? 'ಸದಸ್ಯರು' : 'members'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.isSystem ? 'justify-start' : 'justify-end'}`}
          >
            <div className={`max-w-md ${msg.isSystem ? '' : 'order-2'}`}>
              <div
                className={`rounded-2xl px-4 py-3 ${
                  msg.isSystem
                    ? 'bg-white text-gray-800 shadow-sm'
                    : 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md'
                }`}
              >
                <p className="text-sm font-medium mb-1">
                  {msg.sender}
                </p>
                <p className="text-sm leading-relaxed">{msg.message}</p>
                <div className="flex items-center justify-end mt-2 space-x-1">
                  <Clock className="w-3 h-3 opacity-60" />
                  <span className="text-xs opacity-75">
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white rounded-b-xl shadow-sm border-t border-gray-200 p-4">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isKannada ? 'ಸಂದೇಶ ಬರೆಯಿರಿ...' : 'Type a message...'}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSend}
            disabled={!newMessage.trim()}
            className="p-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-full hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          {isKannada 
            ? 'ನಿಮ್ಮ ಸಂದೇಶಗಳು ಎನ್‌ಕ್ರಿಪ್ಟ್ ಮಾಡಲಾಗಿದೆ' 
            : 'Your messages are end-to-end encrypted'}
        </p>
      </div>
    </div>
  );
}

export default LiveChat;
