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
  DialogTitle
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  Edit as EditIcon,
  Search as SearchIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { getRoles, deleteRole, searchRoles } from '../api/roleService';
import { RoleDetail } from '../types/api';

const RolesPage: React.FC = () => {
  const navigate = useNavigate();
  const { showNotification, setLoading } = useAppContext();
  
  const [roles, setRoles] = useState<RoleDetail[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [roleToDelete, setRoleToDelete] = useState<RoleDetail | null>(null);
  
  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await getRoles(rowsPerPage, page * rowsPerPage);
      
      if (response.success) {
        setRoles(response.data?.roles || []);
        setTotalCount(response.data?.count || 0);
      } else {
        showNotification(response.message || '获取角色列表失败', 'error');
      }
    } catch (error) {
      showNotification('获取角色列表失败', 'error');
      console.error('Error fetching roles:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchRoles();
      return;
    }
    
    try {
      setLoading(true);
      const response = await searchRoles(searchQuery);
      
      if (response.success) {
        setRoles(response.data?.roles || []);
        setTotalCount(response.data?.count || 0);
      } else {
        showNotification(response.message || '搜索角色失败', 'error');
      }
    } catch (error) {
      showNotification('搜索角色失败', 'error');
      console.error('Error searching roles:', error);
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
  
  const handleDeleteClick = (role: RoleDetail) => {
    setRoleToDelete(role);
    setDeleteDialogOpen(true);
  };
  
  const handleDeleteConfirm = async () => {
    if (!roleToDelete) return;
    
    try {
      setLoading(true);
      const response = await deleteRole(roleToDelete.id);
      
      if (response.success) {
        showNotification(`角色 "${roleToDelete.name}" 已删除`, 'success');
        fetchRoles();
      } else {
        showNotification(response.message || '删除角色失败', 'error');
      }
    } catch (error) {
      showNotification('删除角色失败', 'error');
      console.error('Error deleting role:', error);
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
      setRoleToDelete(null);
    }
  };
  
  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setRoleToDelete(null);
  };
  
  const handleCreateRole = () => {
    navigate('/roles/create');
  };
  
  const handleEditRole = (id: string) => {
    navigate(`/roles/edit/${id}`);
  };
  
  const handleViewRole = (id: string) => {
    navigate(`/roles/view/${id}`);
  };
  
  // Initial fetch
  useEffect(() => {
    fetchRoles();
  }, [page, rowsPerPage]);
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          角色管理
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={handleCreateRole}
        >
          创建角色
        </Button>
      </Box>
      
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Box sx={{ p: 2 }}>
          <TextField
            fullWidth
            placeholder="搜索角色..."
            variant="outlined"
            size="small"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
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
          />
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>名称</TableCell>
                <TableCell>描述</TableCell>
                <TableCell>角色类型</TableCell>
                <TableCell>知识领域</TableCell>
                <TableCell>创建时间</TableCell>
                <TableCell>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {roles.length > 0 ? (
                roles.map((role) => (
                  <TableRow key={role.id}>
                    <TableCell>{role.name}</TableCell>
                    <TableCell>{role.description}</TableCell>
                    <TableCell>{role.role_type}</TableCell>
                    <TableCell>
                      {role.knowledge_domains?.map((domain) => (
                        <Chip 
                          key={domain} 
                          label={domain} 
                          size="small" 
                          sx={{ mr: 0.5, mb: 0.5 }} 
                        />
                      ))}
                    </TableCell>
                    <TableCell>
                      {new Date(role.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <IconButton 
                        color="primary" 
                        onClick={() => handleViewRole(role.id)}
                        size="small"
                      >
                        <ViewIcon />
                      </IconButton>
                      <IconButton 
                        color="primary" 
                        onClick={() => handleEditRole(role.id)}
                        size="small"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        onClick={() => handleDeleteClick(role)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    {searchQuery ? '没有找到匹配的角色' : '没有角色数据'}
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
          确认删除角色
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            您确定要删除角色 "{roleToDelete?.name}" 吗？此操作无法撤销。
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

export default RolesPage; 