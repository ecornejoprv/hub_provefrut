import React, { useState } from 'react';
import { authService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import '../styles/AuthPages.css';
import '../styles/LoginNew.css'; // Para el ojito

const ForcePasswordChangePage = () => {
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [showPass, setShowPass] = useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState(''); // <--- NUEVO ESTADO
    
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirm) {
            setError("Las contraseñas no coinciden.");
            return;
        }
        if (password.length < 8) {
            setError("La contraseña debe tener al menos 8 caracteres.");
            return;
        }

        setLoading(true);
        try {
            await authService.cambiarPasswordObligatorio(password);
            
            // 1. Limpieza de seguridad
            localStorage.clear();
            
            // 2. En lugar de alert(), mostramos mensaje en pantalla
            setSuccessMessage("Contraseña establecida correctamente. Redirigiendo al inicio de sesión...");
            
            // 3. Redirección automática después de 3 segundos
            setTimeout(() => {
                navigate('/login');
            }, 3000);

        } catch (err) {
            setError("Error al actualizar la contraseña. Intenta nuevamente.");
            setLoading(false); // Solo quitamos loading si falló
        } 
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                
                {/* --- HEADER --- */}
                <div className="auth-header">
                    <div className="auth-icon-wrapper" style={{ backgroundColor: '#fff7ed', color: '#ea580c' }}>
                        🛡️
                    </div>
                    <h1 className="auth-title">Seguridad Corporativa</h1>
                    
                    {/* Ocultamos el subtítulo si ya hubo éxito para limpiar visualmente */}
                    {!successMessage && (
                        <p className="auth-subtitle">
                            Es tu primer inicio de sesión o tu clave ha expirado. 
                            <strong>Debes establecer una nueva contraseña.</strong>
                        </p>
                    )}
                </div>

                {/* --- ESTADO DE ÉXITO (Reemplaza al formulario) --- */}
                {successMessage ? (
                    <div className="auth-alert success" style={{ textAlign: 'center', flexDirection: 'column', padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
                        <h3 style={{ margin: '0 0 10px 0', color: '#166534' }}>¡Cambio Exitoso!</h3>
                        <p style={{ margin: 0 }}>{successMessage}</p>
                        <div className="spinner-sm" style={{ borderTopColor: '#166534', marginTop: '1.5rem' }}></div>
                    </div>
                ) : (
                    /* --- FORMULARIO NORMAL --- */
                    <form onSubmit={handleSubmit} className="auth-form">
                        
                        {error && <div className="auth-alert error">⚠️ {error}</div>}

                        <div className="form-field">
                            <label>Nueva Contraseña</label>
                            <div className="password-wrapper">
                                <input 
                                    type={showPass ? "text" : "password"}
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    required
                                    minLength={8}
                                    placeholder="••••••••"
                                    disabled={loading}
                                />
                                <button 
                                    type="button" 
                                    className="btn-eye" 
                                    onClick={() => setShowPass(!showPass)}
                                    title={showPass ? "Ocultar" : "Mostrar"}
                                >
                                    {showPass ? (
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                    ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                                        </svg>
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className="form-field">
                            <label>Confirmar Nueva Contraseña</label>
                            <div className="password-wrapper">
                                <input 
                                    type={showPass ? "text" : "password"}
                                    value={confirm}
                                    onChange={e => setConfirm(e.target.value)}
                                    required
                                    placeholder="••••••••"
                                    disabled={loading}
                                />
                            </div>
                        </div>
                        
                        <button 
                            type="submit" 
                            className="btn-auth" 
                            disabled={loading}
                            style={{ backgroundColor: '#ea580c' }} 
                        >
                            {loading ? <span className="spinner-sm"></span> : 'Establecer Contraseña y Entrar'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default ForcePasswordChangePage;