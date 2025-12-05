import axios from 'axios';

// =================================================================
// 0. CONFIGURACIÓN DINÁMICA DE URL
// =================================================================
// ESTRATEGIA:
// 1. En Producción (Amplify): Usará la variable VITE_API_URL que configuraremos en la consola.
// 2. En Local: Usará '/api/' para que el Proxy de Vite (vite.config.js) maneje la redirección a tu backend local.
const baseURL = import.meta.env.VITE_API_URL || '/api/';

console.log("🚀 Conectando a API en:", baseURL); // Log para depuración en consola del navegador

// 1. Configuración Base de Axios
const api = axios.create({
    baseURL: baseURL, 
    headers: {
        'Content-Type': 'application/json',
    }
});

// =================================================================
// INTERCEPTOR DE SOLICITUD (Salida) -> Inyecta el Token
// =================================================================
api.interceptors.request.use(
    (config) => {
        const storedToken = localStorage.getItem('access_token');
        
        // Si hay token y la petición no tiene uno manual, lo inyectamos
        if (storedToken && !config.headers['Authorization']) {
            config.headers['Authorization'] = `Bearer ${storedToken}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// =================================================================
// INTERCEPTOR DE RESPUESTA (Entrada) -> Maneja Errores 401
// =================================================================
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Si el servidor responde con error 401 (No autorizado)
        if (error.response && error.response.status === 401) {
            console.warn("⚠️ Acceso Denegado o Sesión Expirada (401)");

            // Evitar bucle infinito si ya estamos en login
            if (!window.location.pathname.includes('/login')) {
                localStorage.clear();
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

// =================================================================
// SERVICIOS DE AUTENTICACIÓN
// =================================================================
export const authService = {
    login: async (username, password) => {
        const response = await api.post('login/', { username, password });
        return response.data;
    },

    selectEmpresa: async (empresa_id, token_temporal) => {
        if (!token_temporal) throw new Error("Token temporal perdido");
        
        const response = await api.post('select-empresa/', 
            { empresa_id }, 
            { headers: { 'Authorization': `Bearer ${token_temporal}` } }
        );
        return response.data;
    },

    requestPasswordReset: async (email) => {
        const response = await api.post('password-reset/', { email });
        return response.data;
    },

    confirmPasswordReset: async (uidb64, token, password) => {
        const response = await api.post('password-reset-confirm/', {
            uidb64,
            token,
            password
        });
        return response.data;
    },

    cambiarPasswordObligatorio: async (password) => {
        const response = await api.post('cambiar-password-obligatorio/', { password });
        return response.data;
    }
};

export default api;