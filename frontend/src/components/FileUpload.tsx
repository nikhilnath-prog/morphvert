import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, File, Trash2, AlertCircle, Plus, Check } from 'lucide-react';
import { formatBytes } from '../utils/helpers';

interface FileUploadProps {
  accept: string;
  multiple: boolean;
  maxSizeMB: number;
  files: File[];
  onFilesChange: (files: File[]) => void;
}

export default function FileUpload({
  accept,
  multiple,
  maxSizeMB,
  files,
  onFilesChange,
}: FileUploadProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate a single file
  const validateFile = (file: File): { valid: boolean; reason?: string } => {
    // 1. Check size
    const sizeInMB = file.size / (1024 * 1024);
    if (sizeInMB > maxSizeMB) {
      return { valid: false, reason: `File size exceeds the ${maxSizeMB}MB limit.` };
    }

    // 2. Check MIME type or extension matching
    if (!accept) return { valid: true };

    const acceptedTypes = accept.split(',').map((t) => t.trim().toLowerCase());
    const fileType = file.type.toLowerCase();
    const fileName = file.name.toLowerCase();

    const matchesType = acceptedTypes.some((type) => {
      if (type.startsWith('.')) {
        // Extension check (e.g., .docx)
        return fileName.endsWith(type);
      } else if (type.endsWith('/*')) {
        // Wildcard check (e.g., image/*)
        const category = type.slice(0, -2);
        return fileType.startsWith(category);
      } else {
        // Direct MIME check
        return fileType === type;
      }
    });

    if (!matchesType) {
      return { valid: false, reason: `Invalid file type. Expected formatting like: ${accept}` };
    }

    return { valid: true };
  };

  const processFiles = (incomingFiles: ArrayLike<File> | File[]) => {
    setError(null);
    const validIncoming: File[] = [];
    let firstErrorReason: string | null = null;

    for (let i = 0; i < incomingFiles.length; i++) {
      const file = incomingFiles[i];
      const check = validateFile(file);
      if (check.valid) {
        validIncoming.push(file);
      } else if (!firstErrorReason) {
        firstErrorReason = check.reason || 'Invalid file';
      }

      // If we only allow one file, break after the first valid file
      if (!multiple && validIncoming.length > 0) {
        break;
      }
    }

    if (firstErrorReason) {
      setError(firstErrorReason);
    }

    if (validIncoming.length > 0) {
      if (multiple) {
        // Deduplicate: don't add files with the exact same name AND size
        const existingMap = new Set(files.map((f) => `${f.name}-${f.size}`));
        const filtered = validIncoming.filter((f) => !existingMap.has(`${f.name}-${f.size}`));
        onFilesChange([...files, ...filtered]);
      } else {
        onFilesChange(validIncoming);
      }
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
  };

  const removeFile = (indexToRemove: number) => {
    setError(null);
    onFilesChange(files.filter((_, idx) => idx !== indexToRemove));
  };

  const clearAll = () => {
    setError(null);
    onFilesChange([]);
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  const isImageFile = (file: File) => {
    return file.type.startsWith('image/');
  };

  return (
    <div id="file-uploader-wrapper" className="space-y-4">
      {/* Drop Zone Area */}
      <div
        id="drop-zone"
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
        className={`relative border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-300 group focus:outline-none ${
          isDragActive
            ? 'border-[#2563EB] bg-blue-50/50 shadow-inner'
            : 'border-slate-200 bg-slate-50/50 hover:border-blue-500/50 hover:bg-slate-50 hover:shadow-md'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          multiple={multiple}
          accept={accept}
          onChange={handleChange}
          id="hidden-file-input"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="relative">
            <div className={`p-4 rounded-xl bg-white border border-slate-200 text-slate-400 group-hover:text-[#2563EB] group-hover:border-blue-200 transition-colors duration-300 shadow-sm ${
              isDragActive ? 'bg-blue-50 text-blue-600 scale-105 border-blue-200' : ''
            }`}>
              <Upload className="w-8 h-8" />
            </div>
          </div>

          <div className="space-y-1.5 max-w-sm">
            <p className="text-sm font-semibold text-[#1E293B]">
              {multiple ? 'Drag & drop your files here' : 'Drag & drop your file here'}
            </p>
            <p className="text-xs text-slate-500">
              or <span className="text-[#2563EB] font-bold group-hover:underline">browse files</span> on your device
            </p>
          </div>

          <div className="pt-2 flex flex-wrap justify-center gap-x-4 gap-y-1 text-slate-400 font-mono text-[10px]">
            <span>Max Size: {maxSizeMB}MB</span>
            <span>•</span>
            <span className="uppercase">{accept.split(',').map(ext => ext.includes('/') ? ext.split('/')[1] : ext).join(', ')}</span>
          </div>
        </div>
      </div>

      {/* Validation Error Message */}
      {error && (
        <div id="upload-error" className="flex items-start space-x-2.5 p-3.5 bg-red-50 border border-red-100 rounded-xl text-red-600 text-xs text-left animate-in fade-in slide-in-from-top-1">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {/* Selected Files List */}
      {files.length > 0 && (
        <div id="selected-files-container" className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-3">
          <div className="flex justify-between items-center pb-2 border-b border-slate-200">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Selected File{files.length > 1 ? 's' : ''} ({files.length})
            </h3>
            <button
              onClick={(e) => {
                e.stopPropagation();
                clearAll();
              }}
              className="text-xs text-slate-400 hover:text-red-600 transition-colors font-medium cursor-pointer"
            >
              Remove All
            </button>
          </div>

          <div className="max-h-60 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
            {files.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-xl hover:border-slate-300 transition-all duration-150 shadow-sm"
              >
                <div className="flex items-center space-x-3 text-left overflow-hidden">
                  <div className="w-9 h-9 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-500 shrink-0 overflow-hidden">
                    {isImageFile(file) ? (
                      <img
                        src={URL.createObjectURL(file)}
                        alt="preview"
                        className="w-full h-full object-cover rounded-lg"
                        referrerPolicy="no-referrer"
                        onLoad={(e) => {
                          // Clean up object URL memory
                          setTimeout(() => URL.revokeObjectURL((e.target as any).src), 10000);
                        }}
                      />
                    ) : (
                      <File className="w-5 h-5 text-slate-400" />
                    )}
                  </div>
                  <div className="overflow-hidden">
                    <p className="text-xs font-semibold text-[#1E293B] truncate max-w-[200px] sm:max-w-xs">{file.name}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">{formatBytes(file.size)}</p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}
                  className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
                  title="Remove file"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {multiple && (
            <button
              onClick={onButtonClick}
              className="w-full py-2.5 bg-white border border-dashed border-slate-200 hover:border-blue-500/60 text-xs font-semibold text-slate-500 hover:text-[#1E293B] rounded-xl flex items-center justify-center space-x-1.5 transition-all mt-2 cursor-pointer shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Add More Files</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
