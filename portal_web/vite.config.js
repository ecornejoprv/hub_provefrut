import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // --- CONFIGURACIÓN DEL SERVIDOR DE DESARROLLO (npm run dev) ---
  server: {
    // Puerto donde correrá tu Frontend (opcional, por defecto es 5173)
    port: 5173,

    // --- EL PROXY REVERSO (La Magia) ---
    // Esto simula en tu PC lo que Nginx hará en producción.
    // Permite usar rutas relativas "/api/login" sin que falle por CORS.
    proxy: {
      '/api': {
        // A dónde debe ir la petición (Tu Django corriendo en otra terminal)
        // Nota: Si cambias el puerto de Django (ej. 8000), cámbialo aquí también.
        target: 'http://127.0.0.1:8080', 
        
        // Esto engaña al Backend haciéndole creer que la petición viene del mismo origen
        changeOrigin: true,
        
        // Si usaras HTTPS con certificados auto-firmados en local, esto evita errores
        secure: false, 
      }
    }
  },

  // --- CONFIGURACIÓN DE PREVISUALIZACIÓN (npm run preview) ---
  // Esto es para probar el build final antes de subirlo
  preview: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
      }
    }
  }
})