import React from 'react';
import { 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Divider, 
  Box,
  Toolbar
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Class as ClassIcon,
  PlaylistAddCheck as TemplateIcon,
  Settings as SettingsIcon,
  Chat as ChatIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const menuItems = [
    {
      text: '仪表盘',
      icon: <DashboardIcon />,
      path: '/',
    },
    {
      text: '角色管理',
      icon: <PersonIcon />,
      path: '/roles',
    },
    {
      text: '提示词模板',
      icon: <TemplateIcon />,
      path: '/templates',
    },
    {
      text: '会话管理',
      icon: <ChatIcon />,
      path: '/sessions',
    },
    {
      text: '角色类型',
      icon: <ClassIcon />,
      path: '/role-types',
    },
    {
      text: '系统设置',
      icon: <SettingsIcon />,
      path: '/settings',
    },
  ];
  
  const handleNavigation = (path: string) => {
    navigate(path);
  };
  
  return (
    <div>
      <Toolbar>
        <Box sx={{ width: '100%', textAlign: 'center' }}>
          <img 
            src="/logo.png" 
            alt="LLM Role Managers" 
            style={{ maxHeight: '40px' }} 
          />
        </Box>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem 
            button 
            key={item.text} 
            onClick={() => handleNavigation(item.path)}
            selected={location.pathname === item.path}
            sx={{
              '&.Mui-selected': {
                backgroundColor: 'primary.light',
                '&:hover': {
                  backgroundColor: 'primary.light',
                },
              },
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </div>
  );
};

export default Sidebar; 