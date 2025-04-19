import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  Container,
  TextField,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { resumeService } from '../services/api';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [fetchingResumes, setFetchingResumes] = useState(false);

  // Получение списка загруженных резюме при загрузке страницы
  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    setFetchingResumes(true);
    try {
      const response = await resumeService.getAll();
      setResumes(response.data);
    } catch (err) {
      console.error('Ошибка при получении списка резюме:', err);
      setError('Не удалось загрузить список резюме');
    } finally {
      setFetchingResumes(false);
    }
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Автоматически устанавливаем имя файла как заголовок, если поле пустое
      if (!title) {
        setTitle(selectedFile.name.split('.')[0]);
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!file) {
      setError('Пожалуйста, выберите файл резюме');
      return;
    }
  
    if (!title) {
      setError('Пожалуйста, укажите название для резюме');
      return;
    }
  
    setLoading(true);
    setError(null);
    setSuccess(null);
  
    // Определяем тип файла на основе его расширения
    const fileExtension = file.name.split('.').pop().toLowerCase();
    let fileType;
    
    switch (fileExtension) {
      case 'pdf':
        fileType = 'pdf';
        break;
      case 'doc':
        fileType = 'doc';
        break;
      case 'docx':
        fileType = 'docx';
        break;
      default:
        fileType = 'unknown';
    }
  
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('file_type', fileType); // Добавляем обязательное поле file_type
  
    try {
      const response = await resumeService.create(formData);
  
      setSuccess('Резюме успешно загружено и отправлено на анализ!');
      setFile(null);
      setTitle('');
      fetchResumes();
      
      // Через 2 секунды перенаправляем на страницу анализа
      setTimeout(() => {
        navigate(`/resumes/${response.data.id}`);
      }, 2000);
      
    } catch (err) {
      console.error('Ошибка при загрузке резюме:', err);
      if (err.response && err.response.data) {
        console.log('Детали ошибки:', err.response.data);
        if (typeof err.response.data === 'object') {
          const errorMessages = Object.entries(err.response.data)
            .map(([key, value]) => `${key}: ${value}`)
            .join('; ');
          setError(errorMessages || 'Произошла ошибка при загрузке файла');
        } else {
          setError(err.response.data || 'Произошла ошибка при загрузке файла');
        }
      } else {
        setError('Произошла ошибка при загрузке файла');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusLabel = (status) => {
    switch(status) {
      case 'pending': return 'В обработке';
      case 'processing': return 'Анализ...';
      case 'completed': return 'Завершено';
      case 'failed': return 'Ошибка';
      default: return 'Неизвестно';
    }
  };

  const handleViewAnalysis = (resumeId) => {
    navigate(`/resumes/${resumeId}`);
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ pt: 4, pb: 6 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Панель управления
        </Typography>
        <Typography variant="subtitle1" gutterBottom>
          Загрузите резюме для анализа
        </Typography>

        <Paper sx={{ p: 3, mt: 3 }}>
          <form onSubmit={handleSubmit}>
            <Box sx={{ mb: 2 }}>
              <TextField
                label="Название резюме"
                variant="outlined"
                fullWidth
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                margin="normal"
                required
              />
            </Box>
            
            <Box 
              sx={{ 
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                mb: 2,
                cursor: 'pointer' 
              }}
              onClick={() => document.getElementById('resume-file').click()}
            >
              <input
                type="file"
                id="resume-file"
                style={{ display: 'none' }}
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx"
              />
              <CloudUploadIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              <Typography variant="body1" sx={{ mt: 1 }}>
                {file ? `Выбран файл: ${file.name}` : 'Нажмите для выбора файла резюме'}
              </Typography>
              <Typography variant="caption" display="block" color="text.secondary">
                Поддерживаемые форматы: PDF, DOC, DOCX
              </Typography>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

            <Button 
              variant="contained" 
              color="primary" 
              type="submit" 
              disabled={loading || !file}
              fullWidth
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {loading ? 'Загрузка...' : 'Загрузить и проанализировать'}
            </Button>
          </form>
        </Paper>

        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Мои резюме
          </Typography>

          {fetchingResumes ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress />
            </Box>
          ) : resumes.length > 0 ? (
            <List>
              {resumes.map((resume, index) => (
                <React.Fragment key={resume.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemText 
                      primary={resume.title} 
                      secondary={`Статус: ${getStatusLabel(resume.status)} | Дата: ${new Date(resume.created_at).toLocaleDateString()}`}
                    />
                    <Button 
                      color="primary" 
                      size="small" 
                      variant="outlined"
                      onClick={() => handleViewAnalysis(resume.id)}
                    >
                      {resume.status === 'completed' ? 'Просмотреть анализ' : 'Подробнее'}
                    </Button>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
              У вас пока нет загруженных резюме
            </Typography>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default DashboardPage;