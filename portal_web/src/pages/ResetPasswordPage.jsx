import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/AuthPages.css';
// Importamos también el CSS del login porque ahí definimos .password-wrapper y .btn-eye
import '../styles/LoginNew.css'; 

const ResetPasswordPage = () => {
    const { uid, token } = useParams();
    const navigate = useNavigate();

    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPass, setShowPass] = useState(false); // Estado para el ojito
    
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Limpieza de seguridad al entrar (Borrar tokens viejos)
    useEffect(() => {
        localStorage.clear();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        if (password !== confirmPassword) {
            setError('Las contraseñas no coinciden.');
            return;
        }
        if (password.length < 8) {
            setError('La contraseña debe tener al menos 8 caracteres.');
            return;
        }

        setLoading(true);
        try {
            await authService.confirmPasswordReset(uid, token, password);
            setMessage('¡Contraseña actualizada exitosamente!');
            // Redirigir al login
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setError('El enlace es inválido o ha expirado. Por favor solicita uno nuevo.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <div className="auth-icon-wrapper">🔒</div>
                    <h1 className="auth-title">Nueva Contraseña</h1>
                    <p className="auth-subtitle">
                        Crea una contraseña segura para tu cuenta.
                    </p>
                </div>

                {message ? (
                    <div className="auth-alert success" style={{ textAlign: 'center', flexDirection: 'column' }}>
                        <h3 style={{ margin: '0 0 10px 0' }}>¡Todo listo! 🎉</h3>
                        <p>{message}</p>
                        <small>Redirigiendo al inicio de sesión...</small>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="auth-form">
                        {error && <div className="auth-alert error">⚠️ {error}</div>}
                        
                        {/* CAMPO: NUEVA CONTRASEÑA */}
                        <div className="form-field">
                            <label>Nueva Contraseña</label>
                            <div className="password-wrapper">
                                <input 
                                    type={showPass ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required 
                                    minLength={8}
                                    placeholder="Mínimo 8 caracteres"
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

                        {/* CAMPO: CONFIRMAR CONTRASEÑA */}
                        <div className="form-field">
                            <label>Confirmar Contraseña</label>
                            <div className="password-wrapper">
                                <input 
                                    type={showPass ? "text" : "password"}
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required 
                                    placeholder="Repite la contraseña"
                                />
                                {/* No ponemos botón aquí porque el de arriba controla ambos */}
                            </div>
                        </div>

                        <button type="submit" className="btn-auth" disabled={loading}>
                            {loading ? <span className="spinner-sm"></span> : 'Actualizar Contraseña'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default ResetPasswordPage;