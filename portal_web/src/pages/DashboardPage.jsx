/**
 * DashboardPage.jsx
 * * Esta es la pantalla principal (Hub) del Portal Corporativo.
 * * Responsabilidades:
 * 1. Mostrar la identidad del usuario (Quién es y dónde está).
 * 2. Permitir cambiar de empresa (Contexto) dinámicamente.
 * 3. Mostrar el menú de módulos disponibles según los permisos del Token JWT.
 * 4. Actuar como "Lanzador" (Launcher) hacia otros sistemas (SSO).
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from "jwt-decode"; // Librería para leer los datos del token
import { authService } from '../services/api'; // Nuestro servicio de conexión al Backend 8080

const DashboardPage = () => {
    // Estado para guardar los datos decodificados del token (Usuario, Rol, Permisos)
    const [user, setUser] = useState(null);
    // Estado para la lista de empresas del dropdown
    const [empresas, setEmpresas] = useState([]);
    
    const navigate = useNavigate();

    // -----------------------------------------------------------------------
    // EFECTO DE CARGA INICIAL
    // -----------------------------------------------------------------------
    useEffect(() => {
        // 1. Recuperar el Token Principal ("Pasaporte")
        const token = localStorage.getItem('access_token');
        // 2. Recuperar la lista de empresas (que guardamos al hacer login)
        const listaEmpresas = localStorage.getItem('empresas_disponibles');

        // Seguridad básica: Si no hay token, mandar al login
        if (!token) { navigate('/login'); return; }

        try {
            // 3. Decodificar el Token para leer los datos sin ir al backend
            const decoded = jwtDecode(token);
            setUser(decoded);
            
            // Cargar el combo de empresas
            if (listaEmpresas) {
                setEmpresas(JSON.parse(listaEmpresas));
            }

            // LOG PARA DESARROLLADORES (F12)
            console.log("===== SESIÓN ACTIVA =====");
            console.log("Usuario:", decoded.nombre_completo);
            console.log("Empresa:", decoded.empresa_nombre);
            console.log("Permisos:", decoded.permisos);
            console.log("=========================");

        } catch (error) {
            console.error("Error leyendo token:", error);
            navigate('/login');
        }
    }, [navigate]);

    // -----------------------------------------------------------------------
    // FUNCIÓN: CAMBIO DE EMPRESA (Context Switching)
    // -----------------------------------------------------------------------
    const handleCambioEmpresa = async (event) => {
        const nuevaEmpresaId = event.target.value;
        
        // Necesitamos el token temporal (identidad base) para pedir un nuevo pasaporte
        const tempToken = localStorage.getItem('temp_token'); 

        if (!tempToken) {
            alert("Tu sesión base ha expirado. Por favor inicia sesión nuevamente.");
            navigate('/login');
            return;
        }

        try {
            // 1. Pedimos al Backend (8080) el nuevo token para la nueva empresa
            const data = await authService.selectEmpresa(nuevaEmpresaId, tempToken);
            
            // 2. Reemplazamos el token viejo por el nuevo en el navegador
            localStorage.setItem('access_token', data.access_token);
            
            // 3. Actualizamos el estado de React para que la pantalla cambie instantáneamente
            // (Colores, Nombre de empresa, Permisos nuevos)
            const decoded = jwtDecode(data.access_token);
            setUser(decoded);

        } catch (error) {
            console.error("Error cambiando empresa", error);
            alert("No tienes acceso a la empresa seleccionada.");
        }
    };

    // -----------------------------------------------------------------------
    // FUNCIÓN: SINGLE SIGN-ON (SSO) -> SALTO A OTRO FRONTEND
    // -----------------------------------------------------------------------
    const lanzarModuloComprasExterno = () => {
        // 1. Obtenemos el token actual
        const token = localStorage.getItem('access_token');
        
        // 2. Definimos la dirección del OTRO proyecto React (El que creaste en la carpeta aparte)
        // Asegúrate de que el otro proyecto esté corriendo en este puerto.
        const urlFrontendCompras = 'http://localhost:5174'; 
        
        // 3. Redirección total del navegador enviando el token en la URL
        // Esto hace que "salgas" de esta app y entres a la otra.
        window.location.href = `${urlFrontendCompras}/sso?token=${token}`;
    };

    const handleLogout = () => {
        localStorage.clear(); // Borrar todo rastro
        navigate('/login');
    };

    // -----------------------------------------------------------------------
    // FUNCIÓN: LANZAR CHATBOT (SSO)
    // -----------------------------------------------------------------------
    const lanzarChatbotExterno = () => {
        // 1. Obtener tu pasaporte actual
        const token = localStorage.getItem('access_token');
        
        // 2. Definir la dirección del Frontend de tu compañero
        // Puerto o dominio que corre el React del Chatbot"
        const url = import.meta.env.VITE_URL_CHATBOT || 'http://172.20.8.97:5000';
        
        // 3. Redirección con Token
        window.location.href = `${url}/sso-login?token=${token}`;
    };

    // Renderizado condicional: Si no hay usuario cargado, mostrar espera
    if (!user) return <div className="p-5 text-center text-muted">Verificando credenciales...</div>;

    // Helper para verificar permisos en el JSX más limpio
    const tienePermiso = (permiso) => user.permisos && user.permisos.includes(permiso);

    // Función estética para cambiar el color del navbar según la empresa
    const getNavbarColor = (codigo) => {
        if (codigo === 'PVF') return '#285d2f'; // Verde Provefrut
        if (codigo === 'NTG') return '#712d7d'; // Morado Nintanga
        if (codigo === 'PCG') return '#0056b3'; // Azul Procongelados
        return '#333'; // Gris por defecto
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f0f2f5', fontFamily: 'sans-serif' }}>
            
            {/* ================= NAVBAR SUPERIOR ================= */}
            <nav style={{ 
                backgroundColor: getNavbarColor(user.empresa_codigo), 
                color: 'white', 
                padding: '0.8rem 2rem',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                transition: 'background-color 0.5s ease' // Efecto suave al cambiar empresa
            }}>
                {/* SECCIÓN IZQUIERDA: Título y Selector */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <h2 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 600 }}>Portal Corporativo</h2>
                    
                    {/* SELECTOR DE EMPRESA INTELIGENTE */}
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <label style={{ fontSize: '0.7rem', opacity: 0.8, marginBottom: '2px' }}>ESPACIO DE TRABAJO</label>
                        <select 
                            value={user.empresa_id} 
                            onChange={handleCambioEmpresa}
                            style={{
                                padding: '0.4rem', borderRadius: '4px', border: 'none',
                                fontWeight: 'bold', color: '#333', cursor: 'pointer', outline: 'none'
                            }}
                        >
                            {empresas.map(emp => (
                                <option key={emp.id} value={emp.id}>
                                    {emp.nombre}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
                
                {/* SECCIÓN DERECHA: Perfil y Salir */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ textAlign: 'right', lineHeight: '1.2' }}>
                        <div style={{ fontSize: '1rem', fontWeight: 'bold' }}>
                            {user.nombre_completo || user.username}
                        </div>
                        <div style={{ fontSize: '0.75rem', opacity: 0.9, background: 'rgba(255,255,255,0.2)', padding: '2px 6px', borderRadius: '4px', display: 'inline-block' }}>
                            {user.rol_nombre}
                        </div>
                    </div>
                    <button 
                        onClick={handleLogout} 
                        className="btn"
                        style={{ backgroundColor: '#dc3545', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        Salir
                    </button>
                </div>
            </nav>

            {/* ================= GRID DE MÓDULOS ================= */}
            <div className="container" style={{ maxWidth: '1000px', margin: '2rem auto', padding: '0 1rem' }}>
                
                <h3 className="mb-3" style={{ color: '#444', borderBottom: '2px solid #ddd', paddingBottom: '0.5rem' }}>
                    Aplicaciones Disponibles
                </h3>
                
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
                    gap: '2rem' 
                }}>
                    
                    {/* --- TARJETA 1: COMPRAS (SATÉLITE EXTERNO) --- */}
                    {tienePermiso('core.compras_acceso') ? (
                         <div className="card" style={{ background: 'white', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', padding: '2rem', textAlign: 'center', transition: 'transform 0.2s' }}>
                            <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>🛒</div>
                            <h4 style={{ color: getNavbarColor(user.empresa_codigo), margin: '0 0 0.5rem 0' }}>Compras</h4>
                            <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '1.5rem' }}>Gestión de órdenes y proveedores.</p>
                            
                            {/* BOTÓN QUE LANZA EL SSO AL OTRO FRONTEND */}
                            <button 
                                onClick={lanzarModuloComprasExterno} 
                                style={{ 
                                    width: '100%', padding: '0.7rem', 
                                    background: getNavbarColor(user.empresa_codigo), 
                                    color: 'white', border: 'none', borderRadius: '6px', 
                                    cursor: 'pointer', fontWeight: 'bold' 
                                }}
                            >
                                Abrir Aplicación ↗
                            </button>
                         </div>
                    ) : (
                        // ESTADO BLOQUEADO
                        <div className="card" style={{ background: '#e9ecef', borderRadius: '8px', padding: '2rem', textAlign: 'center', opacity: 0.6 }}>
                            <div style={{ fontSize: '3.5rem', marginBottom: '1rem', filter: 'grayscale(100%)' }}>🔒</div>
                            <h4 style={{ color: '#777', margin: '0 0 0.5rem 0' }}>Compras</h4>
                            <p style={{ color: '#888', fontSize: '0.8rem' }}>No tienes acceso a este módulo en {user.empresa_codigo}.</p>
                        </div>
                    )}

                    {/* --- TARJETA 2: INVENTARIO (EJEMPLO INTERNO) --- */}
                    {tienePermiso('core.inventario_acceso') ? (
                        <div className="card" style={{ background: 'white', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', padding: '2rem', textAlign: 'center' }}>
                            <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>📦</div>
                            <h4 style={{ color: getNavbarColor(user.empresa_codigo), margin: '0 0 0.5rem 0' }}>Inventario</h4>
                            <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '1.5rem' }}>Control de kardex y bodegas.</p>
                            <button disabled style={{ width: '100%', padding: '0.7rem', background: '#ccc', color: 'white', border: 'none', borderRadius: '6px', cursor: 'not-allowed' }}>
                                Próximamente
                            </button>
                        </div>
                    ) : (
                        <div className="card" style={{ background: '#e9ecef', borderRadius: '8px', padding: '2rem', textAlign: 'center', opacity: 0.6 }}>
                            <div style={{ fontSize: '3.5rem', marginBottom: '1rem', filter: 'grayscale(100%)' }}>🔒</div>
                            <h4 style={{ color: '#777', margin: '0 0 0.5rem 0' }}>Inventario</h4>
                            <p style={{ color: '#888', fontSize: '0.8rem' }}>Acceso restringido.</p>
                        </div>
                    )}

                    {/* --- TARJETA 3: CHATBOT (EJEMPLO) --- */}
                    {tienePermiso('core.chatbot_acceso') && (
                        <div className="card" style={{ background: 'white', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', padding: '2rem', textAlign: 'center' }}>
                            <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>🤖</div>
                            <h4 style={{ color: getNavbarColor(user.empresa_codigo), margin: '0 0 0.5rem 0' }}>Asistente IA</h4>
                            <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '1.5rem' }}>Consultas inteligentes.</p>
                            <button 
                                onClick={lanzarChatbotExterno} 
                                style={{ 
                                    width: '100%', 
                                    padding: '0.7rem', 
                                    background: '#6c757d', 
                                    color: 'white', 
                                    border: 'none', 
                                    borderRadius: '6px', 
                                    cursor: 'pointer' 
                                }}>
                                Iniciar Chat
                            </button>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default DashboardPage;