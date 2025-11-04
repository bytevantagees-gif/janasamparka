import { useState } from 'react';
import { Sprout, TrendingUp, Phone, FileText, ExternalLink, Calendar } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';

const AgricultureSupport = () => {
  const { t } = useTranslation();
  const { user } = useAuth();

  // Government schemes available
  const schemes = [
    {
      id: 1,
      name: 'PM-KISAN',
      description: '₹6,000 per year direct benefit transfer',
      eligibility: 'All farmer families',
      howToApply: 'Visit nearest CSC or apply online',
      link: 'https://pmkisan.gov.in',
      icon: '🌾',
      benefits: '₹2,000 every 4 months'
    },
    {
      id: 2,
      name: 'Crop Insurance (PMFBY)',
      description: 'Protection against crop loss due to natural calamities',
      eligibility: 'All farmers (loanee & non-loanee)',
      howToApply: 'Through banks or CSC before sowing',
      link: 'https://pmfby.gov.in',
      icon: '🛡️',
      benefits: 'Up to 100% crop value coverage'
    },
    {
      id: 3,
      name: 'Soil Health Card',
      description: 'Free soil testing and recommendations',
      eligibility: 'All farmers',
      howToApply: 'Submit soil sample at agriculture office',
      link: null,
      icon: '🔬',
      benefits: 'Free soil analysis & advice'
    },
    {
      id: 4,
      name: 'Drip Irrigation Subsidy',
      description: '90% subsidy on micro-irrigation systems',
      eligibility: 'Small & marginal farmers',
      howToApply: 'Apply through agriculture department',
      link: null,
      icon: '💧',
      benefits: '90% subsidy on installation'
    }
  ];

  // Market prices
  const marketPrices = [
    { crop: 'Rice', unit: 'Quintal', price: '₹2,850', change: '+50', trend: 'up' },
    { crop: 'Areca Nut', unit: 'Quintal', price: '₹45,000', change: '-1,000', trend: 'down' },
    { crop: 'Coconut', unit: '100 nos', price: '₹3,200', change: '+100', trend: 'up' },
    { crop: 'Vegetables', unit: 'Kg (Avg)', price: '₹25', change: '0', trend: 'stable' }
  ];

  // Expert consultations available
  const expertSessions = [
    {
      expert: 'Dr. Ramesh Kumar',
      expertise: 'Agricultural Expert',
      topic: 'Crop Disease Prevention',
      nextSession: '2024-11-06 at 11:00 AM',
      available: true
    },
    {
      expert: 'Prof. Lakshmi Devi',
      expertise: 'Organic Farming Specialist',
      topic: 'Natural Pest Control Methods',
      nextSession: '2024-11-09 at 2:00 PM',
      available: true
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Sprout className="w-8 h-8 mr-3 text-green-600" />
          Agricultural Support & Information
        </h1>
        <p className="text-gray-600 mt-1">Access government schemes, market prices, and expert advice</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a href="/complaints/new?category=agriculture" className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow">
          <FileText className="w-6 h-6 text-green-600 mb-2" />
          <h3 className="font-semibold text-gray-900">Report Farm Issue</h3>
          <p className="text-sm text-gray-600 mt-1">Irrigation, electricity, road problems</p>
        </a>
        <a href="/citizen/video-consultation" className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg p-4 hover:shadow-md transition-shadow">
          <Phone className="w-6 h-6 text-blue-600 mb-2" />
          <h3 className="font-semibold text-gray-900">Talk to MLA</h3>
          <p className="text-sm text-gray-600 mt-1">Book video consultation slot</p>
        </a>
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-4">
          <Calendar className="w-6 h-6 text-purple-600 mb-2" />
          <h3 className="font-semibold text-gray-900">Expert Sessions</h3>
          <p className="text-sm text-gray-600 mt-1">Free agricultural advice</p>
        </div>
      </div>

      {/* Government Schemes */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Government Schemes for Farmers</h2>
          <p className="text-sm text-gray-600 mt-1">Available subsidies and support programs</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {schemes.map((scheme) => (
              <div key={scheme.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start space-x-3">
                  <div className="text-3xl">{scheme.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{scheme.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{scheme.description}</p>
                    <div className="mt-3 space-y-2 text-sm">
                      <div className="flex items-start">
                        <span className="font-medium text-gray-700 min-w-[80px]">Eligibility:</span>
                        <span className="text-gray-600">{scheme.eligibility}</span>
                      </div>
                      <div className="flex items-start">
                        <span className="font-medium text-gray-700 min-w-[80px]">Benefits:</span>
                        <span className="text-green-600 font-medium">{scheme.benefits}</span>
                      </div>
                      <div className="flex items-start">
                        <span className="font-medium text-gray-700 min-w-[80px]">How to apply:</span>
                        <span className="text-gray-600">{scheme.howToApply}</span>
                      </div>
                    </div>
                    {scheme.link ? (
                      <a
                        href={scheme.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-3 inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                      >
                        Apply Online <ExternalLink className="w-3 h-3 ml-1" />
                      </a>
                    ) : (
                      <p className="mt-3 text-sm text-gray-600">
                        Visit agriculture office or call helpline
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Prices */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
              Today's Market Prices
            </h2>
            <p className="text-sm text-gray-600 mt-1">Latest rates from local mandis</p>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {marketPrices.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{item.crop}</p>
                    <p className="text-xs text-gray-600">{item.unit}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{item.price}</p>
                    <p className={`text-xs ${
                      item.trend === 'up' ? 'text-green-600' :
                      item.trend === 'down' ? 'text-red-600' :
                      'text-gray-600'
                    }`}>
                      {item.trend === 'up' && `↑ ${item.change}`}
                      {item.trend === 'down' && `↓ ${item.change}`}
                      {item.trend === 'stable' && 'Stable'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs text-gray-500">
              Last updated: Today at 9:00 AM
            </p>
          </div>
        </div>

        {/* Expert Consultations */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Free Expert Consultations</h2>
            <p className="text-sm text-gray-600 mt-1">Video sessions with agricultural experts</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {expertSessions.map((session, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                      {session.expert.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{session.expert}</h3>
                      <p className="text-sm text-blue-600">{session.expertise}</p>
                      <p className="text-sm text-gray-700 mt-2 font-medium">{session.topic}</p>
                      <p className="text-xs text-gray-600 mt-1">{session.nextSession}</p>
                      <button className="mt-3 w-full px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700">
                        Book Free Session
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 className="font-semibold text-green-900 mb-2">
          <Sprout className="w-5 h-5 inline mr-2" />
          Agriculture Helpline
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
          <div className="bg-white rounded-lg p-3">
            <p className="text-sm text-gray-600">Irrigation Issues</p>
            <p className="text-lg font-bold text-green-600">1800-123-4567</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-sm text-gray-600">Pest Control Advice</p>
            <p className="text-lg font-bold text-green-600">1800-123-4568</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-sm text-gray-600">Scheme Information</p>
            <p className="text-lg font-bold text-green-600">1800-123-4569</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgricultureSupport;
