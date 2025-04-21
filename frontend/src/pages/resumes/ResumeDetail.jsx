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
  Grid,
  LinearProgress
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import RefreshIcon from '@mui/icons-material/Refresh';
import DescriptionIcon from '@mui/icons-material/Description';

import { resumeService } from '../../services/api';
import ResumeAnalysis from '../../components/resume/ResumeAnalysis';
import MatchingJobs from '../../components/resume/MatchingJobs';

const ResumeDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reanalysisLoading, setReanalysisLoading] = useState(false);
  const [reanalysisSuccess, setReanalysisSuccess] = useState(false);

  useEffect(() => {
    const fetchResumeDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await resumeService.get(id);
        setResume(response.data);
      } catch (err) {
        console.error('Ошибка при получении информации о резюме:', err);
        setError('Не удалось загрузить информацию о резюме');
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchResumeDetails();
    }
  }, [id]);

  const handleReanalyze = async () => {
    try {
      setReanalysisLoading(true);
      setReanalysisSuccess(false);
      
      await resumeService.analyze(id);
      
      setReanalysisSuccess(true);
      
      // Обновляем данные резюме после запуска повторного анализа
      const response = await resumeService.get(id);
      setResume(response.data);
      
      // Через 3 секунды скрываем сообщение об успехе
      setTimeout(() => {
        setReanalysisSuccess(false);
      }, 3000);
      
    } catch (err) {
      console.error('Ошибка при запуске повторного анализа:', err);
      setError('Не удалось запустить повторный анализ резюме');
    } finally {
      setReanalysisLoading(false);
    }
  };

  const handleDownload = () => {
    window.open(`/api/resumes/resumes/${id}/download/`, '_blank');
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  const getStatusInfo = (status) => {
    switch(status) {
      case 'pending':
        return { 
          label: 'В очереди на обработку', 
          color: 'warning',
          progress: true,
          progressValue: 10
        };
      case 'processing':
        return { 
          label: 'Анализ...', 
          color: 'info',
          progress: true,
          progressValue: 50
        };
      case 'completed':
        return { 
          label: 'Анализ завершен', 
          color: 'success',
          progress: false
        };
      case 'failed':
        return { 
          label: 'Ошибка анализа', 
          color: 'error',
          progress: false
        };
      default:
        return { 
          label: 'Неизвестный статус', 
          color: 'default',
          progress: false
        };
    }
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
  
  if (!resume) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ pt: 4 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            Резюме не найдено
          </Alert>
          <Button variant="outlined" onClick={handleBack}>
            Вернуться назад
          </Button>
        </Box>
      </Container>
    );
  }

  const statusInfo = getStatusInfo(resume.status);
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ pt: 4, pb: 6 }}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Button variant="outlined" onClick={handleBack} sx={{ mr: 1 }}>
              Назад
            </Button>
            <Typography variant="h4" component="h1" display="inline">
              {resume.title}
            </Typography>
          </Box>
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<FileDownloadIcon />}
              onClick={handleDownload}
              sx={{ mr: 1 }}
            >
              Скачать файл
            </Button>
            <Button 
              variant="contained" 
              color="primary"
              startIcon={reanalysisLoading ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
              onClick={handleReanalyze}
              disabled={reanalysisLoading || resume.status === 'processing' || resume.status === 'pending'}
            >
              {reanalysisLoading ? 'Запуск...' : 'Повторный анализ'}
            </Button>
          </Box>
        </Box>

        {reanalysisSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Повторный анализ успешно запущен! Пожалуйста, подождите...
          </Alert>
        )}
        
        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Информация о резюме
          </Typography>
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Файл:
              </Typography>
              <Typography variant="body1">
                {resume.file_name || 'Имя файла недоступно'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Дата загрузки:
              </Typography>
              <Typography variant="body1">
                {new Date(resume.created_at).toLocaleString()}
              </Typography>
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Статус:
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Chip 
                label={statusInfo.label} 
                color={statusInfo.color} 
                sx={{ mr: 2 }}
              />
              {statusInfo.progress && (
                <Box sx={{ flexGrow: 1, maxWidth: 200 }}>
                  <LinearProgress 
                    variant="indeterminate" 
                    color={statusInfo.color}
                  />
                </Box>
              )}
            </Box>
          </Box>
          
          {resume.skills && resume.skills.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Навыки:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {resume.skills.map((skill) => (
                  <Chip 
                    key={skill.id} 
                    label={skill.name} 
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </Paper>
        
        {/* Отображаем результаты анализа только если анализ завершен */}
        {resume.status === 'completed' && (
          <>
            {/* Компонент с результатами анализа */}
            <ResumeAnalysis resumeId={id} />
            
            {/* Компонент с подходящими вакансиями */}
            <MatchingJobs resumeId={id} />
          </>
        )}
        
        {(resume.status === 'pending' || resume.status === 'processing') && (
          <Alert severity="info" icon={<CircularProgress size={20} />} sx={{ mb: 2 }}>
            Анализ резюме в процессе. Пожалуйста, подождите. Эта страница автоматически обновится после завершения анализа.
          </Alert>
        )}
        
        {resume.status === 'failed' && (
          <Alert severity="error" sx={{ mb: 2 }}>
            При анализе резюме произошла ошибка. Пожалуйста, попробуйте запустить анализ повторно.
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default ResumeDetailPage;