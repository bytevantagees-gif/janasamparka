import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { Link } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { 
  BarChart3,
  Plus,
  Search,
  Calendar,
  Users,
  CheckCircle,
  Clock,
  TrendingUp,
  MapPin
} from 'lucide-react';
import PollCreateModal from '../components/PollCreateModal';

function Polls() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const queryClient = useQueryClient();

  // Mock data - replace with API call
  const polls = [
    {
      id: '1',
      title: 'Which road should be repaired first?',
      description: 'Help us prioritize road repairs in Ward 1',
      ward_name: 'MG Road Ward',
      created_at: '2025-10-25T10:00:00',
      start_date: '2025-10-25T10:00:00',
      end_date: '2025-10-31T23:59:59',
      is_active: true,
      total_votes: 245,
      options: [
        { id: 'o1', option_text: 'Main Road near Bus Stand', vote_count: 98 },
        { id: 'o2', option_text: 'Temple Street', vote_count: 87 },
        { id: 'o3', option_text: 'Market Road', vote_count: 60 },
      ],
    },
    {
      id: '2',
      title: 'Priority for new street lights?',
      description: 'Vote for areas that need street lights most urgently',
      ward_name: 'Market Ward',
      created_at: '2025-10-20T14:00:00',
      start_date: '2025-10-20T14:00:00',
      end_date: '2025-10-27T23:59:59',
      is_active: true,
      total_votes: 189,
      options: [
        { id: 'o4', option_text: 'School Road', vote_count: 78 },
        { id: 'o5', option_text: 'Park Street', vote_count: 67 },
        { id: 'o6', option_text: 'Station Road', vote_count: 44 },
      ],
    },
    {
      id: '3',
      title: 'Community Center Activities',
      description: 'What activities would you like at the new community center?',
      ward_name: 'All Wards',
      created_at: '2025-10-15T09:00:00',
      start_date: '2025-10-15T09:00:00',
      end_date: '2025-10-22T23:59:59',
      is_active: false,
      total_votes: 412,
      options: [
        { id: 'o7', option_text: 'Sports facilities', vote_count: 156 },
        { id: 'o8', option_text: 'Library & Reading room', vote_count: 142 },
        { id: 'o9', option_text: 'Meeting hall', vote_count: 114 },
      ],
    },
  ];

  const filteredPolls = polls.filter(poll => {
    const matchesSearch = 
      poll.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      poll.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      poll.ward_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = 
      !filterStatus ||
      (filterStatus === 'active' && poll.is_active) ||
      (filterStatus === 'ended' && !poll.is_active);
    
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: polls.length,
    active: polls.filter(p => p.is_active).length,
    ended: polls.filter(p => !p.is_active).length,
    totalVotes: polls.reduce((sum, p) => sum + p.total_votes, 0),
  };

  const getDaysRemaining = (endDate) => {
    const end = new Date(endDate);
    const now = new Date();
    const diff = end - now;
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return days > 0 ? days : 0;
  };

  const handleCreatePoll = async (pollData) => {
    // TODO: Implement actual API call
    console.log('Creating poll:', pollData);
    
    // Mock success - in production, call the API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Invalidate queries to refetch data
    queryClient.invalidateQueries(['polls']);
    
    alert('Poll created successfully!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('polls')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('pollManagement')}
          </p>
        </div>
        <button 
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Poll
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <BarChart3 className="h-6 w-6 text-gray-400" />
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">{t('total')} {t('polls')}</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.total}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <Clock className="h-6 w-6 text-green-500" />
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">{t('activeStatus')}</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.active}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <CheckCircle className="h-6 w-6 text-blue-500" />
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Ended</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.ended}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <Users className="h-6 w-6 text-purple-500" />
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">{t('totalVotes')}</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.totalVotes}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search polls..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="ended">Ended</option>
          </select>
        </div>
      </div>

      {/* Polls List */}
      <div className="space-y-4">
        {filteredPolls.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No polls found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || filterStatus ? 'Try adjusting your filters.' : 'Get started by creating a new poll.'}
            </p>
          </div>
        ) : (
          filteredPolls.map((poll) => {
            const daysRemaining = getDaysRemaining(poll.end_date);
            const topOption = poll.options.reduce((max, opt) => opt.vote_count > max.vote_count ? opt : max, poll.options[0]);
            
            return (
              <div key={poll.id} className="bg-white shadow rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-medium text-gray-900">{poll.title}</h3>
                        {poll.is_active ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <Clock className="mr-1 h-3 w-3" />
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            <CheckCircle className="mr-1 h-3 w-3" />
                            Ended
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{poll.description}</p>
                    </div>
                  </div>

                  {/* Meta Info */}
                  <div className="flex items-center gap-4 mb-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 mr-1" />
                      {poll.ward_name}
                    </div>
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-1" />
                      {poll.total_votes} votes
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      {poll.is_active 
                        ? `${daysRemaining} days left`
                        : `Ended ${new Date(poll.end_date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}`
                      }
                    </div>
                  </div>

                  {/* Options with Results */}
                  <div className="space-y-2 mb-4">
                    {poll.options.map((option) => {
                      const percentage = poll.total_votes > 0 
                        ? Math.round((option.vote_count / poll.total_votes) * 100) 
                        : 0;
                      const isLeading = option.id === topOption.id;

                      return (
                        <div key={option.id} className="relative">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-gray-700">
                              {option.option_text}
                              {isLeading && poll.total_votes > 0 && (
                                <TrendingUp className="inline-block ml-2 h-4 w-4 text-green-600" />
                              )}
                            </span>
                            <span className="text-sm text-gray-600">
                              {option.vote_count} ({percentage}%)
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${
                                isLeading ? 'bg-green-500' : 'bg-primary-500'
                              }`}
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-4 border-t border-gray-200">
                    <Link
                      to={`/polls/${poll.id}`}
                      className="flex-1 text-center px-4 py-2 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 text-sm font-medium"
                    >
                      View Details
                    </Link>
                    <button className="flex-1 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 text-sm font-medium">
                      View Results
                    </button>
                    {poll.is_active && (
                      <button className="px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 text-sm font-medium">
                        End Poll
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Poll Creation Modal */}
      <PollCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={handleCreatePoll}
      />
    </div>
  );
}

export default Polls;
