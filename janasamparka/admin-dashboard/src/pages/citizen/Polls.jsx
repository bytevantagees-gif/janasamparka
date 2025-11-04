import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BarChart3,
  CheckCircle2,
  Clock,
  TrendingUp,
  Vote,
  AlertCircle,
  Calendar,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { pollsAPI } from '../../services/api';

export default function Polls() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [selectedPollId, setSelectedPollId] = useState(null);
  const [selectedOption, setSelectedOption] = useState(null);

  // Fetch available polls
  const { data: pollsData, isLoading } = useQuery({
    queryKey: ['polls', 'available'],
    queryFn: async () => {
      const response = await pollsAPI.getAll();
      return response.data;
    },
  });

  // Fetch user's votes
  const { data: myVotesData } = useQuery({
    queryKey: ['polls', 'my-votes'],
    queryFn: async () => {
      const response = await pollsAPI.getMyVotes();
      return response.data;
    },
  });

  // Vote mutation
  const voteMutation = useMutation({
    mutationFn: async ({ pollId, optionId }) => {
      return pollsAPI.vote(pollId, optionId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['polls']);
      setSelectedPollId(null);
      setSelectedOption(null);
    },
  });

  const polls = pollsData?.polls || [];
  const myVotes = myVotesData?.votes || {};

  // Filter polls
  const activePolls = polls.filter(
    (p) => p.status === 'active' && !myVotes[p.id]
  );
  const votedPolls = polls.filter((p) => myVotes[p.id]);
  const upcomingPolls = polls.filter((p) => p.status === 'scheduled');

  const handleVote = (pollId) => {
    if (selectedOption) {
      voteMutation.mutate({ pollId, optionId: selectedOption });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Community Polls</h1>
        <p className="mt-1 text-sm text-slate-600">
          Share your opinion on important matters
        </p>
      </div>

      {/* Statistics */}
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          icon={Vote}
          label="Available to Vote"
          value={activePolls.length}
          color="blue"
        />
        <StatCard
          icon={CheckCircle2}
          label="You Voted"
          value={votedPolls.length}
          color="green"
        />
        <StatCard
          icon={Clock}
          label="Upcoming"
          value={upcomingPolls.length}
          color="amber"
        />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent"></div>
        </div>
      ) : (
        <>
          {/* Active Polls - Awaiting Your Vote */}
          {activePolls.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-slate-900">
                📩 Awaiting Your Vote
              </h2>
              {activePolls.map((poll) => (
                <PollCard
                  key={poll.id}
                  poll={poll}
                  isVoting={selectedPollId === poll.id}
                  selectedOption={selectedOption}
                  onSelectOption={setSelectedOption}
                  onVote={() => {
                    setSelectedPollId(poll.id);
                    handleVote(poll.id);
                  }}
                  voteMutation={voteMutation}
                  hasVoted={false}
                />
              ))}
            </div>
          )}

          {/* Polls You've Voted On */}
          {votedPolls.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-slate-900">
                ✅ Your Votes
              </h2>
              {votedPolls.map((poll) => (
                <PollCard
                  key={poll.id}
                  poll={poll}
                  hasVoted={true}
                  userVote={myVotes[poll.id]}
                />
              ))}
            </div>
          )}

          {/* Upcoming Polls */}
          {upcomingPolls.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-slate-900">
                ⏰ Coming Soon
              </h2>
              {upcomingPolls.map((poll) => (
                <UpcomingPollCard key={poll.id} poll={poll} />
              ))}
            </div>
          )}

          {/* Empty State */}
          {activePolls.length === 0 &&
            votedPolls.length === 0 &&
            upcomingPolls.length === 0 && (
              <div className="rounded-xl border-2 border-dashed border-slate-200 bg-white p-12 text-center">
                <Vote className="mx-auto h-16 w-16 text-slate-300" />
                <p className="mt-4 text-lg font-semibold text-slate-700">
                  No polls available
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  Check back later for community polls
                </p>
              </div>
            )}
        </>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-emerald-600',
    amber: 'from-amber-500 to-orange-600',
  };

  return (
    <div
      className={`rounded-xl bg-gradient-to-br ${colorClasses[color]} p-6 text-white shadow-lg`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-white/80">{label}</p>
          <p className="mt-2 text-3xl font-bold">{value}</p>
        </div>
        <div className="rounded-lg bg-white/20 p-3">
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

function PollCard({
  poll,
  isVoting,
  selectedOption,
  onSelectOption,
  onVote,
  voteMutation,
  hasVoted,
  userVote,
}) {
  const totalVotes = poll.options?.reduce((sum, opt) => sum + (opt.vote_count || 0), 0) || 0;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      {/* Poll Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-slate-900">{poll.title}</h3>
          {poll.description && (
            <p className="mt-1 text-sm text-slate-600">{poll.description}</p>
          )}
          <div className="mt-2 flex items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              {new Date(poll.created_at).toLocaleDateString()}
            </span>
            {poll.closes_at && (
              <span className="flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" />
                Closes: {new Date(poll.closes_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        {hasVoted && (
          <div className="flex items-center gap-2 rounded-lg bg-green-100 px-3 py-1 text-sm font-semibold text-green-700">
            <CheckCircle2 className="h-4 w-4" />
            Voted
          </div>
        )}
      </div>

      {/* Options */}
      <div className="mt-6 space-y-3">
        {poll.options?.map((option) => {
          const percentage =
            totalVotes > 0 ? ((option.vote_count || 0) / totalVotes) * 100 : 0;
          const isSelected = selectedOption === option.id;
          const isUserVote = userVote === option.id;

          return (
            <div key={option.id}>
              {hasVoted ? (
                // Show results after voting
                <div className="relative overflow-hidden rounded-lg border border-slate-200 p-4">
                  <div
                    className={`absolute inset-0 ${
                      isUserVote ? 'bg-green-100' : 'bg-slate-100'
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                  <div className="relative flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900">
                        {option.option_text}
                      </span>
                      {isUserVote && (
                        <span className="text-xs font-semibold text-green-600">
                          (Your vote)
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold text-slate-700">
                        {percentage.toFixed(1)}%
                      </span>
                      <span className="text-xs text-slate-500">
                        ({option.vote_count || 0} votes)
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                // Show voting interface
                <button
                  onClick={() => onSelectOption && onSelectOption(option.id)}
                  className={`w-full rounded-lg border-2 p-4 text-left transition ${
                    isSelected
                      ? 'border-sky-500 bg-sky-50'
                      : 'border-slate-200 bg-white hover:border-sky-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`h-5 w-5 rounded-full border-2 ${
                        isSelected
                          ? 'border-sky-500 bg-sky-500'
                          : 'border-slate-300'
                      } flex items-center justify-center`}
                    >
                      {isSelected && (
                        <CheckCircle2 className="h-4 w-4 text-white" />
                      )}
                    </div>
                    <span className="font-medium text-slate-900">
                      {option.option_text}
                    </span>
                  </div>
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Vote Button */}
      {!hasVoted && (
        <button
          onClick={onVote}
          disabled={!selectedOption || voteMutation.isLoading}
          className="mt-4 w-full rounded-lg bg-sky-600 py-3 font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {voteMutation.isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Submitting...
            </span>
          ) : (
            'Submit Vote'
          )}
        </button>
      )}

      {/* Total Votes */}
      {hasVoted && (
        <div className="mt-4 flex items-center justify-between border-t border-slate-200 pt-4">
          <span className="text-sm text-slate-600">Total votes</span>
          <span className="text-sm font-semibold text-slate-900">{totalVotes}</span>
        </div>
      )}
    </div>
  );
}

function UpcomingPollCard({ poll }) {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
      <div className="flex items-start gap-4">
        <div className="rounded-lg bg-amber-100 p-3">
          <Clock className="h-6 w-6 text-amber-600" />
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-amber-900">{poll.title}</h3>
          {poll.description && (
            <p className="mt-1 text-sm text-amber-700">{poll.description}</p>
          )}
          <div className="mt-2 flex items-center gap-2 text-xs text-amber-600">
            <Calendar className="h-3.5 w-3.5" />
            Opens: {new Date(poll.starts_at || poll.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  );
}
