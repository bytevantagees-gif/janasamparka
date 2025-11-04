import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import SmartDashboard from './pages/SmartDashboard';
import Constituencies from './pages/Constituencies';
import ConstituencyDetail from './pages/ConstituencyDetail';
import Complaints from './pages/Complaints';
import ComplaintDetail from './pages/ComplaintDetail';
import CreateComplaint from './pages/CreateComplaint';
import DepartmentOfficerComplaints from './pages/DepartmentOfficerComplaints';
import Wards from './pages/Wards';
import WardDetail from './pages/WardDetail';
import Users from './pages/Users';
import Departments from './pages/Departments';
import DepartmentsHierarchy from './pages/DepartmentsHierarchy';
import Panchayats from './pages/Panchayats';
import ZillaPanchayatDetail from './pages/ZillaPanchayatDetail';
import TalukPanchayatDetail from './pages/TalukPanchayatDetail';
import GramPanchayatDetail from './pages/GramPanchayatDetail';
import Polls from './pages/Polls';
import Map from './pages/Map';
import Settings from './pages/Settings';
import Analytics from './pages/Analytics';
import Budget from './pages/Budget';
import MLAPerformanceDashboard from './pages/mla/PerformanceDashboard';
import SatisfactionDashboard from './pages/moderator/SatisfactionDashboard';
import MyComplaints from './pages/citizen/MyComplaints';
import CitizenPolls from './pages/citizen/Polls';
import MyWard from './pages/citizen/MyWard';
import OfficerPerformance from './pages/officer/Performance';
import WardOfficerDashboard from './pages/wardOfficer/WardOfficerDashboard';
import Layout from './components/Layout';
// Citizen Services imports
import VotebankDashboard from './pages/votebank/VotebankDashboard';
import AgriculturalSupport from './pages/votebank/AgriculturalSupport';
import CitizenEngagement from './pages/votebank/CitizenEngagement';
import CitizenVideoConsultation from './pages/citizen/VideoConsultation';
import CitizenAgricultureSupport from './pages/citizen/AgricultureSupport';
// Forum imports
import Forum from './pages/Forum';
import ForumTopicDetail from './pages/ForumTopicDetail';
// Social Feed imports
import SocialFeed from './pages/SocialFeed';
// Chat import
import LiveChat from './pages/LiveChat';

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected routes */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <SmartDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-complaints"
          element={
            <ProtectedRoute allowedRoles={['department_officer', 'moderator']}>
              <Layout>
                <DepartmentOfficerComplaints />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ward-officer"
          element={
            <ProtectedRoute allowedRoles={['ward_officer']}>
              <Layout>
                <WardOfficerDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/constituencies"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <Constituencies />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/constituencies/:id"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <ConstituencyDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/complaints"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <Complaints />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/complaints/new"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator', 'citizen']}>
              <Layout>
                <CreateComplaint />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/complaints/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <ComplaintDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/wards"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <Wards />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/wards/:id"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <WardDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/users"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <Users />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/panchayats"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla']}>
              <Layout>
                <Panchayats />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/panchayats/zilla/:id"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla']}>
              <Layout>
                <ZillaPanchayatDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/panchayats/taluk/:id"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla']}>
              <Layout>
                <TalukPanchayatDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/panchayats/gram/:id"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla']}>
              <Layout>
                <GramPanchayatDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/departments"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <DepartmentsHierarchy />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/polls"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <Polls />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/map"
          element={
            <ProtectedRoute>
              <Layout>
                <Map />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <Analytics />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/mla/performance"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla']}>
              <Layout>
                <MLAPerformanceDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/moderator/satisfaction"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <SatisfactionDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/citizen/complaints"
          element={
            <ProtectedRoute allowedRoles={['citizen']}>
              <Layout>
                <MyComplaints />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/citizen/polls"
          element={
            <ProtectedRoute allowedRoles={['citizen']}>
              <Layout>
                <CitizenPolls />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/citizen/ward"
          element={
            <ProtectedRoute allowedRoles={['citizen']}>
              <Layout>
                <MyWard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/citizen/video-consultation"
          element={
            <ProtectedRoute allowedRoles={['citizen']}>
              <Layout>
                <CitizenVideoConsultation />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/citizen/agriculture-support"
          element={
            <ProtectedRoute allowedRoles={['citizen']}>
              <Layout>
                <CitizenAgricultureSupport />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/officer/performance"
          element={
            <ProtectedRoute allowedRoles={['department_officer']}>
              <Layout>
                <OfficerPerformance />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/budget"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator', 'auditor']}>
              <Layout>
                <Budget />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Forum Routes */}
        <Route
          path="/forum"
          element={
            <ProtectedRoute>
              <Layout>
                <Forum />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/forum/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <ForumTopicDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Social Feed Routes */}
        <Route
          path="/social"
          element={
            <ProtectedRoute>
              <Layout>
                <SocialFeed />
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Live Chat Route */}
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Layout>
                <LiveChat />
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Votebank Engagement Routes */}
        <Route
          path="/votebank"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <VotebankDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/votebank/farmers"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <AgriculturalSupport />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/votebank/businesses"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <CitizenEngagement />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/votebank/youth"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <CitizenEngagement />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/votebank/training"
          element={
            <ProtectedRoute allowedRoles={['admin', 'mla', 'moderator']}>
              <Layout>
                <CitizenEngagement />
              </Layout>
            </ProtectedRoute>
          }
        />
        </Routes>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
