import { useState } from 'react';
import { Video, Calendar, Users, Clock, Phone, MessageSquare, FileText, PlayCircle, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';

const CitizenEngagement = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('video-office');

  // Virtual Office Hours - Citizens can book video calls with MLA
  const virtualOfficeHours = [
    {
      id: 1,
      date: '2024-11-05',
      day: 'Tuesday',
      time: '10:00 AM - 12:00 PM',
      slotsTotal: 12,
      slotsBooked: 8,
      slotsAvailable: 4,
      status: 'Available'
    },
    {
      id: 2,
      date: '2024-11-07',
      day: 'Thursday',
      time: '2:00 PM - 4:00 PM',
      slotsTotal: 12,
      slotsBooked: 12,
      slotsAvailable: 0,
      status: 'Full'
    },
    {
      id: 3,
      date: '2024-11-09',
      day: 'Saturday',
      time: '10:00 AM - 1:00 PM',
      slotsTotal: 18,
      slotsBooked: 5,
      slotsAvailable: 13,
      status: 'Available'
    }
  ];

  // Upcoming Town Halls - Live video broadcasts
  const upcomingTownHalls = [
    {
      id: 1,
      title: 'Budget Discussion & Q&A',
      date: '2024-11-10',
      time: '6:00 PM',
      duration: '90 mins',
      registered: 234,
      platform: 'Live Stream',
      status: 'Upcoming'
    },
    {
      id: 2,
      title: 'Infrastructure Development Update',
      date: '2024-11-15',
      time: '5:00 PM',
      duration: '60 mins',
      registered: 156,
      platform: 'Live Stream',
      status: 'Upcoming'
    }
  ];

  // Past Video Consultations
  const recentConsultations = [
    {
      id: 1,
      citizen: 'Rajesh Kumar',
      issue: 'Road repair in Ward 5',
      date: '2024-11-01',
      duration: '15 mins',
      status: 'Resolved',
      followUp: 'Work order issued'
    },
    {
      id: 2,
      citizen: 'Priya Sharma',
      issue: 'Water supply complaint',
      date: '2024-10-30',
      duration: '12 mins',
      status: 'In Progress',
      followUp: 'Department notified'
    },
    {
      id: 3,
      citizen: 'Mohan Rao',
      issue: 'Street light installation',
      date: '2024-10-28',
      duration: '10 mins',
      status: 'Resolved',
      followUp: 'Installed within 3 days'
    }
  ];

  // Expert Advisory Sessions
  const expertSessions = [
    {
      id: 1,
      expert: 'Dr. Ramesh Kumar',
      expertise: 'Agricultural Expert',
      topic: 'Crop Disease Prevention',
      nextSession: '2024-11-06',
      time: '11:00 AM',
      duration: '45 mins',
      bookings: 23
    },
    {
      id: 2,
      expert: 'Adv. Lakshmi Bai',
      expertise: 'Legal Aid',
      topic: 'Property Disputes',
      nextSession: '2024-11-08',
      time: '3:00 PM',
      duration: '60 mins',
      bookings: 18
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Video className="w-8 h-8 mr-3 text-blue-600" />
            Citizen Engagement Platform
          </h1>
          <p className="text-gray-600 mt-1">Connect citizens with MLA through video consultations and virtual meetings</p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">This Month</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">127</p>
              <p className="text-sm text-green-600 mt-1">Video Consultations</p>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <Video className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Avg. Resolution</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">2.3 days</p>
              <p className="text-sm text-green-600 mt-1">From video calls</p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <Clock className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Town Halls</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">3</p>
              <p className="text-sm text-blue-600 mt-1">This month</p>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Citizen Reach</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">1,847</p>
              <p className="text-sm text-purple-600 mt-1">Total participants</p>
            </div>
            <div className="bg-orange-50 p-3 rounded-lg">
              <Users className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 border-b">
        <button
          onClick={() => setActiveTab('video-office')}
          className={`pb-2 px-1 ${activeTab === 'video-office' 
            ? 'border-b-2 border-blue-600 text-blue-600 font-medium' 
            : 'text-gray-600 hover:text-gray-900'}`}
        >
          <Video className="w-4 h-4 inline mr-1" />
          Virtual Office Hours
        </button>
        <button
          onClick={() => setActiveTab('town-halls')}
          className={`pb-2 px-1 ${activeTab === 'town-halls' 
            ? 'border-b-2 border-blue-600 text-blue-600 font-medium' 
            : 'text-gray-600 hover:text-gray-900'}`}
        >
          <Users className="w-4 h-4 inline mr-1" />
          Town Hall Meetings
        </button>
        <button
          onClick={() => setActiveTab('expert-sessions')}
          className={`pb-2 px-1 ${activeTab === 'expert-sessions' 
            ? 'border-b-2 border-blue-600 text-blue-600 font-medium' 
            : 'text-gray-600 hover:text-gray-900'}`}
        >
          <MessageSquare className="w-4 h-4 inline mr-1" />
          Expert Advisory
        </button>
        <button
          onClick={() => setActiveTab('past-consultations')}
          className={`pb-2 px-1 ${activeTab === 'past-consultations' 
            ? 'border-b-2 border-blue-600 text-blue-600 font-medium' 
            : 'text-gray-600 hover:text-gray-900'}`}
        >
          <FileText className="w-4 h-4 inline mr-1" />
          Past Consultations
        </button>
      </div>

      {/* Virtual Office Hours Tab */}
      {activeTab === 'video-office' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Book Video Consultation</h2>
              <p className="text-sm text-gray-600 mt-1">Schedule one-on-one video calls with MLA</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {virtualOfficeHours.map((slot) => (
                  <div key={slot.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <Calendar className="w-5 h-5 text-blue-600" />
                          <div>
                            <p className="font-semibold text-gray-900">{slot.day}, {slot.date}</p>
                            <p className="text-sm text-gray-600">{slot.time}</p>
                          </div>
                        </div>
                        <div className="mt-3 flex items-center space-x-4">
                          <div className="flex items-center space-x-2">
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${slot.slotsAvailable > 0 ? 'bg-green-600' : 'bg-red-600'}`}
                                style={{ width: `${(slot.slotsBooked / slot.slotsTotal) * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600">
                              {slot.slotsBooked}/{slot.slotsTotal} booked
                            </span>
                          </div>
                        </div>
                      </div>
                      <div>
                        {slot.slotsAvailable > 0 ? (
                          <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">
                            Book Slot
                          </button>
                        ) : (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Full
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-medium text-blue-900 flex items-center">
                  <Phone className="w-4 h-4 mr-2" />
                  How it works
                </h3>
                <ul className="mt-2 text-sm text-blue-800 space-y-1">
                  <li>• Book a 10-minute slot</li>
                  <li>• Receive video call link via SMS</li>
                  <li>• Join from any smartphone or computer</li>
                  <li>• Discuss your issue directly with MLA</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Today's Schedule</h2>
              <p className="text-sm text-gray-600 mt-1">Upcoming video consultations</p>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {[
                  { time: '10:00 AM', citizen: 'Ramesh Kumar', issue: 'Road repair', status: 'In Progress' },
                  { time: '10:15 AM', citizen: 'Lakshmi Devi', issue: 'Water supply', status: 'Waiting' },
                  { time: '10:30 AM', citizen: 'Suresh Gowda', issue: 'Electricity', status: 'Scheduled' },
                  { time: '10:45 AM', citizen: 'Priya Sharma', issue: 'Property tax', status: 'Scheduled' }
                ].map((appointment, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="flex flex-col items-center">
                        <Clock className="w-5 h-5 text-gray-400" />
                        <span className="text-xs text-gray-600 mt-1">{appointment.time}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{appointment.citizen}</p>
                        <p className="text-sm text-gray-600">{appointment.issue}</p>
                      </div>
                    </div>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      appointment.status === 'In Progress' ? 'bg-green-100 text-green-800' :
                      appointment.status === 'Waiting' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {appointment.status}
                    </span>
                  </div>
                ))}
              </div>
              <button className="mt-6 w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center justify-center">
                <PlayCircle className="w-4 h-4 mr-2" />
                Start Next Consultation
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Town Hall Meetings Tab */}
      {activeTab === 'town-halls' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Upcoming Town Halls</h2>
              <p className="text-sm text-gray-600 mt-1">Live video broadcasts for all citizens</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {upcomingTownHalls.map((meeting) => (
                  <div key={meeting.id} className="border-2 border-purple-200 rounded-lg p-4 bg-gradient-to-r from-purple-50 to-blue-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 flex items-center">
                          <Video className="w-5 h-5 mr-2 text-purple-600" />
                          {meeting.title}
                        </h3>
                        <div className="mt-3 space-y-2">
                          <div className="flex items-center space-x-4 text-sm text-gray-600">
                            <span className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              {meeting.date}
                            </span>
                            <span className="flex items-center">
                              <Clock className="w-4 h-4 mr-1" />
                              {meeting.time}
                            </span>
                          </div>
                          <div className="flex items-center space-x-4 text-sm">
                            <span className="text-gray-600">{meeting.duration}</span>
                            <span className="text-purple-600 font-medium">{meeting.registered} registered</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 flex space-x-2">
                      <button className="flex-1 px-4 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700">
                        Join Live Stream
                      </button>
                      <button className="px-4 py-2 border border-purple-600 text-purple-600 text-sm rounded-md hover:bg-purple-50">
                        Set Reminder
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Past Town Halls</h2>
              <p className="text-sm text-gray-600 mt-1">Watch recordings</p>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {[
                  { title: 'Healthcare Improvements', date: '2024-10-25', views: 1234, duration: '85 mins' },
                  { title: 'Education Initiatives', date: '2024-10-18', views: 987, duration: '75 mins' },
                  { title: 'Road Development Plan', date: '2024-10-10', views: 1456, duration: '60 mins' }
                ].map((past, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{past.title}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                          <span>{past.date}</span>
                          <span>•</span>
                          <span>{past.duration}</span>
                          <span>•</span>
                          <span>{past.views} views</span>
                        </div>
                      </div>
                      <PlayCircle className="w-8 h-8 text-blue-600" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Expert Advisory Tab */}
      {activeTab === 'expert-sessions' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Expert Advisory Sessions</h2>
            <p className="text-sm text-gray-600 mt-1">Free video consultations with subject matter experts</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {expertSessions.map((session) => (
                <div key={session.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {session.expert.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{session.expert}</h3>
                      <p className="text-sm text-blue-600">{session.expertise}</p>
                      <p className="text-sm text-gray-700 mt-2 font-medium">{session.topic}</p>
                      <div className="mt-3 flex items-center justify-between">
                        <div className="text-sm text-gray-600">
                          <p>{session.nextSession}</p>
                          <p>{session.time} • {session.duration}</p>
                        </div>
                        <span className="text-sm text-gray-600">{session.bookings} booked</span>
                      </div>
                      <button className="mt-3 w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">
                        Book Session
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Past Consultations Tab */}
      {activeTab === 'past-consultations' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Past Video Consultations</h2>
            <p className="text-sm text-gray-600 mt-1">Track resolution of issues discussed in video calls</p>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {recentConsultations.map((consultation) => (
                <div key={consultation.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-gray-900">{consultation.citizen}</p>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          consultation.status === 'Resolved' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {consultation.status === 'Resolved' ? <CheckCircle className="w-3 h-3 mr-1" /> : <AlertCircle className="w-3 h-3 mr-1" />}
                          {consultation.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mt-1">{consultation.issue}</p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                        <span>{consultation.date}</span>
                        <span>•</span>
                        <span>{consultation.duration}</span>
                      </div>
                      <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-800">
                        <strong>Follow-up:</strong> {consultation.followUp}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CitizenEngagement;
