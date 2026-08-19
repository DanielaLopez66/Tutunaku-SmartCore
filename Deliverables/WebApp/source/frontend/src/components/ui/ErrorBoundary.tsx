// TUTUNAKU — ErrorBoundary
import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RotateCcw } from 'lucide-react'
import { motion } from 'framer-motion'

interface Props {
  children?: ReactNode
}

interface State {
  hasError: boolean
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-[var(--color-bg)]">
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-center max-w-md p-8 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl"
          >
            <div className="w-20 h-20 bg-red-500/20 text-red-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <AlertTriangle size={40} />
            </div>
            <h1 className="text-2xl font-display font-bold mb-3">Algo salió mal</h1>
            <p className="text-[var(--color-muted)] mb-8">
              Hemos tenido un tropiezo técnico. No te preocupes, tus datos están a salvo.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3"
            >
              <RotateCcw size={18} />
              Reintentar carga
            </button>
          </motion.div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
