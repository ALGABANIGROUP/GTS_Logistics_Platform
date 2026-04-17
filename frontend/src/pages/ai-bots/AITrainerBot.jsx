// frontend/src/pages/ai-bots/AITrainerBot.jsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Avatar,
  Rating,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  EmojiEvents as TrophyIcon,
  Timeline as TimelineIcon,
  ExpandMore as ExpandMoreIcon,
  PlayCircle as PlayIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon
} from '@mui/icons-material';
import { useNotification } from '../../contexts/NotificationContext';
import axiosClient from '../../api/axiosClient';

const AITrainerBot = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [courses, setCourses] = useState([]);
  const [userProgress, setUserProgress] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [certifications, setCertifications] = useState([]);
  const [stats, setStats] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [expandedCourse, setExpandedCourse] = useState(null);

  const { showSuccess, showError } = useNotification();

  // Fetch all data
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      console.log('Fetching trainer dashboard...');

      // Fetch data from API
      const [dashboardRes, coursesRes, progressRes, simulationsRes, certsRes, statsRes] = await Promise.all([
        axiosClient.get('/api/v1/trainer/dashboard').catch(e => ({ data: null })),
        axiosClient.get('/api/v1/trainer/courses').catch(e => ({ data: { courses: [] } })),
        axiosClient.get('/api/v1/trainer/progress').catch(e => ({ data: { progress: [] } })),
        axiosClient.get('/api/v1/trainer/simulations').catch(e => ({ data: { simulations: [] } })),
        axiosClient.get('/api/v1/trainer/certifications').catch(e => ({ data: { certifications: [] } })),
        axiosClient.get('/api/v1/trainer/stats').catch(e => ({ data: null }))
      ]);

      setDashboardData(dashboardRes.data);
      setCourses(coursesRes.data.courses || []);
      setUserProgress(progressRes.data.progress || []);
      setSimulations(simulationsRes.data.simulations || []);
      setCertifications(certsRes.data.certifications || []);
      setStats(statsRes.data);

    } catch (error) {
      console.error('Error fetching trainer data:', error);
      showError('Failed to load training data. Using seed data.');

      // Fallback seed data
      setCourses([
        { id: "course_001", title: "Commercial Vehicle Safety Inspection", category: "safety", duration_hours: 4, difficulty: "beginner", status: "published", enrolled_users: 156, completion_rate: 87.5 },
        { id: "course_002", title: "HOS Compliance for Drivers", category: "compliance", duration_hours: 3, difficulty: "beginner", status: "published", enrolled_users: 234, completion_rate: 92.3 },
        { id: "course_003", title: "Dangerous Goods Transportation", category: "safety", duration_hours: 8, difficulty: "advanced", status: "published", enrolled_users: 89, completion_rate: 76.4 },
        { id: "course_004", title: "Customer Service Excellence", category: "soft_skills", duration_hours: 2, difficulty: "beginner", status: "published", enrolled_users: 312, completion_rate: 94.2 }
      ]);

      setUserProgress([
        { course_id: "course_001", progress_percent: 100, status: "completed", score: 95.5 },
        { course_id: "course_002", progress_percent: 65, status: "in_progress" }
      ]);

      setSimulations([
        { id: "sim_001", name: "Emergency Braking Scenario", type: "driving", completions: 234, avg_score: 87.5 },
        { id: "sim_002", name: "Hazardous Spill Response", type: "safety", completions: 89, avg_score: 76.2 }
      ]);

      setStats({
        total_courses: 5,
        published_courses: 4,
        total_enrollments: 791,
        average_completion_rate: 87.6,
        active_learners: 45,
        certifications_issued: 128
      });

      setDashboardData({
        stats: stats || { total_courses: 5, published_courses: 4, total_enrollments: 791 }
      });

    } finally {
      setLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Start training course
  const startCourse = async (courseId) => {
    try {
      await axiosClient.post(`/api/v1/trainer/progress/${courseId}/start`);
      showSuccess('Course started successfully');
      fetchAllData();
    } catch (error) {
      showError('Failed to start course');
    }
  };

  // Get course difficulty color
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return '#4caf50';
      case 'intermediate': return '#ff9800';
      case 'advanced': return '#f44336';
      default: return '#757575';
    }
  };

  // Get category icon
  const getCategoryIcon = (category) => {
    const icons = {
      safety: '🛡️',
      compliance: '📋',
      operations: '⚙️',
      soft_skills: '💬',
      technical: '💻'
    };
    return icons[category] || '📚';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto', bgcolor: '#0e1c2d', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" sx={{ color: '#ffffff' }}>
            AI Trainer Bot
          </Typography>
          <Typography variant="body2" sx={{ color: '#b0b0b0', mt: 0.5 }}>
            Training courses, simulations, and certification management
          </Typography>
        </Box>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchAllData} sx={{ color: '#00d4ff', borderColor: '#00d4ff' }}>
          Refresh
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <SchoolIcon sx={{ fontSize: 40, color: '#00d4ff' }} />
                <Box>
                  <Typography variant="h3" fontWeight="bold" sx={{ color: '#ffffff' }}>{stats?.published_courses || 0}</Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>Active Courses</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <PeopleIcon sx={{ fontSize: 40, color: '#00ff88' }} />
                <Box>
                  <Typography variant="h3" fontWeight="bold" sx={{ color: '#ffffff' }}>{stats?.total_enrollments || 0}</Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>Enrollments</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrophyIcon sx={{ fontSize: 40, color: '#ff6b6b' }} />
                <Box>
                  <Typography variant="h3" fontWeight="bold" sx={{ color: '#ffffff' }}>{stats?.certifications_issued || 0}</Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>Certifications</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUpIcon sx={{ fontSize: 40, color: '#ffd93d' }} />
                <Box>
                  <Typography variant="h3" fontWeight="bold" sx={{ color: '#ffffff' }}>{stats?.average_completion_rate || 0}%</Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>Completion Rate</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="My Courses" />
        <Tab label="All Courses" />
        <Tab label="Simulations" />
        <Tab label="Certifications" />
      </Tabs>

      {/* My Courses Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {userProgress.length === 0 ? (
            <Grid size={{ xs: 12 }}>
              <Card sx={{ p: 6, textAlign: 'center', borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
                <SchoolIcon sx={{ fontSize: 64, color: '#b0b0b0' }} />
                <Typography variant="h6" sx={{ mt: 2, color: '#ffffff' }}>No courses started yet</Typography>
                <Button variant="contained" onClick={() => setTabValue(1)} sx={{ mt: 2, bgcolor: '#00d4ff', color: '#0e1c2d' }}>
                  Browse Courses
                </Button>
              </Card>
            </Grid>
          ) : (
            userProgress.map((progress) => {
              const course = courses.find(c => c.id === progress.course_id);
              if (!course) return null;
              return (
                <Grid key={course.id} size={{ xs: 12, md: 6 }}>
                  <Card sx={{ borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box>
                          <Typography variant="h6" fontWeight="bold" sx={{ color: '#ffffff' }}>{course.title}</Typography>
                          <Chip size="small" label={course.category} sx={{ mt: 1, bgcolor: '#16213e', color: '#00d4ff' }} />
                        </Box>
                        <Chip
                          label={progress.status === 'completed' ? 'Completed' : 'In Progress'}
                          color={progress.status === 'completed' ? 'success' : 'warning'}
                        />
                      </Box>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ color: '#b0b0b0' }}>Progress</Typography>
                        <LinearProgress variant="determinate" value={progress.progress_percent} sx={{ height: 8, borderRadius: 4, mt: 1, bgcolor: '#16213e', '& .MuiLinearProgress-bar': { bgcolor: '#00d4ff' } }} />
                        <Typography variant="caption" sx={{ color: '#b0b0b0' }}>{progress.progress_percent}% complete</Typography>
                      </Box>
                      {progress.score && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" sx={{ color: '#b0b0b0' }}>Score: {progress.score}%</Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })
          )}
        </Grid>
      )}

      {/* All Courses Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {courses.map((course) => (
            <Grid key={course.id} size={{ xs: 12, md: 6, lg: 4 }}>
              <Card sx={{ borderRadius: 2, height: '100%', bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Typography variant="h6">{getCategoryIcon(course.category)}</Typography>
                    <Typography variant="subtitle1" fontWeight="bold" sx={{ color: '#ffffff' }}>{course.title}</Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#b0b0b0', mb: 2 }}>
                    {course.description || `${course.duration_hours} hours • ${course.difficulty}`}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip size="small" label={course.category} sx={{ bgcolor: '#16213e', color: '#00d4ff' }} />
                    <Chip size="small" label={course.difficulty} sx={{ bgcolor: getDifficultyColor(course.difficulty), color: 'white' }} />
                    <Chip size="small" label={`${course.duration_hours}h`} variant="outlined" sx={{ color: '#b0b0b0', borderColor: '#b0b0b0' }} />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                    <Typography variant="caption" sx={{ color: '#b0b0b0' }}>
                      {course.enrolled_users} enrolled • {course.completion_rate}% completed
                    </Typography>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<PlayIcon />}
                      onClick={() => startCourse(course.id)}
                      sx={{ bgcolor: '#00d4ff', color: '#0e1c2d' }}
                    >
                      Start
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Simulations Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          {simulations.map((sim) => (
            <Grid key={sim.id} size={{ xs: 12, md: 6 }}>
              <Card sx={{ borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <AssignmentIcon sx={{ fontSize: 40, color: '#00d4ff' }} />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" sx={{ color: '#ffffff' }}>{sim.name}</Typography>
                      <Typography variant="body2" sx={{ color: '#b0b0b0' }}>{sim.type} • {sim.duration_minutes || 15} min</Typography>
                    </Box>
                    <Button variant="outlined" size="small" sx={{ color: '#00d4ff', borderColor: '#00d4ff' }}>Launch</Button>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                    <Typography variant="caption" sx={{ color: '#b0b0b0' }}>Completions: {sim.completions}</Typography>
                    <Typography variant="caption" sx={{ color: '#b0b0b0' }}>Avg Score: {sim.avg_score}%</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Certifications Tab */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          {certifications.length === 0 ? (
            <Grid size={{ xs: 12 }}>
              <Card sx={{ p: 6, textAlign: 'center', borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
                <TrophyIcon sx={{ fontSize: 64, color: '#b0b0b0' }} />
                <Typography variant="h6" sx={{ mt: 2, color: '#ffffff' }}>No certifications yet</Typography>
                <Typography variant="body2" sx={{ color: '#b0b0b0' }}>Complete courses to earn certifications</Typography>
              </Card>
            </Grid>
          ) : (
            certifications.map((cert, idx) => (
              <Grid key={idx} size={{ xs: 12, md: 6 }}>
                <Card sx={{ borderRadius: 2, bgcolor: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <TrophyIcon sx={{ fontSize: 40, color: '#ffd93d' }} />
                      <Box>
                        <Typography variant="h6" sx={{ color: '#ffffff' }}>{cert.course_title}</Typography>
                        <Typography variant="caption" sx={{ color: '#b0b0b0' }}>Issued: {new Date(cert.issued_date).toLocaleDateString()}</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                      <Chip label={`Score: ${cert.score}%`} color="success" size="small" />
                      <Button size="small" variant="outlined" sx={{ color: '#00d4ff', borderColor: '#00d4ff' }}>Download Certificate</Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}
    </Box>
  );
};

export default AITrainerBot;
