import { useState, useEffect } from 'react';
import { CheckCircle2, AlertCircle, RefreshCw, Download, FileCheck, Share2 } from 'lucide-react';
import { formatBytes } from '../utils/helpers';
import { fileService } from '../services/api.js';
import ProgressBar from './ProgressBar';
import DownloadButton from './DownloadButton';

interface ConversionStatusProps {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
  uploadProgress: number;
  conversionProgress: number;
  resultFilename?: string;
  resultSize?: number;
  resultFileId?: string;
  resultFiles?: Array<{
    fileId?: string;
    filename: string;
    downloadUrl: string;
    size?: number;
    pageNumber?: number;
  }>;
  errorMessage?: string;
  onReset: () => void;
  originalFileName?: string;
  toolName: string;
}

export default function ConversionStatus({
  status,
  uploadProgress,
  conversionProgress,
  resultFilename,
  resultSize,
  resultFileId,
  resultFiles,
  errorMessage,
  onReset,
  originalFileName,
  toolName,
}: ConversionStatusProps) {
  const [copied, setCopied] = useState(false);

  // Auto scroll to status or focus on it
  useEffect(() => {
    const el = document.getElementById('conversion-status-box');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [status]);

  if (status === 'idle') return null;

  const copyUrlToClipboard = () => {
    if (!resultFileId) return;
    const downloadUrl = fileService.getDownloadUrl(resultFileId);
    navigator.clipboard.writeText(downloadUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <div
      id="conversion-status-box"
      className="p-6 sm:p-8 bg-white border border-slate-200 rounded-3xl shadow-sm animate-in fade-in zoom-in-95 duration-300"
    >
      <div className="max-w-md mx-auto text-center space-y-6">
        
        {/* State 1: Uploading */}
        {status === 'uploading' && (
          <div className="space-y-4">
            <div className="w-14 h-14 bg-blue-50 border border-blue-105 text-[#2563EB] rounded-2xl flex items-center justify-center mx-auto animate-pulse">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-semibold text-[#1E293B]">Uploading file to server</h3>
              <p className="text-xs text-slate-500 truncate max-w-sm mx-auto">
                Uploading "{originalFileName}" for {toolName}...
              </p>
            </div>
            <ProgressBar progress={uploadProgress} label="Uploading..." />
          </div>
        )}

        {/* State 2: Processing */}
        {status === 'processing' && (
          <div className="space-y-4">
            <div className="w-14 h-14 bg-gradient-to-tr from-[#2563EB] to-[#3B82F6] text-white rounded-2xl flex items-center justify-center mx-auto shadow-sm relative overflow-hidden">
              <div className="absolute inset-0 bg-white/20 animate-pulse" />
              <RefreshCw className="w-6 h-6 animate-spin relative z-10" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-semibold text-[#1E293B]">Transforming your file</h3>
              <p className="text-xs text-slate-500">
                Running Morphvert file engine optimization algorithms...
              </p>
            </div>
            <ProgressBar progress={conversionProgress} label="Converting..." />
          </div>
        )}

        {/* State 3: Completed */}
        {status === 'completed' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="w-16 h-16 bg-emerald-50 border border-emerald-100 text-[#10B981] rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-bold text-[#1E293B] tracking-tight">Conversion Complete!</h3>
              <p className="text-xs text-slate-500">
                Your file has been successfully transformed and optimized.
              </p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-left flex items-center justify-between space-x-3.5">
              <div className="flex items-center space-x-3 overflow-hidden">
                <div className="w-10 h-10 bg-white border border-slate-200 rounded-xl flex items-center justify-center text-blue-600 shrink-0 shadow-sm">
                  <FileCheck className="w-5 h-5" />
                </div>
                <div className="overflow-hidden">
                  <p className="text-xs font-semibold text-[#1E293B] truncate max-w-[200px] sm:max-w-[220px]">
                    {resultFilename}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-0.5 font-mono">
                    {resultSize ? formatBytes(resultSize) : 'Size optimized'}
                  </p>
                </div>
              </div>

              {resultFileId ? (
                <DownloadButton
                  fileId={resultFileId}
                  filename={resultFilename || 'converted_file'}
                  className="p-2 bg-[#2563EB] hover:bg-blue-700 text-white rounded-lg transition-all shrink-0 cursor-pointer hover:shadow-md"
                  iconOnly
                  title="Download file"
                />
              ) : null}
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2">
              {resultFileId ? (
                <DownloadButton
                  fileId={resultFileId}
                  filename={resultFilename || 'converted_file'}
                  className="w-full py-3 px-4 bg-[#2563EB] hover:bg-blue-700 text-white font-semibold text-sm rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-sm active:scale-98"
                >
                  <Download className="w-4 h-4" />
                  <span>Download File</span>
                </DownloadButton>
              ) : null}

              <button
                onClick={copyUrlToClipboard}
                className={`w-full py-3 px-4 border font-semibold text-sm rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer active:scale-98 ${
                  copied
                    ? 'border-emerald-200 bg-emerald-50 text-[#10B981]'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50 bg-white text-slate-500'
                }`}
              >
                {copied ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Share2 className="w-4 h-4" />
                    <span>Copy Link</span>
                  </>
                )}
              </button>
            </div>

            {resultFiles && resultFiles.length > 0 && (
              <div className="pt-2 space-y-2 text-left">
                <p className="text-[10px] uppercase tracking-wider font-mono text-slate-400 font-semibold">Generated Files</p>
                <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                  {resultFiles.map((file, index) => (
                    <div key={`${file.downloadUrl}-${index}`} className="p-3 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-[#1E293B] truncate" title={file.filename}>
                          {file.filename}
                        </p>
                        <p className="text-[10px] text-slate-400 mt-0.5">
                          {file.pageNumber ? `Page ${file.pageNumber}` : 'Generated output'}
                          {file.size ? ` · ${formatBytes(file.size)}` : ''}
                        </p>
                      </div>
                      <a
                        href={file.downloadUrl}
                        download={file.filename}
                        className="inline-flex items-center justify-center px-3 py-2 rounded-lg bg-white border border-slate-200 text-xs font-semibold text-[#1E293B] hover:border-blue-200 hover:text-blue-700 transition-colors"
                      >
                        Download
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-2">
              <button
                onClick={onReset}
                className="text-xs font-medium text-slate-400 hover:text-blue-600 transition-colors cursor-pointer inline-flex items-center space-x-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Convert another file</span>
              </button>
            </div>
          </div>
        )}

        {/* State 4: Failed */}
        {status === 'failed' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2">
            <div className="w-14 h-14 bg-red-50 border border-red-100 text-red-500 rounded-2xl flex items-center justify-center mx-auto">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-semibold text-[#1E293B]">Conversion Failed</h3>
              <p className="text-xs text-red-650 max-w-sm mx-auto leading-relaxed">
                {errorMessage || 'An error occurred during file optimization processing.'}
              </p>
            </div>
            <div className="pt-4">
              <button
                onClick={onReset}
                className="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm rounded-xl transition-all cursor-pointer shadow-sm"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
