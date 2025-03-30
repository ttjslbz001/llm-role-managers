import apiClient from './apiClient';
import { 
  ApiResponse, 
  TemplateCreate, 
  TemplateDetail, 
  TemplateList, 
  TemplateUpdate 
} from '../types/api';

// Template Management
export const createTemplate = async (template: TemplateCreate): Promise<ApiResponse<TemplateDetail>> => {
  const response = await apiClient.post<ApiResponse<TemplateDetail>>('/prompt-templates', template);
  return response.data;
};

export const getTemplates = async (
  includeDefaults = true, 
  limit = 100, 
  offset = 0
): Promise<ApiResponse<TemplateList>> => {
  const response = await apiClient.get<ApiResponse<TemplateList>>('/prompt-templates', {
    params: { include_defaults: includeDefaults, limit, offset }
  });
  return response.data;
};

export const getTemplate = async (id: string): Promise<ApiResponse<TemplateDetail>> => {
  const response = await apiClient.get<ApiResponse<TemplateDetail>>(`/prompt-templates/${id}`);
  return response.data;
};

export const updateTemplate = async (
  id: string, 
  template: TemplateUpdate
): Promise<ApiResponse<TemplateDetail>> => {
  const response = await apiClient.put<ApiResponse<TemplateDetail>>(
    `/prompt-templates/${id}`, 
    template
  );
  return response.data;
};

export const deleteTemplate = async (id: string): Promise<ApiResponse> => {
  const response = await apiClient.delete<ApiResponse>(`/prompt-templates/${id}`);
  return response.data;
}; 