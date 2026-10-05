import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import ToolsPage from './pages/ToolsPage';
import ToolDetailPage from './pages/ToolDetailPage';
import ConversionHistory from './pages/ConversionHistory';
import AiPdfSummarizer from './pages/AiPdfSummarizer';
import OrganizePdfPage from './pages/OrganizePdfPage';

// Initialize TanStack React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
    mutations: {
      retry: 0,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div id="app-viewport-root" className="flex flex-col min-h-screen bg-[#F8FAFC] text-[#1E293B] font-sans selection:bg-blue-500/10 selection:text-blue-600">
          
          {/* Header Navigation HUD */}
          <Navbar />

          {/* Primary View Router Area */}
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/tools" element={<ToolsPage />} />
              <Route path="/tools/ai-pdf-summarizer" element={<AiPdfSummarizer />} />
              <Route path="/tools/organize-pdf" element={<OrganizePdfPage />} />
              <Route path="/tools/:toolId" element={<ToolDetailPage />} />
              <Route path="/history" element={<ConversionHistory />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          {/* Footer Branding Area */}
          <Footer />

        </div>
      </Router>
    </QueryClientProvider>
  );
}
