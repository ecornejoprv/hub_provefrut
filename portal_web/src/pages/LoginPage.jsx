import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import '../styles/LoginNew.css';
import logosWhite from '../assets/images/logos-grupo-white.png'; 
import isotipoColor from '../assets/images/isotipoPV.png';

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            navigate('/dashboard', { replace: true });
        }
    }, [navigate]);

    const [searchParams] = useSearchParams();

    useEffect(() => {
        if (searchParams.get('action') === 'logout') localStorage.clear();
    }, [searchParams]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            const data = await authService.login(username, password);
            if (data.debe_cambiar_password) {
                localStorage.setItem('access_token', data.access); 
                navigate('/force-password-change');
                return;
            }
            localStorage.setItem('temp_token', data.access);
            localStorage.setItem('empresas_disponibles', JSON.stringify(data.empresas_disponibles));
            if (data.empresas_disponibles.length > 0) {
                const empresaPorDefecto = data.empresas_disponibles[0];
                const tokenData = await authService.selectEmpresa(empresaPorDefecto.id, data.access);
                localStorage.setItem('access_token', tokenData.access_token);
                navigate('/dashboard');
            } else {
                setError('Usuario sin asignación. Contacte a sistemas.');
                localStorage.clear();
            }
        } catch (err) {
            if (err.response && err.response.status === 401) setError('Credenciales incorrectas.');
            else setError('Error de conexión.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-layout">
            
            {/* IZQUIERDA: VISUAL & BRANDING */}
            <div className="login-visual-section">
                <div className="visual-overlay">
                    <div className="visual-content">
                        <span className="visual-tag">SISTEMA INTEGRADO DE GESTIÓN</span>
                        <h1 className="visual-title">Hub Corporativo</h1>
                        <div className="visual-divider"></div>
                        {/*}
                        <p className="visual-text">
                            Acceso unificado a las herramientas de gestión para Provefrut, Nintanga y Procongelados.
                        </p>
                        */}
                    </div>
                    
                    {/* Aquí van los logos blancos, limpios, al pie */}
                    <div className="visual-footer">
                        <img src={logosWhite} alt="Grupo Corporativo" className="logos-group-img" />
                    </div>
                </div>
            </div>

            {/* DERECHA: FORMULARIO */}
            <div className="login-form-section">
                <div className="form-container">
                    <div className="form-header">                        
                        <img src={isotipoColor} alt="Icono" className="form-logo-icon" /> 
                        <h2>Iniciar Sesión</h2>
                        <p>Ingrese sus credenciales para acceder.</p>
                    </div>

                    {error && (
                        <div className="login-alert">
                            <i className="alert-icon">!</i> {error}
                        </div>
                    )}

                    <form onSubmit={handleLogin} className="modern-form">
                        <div className="input-group">
                            <label>Usuario</label>
                            <input 
                                type="text" 
                                placeholder="nombre.apellido"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                disabled={isLoading}
                                autoFocus
                            />
                        </div>

                        <div className="input-group">
                            <label>Contraseña</label>
                            <div className="password-wrapper">
                                <input 
                                    type={showPassword ? "text" : "password"} // Dinámico
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={isLoading}
                                />
                                <button 
                                    type="button" // Importante para no enviar el form
                                    className="btn-eye"
                                    onClick={() => setShowPassword(!showPassword)}
                                    title={showPassword ? "Ocultar" : "Mostrar"}
                                >
                                    {showPassword ? (
                                        // Icono Ojo Abierto
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                    ) : (
                                        // Icono Ojo Cerrado (Tachado)
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                                        </svg>
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className="form-extras">
                            <Link to="/forgot-password" className="link-reset">¿Olvidaste tu contraseña?</Link>
                        </div>

                        <button type="submit" className="btn-submit" disabled={isLoading}>
                            {isLoading ? <span className="spinner"></span> : 'Acceder'}
                        </button>
                    </form>
                    
                    <div className="form-footer-mobile">
                        {/* Solo visible en móvil si la imagen no carga */}
                        <small>© Grupo Provefrut S.A.</small>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;