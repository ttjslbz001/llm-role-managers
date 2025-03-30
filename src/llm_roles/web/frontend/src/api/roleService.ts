import apiClient from './apiClient';
import { 
  ApiResponse, 
  RoleCreate, 
  RoleDetail, 
  RoleList, 
  RoleUpdate, 
  SearchResult,
  PromptGenerateRequest,
  PromptPreviewRequest,
  PromptResult,
  RoleDefaultTemplates
} from '../types/api';

// Role Management
export const createRole = async (role: RoleCreate): Promise<ApiResponse<RoleDetail>> => {
  const response = await apiClient.post<ApiResponse<RoleDetail>>('/roles', role);
  return response.data;
};

export const getRoles = async (limit = 100, offset = 0): Promise<ApiResponse<RoleList>> => {
  const response = await apiClient.get<ApiResponse<RoleList>>('/roles', {
    params: { limit, offset }
  });
  return response.data;
};

export const getRole = async (id: string): Promise<ApiResponse<RoleDetail>> => {
  const response = await apiClient.get<ApiResponse<RoleDetail>>(`/roles/${id}`);
  return response.data;
};

export const updateRole = async (id: string, role: RoleUpdate): Promise<ApiResponse<RoleDetail>> => {
  const response = await apiClient.put<ApiResponse<RoleDetail>>(`/roles/${id}`, role);
  return response.data;
};

export const deleteRole = async (id: string): Promise<ApiResponse> => {
  const response = await apiClient.delete<ApiResponse>(`/roles/${id}`);
  return response.data;
};

export const searchRoles = async (query: string): Promise<ApiResponse<SearchResult>> => {
  const response = await apiClient.get<ApiResponse<SearchResult>>('/search-roles', {
    params: { query }
  });
  return response.data;
};

// Role Prompt Management
export const getRolePrompt = async (
  roleId: string, 
  format?: string, 
  type?: string, 
  templateId?: string
): Promise<ApiResponse<PromptResult>> => {
  const response = await apiClient.get<ApiResponse<PromptResult>>(`/roles/${roleId}/prompt`, {
    params: { format, type, template_id: templateId }
  });
  return response.data;
};

export const generateRolePrompt = async (
  roleId: string, 
  request: PromptGenerateRequest
): Promise<ApiResponse<PromptResult>> => {
  const response = await apiClient.post<ApiResponse<PromptResult>>(
    `/roles/${roleId}/prompt`, 
    request
  );
  return response.data;
};

export const previewRolePrompt = async (
  roleId: string, 
  request: PromptPreviewRequest
): Promise<ApiResponse<PromptResult>> => {
  const response = await apiClient.post<ApiResponse<PromptResult>>(
    `/roles/${roleId}/preview-prompt`, 
    request
  );
  return response.data;
};

// Role Default Templates
export const getRoleDefaultTemplates = async (
  roleId: string
): Promise<ApiResponse<RoleDefaultTemplates>> => {
  const response = await apiClient.get<ApiResponse<RoleDefaultTemplates>>(
    `/roles/${roleId}/default-templates`
  );
  return response.data;
};

export const setRoleDefaultTemplate = async (
  roleId: string,
  templateId: string
): Promise<ApiResponse> => {
  const response = await apiClient.post<ApiResponse>(
    `/roles/${roleId}/default-templates/${templateId}`
  );
  return response.data;
};

export const removeRoleDefaultTemplate = async (
  roleId: string,
  templateId: string
): Promise<ApiResponse> => {
  const response = await apiClient.delete<ApiResponse>(
    `/roles/${roleId}/default-templates/${templateId}`
  );
  return response.data;
}; 