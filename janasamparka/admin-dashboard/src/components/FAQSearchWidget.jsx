import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import debounce from 'lodash.debounce';

/**
 * FAQSearchWidget - Multilingual FAQ search with voting
 * 
 * Features:
 * - Kannada and English search
 * - Relevance scoring
 * - Helpful/Not Helpful voting
 * - Prevented complaints counter
 * - Auto-suggestions
 */
const FAQSearchWidget = ({ 
  constituencyId = null,
  onSolutionSelect = null,
  showPreventedCount = true
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSolution, setSelectedSolution] = useState(null);
  const [preventedComplaintsCount, setPreventedComplaintsCount] = useState(0);
  const [votedSolutions, setVotedSolutions] = useState(new Set());

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (query) => {
      if (!query || query.trim().length < 2) {
        setSearchResults([]);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get('/api/v1/faqs/search', {
          params: {
            query: query.trim(),
            constituency_id: constituencyId,
            limit: 10
          }
        });

        setSearchResults(response.data.results || []);
      } catch (err) {
        console.error('Error searching FAQs:', err);
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    }, 500),
    [constituencyId]
  );

  useEffect(() => {
    debouncedSearch(searchQuery);
    return () => debouncedSearch.cancel();
  }, [searchQuery, debouncedSearch]);

  useEffect(() => {
    if (showPreventedCount) {
      fetchPreventedCount();
    }
  }, [showPreventedCount]);

  const fetchPreventedCount = async () => {
    try {
      const response = await axios.get('/api/v1/faqs/statistics');
      setPreventedComplaintsCount(response.data.total_prevented_complaints || 0);
    } catch (err) {
      console.error('Error fetching prevented complaints count:', err);
    }
  };

  const handleVote = async (solutionId, isHelpful) => {
    if (votedSolutions.has(solutionId)) {
      return; // Already voted
    }

    try {
      await axios.post(`/api/v1/faqs/${solutionId}/vote`, {
        helpful: isHelpful
      });

      // Update local state
      setVotedSolutions(new Set(votedSolutions.add(solutionId)));
      
      // Refresh results to show updated counts
      if (searchQuery) {
        debouncedSearch(searchQuery);
      }
    } catch (err) {
      console.error('Error voting on solution:', err);
    }
  };

  const handleSolutionClick = (solution) => {
    setSelectedSolution(solution);
    if (onSolutionSelect) {
      onSolutionSelect(solution);
    }
  };

  const highlightMatch = (text, query) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, idx) => 
      regex.test(part) ? (
        <mark key={idx} className="bg-yellow-200 font-medium">{part}</mark>
      ) : part
    );
  };

  const getRelevanceColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-blue-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-gray-600';
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
            💡 FAQ Knowledge Base
          </h3>
          {showPreventedCount && preventedComplaintsCount > 0 && (
            <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
              🎯 {preventedComplaintsCount} complaints prevented
            </div>
          )}
        </div>
        <p className="text-sm text-gray-600">
          Search in ಕನ್ನಡ or English for instant solutions
        </p>
      </div>

      {/* Search Input */}
      <div className="p-4">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Type your question in Kannada or English... (e.g., ರಸ್ತೆ ಸರಿಪಡಿಸಲು or road repair)"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {loading && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            </div>
          )}
        </div>
      </div>

      {/* Search Results */}
      <div className="max-h-96 overflow-y-auto">
        {searchResults.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {searchResults.map((result) => {
              const hasVoted = votedSolutions.has(result.id);
              
              return (
                <div
                  key={result.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer transition ${
                    selectedSolution?.id === result.id ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleSolutionClick(result)}
                >
                  {/* Question */}
                  <div className="mb-2">
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="font-semibold text-gray-900 text-sm flex-1">
                        {highlightMatch(result.question_en, searchQuery)}
                      </h4>
                      <span 
                        className={`text-xs font-medium px-2 py-1 rounded ${getRelevanceColor(result.relevance_score)}`}
                      >
                        {(result.relevance_score * 100).toFixed(0)}% match
                      </span>
                    </div>
                    {result.question_kn && (
                      <p className="text-sm text-gray-600 mt-1">
                        {highlightMatch(result.question_kn, searchQuery)}
                      </p>
                    )}
                  </div>

                  {/* Solution Preview */}
                  <div className="mb-3">
                    <p className="text-sm text-gray-700 line-clamp-2">
                      {result.solution_en}
                    </p>
                  </div>

                  {/* Metadata */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1">
                        📂 {result.category}
                      </span>
                      <span className="flex items-center gap-1">
                        ✅ Prevented {result.prevented_complaints_count || 0} complaints
                      </span>
                    </div>

                    {/* Voting Buttons */}
                    <div className="flex items-center gap-2">
                      {hasVoted ? (
                        <span className="text-green-600 font-medium">✓ Voted</span>
                      ) : (
                        <>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleVote(result.id, true);
                            }}
                            className="flex items-center gap-1 px-2 py-1 rounded hover:bg-green-100 text-green-600 transition"
                            title="Helpful"
                          >
                            👍 {result.helpful_count || 0}
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleVote(result.id, false);
                            }}
                            className="flex items-center gap-1 px-2 py-1 rounded hover:bg-red-100 text-red-600 transition"
                            title="Not Helpful"
                          >
                            👎 {result.not_helpful_count || 0}
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : searchQuery.length >= 2 && !loading ? (
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-2">🔍</div>
            <p>No solutions found for "{searchQuery}"</p>
            <p className="text-sm mt-1">Try different keywords or check spelling</p>
          </div>
        ) : !searchQuery ? (
          <div className="p-8 text-center text-gray-400">
            <div className="text-4xl mb-2">💭</div>
            <p>Start typing to search for solutions</p>
          </div>
        ) : null}
      </div>

      {/* Selected Solution Detail */}
      {selectedSolution && (
        <div className="border-t border-gray-200 bg-blue-50 p-4">
          <div className="flex items-start justify-between mb-2">
            <h4 className="font-bold text-gray-900">Full Solution:</h4>
            <button
              onClick={() => setSelectedSolution(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <p className="text-sm text-gray-700 mb-2">{selectedSolution.solution_en}</p>
          {selectedSolution.solution_kn && (
            <p className="text-sm text-gray-600 mb-2">{selectedSolution.solution_kn}</p>
          )}
          {selectedSolution.department && (
            <div className="text-xs text-gray-500 mt-2">
              📞 Contact: {selectedSolution.department}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

FAQSearchWidget.propTypes = {
  constituencyId: PropTypes.number,
  onSolutionSelect: PropTypes.func,
  showPreventedCount: PropTypes.bool
};

export default FAQSearchWidget;
