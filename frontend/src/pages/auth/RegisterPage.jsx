import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { 
  TextField, Button, Typography, Paper, Box, Alert, Link,
  FormControl, InputLabel, Select, MenuItem, FormHelperText 
} from '@mui/material';
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
    .min(8, 'Пароль должен быть не менее 8 символов')
    .required('Пароль обязателен'),
  confirmPassword: yup
    .string('Подтвердите пароль')
    .oneOf([yup.ref('password'), null], 'Пароли должны совпадать')
    .required('Подтверждение пароля обязательно'),
  first_name: yup
    .string('Введите имя')
    .required('Имя обязательно'),
  last_name: yup
    .string('Введите фамилию')
    .required('Фамилия обязательна'),
  role: yup
    .string('Выберите роль')
    .oneOf(['jobseeker', 'employer'], 'Выберите корректную роль')
    .required('Роль обязательна'),
});

const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
      confirmPassword: '',
      first_name: '',
      last_name: '',
      role: 'jobseeker',
    },
    validationSchema: validationSchema,
    onSubmit: async (values) => {
      try {
        const { confirmPassword, ...userData } = values;
        await register(userData);
        navigate('/login', { state: { message: 'Регистрация успешна. Теперь вы можете войти.' } });
      } catch (err) {
        setError(err.response?.data?.error || 'Ошибка регистрации. Пожалуйста, попробуйте еще раз.');
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
      <Paper elevation={3} sx={{ p: 4, width: '100%', maxWidth: 600 }}>
        <Typography component="h1" variant="h5" align="center" gutterBottom>
          Регистрация
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <form onSubmit={formik.handleSubmit}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              id="first_name"
              name="first_name"
              label="Имя"
              value={formik.values.first_name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.first_name && Boolean(formik.errors.first_name)}
              helperText={formik.touched.first_name && formik.errors.first_name}
              margin="normal"
            />
            <TextField
              fullWidth
              id="last_name"
              name="last_name"
              label="Фамилия"
              value={formik.values.last_name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.last_name && Boolean(formik.errors.last_name)}
              helperText={formik.touched.last_name && formik.errors.last_name}
              margin="normal"
            />
          </Box>
          
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
          
          <FormControl 
            fullWidth 
            margin="normal"
            error={formik.touched.role && Boolean(formik.errors.role)}
          >
            <InputLabel id="role-label">Роль</InputLabel>
            <Select
              labelId="role-label"
              id="role"
              name="role"
              value={formik.values.role}
              label="Роль"
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
            >
              <MenuItem value="jobseeker">Соискатель</MenuItem>
              <MenuItem value="employer">Работодатель</MenuItem>
            </Select>
            {formik.touched.role && formik.errors.role && (
              <FormHelperText>{formik.errors.role}</FormHelperText>
            )}
          </FormControl>
          
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
          
          <TextField
            fullWidth
            id="confirmPassword"
            name="confirmPassword"
            label="Подтвердите пароль"
            type="password"
            value={formik.values.confirmPassword}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.confirmPassword && Boolean(formik.errors.confirmPassword)}
            helperText={formik.touched.confirmPassword && formik.errors.confirmPassword}
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
            {formik.isSubmitting ? 'Регистрация...' : 'Зарегистрироваться'}
          </Button>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link component={RouterLink} to="/login" variant="body2">
              Уже есть аккаунт? Войти
            </Link>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default RegisterPage;