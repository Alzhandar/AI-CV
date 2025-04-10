import React from 'react';
import { Typography, Box, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <Box sx={{ textAlign: 'center', mt: 8 }}>
      <Typography variant="h1" gutterBottom>
        404
      </Typography>
      <Typography variant="h4" gutterBottom>
        Страница не найдена
      </Typography>
      <Typography variant="body1" sx={{ mb: 4 }}>
        Запрашиваемая страница не существует или была перемещена.
      </Typography>
      <Button variant="contained" component={RouterLink} to="/">
        Вернуться на главную
      </Button>
    </Box>
  );
};

export default NotFoundPage;