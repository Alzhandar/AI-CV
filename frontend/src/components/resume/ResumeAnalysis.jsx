import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Chip,
  CircularProgress, 
  Divider,
  List,
  ListItem,
  ListItemText,
  Rating,
  Alert,
  Grid
} from '@mui/material';
import SkillsIcon from '@mui/icons-material/Psychology';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { resumeService } from '../../services/api';

// Вспомогательная функция для категоризации навыков
const categorizeSkills = (skills) => {
  if (!skills || !Array.isArray(skills)) return {};
  
  const categories = {
    'technical': { name: 'Технические', skills: [] },
    'soft': { name: 'Гибкие', skills: [] },
    'language': { name: 'Языки', skills: [] },
    'other': { name: 'Прочие', skills: [] }
  };
  
  // Предполагаем, что у нас есть какое-то базовое разделение навыков
  const technicalSkills = ['python', 'java', 'javascript', 'react', 'angular', 'django', 'html', 'css', 'docker'];
  const softSkills = ['коммуникабельность', 'лидерство', 'работа в команде', 'тайм-менеджмент'];
  const languageSkills = ['английский', 'немецкий', 'французский', 'китайский', 'испанский'];
  
  skills.forEach(skill => {
    const skillLower = skill.toLowerCase();
    if (technicalSkills.some(tech => skillLower.includes(tech))) {
      categories.technical.skills.push(skill);
    } else if (softSkills.some(soft => skillLower.includes(soft))) {
      categories.soft.skills.push(skill);
    } else if (languageSkills.some(lang => skillLower.includes(lang))) {
      categories.language.skills.push(skill);
    } else {
      categories.other.skills.push(skill);
    }
  });
  
  return categories;
};

const ResumeAnalysis = ({ resumeId }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await resumeService.getAnalysisResults(resumeId);
        setAnalysisData(response.data);
      } catch (err) {
        console.error('Ошибка при получении результатов анализа:', err);
        setError(
          err.response?.data?.error || 
          'Не удалось загрузить результаты анализа. Возможно, анализ еще не завершен.'
        );
      } finally {
        setLoading(false);
      }
    };
    
    if (resumeId) {
      fetchAnalysis();
    }
  }, [resumeId]);
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }
  
  if (!analysisData || !analysisData.analysis_results) {
    return (
      <Alert severity="info">
        Результаты анализа недоступны.
      </Alert>
    );
  }
  
  const { analysis_results } = analysisData;
  const skillsFound = analysis_results.skills_found || [];
  const skillCategories = categorizeSkills(skillsFound);
  
  return (
    <Box sx={{ mb: 4 }}>
      <Paper elevation={2} sx={{ p: 3, mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          Результаты анализа резюме
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={6}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>
                Общая оценка
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ mr: 2, position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={analysis_results.overall_score || 0}
                    size={80}
                    thickness={4}
                    color={
                      analysis_results.overall_score > 70 ? 'success' :
                      analysis_results.overall_score > 40 ? 'warning' : 'error'
                    }
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h6" component="div">
                      {Math.round(analysis_results.overall_score || 0)}%
                    </Typography>
                  </Box>
                </Box>
                <Box>
                  <Rating
                    value={(analysis_results.overall_score || 0) / 20}
                    precision={0.5}
                    readOnly
                  />
                </Box>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle1" gutterBottom>
                Статистика резюме
              </Typography>
              <List dense disablePadding>
                <ListItem disableGutters>
                  <ListItemText 
                    primary="Количество слов" 
                    secondary={analysis_results.word_count || 'Нет данных'}
                  />
                </ListItem>
                <ListItem disableGutters>
                  <ListItemText 
                    primary="Количество навыков" 
                    secondary={skillsFound.length}
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>

        <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
          <SkillsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Выявленные навыки
        </Typography>
        
        {Object.entries(skillCategories).map(([categoryKey, category]) => (
          category.skills.length > 0 && (
            <Box key={categoryKey} sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {category.name}:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {category.skills.map((skill, index) => (
                  <Chip 
                    key={index}
                    label={skill}
                    color={
                      categoryKey === 'technical' ? 'primary' :
                      categoryKey === 'soft' ? 'secondary' :
                      categoryKey === 'language' ? 'success' : 'default'
                    }
                    variant="outlined"
                    size="small"
                  />
                ))}
              </Box>
            </Box>
          )
        ))}

        {(!skillsFound || skillsFound.length === 0) && (
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Навыки не обнаружены
          </Typography>
        )}

        <Divider sx={{ my: 2 }} />

        <Typography variant="h6" gutterBottom>
          Рекомендации
        </Typography>
        
        {analysis_results.recommendations && analysis_results.recommendations.length > 0 ? (
          <List dense>
            {analysis_results.recommendations.map((recommendation, index) => (
              <ListItem key={index} disableGutters>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                      <ErrorOutlineIcon color="warning" sx={{ mr: 1, fontSize: 20 }} />
                      {recommendation}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography color="text.secondary">
            Нет рекомендаций
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default ResumeAnalysis;