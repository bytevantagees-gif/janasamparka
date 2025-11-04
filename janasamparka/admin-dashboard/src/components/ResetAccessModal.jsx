import { useState, useEffect } from 'react';
import { X, Key, Clock, Mail, Copy, CheckCircle, AlertCircle, User, Phone } from 'lucide-react';
import { authAPI } from '../services/api';

function ResetAccessModal({ isOpen, onClose, user }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [accessData, setAccessData] = useState(null);
  const [copied, setCopied] = useState(false);

  // Generate code when modal opens
  useEffect(() => {
    if (isOpen && user) {
      generateAccessCode();
    }
  }, [isOpen, user]);

  const generateAccessCode = async () => {
    setIsLoading(true);
    setError(null);
    setAccessData(null);
    setCopied(false);

    try {
      const response = await authAPI.resetUserAccess(user.id);
      setAccessData(response);

      // Auto-copy to clipboard
      if (response.access_code) {
        await navigator.clipboard.writeText(response.access_code);
        setCopied(true);
        setTimeout(() => setCopied(false), 3000);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate access code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyCode = async () => {
    if (accessData?.access_code) {
      try {
        await navigator.clipboard.writeText(accessData.access_code);
        setCopied(true);
        setTimeout(() => setCopied(false), 3000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    }
  };

  const formatExpiryTime = (expiresAt) => {
    const expiry = new Date(expiresAt);
    const now = new Date();
    const hoursLeft = Math.round((expiry - now) / (1000 * 60 * 60));
    
    return {
      fullDate: expiry.toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }),
      hoursLeft,
    };
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
                <Key className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-medium text-gray-900">
                  Reset User Access
                </h3>
                <p className="text-sm text-gray-500">
                  Generate temporary login code
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* User Info */}
          {user && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <User className="h-4 w-4 text-gray-400 mr-2" />
                  <span className="font-medium text-gray-700">Name:</span>
                  <span className="ml-2 text-gray-900">{user.name}</span>
                </div>
                <div className="flex items-center text-sm">
                  <Phone className="h-4 w-4 text-gray-400 mr-2" />
                  <span className="font-medium text-gray-700">Phone:</span>
                  <span className="ml-2 text-gray-900">{user.phone}</span>
                </div>
                {user.email && (
                  <div className="flex items-center text-sm">
                    <Mail className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="font-medium text-gray-700">Email:</span>
                    <span className="ml-2 text-gray-900">{user.email}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-sm text-gray-600">Generating access code...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                </div>
              </div>
              <button
                onClick={generateAccessCode}
                className="mt-3 text-sm font-medium text-red-600 hover:text-red-500"
              >
                Try again
              </button>
            </div>
          )}

          {/* Success State - Access Code */}
          {accessData && !isLoading && (
            <div className="space-y-4">
              {/* Access Code Display */}
              <div className="p-6 bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg border-2 border-primary-300">
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Temporary Access Code
                  </p>
                  <div className="text-5xl font-bold text-primary-900 tracking-widest mb-4 font-mono">
                    {accessData.access_code}
                  </div>
                  <button
                    onClick={handleCopyCode}
                    className="inline-flex items-center px-4 py-2 border border-primary-300 rounded-md shadow-sm text-sm font-medium text-primary-700 bg-white hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                  >
                    {copied ? (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4 text-green-600" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="mr-2 h-4 w-4" />
                        Copy Code
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Expiry Info */}
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start">
                  <Clock className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-yellow-900">
                      Code Expires In {formatExpiryTime(accessData.expires_at).hoursLeft} Hours
                    </h4>
                    <p className="mt-1 text-sm text-yellow-700">
                      Valid until: {formatExpiryTime(accessData.expires_at).fullDate}
                    </p>
                    <p className="mt-2 text-xs text-yellow-600">
                      This code can only be used once. After successful login, it will be invalidated.
                    </p>
                  </div>
                </div>
              </div>

              {/* Email Status */}
              {accessData.email_sent ? (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-green-900">
                        Email Sent Successfully
                      </h4>
                      <p className="mt-1 text-sm text-green-700">
                        The access code has been sent to <strong>{accessData.user.email}</strong>
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                  <div className="flex items-start">
                    <Mail className="h-5 w-5 text-gray-400 mt-0.5" />
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-gray-900">
                        No Email Configured
                      </h4>
                      <p className="mt-1 text-sm text-gray-600">
                        {accessData.message || 'Please share this code manually with the user.'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Instructions */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">
                  How to use this code:
                </h4>
                <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                  <li>Share this 6-digit code with the user</li>
                  <li>User clicks "Phone broken? Use temporary code" on login page</li>
                  <li>User enters the code to gain access</li>
                  <li>Code becomes invalid after use or 24 hours</li>
                </ol>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="mt-6 flex justify-end space-x-3">
            {accessData && (
              <button
                onClick={generateAccessCode}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Generate New Code
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {accessData ? 'Done' : 'Cancel'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResetAccessModal;
