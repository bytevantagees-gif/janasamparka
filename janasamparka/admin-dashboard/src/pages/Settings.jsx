import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api, { constituenciesAPI, usersAPI } from '../services/api';
import {
  User,
  Lock,
  Bell,
  Globe,
  Shield,
  Save,
  Mail,
  Phone,
  MapPin,
  Database,
  Download,
  Upload,
  Trash2,
  RefreshCw,
  HardDrive,
  CheckCircle,
  AlertCircle,
  Loader2,
  Camera
} from 'lucide-react';

function Settings() {
  const { t } = useTranslation();
  const { user, updateUser } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === 'admin';
  
  const [settings, setSettings] = useState({
    // Profile
    name: user?.name || '',
    phone: user?.phone || '',
    email: '',
    locale: user?.locale_pref || 'en',
    
    // Notifications
    emailNotifications: true,
    smsNotifications: true,
    pushNotifications: false,
    complaintNotifications: true,
    statusUpdates: true,
    weeklyReports: false,
    
    // Privacy
    profileVisibility: 'public',
    showContactInfo: true,
    showStatistics: true,
  });

  // Database management state
  const [selectedTables, setSelectedTables] = useState([]);
  const [showRestoreConfirm, setShowRestoreConfirm] = useState(null);
  const [profilePhotoPreview, setProfilePhotoPreview] = useState(user?.profile_photo || null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [selectedConstituency, setSelectedConstituency] = useState(user?.constituency_id || null);

  // Fetch constituencies for citizen selection
  const { data: constituenciesData } = useQuery({
    queryKey: ['constituencies', 'active'],
    queryFn: async () => {
      const response = await constituenciesAPI.getAll(true);
      return response.data;
    },
    enabled: user?.role === 'citizen',
  });

  const constituencies = constituenciesData?.constituencies || [];

  // Profile photo upload mutation
  const uploadPhotoMutation = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/api/auth/me/profile-photo', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: (data) => {
      setProfilePhotoPreview(data.profile_photo);
      queryClient.invalidateQueries(['current-user']);
      // Update user in AuthContext and localStorage
      updateUser(data);
      alert('Profile photo uploaded successfully!');
    },
    onError: (error) => {
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handlePhotoChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size too large. Maximum 5MB allowed.');
      return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file.');
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setProfilePhotoPreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Upload
    setUploadingPhoto(true);
    await uploadPhotoMutation.mutateAsync(file);
    setUploadingPhoto(false);
  };

  // Fetch database info
  const { data: dbInfo, isLoading: dbInfoLoading, refetch: refetchDbInfo } = useQuery({
    queryKey: ['database-info'],
    queryFn: async () => {
      const response = await api.get('/api/database/info');
      return response.data;
    },
    enabled: isAdmin,
  });

  // Full backup mutation
  const fullBackupMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/api/database/backup/full');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['database-info']);
      alert('Full database backup created successfully!');
    },
    onError: (error) => {
      alert(`Backup failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Selective backup mutation
  const selectiveBackupMutation = useMutation({
    mutationFn: async (tables) => {
      const response = await api.post('/api/database/backup/selective', tables);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['database-info']);
      setSelectedTables([]);
      alert('Selective backup created successfully!');
    },
    onError: (error) => {
      alert(`Backup failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Restore mutation
  const restoreMutation = useMutation({
    mutationFn: async (filename) => {
      const response = await api.post(`/api/database/restore/${filename}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['database-info']);
      setShowRestoreConfirm(null);
      alert('Database restored successfully!');
    },
    onError: (error) => {
      alert(`Restore failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Delete backup mutation
  const deleteBackupMutation = useMutation({
    mutationFn: async (filename) => {
      const response = await api.delete(`/api/database/backup/${filename}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['database-info']);
      alert('Backup deleted successfully!');
    },
    onError: (error) => {
      alert(`Delete failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Update constituency mutation
  const updateConstituencyMutation = useMutation({
    mutationFn: async (constituencyId) => {
      const response = await usersAPI.updateUser(user.id, {
        constituency_id: constituencyId,
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Find constituency name
      const constituency = constituencies.find(c => c.id === data.constituency_id);
      const updatedUser = {
        ...user,
        constituency_id: data.constituency_id,
        constituency_name: constituency?.name,
      };
      updateUser(updatedUser);
      queryClient.invalidateQueries(['current-user']);
      alert('Constituency updated successfully!');
    },
    onError: (error) => {
      alert(`Update failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (profileData) => {
      const response = await usersAPI.updateUser(user.id, profileData);
      return response.data;
    },
    onSuccess: (data) => {
      const updatedUser = {
        ...user,
        name: data.name,
        email: data.email,
        locale_pref: data.locale_pref,
      };
      updateUser(updatedUser);
      queryClient.invalidateQueries(['current-user']);
      alert('Profile updated successfully!');
    },
    onError: (error) => {
      alert(`Update failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleSave = (section) => {
    if (section === 'Constituency' && selectedConstituency) {
      updateConstituencyMutation.mutate(selectedConstituency);
      return;
    }
    
    if (section === 'Profile') {
      // Update profile with name and email
      updateProfileMutation.mutate({
        name: settings.name,
        email: settings.email,
      });
      return;
    }

    if (section === 'Preferences') {
      // Update locale preference
      updateProfileMutation.mutate({
        locale_pref: settings.locale,
      });
      return;
    }

    // For other sections, just show alert for now
    alert(`${section} settings saved!`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('settings')}</h1>
        <p className="mt-1 text-sm text-gray-500">
          {t('accountSettings')}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <nav className="space-y-1 bg-white shadow rounded-lg p-4">
            <a href="#profile" className="flex items-center px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 rounded-md">
              <User className="mr-3 h-5 w-5" />
              {t('profile')}
            </a>
            <a href="#notifications" className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md">
              <Bell className="mr-3 h-5 w-5" />
              {t('notifications')}
            </a>
            <a href="#privacy" className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md">
              <Shield className="mr-3 h-5 w-5" />
              {t('privacy')}
            </a>
            <a href="#preferences" className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md">
              <Globe className="mr-3 h-5 w-5" />
              {t('preferences')}
            </a>
            <a href="#security" className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md">
              <Lock className="mr-3 h-5 w-5" />
              {t('security')}
            </a>
            {isAdmin && (
              <a href="#database" className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md">
                <Database className="mr-3 h-5 w-5" />
                Database Management
              </a>
            )}
          </nav>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Profile Section */}
          <div id="profile" className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <User className="mr-2 h-5 w-5 text-gray-400" />
              {t('profileInformation')}
            </h2>
            <div className="space-y-4">
              {/* Profile Photo Upload */}
              <div className="flex items-center space-x-6 mb-6">
                <div className="relative">
                  <div className="h-24 w-24 rounded-full overflow-hidden bg-gray-200 ring-4 ring-gray-100">
                    {profilePhotoPreview ? (
                      <img
                        src={profilePhotoPreview.startsWith('/') ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${profilePhotoPreview}` : profilePhotoPreview}
                        alt="Profile"
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="h-full w-full flex items-center justify-center bg-primary-100">
                        <User className="h-12 w-12 text-primary-600" />
                      </div>
                    )}
                  </div>
                  <label
                    htmlFor="profile-photo"
                    className="absolute bottom-0 right-0 bg-primary-600 text-white p-2 rounded-full cursor-pointer hover:bg-primary-700 shadow-lg"
                  >
                    {uploadingPhoto ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Camera className="h-4 w-4" />
                    )}
                    <input
                      id="profile-photo"
                      type="file"
                      accept="image/*"
                      onChange={handlePhotoChange}
                      className="hidden"
                      disabled={uploadingPhoto}
                    />
                  </label>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-gray-900 mb-1">Profile Photo</h3>
                  <p className="text-xs text-gray-500 mb-2">
                    Upload a profile photo (JPG, PNG, or GIF. Max 5MB)
                  </p>
                  <label
                    htmlFor="profile-photo-btn"
                    className="inline-flex items-center px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 cursor-pointer"
                  >
                    <Upload className="h-4 w-4 mr-1" />
                    Upload Photo
                    <input
                      id="profile-photo-btn"
                      type="file"
                      accept="image/*"
                      onChange={handlePhotoChange}
                      className="hidden"
                      disabled={uploadingPhoto}
                    />
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('fullName')}
                </label>
                <input
                  type="text"
                  value={settings.name}
                  onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('phoneNumber')}
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="tel"
                    value={settings.phone}
                    onChange={(e) => setSettings({ ...settings, phone: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    disabled
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">{t('phoneCannotChange')}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('emailAddress')}
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    value={settings.email}
                    onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                    placeholder="your@email.com"
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('role')}
                </label>
                <input
                  type="text"
                  value={user?.role?.toUpperCase() || 'USER'}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  disabled
                />
              </div>

              {/* Constituency Selector for Citizens */}
              {user?.role === 'citizen' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <MapPin className="inline h-4 w-4 mr-1" />
                    Constituency
                  </label>
                  <select
                    value={selectedConstituency || ''}
                    onChange={(e) => setSelectedConstituency(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Select your constituency...</option>
                    {constituencies.map((constituency) => (
                      <option key={constituency.id} value={constituency.id}>
                        {constituency.name}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-gray-500">
                    Select the constituency where you reside to see relevant complaints
                  </p>
                  {selectedConstituency && selectedConstituency !== user?.constituency_id && (
                    <button
                      onClick={() => handleSave('Constituency')}
                      disabled={updateConstituencyMutation.isLoading}
                      className="mt-3 inline-flex items-center px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 disabled:opacity-50"
                    >
                      {updateConstituencyMutation.isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Updating...
                        </>
                      ) : (
                        <>
                          <Save className="mr-2 h-4 w-4" />
                          Update Constituency
                        </>
                      )}
                    </button>
                  )}
                </div>
              )}

              <div className="pt-4">
                <button
                  onClick={() => handleSave('Profile')}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  <Save className="mr-2 h-4 w-4" />
                  {t('saveChanges')}
                </button>
              </div>
            </div>
          </div>

          {/* Notifications Section */}
          <div id="notifications" className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Bell className="mr-2 h-5 w-5 text-gray-400" />
              Notification Preferences
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Email Notifications</p>
                  <p className="text-sm text-gray-500">Receive notifications via email</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.emailNotifications}
                    onChange={(e) => setSettings({ ...settings, emailNotifications: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">SMS Notifications</p>
                  <p className="text-sm text-gray-500">Receive notifications via SMS</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.smsNotifications}
                    onChange={(e) => setSettings({ ...settings, smsNotifications: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Push Notifications</p>
                  <p className="text-sm text-gray-500">Receive push notifications on your device</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.pushNotifications}
                    onChange={(e) => setSettings({ ...settings, pushNotifications: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <hr className="my-4" />

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">New Complaints</p>
                  <p className="text-sm text-gray-500">Get notified when new complaints are filed</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.complaintNotifications}
                    onChange={(e) => setSettings({ ...settings, complaintNotifications: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Status Updates</p>
                  <p className="text-sm text-gray-500">Get notified about complaint status changes</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.statusUpdates}
                    onChange={(e) => setSettings({ ...settings, statusUpdates: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Weekly Reports</p>
                  <p className="text-sm text-gray-500">Receive weekly summary reports</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.weeklyReports}
                    onChange={(e) => setSettings({ ...settings, weeklyReports: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="pt-4">
                <button
                  onClick={() => handleSave('Notifications')}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Save Preferences
                </button>
              </div>
            </div>
          </div>

          {/* Privacy Section */}
          <div id="privacy" className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Shield className="mr-2 h-5 w-5 text-gray-400" />
              Privacy Settings
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Profile Visibility
                </label>
                <select
                  value={settings.profileVisibility}
                  onChange={(e) => setSettings({ ...settings, profileVisibility: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                  <option value="constituents">Constituents Only</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Show Contact Information</p>
                  <p className="text-sm text-gray-500">Display phone and email on public profile</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.showContactInfo}
                    onChange={(e) => setSettings({ ...settings, showContactInfo: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Show Statistics</p>
                  <p className="text-sm text-gray-500">Display complaint resolution statistics publicly</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.showStatistics}
                    onChange={(e) => setSettings({ ...settings, showStatistics: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="pt-4">
                <button
                  onClick={() => handleSave('Privacy')}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Save Settings
                </button>
              </div>
            </div>
          </div>

          {/* Preferences Section */}
          <div id="preferences" className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Globe className="mr-2 h-5 w-5 text-gray-400" />
              Preferences
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language / Locale
                </label>
                <select
                  value={settings.locale}
                  onChange={(e) => setSettings({ ...settings, locale: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="en">English</option>
                  <option value="kn">ಕನ್ನಡ (Kannada)</option>
                  <option value="hi">हिंदी (Hindi)</option>
                </select>
              </div>

              <div className="pt-4">
                <button
                  onClick={() => handleSave('Preferences')}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Save Preferences
                </button>
              </div>
            </div>
          </div>

          {/* Security Section */}
          <div id="security" className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Lock className="mr-2 h-5 w-5 text-gray-400" />
              Security
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-700 mb-4">
                  Your account is secured with OTP-based authentication.
                </p>
                <button className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                  <Lock className="mr-2 h-4 w-4" />
                  Change Phone Number
                </button>
              </div>

              <hr />

              <div>
                <p className="font-medium text-gray-900 mb-2">Active Sessions</p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Current Device</p>
                      <p className="text-xs text-gray-500">Last active: Just now</p>
                    </div>
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      Active
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Database Management Section - Admin Only */}
          {isAdmin && (
            <div id="database" className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <Database className="mr-2 h-5 w-5 text-gray-400" />
                Database Management
              </h2>

              {dbInfoLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Database Info */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                      <HardDrive className="h-5 w-5 mr-2 text-gray-600" />
                      Database Information
                    </h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Database Name:</p>
                        <p className="font-medium">{dbInfo?.database_name}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Total Size:</p>
                        <p className="font-medium">{dbInfo?.database_size}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Total Tables:</p>
                        <p className="font-medium">{dbInfo?.total_tables}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Available Backups:</p>
                        <p className="font-medium">{dbInfo?.available_backups?.length || 0}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => refetchDbInfo()}
                      className="mt-3 inline-flex items-center text-sm text-primary-600 hover:text-primary-700"
                    >
                      <RefreshCw className="h-4 w-4 mr-1" />
                      Refresh Info
                    </button>
                  </div>

                  {/* Full Backup */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">Complete Backup</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Create a full backup of the entire database including all tables and data.
                    </p>
                    <button
                      onClick={() => fullBackupMutation.mutate()}
                      disabled={fullBackupMutation.isPending}
                      className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      {fullBackupMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating Backup...
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-4 w-4" />
                          Create Full Backup
                        </>
                      )}
                    </button>
                  </div>

                  {/* Selective Backup */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">Selective Backup</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Select specific tables to backup.
                    </p>
                    
                    <div className="mb-3 max-h-48 overflow-y-auto border border-gray-200 rounded p-2">
                      {dbInfo?.tables?.map((table) => (
                        <label key={table.table_name} className="flex items-center py-1 hover:bg-gray-50 px-2 rounded">
                          <input
                            type="checkbox"
                            checked={selectedTables.includes(table.table_name)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedTables([...selectedTables, table.table_name]);
                              } else {
                                setSelectedTables(selectedTables.filter(t => t !== table.table_name));
                              }
                            }}
                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                          />
                          <span className="ml-2 text-sm text-gray-700 flex-1">
                            {table.table_name}
                          </span>
                          <span className="text-xs text-gray-500">
                            {dbInfo?.table_counts?.[table.table_name]} rows, {table.size}
                          </span>
                        </label>
                      ))}
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setSelectedTables(dbInfo?.tables?.map(t => t.table_name) || [])}
                        className="text-sm text-primary-600 hover:text-primary-700"
                      >
                        Select All
                      </button>
                      <span className="text-gray-300">|</span>
                      <button
                        onClick={() => setSelectedTables([])}
                        className="text-sm text-primary-600 hover:text-primary-700"
                      >
                        Clear
                      </button>
                      <span className="ml-auto text-sm text-gray-600">
                        {selectedTables.length} selected
                      </span>
                    </div>

                    <button
                      onClick={() => selectiveBackupMutation.mutate(selectedTables)}
                      disabled={selectiveBackupMutation.isPending || selectedTables.length === 0}
                      className="mt-3 inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                    >
                      {selectiveBackupMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating Backup...
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-4 w-4" />
                          Create Selective Backup
                        </>
                      )}
                    </button>
                  </div>

                  {/* Available Backups */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-3">Available Backups</h3>
                    
                    {dbInfo?.available_backups?.length === 0 ? (
                      <p className="text-sm text-gray-500 italic">No backups available</p>
                    ) : (
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {dbInfo?.available_backups?.map((backup) => (
                          <div key={backup.filename} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-900">{backup.filename}</p>
                              <p className="text-xs text-gray-500">
                                {new Date(backup.created_at).toLocaleString()} • {backup.size_pretty}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <a
                                href={`/api/database/backup/download/${backup.filename}`}
                                download
                                className="inline-flex items-center px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                              >
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </a>
                              <button
                                onClick={() => setShowRestoreConfirm(backup.filename)}
                                className="inline-flex items-center px-3 py-1.5 text-sm bg-orange-600 text-white rounded hover:bg-orange-700"
                              >
                                <Upload className="h-4 w-4 mr-1" />
                                Restore
                              </button>
                              <button
                                onClick={() => {
                                  if (confirm(`Delete backup ${backup.filename}?`)) {
                                    deleteBackupMutation.mutate(backup.filename);
                                  }
                                }}
                                disabled={deleteBackupMutation.isPending}
                                className="inline-flex items-center px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Restore Confirmation Modal */}
                  {showRestoreConfirm && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex items-center mb-4">
                          <AlertCircle className="h-6 w-6 text-red-600 mr-2" />
                          <h3 className="text-lg font-medium text-gray-900">Confirm Restore</h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-4">
                          Are you sure you want to restore from <strong>{showRestoreConfirm}</strong>?
                        </p>
                        <p className="text-sm text-red-600 mb-4">
                          ⚠️ <strong>WARNING:</strong> This will overwrite all current data. This action cannot be undone!
                        </p>
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => setShowRestoreConfirm(null)}
                            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => restoreMutation.mutate(showRestoreConfirm)}
                            disabled={restoreMutation.isPending}
                            className="px-4 py-2 text-sm text-white bg-red-600 rounded hover:bg-red-700 disabled:opacity-50"
                          >
                            {restoreMutation.isPending ? (
                              <>
                                <Loader2 className="inline h-4 w-4 animate-spin mr-1" />
                                Restoring...
                              </>
                            ) : (
                              'Yes, Restore Database'
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Warning Notice */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex">
                      <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0" />
                      <div className="text-sm text-yellow-800">
                        <p className="font-medium mb-1">Important Notes:</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li>Backups are stored on the server and can be downloaded</li>
                          <li>Restoring a backup will overwrite all current data</li>
                          <li>Always create a backup before performing restore operations</li>
                          <li>Large databases may take several minutes to backup/restore</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
