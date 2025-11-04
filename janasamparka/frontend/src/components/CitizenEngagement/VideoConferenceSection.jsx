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
  LinearProgress,
  Alert,
  Snackbar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemIcon,
  Divider,
  Badge,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  Videocam,
  VideocamOff,
  Mic,
  MicOff,
  ScreenShare,
  StopScreenShare,
  CallEnd,
  People,
  Schedule,
  LocationOn,
  Event,
  Public,
  Lock,
  RecordVoiceOver,
  Chat,
  Settings,
  Share,
  ContentCopy,
  CalendarToday,
  AccessTime
} from '@mui/icons-material';
import { format, addDays, isAfter, isBefore } from 'date-fns';

const VideoConferenceSection = ({ constituencyId, userRole, currentUser }) => {
  const theme = useTheme();
  
  const [activeTab, setActiveTab] = useState(0);
  const [conferences, setConferences] = useState([]);
  const [myConferences, setMyConferences] = useState([]);
  const [selectedConference, setSelectedConference] = useState(null);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [joinDialog, setJoinDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Form states
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    conference_type: 'meeting',
    scheduled_start: '',
    scheduled_end: '',
    max_participants: 100,
    is_public: false,
    requires_registration: true,
    is_recorded: false,
    venue: '',
    address: ''
  });

  // Conference states
  const [isInCall, setIsInCall] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [participants, setParticipants] = useState([]);

  // Fetch conferences
  const fetchConferences = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch all conferences
      const response = await fetch('/api/engagement/video-conferences', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConferences(data.items);
      }
      
      // Fetch my conferences
      if (userRole !== 'citizen') {
        const myResponse = await fetch('/api/engagement/video-conferences?my_conferences=true', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (myResponse.ok) {
          const myData = await myResponse.json();
          setMyConferences(myData.items);
        }
      }
      
    } catch (error) {
      console.error('Error fetching conferences:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConferences();
  }, [constituencyId]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleCreateConference = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/engagement/video-conferences', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          scheduled_start: new Date(formData.scheduled_start),
          scheduled_end: new Date(formData.scheduled_end)
        })
      });

      if (response.ok) {
        setSnackbar({ open: true, message: 'Conference created successfully!', severity: 'success' });
        setOpenDialog(false);
        setFormData({
          title: '',
          description: '',
          conference_type: 'meeting',
          scheduled_start: '',
          scheduled_end: '',
          max_participants: 100,
          is_public: false,
          requires_registration: true,
          is_recorded: false,
          venue: '',
          address: ''
        });
        fetchConferences();
      } else {
        setSnackbar({ open: true, message: 'Failed to create conference', severity: 'error' });
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'Error creating conference', severity: 'error' });
    }
  };

  const handleJoinConference = async (conference) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/engagement/video-conferences/${conference.id}/join`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setJoinDialog(false);
        setSelectedConference(data.conference);
        setIsInCall(true);
        setSnackbar({ open: true, message: 'Joined conference successfully!', severity: 'success' });
        
        // Open meeting URL in new tab
        window.open(data.join_url, '_blank');
      } else {
        setSnackbar({ open: true, message: 'Failed to join conference', severity: 'error' });
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'Error joining conference', severity: 'error' });
    }
  };

  const getConferenceIcon = (type) => {
    switch (type) {
      case 'one_on_one': return <Videocam />;
      case 'group_meeting': return <People />;
      case 'public_hearing': return <Public />;
      case 'press_conference': return <RecordVoiceOver />;
      case 'town_hall': return <Event />;
      case 'office_hours': return <Schedule />;
      default: return <Videocam />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'info';
      case 'started': return 'success';
      case 'ended': return 'default';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const isConferenceLive = (conference) => {
    const now = new Date();
    const start = new Date(conference.scheduled_start);
    const end = new Date(conference.scheduled_end);
    return isAfter(now, start) && isBefore(now, end) && conference.status === 'started';
  };

  const isConferenceUpcoming = (conference) => {
    const now = new Date();
    const start = new Date(conference.scheduled_start);
    return isAfter(start, now) && conference.status === 'scheduled';
  };

  // Conference Card Component
  const ConferenceCard = ({ conference, showActions = true }) => (
    <Card sx={{ mb: 2, cursor: 'pointer' }} onClick={() => setSelectedConference(conference)}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
            {getConferenceIcon(conference.conference_type)}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom>
              {conference.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <Chip label={conference.conference_type.replace('_', ' ').toUpperCase()} size="small" />
              <Chip label={conference.status} color={getStatusColor(conference.status)} size="small" />
              {conference.is_public ? (
                <Chip icon={<Public />} label="Public" size="small" />
              ) : (
                <Chip icon={<Lock />} label="Private" size="small" />
              )}
              {isConferenceLive(conference) && (
                <Chip label="LIVE" color="error" size="small" />
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {conference.description}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CalendarToday sx={{ fontSize: 16, mr: 0.5 }} />
                <Typography variant="caption">
                  {format(new Date(conference.scheduled_start), 'MMM dd, yyyy')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AccessTime sx={{ fontSize: 16, mr: 0.5 }} />
                <Typography variant="caption">
                  {format(new Date(conference.scheduled_start), 'hh:mm a')} - 
                  {format(new Date(conference.scheduled_end), 'hh:mm a')}
                </Typography>
              </Box>
            </Box>
            {conference.venue && (
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <LocationOn sx={{ fontSize: 16, mr: 0.5 }} />
                <Typography variant="caption">
                  {conference.venue}
                </Typography>
              </Box>
            )}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                {conference.registered_participants} / {conference.max_participants} participants
              </Typography>
              {showActions && (
                <Box>
                  {isConferenceLive(conference) ? (
                    <Button
                      variant="contained"
                      color="error"
                      size="small"
                      startIcon={<Videocam />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleJoinConference(conference);
                      }}
                    >
                      Join Now
                    </Button>
                  ) : isConferenceUpcoming(conference) ? (
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<Schedule />}
                      onClick={(e) => {
                        e.stopPropagation();
                        setJoinDialog(true);
                        setSelectedConference(conference);
                      }}
                    >
                      Register
                    </Button>
                  ) : (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Share />}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(conference.meeting_url);
                        setSnackbar({ open: true, message: 'Meeting link copied!', severity: 'success' });
                      }}
                    >
                      Copy Link
                    </Button>
                  )}
                </Box>
              )}
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  // In-Call Interface Component
  const InCallInterface = () => (
    <Card sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            {selectedConference?.title}
          </Typography>
          <Badge badgeContent={participants.length} color="primary">
            <People />
          </Badge>
        </Box>

        {/* Video Area */}
        <Box sx={{ flexGrow: 1, bgcolor: 'black', borderRadius: 1, mb: 2, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="h6" color="white">
            {isVideoOff ? 'Camera Off' : 'Video Feed'}
          </Typography>
          
          {/* Participant Grid */}
          <Grid container spacing={1} sx={{ position: 'absolute', top: 8, right: 8, width: 200 }}>
            {participants.slice(0, 4).map((participant, index) => (
              <Grid item xs={6} key={index}>
                <Box sx={{ bgcolor: 'grey.800', borderRadius: 1, p: 1, height: 80 }}>
                  <Typography variant="caption" color="white">
                    {participant.name}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Controls */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Tooltip title={isMuted ? "Unmute" : "Mute"}>
            <IconButton
              color={isMuted ? "error" : "default"}
              onClick={() => setIsMuted(!isMuted)}
              sx={{ bgcolor: 'grey.100' }}
            >
              {isMuted ? <MicOff /> : <Mic />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title={isVideoOff ? "Turn on Camera" : "Turn off Camera"}>
            <IconButton
              color={isVideoOff ? "error" : "default"}
              onClick={() => setIsVideoOff(!isVideoOff)}
              sx={{ bgcolor: 'grey.100' }}
            >
              {isVideoOff ? <VideocamOff /> : <Videocam />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title={isScreenSharing ? "Stop Sharing" : "Share Screen"}>
            <IconButton
              color={isScreenSharing ? "primary" : "default"}
              onClick={() => setIsScreenSharing(!isScreenSharing)}
              sx={{ bgcolor: 'grey.100' }}
            >
              {isScreenSharing ? <StopScreenShare /> : <ScreenShare />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title="End Call">
            <IconButton
              color="error"
              onClick={() => {
                setIsInCall(false);
                setSelectedConference(null);
              }}
              sx={{ bgcolor: 'error.main', color: 'white' }}
            >
              <CallEnd />
            </IconButton>
          </Tooltip>
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
          Video Conferences
        </Typography>
        {userRole !== 'citizen' && (
          <Button
            variant="contained"
            startIcon={<Videocam />}
            onClick={() => setOpenDialog(true)}
          >
            Create Conference
          </Button>
        )}
      </Box>

      {/* In-Call Interface */}
      {isInCall && selectedConference ? (
        <InCallInterface />
      ) : (
        <>
          {/* Tabs */}
          <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
            <Tab label="Upcoming Conferences" />
            <Tab label="My Conferences" />
            <Tab label="Past Conferences" />
          </Tabs>

          {/* Tab Content */}
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Upcoming Conferences
              </Typography>
              {conferences
                .filter(c => c.status === 'scheduled')
                .map(conference => (
                  <ConferenceCard key={conference.id} conference={conference} />
                ))}
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                My Conferences
              </Typography>
              {myConferences.map(conference => (
                <ConferenceCard key={conference.id} conference={conference} />
              ))}
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Past Conferences
              </Typography>
              {conferences
                .filter(c => c.status === 'ended')
                .map(conference => (
                  <ConferenceCard key={conference.id} conference={conference} showActions={false} />
                ))}
            </Box>
          )}
        </>
      )}

      {/* Create Conference Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Video Conference</DialogTitle>
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
                rows={3}
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={formData.conference_type}
                  onChange={(e) => setFormData({ ...formData, conference_type: e.target.value })}
                  label="Type"
                >
                  <MenuItem value="one_on_one">One-on-One</MenuItem>
                  <MenuItem value="group_meeting">Group Meeting</MenuItem>
                  <MenuItem value="public_hearing">Public Hearing</MenuItem>
                  <MenuItem value="press_conference">Press Conference</MenuItem>
                  <MenuItem value="town_hall">Town Hall</MenuItem>
                  <MenuItem value="office_hours">Office Hours</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Max Participants"
                value={formData.max_participants}
                onChange={(e) => setFormData({ ...formData, max_participants: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="datetime-local"
                label="Start Time"
                value={formData.scheduled_start}
                onChange={(e) => setFormData({ ...formData, scheduled_start: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="datetime-local"
                label="End Time"
                value={formData.scheduled_end}
                onChange={(e) => setFormData({ ...formData, scheduled_end: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Venue (Optional)"
                value={formData.venue}
                onChange={(e) => setFormData({ ...formData, venue: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Address (Optional)"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateConference} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Join Conference Dialog */}
      <Dialog open={joinDialog} onClose={() => setJoinDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Join Conference</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {selectedConference?.title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {selectedConference?.description}
          </Typography>
          <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Meeting Link
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              <Typography variant="body2" sx={{ flexGrow: 1 }}>
                {selectedConference?.meeting_url}
              </Typography>
              <IconButton
                size="small"
                onClick={() => {
                  navigator.clipboard.writeText(selectedConference?.meeting_url);
                  setSnackbar({ open: true, message: 'Link copied!', severity: 'success' });
                }}
              >
                <ContentCopy />
              </IconButton>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setJoinDialog(false)}>Cancel</Button>
          <Button
            onClick={() => handleJoinConference(selectedConference)}
            variant="contained"
            startIcon={<Videocam />}
          >
            Join Conference
          </Button>
        </DialogActions>
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

export default VideoConferenceSection;
