import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  Chip,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import { resumeService } from '../services/api';

// Компонент для визуализации процента в виде круга
const CircularProgressWithLabel = (props) => {
  return (
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <CircularProgress variant="determinate" {...props} />
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
        <Typography variant="caption" component="div" color="text.secondary">
          {`${Math.round(props.value)}%`}
        </Typography>
      </Box>
    </Box>
  );
};

const ResumeAnalysisView = ({ resumeId }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        const response = await resumeService.getAnalysisResults(resumeId);
        setAnalysis(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching resume analysis:', err);
        setError('Не удалось загрузить результаты анализа');
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
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!analysis) {
    return (
      <Alert severity="info" sx={{ my: 2 }}>
        Анализ недоступен
      </Alert>
    );
  }

  const { analysis_results } = analysis;
  
  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Общая оценка резюме
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', my: 3 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgressWithLabel 
              value={analysis_results.overall_score || 0} 
              size={100} 
              thickness={4} 
              color={
                analysis_results.overall_score >= 80 ? 'success' :
                analysis_results.overall_score >= 60 ? 'primary' :
                'warning'
              }
            />
            <Typography variant="body1" sx={{ mt: 1 }}>
              Общая оценка
            </Typography>
          </Box>
          
          {analysis_results.analysis_details && (
            <>
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgressWithLabel 
                  value={analysis_results.analysis_details.content_score || 0} 
                  size={80} 
                  thickness={4} 
                  color="info" 
                />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Содержание
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgressWithLabel 
                  value={analysis_results.analysis_details.format_score || 0} 
                  size={80} 
                  thickness={4} 
                  color="secondary" 
                />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Формат
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgressWithLabel 
                  value={analysis_results.analysis_details.completeness_score || 0} 
                  size={80} 
                  thickness={4} 
                  color="success" 
                />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Полнота
                </Typography>
              </Box>
            </>
          )}
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <Box sx={{ mb: 2, minWidth: '200px' }}>
            <Typography variant="subtitle2" color="text.secondary">
              Количество слов
            </Typography>
            <Typography variant="h6">
              {analysis_results.word_count || 'Нет данных'}
            </Typography>
          </Box>
          
          <Box sx={{ mb: 2, minWidth: '200px' }}>
            <Typography variant="subtitle2" color="text.secondary">
              Найдено навыков
            </Typography>
            <Typography variant="h6">
              {analysis_results.skills_found?.length || 0}
            </Typography>
          </Box>
        </Box>
      </Paper>
      
      {/* Секция с найденными навыками */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Найденные навыки
        </Typography>
        
        {analysis_results.skills_found && analysis_results.skills_found.length > 0 ? (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
              {analysis_results.skills_found.map((skill, index) => (
                <Chip
                  key={`skill-${index}`}
                  label={skill.name}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Совпадения навыков в тексте резюме</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {analysis_results.skill_matches && analysis_results.skill_matches.length > 0 ? (
                  <List>
                    {analysis_results.skill_matches.map((match, index) => (
                      <ListItem key={`match-${index}`} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {match.skill_name}
                        </Typography>
                        
                        <List sx={{ width: '100%', pl: 2 }}>
                          {match.matches.map((occurrence, idx) => (
                            <ListItem key={`occurrence-${idx}`} sx={{ border: '1px solid #eee', borderRadius: 1, my: 1 }}>
                              <ListItemText
                                primary={
                                  <>
                                    <span style={{ backgroundColor: '#e3f2fd' }}>
                                      {occurrence.text}
                                    </span>
                                    {occurrence.matched_alias && (
                                      <Chip
                                        label={`Найдено как: ${occurrence.matched_alias}`}
                                        size="small"
                                        color="secondary"
                                        sx={{ ml: 1 }}
                                      />
                                    )}
                                  </>
                                }
                                secondary={occurrence.context}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Подробная информация о совпадениях недоступна
                  </Typography>
                )}
              </AccordionDetails>
            </Accordion>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Навыки не найдены. Рекомендуется добавить в резюме ключевые навыки и технологии, которыми вы владеете.
          </Typography>
        )}
      </Paper>
      
      {/* Секция с рекомендациями */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Рекомендации по улучшению
        </Typography>
        
        {analysis_results.recommendations && analysis_results.recommendations.length > 0 ? (
          <List>
            {analysis_results.recommendations.map((recommendation, index) => (
              <ListItem key={`rec-${index}`}>
                <ListItemText primary={recommendation} />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Рекомендации отсутствуют
          </Typography>
        )}
      </Paper>
      
      {/* Секция со структурой резюме */}
      {analysis_results.structure_analysis && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Анализ структуры резюме
          </Typography>
          
          <List>
            <ListItem>
              <ListItemText 
                primary="Контактная информация" 
                secondary={analysis_results.structure_analysis.has_contact_info ? "Присутствует" : "Отсутствует"} 
              />
              {analysis_results.structure_analysis.has_contact_info ? 
                <CheckIcon color="success" /> : <CloseIcon color="error" />}
            </ListItem>
            
            <ListItem>
              <ListItemText 
                primary="Образование" 
                secondary={analysis_results.structure_analysis.has_education ? "Присутствует" : "Отсутствует"} 
              />
              {analysis_results.structure_analysis.has_education ? 
                <CheckIcon color="success" /> : <CloseIcon color="error" />}
            </ListItem>
            
            <ListItem>
              <ListItemText 
                primary="Опыт работы" 
                secondary={analysis_results.structure_analysis.has_experience ? "Присутствует" : "Отсутствует"} 
              />
              {analysis_results.structure_analysis.has_experience ? 
                <CheckIcon color="success" /> : <CloseIcon color="error" />}
            </ListItem>
            
            <ListItem>
              <ListItemText 
                primary="Навыки" 
                secondary={analysis_results.structure_analysis.has_skills ? "Присутствует" : "Отсутствует"} 
              />
              {analysis_results.structure_analysis.has_skills ? 
                <CheckIcon color="success" /> : <CloseIcon color="error" />}
            </ListItem>
          </List>
        </Paper>
      )}
      
      {/* Секция с извлеченным текстом */}
      <Paper sx={{ p: 3 }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Извлеченный текст резюме</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
              {analysis.extracted_text || "Текст не был извлечен"}
            </Box>
          </AccordionDetails>
        </Accordion>
      </Paper>
    </Box>
  );
};

export default ResumeAnalysisView;