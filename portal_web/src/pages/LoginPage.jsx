import React, { useState, useEffect } from 'react';
import { authService } from '../services/api'; // Importamos el servicio de API
import { useNavigate, useSearchParams } from 'react-router-dom'; // useSearchParams es nuevo

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    
    const navigate = useNavigate();
    const [searchParams] = useSearchParams(); // Para leer ?action=logout de la URL

    // --- EFECTO: DETECTOR DE LOGOUT GLOBAL ---
    // Este efecto se ejecuta apenas carga la página de Login.
    // Si venimos de un satélite (ej. Compras) que nos mandó a /login?action=logout,
    // aquí es donde limpiamos la basura restante del Hub.
    useEffect(() => {
        if (searchParams.get('action') === 'logout') {
            console.log("🔄 Ejecutando limpieza por Logout Global...");
            localStorage.clear(); // Borra tokens, listas de empresas, todo.
            setError('Sesión cerrada correctamente.'); // Feedback visual opcional
        }
    }, [searchParams]);

    // --- FUNCIÓN DE LOGIN ---
    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        try {
            // 1. Petición de Login Inicial (Credenciales)
            const data = await authService.login(username, password);
            
            // 2. Guardamos los datos temporales (Identidad base)
            localStorage.setItem('temp_token', data.access);
            localStorage.setItem('empresas_disponibles', JSON.stringify(data.empresas_disponibles));

            // 3. LÓGICA DE AUTO-ENTRADA (Mejora UX)
            // En lugar de preguntar a qué empresa quiere entrar,
            // elegimos la primera de la lista automáticamente.
            if (data.empresas_disponibles.length > 0) {
                const empresaPorDefecto = data.empresas_disponibles[0];
                
                // 4. Canjeamos el Token Temporal por el Pasaporte Universal inmediatamente
                const tokenData = await authService.selectEmpresa(empresaPorDefecto.id, data.access);
                
                // 5. Guardamos el Pasaporte Final
                localStorage.setItem('access_token', tokenData.access_token);
                
                // 6. Redirigimos al Dashboard principal
                navigate('/dashboard');
            } else {
                // Caso raro: Usuario existe pero no tiene empresas asignadas en Pertenencia
                setError('Tu usuario no tiene ninguna empresa asignada. Contacta a Sistemas.');
                localStorage.clear();
            }

        } catch (err) {
            console.error("Error login:", err);
            // Manejo básico de errores (401 = Credenciales malas)
            if (err.response && err.response.status === 401) {
                setError('Usuario o contraseña incorrectos.');
            } else {
                setError('Error de conexión con el servidor.');
            }
        }
    };

    return (
        <div style={{ 
            minHeight: '100vh', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            backgroundColor: '#f0f2f5' 
        }}>
            <div className="card" style={{ width: '100%', maxWidth: '400px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                
                <div className="card-header text-center" style={{ background: '#fff', borderBottom: '1px solid #eee', padding: '1.5rem' }}>
                    <h3 style={{ margin: 0, color: '#333' }}>Hub de Identidad</h3>
                    <small className="text-muted">Acceso Corporativo Unificado</small>
                </div>
                
                <div className="card-body" style={{ padding: '2rem' }}>
                    {error && (
                        <div className="alert alert-danger" style={{ fontSize: '0.9rem' }}>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleLogin}>
                        <div className="form-group mb-3">
                            <label className="form-label">Usuario</label>
                            <input 
                                type="text" 
                                className="form-control" 
                                placeholder="ej. edwin.arias"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                autoFocus
                                required
                            />
                        </div>

                        <div className="form-group mb-4">
                            <label className="form-label">Contraseña</label>
                            <input 
                                type="password" 
                                className="form-control" 
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <button 
                            type="submit" 
                            className="btn btn-primary" 
                            style={{ width: '100%', padding: '0.8rem', fontWeight: 'bold' }}
                        >
                            Iniciar Sesión
                        </button>
                    </form>
                </div>
                
                <div className="card-footer text-center" style={{ background: '#f8f9fa', padding: '1rem', fontSize: '0.8rem', color: '#666' }}>
                    Provefrut S.A. - Departamento de Sistemas
                </div>
            </div>
        </div>
    );
};

export default LoginPage;