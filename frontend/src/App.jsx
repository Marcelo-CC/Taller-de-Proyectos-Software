import React, { useState } from 'react';
import './App.css';

export default function App() {
  // Estado para controlar la pantalla actual (1 = Datos Personales, 2 = Detalle del Reclamo)
  const [paso, setPaso] = useState(1);

  // Paso 1: Datos Personales
  const [datosPersonales, setDatosPersonales] = useState({
    dni: '',
    nombre: '',
    direccion: ''
  });

  // Paso 2: Datos del Reclamo
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    categoria: 'Vías Públicas'
  });

  const [mostrarModal, setMostrarModal] = useState(false);
  const [cargando, setCargando] = useState(false);

  // Avanzar del Paso 1 al Paso 2
  const handleSiguiente = (e) => {
    e.preventDefault();
    if (!datosPersonales.dni || !datosPersonales.nombre) {
      alert('Por favor complete su DNI y Nombre antes de continuar.');
      return;
    }
    setPaso(2);
  };

  // Enviar el formulario consolidado al Backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setCargando(true);

    // Concatena los datos ingresados para que el backend anonimice el texto en la Capa de Dominio
    const descripcionConsolidada = `Soy ${datosPersonales.nombre} con DNI ${datosPersonales.dni}, domiciliado en ${datosPersonales.direccion}. Detalle del problema: ${formData.descripcion}`;

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://taller-de-proyectos-software.onrender.com';
      const response = await fetch(`${API_URL}/api/reclamos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          titulo: formData.titulo,
          descripcion: descripcionConsolidada,
          categoria: formData.categoria
        })
      });

      if (response.ok) {
        setMostrarModal(true);
      } else {
        const errorData = await response.json();
        alert('Error al guardar: ' + (errorData.detail || 'Error en servidor'));
      }
    } catch (error) {
      console.error('Error de red:', error);
      alert('No se pudo conectar con el servidor backend.');
    } finally {
      setCargando(false);
    }
  };

  const handleCerrarModal = () => {
    setMostrarModal(false);
    setPaso(1);
    setDatosPersonales({
      dni: '',
      nombre: '',
      direccion: ''
    });
    setFormData({
      titulo: '',
      descripcion: '',
      categoria: 'Vías Públicas'
    });
  };

  return (
    <div className="app-container">
      {/* Contenedor principal */}
      <div className="form-container">
        <h1>Municipalidad Provincial de Huancayo</h1>
        <h2>Gestión de Reclamos Vecinales (Green AI)</h2>

        {/* PASO 1: DATOS PERSONALES DEL CIUDADANO */}
        {paso === 1 && (
          <form onSubmit={handleSiguiente}>
            <h3 style={{ color: '#4CAF50', marginTop: 0, marginBottom: '1.2rem' }}>
              Paso 1: Datos del Ciudadano
            </h3>

            <div className="form-group">
              <label>DNI del Ciudadano:</label>
              <input
                type="text"
                maxLength="8"
                value={datosPersonales.dni}
                onChange={(e) =>
                  setDatosPersonales({ ...datosPersonales, dni: e.target.value })
                }
                placeholder="Ingrese DNI (8 dígitos)"
                required
              />
            </div>

            <div className="form-group">
              <label>Nombres y Apellidos:</label>
              <input
                type="text"
                value={datosPersonales.nombre}
                onChange={(e) =>
                  setDatosPersonales({ ...datosPersonales, nombre: e.target.value })
                }
                placeholder="Ej. Juan Pérez"
                required
              />
            </div>

            <div className="form-group">
              <label>Dirección / Domicilio:</label>
              <input
                type="text"
                value={datosPersonales.direccion}
                onChange={(e) =>
                  setDatosPersonales({ ...datosPersonales, direccion: e.target.value })
                }
                placeholder="Ej. Av. Giráldez 123"
                required
              />
            </div>

            <button type="submit" className="btn-submit">
              Siguiente Paso ➔
            </button>
          </form>
        )}

        {/* PASO 2: DETALLE DEL RECLAMO VECINAL */}
        {paso === 2 && (
          <form onSubmit={handleSubmit}>
            <h3 style={{ color: '#4CAF50', marginTop: 0, marginBottom: '1.2rem' }}>
              Paso 2: Registro del Reclamo
            </h3>

            {/* Título */}
            <div className="form-group">
              <label>Título del Reclamo:</label>
              <input
                type="text"
                value={formData.titulo}
                onChange={(e) =>
                  setFormData({ ...formData, titulo: e.target.value })
                }
                placeholder="Ingrese el título del reclamo"
                required
              />
            </div>

            {/* Descripción */}
            <div className="form-group">
              <label>Descripción del Problema:</label>
              <textarea
                value={formData.descripcion}
                onChange={(e) =>
                  setFormData({ ...formData, descripcion: e.target.value })
                }
                placeholder="Describa el problema con detalle"
                rows="5"
                required
              />
            </div>

            {/* Categoría */}
            <div className="form-group">
              <label>Categoría estimada:</label>
              <select
                value={formData.categoria}
                onChange={(e) =>
                  setFormData({ ...formData, categoria: e.target.value })
                }
              >
                <option value="Vías Públicas">Vías Públicas / Obras</option>
                <option value="Limpieza Pública">Limpieza Pública y Basura</option>
                <option value="Parques y Jardines">Parques y Jardines</option>
                <option value="Alumbrado">Alumbrado e Infraestructura</option>
              </select>
            </div>

            {/* Botones de navegación */}
            <div style={{ display: 'flex', gap: '10px', marginTop: '1rem' }}>
              <button
                type="button"
                onClick={() => setPaso(1)}
                style={{
                  width: '30%',
                  padding: '0.75rem',
                  backgroundColor: '#444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                ⬅ Regresar
              </button>

              <button
                type="submit"
                disabled={cargando}
                className="btn-submit"
                style={{ width: '70%', marginTop: 0 }}
              >
                {cargando
                  ? 'Procesando con Green AI...'
                  : 'Enviar Reclamo a la Mesa de Partes'}
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Modal de éxito */}
      {mostrarModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-icon">✓</div>
            <h3>¡Registro Exitoso!</h3>
            <p>
              Reclamo registrado con éxito en el sistema municipal y guardado en Supabase.
            </p>
            <p style={{ fontSize: '0.8rem', color: '#4CAF50', margin: '0.5rem 0 1.2rem 0' }}>
              🔒 Datos de identificación personal anonimizados en la Base de Datos.
            </p>
            <button onClick={handleCerrarModal} className="btn-modal">
              Aceptar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}