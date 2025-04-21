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
        console.log('Ответ API для подходящих вакансий:', response.data);
        
        // Более гибкая обработка ответа API в зависимости от его структуры
        if (response.data && response.data.jobs) {
          // Если ответ содержит свойство jobs (массив вакансий)
          setMatchingJobs(response.data.jobs);
        } else if (response.data && response.data.results) {
          // Если ответ содержит свойство results (массив вакансий)
          setMatchingJobs(response.data.results);
        } else if (Array.isArray(response.data)) {
          // Если ответ уже является массивом вакансий
          setMatchingJobs(response.data);
        } else {
          // Если ничего из вышеперечисленного не подходит, установим пустой массив
          setMatchingJobs([]);
        }
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

  const handleViewJob = (jobId, jobSlug) => {
    const identifier = jobSlug || jobId;
    navigate(`/jobs/${identifier}`);
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
            <Card key={job.id || index} sx={{ mb: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {job.title}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <BusinessIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
                  {job.company?.name || job.company_name || 'Компания не указана'}
                </Typography>
                
                {job.matching_skills_count !== undefined && (
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
                          label={typeof skill === 'string' ? skill : skill.name}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
                
                {/* Отображение зарплаты, если она указана */}
                {job.salary_min && job.salary_max && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Зарплата: {job.salary_min} - {job.salary_max} {job.salary_currency || 'руб.'}
                  </Typography>
                )}
                
                {/* Отображение местоположения, если оно указано */}
                {job.location && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Местоположение: {job.location}
                  </Typography>
                )}
                
                {/* Отображение типа работы, если он указан */}
                {job.job_type && (
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    Тип: {job.job_type}
                  </Typography>
                )}
              </CardContent>
              <CardActions>
              <Button 
                size="small" 
                onClick={() => handleViewJob(job.id, job.slug)}
              >
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