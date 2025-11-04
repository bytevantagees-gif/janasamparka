import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Tabs,
  Tab,
  Badge,
  LinearProgress,
  Alert,
  Snackbar,
  useTheme,
  useMediaQuery,
  Fab,
  Tooltip
} from '@mui/material';
import {
  Add,
  Feedback,
  Lightbulb,
  ThumbUp,
  ThumbDown,
  Send,
  Schedule,
  Videocam,
  Campaign,
  FilterList,
  Search,
  MoreVert,
  Reply,
  Share,
  Bookmark,
  BookmarkBorder,
  LocationOn,
  AttachFile,
  VideoCall
} from '@mui/icons-material';
import { format } from 'date-fns';

const FeedbackSection = ({ constituencyId, userRole, currentUser }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [activeTab, setActiveTab] = useState(0);
  const [feedbackList, setFeedbackList] = useState([]);
  const [conferences, setConferences] = useState([]);
  const [broadcasts, setBroadcasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Form states
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    feedback_type: 'complaint',
    priority: 'medium',
    category: '',
    is_public: false,
    is_anonymous: false
  });

  // Fetch data
  const fetchFeedbackData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch feedback
      const feedbackResponse = await fetch('/api/engagement/feedback', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (feedbackResponse.ok) {
        const feedbackData = await feedbackResponse.json();
        setFeedbackList(feedbackData.items);
      }
      
      // Fetch conferences
      const conferenceResponse = await fetch('/api/engagement/video-conferences?upcoming=true', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (conferenceResponse.ok) {
        const conferenceData = await conferenceResponse.json();
        setConferences(conferenceData.items);
      }
      
      // Fetch broadcasts
      const broadcastResponse = await fetch('/api/engagement/broadcasts?upcoming=true', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (broadcastResponse.ok) {
        const broadcastData = await broadcastResponse.json();
        setBroadcasts(broadcastData.items);
      }
      
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedbackData();
  }, [constituencyId]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSubmitFeedback = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/engagement/feedback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSnackbar({ open: true, message: 'Feedback submitted successfully!', severity: 'success' });
        setOpenDialog(false);
        setFormData({
          title: '',
          content: '',
          feedback_type: 'complaint',
          priority: 'medium',
          category: '',
          is_public: false,
          is_anonymous: false
        });
        fetchFeedbackData();
      } else {
        setSnackbar({ open: true, message: 'Failed to submit feedback', severity: 'error' });
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'Error submitting feedback', severity: 'error' });
    }
  };

  const handleVote = async (feedbackId, voteType) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/engagement/feedback/${feedbackId}/vote?vote_type=${voteType}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchFeedbackData();
      }
    } catch (error) {
      console.error('Error voting:', error);
    }
  };

  const getFeedbackIcon = (type) => {
    switch (type) {
      case 'complaint': return <Feedback color="error" />;
      case 'suggestion': return <Lightbulb color="warning" />;
      case 'idea': return <Lightbulb color="primary" />;
      case 'appreciation': return <ThumbUp color="success" />;
      default: return <Feedback />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return 'success';
      case 'in_progress': return 'warning';
      case 'under_review': return 'info';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  // Feedback Card Component
  const FeedbackCard = ({ feedback }) => (
    <Card sx={{ mb: 2, cursor: 'pointer' }} onClick={() => setSelectedFeedback(feedback)}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ mr: 2 }}>
            {getFeedbackIcon(feedback.feedback_type)}
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom>
              {feedback.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <Chip label={feedback.feedback_type} size="small" />
              <Chip label={feedback.priority} color={getPriorityColor(feedback.priority)} size="small" />
              <Chip label={feedback.status} color={getStatusColor(feedback.status)} size="small" />
              {feedback.category && <Chip label={feedback.category} variant="outlined" size="small" />}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {feedback.content.substring(0, 200)}{feedback.content.length > 200 ? '...' : ''}
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                {format(new Date(feedback.created_at), 'MMM dd, yyyy')}
                {feedback.location_address && ` • ${feedback.location_address}`}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconButton size="small" onClick={(e) => {
                  e.stopPropagation();
                  handleVote(feedback.id, 'up');
                }}>
                  <ThumbUp fontSize="small" />
                  <Typography variant="caption" sx={{ ml: 0.5 }}>{feedback.upvotes}</Typography>
                </IconButton>
                <IconButton size="small" onClick={(e) => {
                  e.stopPropagation();
                  handleVote(feedback.id, 'down');
                }}>
                  <ThumbDown fontSize="small" />
                  <Typography variant="caption" sx={{ ml: 0.5 }}>{feedback.downvotes}</Typography>
                </IconButton>
              </Box>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  // Conference Card Component
  const ConferenceCard = ({ conference }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
            <Videocam />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom>
              {conference.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {conference.conference_type.replace('_', ' ').toUpperCase()}
            </Typography>
          </Box>
          {conference.is_public && (
            <Chip label="Public" color="primary" size="small" />
          )}
        </Box>
        
        <Typography variant="body2" sx={{ mb: 2 }}>
          {conference.description}
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            {format(new Date(conference.scheduled_start), 'MMM dd, yyyy • hh:mm a')}
          </Typography>
          <Button
            variant="contained"
            size="small"
            startIcon={<VideoCall />}
            onClick={() => window.open(conference.meeting_url, '_blank')}
          >
            Join
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  // Broadcast Card Component
  const BroadcastCard = ({ broadcast }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: theme.palette.secondary.main, mr: 2 }}>
            <Campaign />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom>
              {broadcast.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {broadcast.broadcast_type.replace('_', ' ').toUpperCase()}
            </Typography>
          </Box>
          <Chip label={`Priority: ${broadcast.priority}`} color="warning" size="small" />
        </Box>
        
        <Typography variant="body2" sx={{ mb: 2 }}>
          {broadcast.message}
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Scheduled for: {format(new Date(broadcast.scheduled_at), 'MMM dd, yyyy • hh:mm a')}
          </Typography>
          <Box>
            {broadcast.send_push && <Chip label="Push" size="small" sx={{ mr: 1 }} />}
            {broadcast.send_sms && <Chip label="SMS" size="small" sx={{ mr: 1 }} />}
            {broadcast.send_email && <Chip label="Email" size="small" />}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Citizen Engagement
        </Typography>
        <Fab
          color="primary"
          aria-label="add"
          onClick={() => setOpenDialog(true)}
          sx={{ position: 'fixed', bottom: 16, right: 16, zIndex: 1000 }}
        >
          <Add />
        </Fab>
      </Box>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Feedback & Ideas" />
        <Tab label="Video Conferences" />
        <Tab label="Broadcasts" />
      </Tabs>

      {/* Search and Filter */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          placeholder="Search feedback..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{ startAdornment: <Search /> }}
          sx={{ flexGrow: 1 }}
        />
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Filter</InputLabel>
          <Select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            label="Filter"
          >
            <MenuItem value="all">All Types</MenuItem>
            <MenuItem value="complaint">Complaints</MenuItem>
            <MenuItem value="suggestion">Suggestions</MenuItem>
            <MenuItem value="idea">Ideas</MenuItem>
            <MenuItem value="appreciation">Appreciation</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Recent Feedback & Ideas
          </Typography>
          {feedbackList
            .filter(item => filterType === 'all' || item.feedback_type === filterType)
            .filter(item => item.title.toLowerCase().includes(searchQuery.toLowerCase()))
            .map(feedback => (
              <FeedbackCard key={feedback.id} feedback={feedback} />
            ))}
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Upcoming Video Conferences
          </Typography>
          {conferences.map(conference => (
            <ConferenceCard key={conference.id} conference={conference} />
          ))}
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Scheduled Broadcasts
          </Typography>
          {broadcasts.map(broadcast => (
            <BroadcastCard key={broadcast.id} broadcast={broadcast} />
          ))}
        </Box>
      )}

      {/* Create Feedback Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Submit Feedback</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={formData.feedback_type}
                  onChange={(e) => setFormData({ ...formData, feedback_type: e.target.value })}
                  label="Type"
                >
                  <MenuItem value="complaint">Complaint</MenuItem>
                  <MenuItem value="suggestion">Suggestion</MenuItem>
                  <MenuItem value="idea">Idea</MenuItem>
                  <MenuItem value="appreciation">Appreciation</MenuItem>
                  <MenuItem value="query">Query</MenuItem>
                  <MenuItem value="grievance">Grievance</MenuItem>
                  <MenuItem value="request">Request</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Category (Optional)"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmitFeedback} variant="contained" startIcon={<Send />}>
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Feedback Detail Dialog */}
      <Dialog open={!!selectedFeedback} onClose={() => setSelectedFeedback(null)} maxWidth="md" fullWidth>
        {selectedFeedback && (
          <>
            <DialogTitle>{selectedFeedback.title}</DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                {getFeedbackIcon(selectedFeedback.feedback_type)}
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <Chip label={selectedFeedback.feedback_type} />
                  <Chip label={selectedFeedback.priority} color={getPriorityColor(selectedFeedback.priority)} />
                  <Chip label={selectedFeedback.status} color={getStatusColor(selectedFeedback.status)} />
                  {selectedFeedback.reference_number && (
                    <Chip label={`Ref: ${selectedFeedback.reference_number}`} variant="outlined" />
                  )}
                </Box>
              </Box>
              
              <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.6 }}>
                {selectedFeedback.content}
              </Typography>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  {format(new Date(selectedFeedback.created_at), 'MMM dd, yyyy')}
                  {selectedFeedback.location_address && ` • ${selectedFeedback.location_address}`}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <IconButton onClick={() => handleVote(selectedFeedback.id, 'up')}>
                    <ThumbUp />
                    <Typography variant="caption">{selectedFeedback.upvotes}</Typography>
                  </IconButton>
                  <IconButton onClick={() => handleVote(selectedFeedback.id, 'down')}>
                    <ThumbDown />
                    <Typography variant="caption">{selectedFeedback.downvotes}</Typography>
                  </IconButton>
                </Box>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedFeedback(null)}>Close</Button>
              <Button startIcon={<Reply />}>Respond</Button>
              <Button startIcon={<Share />}>Share</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FeedbackSection;
