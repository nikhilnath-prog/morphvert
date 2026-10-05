import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');
const REQUEST_TIMEOUT_MS = 120000;

export class ApiError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = options.status;
    this.code = options.code;
    this.details = options.details;
    this.kind = options.kind || 'unknown';
  }
}

const api = axios.create({      
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    Accept: 'application/json',
  },
});

const buildApiError = (error) => {
  if (!axios.isAxiosError(error)) {
    return new ApiError(error instanceof Error ? error.message : 'Unexpected API error');
  }

  if (error.code === 'ECONNABORTED') {
    return new ApiError('Request timed out. Please try again.', {
      kind: 'timeout',
      code: error.code,
    });
  }

  if (!error.response) {
    return new ApiError(`Cannot reach Morphvert API at ${API_BASE_URL}. Start the backend and verify frontend/.env.local (VITE_API_URL).`, {
      kind: 'network',
      code: error.code,
    });
  }

  const status = error.response.status;
  const payload = error.response.data;
  const detail = payload?.detail ?? payload?.message ?? payload?.error;
  const message = Array.isArray(detail) ? detail.join(', ') : detail || error.message || 'Request failed';

  return new ApiError(message, {
    kind: status >= 500 ? 'server' : status === 422 ? 'validation' : 'http',
    status,
    code: error.code,
    details: payload,
  });
};

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(buildApiError(error)),
);

const createSingleFileFormData = (fieldName, file) => {
  const formData = new FormData();
  formData.append(fieldName, file);
  return formData;
};

const createMultipleFilesFormData = (fieldName, files) => {
  const formData = new FormData();
  files.forEach((file) => formData.append(fieldName, file));
  return formData;
};

const createUploadOptions = (onProgress) => ({
  onUploadProgress: (progressEvent) => {
    if (!onProgress || !progressEvent.total) {
      return;
    }

    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
    onProgress(percentCompleted);
  },
});

const normalizeHistoryItem = (item) => ({
  id: item.id,
  toolId: item.conversion_type,
  toolName: item.conversion_type
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase()),
  status: item.status,
  date: item.completed_at || item.created_at,
  originalName: item.input_filename || 'Unknown file',
  resultFileId: item.output_file_id || '',
  resultName: item.output_filename || item.input_filename || 'Converted file',
  resultSize: 0,
});

const normalizeFileResult = (data, fallbackFileId) => ({
  resultFileId: data.output_file_id || fallbackFileId,
  resultFilename: data.output_filename || data.filename || 'converted_file',
  resultSize: data.compressed_size_bytes || data.file_size || data.size || 0,
  downloadUrl: resolveDownloadUrl(data.download_url || (data.output_file_id ? `/api/v1/download/${data.output_file_id}` : undefined)),
});

const resolveDownloadUrl = (downloadUrl) => {
  if (!downloadUrl) {
    return undefined;
  }

  if (downloadUrl.startsWith('http://') || downloadUrl.startsWith('https://')) {
    return downloadUrl;
  }

  return `${API_BASE_URL}${downloadUrl.startsWith('/') ? downloadUrl : `/${downloadUrl}`}`;
};

const normalizeMultiFileResult = (data) => {
  const items = [];

  if (Array.isArray(data.output_files)) {
    data.output_files.forEach((item) => {
      items.push({
        fileId: item.file_id,
        filename: item.filename,
        downloadUrl: resolveDownloadUrl(item.download_url),
        pageNumber: item.page_number,
      });
    });
  }

  if (Array.isArray(data.download_urls) && Array.isArray(data.output_filenames)) {
    data.download_urls.forEach((downloadUrl, index) => {
      items.push({
        fileId: Array.isArray(data.output_file_ids) ? data.output_file_ids[index] : undefined,
        filename: data.output_filenames[index] || `page_${index + 1}.png`,
        downloadUrl: resolveDownloadUrl(downloadUrl),
        pageNumber: index + 1,
      });
    });
  }

  return items;
};

const uploadFile = async (file, onProgress) => {
  const response = await api.post('/api/v1/files/upload', createSingleFileFormData('file', file), {
    ...createUploadOptions(onProgress),
  });

  return response.data;
};

const convertToDocx = async (file) => {
  const response = await api.post('/api/v1/convert/pdf/to-docx', createSingleFileFormData('file', file));
  return {
    ...normalizeFileResult(response.data),
    raw: response.data,
  };
};

const pdfToExcel = async (file) => {
  const response = await api.post('/api/v1/convert/pdf/to-excel', createSingleFileFormData('file', file));
  return {
    ...normalizeFileResult(response.data),
    raw: response.data,
  };
};

const excelToPdf = async (file) => {
  const response = await api.post('/api/v1/convert/excel/to-pdf', createSingleFileFormData('file', file));
  return {
    ...normalizeFileResult(response.data),
    raw: response.data,
  };
};

const convertToImages = async (file) => {
  const response = await api.post('/api/v1/convert/pdf/to-images', createSingleFileFormData('file', file));
  return {
    items: normalizeMultiFileResult(response.data),
    raw: response.data,
  };
};

const mergePdf = async (files) => {
  const response = await api.post('/api/v1/pdf/merge', createMultipleFilesFormData('files', files));
  return {
    ...normalizeFileResult(response.data),
    raw: response.data,
  };
};

const splitPdf = async (file, pages) => {
  const formData = createSingleFileFormData('file', file);
  if (pages) {
    formData.append('pages', pages);
  }

  const response = await api.post('/api/v1/pdf/split', formData);
  return {
    items: normalizeMultiFileResult(response.data),
    raw: response.data,
  };
};

const imageToPdf = async (files) => {
  const response = await api.post(
    '/api/v1/convert/image/to-pdf',
    createMultipleFilesFormData('file', files)
  );

  return {
    ...normalizeFileResult(response.data),
    raw: response.data,
  };
};

const compressPdf = async (file, level) => {
  const formData = createSingleFileFormData('file', file);
  if (level) {
    formData.append('level', level);
  }

  const response = await api.post('/api/v1/pdf/compress', formData);
  return {
    ...normalizeFileResult(response.data),
    raw: response.data,
  };
};

const summarizePdf = async (file, mode = 'all') => {
  const formData = createSingleFileFormData('file', file);
  formData.append('mode', mode);
  const response = await api.post('/api/v1/ai/pdf/summarize', formData);
  return response.data;
};

const getPdfInfo = async (file) => {
  const response = await api.post('/api/v1/pdf/info', createSingleFileFormData('file', file));
  return response.data;
};

const organizePdf = async (file, order, rotations, deletePages) => {
  const formData = createSingleFileFormData('file', file);
  formData.append('order', JSON.stringify(order));
  formData.append('rotations', JSON.stringify(rotations));
  formData.append('delete_pages', JSON.stringify(deletePages));
  const response = await api.post('/api/v1/pdf/organize', formData, { responseType: 'blob' });
  return response.data;
};

const getHistory = async () => {
  const response = await api.get('/api/v1/conversions/history');
  return Array.isArray(response.data) ? response.data.map(normalizeHistoryItem) : [];
};

const getDownloadUrl = (fileId) => `${API_BASE_URL}/api/v1/download/${fileId}`;

const getApiErrorMessage = (error, fallbackMessage = 'Something went wrong while contacting the API.') => {
  if (!error) {
    return fallbackMessage;
  }

  if (error instanceof ApiError) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return error?.message || fallbackMessage;
};

export const fileService = {
  uploadFile,
  convertToDocx,
  pdfToExcel,
  excelToPdf,
  convertToImages,
  mergePdf,
  splitPdf,
  imageToPdf,
  compressPdf,
  summarizePdf,
  getPdfInfo,
  organizePdf,
  getHistory,
  getDownloadUrl,
  getApiErrorMessage,
};

export { api };