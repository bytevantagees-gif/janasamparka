import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  ThumbsUp,
  MessageSquare,
  Check,
  X,
  AlertCircle,
  Clock,
  CheckCircle,
  Send
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function ForumTopicDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [replyContent, setReplyContent] = useState('');
  const [loading, setLoading] = useState(false);

  const isModerator = ['admin', 'mla', 'moderator'].includes(user?.role);

  // Fetch topic with posts
  const { data: topicData, isLoading, refetch } = useQuery({
    queryKey: ['forum-topic', id],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/forum/topics/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.json();
    },
  });

  // Fetch pending posts for moderators
  const { data: pendingPosts, refetch: refetchPending } = useQuery({
    queryKey: ['forum-pending'],
    queryFn: async () => {
      if (!isModerator) return [];
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/forum/posts/pending`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.json();
    },
    enabled: isModerator,
  });

  const handlePostReply = async (e) => {
    e.preventDefault();
    if (!replyContent.trim()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/forum/topics/${id}/posts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: replyContent })
      });

      if (response.ok) {
        setReplyContent('');
        if (isModerator) {
          refetchPending();
        }
        alert('Reply submitted! ' + (isModerator ? 'Awaiting approval.' : 'It will appear after moderation.'));
      }
    } catch (error) {
      console.error('Failed to post reply:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleModerate = async (postId, action) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_BASE}/api/forum/posts/${postId}/moderate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });

      refetch();
      refetchPending();
    } catch (error) {
      console.error('Failed to moderate post:', error);
    }
  };

  const handleMarkSolution = async (postId) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_BASE}/api/forum/posts/${postId}/mark-solution`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      refetch();
    } catch (error) {
      console.error('Failed to mark solution:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading discussion...</p>
        </div>
      </div>
    );
  }

  const topic = topicData?.topic;
  const posts = topicData?.posts || [];
  const topicPending = pendingPosts?.filter(p => p.topic_id === id) || [];

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link
        to="/forum"
        className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Forum
      </Link>

      {/* Topic Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-3">
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {topic?.category}
              </span>
              {topic?.status === 'closed' && (
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Closed
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {topic?.title}
            </h1>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>By {topic?.author_name} ({topic?.author_role})</span>
              <span>•</span>
              <span>{new Date(topic?.created_at).toLocaleString()}</span>
              <span>•</span>
              <span>{topic?.views_count} views</span>
            </div>
          </div>
        </div>

        {topic?.description && (
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{topic.description}</p>
          </div>
        )}

        <div className="mt-4 flex items-center space-x-4">
          <button className="inline-flex items-center px-3 py-1 text-sm text-gray-600 hover:text-blue-600">
            <ThumbsUp className="w-4 h-4 mr-1" />
            {topic?.likes_count || 0} Likes
          </button>
          <span className="inline-flex items-center px-3 py-1 text-sm text-gray-600">
            <MessageSquare className="w-4 h-4 mr-1" />
            {topic?.replies_count || 0} Replies
          </span>
        </div>
      </div>

      {/* Moderator Panel - Pending Posts */}
      {isModerator && topicPending.length > 0 && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
            <h3 className="text-lg font-semibold text-yellow-900">
              {topicPending.length} Posts Awaiting Moderation
            </h3>
          </div>
          <div className="space-y-3">
            {topicPending.map((post) => (
              <div key={post.id} className="bg-white rounded p-4 border border-yellow-300">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{post.author_name} ({post.author_role})</p>
                    <p className="text-sm text-gray-700 mt-2 whitespace-pre-wrap">{post.content}</p>
                    <p className="text-xs text-gray-500 mt-2">{new Date(post.created_at).toLocaleString()}</p>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button
                      onClick={() => handleModerate(post.id, 'approve')}
                      className="p-2 text-green-600 hover:bg-green-50 rounded"
                      title="Approve"
                    >
                      <Check className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleModerate(post.id, 'reject')}
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
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

      {/* Replies Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {posts.length} {posts.length === 1 ? 'Reply' : 'Replies'}
          </h2>
        </div>

        <div className="divide-y divide-gray-200">
          {posts.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <MessageSquare className="w-12 h-12 mx-auto text-gray-300 mb-2" />
              <p>No replies yet. Be the first to respond!</p>
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-primary-600 font-semibold">
                        {post.author_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium text-gray-900">{post.author_name}</span>
                      <span className="text-sm text-gray-500">({post.author_role})</span>
                      {post.is_solution && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Solution
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap mb-3">{post.content}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <button className="inline-flex items-center hover:text-blue-600">
                        <ThumbsUp className="w-4 h-4 mr-1" />
                        {post.likes_count || 0}
                      </button>
                      <span>{new Date(post.created_at).toLocaleString()}</span>
                      {post.edited_at && (
                        <span className="text-xs">(edited)</span>
                      )}
                      {!post.is_solution && topic?.author_id === user?.id && (
                        <button
                          onClick={() => handleMarkSolution(post.id)}
                          className="text-xs text-green-600 hover:text-green-700"
                        >
                          Mark as Solution
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Reply Form */}
      {topic?.status !== 'closed' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Post a Reply</h3>
          <form onSubmit={handlePostReply}>
            <textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder="Share your thoughts..."
              rows={4}
              className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 mb-4"
              required
            />
            {!isModerator && (
              <p className="text-xs text-gray-500 mb-4">
                Your reply will be visible after moderator approval.
              </p>
            )}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading || !replyContent.trim()}
                className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
              >
                <Send className="w-4 h-4 mr-2" />
                {loading ? 'Posting...' : 'Post Reply'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default ForumTopicDetail;
