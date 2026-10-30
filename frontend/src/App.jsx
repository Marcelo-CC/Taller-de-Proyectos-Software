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

  // Paso 2: Datos del Reclamo (Categoría eliminada, ahora la maneja la IA)
  const [formData, setFormData] = useState({
    titulo: '',
    ubicacion: '',
    descripcion: ''
  });

  const [mostrarModal, setMostrarModal] = useState(false);
  const [cargando, setCargando] = useState(false);

  // Avanzar del Paso 1 al Paso 2
  const handleSiguiente = (e) => {
    e.preventDefault();
    if (!/^\d{8}$/.test(datosPersonales.dni)) {
      alert('El DNI debe tener exactamente 8 dígitos numéricos.');
      return;
    }
    if (!datosPersonales.nombre.trim() || !datosPersonales.direccion.trim()) {
      alert('Por favor complete su Nombre y Dirección antes de continuar.');
      return;
    }
    setPaso(2);
  };

  // Enviar el formulario consolidado al Backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setCargando(true);

    // Concatena los datos ingresados para que Gemini procese la anonimización e identificación
    const descripcionConsolidada = `Soy ${datosPersonales.nombre} con DNI ${datosPersonales.dni}, domiciliado en ${datosPersonales.direccion}. Ubicación del problema: ${formData.ubicacion}. Detalle del problema: ${formData.descripcion}`;

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://taller-de-proyectos-software.onrender.com';
      const response = await fetch(`${API_URL}/api/reclamos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          titulo: formData.titulo,
          descripcion: descripcionConsolidada
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
      ubicacion: '',
      descripcion: ''
    });
  };

  return (
    <div className="app-container">
      <div className="form-container">
        <h1>Municipalidad Provincial de Huancayo</h1>
        <h2>Gestión de Reclamos Vecinales (Green AI)</h2>

        {/* PASO 1: DATOS PERSONALES DEL CIUDADANO */}
        {paso === 1 && (
          <form onSubmit={handleSiguiente}>
            <h3 style={{ color: '#4CAF50', marginTop: 0, marginBottom: '1.2rem' }}>
              Paso 1: Datos del Ciudadano
            </h3>

            {/* Aviso de privacidad */}
            <p
              style={{
                color: '#ff6b6b',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                border: '1px solid #ff6b6b',
                borderRadius: '4px',
                padding: '0.6rem',
                fontSize: '0.85rem',
                margin: '0 0 1.2rem 0'
              }}
            >
              🔒 Sus datos personales son confidenciales: su DNI, nombre y domicilio se anonimizan
              automáticamente y no se guardan de forma visible en el sistema.
            </p>

            <div className="form-group">
              <label>DNI del Ciudadano:</label>
              <input
                type="text"
                inputMode="numeric"
                maxLength="8"
                pattern="\d{8}"
                title="El DNI debe tener exactamente 8 dígitos numéricos"
                value={datosPersonales.dni}
                onChange={(e) =>
                  // Solo números, máximo 8
                  setDatosPersonales({ ...datosPersonales, dni: e.target.value.replace(/\D/g, '').slice(0, 8) })
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
                  // Solo letras (con tildes y ñ), espacios, apóstrofo y guion
                  setDatosPersonales({
                    ...datosPersonales,
                    nombre: e.target.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'-]/g, '')
                  })
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

            {/* Ubicación del problema */}
            <div className="form-group">
              <label>Dirección Exacta del Lugar:</label>
              <input
                type="text"
                value={formData.ubicacion}
                onChange={(e) =>
                  setFormData({ ...formData, ubicacion: e.target.value })
                }
                placeholder="Ej. Jr. Arequipa cuadra 3, esquina con Av. Giráldez"
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
              🔒 Datos personales anonimizados y categorizados automáticamente mediante Gemini AI.
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