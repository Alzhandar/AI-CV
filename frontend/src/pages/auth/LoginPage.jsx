import React, { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import { TextField, Button, Typography, Paper, Box, Alert, Link } from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { useAuth } from '../../context/AuthContext';

const validationSchema = yup.object({
  email: yup
    .string('Введите email')
    .email('Введите корректный email')
    .required('Email обязателен'),
  password: yup
    .string('Введите пароль')
    .required('Пароль обязателен'),
});

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    // Проверяем сообщение из состояния навигации
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
    }
  }, [location]);

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
    },
    validationSchema: validationSchema,
    onSubmit: async (values) => {
      try {
        console.log('Отправляемые данные для входа:', values);
        await login(values);
        navigate('/dashboard');
      } catch (err) {
        console.error('Ошибка входа:', err);
        
        // Улучшенная обработка ошибок
        if (err.response && err.response.data) {
          const errorData = err.response.data;
          if (typeof errorData === 'string') {
            setError(errorData);
          } else if (errorData.error) {
            setError(errorData.error);
          } else if (errorData.detail) {
            setError(errorData.detail);
          } else if (errorData.non_field_errors) {
            setError(Array.isArray(errorData.non_field_errors) 
              ? errorData.non_field_errors.join(', ') 
              : errorData.non_field_errors);
          } else {
            setError('Ошибка входа. Проверьте учетные данные.');
          }
        } else {
          setError('Ошибка соединения с сервером. Пожалуйста, попробуйте позже.');
        }
      }
    },
  });

  return (
    <Box 
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Paper elevation={3} sx={{ p: 4, width: '100%', maxWidth: 400 }}>
        <Typography component="h1" variant="h5" align="center" gutterBottom>
          Вход в систему
        </Typography>
        
        {successMessage && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {successMessage}
          </Alert>
        )}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <form onSubmit={formik.handleSubmit}>
          <TextField
            fullWidth
            id="email"
            name="email"
            label="Email"
            value={formik.values.email}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.email && Boolean(formik.errors.email)}
            helperText={formik.touched.email && formik.errors.email}
            margin="normal"
          />
          <TextField
            fullWidth
            id="password"
            name="password"
            label="Пароль"
            type="password"
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.password && Boolean(formik.errors.password)}
            helperText={formik.touched.password && formik.errors.password}
            margin="normal"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{ mt: 3, mb: 2 }}
            disabled={formik.isSubmitting}
          >
            {formik.isSubmitting ? 'Вход...' : 'Войти'}
          </Button>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link component={RouterLink} to="/register" variant="body2">
              Нет аккаунта? Зарегистрироваться
            </Link>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default LoginPage;