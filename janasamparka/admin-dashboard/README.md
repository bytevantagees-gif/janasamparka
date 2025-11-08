# 🎨 ಜನಮನಾ ಸಂಪರ್ಕ | JanaMana Samparka Admin Dashboard

React-based admin dashboard for managing constituencies, MLAs, and citizen grievances.

**"Connecting People's Minds – Every voice heard, every corner connected."**

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (or use nvm)
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Navigate to admin dashboard
cd admin-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

---

## 📦 Tech Stack

- **Framework:** React 18
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Routing:** React Router v6
- **Data Fetching:** TanStack Query (React Query)
- **HTTP Client:** Axios
- **Icons:** Lucide React

---

## 📂 Project Structure

```
admin-dashboard/
├── src/
│   ├── components/          # Reusable UI components
│   │   └── Layout.jsx      # Main layout with sidebar
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx   # Main dashboard
│   │   ├── Constituencies.jsx
│   │   ├── ConstituencyDetail.jsx
│   │   └── Complaints.jsx
│   ├── services/           # API services
│   │   └── api.js          # Axios instance & API functions
│   ├── hooks/              # Custom React hooks (future)
│   ├── utils/              # Utility functions (future)
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── index.html             # HTML template
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── package.json           # Dependencies
```

---

## 🎯 Features

### Current Features ✅
- **Dashboard Overview**
  - Total constituencies count
  - System-wide complaint statistics
  - Resolution rate tracking
  - Constituency performance ranking

- **Constituency Management**
  - View all constituencies
  - Filter active/inactive
  - View detailed constituency info
  - MLA information display
  - Statistics per constituency

- **Responsive Layout**
  - Sidebar navigation
  - Modern UI with Tailwind CSS
  - Loading states
  - Error handling

### Coming Soon 🚧
- Complaint management interface
- User management
- Real-time notifications
- Advanced analytics & charts
- Report generation
- Settings panel
- Authentication UI

---

## 🔌 API Integration

The dashboard connects to the FastAPI backend via proxy:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### Available API Endpoints

**Constituencies:**
- `GET /api/constituencies/` - List all constituencies
- `GET /api/constituencies/{id}` - Get constituency details
- `GET /api/constituencies/{id}/stats` - Get statistics
- `POST /api/constituencies/` - Create constituency (admin)
- `PATCH /api/constituencies/{id}` - Update constituency (admin)
- `DELETE /api/constituencies/{id}` - Deactivate constituency (admin)
- `GET /api/constituencies/compare/all` - Compare all (admin)

**Complaints:**
- `GET /api/complaints/` - List complaints
- `GET /api/complaints/stats/summary` - Get statistics
- `POST /api/complaints/{id}/assign` - Assign complaint
- `PATCH /api/complaints/{id}/status` - Update status

---

## 🎨 UI Components

### Layout
Main layout with:
- Fixed sidebar navigation
- Kannada branding (ಜನಸಂಪರ್ಕ)
- User profile section
- Responsive design

### Pages

**Dashboard**
- System-wide statistics
- Constituency performance leaderboard
- Recent activity feed (coming soon)

**Constituencies**
- Grid view of all constituencies
- MLA information cards
- Status badges (Active/Inactive)
- Quick stats

**Constituency Detail**
- Comprehensive constituency info
- MLA contact details
- Performance metrics
- Ward and department stats

---

## 🔐 Authentication (Coming Soon)

```javascript
// Login flow
1. Request OTP via phone number
2. Verify OTP
3. Store JWT token
4. Include token in API requests

// Auto-logout on token expiry
// Refresh token handling
```

---

## 📊 Data Flow

```
User Action → Component
           ↓
    React Query Hook
           ↓
    API Service (axios)
           ↓
    FastAPI Backend
           ↓
    PostgreSQL Database
           ↓
    Response → Cache → UI Update
```

---

## 🛠️ Development

### Available Scripts

```bash
# Development server (hot reload)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation link in `src/components/Layout.jsx`

Example:
```jsx
// src/pages/NewPage.jsx
function NewPage() {
  return <div>New Page</div>;
}
export default NewPage;

// src/App.jsx
<Route path="/new-page" element={<NewPage />} />

// src/components/Layout.jsx
const navigation = [
  // ...
  { name: 'New Page', href: '/new-page', icon: IconComponent },
];
```

---

## 🎨 Styling Guidelines

### Tailwind CSS Classes

**Colors:**
- Primary: `text-primary-600`, `bg-primary-600`
- Secondary: `text-gray-600`, `bg-gray-100`
- Success: `text-green-600`, `bg-green-100`
- Error: `text-red-600`, `bg-red-100`

**Spacing:**
- Consistent padding: `p-4`, `p-6`
- Gap between elements: `space-y-4`, `space-x-4`

**Cards:**
```jsx
<div className="bg-white shadow rounded-lg p-6">
  {/* Content */}
</div>
```

**Buttons:**
```jsx
<button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
  Action
</button>
```

---

## 🐛 Troubleshooting

### Common Issues

**1. API Connection Failed**
```bash
# Ensure backend is running
cd ../backend
uvicorn app.main:app --reload

# Check CORS settings in backend
```

**2. Dependencies Not Installing**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**3. Tailwind Styles Not Applied**
```bash
# Ensure PostCSS is configured
# Check tailwind.config.js content paths
# Restart dev server
```

**4. Hot Reload Not Working**
```bash
# Restart Vite server
npm run dev
```

---

## 📈 Performance

- **Code Splitting:** Automatic route-based splitting
- **Lazy Loading:** Use React.lazy() for heavy components
- **Caching:** React Query handles API response caching
- **Optimistic Updates:** Immediate UI updates before API response

---

## 🔒 Security

- JWT tokens stored in localStorage
- Token included in Authorization header
- CORS configured on backend
- Input validation on forms
- XSS protection via React

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

Output in `dist/` folder.

### Deploy Options

**1. Static Hosting (Netlify, Vercel)**
```bash
# Build command
npm run build

# Publish directory
dist
```

**2. Docker**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
CMD ["npm", "run", "preview"]
```

**3. Nginx**
```nginx
server {
  listen 80;
  root /var/www/admin-dashboard/dist;
  index index.html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://backend:8000;
  }
}
```

---

## 🎯 Roadmap

### Phase 1 (Current)
- [x] Dashboard with statistics
- [x] Constituency list and details
- [x] Basic navigation and layout

### Phase 2 (Next)
- [ ] Complaint management interface
- [ ] User management
- [ ] Authentication UI
- [ ] Advanced filters and search

### Phase 3 (Future)
- [ ] Real-time updates (WebSockets)
- [ ] Charts and analytics
- [ ] Report generation
- [ ] Notification system
- [ ] Settings and configuration

---

## 💡 Tips

1. **Use React Query DevTools** for debugging API calls
2. **Keep components small** - split into smaller components if > 200 lines
3. **Use TypeScript** for better type safety (future migration)
4. **Test responsive design** on mobile devices
5. **Monitor bundle size** - keep under 500KB gzipped

---

## 📚 Resources

- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TanStack Query](https://tanstack.com/query/latest)
- [React Router](https://reactrouter.com/)
- [Lucide Icons](https://lucide.dev/)

---

## 🤝 Contributing

1. Follow existing code style
2. Use meaningful component and variable names
3. Add comments for complex logic
4. Test on different screen sizes
5. Update README for new features

---

**Version:** 1.0.0-alpha  
**Last Updated:** November 2025  
**Built with ❤️ for Karnataka's MLAs and Citizens**  
**ಜನಮನಾ ಸಂಪರ್ಕ | JanaMana Samparka – Connecting People's Minds**
