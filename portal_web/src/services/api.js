import axios from 'axios';

// 1. Configuración Base
// Apuntamos al puerto 8080 donde corre tu Django
const api = axios.create({
    //baseURL: 'http://127.0.0.1:8080/api/',
    //baseURL: 'http://172.20.0.101:8080/api/',
    baseURL: '/api/',
    headers: {
        'Content-Type': 'application/json',
    }
});

// 2. Interceptor de Peticiones (El que pega el token)
api.interceptors.request.use(
    (config) => {
        // Buscamos si existe un "Pasaporte Universal" guardado
        const token = localStorage.getItem('access_token');
        
        // Si existe, lo pegamos en la cabecera Authorization
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 3. Funciones de Autenticación (Los endpoints que creamos en Django)
export const authService = {
    // Paso 1: Login inicial (Usuario/Clave) -> Devuelve Token temporal + Empresas
    login: async (username, password) => {
        const response = await api.post('login/', { username, password });
        return response.data;
    },

    // Paso 2: Selección de Empresa -> Devuelve Pasaporte Universal
    selectEmpresa: async (empresa_id, token_temporal) => {
        // Aquí necesitamos enviar el token temporal explícitamente
        // porque aún no lo hemos guardado como "oficial"
        const response = await api.post('select-empresa/', 
            { empresa_id }, 
            { 
                headers: { Authorization: `Bearer ${token_temporal}` } 
            }
        );
        return response.data;
    }
};

export default api;