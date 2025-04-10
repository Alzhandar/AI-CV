import React, { useState, useEffect } from 'react';
import { Typography, Grid, Paper, Box, Button, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { resumeService, jobService, analysisService } from '../services/api';

const DashboardPage = () => {
  const { user, isJobseeker, isEmployer } = useAuth();
  const navigate = useNavigate();
  
  const [stats, setStats] = useState({
    resumes: { count: 0, loading: true, error: null },
    jobs: { count: 0, loading: true, error: null },
    analyses: { count: 0, loading: true, error: null },
  });

  useEffect(() => {
    const fetchData = async () => {
      if (isJobseeker) {
        try {
          const resumeResponse = await resumeService.getAll();
          setStats(prev => ({
            ...prev,
            resumes: { count: resumeResponse.data.length, loading: false, error: null }
          }));
        } catch (error) {
          setStats(prev => ({
            ...prev,
            resumes: { ...prev.resumes, loading: false, error: 'Ошибка загрузки данных' }
          }));
        }

        try {
          const analysisResponse = await analysisService.getStatistics();
          setStats(prev => ({
            ...prev,
            analyses: { 
              count: analysisResponse.data.total_analyses, 
              loading: false, 
              error: null,
              data: analysisResponse.data 
            }
          }));
        } catch (error) {
          setStats(prev => ({
            ...prev,
            analyses: { ...prev.analyses, loading: false, error: 'Ошибка загрузки данных' }
          }));
        }

        try {
          const jobsResponse = await jobService.getMatching();
          setStats(prev => ({
            ...prev,
            jobs: { count: jobsResponse.data.length, loading: false, error: null }
          }));
        } catch (error) {
          setStats(prev => ({
            ...prev,
            jobs: { ...prev.jobs, loading: false, error: 'Ошибка загрузки данных' }
          }));
        }
      }
      
      if (isEmployer) {
        try {
          const jobsResponse = await jobService.getAll();
          setStats(prev => ({
            ...prev,
            jobs: { count: jobsResponse.data.length, loading: false, error: null }
          }));
        } catch (error) {
          setStats(prev => ({
            ...prev,
            jobs: { ...prev.jobs, loading: false, error: 'Ошибка загрузки данных' }
          }));
        }
      }
    };

    fetchData();
  }, [isJobseeker, isEmployer]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Добро пожаловать, {user?.first_name || 'пользователь'}!
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {isJobseeker && (
          <>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Мои резюме
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {stats.resumes.loading ? (
                    <CircularProgress size={24} sx={{ mr: 2 }} />
                  ) : (
                    <Typography variant="h3" sx={{ mr: 2 }}>
                      {stats.resumes.count}
                    </Typography>
                  )}
                  <Typography variant="body1">
                    {stats.resumes.loading 
                      ? 'Загрузка...' 
                      : `Загружено ${stats.resumes.count} резюме`}
                  </Typography>
                </Box>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => navigate('/resumes')}
                >
                  Управление резюме
                </Button>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Анализ
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {stats.analyses.loading ? (
                    <CircularProgress size={24} sx={{ mr: 2 }} />
                  ) : (
                    <Typography variant="h3" sx={{ mr: 2 }}>
                      {stats.analyses.count}
                    </Typography>
                  )}
                  <Typography variant="body1">
                    {stats.analyses.loading 
                      ? 'Загрузка...' 
                      : `Проведено ${stats.analyses.count} анализов`}
                  </Typography>
                </Box>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => navigate('/analysis')}
                >
                  Просмотр анализов
                </Button>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Подходящие вакансии
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {stats.jobs.loading ? (
                    <CircularProgress size={24} sx={{ mr: 2 }} />
                  ) : (
                    <Typography variant="h3" sx={{ mr: 2 }}>
                      {stats.jobs.count}
                    </Typography>
                  )}
                  <Typography variant="body1">
                    {stats.jobs.loading 
                      ? 'Загрузка...' 
                      : `Найдено ${stats.jobs.count} подходящих вакансий`}
                  </Typography>
                </Box>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => navigate('/jobs')}
                >
                  Просмотр вакансий
                </Button>
              </Paper>
            </Grid>
          </>
        )}
        
        {isEmployer && (
          <>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Мои вакансии
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {stats.jobs.loading ? (
                    <CircularProgress size={24} sx={{ mr: 2 }} />
                  ) : (
                    <Typography variant="h3" sx={{ mr: 2 }}>
                      {stats.jobs.count}
                    </Typography>
                  )}
                  <Typography variant="body1">
                    {stats.jobs.loading 
                      ? 'Загрузка...' 
                      : `У вас опубликовано ${stats.jobs.count} вакансий`}
                  </Typography>
                </Box>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => navigate('/jobs/manage')}
                  sx={{ mr: 2 }}
                >
                  Управление вакансиями
                </Button>
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => navigate('/jobs/create')}
                >
                  Создать вакансию
                </Button>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Мои компании
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body1">
                    Управляйте данными о компаниях для публикации вакансий
                  </Typography>
                </Box>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => navigate('/companies')}
                  sx={{ mr: 2 }}
                >
                  Управление компаниями
                </Button>
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => navigate('/companies/create')}
                >
                  Создать компанию
                </Button>
              </Paper>
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
};

export default DashboardPage;