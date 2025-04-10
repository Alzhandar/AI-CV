import React from 'react';
import { Typography, Button, Container, Grid, Paper, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const { isAuthenticated, isJobseeker, isEmployer } = useAuth();

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 8 }}>
        <Typography
          component="h1"
          variant="h2"
          align="center"
          color="text.primary"
          gutterBottom
        >
          AI-Powered Resume Analyzer
        </Typography>
        <Typography variant="h5" align="center" color="text.secondary" paragraph>
          Оптимизируйте свое резюме с помощью искусственного интеллекта. 
          Получите детальный анализ навыков, форматирования и совместимости с вакансиями.
        </Typography>
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          {!isAuthenticated ? (
            <>
              <Button variant="contained" color="primary" component={RouterLink} to="/register" sx={{ mx: 1 }}>
                Регистрация
              </Button>
              <Button variant="outlined" color="primary" component={RouterLink} to="/login" sx={{ mx: 1 }}>
                Войти
              </Button>
            </>
          ) : (
            <Button variant="contained" color="primary" component={RouterLink} to="/dashboard" sx={{ mx: 1 }}>
              Перейти в кабинет
            </Button>
          )}
        </Box>
      </Box>
      
      <Grid container spacing={4} sx={{ mt: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              height: '100%',
            }}
          >
            <Typography variant="h5" component="h2" gutterBottom>
              Анализ резюме
            </Typography>
            <Typography paragraph>
              Загрузите свое резюме в формате PDF или DOCX и получите подробный анализ 
              содержания, структуры и стиля с рекомендациями по улучшению.
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              height: '100%',
            }}
          >
            <Typography variant="h5" component="h2" gutterBottom>
              Сопоставление с вакансиями
            </Typography>
            <Typography paragraph>
              Найдите идеальные вакансии на основе ваших навыков или проверьте 
              совместимость вашего резюме с конкретной вакансией.
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              height: '100%',
            }}
          >
            <Typography variant="h5" component="h2" gutterBottom>
              Для работодателей
            </Typography>
            <Typography paragraph>
              Размещайте вакансии и получайте доступ к базе соискателей 
              с проанализированными и оптимизированными резюме.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HomePage;