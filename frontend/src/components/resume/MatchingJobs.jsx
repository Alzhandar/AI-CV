import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Chip, 
  Button,
  CircularProgress, 
  List, 
  ListItem,
  ListItemText,
  Divider,
  Card,
  CardContent,
  CardActions,
  Alert
} from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import WorkIcon from '@mui/icons-material/Work';
import { resumeService } from '../../services/api';
import { useNavigate } from 'react-router-dom';

const MatchingJobs = ({ resumeId }) => {
  const [matchingJobs, setMatchingJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchMatchingJobs = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await resumeService.getMatchingJobs(resumeId);
        setMatchingJobs(response.data.jobs || []);
      } catch (err) {
        console.error('Ошибка при получении подходящих вакансий:', err);
        setError('Не удалось загрузить подходящие вакансии');
      } finally {
        setLoading(false);
      }
    };
    
    if (resumeId) {
      fetchMatchingJobs();
    }
  }, [resumeId]);

  const handleViewJob = (jobId) => {
    navigate(`/jobs/${jobId}`);
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }
  
  if (!matchingJobs || matchingJobs.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          <WorkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Подходящие вакансии
        </Typography>
        <Alert severity="info">
          Для этого резюме не найдено подходящих вакансий
        </Alert>
      </Paper>
    );
  }
  
  return (
    <Box>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          <WorkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Подходящие вакансии ({matchingJobs.length})
        </Typography>
        
        <Box sx={{ mt: 2 }}>
          {matchingJobs.map((job, index) => (
            <Card key={job.id} sx={{ mb: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {job.title}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <BusinessIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
                  {job.company?.name || 'Компания не указана'}
                </Typography>
                
                {job.matching_skills_count && (
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="body2" component="span">
                      Совпадение навыков: 
                    </Typography>
                    <Chip
                      size="small"
                      label={`${job.matching_skills_count} совпадений`}
                      color="success"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                )}
                
                {job.required_skills && job.required_skills.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Требуемые навыки:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {job.required_skills.map((skill, idx) => (
                        <Chip
                          key={idx}
                          label={skill.name}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
                
                {job.salary_min && job.salary_max && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Зарплата: {job.salary_min} - {job.salary_max} {job.salary_currency || 'руб.'}
                  </Typography>
                )}
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => handleViewJob(job.id)}>
                  Подробнее
                </Button>
              </CardActions>
            </Card>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default MatchingJobs;