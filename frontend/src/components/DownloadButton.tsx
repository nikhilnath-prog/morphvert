import { useState } from 'react';
import type { ReactNode } from 'react';
import { Download } from 'lucide-react';
import { fileService } from '../services/api.js';

interface DownloadButtonProps {
  fileId: string;
  filename: string;
  className?: string;
  iconOnly?: boolean;
  title?: string;
  children?: ReactNode;
}

export default function DownloadButton({
  fileId,
  filename,
  className = '',
  iconOnly = false,
  title,
  children,
}: DownloadButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleClick = () => {
    if (!fileId || isDownloading) {
      return;
    }

    setIsDownloading(true);

    try {
      const link = document.createElement('a');
      link.href = fileService.getDownloadUrl(fileId);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } finally {
      window.setTimeout(() => setIsDownloading(false), 300);
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      title={title || (isDownloading ? 'Preparing download' : 'Download file')}
      disabled={isDownloading}
      className={className}
    >
      {iconOnly ? (
        isDownloading ? <span className="w-4 h-4 animate-pulse rounded-full bg-white/70" /> : <Download className="w-4 h-4" />
      ) : children ? (
        <>
          {isDownloading ? <span className="w-4 h-4 animate-pulse rounded-full bg-white/70" /> : null}
          {children}
        </>
      ) : (
        <>
          {isDownloading ? <span className="w-4 h-4 animate-pulse rounded-full bg-white/70" /> : <Download className="w-4 h-4" />}
          <span>{isDownloading ? 'Downloading...' : 'Download'}</span>
        </>
      )}
    </button>
  );
}