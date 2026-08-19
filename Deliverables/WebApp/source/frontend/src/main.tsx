import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import App from './App'
import ErrorBoundary from './components/ui/ErrorBoundary'
import './index.css'
import { useThemeStore } from './store/themeStore'

// Inicializar tema desde localStorage
const isDark = useThemeStore.getState().isDark
document.documentElement.classList.toggle('dark', isDark)

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,     // 5 minutos
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 3500,
            style: {
              background: isDark ? '#1A1A2E' : '#fff',
              color: isDark ? '#F0F0FF' : '#1A1A2E',
              border: '1px solid rgba(255,107,107,0.3)',
              borderRadius: '16px',
              fontFamily: 'Nunito, sans-serif',
              fontWeight: '600',
            },
            success: {
              iconTheme: { primary: '#4ECDC4', secondary: '#fff' },
            },
            error: {
              iconTheme: { primary: '#FF6B6B', secondary: '#fff' },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)
