import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Breadcrumbs,
  Link
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';
import { resumeService } from '../../services/api';
import ResumeAnalysisView from '../../components/ResumeAnalysisView';

const ResumeAnalysisPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reanalyzing, setReanalyzing] = useState(false);

  useEffect(() => {
    const fetchResume = async () => {
      try {
        setLoading(true);
        const response = await resumeService.get(id);
        setResume(response.data);
      } catch (err) {
        console.error('Error fetching resume:', err);
        setError('Не удалось загрузить данные резюме');
      } finally {
        setLoading(false);
      }
    };

    fetchResume();
  }, [id]);

  const handleReanalyze = async () => {
    try {
      setReanalyzing(true);
      await resumeService.analyze(id);
      // Обновляем данные резюме после запуска реанализа
      const response = await resumeService.get(id);
      setResume(response.data);
      setReanalyzing(false);
    } catch (err) {
      console.error('Error reanalyzing resume:', err);
      setError('Не удалось запустить повторный анализ');
      setReanalyzing(false);
    }
  };

  const handleDownload = () => {
    window.open(`/api/resumes/resumes/${id}/download/`, '_blank');
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/dashboard')}
        >
          Вернуться на главную
        </Button>
      </Container>
    );
  }

  if (!resume) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="warning">
          Резюме не найдено
        </Alert>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/dashboard')}
          sx={{ mt: 2 }}
        >
          Вернуться на главную
        </Button>
      </Container>
    );
  }

  const isPending = resume.status === 'pending' || resume.status === 'processing';

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Breadcrumbs aria-label="breadcrumb">
          <Link color="inherit" onClick={() => navigate('/dashboard')} sx={{ cursor: 'pointer' }}>
            Главная
          </Link>
          <Link color="inherit" onClick={() => navigate('/resumes')} sx={{ cursor: 'pointer' }}>
            Мои резюме
          </Link>
          <Typography color="text.primary">{resume.title}</Typography>
        </Breadcrumbs>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            {resume.title}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Создано: {new Date(resume.created_at).toLocaleString()}
          </Typography>
          {resume.analyzed_at && (
            <Typography variant="subtitle1" color="text.secondary">
              Проанализировано: {new Date(resume.analyzed_at).toLocaleString()}
            </Typography>
          )}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/resumes')}
          >
            Назад
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
          >
            Скачать файл
          </Button>
          
          <Button
            variant="contained"
            startIcon={reanalyzing ? <CircularProgress size={20} /> : <RefreshIcon />}
            disabled={reanalyzing || isPending}
            onClick={handleReanalyze}
          >
            {reanalyzing ? 'Анализ...' : 'Повторный анализ'}
          </Button>
        </Box>
      </Box>

      {isPending ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <CircularProgress size={60} sx={{ mb: 3 }} />
          <Typography variant="h6" gutterBottom>
            Идет анализ резюме...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Этот процесс может занять до нескольких минут. Пожалуйста, подождите или вернитесь позже.
          </Typography>
        </Paper>
      ) : resume.status === 'failed' ? (
        <Paper sx={{ p: 4 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            Произошла ошибка при анализе резюме
          </Alert>
          <Typography variant="body1">
            К сожалению, не удалось выполнить анализ вашего резюме. Возможные причины:
          </Typography>
          <ul>
            <li>Проблемы с извлечением текста из файла</li>
            <li>Неподдерживаемый формат документа</li>
            <li>Временная техническая неполадка</li>
          </ul>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Вы можете попробовать запустить анализ повторно или загрузить резюме в другом формате.
          </Typography>
        </Paper>
      ) : !resume.mongodb_id ? (
        <Paper sx={{ p: 4 }}>
          <Alert severity="warning">
            Результаты анализа недоступны
          </Alert>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Запустите анализ, чтобы получить результаты.
          </Typography>
        </Paper>
      ) : (
        <ResumeAnalysisView resumeId={id} />
      )}
    </Container>
  );
};

export default ResumeAnalysisPage;