import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('AuraCFO UI Error caught by boundary:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[70vh] p-6 text-center space-y-4">
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-full text-red-400">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h2 className="text-lg font-bold text-slate-100">Render Error Intercepted</h2>
          <p className="text-xs text-slate-400 max-w-md font-mono bg-[#181B24] p-3 rounded border border-[#232738] overflow-x-auto text-left">
            {this.state.error?.message || 'An unexpected rendering error occurred.'}
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
            className="flex items-center gap-1.5 py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
