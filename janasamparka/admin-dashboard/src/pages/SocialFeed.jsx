import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  MessageCircle, 
  Plus, 
  Search,
  Pin,
  Calendar,
  Users,
  ThumbsUp,
  MessageSquare,
  MapPin
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function SocialFeed() {
  const { user } = useAuth();
  const { t, isKannada } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch posts
  const { data: posts, isLoading } = useQuery({
    queryKey: ['social-posts', searchTerm],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/social/posts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.json();
    },
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['social-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/social/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.json();
    },
  });

  const canCreatePost = ['admin', 'mla', 'moderator'].includes(user?.role);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">{isKannada ? 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...' : 'Loading...'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <MessageCircle className="w-8 h-8 mr-3 text-primary-600" />
            {isKannada ? 'MLA ನವೀಕರಣಗಳು' : 'MLA Updates'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {isKannada 
              ? 'ನಿಮ್ಮ MLA ರಿಂದ ಇತ್ತೀಚಿನ ನವೀಕರಣಗಳು ಮತ್ತು ಸಾರ್ವಜನಿಕ ಸಭೆಗಳು'
              : 'Latest updates and public meetings from your MLA'
            }
          </p>
        </div>
        {canCreatePost && (
          <button
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 shadow-sm"
          >
            <Plus className="w-5 h-5 mr-2" />
            {isKannada ? 'ಪೋಸ್ಟ್ ರಚಿಸಿ' : 'Create Post'}
          </button>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-white" />
              <div className="ml-5">
                <dt className="text-sm font-medium text-blue-100">
                  {isKannada ? 'ಒಟ್ಟು ಪೋಸ್ಟ್‌ಗಳು' : 'Total Posts'}
                </dt>
                <dd className="text-2xl font-bold text-white">{stats?.total_posts || 0}</dd>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <ThumbsUp className="h-8 w-8 text-white" />
              <div className="ml-5">
                <dt className="text-sm font-medium text-green-100">
                  {isKannada ? 'ಒಟ್ಟು ಟಿಪ್ಪಣಿಗಳು' : 'Total Comments'}
                </dt>
                <dd className="text-2xl font-bold text-white">{stats?.total_comments || 0}</dd>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-white" />
              <div className="ml-5">
                <dt className="text-sm font-medium text-purple-100">
                  {isKannada ? 'ಮುಂಬರುವ ಸಭೆಗಳು' : 'Upcoming Meetings'}
                </dt>
                <dd className="text-2xl font-bold text-white">{stats?.upcoming_meetings || 0}</dd>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-white" />
              <div className="ml-5">
                <dt className="text-sm font-medium text-orange-100">
                  {isKannada ? 'ಮಾಡರೇಷನ್ ಬಾಕಿ' : 'Pending Moderation'}
                </dt>
                <dd className="text-2xl font-bold text-white">{stats?.pending_moderation || 0}</dd>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder={isKannada ? 'ಪೋಸ್ಟ್‌ಗಳನ್ನು ಹುಡುಕಿ...' : 'Search posts...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      {/* Posts List */}
      <div className="space-y-4">
        {posts?.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">
              {isKannada ? 'ಇನ್ನೂ ಯಾವುದೇ ಪೋಸ್ಟ್‌ಗಳಿಲ್ಲ' : 'No posts yet'}
            </p>
          </div>
        ) : (
          posts?.map((post) => (
            <div key={post.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-primary-600 font-semibold text-lg">
                        {post.author_name?.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {post.is_pinned && (
                        <Pin className="w-4 h-4 text-blue-600" />
                      )}
                      <span className="font-semibold text-gray-900">{post.author_name}</span>
                      <span className="text-sm text-gray-500">({post.author_role})</span>
                      <span className="text-sm text-gray-500">•</span>
                      <span className="text-sm text-gray-500">
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-4 whitespace-pre-wrap">{post.content}</p>
                    
                    {post.post_type === 'meeting' && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                        <div className="flex items-center mb-2">
                          <Calendar className="w-5 h-5 text-blue-600 mr-2" />
                          <span className="font-semibold text-blue-900">
                            {isKannada ? 'ಸಾರ್ವಜನಿಕ ಸಭೆ' : 'Public Meeting'}
                          </span>
                        </div>
                        <p className="text-blue-800 font-medium">{post.meeting_title}</p>
                        {post.meeting_date && (
                          <p className="text-blue-700 text-sm mt-1">
                            {isKannada ? 'ದಿನಾಂಕ: ' : 'Date: '}
                            {new Date(post.meeting_date).toLocaleString()}
                          </p>
                        )}
                        {post.meeting_location && (
                          <p className="text-blue-700 text-sm mt-1">
                            <MapPin className="w-4 h-4 inline mr-1" />
                            {post.meeting_location}
                          </p>
                        )}
                        {post.meeting_capacity && (
                          <p className="text-blue-700 text-sm mt-1">
                            <Users className="w-4 h-4 inline mr-1" />
                            {isKannada ? 'ಸಾಮರ್ಥ್ಯ: ' : 'Capacity: '}{post.meeting_capacity}
                          </p>
                        )}
                      </div>
                    )}
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <button className="inline-flex items-center hover:text-blue-600">
                        <ThumbsUp className="w-4 h-4 mr-1" />
                        {post.likes_count} {isKannada ? 'ಲೈಕ್‌ಗಳು' : 'likes'}
                      </button>
                      <span className="inline-flex items-center">
                        <MessageSquare className="w-4 h-4 mr-1" />
                        {post.comments_count} {isKannada ? 'ಟಿಪ್ಪಣಿಗಳು' : 'comments'}
                      </span>
                      <span>
                        {post.views_count} {isKannada ? 'ವೀಕ್ಷಣೆಗಳು' : 'views'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default SocialFeed;
