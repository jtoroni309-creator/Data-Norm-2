import React from 'react'
import ReactDOM from 'react-dom/client'
import { FluentProvider, webLightTheme } from '@fluentui/react-components'
import './index.css'

function App() {
  return (
    <FluentProvider theme={webLightTheme}>
      <div style={{ padding: '2rem' }}>
        <h1>Aura Audit AI</h1>
        <p>Enterprise Audit Platform</p>
      </div>
    </FluentProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
