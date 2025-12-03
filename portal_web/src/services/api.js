import axios from 'axios';

// 1. Configuración Base
const api = axios.create({
    baseURL: '/api/', 
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
        // Si todo sale bien (Status 200-299), pasamos la respuesta limpia
        return response;
    },
    (error) => {
        // Si el servidor responde con error
        if (error.response && error.response.status === 401) {
            console.warn("⚠️ Acceso Denegado o Sesión Expirada (401)");

            // EVITAR BUCLE INFINITO:
            // Si ya estamos en el login, no intentamos redirigir de nuevo
            if (!window.location.pathname.includes('/login')) {
                // 1. Limpiamos basura
                localStorage.clear();
                
                // 2. Redirección forzosa al Login
                // Usamos window.location en lugar de navigate para asegurar un reset total de memoria
                window.location.href = '/login';
            }
        }
        
        // Rechazamos la promesa para que el componente sepa que hubo error (y muestre alertas si quiere)
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