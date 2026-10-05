import express from 'express';
import path from 'path';
import multer from 'multer';
import { createServer as createViteServer } from 'vite';

// Define Interface for in-memory files
interface MemoryFile {
  fileId: string;
  filename: string;
  size: number;
  mimetype: string;
  buffer: Buffer;
  createdAt: Date;
}

interface ConversionHistoryItem {
  id: string;
  toolId: string;
  toolName: string;
  status: 'completed' | 'failed';
  date: string;
  originalName: string;
  resultFileId: string;
  resultName: string;
  resultSize: number;
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  // JSON and URL-encoded body parser
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // In-memory data store
  const filesStore = new Map<string, MemoryFile>();
  const historyStore: ConversionHistoryItem[] = [];

  // Initialize Multer for in-memory storage (prevents disk clutter)
  const storage = multer.memoryStorage();
  const upload = multer({
    storage: storage,
    limits: {
      fileSize: 50 * 1024 * 1024, // 50MB max
    },
  });

  // Endpoints: File upload
  app.post('/api/v1/files/upload', upload.single('file'), (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const fileId = 'file_' + Math.random().toString(36).substring(2, 15);
      const newFile: MemoryFile = {
        fileId,
        filename: req.file.originalname,
        size: req.file.size,
        mimetype: req.file.mimetype,
        buffer: req.file.buffer,
        createdAt: new Date(),
      };

      filesStore.set(fileId, newFile);

      res.status(200).json({
        fileId: newFile.fileId,
        filename: newFile.filename,
        size: newFile.size,
        mimetype: newFile.mimetype,
        uploadedAt: newFile.createdAt.toISOString(),
      });
    } catch (err: any) {
      console.error('Upload Error:', err);
      res.status(500).json({ error: err.message || 'Error uploading file' });
    }
  });

  // Helper to generate a dummy PDF buffer
  const generatePdfBuffer = (title: string): Buffer => {
    // Return a basic, clean file stream text/pdf representation
    return Buffer.from(
      `%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 120 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(${title}) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000216 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n386\n%%EOF`
    );
  };

  // Helper to generate a dummy Docx buffer
  const generateDocxBuffer = (text: string): Buffer => {
    // Return mock Word document content (plain text representing document)
    return Buffer.from(`Morphvert Professional Document\nGenerated: ${new Date().toLocaleString()}\nContent: ${text}`);
  };

  // Helper to generate dummy PNG buffer
  const generatePngBuffer = (): Buffer => {
    // Return a 1x1 transparent pixel png
    return Buffer.from(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
      'base64'
    );
  };

  // Endpoints: PDF -> DOCX
  app.post('/api/v1/convert/pdf/to-docx', (req, res) => {
    try {
      const { fileId } = req.body;
      if (!fileId) {
        return res.status(400).json({ error: 'Missing fileId parameter' });
      }

      const file = filesStore.get(fileId);
      if (!file) {
        return res.status(404).json({ error: 'Source file not found' });
      }

      // Perform simulated conversion
      const resultFileId = 'result_' + Math.random().toString(36).substring(2, 15);
      const resultFilename = file.filename.replace(/\.[^/.]+$/, "") + ".docx";
      const wordContent = `This docx was successfully transformed from your PDF: "${file.filename}". File size was ${file.size} bytes.`;
      const docxBuffer = generateDocxBuffer(wordContent);

      const resultFile: MemoryFile = {
        fileId: resultFileId,
        filename: resultFilename,
        size: docxBuffer.length,
        mimetype: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        buffer: docxBuffer,
        createdAt: new Date(),
      };

      filesStore.set(resultFileId, resultFile);

      // Save to History
      const historyItem: ConversionHistoryItem = {
        id: 'hist_' + Math.random().toString(36).substring(2, 15),
        toolId: 'pdf-to-docx',
        toolName: 'PDF to DOCX',
        status: 'completed',
        date: new Date().toISOString(),
        originalName: file.filename,
        resultFileId: resultFileId,
        resultName: resultFilename,
        resultSize: resultFile.size,
      };
      historyStore.unshift(historyItem);

      res.status(200).json({
        id: historyItem.id,
        toolId: 'pdf-to-docx',
        status: 'completed',
        originalFiles: [{
          fileId: file.fileId,
          filename: file.filename,
          size: file.size,
          mimetype: file.mimetype,
          uploadedAt: file.createdAt.toISOString()
        }],
        resultFileId,
        resultFilename,
        resultSize: resultFile.size,
        createdAt: historyItem.date,
      });
    } catch (err: any) {
      res.status(500).json({ error: err.message || 'Error during conversion' });
    }
  });

  // Endpoints: PDF -> Images
  app.post('/api/v1/convert/pdf/to-images', (req, res) => {
    try {
      const { fileId } = req.body;
      if (!fileId) {
        return res.status(400).json({ error: 'Missing fileId parameter' });
      }

      const file = filesStore.get(fileId);
      if (!file) {
        return res.status(404).json({ error: 'Source file not found' });
      }

      const resultFileId = 'result_' + Math.random().toString(36).substring(2, 15);
      const resultFilename = file.filename.replace(/\.[^/.]+$/, "") + "_pages.zip";
      
      // Mock zipped pages
      const zipBuffer = Buffer.from(`Mock ZIP File containing PNGs converted from: ${file.filename}`);
      const resultFile: MemoryFile = {
        fileId: resultFileId,
        filename: resultFilename,
        size: zipBuffer.length,
        mimetype: 'application/zip',
        buffer: zipBuffer,
        createdAt: new Date(),
      };

      filesStore.set(resultFileId, resultFile);

      const historyItem: ConversionHistoryItem = {
        id: 'hist_' + Math.random().toString(36).substring(2, 15),
        toolId: 'pdf-to-images',
        toolName: 'PDF to Images',
        status: 'completed',
        date: new Date().toISOString(),
        originalName: file.filename,
        resultFileId: resultFileId,
        resultName: resultFilename,
        resultSize: resultFile.size,
      };
      historyStore.unshift(historyItem);

      res.status(200).json({
        id: historyItem.id,
        toolId: 'pdf-to-images',
        status: 'completed',
        originalFiles: [{
          fileId: file.fileId,
          filename: file.filename,
          size: file.size,
          mimetype: file.mimetype,
          uploadedAt: file.createdAt.toISOString()
        }],
        resultFileId,
        resultFilename,
        resultSize: resultFile.size,
        createdAt: historyItem.date,
      });
    } catch (err: any) {
      res.status(500).json({ error: err.message || 'Error during conversion' });
    }
  });

  // Endpoints: Merge PDF
  app.post('/api/v1/pdf/merge', (req, res) => {
    try {
      const { fileIds } = req.body;
      if (!fileIds || !Array.isArray(fileIds) || fileIds.length === 0) {
        return res.status(400).json({ error: 'Missing or invalid fileIds' });
      }

      const originalFiles: any[] = [];
      let totalOriginalSize = 0;
      let primaryFilename = 'merged_document.pdf';

      for (let i = 0; i < fileIds.length; i++) {
        const file = filesStore.get(fileIds[i]);
        if (!file) {
          return res.status(404).json({ error: `File at index ${i} (${fileIds[i]}) not found` });
        }
        originalFiles.push({
          fileId: file.fileId,
          filename: file.filename,
          size: file.size,
          mimetype: file.mimetype,
          uploadedAt: file.createdAt.toISOString()
        });
        totalOriginalSize += file.size;
        if (i === 0) {
          primaryFilename = file.filename.replace(/\.[^/.]+$/, "") + "_merged.pdf";
        }
      }

      const resultFileId = 'result_' + Math.random().toString(36).substring(2, 15);
      const mergedPdfBuffer = generatePdfBuffer(`Merged PDF of ${fileIds.length} files`);

      const resultFile: MemoryFile = {
        fileId: resultFileId,
        filename: primaryFilename,
        size: mergedPdfBuffer.length,
        mimetype: 'application/pdf',
        buffer: mergedPdfBuffer,
        createdAt: new Date(),
      };

      filesStore.set(resultFileId, resultFile);

      const historyItem: ConversionHistoryItem = {
        id: 'hist_' + Math.random().toString(36).substring(2, 15),
        toolId: 'merge-pdf',
        toolName: 'Merge PDF',
        status: 'completed',
        date: new Date().toISOString(),
        originalName: `${fileIds.length} Files`,
        resultFileId: resultFileId,
        resultName: primaryFilename,
        resultSize: resultFile.size,
      };
      historyStore.unshift(historyItem);

      res.status(200).json({
        id: historyItem.id,
        toolId: 'merge-pdf',
        status: 'completed',
        originalFiles,
        resultFileId,
        resultFilename: primaryFilename,
        resultSize: resultFile.size,
        createdAt: historyItem.date,
      });
    } catch (err: any) {
      res.status(500).json({ error: err.message || 'Error during merge' });
    }
  });

  // Endpoints: Split PDF
  app.post('/api/v1/pdf/split', (req, res) => {
    try {
      const { fileId, pages } = req.body;
      if (!fileId) {
        return res.status(400).json({ error: 'Missing fileId parameter' });
      }

      const file = filesStore.get(fileId);
      if (!file) {
        return res.status(404).json({ error: 'Source file not found' });
      }

      const resultFileId = 'result_' + Math.random().toString(36).substring(2, 15);
      const resultFilename = file.filename.replace(/\.[^/.]+$/, "") + "_split.zip";
      
      const zipBuffer = Buffer.from(`ZIP archive containing split pages (${pages || '1-end'}) of: ${file.filename}`);
      const resultFile: MemoryFile = {
        fileId: resultFileId,
        filename: resultFilename,
        size: zipBuffer.length,
        mimetype: 'application/zip',
        buffer: zipBuffer,
        createdAt: new Date(),
      };

      filesStore.set(resultFileId, resultFile);

      const historyItem: ConversionHistoryItem = {
        id: 'hist_' + Math.random().toString(36).substring(2, 15),
        toolId: 'split-pdf',
        toolName: 'Split PDF',
        status: 'completed',
        date: new Date().toISOString(),
        originalName: file.filename,
        resultFileId: resultFileId,
        resultName: resultFilename,
        resultSize: resultFile.size,
      };
      historyStore.unshift(historyItem);

      res.status(200).json({
        id: historyItem.id,
        toolId: 'split-pdf',
        status: 'completed',
        originalFiles: [{
          fileId: file.fileId,
          filename: file.filename,
          size: file.size,
          mimetype: file.mimetype,
          uploadedAt: file.createdAt.toISOString()
        }],
        resultFileId,
        resultFilename,
        resultSize: resultFile.size,
        createdAt: historyItem.date,
      });
    } catch (err: any) {
      res.status(500).json({ error: err.message || 'Error splitting file' });
    }
  });

  // Endpoints: Image to PDF
  app.post('/api/v1/convert/image/to-pdf', (req, res) => {
    try {
      const { fileIds } = req.body;
      if (!fileIds || !Array.isArray(fileIds) || fileIds.length === 0) {
        return res.status(400).json({ error: 'Missing or invalid fileIds' });
      }

      const originalFiles: any[] = [];
      let primaryFilename = 'converted_images.pdf';

      for (let i = 0; i < fileIds.length; i++) {
        const file = filesStore.get(fileIds[i]);
        if (!file) {
          return res.status(404).json({ error: `File at index ${i} (${fileIds[i]}) not found` });
        }
        originalFiles.push({
          fileId: file.fileId,
          filename: file.filename,
          size: file.size,
          mimetype: file.mimetype,
          uploadedAt: file.createdAt.toISOString()
        });
        if (i === 0) {
          primaryFilename = file.filename.replace(/\.[^/.]+$/, "") + ".pdf";
        }
      }

      const resultFileId = 'result_' + Math.random().toString(36).substring(2, 15);
      const generatedPdf = generatePdfBuffer(`PDF created from ${fileIds.length} images`);

      const resultFile: MemoryFile = {
        fileId: resultFileId,
        filename: primaryFilename,
        size: generatedPdf.length,
        mimetype: 'application/pdf',
        buffer: generatedPdf,
        createdAt: new Date(),
      };

      filesStore.set(resultFileId, resultFile);

      const historyItem: ConversionHistoryItem = {
        id: 'hist_' + Math.random().toString(36).substring(2, 15),
        toolId: 'image-to-pdf',
        toolName: 'Image to PDF',
        status: 'completed',
        date: new Date().toISOString(),
        originalName: `${fileIds.length} Images`,
        resultFileId: resultFileId,
        resultName: primaryFilename,
        resultSize: resultFile.size,
      };
      historyStore.unshift(historyItem);

      res.status(200).json({
        id: historyItem.id,
        toolId: 'image-to-pdf',
        status: 'completed',
        originalFiles,
        resultFileId,
        resultFilename: primaryFilename,
        resultSize: resultFile.size,
        createdAt: historyItem.date,
      });
    } catch (err: any) {
      res.status(500).json({ error: err.message || 'Error during PDF conversion' });
    }
  });

  // Endpoints: Compress PDF
  app.post('/api/v1/pdf/compress', (req, res) => {
    try {
      const { fileId, level } = req.body; // level: 'low' | 'recommended' | 'extreme'
      if (!fileId) {
        return res.status(400).json({ error: 'Missing fileId parameter' });
      }

      const file = filesStore.get(fileId);
      if (!file) {
        return res.status(404).json({ error: 'Source file not found' });
      }

      const ratio = level === 'extreme' ? 0.35 : level === 'low' ? 0.75 : 0.55;
      const targetSize = Math.max(1024, Math.floor(file.size * ratio));

      const resultFileId = 'result_' + Math.random().toString(36).substring(2, 15);
      const resultFilename = file.filename.replace(/\.[^/.]+$/, "") + "_compressed.pdf";
      const compressedBuffer = generatePdfBuffer(`Compressed content of: ${file.filename} (Ratio: ${level})`);

      const resultFile: MemoryFile = {
        fileId: resultFileId,
        filename: resultFilename,
        size: targetSize, // Reflected ratio size
        mimetype: 'application/pdf',
        buffer: compressedBuffer,
        createdAt: new Date(),
      };

      filesStore.set(resultFileId, resultFile);

      const historyItem: ConversionHistoryItem = {
        id: 'hist_' + Math.random().toString(36).substring(2, 15),
        toolId: 'compress-pdf',
        toolName: 'Compress PDF',
        status: 'completed',
        date: new Date().toISOString(),
        originalName: file.filename,
        resultFileId: resultFileId,
        resultName: resultFilename,
        resultSize: targetSize,
      };
      historyStore.unshift(historyItem);

      res.status(200).json({
        id: historyItem.id,
        toolId: 'compress-pdf',
        status: 'completed',
        originalFiles: [{
          fileId: file.fileId,
          filename: file.filename,
          size: file.size,
          mimetype: file.mimetype,
          uploadedAt: file.createdAt.toISOString()
        }],
        resultFileId,
        resultFilename,
        resultSize: targetSize,
        createdAt: historyItem.date,
      });
    } catch (err: any) {
      res.status(500).json({ error: err.message || 'Error compressing file' });
    }
  });

  // Endpoints: Download Result Download API
  app.get('/api/v1/download/:fileId', (req, res) => {
    try {
      const { fileId } = req.params;
      const file = filesStore.get(fileId);
      if (!file) {
        return res.status(404).send('File not found or expired');
      }

      res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(file.filename)}"`);
      res.setHeader('Content-Type', file.mimetype);
      res.setHeader('Content-Length', file.size);
      res.send(file.buffer);
    } catch (err: any) {
      res.status(500).send(err.message || 'Error retrieving file');
    }
  });

  // Endpoints: History Retrievals
  app.get('/api/v1/conversions/history', (req, res) => {
    try {
      res.status(200).json({ history: historyStore });
    } catch (err: any) {
      res.status(500).json({ error: 'Error fetching history list' });
    }
  });

  // Vite development middleware vs Static Production files
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[Morphvert] Backend Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((error) => {
  console.error('Failed to start server:', error);
});
