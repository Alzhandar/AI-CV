import React from 'react';
import { Box, Container, Typography, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box component="footer" sx={{ py: 3, mt: 'auto', backgroundColor: 'primary.main', color: 'white' }}>
      <Container maxWidth="lg">
        <Typography variant="body2" align="center">
          &copy; {new Date().getFullYear()} AI-Powered Resume Analyzer
        </Typography>
        <Typography variant="body2" align="center">
          <Link color="inherit" href="/">
            Главная
          </Link>{' | '}
          <Link color="inherit" href="/about">
            О сервисе
          </Link>{' | '}
          <Link color="inherit" href="/privacy">
            Политика конфиденциальности
          </Link>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;