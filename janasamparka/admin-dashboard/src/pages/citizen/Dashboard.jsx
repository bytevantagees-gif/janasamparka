import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  CheckCircle,
  Users,
  Building,
  Sparkles,
  Calendar,
  AlertCircle,
  ArrowRight,
  Award,
  Zap,
  Target,
  Clock,
  Video,
  Newspaper,
  Bell
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';

const CitizenDashboard = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [currentNewsIndex, setCurrentNewsIndex] = useState(0);

  // News ticker - highlighting MLA's work
  const newsTicker = [
    "🎉 156 complaints resolved this month - Fastest response time in Karnataka!",
    "🏗️ New community center construction approved - Work starts next week",
    "💧 Water supply restored in Ward 5 within 24 hours of complaint",
    "🌾 ₹8.5 Lakh in farm subsidies distributed to 23 farmers this week",
    "🎓 5 new scholarship applications approved for students",
    "🛣️ Road repair completed in Ward 3 - Under budget and ahead of schedule"
  ];

  // Auto-rotate news ticker
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentNewsIndex((prev) => (prev + 1) % newsTicker.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // MLA's Impact This Month - Big Numbers
  const impactMetrics = [
    {
      title: 'Issues Resolved',
      value: '156',
      subtitle: 'This Month',
      change: '+23% vs last month',
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      trend: 'up'
    },
    {
      title: 'Avg. Resolution Time',
      value: '3.2 days',
      subtitle: 'Faster than target',
      change: 'Target: 7 days',
      icon: Zap,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      trend: 'up'
    },
    {
      title: 'Citizens Helped',
      value: '1,247',
      subtitle: 'Direct Assistance',
      change: '+156 this month',
      icon: Users,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      trend: 'up'
    },
    {
      title: 'Budget Utilized',
      value: '₹2.4 Cr',
      subtitle: 'Development Work',
      change: '87% of allocation',
      icon: Target,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      trend: 'up'
    }
  ];

  // Recent Achievements - Making MLA look good
  const recentAchievements = [
    {
      title: 'Emergency Response',
      description: 'Water supply disruption fixed within 6 hours',
      impact: '2,300 families',
      date: '2 days ago',
      icon: '💧',
      status: 'Completed'
    },
    {
      title: 'Infrastructure Win',
      description: 'Street lights installed in 5 wards',
      impact: '89 new lights',
      date: '5 days ago',
      icon: '💡',
      status: 'Completed'
    },
    {
      title: 'Farmer Support',
      description: 'Crop insurance claims expedited',
      impact: '₹4.5L disbursed',
      date: '1 week ago',
      icon: '🌾',
      status: 'Completed'
    }
  ];

  // Ongoing Projects - Show progress
  const ongoingProjects = [
    {
      name: 'Community Health Center',
      location: 'Ward 7',
      progress: 75,
      expectedCompletion: 'Dec 2024',
      budget: '₹45 Lakhs',
      status: 'On Track'
    },
    {
      name: 'Road Infrastructure Upgrade',
      location: 'Multiple Wards',
      progress: 60,
      expectedCompletion: 'Jan 2025',
      budget: '₹1.2 Cr',
      status: 'On Track'
    },
    {
      name: 'Sports Complex',
      location: 'Ward 12',
      progress: 45,
      expectedCompletion: 'Mar 2025',
      budget: '₹85 Lakhs',
      status: 'On Track'
    }
  ];

  // Upcoming Events/Initiatives
  const upcomingEvents = [
    {
      title: 'Budget Town Hall Meeting',
      date: 'Nov 10, 2024',
      time: '6:00 PM',
      type: 'Live Stream',
      description: 'Discuss next quarter development plans'
    },
    {
      title: 'Health Camp',
      date: 'Nov 15, 2024',
      time: '10:00 AM',
      type: 'In-Person',
      description: 'Free health checkup for all citizens'
    },
    {
      title: 'Virtual Office Hours',
      date: 'Every Tuesday',
      time: '10:00 AM',
      type: 'Video Call',
      description: 'Book a slot to discuss your issues'
    }
  ];

  return (
    <div className="space-y-6">
      {/* News Ticker - Rotating MLA Achievements */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg overflow-hidden">
        <div className="px-6 py-4 flex items-center space-x-3">
          <Bell className="w-5 h-5 animate-pulse" />
          <div className="flex-1 overflow-hidden">
            <p className="font-medium animate-fade-in">{newsTicker[currentNewsIndex]}</p>
          </div>
          <div className="flex space-x-1">
            {newsTicker.map((_, idx) => (
              <div
                key={idx}
                className={`w-2 h-2 rounded-full transition-all ${
                  idx === currentNewsIndex ? 'bg-white' : 'bg-white/40'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Welcome Banner with MLA's commitment */}
      <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-pink-50 border-2 border-blue-200 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Welcome back, {user?.name}! 👋
            </h1>
            <p className="text-gray-700 text-lg">
              Your MLA is working hard for our constituency's development
            </p>
            <div className="mt-4 flex items-center space-x-4">
              <Link
                to="/citizen/video-consultation"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Video className="w-4 h-4 mr-2" />
                Book Video Call
              </Link>
              <Link
                to="/complaints/new"
                className="inline-flex items-center px-4 py-2 bg-white border-2 border-blue-600 text-blue-600 rounded-md hover:bg-blue-50"
              >
                <AlertCircle className="w-4 h-4 mr-2" />
                Report an Issue
              </Link>
            </div>
          </div>
          <div className="hidden md:block text-6xl">
            🏛️
          </div>
        </div>
      </div>

      {/* Impact Metrics - Big Numbers to Impress */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <Sparkles className="w-6 h-6 mr-2 text-yellow-500" />
          This Month's Impact
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {impactMetrics.map((metric, idx) => {
            const Icon = metric.icon;
            return (
              <div key={idx} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{metric.value}</p>
                    <p className="text-sm text-gray-600 mt-1">{metric.subtitle}</p>
                    <p className="text-xs text-green-600 mt-2 font-medium">{metric.change}</p>
                  </div>
                  <div className={`${metric.bgColor} p-3 rounded-lg`}>
                    <Icon className={`w-6 h-6 ${metric.color}`} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Achievements */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Award className="w-5 h-5 mr-2 text-yellow-500" />
              Recent Wins for Our Constituency
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentAchievements.map((achievement, idx) => (
                <div key={idx} className="border-l-4 border-green-500 bg-green-50 p-4 rounded-r-lg">
                  <div className="flex items-start space-x-3">
                    <div className="text-3xl">{achievement.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{achievement.title}</h3>
                      <p className="text-sm text-gray-700 mt-1">{achievement.description}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-sm font-medium text-green-700">
                          Impact: {achievement.impact}
                        </span>
                        <span className="text-xs text-gray-600">{achievement.date}</span>
                      </div>
                    </div>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  </div>
                </div>
              ))}
            </div>
            <Link
              to="/citizen/complaints"
              className="mt-4 inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
            >
              See all resolved issues <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
        </div>

        {/* Ongoing Projects */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Building className="w-5 h-5 mr-2 text-blue-600" />
              Development Projects in Progress
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {ongoingProjects.map((project, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{project.name}</h3>
                      <p className="text-sm text-gray-600">{project.location}</p>
                    </div>
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                      {project.status}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-medium text-gray-900">{project.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${project.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <span>Budget: {project.budget}</span>
                      <span>Expected: {project.expectedCompletion}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Events */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-purple-600" />
            Upcoming Events & Opportunities
          </h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {upcomingEvents.map((event, idx) => (
              <div key={idx} className="border-2 border-purple-200 rounded-lg p-4 bg-gradient-to-br from-purple-50 to-pink-50">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{event.title}</h3>
                  <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded-full">
                    {event.type}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-3">{event.description}</p>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Calendar className="w-4 h-4" />
                  <span>{event.date}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600 mt-1">
                  <Clock className="w-4 h-4" />
                  <span>{event.time}</span>
                </div>
                <button className="mt-3 w-full px-4 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700">
                  Register / Learn More
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions - Citizen Tools */}
      <div className="bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Link
            to="/citizen/video-consultation"
            className="flex flex-col items-center p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
          >
            <Video className="w-8 h-8 text-blue-600 mb-2" />
            <span className="text-sm font-medium text-gray-900 text-center">Book Video Call</span>
          </Link>
          <Link
            to="/complaints/new"
            className="flex flex-col items-center p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
          >
            <AlertCircle className="w-8 h-8 text-red-600 mb-2" />
            <span className="text-sm font-medium text-gray-900 text-center">Report Issue</span>
          </Link>
          <Link
            to="/citizen/agriculture-support"
            className="flex flex-col items-center p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
          >
            <TrendingUp className="w-8 h-8 text-green-600 mb-2" />
            <span className="text-sm font-medium text-gray-900 text-center">Agri Support</span>
          </Link>
          <Link
            to="/citizen/complaints"
            className="flex flex-col items-center p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
          >
            <Newspaper className="w-8 h-8 text-purple-600 mb-2" />
            <span className="text-sm font-medium text-gray-900 text-center">My Complaints</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default CitizenDashboard;
