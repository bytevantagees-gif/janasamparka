import React, { useState, useEffect } from 'react';
import { Star, MessageSquare, CheckCircle, AlertCircle } from 'lucide-react';

/**
 * CitizenRating Component
 * Allows citizens to rate completed work and provide feedback
 * 
 * Features:
 * - 5-star rating system
 * - Optional text feedback
 * - Can update rating within 24 hours
 * - Shows eligibility status
 */
const CitizenRating = ({ complaintId, onRatingSubmitted }) => {
  const [ratingData, setRatingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [selectedRating, setSelectedRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [message, setMessage] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchRatingStatus();
  }, [complaintId]);

  const fetchRatingStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/api/ratings/${complaintId}/rating`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setRatingData(data);
        if (data.citizen_rating) {
          setSelectedRating(data.citizen_rating);
          setFeedback(data.citizen_feedback || '');
        }
      }
    } catch (error) {
      console.error('Error fetching rating status:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitRating = async () => {
    if (selectedRating === 0) {
      setMessage({ type: 'error', text: 'Please select a rating' });
      return;
    }

    setSubmitting(true);
    setMessage(null);

    try {
      const token = localStorage.getItem('access_token');
      const url = `http://localhost:8000/api/ratings/${complaintId}/rate`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          rating: selectedRating,
          feedback: feedback.trim() || null
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: 'Thank you for your feedback!' 
        });
        setRatingData(data);
        setIsEditing(false);
        if (onRatingSubmitted) onRatingSubmitted(data);
      } else {
        setMessage({ 
          type: 'error', 
          text: data.detail || 'Failed to submit rating' 
        });
      }
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: 'Error submitting rating. Please try again.' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  const updateRating = async () => {
    setSubmitting(true);
    setMessage(null);

    try {
      const token = localStorage.getItem('access_token');
      const url = `http://localhost:8000/api/ratings/${complaintId}/rating`;
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          rating: selectedRating,
          feedback: feedback.trim() || null
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: 'Rating updated successfully!' 
        });
        setRatingData(data);
        setIsEditing(false);
        if (onRatingSubmitted) onRatingSubmitted(data);
      } else {
        setMessage({ 
          type: 'error', 
          text: data.detail || 'Failed to update rating' 
        });
      }
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: 'Error updating rating. Please try again.' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  const StarRating = () => (
    <div className="flex items-center gap-2">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => setSelectedRating(star)}
          onMouseEnter={() => setHoverRating(star)}
          onMouseLeave={() => setHoverRating(0)}
          disabled={!isEditing && ratingData?.citizen_rating}
          className={`transition-all duration-200 ${
            (!isEditing && ratingData?.citizen_rating) ? 'cursor-default' : 'cursor-pointer hover:scale-110'
          }`}
        >
          <Star
            className={`w-10 h-10 ${
              star <= (hoverRating || selectedRating)
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }`}
          />
        </button>
      ))}
      {selectedRating > 0 && (
        <span className="ml-2 text-lg font-medium text-gray-700">
          {selectedRating} / 5
        </span>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Not eligible to rate
  if (!ratingData?.can_rate && !ratingData?.citizen_rating) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-gray-600">{ratingData?.rating_message}</p>
          </div>
        </div>
      </div>
    );
  }

  // Already rated (view mode)
  if (ratingData?.citizen_rating && !isEditing) {
    const canEdit = ratingData.rating_submitted_at && 
      (new Date() - new Date(ratingData.rating_submitted_at)) / (1000 * 60 * 60) < 24;

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Your Rating</h3>
          {canEdit && (
            <button
              onClick={() => setIsEditing(true)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Edit Rating
            </button>
          )}
        </div>

        <div className="mb-4">
          <StarRating />
        </div>

        {ratingData.citizen_feedback && (
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <MessageSquare className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Your Feedback</p>
                <p className="text-sm text-gray-600">{ratingData.citizen_feedback}</p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span>
            Rated on {new Date(ratingData.rating_submitted_at).toLocaleDateString()}
          </span>
        </div>

        {!canEdit && (
          <p className="mt-2 text-xs text-gray-500">
            Rating can only be edited within 24 hours of submission
          </p>
        )}
      </div>
    );
  }

  // Rating form (new or edit)
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {isEditing ? 'Update Your Rating' : 'Rate the Work'}
      </h3>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          How satisfied are you with the work?
        </label>
        <StarRating />
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Feedback (Optional)
        </label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Share your experience with the resolution..."
          rows={4}
          maxLength={1000}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
        <p className="mt-1 text-xs text-gray-500">
          {feedback.length} / 1000 characters
        </p>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          <p className="text-sm">{message.text}</p>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={isEditing ? updateRating : submitRating}
          disabled={submitting || selectedRating === 0}
          className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {submitting ? 'Submitting...' : isEditing ? 'Update Rating' : 'Submit Rating'}
        </button>
        
        {isEditing && (
          <button
            onClick={() => {
              setIsEditing(false);
              setSelectedRating(ratingData.citizen_rating);
              setFeedback(ratingData.citizen_feedback || '');
              setMessage(null);
            }}
            className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
};

export default CitizenRating;
