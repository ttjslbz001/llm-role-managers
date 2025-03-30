import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TablePagination, 
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Switch,
  FormControlLabel
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  Edit as EditIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { getTemplates, deleteTemplate } from '../api/templateService';
import { TemplateDetail } from '../types/api';

const TemplatesPage: React.FC = () => {
  const navigate = useNavigate();
  const { showNotification, setLoading } = useAppContext();
  
  const [templates, setTemplates] = useState<TemplateDetail[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [includeDefaults, setIncludeDefaults] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState<TemplateDetail | null>(null);
  
  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await getTemplates(includeDefaults, rowsPerPage, page * rowsPerPage);
      
      if (response.success) {
        setTemplates(response.data?.templates || []);
        setTotalCount(response.data?.count || 0);
      } else {
        showNotification(response.message || '获取模板列表失败', 'error');
      }
    } catch (error) {
      showNotification('获取模板列表失败', 'error');
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handlePageChange = (_event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
    setPage(newPage);
  };
  
  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  const handleDeleteClick = (template: TemplateDetail) => {
    setTemplateToDelete(template);
    setDeleteDialogOpen(true);
  };
  
  const handleDeleteConfirm = async () => {
    if (!templateToDelete) return;
    
    try {
      setLoading(true);
      const response = await deleteTemplate(templateToDelete.id);
      
      if (response.success) {
        showNotification(`模板 "${templateToDelete.name}" 已删除`, 'success');
        fetchTemplates();
      } else {
        showNotification(response.message || '删除模板失败', 'error');
      }
    } catch (error) {
      showNotification('删除模板失败', 'error');
      console.error('Error deleting template:', error);
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
      setTemplateToDelete(null);
    }
  };
  
  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setTemplateToDelete(null);
  };
  
  const handleCreateTemplate = () => {
    navigate('/templates/create');
  };
  
  const handleEditTemplate = (id: string) => {
    navigate(`/templates/edit/${id}`);
  };
  
  const handleViewTemplate = (id: string) => {
    navigate(`/templates/view/${id}`);
  };
  
  const handleSearch = () => {
    // Filter templates based on search term
    // This is a client-side search as the API doesn't provide a search endpoint for templates
    if (!searchTerm.trim()) {
      fetchTemplates();
      return;
    }
    
    const term = searchTerm.toLowerCase();
    const filteredTemplates = templates.filter(
      template => 
        template.name.toLowerCase().includes(term) || 
        (template.description && template.description.toLowerCase().includes(term))
    );
    
    setTemplates(filteredTemplates);
    setTotalCount(filteredTemplates.length);
  };
  
  const handleIncludeDefaultsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setIncludeDefaults(event.target.checked);
  };
  
  // Initial fetch and when filters change
  useEffect(() => {
    fetchTemplates();
  }, [page, rowsPerPage, includeDefaults]);
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          提示词模板管理
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={handleCreateTemplate}
        >
          创建模板
        </Button>
      </Box>
      
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
          <TextField
            placeholder="搜索模板..."
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <Button onClick={handleSearch} size="small">
                    搜索
                  </Button>
                </InputAdornment>
              ),
            }}
            sx={{ flexGrow: 1, mr: 2 }}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={includeDefaults}
                onChange={handleIncludeDefaultsChange}
                color="primary"
              />
            }
            label="包含默认模板"
          />
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>名称</TableCell>
                <TableCell>描述</TableCell>
                <TableCell>格式</TableCell>
                <TableCell>适用角色类型</TableCell>
                <TableCell>默认模板</TableCell>
                <TableCell>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {templates.length > 0 ? (
                templates.map((template) => (
                  <TableRow key={template.id}>
                    <TableCell>{template.name}</TableCell>
                    <TableCell>{template.description}</TableCell>
                    <TableCell>{template.format}</TableCell>
                    <TableCell>
                      {template.role_types?.map((type) => (
                        <Chip 
                          key={type} 
                          label={type} 
                          size="small" 
                          sx={{ mr: 0.5, mb: 0.5 }} 
                        />
                      ))}
                    </TableCell>
                    <TableCell>
                      {template.is_default ? '是' : '否'}
                    </TableCell>
                    <TableCell>
                      <IconButton 
                        color="primary" 
                        onClick={() => handleViewTemplate(template.id)}
                        size="small"
                        title="查看模板"
                      >
                        <ViewIcon />
                      </IconButton>
                      <IconButton 
                        color="primary" 
                        onClick={() => handleEditTemplate(template.id)}
                        size="small"
                        title="编辑模板"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        color="info" 
                        onClick={() => navigate(`/templates/${template.id}/preview`)}
                        size="small"
                        title="预览模板"
                      >
                        <CodeIcon />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        onClick={() => handleDeleteClick(template)}
                        size="small"
                        title="删除模板"
                        disabled={template.is_default}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    {searchTerm ? '没有找到匹配的模板' : '没有模板数据'}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
          labelRowsPerPage="每页行数:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}-${to} / ${count !== -1 ? count : '未知'}`
          }
        />
      </Paper>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          确认删除模板
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            您确定要删除模板 "{templateToDelete?.name}" 吗？此操作无法撤销。
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            取消
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            删除
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TemplatesPage; 