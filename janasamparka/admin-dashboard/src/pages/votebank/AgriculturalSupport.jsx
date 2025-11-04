import { useState, useEffect } from 'react';
import { Sprout, TrendingUp, DollarSign, Users, CheckCircle, Clock, FileText, Award } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';

const AgriculturalSupport = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);

  // Impact metrics from your existing complaint system
  const impactMetrics = [
    {
      title: 'Agriculture Issues',
      value: '156',
      change: 'This month',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Issues Resolved',
      value: '142',
      change: '91% resolution rate',
      icon: CheckCircle,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Pending Issues',
      value: '14',
      change: 'Being addressed',
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    },
    {
      title: 'Avg. Resolution Time',
      value: '4.2 days',
      change: 'Target: 7 days',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  // Active support schemes
  const supportSchemes = [
    {
      id: 1,
      name: 'PM-KISAN Direct Benefit',
      description: '₹6,000/year direct to farmers',
      beneficiaries: 456,
      status: 'Active',
      amount: '₹27.36L distributed',
      icon: '🌾'
    },
    {
      id: 2,
      name: 'Crop Insurance Scheme',
      description: 'Protection against crop loss',
      beneficiaries: 312,
      status: 'Active',
      amount: '₹18.72L coverage',
      icon: '🛡️'
    },
    {
      id: 3,
      name: 'Soil Health Card',
      description: 'Free soil testing & recommendations',
      beneficiaries: 234,
      status: 'Active',
      amount: '234 cards issued',
      icon: '🔬'
    },
    {
      id: 4,
      name: 'Drip Irrigation Subsidy',
      description: '90% subsidy on irrigation systems',
      beneficiaries: 89,
      status: 'Active',
      amount: '₹12.5L subsidy',
      icon: '💧'
    }
  ];

  // Recent agriculture-related complaints resolved (from existing complaint system)
  const recentResolutions = [
    {
      id: 'CMP001',
      citizen: 'Ramesh Kumar',
      issue: 'Irrigation canal repair needed',
      date: '2024-10-28',
      status: 'Resolved',
      category: 'Water Supply',
      resolutionDays: 3
    },
    {
      id: 'CMP002',
      citizen: 'Lakshmi Devi',
      issue: 'Farm road in bad condition',
      date: '2024-10-27',
      status: 'Resolved',
      category: 'Road Infrastructure',
      resolutionDays: 5
    },
    {
      id: 'CMP003',
      citizen: 'Suresh Gowda',
      issue: 'Electricity supply to pump',
      date: '2024-10-29',
      status: 'In Progress',
      category: 'Electricity',
      resolutionDays: 2
    },
    {
      id: 'CMP004',
      citizen: 'Manjula Bhat',
      issue: 'Pesticide subsidy query',
      date: '2024-10-26',
      status: 'Resolved',
      category: 'Agriculture',
      resolutionDays: 1
    }
  ];

  // Success stories showcasing impact
  const successStories = [
    {
      name: 'Mohan Hegde',
      achievement: 'Increased crop yield by 40% using drip irrigation',
      scheme: 'Drip Irrigation Subsidy',
      image: '👨‍🌾'
    },
    {
      name: 'Savita Patil',
      achievement: 'Started organic farming, earning ₹3L more annually',
      scheme: 'Organic Farming Support',
      image: '👩‍🌾'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Sprout className="w-8 h-8 mr-3 text-green-600" />
            Agricultural Support Hub
          </h1>
          <p className="text-gray-600 mt-1">Track and resolve agriculture-related complaints efficiently</p>
        </div>
        <a href="/complaints?category=agriculture" className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
          <FileText className="w-4 h-4 mr-2" />
          View All Agriculture Issues
        </a>
      </div>

      {/* Impact Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {impactMetrics.map((metric, idx) => {
          const Icon = metric.icon;
          return (
            <div key={idx} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{metric.value}</p>
                  <p className="text-sm text-green-600 mt-1">{metric.change}</p>
                </div>
                <div className={`${metric.bgColor} p-3 rounded-lg`}>
                  <Icon className={`w-6 h-6 ${metric.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Support Schemes - Informational */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Active Government Schemes</h2>
          <p className="text-sm text-gray-600 mt-1">Reference information for farmers - help citizens apply through proper channels</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {supportSchemes.map((scheme) => (
              <div key={scheme.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start space-x-3">
                  <div className="text-3xl">{scheme.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{scheme.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{scheme.description}</p>
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-700">
                          <Users className="w-4 h-4 inline mr-1" />
                          {scheme.beneficiaries} beneficiaries
                        </span>
                      </div>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {scheme.status}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-green-600 mt-2">{scheme.amount}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Agriculture Issues Resolved */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Agriculture Issues Resolved</h2>
            <p className="text-sm text-gray-600 mt-1">From your existing complaint tracking system</p>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {recentResolutions.map((complaint) => (
                <div key={complaint.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-gray-900">{complaint.citizen}</p>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        complaint.status === 'Resolved' ? 'bg-green-100 text-green-800' :
                        complaint.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {complaint.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-1">{complaint.issue}</p>
                    <div className="flex items-center space-x-3 mt-2 text-xs text-gray-500">
                      <span className="inline-flex items-center px-2 py-1 rounded-full bg-gray-200 text-gray-700">
                        {complaint.category}
                      </span>
                      <span>•</span>
                      <span className="text-green-600">Resolved in {complaint.resolutionDays} days</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <a href="/complaints?category=agriculture" className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                View all agriculture complaints →
              </a>
            </div>
          </div>
        </div>

        {/* Success Stories */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Award className="w-5 h-5 mr-2 text-yellow-500" />
              Success Stories
            </h2>
            <p className="text-sm text-gray-600 mt-1">Impact of our support initiatives</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {successStories.map((story, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-gradient-to-r from-green-50 to-blue-50">
                  <div className="flex items-start space-x-3">
                    <div className="text-4xl">{story.image}</div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900">{story.name}</p>
                      <p className="text-sm text-gray-700 mt-1">{story.achievement}</p>
                      <p className="text-xs text-green-600 mt-2 font-medium">via {story.scheme}</p>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Call to Action */}
              <div className="border-2 border-dashed border-green-300 rounded-lg p-4 text-center bg-green-50">
                <Sprout className="w-8 h-8 mx-auto text-green-600 mb-2" />
                <p className="text-sm font-medium text-gray-900">Have a success story?</p>
                <p className="text-xs text-gray-600 mt-1">Share how our support helped you</p>
                <button className="mt-3 px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700">
                  Share Your Story
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Market Information Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
            Market Price Information
          </h2>
          <p className="text-sm text-gray-600 mt-1">Latest market rates to help farmers make informed decisions</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-600">Rice (Quintal)</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">₹2,850</p>
              <p className="text-xs text-green-600 mt-1">↑ ₹50 from last week</p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-600">Areca Nut (Quintal)</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">₹45,000</p>
              <p className="text-xs text-red-600 mt-1">↓ ₹1,000 from last week</p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-600">Coconut (100 nos)</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">₹3,200</p>
              <p className="text-xs text-green-600 mt-1">↑ ₹100 from last week</p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-600">Vegetables (Avg)</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">₹25/kg</p>
              <p className="text-xs text-gray-600 mt-1">Stable</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgriculturalSupport;
