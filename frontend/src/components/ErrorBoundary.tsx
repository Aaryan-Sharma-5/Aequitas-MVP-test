import React from 'react';

interface State {
  hasError: boolean;
  errorMessage?: string;
}

class ErrorBoundary extends React.Component<React.PropsWithChildren<{}>, State> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, errorMessage: error?.message };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Log full error for debugging
    // In production you might send this to an error tracking service
    // eslint-disable-next-line no-console
    console.error('ErrorBoundary caught an error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-sm font-semibold text-red-800">Something went wrong rendering the map</h3>
          <p className="mt-1 text-xs text-red-700">{this.state.errorMessage || 'An unexpected error occurred.'}</p>
          <p className="mt-2 text-xs text-gray-600">Check the browser console for a full stack trace.</p>
        </div>
      );
    }

    return this.props.children as React.ReactElement;
  }
}

export default ErrorBoundary;
