import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Avatar, Menu, MenuItem, IconButton } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useState } from 'react';

const Header = () => {
  const { user, isAuthenticated, logout, isEmployer, isJobseeker, isAdmin } = useAuth();
  const navigate = useNavigate();
  
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  
  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogout = async () => {
    await logout();
    navigate('/');
  };
  
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={RouterLink} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'white' }}>
          AI Resume Analyzer
        </Typography>
        
        {isAuthenticated ? (
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {isJobseeker && (
                <>
                  <Button color="inherit" component={RouterLink} to="/resumes">
                    Мои Резюме
                  </Button>
                  <Button color="inherit" component={RouterLink} to="/jobs">
                    Вакансии
                  </Button>
                </>
              )}
              
              {isEmployer && (
                <>
                  <Button color="inherit" component={RouterLink} to="/companies">
                    Мои Компании
                  </Button>
                  <Button color="inherit" component={RouterLink} to="/jobs/manage">
                    Управление Вакансиями
                  </Button>
                </>
              )}
              
              {isAdmin && (
                <Button color="inherit" component={RouterLink} to="/admin-dashboard">
                  Админ-панель
                </Button>
              )}
              
              <IconButton onClick={handleMenuClick}>
                <Avatar 
                  alt={user?.first_name || user?.email} 
                  src={user?.profile_picture || "/static/images/avatar.jpg"}
                />
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleMenuClose}
              >
                <MenuItem 
                  component={RouterLink} 
                  to="/profile" 
                  onClick={handleMenuClose}
                >
                  Мой профиль
                </MenuItem>
                {isJobseeker && (
                  <MenuItem 
                    component={RouterLink} 
                    to="/analysis" 
                    onClick={handleMenuClose}
                  >
                    История анализа
                  </MenuItem>
                )}
                <MenuItem onClick={handleLogout}>Выйти</MenuItem>
              </Menu>
            </Box>
          </>
        ) : (
          <>
            <Button color="inherit" component={RouterLink} to="/login">
              Войти
            </Button>
            <Button color="inherit" component={RouterLink} to="/register">
              Регистрация
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;