import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { Phone, Lock, Loader2, Key, AlertCircle } from 'lucide-react';
import ConstituencySelector from '../components/ConstituencySelector';
import { authAPI } from '../services/api';
import emblem from '../assets/karnataka-emblem.svg';

function Login() {
  const { t } = useTranslation();
  const [step, setStep] = useState('phone'); // 'phone', 'otp', 'constituency', or 'code'
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [accessCode, setAccessCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [otpData, setOtpData] = useState(null);
  const [rememberMe, setRememberMe] = useState(false);

  const { requestOTP, verifyOTP, user, login } = useAuth();
  const navigate = useNavigate();

  const handleRequestOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await requestOTP(phone);
      setOtpData(data);
      setStep('otp');
      // In development, auto-fill OTP
      if (data.otp) {
        setOtp(data.otp);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const userData = await verifyOTP(phone, otp);
      
      // Store remember me preference
      if (rememberMe) {
        localStorage.setItem('remember_me', 'true');
      } else {
        localStorage.removeItem('remember_me');
      }

      // Check if citizen needs to select constituency
      if (userData.role === 'citizen' && !userData.constituency_id) {
        setStep('constituency');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConstituencyComplete = () => {
    navigate('/dashboard');
  };

  const handleBack = () => {
    setStep('phone');
    setOtp('');
    setAccessCode('');
    setError('');
    setOtpData(null);
  };

  const handleUseCode = () => {
    setStep('code');
    setError('');
  };

  const handleLoginWithCode = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.loginWithCode(accessCode);
      
      // Store tokens
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      
      // Store user data
      const userData = response.data.user;
      
      // Store remember me preference
      if (rememberMe) {
        localStorage.setItem('remember_me', 'true');
      } else {
        localStorage.removeItem('remember_me');
      }

      // Call login to update auth context
      if (login) {
        login(userData, response.data.access_token, response.data.refresh_token);
      }

      // Check if citizen needs to select constituency
      if (userData.role === 'citizen' && !userData.constituency_id) {
        setStep('constituency');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid or expired access code');
    } finally {
      setLoading(false);
    }
  };

  // Show constituency selector if needed
  if (step === 'constituency') {
    return <ConstituencySelector onComplete={handleConstituencyComplete} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img 
              src={emblem} 
              alt="Government of Karnataka" 
              className="h-24 w-24 drop-shadow-lg animate-pulse"
            />
          </div>
          <h1 className="text-4xl font-bold text-primary-700 mb-2">ಜನಸಂಪರ್ಕ</h1>
          <p className="text-gray-600 text-lg">Jana Samparka - MLA Connect</p>
          <p className="text-gray-500 text-sm">Government of Karnataka</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {step === 'phone' ? (
            <>
              <div className="flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mx-auto mb-4">
                <Phone className="w-8 h-8 text-primary-600" />
              </div>
              
              <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">
                {t('welcomeBack')}
              </h2>
              <p className="text-center text-gray-600 mb-6">
                {t('enterPhoneNumber')}
              </p>

              <form onSubmit={handleRequestOTP}>
                <div className="mb-4">
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('phoneNumber')}
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                    pattern="^\+?[0-9]{10,15}$"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Enter phone number with country code (e.g., +919876543210)
                  </p>
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin mr-2 h-5 w-5" />
                      {t('loading')}...
                    </>
                  ) : (
                    t('requestOTP')
                  )}
                </button>
              </form>

              {/* Alternative Login Option */}
              <div className="mt-6 text-center">
                <button
                  onClick={handleUseCode}
                  className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  <Key className="h-4 w-4 mr-2" />
                  Phone broken? Use temporary code
                </button>
              </div>

              {/* Quick Test Logins - Real Database Users */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-xs text-center text-gray-500 mb-3">Quick Test Login (Real Accounts)</p>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {/* Admin */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">👨‍💼 Admin</p>
                    <button
                      onClick={() => setPhone('+919999999999')}
                      className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div className="font-medium">Admin User</div>
                      <div className="text-xs text-gray-500">+919999999999</div>
                    </button>
                  </div>

                  {/* MLAs */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">🏛️ MLAs</p>
                    <div className="space-y-1">
                      {[
                        { phone: '+918242226666', name: 'Ashok Kumar Rai', label: 'Puttur' },
                        { phone: '+91991000001', name: 'MLA Puttur', label: 'Puttur' },
                        { phone: '+91991000002', name: 'MLA Bantwal', label: 'Bantwal' },
                        { phone: '+91991000003', name: 'MLA Mangalore City South', label: 'Mangalore' },
                      ].map((user) => (
                        <button
                          key={user.phone}
                          onClick={() => setPhone(user.phone)}
                          className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200"
                        >
                          <div className="font-medium">{user.name}</div>
                          <div className="text-xs text-gray-500">{user.phone} • {user.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Moderators */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">👮 Moderators</p>
                    <div className="space-y-1">
                      {[
                        { phone: '+919900000000', name: 'Puttur Moderator', label: 'Puttur' },
                        { phone: '+919900000001', name: 'Mangalore North Moderator', label: 'Mangalore' },
                        { phone: '+919900000002', name: 'Udupi Moderator', label: 'Udupi' },
                      ].map((user) => (
                        <button
                          key={user.phone}
                          onClick={() => setPhone(user.phone)}
                          className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200"
                        >
                          <div className="font-medium">{user.name}</div>
                          <div className="text-xs text-gray-500">{user.phone} • {user.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Department Officers */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">🏢 Department Officers</p>
                    <div className="space-y-1">
                      {[
                        { phone: '+9199001000', name: 'PWD Officer - Puttur', label: 'Puttur' },
                        { phone: '+9199002000', name: 'Water Officer - Puttur', label: 'Puttur' },
                        { phone: '+9199003000', name: 'Electricity Officer - Puttur', label: 'Puttur' },
                        { phone: '+9199001100', name: 'PWD Officer - Mangalore', label: 'Mangalore' },
                        { phone: '+9199002100', name: 'Water Officer - Mangalore', label: 'Mangalore' },
                        { phone: '+9199003100', name: 'Electricity Officer - Mangalore', label: 'Mangalore' },
                        { phone: '+9199001200', name: 'PWD Officer - Udupi', label: 'Udupi' },
                        { phone: '+9199002200', name: 'Water Officer - Udupi', label: 'Udupi' },
                        { phone: '+9199003200', name: 'Electricity Officer - Udupi', label: 'Udupi' },
                      ].map((user) => (
                        <button
                          key={user.phone}
                          onClick={() => setPhone(user.phone)}
                          className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200"
                        >
                          <div className="font-medium">{user.name}</div>
                          <div className="text-xs text-gray-500">{user.phone} • {user.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Auditors */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">📊 Auditors</p>
                    <div className="space-y-1">
                      {[
                        { phone: '+9199006000', name: 'Auditor - Puttur', label: 'Puttur' },
                        { phone: '+9199006001', name: 'Auditor - Mangalore North', label: 'Mangalore' },
                        { phone: '+9199006002', name: 'Auditor - Udupi', label: 'Udupi' },
                      ].map((user) => (
                        <button
                          key={user.phone}
                          onClick={() => setPhone(user.phone)}
                          className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200"
                        >
                          <div className="font-medium">{user.name}</div>
                          <div className="text-xs text-gray-500">{user.phone} • {user.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Citizens */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">👥 Citizens</p>
                    <div className="space-y-1">
                      {[
                        { phone: '+919876543214', name: 'Lakshmi Bhat' },
                        { phone: '+919876543216', name: 'Kavitha Nayak' },
                        { phone: '+919876543219', name: 'Harish Bhandary' },
                        { phone: '+919876543222', name: 'Anitha Hegde' },
                      ].map((user) => (
                        <button
                          key={user.phone}
                          onClick={() => setPhone(user.phone)}
                          className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200"
                        >
                          <div className="font-medium">{user.name}</div>
                          <div className="text-xs text-gray-500">{user.phone}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <p className="text-xs text-center text-gray-400 mt-3">
                  ✅ All accounts verified in database • OTP shown above
                </p>
              </div>
            </>
          ) : step === 'otp' ? (
            <>
              <div className="flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mx-auto mb-4">
                <Lock className="w-8 h-8 text-primary-600" />
              </div>
              
              <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">
                {t('verifyOTP')}
              </h2>
              <p className="text-center text-gray-600 mb-6">
                {t('enterOTP')} {phone}
              </p>

              {otpData?.otp && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-800">
                    <strong>Development Mode:</strong> Your OTP is <strong>{otpData.otp}</strong>
                  </p>
                </div>
              )}

              <form onSubmit={handleVerifyOTP}>
                <div className="mb-4">
                  <label htmlFor="otp" className="block text-sm font-medium text-gray-700 mb-2">
                    One-Time Password
                  </label>
                  <input
                    type="text"
                    id="otp"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="Enter 6-digit OTP"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-center text-2xl tracking-widest"
                    required
                    maxLength="6"
                    pattern="[0-9]{6}"
                  />
                  <p className="mt-1 text-xs text-gray-500 text-center">
                    Valid for {otpData?.expires_in_minutes || 5} minutes
                  </p>
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}

                {/* Remember Me Checkbox */}
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Keep me signed in for 7 days
                    </span>
                  </label>
                  <p className="mt-1 ml-6 text-xs text-gray-500">
                    Recommended only on your personal device
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mb-3"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin mr-2 h-5 w-5" />
                      Verifying...
                    </>
                  ) : (
                    'Verify & Login'
                  )}
                </button>

                <button
                  type="button"
                  onClick={handleBack}
                  className="w-full text-gray-600 py-2 px-4 rounded-lg font-medium hover:bg-gray-50"
                >
                  Back to Phone Entry
                </button>
              </form>

              <div className="mt-4 text-center">
                <button
                  onClick={handleRequestOTP}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Didn't receive OTP? Resend
                </button>
              </div>
            </>
          ) : step === 'code' ? (
            <>
              <div className="flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mx-auto mb-4">
                <Key className="w-8 h-8 text-yellow-600" />
              </div>
              
              <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">
                Temporary Access Code
              </h2>
              <p className="text-center text-gray-600 mb-6">
                Enter the 6-digit code provided by your administrator
              </p>

              <form onSubmit={handleLoginWithCode}>
                <div className="mb-4">
                  <label htmlFor="accessCode" className="block text-sm font-medium text-gray-700 mb-2">
                    Access Code
                  </label>
                  <input
                    type="text"
                    id="accessCode"
                    value={accessCode}
                    onChange={(e) => setAccessCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="Enter 6-digit code"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent text-center text-2xl tracking-widest font-mono"
                    required
                    maxLength="6"
                    pattern="[0-9]{6}"
                    autoFocus
                  />
                  <p className="mt-1 text-xs text-gray-500 text-center">
                    Enter only numeric digits (0-9)
                  </p>
                </div>

                {/* Info Box */}
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start">
                    <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-blue-900">
                        What is a temporary access code?
                      </h4>
                      <p className="mt-1 text-xs text-blue-700">
                        If you cannot access your phone or receive OTPs, contact your administrator to generate a temporary 6-digit access code. This code is valid for 24 hours and can only be used once.
                      </p>
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start">
                      <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                      <div className="ml-3">
                        <p className="text-sm text-red-600 font-medium">Error</p>
                        <p className="text-xs text-red-600 mt-1">{error}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Remember Me Checkbox */}
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Keep me signed in for 7 days
                    </span>
                  </label>
                  <p className="mt-1 ml-6 text-xs text-gray-500">
                    Recommended only on your personal device
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading || accessCode.length !== 6}
                  className="w-full bg-yellow-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mb-3"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin mr-2 h-5 w-5" />
                      Verifying Code...
                    </>
                  ) : (
                    <>
                      <Key className="mr-2 h-5 w-5" />
                      Login with Code
                    </>
                  )}
                </button>

                <button
                  type="button"
                  onClick={handleBack}
                  className="w-full text-gray-600 py-2 px-4 rounded-lg font-medium hover:bg-gray-50"
                >
                  Back to Phone Login
                </button>
              </form>
            </>
          ) : null}
        </div>

        {/* Footer - Developer Credits */}
        <div className="mt-8 text-center">
          <div className="bg-white/80 backdrop-blur rounded-lg p-4 shadow-sm">
            <p className="text-sm font-semibold text-gray-700 mb-1">
              Developed by <span className="text-primary-600">srbhandary</span>
            </p>
            <p className="text-xs text-gray-600 mb-2">
              <span className="font-medium">Bytevantage Enterprise Solutions</span> • Mangalore
            </p>
            <div className="flex items-center justify-center gap-3 text-xs text-gray-500">
              <a 
                href="https://www.bytevantage.in" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-primary-600 hover:text-primary-700 hover:underline"
              >
                www.bytevantage.in
              </a>
              <span>•</span>
              <a 
                href="mailto:srbhandary@bytevantage.in" 
                className="text-primary-600 hover:text-primary-700 hover:underline"
              >
                srbhandary@bytevantage.in
              </a>
            </div>
            <p className="text-xs text-gray-400 mt-2">© 2025 All Rights Reserved</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
