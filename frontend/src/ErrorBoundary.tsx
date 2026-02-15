import React from 'react'

type Props = { children: React.ReactNode }
type State = { hasError: boolean; error: Error | null }

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div className="container" style={{ padding: '2rem', maxWidth: 600 }}>
          <div className="card">
            <h2 style={{ color: '#c62828' }}>Ошибка приложения</h2>
            <pre style={{ background: '#f5f5f5', padding: '1rem', overflow: 'auto', fontSize: '0.85rem' }}>
              {this.state.error.message}
            </pre>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Обновить
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
