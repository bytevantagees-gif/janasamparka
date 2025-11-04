import { useState } from 'react';
import { Video, Calendar, Clock, CheckCircle, AlertCircle, Phone } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';

const VideoConsultation = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [selectedSlot, setSelectedSlot] = useState(null);

  // Available time slots for booking
  const availableSlots = [
    {
      id: 1,
      date: '2024-11-05',
      day: 'Tuesday',
      time: '10:00 AM',
      available: true
    },
    {
      id: 2,
      date: '2024-11-05',
      day: 'Tuesday',
      time: '10:15 AM',
      available: true
    },
    {
      id: 3,
      date: '2024-11-05',
      day: 'Tuesday',
      time: '10:30 AM',
      available: false
    },
    {
      id: 4,
      date: '2024-11-07',
      day: 'Thursday',
      time: '2:00 PM',
      available: true
    },
    {
      id: 5,
      date: '2024-11-07',
      day: 'Thursday',
      time: '2:15 PM',
      available: true
    },
    {
      id: 6,
      date: '2024-11-09',
      day: 'Saturday',
      time: '10:00 AM',
      available: true
    }
  ];

  // User's upcoming bookings
  const myBookings = [
    {
      id: 1,
      date: '2024-11-05',
      time: '10:45 AM',
      status: 'Confirmed',
      meetingLink: 'https://meet.example.com/abc123'
    }
  ];

  // Upcoming town halls
  const townHalls = [
    {
      id: 1,
      title: 'Budget Discussion & Q&A',
      date: '2024-11-10',
      time: '6:00 PM',
      duration: '90 mins',
      registered: true,
      liveLink: 'https://youtube.com/live/xyz'
    },
    {
      id: 2,
      title: 'Infrastructure Development Update',
      date: '2024-11-15',
      time: '5:00 PM',
      duration: '60 mins',
      registered: false
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Video className="w-8 h-8 mr-3 text-blue-600" />
          Video Consultations with MLA
        </h1>
        <p className="text-gray-600 mt-1">Book a video call or join town hall meetings</p>
      </div>

      {/* My Upcoming Bookings */}
      {myBookings.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
            Your Upcoming Video Call
          </h2>
          {myBookings.map((booking) => (
            <div key={booking.id} className="bg-white rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-semibold text-gray-900">
                    {booking.date} at {booking.time}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">Duration: 10 minutes</p>
                </div>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  {booking.status}
                </span>
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-blue-900 font-medium mb-2">
                  <Phone className="w-4 h-4 inline mr-1" />
                  You will receive SMS with video call link 5 minutes before your slot
                </p>
                <button className="w-full mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  Join Video Call (Opens at scheduled time)
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Book New Video Consultation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Book Video Consultation</h2>
            <p className="text-sm text-gray-600 mt-1">Choose an available 10-minute slot</p>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {availableSlots.map((slot) => (
                <div
                  key={slot.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    !slot.available
                      ? 'bg-gray-50 border-gray-200 opacity-50 cursor-not-allowed'
                      : selectedSlot?.id === slot.id
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'
                  }`}
                  onClick={() => slot.available && setSelectedSlot(slot)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Calendar className="w-5 h-5 text-blue-600" />
                      <div>
                        <p className="font-medium text-gray-900">{slot.day}, {slot.date}</p>
                        <p className="text-sm text-gray-600">{slot.time}</p>
                      </div>
                    </div>
                    {slot.available ? (
                      <span className="text-sm text-green-600 font-medium">Available</span>
                    ) : (
                      <span className="text-sm text-red-600 font-medium">Booked</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {selectedSlot && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-900 font-medium mb-3">
                  Selected: {selectedSlot.day}, {selectedSlot.date} at {selectedSlot.time}
                </p>
                <button className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
                  Confirm Booking
                </button>
              </div>
            )}

            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-medium text-blue-900 mb-2">How it works:</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Select your preferred time slot</li>
                <li>✓ Receive confirmation SMS instantly</li>
                <li>✓ Get video call link 5 minutes before</li>
                <li>✓ Join from any smartphone or computer</li>
                <li>✓ Discuss your issue directly with MLA</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Town Hall Meetings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Upcoming Town Hall Meetings</h2>
            <p className="text-sm text-gray-600 mt-1">Watch live broadcasts & ask questions</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {townHalls.map((meeting) => (
                <div key={meeting.id} className="border-2 border-purple-200 rounded-lg p-4 bg-gradient-to-r from-purple-50 to-blue-50">
                  <h3 className="font-semibold text-gray-900 mb-2">{meeting.title}</h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      {meeting.date} at {meeting.time}
                    </p>
                    <p className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Duration: {meeting.duration}
                    </p>
                  </div>
                  <div className="mt-3">
                    {meeting.registered ? (
                      <div className="space-y-2">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          You're registered
                        </span>
                        <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700">
                          Join Live Stream
                        </button>
                      </div>
                    ) : (
                      <button className="w-full px-4 py-2 border-2 border-purple-600 text-purple-600 rounded-md hover:bg-purple-50">
                        Register for This Event
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
              <h3 className="font-medium text-purple-900 mb-2">Why attend town halls?</h3>
              <ul className="text-sm text-purple-800 space-y-1">
                <li>• Hear about development plans</li>
                <li>• Ask questions in Q&A session</li>
                <li>• See how budget is spent</li>
                <li>• Connect with other citizens</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="font-semibold text-yellow-900 mb-2">
          <AlertCircle className="w-5 h-5 inline mr-2" />
          Need immediate help?
        </h3>
        <p className="text-sm text-yellow-800 mb-3">
          For urgent issues, please submit a complaint instead of waiting for a video call slot.
        </p>
        <a href="/complaints/new" className="inline-flex items-center px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700">
          Submit Urgent Complaint →
        </a>
      </div>
    </div>
  );
};

export default VideoConsultation;
