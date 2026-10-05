import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { TOOLS } from '../utils/toolsData';
import FileUpload from '../components/FileUpload';
import ConversionStatus from '../components/ConversionStatus';
import { fileService } from '../services/api.js';
import { formatBytes } from '../utils/helpers';
import {
  ArrowLeft,
  Settings,
  ArrowUp,
  ArrowDown,
  Trash2,
  FileCheck,
  CheckCircle,
  HelpCircle,
  Scissors,
  Layers,
  Minimize2,
  Image,
  Info
} from 'lucide-react';

export default function ToolDetailPage() {
  const { toolId } = useParams<{ toolId: string }>();
  const navigate = useNavigate();

  // Find tool definition
  const tool = TOOLS.find((t) => t.id === toolId);

  if (!tool) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#F8FAFC] text-[#1E293B] p-6">
        <div className="space-y-4 max-w-sm text-center">
          <Info className="w-12 h-12 text-[#2563EB] mx-auto" />
          <h2 className="text-xl font-bold">Tool Not Found</h2>
          <p className="text-xs text-slate-500">The page or document utility you requested does not exist or has been relocated.</p>
          <Link to="/tools" className="inline-block px-4 py-2 bg-[#2563EB] rounded-lg text-xs font-semibold text-white">
            Return to Tools
          </Link>
        </div>
      </div>
    );
  }

  // Upload/Conversion states
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [conversionProgress, setConversionProgress] = useState(0);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'failed'>('idle');

  // Custom tool configurables
  const [compressionLevel, setCompressionLevel] = useState<'low' | 'recommended' | 'extreme'>('recommended');
  const [splitRange, setSplitRange] = useState('1-end');

  // Result metadata
  const [resultFileId, setResultFileId] = useState<string | undefined>(undefined);
  const [resultFilename, setResultFilename] = useState<string | undefined>(undefined);
  const [resultSize, setResultSize] = useState<number | undefined>(undefined);
  const [resultFiles, setResultFiles] = useState<Array<{ fileId?: string; filename: string; downloadUrl: string; size?: number; pageNumber?: number }> | undefined>(undefined);
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
  const queryClient = useQueryClient();

  const conversionMutation = useMutation({
    mutationFn: async () => {
      switch (tool.id) {
        case 'pdf-to-docx':
          return fileService.convertToDocx(files[0]);
        case 'pdf-to-excel':
          return fileService.pdfToExcel(files[0]);
        case 'pdf-to-images':
          return fileService.convertToImages(files[0]);
        case 'excel-to-pdf':
          return fileService.excelToPdf(files[0]);
        case 'merge-pdf':
          return fileService.mergePdf(files);
        case 'split-pdf':
          return fileService.splitPdf(files[0], splitRange);
        case 'image-to-pdf':
          return fileService.imageToPdf(files);
        case 'compress-pdf':
          return fileService.compressPdf(files[0], compressionLevel);
        default:
          throw new Error('Unknown tool identifier');
      }
    },
  });

  // File reordering actions
  const moveUp = (idx: number) => {
    if (idx === 0) return;
    const work = [...files];
    const prev = work[idx - 1];
    work[idx - 1] = work[idx];
    work[idx] = prev;
    setFiles(work);
  };

  const moveDown = (idx: number) => {
    if (idx === files.length - 1) return;
    const work = [...files];
    const next = work[idx + 1];
    work[idx + 1] = work[idx];
    work[idx] = next;
    setFiles(work);
  };

  const removeAt = (idx: number) => {
    setFiles(files.filter((_, i) => i !== idx));
  };

  // Main Conversion Workflow Execution
  const executeConversion = async () => {
    if (files.length === 0) return;

    setStatus('uploading');
    setUploadProgress(0);
    setConversionProgress(0);
    setErrorMessage(undefined);

    try {
      const totalCount = files.length;

      // 1. Sequentially upload matching files to server memory
      for (let i = 0; i < totalCount; i++) {
        const file = files[i];
        
        // Compute partition progress boundaries
        const baseProgress = (i / totalCount) * 100;
        await fileService.uploadFile(file, (p) => {
          // Adjust overall progress relative to file index
          const incremental = (p / totalCount);
          setUploadProgress(Math.round(baseProgress + incremental));
        });

      }

      setUploadProgress(100);
      setStatus('processing');

      // 2. Animate and simulate conversion steps over 2 seconds
      let pAccumulate = 5;
      const interval = setInterval(() => {
        pAccumulate += Math.floor(Math.random() * 12) + 4;
        if (pAccumulate >= 92) {
          pAccumulate = 92;
          clearInterval(interval);
        }
        setConversionProgress(pAccumulate);
      }, 150);

      // 3. Initiate proper endpoint requests
      const resultData = await conversionMutation.mutateAsync() as {
        resultFileId?: string;
        resultFilename?: string;
        resultSize?: number;
        items?: Array<{ fileId?: string; filename: string; downloadUrl: string; size?: number; pageNumber?: number }>;
      };

      clearInterval(interval);
      setConversionProgress(100);

      // 4. Update Success state
      setResultFileId(resultData.resultFileId);
      setResultFilename(resultData.resultFilename);
      setResultSize(resultData.resultSize);
      setResultFiles(resultData.items);
      setStatus('completed');
      queryClient.invalidateQueries({ queryKey: ['conversions-history'] });
    } catch (err: any) {
      console.error(err);
      setErrorMessage(fileService.getApiErrorMessage(err, 'Transmission / Operation interrupted on the host.'));
      setStatus('failed');
    }
  };

  const handleReset = () => {
    setFiles([]);
    setStatus('idle');
    setUploadProgress(0);
    setConversionProgress(0);
    setResultFileId(undefined);
    setResultFilename(undefined);
    setResultSize(undefined);
    setResultFiles(undefined);
    setErrorMessage(undefined);
  };

  const isMultiple = tool.multiple;

  return (
    <div id="tool-detail-page" className="min-h-screen bg-[#F8FAFC] text-[#1E293B] relative py-12 sm:py-16">
      {/* Decorative gradient overlay */}
      <div className="absolute top-20 left-10 w-80 h-80 rounded-full bg-blue-500/5 filter blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 right-10 w-80 h-80 rounded-full bg-cyan-400/5 filter blur-[120px] pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 relative z-10">
        
        {/* Back and breadcrumb panel */}
        <div className="flex justify-between items-center bg-transparent sticky top-16 z-30 py-2 border-b border-transparent">
          <Link
            to="/tools"
            className="inline-flex items-center space-x-1.5 text-xs text-slate-500 hover:text-[#1E293B] transition-colors focus:outline-none"
            id="back-to-tools-link"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to All Tools</span>
          </Link>
          <span className="text-[10px] uppercase font-mono tracking-widest text-[#2563EB] font-bold">
            {tool.category} Utility
          </span>
        </div>

        {/* Header Hero Title */}
        <div className="text-left space-y-2 max-w-2xl">
          <h1 className="font-sans font-extrabold text-2xl sm:text-4xl text-[#1E293B] tracking-tight">
            {tool.name}
          </h1>
          <p className="text-slate-500 text-xs sm:text-sm leading-relaxed">
            {tool.description}
          </p>
        </div>

        {status === 'idle' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            
            {/* Core Workspace Dropzone / Multiple file table */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white border border-slate-200 rounded-3xl p-5 sm:p-6 space-y-5 shadow-sm">
                <div className="space-y-1 text-left">
                  <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">1. Select Files</h2>
                  <p className="text-xs text-slate-500">Selected documents are loaded dynamically into server memory stream buffers.</p>
                </div>

                <FileUpload
                  accept={tool.accepts}
                  multiple={isMultiple}
                  maxSizeMB={tool.maxSizeMB}
                  files={files}
                  onFilesChange={setFiles}
                />
              </div>

              {/* Extra Multiple Reordering Control widget */}
              {isMultiple && files.length >= 2 && (
                <div className="bg-white border border-slate-200 rounded-3xl p-6 text-left space-y-4 shadow-sm animate-in fade-in duration-300 font-sans">
                  <div className="space-y-1 block">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">Rearrange Document Order</h3>
                    <p className="text-[11px] text-slate-500">Morphvert processes files in sequence from top to bottom. Order them correctly.</p>
                  </div>

                  <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                    {files.map((file, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-slate-50 border border-slate-100 rounded-xl"
                      >
                        <div className="flex items-center space-x-3 overflow-hidden text-left font-sans">
                          <span className="w-5 h-5 rounded-md bg-white border border-slate-200 flex items-center justify-center font-mono text-[10px] text-slate-500 shrink-0 font-bold">
                            {idx + 1}
                          </span>
                          <span className="text-xs font-medium text-[#1E293B] truncate max-w-[200px] sm:max-w-xs">{file.name}</span>
                          <span className="text-[10px] text-slate-400 shrink-0">({formatBytes(file.size)})</span>
                        </div>

                        <div className="flex items-center space-x-1.5 ml-2">
                          <button
                            type="button"
                            onClick={() => moveUp(idx)}
                            disabled={idx === 0}
                            className="p-1 text-slate-400 hover:text-[#1E293B] hover:bg-slate-100 rounded transition disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
                            title="Move up"
                          >
                            <ArrowUp className="w-3.5 h-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => moveDown(idx)}
                            disabled={idx === files.length - 1}
                            className="p-1 text-slate-400 hover:text-[#1E293B] hover:bg-slate-100 rounded transition disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
                            title="Move down"
                          >
                            <ArrowDown className="w-3.5 h-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => removeAt(idx)}
                            className="p-1 text-slate-400 hover:text-red-650 hover:bg-red-50 rounded transition cursor-pointer text-slate-400 hover:text-red-600"
                            title="Remove file"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Config & Conversion Actions Sidebar Panel */}
            <div className="space-y-6">
              <div className="bg-white border border-slate-200 rounded-3xl p-6 text-left space-y-6 relative overflow-hidden shadow-sm">
                <div className="space-y-1.5">
                  <div className="flex items-center space-x-2 text-xs font-bold text-slate-400 uppercase tracking-wider font-mono text-xs">
                    <Settings className="w-4 h-4 text-slate-400" />
                    <span>2. Preferences</span>
                  </div>
                  <p className="text-xs text-slate-500">Configure parameters before activating core conversion engine.</p>
                </div>

                {/* Specific tool configurables widgets */}
                {tool.id === 'compress-pdf' && (
                  <div className="space-y-3">
                    <label className="text-xs font-semibold text-slate-700">Compression Level</label>
                    <div className="grid grid-cols-1 gap-2.5">
                      {[
                        { id: 'recommended', name: 'Recommended Compression', desc: 'Good quality and file size reduction' },
                        { id: 'extreme', name: 'Extreme Compression', desc: 'Slight quality loss, maximum compression ratio' },
                        { id: 'low', name: 'Low Compression', desc: 'Exceptional image quality, low compression ratio' },
                      ].map((lvl) => (
                        <button
                          key={lvl.id}
                          type="button"
                          onClick={() => setCompressionLevel(lvl.id as any)}
                          className={`p-3 rounded-xl border text-left space-y-1 transition-all cursor-pointer ${
                            compressionLevel === lvl.id
                              ? 'border-[#2563EB] bg-blue-50 text-[#2563EB]'
                              : 'border-slate-200 bg-slate-50 text-slate-500 hover:border-slate-350 hover:bg-[#F8FAFC]'
                          }`}
                        >
                          <div className="text-xs font-bold">{lvl.name}</div>
                          <div className="text-[10px] leading-relaxed opacity-80">{lvl.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {tool.id === 'split-pdf' && (
                  <div className="space-y-3">
                    <label className="text-xs font-semibold text-slate-700">Page Range Settings</label>
                    <div className="space-y-1.5 font-sans">
                      <input
                        type="text"
                        value={splitRange}
                        onChange={(e) => setSplitRange(e.target.value)}
                        placeholder="e.g. 1-3, 5, 8-end"
                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-xs text-[#1E293B] placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                      />
                      <p className="text-[10px] text-slate-500 leading-relaxed">
                        Specify pages to isolate or range indexes. Use <b>1-end</b> to split and pack all pages into a folder automatically.
                      </p>
                    </div>
                  </div>
                )}

                {tool.id === 'image-to-pdf' && (
                  <div className="space-y-2 text-xs py-2 px-3.5 bg-blue-50 border border-blue-100 rounded-xl text-blue-700 font-sans">
                    <p className="font-semibold flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-blue-600" />
                      <span>Orientation Auto-Fit</span>
                    </p>
                    <p className="text-[10px] opacity-90 leading-relaxed text-blue-600/90">Images will be resized and centered on A4 paper margins automatically.</p>
                  </div>
                )}

                {(tool.id === 'pdf-to-docx' || tool.id === 'pdf-to-excel') && (
                  <div className="space-y-2 text-xs py-2 px-3.5 bg-emerald-50 border border-emerald-100 rounded-xl text-emerald-700 font-sans">
                    <p className="font-semibold flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{tool.id === 'pdf-to-docx' ? 'Smart OCR Detection' : 'Table Extraction'}</span>
                    </p>
                    <p className="text-[10px] opacity-90 leading-relaxed text-emerald-600/90">{tool.id === 'pdf-to-docx' ? 'Fonts are automatically mapped to standard matching system interfaces.' : 'Structured table content is converted into worksheet rows and columns when available.'}</p>
                  </div>
                )}

                {tool.id === 'excel-to-pdf' && (
                  <div className="space-y-2 text-xs py-2 px-3.5 bg-violet-50 border border-violet-100 rounded-xl text-violet-700 font-sans">
                    <p className="font-semibold flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-violet-600" />
                      <span>Workbook to PDF</span>
                    </p>
                    <p className="text-[10px] opacity-90 leading-relaxed text-violet-600/90">Sheet names, row values, and basic formatting are kept readable in the exported PDF.</p>
                  </div>
                )}

                {/* Fallback tooltip when files is empty */}
                {files.length === 0 ? (
                  <div className="text-xs text-slate-500 bg-slate-55 p-4 border border-slate-200 rounded-2xl flex items-start gap-2">
                    <HelpCircle className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                    <p>Select at least one valid file to activate the Morphvert high fidelity file conversion workbench.</p>
                  </div>
                ) : (
                  <div className="space-y-2.5 font-sans">
                    <div className="text-xs text-slate-550 font-semibold flex items-center justify-between">
                      <span>Total Queue:</span>
                      <span className="text-[#1E293B] font-bold">{files.length} Item{files.length > 1 ? 's' : ''}</span>
                    </div>
                    <button
                      type="button"
                      onClick={executeConversion}
                      className="w-full py-4.5 bg-[#2563EB] hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-600/20 active:scale-98 text-white font-bold text-sm rounded-2xl transition-all cursor-pointer select-none flex items-center justify-center space-x-2"
                    >
                      <span>Activate Conversion</span>
                    </button>
                  </div>
                )}
              </div>
            </div>

          </div>
        ) : (
          /* Conversion status tracker box */
          <div className="max-w-2xl mx-auto">
            <ConversionStatus
              status={status}
              uploadProgress={uploadProgress}
              conversionProgress={conversionProgress}
              resultFilename={resultFilename}
              resultSize={resultSize}
              resultFileId={resultFileId}
              resultFiles={resultFiles}
              errorMessage={errorMessage}
              onReset={handleReset}
              originalFileName={files.length > 0 ? files[0].name : undefined}
              toolName={tool.name}
            />
          </div>
        )}
      </div>
    </div>
  );
}
