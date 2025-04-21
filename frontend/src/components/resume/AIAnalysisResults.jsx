import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  Divider,
  Alert,
  Chip
} from '@mui/material';
import LoopIcon from '@mui/icons-material/Loop';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import LightbulbIcon from '@mui/icons-material/Lightbulb';

const AIAnalysisResults = ({ results }) => {
  if (!results) {
    return (
      <Alert severity="info">
        Результаты AI анализа недоступны
      </Alert>
    );
  }

  // Функция для определения цвета качества формата
  const getFormatQualityColor = (quality) => {
    switch(quality) {
      case 'good': return 'success';
      case 'average': return 'warning';
      case 'needs_improvement': return 'error';
      default: return 'default';
    }
  };

  const getFormatQualityLabel = (quality) => {
    switch(quality) {
      case 'good': return 'Хороший';
      case 'average': return 'Средний';
      case 'needs_improvement': return 'Требует улучшения';
      default: return 'Не определено';
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <SmartToyIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h5">
          Результаты AI анализа
        </Typography>
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Общая оценка: {results.overall_score}/10
        </Typography>
        
        <Typography variant="body2" sx={{ mb: 2 }}>
          Качество оформления: 
          <Chip 
            label={getFormatQualityLabel(results.format_quality)} 
            color={getFormatQualityColor(results.format_quality)}
            size="small"
            sx={{ ml: 1 }}
          />
        </Typography>
      </Box>

      {results.skills_found && results.skills_found.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Обнаруженные навыки:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {results.skills_found.map((skill, index) => (
              <Chip
                key={index}
                label={skill}
                size="small"
                variant="outlined"
                color="primary"
              />
            ))}
          </Box>
        </Box>
      )}

      {results.structure_analysis && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Анализ структуры резюме:
          </Typography>
          <List dense>
            {Object.entries(results.structure_analysis).map(([key, value]) => {
              let label = '';
              switch(key) {
                case 'has_contact_info': label = 'Контактная информация'; break;
                case 'has_professional_summary': label = 'Профессиональное резюме'; break;
                case 'has_work_experience': label = 'Опыт работы'; break;
                case 'has_education': label = 'Образование'; break;
                case 'has_skills_section': label = 'Раздел навыков'; break;
                default: label = key;
              }
              
              return (
                <ListItem key={key}>
                  <ListItemIcon>
                    {value ? 
                      <CheckCircleIcon color="success" /> : 
                      <ErrorIcon color="error" />
                    }
                  </ListItemIcon>
                  <ListItemText 
                    primary={label} 
                    secondary={value ? 'Присутствует' : 'Отсутствует'}
                  />
                </ListItem>
              );
            })}
          </List>
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {results.improvement_suggestions && results.improvement_suggestions.length > 0 && (
        <Box>
          <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <LightbulbIcon sx={{ mr: 1, color: 'warning.main' }} />
            Рекомендации по улучшению:
          </Typography>
          <List dense>
            {results.improvement_suggestions.map((suggestion, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <WarningIcon color="warning" />
                </ListItemIcon>
                <ListItemText primary={suggestion} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Дополнительные данные для сопоставления с вакансией (если они есть) */}
      {results.job_match_percentage !== undefined && (
        <Box sx={{ mt: 3 }}>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="subtitle1" gutterBottom>
            Соответствие требуемой должности: {results.job_match_percentage}%
          </Typography>
          
          {results.matching_skills && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Совпадающие навыки:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {results.matching_skills.map((skill, index) => (
                  <Chip
                    key={index}
                    label={skill}
                    size="small"
                    color="success"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
          
          {results.missing_skills && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Отсутствующие навыки:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {results.missing_skills.map((skill, index) => (
                  <Chip
                    key={index}
                    label={skill}
                    size="small"
                    color="error"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
          
          {results.tailoring_suggestions && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Рекомендации по адаптации резюме:
              </Typography>
              <List dense>
                {results.tailoring_suggestions.map((suggestion, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <LightbulbIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText primary={suggestion} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default AIAnalysisResults;