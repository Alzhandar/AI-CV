import React from 'react';
import { 
  Typography, 
  Button, 
  Container, 
  Grid, 
  Paper, 
  Box,
  Stack,
  Divider,
  useTheme
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import WorkIcon from '@mui/icons-material/Work';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter';

// Стилизованные компоненты
const HeroSection = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(8, 2),
  backgroundColor: theme.palette.grey[50],
  borderRadius: theme.shape.borderRadius,
  marginBottom: theme.spacing(6),
  border: `1px solid ${theme.palette.grey[100]}`,
}));

const HeroTitle = styled(Typography)(({ theme }) => ({
  fontWeight: 700,
  marginBottom: theme.spacing(2),
  color: theme.palette.text.primary,
}));

const FeatureCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.grey[100]}`,
}));

const FeatureIconWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 54,
  height: 54,
  borderRadius: '8px',
  backgroundColor: theme.palette.primary.main,
  marginBottom: theme.spacing(2),
  color: theme.palette.common.white,
}));

const HomePage = () => {
  const { isAuthenticated, isJobseeker, isEmployer } = useAuth();
  const theme = useTheme();

  return (
    <>
      <HeroSection>
        <Container maxWidth="md">
          <Box>
            <HeroTitle variant="h2" component="h1">
              AI-Powered Resume Analyzer
            </HeroTitle>
          </Box>
          
          <Box>
            <Typography 
              variant="h5" 
              color="text.secondary" 
              sx={{ 
                mb: 4, 
                maxWidth: '800px', 
                mx: 'auto',
                fontWeight: 400,
                lineHeight: 1.5
              }}
            >
              Оптимизируйте свое резюме с помощью искусственного интеллекта. 
              Получите детальный анализ навыков, форматирования и совместимости с вакансиями.
            </Typography>
          </Box>
          
          <Box>
            <Stack 
              direction={{ xs: 'column', sm: 'row' }} 
              spacing={2} 
              justifyContent="center"
              sx={{ mt: 4 }}
            >
              {!isAuthenticated ? (
                <>
                  <Button 
                    variant="contained" 
                    size="large"
                    component={RouterLink} 
                    to="/register"
                    sx={{ 
                      px: 4, 
                      py: 1.25,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      borderRadius: '8px',
                    }}
                  >
                    Начать бесплатно
                  </Button>
                  <Button 
                    variant="outlined" 
                    size="large"
                    component={RouterLink} 
                    to="/login"
                    sx={{ 
                      px: 4, 
                      py: 1.25,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      borderRadius: '8px'
                    }}
                  >
                    Войти в аккаунт
                  </Button>
                </>
              ) : (
                <Button 
                  variant="contained" 
                  size="large"
                  component={RouterLink} 
                  to="/dashboard"
                  sx={{ 
                    px: 4, 
                    py: 1.25,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    borderRadius: '8px',
                  }}
                >
                  Перейти в личный кабинет
                </Button>
              )}
            </Stack>
          </Box>
        </Container>
      </HeroSection>
      
      <Container maxWidth="lg">
        <Box sx={{ mb: 6 }}>
          <Typography 
            variant="h4" 
            component="h2" 
            align="center" 
            gutterBottom
            sx={{ 
              fontWeight: 700,
              mb: 4,
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: -8,
                left: '50%',
                transform: 'translateX(-50%)',
                width: 50,
                height: 3,
                bgcolor: 'primary.main',
                borderRadius: 1
              }
            }}
          >
            Основные возможности
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box>
                <FeatureCard elevation={0}>
                  <FeatureIconWrapper>
                    <AnalyticsIcon fontSize="medium" />
                  </FeatureIconWrapper>
                  <Typography variant="h5" component="h3" fontWeight={600} gutterBottom>
                    Анализ резюме
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph sx={{ flex: 1 }}>
                    Загрузите свое резюме в формате PDF или DOCX и получите подробный анализ 
                    содержания, структуры и стиля с персонализированными рекомендациями по улучшению.
                  </Typography>
                  {isAuthenticated && (
                    <Button 
                      component={RouterLink} 
                      to="/dashboard" 
                      variant="outlined" 
                      color="primary"
                      sx={{ alignSelf: 'flex-start', mt: 2 }}
                    >
                      Попробовать
                    </Button>
                  )}
                </FeatureCard>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Box>
                <FeatureCard elevation={0}>
                  <FeatureIconWrapper>
                    <WorkIcon fontSize="medium" />
                  </FeatureIconWrapper>
                  <Typography variant="h5" component="h3" fontWeight={600} gutterBottom>
                    Сопоставление с вакансиями
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph sx={{ flex: 1 }}>
                    Найдите идеальные вакансии на основе ваших навыков или проверьте 
                    совместимость вашего резюме с конкретной позицией. Получайте рекомендации 
                    по улучшению соответствия требованиям.
                  </Typography>
                  {isAuthenticated && isJobseeker && (
                    <Button 
                      component={RouterLink} 
                      to="/jobs" 
                      variant="outlined" 
                      color="primary"
                      sx={{ alignSelf: 'flex-start', mt: 2 }}
                    >
                      Найти вакансии
                    </Button>
                  )}
                </FeatureCard>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Box>
                <FeatureCard elevation={0}>
                  <FeatureIconWrapper>
                    <BusinessCenterIcon fontSize="medium" />
                  </FeatureIconWrapper>
                  <Typography variant="h5" component="h3" fontWeight={600} gutterBottom>
                    Для работодателей
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph sx={{ flex: 1 }}>
                    Размещайте вакансии и получайте доступ к базе соискателей 
                    с проанализированными и оптимизированными резюме. Находите 
                    идеальных кандидатов быстрее и эффективнее.
                  </Typography>
                  {isAuthenticated && isEmployer && (
                    <Button 
                      component={RouterLink} 
                      to="/company/dashboard" 
                      variant="outlined" 
                      color="primary"
                      sx={{ alignSelf: 'flex-start', mt: 2 }}
                    >
                      Управление вакансиями
                    </Button>
                  )}
                </FeatureCard>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </>
  );
};

export default HomePage;