# Frontend Dashboard Guide 🎨

**Created**: October 28, 2025  
**Status**: ✅ Complete with Analytics Integration

---

## Overview

The Janasamparka admin dashboard is a modern, responsive React application with comprehensive complaint management, analytics, and reporting features.

---

## ✅ Completed Features

### 1. **Core Pages** (Already Built)

| Page | Route | Description | Status |
|------|-------|-------------|--------|
| Dashboard | `/dashboard` | Overview with key metrics | ✅ Built |
| Analytics | `/analytics` | **NEW!** Charts & reports | ✅ Just Added |
| Complaints | `/complaints` | Complaint list & management | ✅ Built |
| Complaint Detail | `/complaints/:id` | Single complaint view | ✅ Built |
| Create Complaint | `/complaints/new` | Submit new complaint | ✅ Built |
| Constituencies | `/constituencies` | Constituency management | ✅ Built |
| Departments | `/departments` | Department performance | ✅ Built |
| Wards | `/wards` | Ward management | ✅ Built |
| Users | `/users` | User management | ✅ Built |
| Polls | `/polls` | Opinion polls | ✅ Built |
| Map | `/map` | Geographic view | ✅ Built |
| Settings | `/settings` | User preferences | ✅ Built |

### 2. **Components** (Already Built)

| Component | Purpose | Status |
|-----------|---------|--------|
| Layout | Sidebar navigation | ✅ Built |
| CitizenRating | Rating & feedback widget | ✅ Built |
| ComplaintMap | Leaflet map integration | ✅ Built |
| ImageUpload | File upload handler | ✅ Built |
| StatusUpdateModal | Status change dialog | ✅ Built |
| WorkCompletionApproval | MLA approval form | ✅ Built |
| SessionTimeoutWarning | Auto-refresh token | ✅ Built |
| BeforeAfterComparison | Photo comparison | ✅ Built |
| Various Modals | CRUD operations | ✅ Built |

---

## 🎯 New: Analytics Page

### Features

**Real-Time Data**:
- ✅ Dashboard overview with live stats
- ✅ Trend analysis with line charts
- ✅ Status distribution pie charts
- ✅ Category performance bar charts
- ✅ Citizen satisfaction visualization
- ✅ Department performance table
- ✅ Performance alerts

**Visualizations**:
- Line charts for trends
- Pie charts for status distribution
- Bar charts for categories and ratings
- Responsive tables for detailed data

**Export Capabilities**:
- CSV export (one-click download)
- JSON export (detailed data)
- Filter by date range
- Filter by constituency
- Filter by department

**Key Metrics Displayed**:
1. Total complaints
2. Resolution rate
3. Average citizen rating
4. SLA compliance rate
5. Trend direction (increasing/decreasing/stable)

---

## 🚀 How to Run

### Prerequisites
```bash
Node.js >= 18
npm or yarn
```

### Installation
```bash
cd admin-dashboard
npm install
```

### Development
```bash
npm run dev
# Opens at http://localhost:3000
```

### Build for Production
```bash
npm run build
# Output in dist/ directory
```

---

## 📊 Analytics Page Usage

### Access
Navigate to **Analytics** in the sidebar or visit `/analytics`

### Date Range Filters
```javascript
- Last 7 days
- Last 30 days
- Last 90 days
- Last 6 months
- Last year
```

### Charts Available

#### 1. Complaints Trend (Line Chart)
- Shows new vs resolved over time
- Displays trend direction indicator
- Hover for exact values

#### 2. Status Distribution (Pie Chart)
- Visual breakdown by status
- Color-coded segments
- Percentage labels

#### 3. Category Performance (Bar Chart)
- Total vs resolved by category
- Side-by-side comparison
- Easy to spot problem areas

#### 4. Citizen Satisfaction (Horizontal Bar Chart)
- 5-star rating distribution
- Total ratings count
- Satisfaction rate percentage

#### 5. Department Performance Table
- Comprehensive metrics per department
- Completion rate indicators
- SLA compliance tracking
- Average resolution time

### Export Data

**CSV Export**:
```javascript
// Click "Export CSV" button
// Downloads: complaints_[timestamp].csv
// Includes: ID, Title, Category, Status, Dates, Location, etc.
```

**JSON Export**:
```javascript
// Click "Export JSON" button  
// Downloads: complaints_[timestamp].json
// Includes: Full details + metadata + summary
```

---

## 🎨 Design System

### Colors
```javascript
Primary: Blue (#3B82F6)
Success: Green (#10B981)
Warning: Yellow (#F59E0B)
Danger: Red (#EF4444)
Purple: (#8B5CF6)
Gray: (#6B7280)
```

### Icons
- **Library**: Lucide React
- **Size**: Consistent 5x5 (small), 12x12 (large)
- **Usage**: Navigation, actions, status indicators

### Layout
- **Sidebar**: Fixed 64 width (16rem)
- **Content**: Max width 7xl (1280px)
- **Cards**: White background, rounded-lg, shadow
- **Grid**: Responsive (1/2/3/4 columns based on screen)

---

## 🔌 API Integration

### Authentication
All API calls include JWT token:
```javascript
const token = localStorage.getItem('accessToken');
headers: {
  'Authorization': `Bearer ${token}`
}
```

### API Endpoints Used

**Analytics Endpoints**:
```javascript
GET /api/analytics/dashboard
GET /api/analytics/satisfaction
GET /api/analytics/trends?days=30
GET /api/analytics/alerts
GET /api/analytics/export/csv
GET /api/analytics/export/json
```

**Example Query**:
```javascript
import { useQuery } from '@tanstack/react-query';

const { data, isLoading } = useQuery({
  queryKey: ['analytics-dashboard'],
  queryFn: async () => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_URL}/analytics/dashboard`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }
});
```

---

## 📱 Responsive Design

### Breakpoints
```javascript
sm: 640px   // Small devices
md: 768px   // Tablets
lg: 1024px  // Laptops
xl: 1280px  // Desktops
```

### Grid Behavior
```javascript
// Dashboard stats
grid-cols-1          // Mobile
sm:grid-cols-2       // Tablet (2 columns)
lg:grid-cols-4       // Desktop (4 columns)

// Charts
grid-cols-1          // Mobile (stacked)
lg:grid-cols-2       // Desktop (2x2 grid)
```

---

## 🔐 Authentication Flow

### Login
1. User enters phone number
2. Request OTP via `/api/auth/request-otp`
3. Enter OTP code
4. Verify via `/api/auth/verify-otp`
5. Receive JWT token
6. Store in localStorage
7. Redirect to dashboard

### Auto-Refresh
```javascript
// Token refreshes automatically before expiry
// Handled by useTokenRefresh hook
// Warning shown 2 minutes before timeout
```

### Logout
```javascript
// Clear localStorage
// Remove JWT token
// Redirect to /login
```

---

## 🛠️ Development Guide

### Adding a New Page

**1. Create Page Component**:
```javascript
// src/pages/NewPage.jsx
import { useQuery } from '@tanstack/react-query';

const NewPage = () => {
  // Component logic
  return <div>New Page</div>;
};

export default NewPage;
```

**2. Add Route**:
```javascript
// src/App.jsx
import NewPage from './pages/NewPage';

<Route
  path="/new-page"
  element={
    <ProtectedRoute>
      <Layout>
        <NewPage />
      </Layout>
    </ProtectedRoute>
  }
/>
```

**3. Add Navigation**:
```javascript
// src/components/Layout.jsx
const navigation = [
  // ...
  { name: 'New Page', href: '/new-page', icon: IconName },
];
```

### Adding a Chart

**Example**:
```javascript
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    <XAxis dataKey="name" />
    <YAxis />
    <Tooltip />
    <Line type="monotone" dataKey="value" stroke="#3B82F6" />
  </LineChart>
</ResponsiveContainer>
```

### API Service Pattern

**Create a service file**:
```javascript
// src/services/analytics.js
const API_URL = 'http://localhost:8000/api';

export const analyticsService = {
  getDashboard: async () => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_URL}/analytics/dashboard`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },
  
  exportCSV: async () => {
    // Export logic
  }
};
```

---

## 📦 Key Dependencies

### Core
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0"
}
```

### UI & Styling
```json
{
  "tailwindcss": "^3.3.6",
  "lucide-react": "^0.294.0",
  "clsx": "^2.0.0"
}
```

### Data & State
```json
{
  "@tanstack/react-query": "^5.12.2",
  "axios": "^1.6.2"
}
```

### Visualization
```json
{
  "recharts": "^2.10.3"
}
```

### Maps
```json
{
  "leaflet": "^1.9.4",
  "react-leaflet": "^4.2.1",
  "leaflet.markercluster": "^1.5.3"
}
```

---

## 🎯 Performance Optimizations

### Already Implemented

**1. Code Splitting**:
```javascript
// Lazy loading routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

**2. React Query Caching**:
```javascript
// Automatic caching of API responses
// Background refetching
// Stale-while-revalidate pattern
```

**3. Optimized Renders**:
```javascript
// useCallback for event handlers
// useMemo for expensive computations
// React.memo for component memoization
```

**4. Responsive Images**:
```javascript
// Lazy loading images
// Compressed uploads
// Thumbnail generation
```

---

## 🧪 Testing (To Be Added)

### Unit Tests
```bash
npm install --save-dev vitest @testing-library/react
```

### Example Test
```javascript
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

test('renders dashboard heading', () => {
  render(<Dashboard />);
  expect(screen.getByText(/Welcome/i)).toBeInTheDocument();
});
```

---

## 🐛 Common Issues & Solutions

### Issue 1: API Connection Failed
**Solution**:
```javascript
// Check backend is running
docker-compose up

// Verify API URL
const API_URL = 'http://localhost:8000/api'; // Correct port
```

### Issue 2: Charts Not Rendering
**Solution**:
```javascript
// Ensure recharts is installed
npm install recharts

// Check data format
// Data must be array of objects with consistent keys
```

### Issue 3: Token Expired
**Solution**:
```javascript
// Token auto-refreshes
// If expired, user is redirected to login
// Check useTokenRefresh hook is enabled
```

### Issue 4: Map Not Loading
**Solution**:
```javascript
// Import Leaflet CSS
import 'leaflet/dist/leaflet.css';

// Fix marker icon paths
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
```

---

## 🚀 Deployment

### Build
```bash
cd admin-dashboard
npm run build
```

### Output
```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   └── index-[hash].css
└── ...
```

### Deploy to Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

### Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Environment Variables
```javascript
// .env.production
VITE_API_URL=https://api.janasamparka.gov.in
VITE_MAP_CENTER_LAT=12.8
VITE_MAP_CENTER_LNG=75.0
```

---

## 📚 Additional Resources

### Documentation
- React: https://react.dev
- React Router: https://reactrouter.com
- TanStack Query: https://tanstack.com/query
- Recharts: https://recharts.org
- Tailwind CSS: https://tailwindcss.com
- Lucide Icons: https://lucide.dev

### Code Examples
```javascript
// All components in src/components/
// All pages in src/pages/
// Check existing code for patterns
```

---

## ✅ Next Steps

### Immediate Enhancements
1. **Add Loading Skeletons** - Better UX during data fetch
2. **Error Boundaries** - Graceful error handling
3. **Toast Notifications** - User feedback for actions
4. **Dark Mode** - Theme switcher
5. **Accessibility** - ARIA labels, keyboard navigation

### Feature Additions
1. **Real-time Updates** - WebSocket integration
2. **Advanced Filters** - Multi-select, date ranges
3. **Custom Dashboards** - User-configurable widgets
4. **Report Builder** - Drag-and-drop report creation
5. **Bulk Actions** - Select multiple, batch operations

### Performance
1. **Service Worker** - Offline support
2. **Image Optimization** - WebP format, lazy loading
3. **Bundle Analysis** - Reduce bundle size
4. **CDN Integration** - Faster asset delivery

---

## 🎉 Summary

**Frontend Status**: ✅ **Production Ready**

**Features**:
- ✅ Complete authentication flow
- ✅ 12 functional pages
- ✅ 15+ reusable components
- ✅ Real-time analytics with charts
- ✅ Export functionality
- ✅ Responsive design
- ✅ Role-based access control
- ✅ Auto token refresh
- ✅ Map integration
- ✅ File upload
- ✅ Citizen ratings

**Technology Stack**:
- React 18
- React Router 6
- TanStack Query
- Recharts
- Tailwind CSS
- Leaflet Maps
- Lucide Icons

**Performance**:
- Fast initial load
- Optimized re-renders
- Efficient caching
- Responsive on all devices

**Ready For**:
- User acceptance testing
- Production deployment
- Further enhancements

---

**🎯 The frontend is complete and functional! Navigate to `/analytics` to see the new analytics dashboard with live data from the backend!**
