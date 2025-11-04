import { useState, useEffect } from 'react';
import { Users, TrendingUp, Building, Sprout, GraduationCap } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from '../../hooks/useTranslation';

const VotebankDashboard = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    farmers: 0,
    businesses: 0,
    youth: 0,
    programs: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Fetch analytics from the dedicated dashboard endpoint
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/votebank/analytics/dashboard`,
        { headers }
      );

      if (response.ok) {
        const data = await response.json();
        setStats({
          farmers: data.farmer_engagement?.total_farmers || 0,
          businesses: data.business_engagement?.total_businesses || 0,
          youth: data.youth_engagement?.total_youth || 0,
          programs: data.youth_engagement?.active_programs || 0
        });
      } else {
        throw new Error('Failed to fetch analytics');
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      // Set default values for demo
      setStats({
        farmers: 12,
        businesses: 8,
        youth: 25,
        programs: 6
      });
    } finally {
      setLoading(false);
    }
  };

  const menuItems = [
    {
      title: 'Agricultural Support',
      description: 'Track agriculture-related complaints efficiently',
      icon: Sprout,
      count: '156',
      metric: 'Issues This Month',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      href: '/votebank/farmers'
    },
    {
      title: 'Video Consultations',
      description: 'Virtual office hours & town hall meetings',
      icon: Building,
      count: '127',
      metric: 'Video Calls',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      href: '/votebank/businesses'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Citizen Services & Impact</h1>
          <p className="text-gray-600 mt-1">Delivering government services and tracking community impact</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <TrendingUp className="w-4 h-4 mr-1" />
            2,183 Citizens Helped This Month
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.title} className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-200">
              <a href={item.href} className="block">
                <div className="p-6">
                  <div className={`w-12 h-12 rounded-lg ${item.bgColor} flex items-center justify-center mb-4`}>
                    <Icon className={`w-6 h-6 ${item.color}`} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-sm text-gray-600 mb-4">{item.description}</p>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{item.count}</p>
                      <p className="text-xs text-gray-500 mt-1">{item.metric}</p>
                    </div>
                    <button className="text-gray-400 hover:text-gray-600">
                      →
                    </button>
                  </div>
                </div>
              </a>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('recent_activities')}</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center space-x-3">
                  <Sprout className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="font-medium">₹8.5L in farm subsidies approved</p>
                    <p className="text-sm text-gray-600">23 farmers benefited today</p>
                  </div>
                </div>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">✓ Approved</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-3">
                  <Building className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium">5 business licenses expedited</p>
                    <p className="text-sm text-gray-600">Avg. processing: 2 days</p>
                  </div>
                </div>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Fast Track</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-center space-x-3">
                  <GraduationCap className="w-5 h-5 text-purple-600" />
                  <div>
                    <p className="font-medium">34 youth placed in jobs</p>
                    <p className="text-sm text-gray-600">Via skill training program</p>
                  </div>
                </div>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">This Week</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('quick_actions')}</h2>
            <div className="space-y-3">
              <button className="w-full flex items-center justify-start px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700">
                <Sprout className="w-4 h-4 mr-2" />
                Process Farm Scheme Application
              </button>
              <button className="w-full flex items-center justify-start px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                <Building className="w-4 h-4 mr-2" />
                Expedite Business License
              </button>
              <button className="w-full flex items-center justify-start px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                <GraduationCap className="w-4 h-4 mr-2" />
                Review Job Placement Requests
              </button>
              <button className="w-full flex items-center justify-start px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                <Users className="w-4 h-4 mr-2" />
                View Impact Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VotebankDashboard;
