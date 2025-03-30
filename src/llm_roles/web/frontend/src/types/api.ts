// API Response types
export interface ApiResponse<T = any> {
  status: number;
  message: string;
  success: boolean;
  data?: T;
}

export interface ErrorResponse {
  status: number;
  message: string;
  success: false;
  data?: any;
}

// Role types
export interface RoleBase {
  name: string;
  description?: string;
  role_type?: string;
  language_style?: string;
  knowledge_domains?: string[];
  response_mode?: string;
  allowed_topics?: string[];
  forbidden_topics?: string[];
}

export interface RoleCreate extends RoleBase {}

export interface RoleUpdate extends Partial<RoleBase> {}

export interface RoleDetail extends RoleBase {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface RoleList {
  roles: RoleDetail[];
  count: number;
  limit: number;
  offset: number;
}

export interface SearchResult {
  roles: RoleDetail[];
  count: number;
  query: string;
}

// Template types
export interface TemplateVariable {
  name: string;
  source: string;
}

export interface TemplateBase {
  name: string;
  description?: string;
  format?: string;
  role_types?: string[];
  template_content: string;
  variables?: TemplateVariable[];
  is_default?: boolean;
}

export interface TemplateCreate extends TemplateBase {}

export interface TemplateUpdate extends Partial<TemplateBase> {}

export interface TemplateDetail extends TemplateBase {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateList {
  templates: TemplateDetail[];
  count: number;
  limit: number;
  offset: number;
}

export interface RoleDefaultTemplates {
  templates: TemplateDetail[];
  count: number;
  role_id: string;
}

// Prompt types
export interface PromptGenerateRequest {
  format?: string;
  type?: string;
  template_id?: string;
  custom_variables?: Record<string, any>;
}

export interface PromptPreviewRequest {
  template_id: string;
  format?: string;
  type?: string;
  custom_variables?: Record<string, any>;
}

export interface PromptResult {
  role_id: string;
  role_name: string;
  prompt: string;
  template_id: string;
  template_name: string;
  format: string;
  type: string;
}

// System types
export interface HealthCheckResponse {
  status: string;
  message: string;
} 