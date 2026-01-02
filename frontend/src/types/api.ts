export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone: string;
  iin: string;
  organization: string;
  position: string;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  date_joined: string;
  last_login: string;
}

export interface UserProfile {
  id: number;
  user: User;
  avatar: string;
  address: string;
  city: string;
  region: string;
  postal_code: string;
  additional_info: Record<string, any>;
}

export interface Application {
  id: number;
  number: string;
  applicant: User;
  source: string;
  application_type: string;
  status: string;
  subject: string;
  description: string;
  amount: number;
  creditor_name: string;
  contract_number: string;
  assigned_to: User | null;
  deadline: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  metadata: Record<string, any>;
  tags: string;
  priority: number;
}

export interface ApplicationStats {
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  this_month: number;
  completed_this_month: number;
}

export interface ApplicationHistory {
  id: number;
  application: Application;
  user: User;
  action: string;
  old_status: string;
  new_status: string;
  comment: string;
  created_at: string;
}

export interface ApplicationComment {
  id: number;
  application: Application;
  author: User;
  content: string;
  is_internal: boolean;
  created_at: string;
  updated_at: string;
}

export interface DocumentTemplate {
  id: number;
  name: string;
  code: string;
  description: string;
  template_file: string;
  document_type: string;
  application_types: string[];
  required_fields: string[];
  is_active: boolean;
}

export interface GeneratedDocument {
  id: number;
  template: DocumentTemplate;
  application: Application;
  created_by: User;
  original_file: string;
  signed_file: string | null;
  document_data: Record<string, any>;
  field_values: Record<string, any>;
  signature_type: string;
  signature_status: string;
  signed_at: string | null;
  signed_by: User | null;
  status: string;
  version: number;
  sent_at: string | null;
  sent_to: string[];
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: number;
  recipient: User;
  template: any;
  notification_type: string;
  channel: string;
  title: string;
  message: string;
  data: Record<string, any>;
  status: string;
  attempts: number;
  max_attempts: number;
  scheduled_at: string | null;
  sent_at: string | null;
  delivered_at: string | null;
  read_at: string | null;
  related_application: Application | null;
  related_document: GeneratedDocument | null;
  created_at: string;
  updated_at: string;
}

export interface ChatRoom {
  id: number;
  name: string;
  application: Application;
  participants: User[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  room: ChatRoom;
  author: User;
  content: string;
  message_type: string;
  file: string | null;
  is_read: boolean;
  read_by: User[];
  created_at: string;
  updated_at: string;
}

export interface AIConversation {
  id: number;
  user: User;
  application: Application | null;
  session_id: string;
  context: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AIMessage {
  id: number;
  conversation: AIConversation;
  role: 'user' | 'assistant' | 'system';
  content: string;
  intent: any;
  parameters: Record<string, any>;
  tokens_used: number | null;
  processing_time: number | null;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface APIError {
  detail: string;
  code?: string;
}