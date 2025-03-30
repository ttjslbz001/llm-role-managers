import React, { createContext, useContext, useState, ReactNode } from 'react';
import { RoleDetail, TemplateDetail } from '../types/api';

interface AppContextType {
  // Notifications
  notification: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'info' | 'warning';
  };
  showNotification: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
  hideNotification: () => void;
  
  // Active role and template
  activeRole: RoleDetail | null;
  setActiveRole: (role: RoleDetail | null) => void;
  activeTemplate: TemplateDetail | null;
  setActiveTemplate: (template: TemplateDetail | null) => void;
  
  // Loading state
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Notification state
  const [notification, setNotification] = useState({
    show: false,
    message: '',
    type: 'info' as 'success' | 'error' | 'info' | 'warning',
  });
  
  // Active elements
  const [activeRole, setActiveRole] = useState<RoleDetail | null>(null);
  const [activeTemplate, setActiveTemplate] = useState<TemplateDetail | null>(null);
  
  // Loading state
  const [loading, setLoading] = useState(false);
  
  const showNotification = (
    message: string, 
    type: 'success' | 'error' | 'info' | 'warning' = 'info'
  ) => {
    setNotification({
      show: true,
      message,
      type,
    });
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      hideNotification();
    }, 5000);
  };
  
  const hideNotification = () => {
    setNotification((prev) => ({
      ...prev,
      show: false,
    }));
  };
  
  const value = {
    notification,
    showNotification,
    hideNotification,
    activeRole,
    setActiveRole,
    activeTemplate,
    setActiveTemplate,
    loading,
    setLoading,
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}; 