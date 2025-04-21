import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Container,
  Button,
  CircularProgress, 
  Alert,
  Chip,
  Divider,
  Grid
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import WorkIcon from '@mui/icons-material/Work';
import BusinessIcon from '@mui/icons-material/Business';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

import { jobService } from '../../services/api';

const JobDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log(`Загрузка информации о вакансии с идентификатором: ${id}`);
        
        try {
          const response = await jobService.get(id);
          console.log('Получен ответ от сервера:', response.data);
          setJob(response.data);
        } catch (error) {
          console.error('Полная ошибка запроса:', error);
          console.error('Детали ошибки:', error.response ? error.response.data : 'Нет данных ответа');
          setError(`Не удалось загрузить информацию о вакансии: ${error.response?.data?.detail || error.message}`);
        }
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchJobDetails();
    }
  }, [id]);

  const handleBack = () => {
    navigate(-1); // Возвращаемся назад в истории браузера
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ pt: 4, display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ pt: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button variant="outlined" onClick={handleBack}>
            Вернуться назад
          </Button>
        </Box>
      </Container>
    );
  }
  
  if (!job) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ pt: 4 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            Вакансия не найдена
          </Alert>
          <Button variant="outlined" onClick={handleBack}>
            Вернуться назад
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ pt: 4, pb: 6 }}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Button variant="outlined" onClick={handleBack} sx={{ mr: 1 }}>
              Назад
            </Button>
            <Typography variant="h4" component="h1" display="inline">
              {job.title}
            </Typography>
          </Box>
        </Box>

        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <BusinessIcon sx={{ mr: 1 }} />
            <Typography variant="h6">
              {job.company?.name || 'Avatariya'}
            </Typography>
          </Box>
          
          <Divider sx={{ mb: 2 }} />
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            {job.location && (
              <Grid item xs={12} sm={6} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LocationOnIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    {job.location}
                  </Typography>
                </Box>
              </Grid>
            )}
            
            {job.job_type && (
              <Grid item xs={12} sm={6} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <WorkIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    {job.job_type}
                  </Typography>
                </Box>
              </Grid>
            )}
            
            {job.salary_min && job.salary_max && (
              <Grid item xs={12} sm={6} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <AttachMoneyIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    {job.salary_min} - {job.salary_max} {job.salary_currency || 'руб.'}
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
          
          <Typography variant="h6" gutterBottom>
            Описание
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, whiteSpace: 'pre-line' }}>
            {job.description || 'Описание отсутствует'}
          </Typography>
          
          {job.required_skills && job.required_skills.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Требуемые навыки
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.8 }}>
                {job.required_skills.map((skill, index) => (
                  <Chip 
                    key={index}
                    label={typeof skill === 'string' ? skill : skill.name}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </Paper>
        
        {job.requirements && (
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Требования
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
              {job.requirements}
            </Typography>
          </Paper>
        )}
        
        {job.benefits && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Преимущества
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
              {job.benefits}
            </Typography>
          </Paper>
        )}
      </Box>
    </Container>
  );
};

export default JobDetailPage;