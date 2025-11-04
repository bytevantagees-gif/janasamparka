import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CircularProgress,
  Alert,
  Grid,
  Paper,
  Stack,
  Tabs,
  Tab,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Pending as PendingIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Category mapping (same as ComplaintsList)
const CATEGORY_MAP = {
  'roads_transport': { label: 'Roads & Transport', color: 'primary' },
  'water_sanitation': { label: 'Water & Sanitation', color: 'info' },
  'electricity': { label: 'Electricity', color: 'warning' },
  'health': { label: 'Health', color: 'error' },
  'education': { label: 'Education', color: 'success' },
  'agriculture': { label: 'Agriculture', color: 'secondary' },
  'social_welfare': { label: 'Social Welfare', color: 'default' },
  'others': { label: 'Others', color: 'default' }
};

// Status mapping
const STATUS_MAP = {
  'pending': { label: 'Pending', color: 'warning' },
  'assigned': { label: 'Assigned', color: 'info' },
  'in_progress': { label: 'In Progress', color: 'primary' },
  'resolved': { label: 'Resolved', color: 'success' },
  'closed': { label: 'Closed', color: 'default' }
};

export default function WardOfficerDashboard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState(0);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [publicNote, setPublicNote] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterCategory, setFilterCategory] = useState('');

  // Get user info from localStorage/context
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const token = localStorage.getItem('token');

  // Fetch ward complaints
  const { data: complaintsData, isLoading: complaintsLoading } = useQuery({
    queryKey: ['ward-complaints', filterStatus, filterCategory],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filterStatus) params.append('status', filterStatus);
      if (filterCategory) params.append('category', filterCategory);
      
      const response = await axios.get(
        `${API_BASE_URL}/complaints/my-ward?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    enabled: !!token
  });

  // Fetch available departments for ward
  const { data: departmentsData, isLoading: departmentsLoading } = useQuery({
    queryKey: ['ward-departments', user.ward_id],
    queryFn: async () => {
      const response = await axios.get(
        `${API_BASE_URL}/complaints/ward/${user.ward_id}/available-departments`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    enabled: !!token && !!user.ward_id && assignDialogOpen
  });

  // Assign complaint mutation
  const assignMutation = useMutation({
    mutationFn: async ({ complaintId, deptId, note }) => {
      const response = await axios.post(
        `${API_BASE_URL}/complaints/${complaintId}/ward-assign`,
        { dept_id: deptId, public_note: note },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['ward-complaints']);
      setAssignDialogOpen(false);
      setSelectedComplaint(null);
      setSelectedDepartment('');
      setPublicNote('');
    }
  });

  const handleAssignClick = (complaint) => {
    setSelectedComplaint(complaint);
    setAssignDialogOpen(true);
  };

  const handleAssignSubmit = () => {
    if (!selectedDepartment || !publicNote.trim()) {
      alert('Please select a department and provide a public note');
      return;
    }

    if (publicNote.length < 10) {
      alert('Public note must be at least 10 characters');
      return;
    }

    assignMutation.mutate({
      complaintId: selectedComplaint.id,
      deptId: selectedDepartment,
      note: publicNote
    });
  };

  const handleCloseDialog = () => {
    setAssignDialogOpen(false);
    setSelectedComplaint(null);
    setSelectedDepartment('');
    setPublicNote('');
  };

  // Calculate statistics
  const pendingCount = complaintsData?.complaints?.filter(c => c.assignment_type === 'ward' && c.status === 'pending').length || 0;
  const assignedToday = complaintsData?.complaints?.filter(c => {
    const assignedDate = new Date(c.updated_at);
    const today = new Date();
    return c.assignment_type === 'department' && 
           assignedDate.toDateString() === today.toDateString();
  }).length || 0;

  // Filter complaints based on tab
  const filteredComplaints = complaintsData?.complaints?.filter(c => {
    if (selectedTab === 0) return c.assignment_type === 'ward'; // Pending at ward
    if (selectedTab === 1) return c.assignment_type === 'department'; // Assigned to dept
    return true; // All
  }) || [];

  if (complaintsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Ward Officer Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage complaints for your ward and assign to appropriate departments
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box sx={{ 
                  bgcolor: 'primary.light', 
                  p: 2, 
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <AssignmentIcon sx={{ color: 'primary.main', fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {complaintsData?.total || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Complaints
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box sx={{ 
                  bgcolor: 'warning.light', 
                  p: 2, 
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <PendingIcon sx={{ color: 'warning.main', fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {pendingCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending Assignment
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box sx={{ 
                  bgcolor: 'success.light', 
                  p: 2, 
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <CheckCircleIcon sx={{ color: 'success.main', fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {assignedToday}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Assigned Today
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FilterIcon color="action" />
          <TextField
            select
            label="Status"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            size="small"
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="">All Statuses</MenuItem>
            {Object.entries(STATUS_MAP).map(([key, val]) => (
              <MenuItem key={key} value={key}>{val.label}</MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Category"
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            size="small"
            sx={{ minWidth: 180 }}
          >
            <MenuItem value="">All Categories</MenuItem>
            {Object.entries(CATEGORY_MAP).map(([key, val]) => (
              <MenuItem key={key} value={key}>{val.label}</MenuItem>
            ))}
          </TextField>
          {(filterStatus || filterCategory) && (
            <Button 
              size="small" 
              onClick={() => {
                setFilterStatus('');
                setFilterCategory('');
              }}
            >
              Clear Filters
            </Button>
          )}
        </Stack>
      </Paper>

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs value={selectedTab} onChange={(e, val) => setSelectedTab(val)}>
          <Tab label={`Pending at Ward (${pendingCount})`} />
          <Tab label="Assigned to Departments" />
          <Tab label="All Complaints" />
        </Tabs>
      </Paper>

      {/* Complaints List */}
      {filteredComplaints.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No complaints found
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={2}>
          {filteredComplaints.map((complaint) => (
            <Grid item xs={12} key={complaint.id}>
              <Card sx={{ 
                borderLeft: complaint.assignment_type === 'ward' ? '4px solid #ff9800' : '4px solid #2196f3'
              }}>
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    {/* Complaint Info */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        {complaint.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {complaint.description?.substring(0, 100)}
                        {complaint.description?.length > 100 && '...'}
                      </Typography>
                      <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                        <Chip 
                          label={CATEGORY_MAP[complaint.category]?.label || complaint.category}
                          color={CATEGORY_MAP[complaint.category]?.color || 'default'}
                          size="small"
                        />
                        <Chip 
                          label={STATUS_MAP[complaint.status]?.label || complaint.status}
                          color={STATUS_MAP[complaint.status]?.color || 'default'}
                          size="small"
                        />
                        {complaint.assignment_type === 'ward' && (
                          <Chip 
                            label="At Ward" 
                            color="warning" 
                            size="small" 
                            variant="outlined"
                          />
                        )}
                      </Stack>
                    </Grid>

                    {/* Actions */}
                    <Grid item xs={12} md={6} textAlign="right">
                      <Stack spacing={1} alignItems="flex-end">
                        <Typography variant="caption" color="text.secondary">
                          Created: {new Date(complaint.created_at).toLocaleDateString()}
                        </Typography>
                        
                        {complaint.assignment_type === 'ward' ? (
                          <Button
                            variant="contained"
                            color="primary"
                            startIcon={<AssignmentIcon />}
                            onClick={() => handleAssignClick(complaint)}
                            size="small"
                          >
                            Assign to Department
                          </Button>
                        ) : (
                          <Chip 
                            label="Assigned" 
                            color="success" 
                            size="small"
                            icon={<CheckCircleIcon />}
                          />
                        )}
                        
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<InfoIcon />}
                          onClick={() => navigate(`/complaints/${complaint.id}`)}
                        >
                          View Details
                        </Button>
                      </Stack>
                    </Grid>

                    {/* Public Notes (if any) */}
                    {complaint.public_notes && (
                      <Grid item xs={12}>
                        <Paper sx={{ p: 2, bgcolor: 'action.hover' }}>
                          <Typography variant="caption" color="text.secondary" fontWeight="bold">
                            PUBLIC NOTES (Visible to Citizen):
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                            {complaint.public_notes}
                          </Typography>
                        </Paper>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Assignment Dialog */}
      <Dialog 
        open={assignDialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Assign Complaint to Department</Typography>
            <IconButton onClick={handleCloseDialog} size="small">
              <CloseIcon />
            </IconButton>
          </Stack>
        </DialogTitle>
        <DialogContent dividers>
          {selectedComplaint && (
            <>
              {/* Complaint Summary */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'action.hover' }}>
                <Typography variant="subtitle2" gutterBottom>
                  {selectedComplaint.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedComplaint.description}
                </Typography>
                <Chip 
                  label={CATEGORY_MAP[selectedComplaint.category]?.label || selectedComplaint.category}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </Paper>

              {/* Department Selection */}
              <TextField
                select
                fullWidth
                label="Select Department"
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                required
                helperText="Only departments in your ward's jurisdiction are shown"
                sx={{ mb: 3 }}
                disabled={departmentsLoading}
              >
                {departmentsLoading ? (
                  <MenuItem disabled>
                    <CircularProgress size={20} /> Loading departments...
                  </MenuItem>
                ) : departmentsData && departmentsData.length > 0 ? (
                  departmentsData.map((dept) => (
                    <MenuItem key={dept.id} value={dept.id}>
                      {dept.name} ({dept.code})
                    </MenuItem>
                  ))
                ) : (
                  <MenuItem disabled>No departments available</MenuItem>
                )}
              </TextField>

              {/* Public Note */}
              <TextField
                fullWidth
                label="Public Note (Visible to Citizen)"
                placeholder="Explain why you're assigning to this department. E.g., 'Road pothole issue, assigning to PWD for immediate repair'"
                value={publicNote}
                onChange={(e) => setPublicNote(e.target.value)}
                multiline
                rows={4}
                required
                helperText={`${publicNote.length}/500 characters (minimum 10 required)`}
                inputProps={{ maxLength: 500 }}
                error={publicNote.length > 0 && publicNote.length < 10}
              />

              <Alert severity="info" sx={{ mt: 2 }}>
                <strong>Note:</strong> This note will be visible to the citizen who filed the complaint.
                Use clear language explaining why this department is appropriate.
              </Alert>

              {assignMutation.error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {assignMutation.error.response?.data?.detail || 'Failed to assign complaint'}
                </Alert>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={assignMutation.isPending}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleAssignSubmit}
            disabled={!selectedDepartment || publicNote.length < 10 || assignMutation.isPending}
          >
            {assignMutation.isPending ? <CircularProgress size={20} /> : 'Assign to Department'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
