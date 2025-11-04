import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Avatar,
  IconButton,
  Button,
  Grid,
  Fade,
  Slide,
  Paper,
  Divider,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Article,
  Schedule,
  Event,
  LocationOn,
  People,
  AccessTime,
  ArrowForward,
  Close,
  Refresh,
  Share,
  Bookmark,
  BookmarkBorder
} from '@mui/icons-material';
import { format } from 'date-fns';

const NewsSection = ({ constituencyId, userRole }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [newsData, setNewsData] = useState({
    featuredNews: [],
    latestNews: [],
    upcomingSchedules: [],
    tickerItems: []
  });
  const [loading, setLoading] = useState(true);
  const [selectedNews, setSelectedNews] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [savedItems, setSavedItems] = useState(new Set());

  // Fetch dashboard content
  const fetchDashboardContent = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('/api/news/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setNewsData(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard content:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardContent();
  }, [constituencyId]);

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  // Get category color
  const getCategoryColor = (category) => {
    const colors = {
      local_development: 'primary',
      government_initiative: 'secondary',
      public_service: 'success',
      meeting: 'info',
      achievement: 'warning',
      announcement: 'error',
      emergency: 'error',
      other: 'default'
    };
    return colors[category] || 'default';
  };

  // Toggle saved item
  const toggleSaved = (itemId) => {
    const newSaved = new Set(savedItems);
    if (newSaved.has(itemId)) {
      newSaved.delete(itemId);
    } else {
      newSaved.add(itemId);
    }
    setSavedItems(newSaved);
  };

  // Share functionality
  const shareItem = (item, type) => {
    if (navigator.share) {
      navigator.share({
        title: item.title,
        text: item.summary || item.content,
        url: window.location.origin
      });
    } else {
      // Fallback - copy to clipboard
      navigator.clipboard.writeText(
        `${item.title}\n${item.summary || item.content}\n${window.location.origin}`
      );
    }
  };

  // News Card Component
  const NewsCard = ({ news, featured = false }) => (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8]
        }
      }}
      onClick={() => setSelectedNews(news)}
    >
      {news.featured_image_url && (
        <Box
          sx={{
            height: featured ? 200 : 140,
            backgroundImage: `url(${news.featured_image_url})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            position: 'relative'
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              display: 'flex',
              gap: 1
            }}
          >
            <IconButton
              size="small"
              sx={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
              onClick={(e) => {
                e.stopPropagation();
                toggleSaved(news.id);
              }}
            >
              {savedItems.has(news.id) ? <Bookmark /> : <BookmarkBorder />}
            </IconButton>
            <IconButton
              size="small"
              sx={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
              onClick={(e) => {
                e.stopPropagation();
                shareItem(news, 'news');
              }}
            >
              <Share />
            </IconButton>
          </Box>
        </Box>
      )}
      
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Chip 
            label={news.category.replace('_', ' ')} 
            color={getCategoryColor(news.category)}
            size="small"
          />
          <Chip 
            label={news.priority} 
            color={getPriorityColor(news.priority)}
            size="small"
          />
        </Box>
        
        <Typography 
          variant={featured ? "h6" : "subtitle1"} 
          gutterBottom 
          sx={{ 
            fontWeight: featured ? 'bold' : 'medium',
            lineHeight: 1.3
          }}
        >
          {news.title}
        </Typography>
        
        {news.summary && (
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ 
              mb: 2,
              display: '-webkit-box',
              WebkitLineClamp: featured ? 3 : 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}
          >
            {news.summary}
          </Typography>
        )}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            {format(new Date(news.created_at), 'MMM dd, yyyy')}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {news.view_count} views
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  // Schedule Card Component
  const ScheduleCard = ({ schedule }) => (
    <Card 
      sx={{ 
        height: '100%', 
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[6]
        }
      }}
      onClick={() => setSelectedSchedule(schedule)}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
            <Event />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
              {schedule.title}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {schedule.schedule_type.replace('_', ' ').toUpperCase()}
            </Typography>
          </Box>
          {schedule.is_featured && (
            <Chip label="Featured" color="primary" size="small" />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AccessTime sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
          <Typography variant="body2">
            {format(new Date(schedule.start_datetime), 'MMM dd, hh:mm a')}
          </Typography>
        </Box>
        
        {schedule.venue && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <LocationOn sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="body2">
              {schedule.venue}
            </Typography>
          </Box>
        )}
        
        {schedule.expected_attendees && (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <People sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="body2">
              Expected: {schedule.expected_attendees} attendees
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  // Ticker Component
  const Ticker = () => (
    <Paper 
      elevation={2} 
      sx={{ 
        overflow: 'hidden', 
        backgroundColor: '#f5f5f5',
        mb: 3
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', py: 1 }}>
        <Typography 
          variant="body2" 
          sx={{ 
            px: 2, 
            py: 1, 
            backgroundColor: theme.palette.primary.main,
            color: 'white',
            fontWeight: 'bold',
            whiteSpace: 'nowrap'
          }}
        >
          LATEST UPDATES
        </Typography>
        <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
          <Box
            sx={{
              display: 'flex',
              animation: 'scroll 30s linear infinite',
              '@keyframes scroll': {
                '0%': { transform: 'translateX(100%)' },
                '100%': { transform: 'translateX(-100%)' }
              }
            }}
          >
            {newsData.tickerItems.map((item, index) => (
              <Box
                key={item.id}
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  px: 3,
                  py: 1,
                  whiteSpace: 'nowrap',
                  backgroundColor: item.background_color,
                  color: item.text_color,
                  mx: 1,
                  borderRadius: 1
                }}
              >
                {item.icon && <span style={{ marginRight: 8 }}>{item.icon}</span>}
                <Typography variant="body2">
                  {item.content}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      </Box>
    </Paper>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <Typography>Loading news and updates...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          News & Updates
        </Typography>
        <IconButton onClick={fetchDashboardContent}>
          <Refresh />
        </IconButton>
      </Box>

      {/* Ticker */}
      {newsData.tickerItems.length > 0 && <Ticker />}

      <Grid container spacing={3}>
        {/* Featured News */}
        {newsData.featuredNews.length > 0 && (
          <Grid item xs={12} md={8}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'medium' }}>
              Featured News
            </Typography>
            <Grid container spacing={2}>
              {newsData.featuredNews.slice(0, 2).map((news) => (
                <Grid item xs={12} sm={6} key={news.id}>
                  <NewsCard news={news} featured />
                </Grid>
              ))}
            </Grid>
          </Grid>
        )}

        {/* Upcoming Schedules */}
        {newsData.upcomingSchedules.length > 0 && (
          <Grid item xs={12} md={4}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'medium' }}>
              Upcoming Events
            </Typography>
            {newsData.upcomingSchedules.slice(0, 3).map((schedule) => (
              <Box key={schedule.id} sx={{ mb: 2 }}>
                <ScheduleCard schedule={schedule} />
              </Box>
            ))}
          </Grid>
        )}

        {/* Latest News */}
        {newsData.latestNews.length > 0 && (
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 'medium' }}>
                Latest News
              </Typography>
              <Button 
                endIcon={<ArrowForward />}
                size="small"
                onClick={() => window.location.href = '/news'}
              >
                View All
              </Button>
            </Box>
            <Grid container spacing={2}>
              {newsData.latestNews.slice(0, 6).map((news) => (
                <Grid item xs={12} sm={6} md={4} key={news.id}>
                  <NewsCard news={news} />
                </Grid>
              ))}
            </Grid>
          </Grid>
        )}
      </Grid>

      {/* News Detail Dialog */}
      <Dialog 
        open={!!selectedNews} 
        onClose={() => setSelectedNews(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedNews && (
          <>
            <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">{selectedNews.title}</Typography>
              <IconButton onClick={() => setSelectedNews(null)}>
                <Close />
              </IconButton>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={selectedNews.category.replace('_', ' ')} 
                  color={getCategoryColor(selectedNews.category)}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip 
                  label={selectedNews.priority} 
                  color={getPriorityColor(selectedNews.priority)}
                  size="small"
                />
              </Box>
              
              {selectedNews.featured_image_url && (
                <Box
                  component="img"
                  src={selectedNews.featured_image_url}
                  alt={selectedNews.title}
                  sx={{ width: '100%', height: 300, objectFit: 'cover', mb: 2, borderRadius: 1 }}
                />
              )}
              
              <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.6 }}>
                {selectedNews.content}
              </Typography>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  By {selectedNews.author || 'Admin'} • {format(new Date(selectedNews.created_at), 'MMM dd, yyyy')}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {selectedNews.view_count} views
                </Typography>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => shareItem(selectedNews, 'news')}>
                Share
              </Button>
              <Button onClick={() => toggleSaved(selectedNews.id)}>
                {savedItems.has(selectedNews.id) ? 'Remove from Saved' : 'Save'}
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Schedule Detail Dialog */}
      <Dialog 
        open={!!selectedSchedule} 
        onClose={() => setSelectedSchedule(null)}
        maxWidth="sm"
        fullWidth
      >
        {selectedSchedule && (
          <>
            <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">{selectedSchedule.title}</Typography>
              <IconButton onClick={() => setSelectedSchedule(null)}>
                <Close />
              </IconButton>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={selectedSchedule.schedule_type.replace('_', ' ').toUpperCase()}
                  color="primary"
                  size="small"
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Date & Time
                </Typography>
                <Typography variant="body1">
                  {format(new Date(selectedSchedule.start_datetime), 'EEEE, MMM dd, yyyy')}
                </Typography>
                <Typography variant="body1">
                  {format(new Date(selectedSchedule.start_datetime), 'hh:mm a')} - 
                  {format(new Date(selectedSchedule.end_datetime), 'hh:mm a')}
                </Typography>
              </Box>
              
              {selectedSchedule.venue && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Venue
                  </Typography>
                  <Typography variant="body1">{selectedSchedule.venue}</Typography>
                  {selectedSchedule.address && (
                    <Typography variant="body2" color="text.secondary">
                      {selectedSchedule.address}
                    </Typography>
                  )}
                </Box>
              )}
              
              {selectedSchedule.description && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Description
                  </Typography>
                  <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                    {selectedSchedule.description}
                  </Typography>
                </Box>
              )}
              
              {selectedSchedule.agenda && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Agenda
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                    {selectedSchedule.agenda}
                  </Typography>
                </Box>
              )}
              
              {selectedSchedule.contact_person && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Contact Information
                  </Typography>
                  <Typography variant="body1">
                    {selectedSchedule.contact_person}
                  </Typography>
                  {selectedSchedule.contact_phone && (
                    <Typography variant="body2" color="text.secondary">
                      {selectedSchedule.contact_phone}
                    </Typography>
                  )}
                  {selectedSchedule.contact_email && (
                    <Typography variant="body2" color="text.secondary">
                      {selectedSchedule.contact_email}
                    </Typography>
                  )}
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => shareItem(selectedSchedule, 'schedule')}>
                Share Event
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default NewsSection;
