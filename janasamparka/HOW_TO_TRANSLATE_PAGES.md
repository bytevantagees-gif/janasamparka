# How to Translate Pages to Kannada 📝

**Guide Created**: October 29, 2025  
**Purpose**: Enable full page content translation

---

## Current Status

✅ **Sidebar** - Fully translated  
✅ **Header/Top Bar** - Fully translated  
✅ **Translation System** - Ready to use  
⚠️ **Page Content** - Needs translation  

---

## How Translation Works

### 1. Import the Hook

```javascript
import { useTranslation } from '../hooks/useTranslation';
```

### 2. Use in Component

```javascript
function MyPage() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('welcomeBack')}</h1>
      <button>{t('submit')}</button>
    </div>
  );
}
```

### 3. That's It!

The `t()` function automatically:
- Detects current language (en/kn)
- Returns the right translation
- Falls back to English if key missing

---

## Step-by-Step: Translating a Page

### Example: Dashboard.jsx

#### Before (Hardcoded English)
```javascript
function Dashboard() {
  return (
    <div>
      <h1>Welcome back, {user?.name}</h1>
      <p>Total Complaints: {count}</p>
      <button>View All</button>
    </div>
  );
}
```

#### After (Translatable)
```javascript
import { useTranslation } from '../hooks/useTranslation';

function Dashboard() {
  const { t } = useTranslation();  // ← Add this
  
  return (
    <div>
      <h1>{t('welcomeBack')}, {user?.name}</h1>
      <p>{t('totalComplaints')}: {count}</p>
      <button>{t('viewAll')}</button>
    </div>
  );
}
```

---

## What Needs Translation?

### High Priority (User-Facing Text)

1. **Headings & Titles**
   ```javascript
   <h1>{t('dashboard')}</h1>
   <h2>{t('recentComplaints')}</h2>
   ```

2. **Button Labels**
   ```javascript
   <button>{t('submit')}</button>
   <button>{t('cancel')}</button>
   ```

3. **Form Labels**
   ```javascript
   <label>{t('title')}</label>
   <label>{t('description')}</label>
   ```

4. **Status Messages**
   ```javascript
   <span>{t('loading')}</span>
   <span>{t('success')}</span>
   ```

5. **Table Headers**
   ```javascript
   <th>{t('name')}</th>
   <th>{t('status')}</th>
   ```

### Low Priority (Technical)

- Console.log messages
- Error codes
- API endpoints
- Class names

---

## Available Translations

We already have 150+ translations ready! Check `/locales/translations.js`:

### Navigation
- dashboard, complaints, analytics, wards, etc.

### Status
- submitted, assigned, inProgress, resolved, closed, rejected

### Categories
- roadInfrastructure, waterSupply, electricity, sanitation, etc.

### Actions
- create, edit, delete, save, submit, cancel, search, export

### Common
- loading, error, success, total, average, status, etc.

---

## Adding New Translations

### Step 1: Add to translations.js

```javascript
// /locales/translations.js

export const translations = {
  en: {
    // ... existing ...
    myNewText: 'My New Text',
    anotherLabel: 'Another Label',
  },
  kn: {
    // ... existing ...
    myNewText: 'ನನ್ನ ಹೊಸ ಪಠ್ಯ',
    anotherLabel: 'ಇನ್ನೊಂದು ಲೇಬಲ್',
  }
};
```

### Step 2: Use in Component

```javascript
<h1>{t('myNewText')}</h1>
<label>{t('anotherLabel')}</label>
```

---

## Quick Translation Guide

### Dashboard Page

**File**: `/pages/Dashboard.jsx`

**Add at top**:
```javascript
import { useTranslation } from '../hooks/useTranslation';
```

**In component**:
```javascript
function Dashboard() {
  const { t } = useTranslation();  // Add this line
  
  // Then replace hardcoded strings:
  // "Welcome back" → {t('welcomeBack')}
  // "Total Complaints" → {t('totalComplaints')}
  // "View All" → {t('viewAll')}
}
```

### Analytics Page

**Already has the hook!** Just replace strings:

```javascript
// Before
<h1>Analytics & Reports</h1>

// After
<h1>{t('analyticsReports')}</h1>
```

### Complaints List

**File**: `/pages/ComplaintsList.jsx`

Replace:
- "Complaints" → `{t('complaints')}`
- "Status" → `{t('status')}`
- "Category" → `{t('category')}`
- "View Details" → `{t('viewDetails')}`

---

## Pattern Examples

### Replacing Static Text

```javascript
// Before
<h2>Recent Activity</h2>

// After
<h2>{t('recentActivity')}</h2>
```

### Replacing with Variables

```javascript
// Before
<p>Total: {count} complaints</p>

// After
<p>{t('total')}: {count} {t('complaints')}</p>
```

### Conditional Text

```javascript
// Before
{isLoading ? 'Loading...' : 'Ready'}

// After
{isLoading ? t('loading') : t('ready')}
```

### Button Text

```javascript
// Before
<button>Submit Complaint</button>

// After
<button>{t('submit')} {t('complaints')}</button>
```

### Table Headers

```javascript
// Before
<thead>
  <tr>
    <th>Title</th>
    <th>Status</th>
    <th>Category</th>
  </tr>
</thead>

// After
<thead>
  <tr>
    <th>{t('title')}</th>
    <th>{t('status')}</th>
    <th>{t('category')}</th>
  </tr>
</thead>
```

---

## Page-by-Page Checklist

### ✅ Layout (Done)
- Sidebar navigation
- Header elements
- User profile section

### ⚠️ Dashboard (Partial)
- [ ] Welcome message
- [ ] Metric cards
- [ ] Chart titles
- [ ] Section headings
- [ ] Button labels

### ⚠️ Analytics (Partial)
- [ ] Page title
- [ ] Filter labels
- [ ] Chart labels
- [ ] Export buttons
- [ ] Table headers

### ❌ Complaints (To Do)
- [ ] List headers
- [ ] Status badges
- [ ] Action buttons
- [ ] Filter labels

### ❌ Users (To Do)
- [ ] Table headers
- [ ] Role labels
- [ ] Action buttons

### ❌ Departments (To Do)
- [ ] Department names
- [ ] Metrics labels
- [ ] Performance indicators

### ❌ Settings (To Do)
- [ ] Section titles
- [ ] Form labels
- [ ] Save buttons

---

## Common Translations Reference

### Status Values (Already Available)
```javascript
{t('submitted')}    // ಸಲ್ಲಿಸಲಾಗಿದೆ
{t('assigned')}     // ನಿಯೋಜಿಸಲಾಗಿದೆ
{t('inProgress')}   // ಪ್ರಗತಿಯಲ್ಲಿದೆ
{t('resolved')}     // ಪರಿಹರಿಸಲಾಗಿದೆ
{t('closed')}       // ಮುಚ್ಚಲಾಗಿದೆ
{t('rejected')}     // ತಿರಸ್ಕರಿಸಲಾಗಿದೆ
```

### Categories (Already Available)
```javascript
{t('roadInfrastructure')}  // ರಸ್ತೆ ಮತ್ತು ಮೂಲಸೌಕರ್ಯ
{t('waterSupply')}         // ನೀರು ಸರಬರಾಜು
{t('electricity')}         // ವಿದ್ಯುತ್
{t('sanitation')}          // ನೈರ್ಮಲ್ಯ
```

### Actions (Already Available)
```javascript
{t('create')}    // ರಚಿಸಿ
{t('edit')}      // ಸಂಪಾದಿಸಿ
{t('delete')}    // ಅಳಿಸಿ
{t('save')}      // ಉಳಿಸಿ
{t('submit')}    // ಸಲ್ಲಿಸಿ
{t('cancel')}    // ರದ್ದುಗೊಳಿಸಿ
{t('search')}    // ಹುಡುಕಿ
{t('export')}    // ರಫ್ತು ಮಾಡಿ
```

---

## Testing Your Translation

### 1. Add Translation Hook
```javascript
const { t } = useTranslation();
```

### 2. Replace One String
```javascript
<h1>{t('dashboard')}</h1>
```

### 3. Save & Refresh Browser

### 4. Toggle Language
- Click "ಕನ್ನಡ" in sidebar
- See if text changes

### 5. If It Works
- Continue replacing more strings!

---

## Quick Wins (Easy Pages)

### Start Here for Quick Results

#### 1. Settings Page
Simple form labels, easy to translate:
```javascript
// settings.jsx
{t('name')}
{t('email')}
{t('phone')}
{t('save')}
```

#### 2. Users Page
Table headers and buttons:
```javascript
// users.jsx
{t('name')}
{t('role')}
{t('status')}
{t('edit')}
{t('delete')}
```

#### 3. Departments Page
Similar to users, mostly labels:
```javascript
// departments.jsx
{t('department')}
{t('totalAssigned')}
{t('completed')}
```

---

## Translation Tips

### ✅ Do
- Use existing translation keys when possible
- Keep translation keys descriptive (camelCase)
- Test both languages
- Add translations for both en and kn

### ❌ Don't
- Hardcode English strings
- Translate technical terms unnecessarily
- Forget to import useTranslation
- Skip testing in Kannada mode

---

## Need Help?

### Where are translations defined?
`/locales/translations.js`

### How do I know what keys exist?
Open `/locales/translations.js` and search for the English text

### What if a translation doesn't exist?
Add it to both `en` and `kn` objects in translations.js

### How do I test?
1. Click language toggle in sidebar
2. Navigate to your page
3. Check if text switches

---

## Example: Full Page Translation

### Before
```javascript
function ComplaintsList() {
  return (
    <div>
      <h1>Complaints</h1>
      <button>Create New</button>
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
      </table>
    </div>
  );
}
```

### After
```javascript
import { useTranslation } from '../hooks/useTranslation';

function ComplaintsList() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('complaints')}</h1>
      <button>{t('create')} {t('new')}</button>
      <table>
        <thead>
          <tr>
            <th>{t('title')}</th>
            <th>{t('status')}</th>
            <th>{t('actions')}</th>
          </tr>
        </thead>
      </table>
    </div>
  );
}
```

---

## Roadmap

### Phase 1 (Now)
- ✅ Translation system setup
- ✅ Sidebar & header translated
- ✅ 150+ translations ready
- ⚠️ Developer guide (this document)

### Phase 2 (Next)
- [ ] Translate all page headings
- [ ] Translate all buttons
- [ ] Translate all form labels
- [ ] Translate all table headers

### Phase 3 (Later)
- [ ] Translate tooltips
- [ ] Translate error messages
- [ ] Translate success messages
- [ ] Date/time localization

---

## Summary

**You have everything you need!**

1. ✅ Translation system is working
2. ✅ 150+ translations already available
3. ✅ Simple hook to use: `const { t } = useTranslation()`
4. ✅ Just replace strings: `"Text"` → `{t('key')}`

**Start translating!** Begin with simple pages like Settings or Users, then move to complex ones like Dashboard.

---

**Next Steps**:
1. Pick a page (start with Settings or Users)
2. Add `import { useTranslation } from '../hooks/useTranslation'`
3. Add `const { t } = useTranslation()` in component
4. Replace hardcoded strings with `{t('translationKey')}`
5. Test by toggling language
6. Move to next page!

**Need a translation that doesn't exist?** Add it to `/locales/translations.js` in both `en` and `kn` objects!

🎉 **Happy translating!**
