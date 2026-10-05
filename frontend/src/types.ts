export type ToolID =
  | 'pdf-to-docx'
  | 'pdf-to-excel'
  | 'pdf-to-images'
  | 'excel-to-pdf'
  | 'merge-pdf'
  | 'split-pdf'
  | 'image-to-pdf'
  | 'compress-pdf'
  | 'ai-pdf-summarizer'
  | 'organize-pdf';

export interface ToolDefinition {
  id: ToolID;
  name: string;
  description: string;
  shortDescription: string;
  category: 'convert' | 'optimize' | 'organize' | 'ai';
  iconName: string;
  accepts: string;
  multiple: boolean;
  maxSizeMB: number;
}

export interface UploadedFile {
  fileId: string;
  filename: string;
  size: number;
  mimetype: string;
  uploadedAt: string;
  previewUrl?: string;
}

export interface ConversionResult {
  id: string;
  toolId: ToolID;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  originalFiles: UploadedFile[];
  resultFileId?: string;
  resultFilename?: string;
  resultSize?: number;
  errorMessage?: string;
  createdAt: string;
}

export interface ResultFileItem {
  fileId?: string;
  filename: string;
  downloadUrl: string;
  size?: number;
  pageNumber?: number;
}

export interface HistoryItem {
  id: string;
  toolId: ToolID;
  toolName: string;
  status: 'completed' | 'failed';
  date: string;
  originalName: string;
  resultFileId: string;
  resultName: string;
  resultSize: number;
}
