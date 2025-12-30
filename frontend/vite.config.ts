import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(() => {
  return {
    plugins: [react()],
    // Dev server proxy: forward API requests to the backend running on port
    // 5001. This allows the frontend to use a relative /api/v1 path in
    // development while the backend runs on a separate port.
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:5001',
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
