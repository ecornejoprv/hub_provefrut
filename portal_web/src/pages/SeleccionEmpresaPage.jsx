import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const SeleccionEmpresaPage = () => {
    const [empresas, setEmpresas] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const empresasGuardadas = localStorage.getItem('empresas_disponibles');
        if (empresasGuardadas) {
            setEmpresas(JSON.parse(empresasGuardadas));
        } else {
            navigate('/login');
        }
    }, [navigate]);

    const handleLogout = () => {
        // Limpiamos todo para un cierre limpio
        localStorage.clear();
        navigate('/login');
    };

    const handleSeleccion = async (empresaId) => {
        setLoading(true);
        try {
            const tempToken = localStorage.getItem('temp_token');
            const data = await authService.selectEmpresa(empresaId, tempToken);
            
            localStorage.setItem('access_token', data.access_token);
            
            // 🔴 ANTES TENÍAS ESTO (ELIMÍNALO O COMÉNTALO):
            // localStorage.removeItem('temp_token');
            // localStorage.removeItem('empresas_disponibles');
            
            // ✅ AHORA SOLO NAVEGAMOS:
            navigate('/dashboard');

        } catch (error) {
            console.error("Error", error);
            alert("Error de acceso o sesión expirada.");
            navigate('/login'); // Si falla, ahí sí al login
        } finally {
            setLoading(false);
        }
    };

    const getEmpresaClass = (codigo) => {
        if (codigo === 'PVF') return 'provefrut-theme';
        if (codigo === 'NTG') return 'nintanga-theme';
        return '';
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
            {/* --- NUEVA BARRA SUPERIOR CON LOGOUT --- */}
            <nav style={{ background: '#fff', padding: '1rem 2rem', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 'bold', color: '#333' }}>Hub de Identidad</span>
                <button onClick={handleLogout} className="btn btn-danger btn-sm">Cerrar Sesión</button>
            </nav>

            <div className="container text-center" style={{ marginTop: '2rem' }}>
                <h1>Selecciona tu Espacio de Trabajo</h1>
                <p className="text-muted">Elige la empresa para cargar tus permisos.</p>
                
                {loading && <div className="alert alert-info">Generando accesos...</div>}

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
                    {empresas.map((empresa) => (
                        <div 
                            key={empresa.id} 
                            className={`card ${getEmpresaClass(empresa.codigo)}`}
                            style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                            onClick={() => handleSeleccion(empresa.id)}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <div className="card-body text-center">
                                <h3 style={{ color: 'var(--color-primary)', marginTop: 0 }}>{empresa.nombre}</h3>
                                <span className="badge" style={{ backgroundColor: '#eee', color: '#555' }}>{empresa.codigo}</span>
                                <div style={{ marginTop: '1rem' }}>
                                    <button className="btn btn-primary btn-sm">Acceder</button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default SeleccionEmpresaPage;