import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const ProfilePage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Профиль пользователя
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Страница в разработке
        </Typography>
      </Paper>
    </Box>
  );
};

export default ProfilePage;