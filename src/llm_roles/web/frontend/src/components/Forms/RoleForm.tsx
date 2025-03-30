import React, { useState, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Grid, 
  Paper,
  Typography,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  SelectChangeEvent
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { RoleCreate, RoleDetail, RoleUpdate } from '../../types/api';
import { useAppContext } from '../../contexts/AppContext';

interface RoleFormProps {
  role?: RoleDetail;
  onSubmit: (role: RoleCreate | RoleUpdate) => Promise<void>;
  isEdit?: boolean;
}

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

// Dummy data for role types - in a real app, these would come from an API
const roleTypes = ['advisor', 'assistant', 'teacher', 'specialist', 'consultant'];

const RoleForm: React.FC<RoleFormProps> = ({ role, onSubmit, isEdit = false }) => {
  const navigate = useNavigate();
  const { showNotification, setLoading } = useAppContext();
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [roleType, setRoleType] = useState('');
  const [languageStyle, setLanguageStyle] = useState('');
  const [knowledgeDomains, setKnowledgeDomains] = useState<string[]>([]);
  const [responseMode, setResponseMode] = useState('');
  const [allowedTopics, setAllowedTopics] = useState<string[]>([]);
  const [forbiddenTopics, setForbiddenTopics] = useState<string[]>([]);
  
  // For handling tag inputs
  const [domainInput, setDomainInput] = useState('');
  const [allowedTopicInput, setAllowedTopicInput] = useState('');
  const [forbiddenTopicInput, setForbiddenTopicInput] = useState('');
  
  // Load role data if in edit mode
  useEffect(() => {
    if (role) {
      setName(role.name || '');
      setDescription(role.description || '');
      setRoleType(role.role_type || '');
      setLanguageStyle(role.language_style || '');
      setKnowledgeDomains(role.knowledge_domains || []);
      setResponseMode(role.response_mode || '');
      setAllowedTopics(role.allowed_topics || []);
      setForbiddenTopics(role.forbidden_topics || []);
    }
  }, [role]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      const formData: RoleCreate | RoleUpdate = {
        name,
        description,
        role_type: roleType,
        language_style: languageStyle,
        knowledge_domains: knowledgeDomains,
        response_mode: responseMode,
        allowed_topics: allowedTopics,
        forbidden_topics: forbiddenTopics
      };
      
      await onSubmit(formData);
      
      showNotification(
        isEdit ? '角色更新成功' : '角色创建成功', 
        'success'
      );
      
      navigate('/roles');
    } catch (error) {
      showNotification(
        isEdit ? '更新角色时出错' : '创建角色时出错',
        'error'
      );
      console.error('Form submission error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCancel = () => {
    navigate('/roles');
  };
  
  // Handle tag input for knowledge domains
  const handleAddDomain = () => {
    if (domainInput.trim() && !knowledgeDomains.includes(domainInput.trim())) {
      setKnowledgeDomains([...knowledgeDomains, domainInput.trim()]);
      setDomainInput('');
    }
  };
  
  const handleDeleteDomain = (domain: string) => {
    setKnowledgeDomains(knowledgeDomains.filter(d => d !== domain));
  };
  
  // Handle tag input for allowed topics
  const handleAddAllowedTopic = () => {
    if (allowedTopicInput.trim() && !allowedTopics.includes(allowedTopicInput.trim())) {
      setAllowedTopics([...allowedTopics, allowedTopicInput.trim()]);
      setAllowedTopicInput('');
    }
  };
  
  const handleDeleteAllowedTopic = (topic: string) => {
    setAllowedTopics(allowedTopics.filter(t => t !== topic));
  };
  
  // Handle tag input for forbidden topics
  const handleAddForbiddenTopic = () => {
    if (forbiddenTopicInput.trim() && !forbiddenTopics.includes(forbiddenTopicInput.trim())) {
      setForbiddenTopics([...forbiddenTopics, forbiddenTopicInput.trim()]);
      setForbiddenTopicInput('');
    }
  };
  
  const handleDeleteForbiddenTopic = (topic: string) => {
    setForbiddenTopics(forbiddenTopics.filter(t => t !== topic));
  };
  
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" component="h2" gutterBottom>
        {isEdit ? '编辑角色' : '创建新角色'}
      </Typography>
      
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              基本信息
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              label="角色名称"
              value={name}
              onChange={(e) => setName(e.target.value)}
              helperText="给角色起一个描述性的名称"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel id="role-type-label">角色类型</InputLabel>
              <Select
                labelId="role-type-label"
                value={roleType}
                onChange={(e) => setRoleType(e.target.value)}
                label="角色类型"
              >
                {roleTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="角色描述"
              multiline
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              helperText="详细描述角色的目的和功能"
            />
          </Grid>
          
          {/* Behavior Characteristics */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              行为特征
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="语言风格"
              value={languageStyle}
              onChange={(e) => setLanguageStyle(e.target.value)}
              helperText="如专业、友好、技术性等"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="响应模式"
              value={responseMode}
              onChange={(e) => setResponseMode(e.target.value)}
              helperText="如详细、简洁等"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ mb: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                知识领域
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {knowledgeDomains.map((domain) => (
                  <Chip
                    key={domain}
                    label={domain}
                    onDelete={() => handleDeleteDomain(domain)}
                    color="primary"
                    variant="outlined"
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                label="添加知识领域"
                variant="outlined"
                size="small"
                value={domainInput}
                onChange={(e) => setDomainInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddDomain();
                  }
                }}
              />
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleAddDomain}
                size="small"
              >
                添加
              </Button>
            </Box>
          </Grid>
          
          {/* Constraints */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              约束条件
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                允许讨论的主题
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {allowedTopics.map((topic) => (
                  <Chip
                    key={topic}
                    label={topic}
                    onDelete={() => handleDeleteAllowedTopic(topic)}
                    color="success"
                    variant="outlined"
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                label="添加允许主题"
                variant="outlined"
                size="small"
                value={allowedTopicInput}
                onChange={(e) => setAllowedTopicInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddAllowedTopic();
                  }
                }}
              />
              <Button 
                variant="contained" 
                color="success"
                onClick={handleAddAllowedTopic}
                size="small"
              >
                添加
              </Button>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                禁止的主题或行为
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {forbiddenTopics.map((topic) => (
                  <Chip
                    key={topic}
                    label={topic}
                    onDelete={() => handleDeleteForbiddenTopic(topic)}
                    color="error"
                    variant="outlined"
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                label="添加禁止主题"
                variant="outlined"
                size="small"
                value={forbiddenTopicInput}
                onChange={(e) => setForbiddenTopicInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddForbiddenTopic();
                  }
                }}
              />
              <Button 
                variant="contained" 
                color="error"
                onClick={handleAddForbiddenTopic}
                size="small"
              >
                添加
              </Button>
            </Box>
          </Grid>
          
          {/* Form Actions */}
          <Grid item xs={12} sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button onClick={handleCancel} variant="outlined">
              取消
            </Button>
            <Button type="submit" variant="contained" color="primary">
              {isEdit ? '更新角色' : '创建角色'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default RoleForm; 