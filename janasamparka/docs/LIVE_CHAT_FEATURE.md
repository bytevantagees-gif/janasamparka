# Live Chat Feature with Moderation - Complete Implementation

## 🎯 Overview

A complete live chat system for video conferences with **mandatory moderation** to prevent abuse and ensure quality conversations during MLA town halls and virtual office hours.

---

## ✅ What's Implemented

### 1. **Database Schema**
- **Table**: `conference_chat_messages`
- **Moderation Fields**:
  - `is_approved` - Whether moderator approved the message
  - `is_rejected` - Whether moderator rejected the message
  - `moderated_by` - Which moderator took action
  - `moderated_at` - When the action was taken
  - `rejection_reason` - Why the message was rejected

### 2. **API Endpoints** (`/api/chat/`)

**For All Users (Citizens & Moderators):**
- `POST /conferences/{id}/chat` - Send a message
  - Citizens: Goes to moderation queue (not visible yet)
  - Result: Message created, pending approval

- `GET /conferences/{id}/chat` - View approved messages
  - Only shows approved, non-deleted messages
  - Real-time updates every 5 seconds

**For Moderators Only:**
- `GET /conferences/{id}/chat/pending` - View messages awaiting approval
- `POST /conferences/{id}/chat/{msg_id}/moderate` - Approve or reject
  - Action: "approve" or "reject"
  - Optional: rejection_reason
  
- `POST /conferences/{id}/chat/{msg_id}/pin` - Pin important messages
- `POST /conferences/{id}/chat/{msg_id}/answer` - Mark Q&A as answered
- `GET /conferences/{id}/chat/stats` - Get moderation statistics

### 3. **Frontend Component** (`ConferenceChat.jsx`)

**Features:**
- ✅ Live scrolling chat
- ✅ Auto-refresh every 5 seconds
- ✅ Send messages with Q&A marking
- ✅ Like/upvote messages
- ✅ View pinned messages
- ✅ Moderator approval panel (if user is moderator)
- ✅ One-click approve/reject buttons
- ✅ Visual indicators (pinned, Q&A, answered)

**How to Use:**
```jsx
import ConferenceChat from '../components/ConferenceChat';

// For citizens
<ConferenceChat conferenceId="conference-uuid" />

// For moderators
<ConferenceChat 
  conferenceId="conference-uuid" 
  isModerator={true} 
/>
```

### 4. **Moderation Workflow**

```
Citizen sends message
        ↓
Message saved (is_approved=false)
        ↓
Appears in moderator's pending queue
        ↓
Moderator reviews
        ↓
    ┌───────┴────────┐
    ↓                ↓
APPROVE           REJECT
    ↓                ↓
Visible to all   Hidden forever
```

**Moderator Actions:**
- ✅ Click to approve
- ❌ Click to reject with reason
- 📌 Pin important messages
- ✓ Mark Q&A as answered

---

## 📊 Sample Data (Already Seeded)

Run: `docker exec janasamparka_backend python seed_conference_chat.py`

**What you get:**
- 4 approved messages (visible to all)
- 3 pending messages (waiting for moderator)
- 1 rejected message (spam filtered)
- 2 Q&A questions
- 1 pinned message (moderator announcement)

---

## 🚀 Usage Examples

### For Citizens

**Send a message during town hall:**
```javascript
// Message goes to moderation queue
POST /api/chat/conferences/abc-123/chat
{
  "message": "When will the road work start?",
  "is_question": false
}

// Response
{
  "id": "msg-456",
  "is_approved": false,  // Waiting for approval
  "message": "When will the road work start?"
}
```

**View approved messages:**
```javascript
GET /api/chat/conferences/abc-123/chat

// Returns only approved messages
[
  {
    "id": "msg-789",
    "sender_name": "Ramesh Kumar",
    "message": "Great initiative!",
    "is_approved": true,
    "likes_count": 5,
    "is_pinned": false
  }
]
```

### For Moderators

**View pending messages:**
```javascript
GET /api/chat/conferences/abc-123/chat/pending

// Returns messages awaiting approval
[
  {
    "id": "msg-456",
    "sender_name": "Lakshmi Devi",
    "message": "When will the road work start?",
    "is_approved": false,
    "is_rejected": false
  }
]
```

**Approve a message:**
```javascript
POST /api/chat/conferences/abc-123/chat/msg-456/moderate
{
  "action": "approve"
}

// Message now visible to everyone
```

**Reject a message:**
```javascript
POST /api/chat/conferences/abc-123/chat/msg-456/moderate
{
  "action": "reject",
  "rejection_reason": "Spam content"
}

// Message hidden forever
```

---

## 🎨 UI Features

### Chat Display
- **Pinned messages**: Blue background, pin icon
- **MLA/Host messages**: Purple background
- **Regular messages**: Gray background
- **Q&A questions**: Purple badge
- **Answered questions**: Green badge

### Moderator Panel
- **Yellow alert box** at top showing pending count
- **One-click approve** (green checkmark)
- **One-click reject** (red X)
- **Auto-refresh** every 5 seconds
- **Real-time updates** when new messages arrive

---

## 🔒 Security & Abuse Prevention

### What Prevents Abuse:

1. **Mandatory Moderation**
   - ALL citizen messages must be approved
   - No message visible until moderator approves
   - Spam/abuse can be rejected instantly

2. **Rejection Tracking**
   - Track who rejected and why
   - Audit trail of all moderation actions
   - Can review rejection reasons

3. **Role-Based Access**
   - Only moderators can approve/reject
   - Only moderators see pending queue
   - Citizens only see approved messages

4. **Message Metadata**
   - Track sender name, role, timestamp
   - IP tracking can be added if needed
   - Rate limiting can be added

---

## 📈 Statistics & Monitoring

**Moderation stats endpoint:**
```javascript
GET /api/chat/conferences/abc-123/chat/stats

{
  "total_messages": 50,
  "approved": 42,
  "pending": 5,
  "rejected": 3,
  "questions": 12,
  "answered_questions": 8,
  "approval_rate": "84.0%"
}
```

Use this to:
- Monitor moderator efficiency
- Track abuse/spam rates
- See citizen engagement
- Q&A effectiveness

---

## 🔄 Auto-Refresh (Polling)

Currently using **5-second polling** for updates:
- Frontend fetches new messages every 5 seconds
- Moderators get pending messages every 5 seconds
- Approved messages appear automatically

### Future: WebSocket Support

For true real-time (optional upgrade):
```python
# WebSocket endpoint (to be implemented)
@router.websocket("/conferences/{id}/chat/ws")
async def chat_websocket(websocket: WebSocket, conference_id: str):
    # Real-time push updates
    # Instant message delivery
    # No polling needed
```

---

## 🎯 Best Practices

### For Moderators:

1. **Approve quickly** - Citizens see delay
2. **Be fair** - Only reject true spam/abuse
3. **Use pin feature** - Highlight important info
4. **Mark Q&A answered** - Show responsiveness
5. **Monitor stats** - Track engagement

### For System Admins:

1. **Monitor rejection rates** - High rate = too strict
2. **Review rejected messages** - Ensure fairness
3. **Track response time** - How fast are moderators?
4. **Analyze questions** - Common citizen concerns
5. **Export chat logs** - For reporting/analysis

---

## 📝 Integration Examples

### In Town Hall Page:
```jsx
import ConferenceChat from '../components/ConferenceChat';

function TownHallPage() {
  const isModerator = user.role === 'moderator' || user.role === 'admin';
  
  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        {/* Video player */}
        <VideoPlayer conferenceId={id} />
      </div>
      <div>
        {/* Live chat with moderation */}
        <ConferenceChat 
          conferenceId={id}
          isModerator={isModerator}
        />
      </div>
    </div>
  );
}
```

### In Virtual Office Hours:
```jsx
// Citizens can ask questions during 1-on-1 calls
<ConferenceChat 
  conferenceId={sessionId}
  isModerator={false}
/>
```

---

## 🐛 Testing

### Test Moderation Workflow:

1. **Login as citizen** → Send message
2. **Login as moderator** → See message in pending queue
3. **Approve message** → Message appears for everyone
4. **Send another as citizen** → Reject it
5. **Verify** → Rejected message never shows

### Test Q&A Feature:

1. **Send message with is_question=true**
2. **Moderator approves**
3. **Moderator marks as answered**
4. **Verify** → Shows "✓ Answered" badge

---

## ✅ Summary

**What You Have Now:**
- ✅ Complete live chat system
- ✅ Mandatory moderation workflow
- ✅ Abuse prevention built-in
- ✅ Q&A feature for town halls
- ✅ Pin important messages
- ✅ Auto-refresh updates
- ✅ Moderation statistics
- ✅ Sample data to test

**Ready to Use:**
- Citizens can chat during live events
- Moderators approve/reject in real-time
- No spam or abuse reaches audience
- Professional, YouTube-style experience

**Optional Future Enhancements:**
- WebSocket for true real-time (no polling)
- Message reactions (emoji)
- Threaded replies
- File/image sharing
- Chat export/archive

---

## 📞 Support

**Files to Check:**
- Backend: `/backend/app/routers/conference_chat.py`
- Model: `/backend/app/models/citizen_engagement.py`
- Frontend: `/admin-dashboard/src/components/ConferenceChat.jsx`
- Seed: `/backend/seed_conference_chat.py`

**API Docs:**
- Visit: `http://localhost:8000/docs`
- Section: "Conference Chat"

---

**Status: ✅ PRODUCTION READY**
