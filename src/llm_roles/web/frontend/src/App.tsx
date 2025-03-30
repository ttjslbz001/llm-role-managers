import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AppLayout from './components/Layout/AppLayout';
import RolesPage from './pages/RolesPage';
import TemplatesPage from './pages/TemplatesPage';
import { AppProvider } from './contexts/AppContext';

// Create a react-query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Create the theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2e7d32', // Green
    },
    secondary: {
      main: '#6a1b9a', // Purple
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppProvider>
          <Router>
            <AppLayout>
              <Routes>
                <Route path="/" element={<RolesPage />} />
                <Route path="/roles" element={<RolesPage />} />
                <Route path="/templates" element={<TemplatesPage />} />
                {/* Add more routes as needed */}
              </Routes>
            </AppLayout>
          </Router>
        </AppProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
