import React, { useState } from 'react';
import './App.css';

export default function App() {
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    categoria: 'Vías Públicas'
  });

  const [mostrarModal, setMostrarModal] = useState(false);
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCargando(true);

    try {
      const response = await fetch('http://localhost:8000/api/reclamos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setMostrarModal(true);
      } else {
        const errorData = await response.json();

        alert(
          'Error al guardar: ' +
            (errorData.detail || 'Error en servidor')
        );
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

        <h1>
          Municipalidad Provincial de Huancayo
        </h1>

        <h2>
          Gestión de Reclamos Vecinales (Green AI)
        </h2>

        <form onSubmit={handleSubmit}>

          {/* Título */}
          <div className="form-group">
            <label>
              Título del Reclamo:
            </label>

            <input
              type="text"
              value={formData.titulo}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  titulo: e.target.value
                })
              }
              placeholder="Ingrese el título del reclamo"
              required
            />
          </div>

          {/* Descripción */}
          <div className="form-group">
            <label>
              Descripción del Problema:
            </label>

            <textarea
              value={formData.descripcion}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  descripcion: e.target.value
                })
              }
              placeholder="Describa el problema con detalle"
              rows="5"
              required
            />
          </div>

          {/* Categoría */}
          <div className="form-group">
            <label>
              Categoría estimada:
            </label>

            <select
              value={formData.categoria}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  categoria: e.target.value
                })
              }
            >
              <option value="Vías Públicas">
                Vías Públicas / Obras
              </option>

              <option value="Limpieza Pública">
                Limpieza Pública y Basura
              </option>

              <option value="Parques y Jardines">
                Parques y Jardines
              </option>

              <option value="Alumbrado">
                Alumbrado e Infraestructura
              </option>
            </select>
          </div>

          {/* Botón */}
          <button
            type="submit"
            disabled={cargando}
            className="btn-submit"
          >
            {cargando
              ? 'Procesando con Green AI...'
              : 'Enviar Reclamo a la Mesa de Partes'}
          </button>

        </form>
      </div>

      {/* Modal */}
      {mostrarModal && (
        <div className="modal-overlay">

          <div className="modal-content">

            <div className="modal-icon">
              ✓
            </div>

            <h3>
              ¡Registro Exitoso!
            </h3>

            <p>
              Reclamo registrado con éxito en el sistema municipal
              y guardado en Supabase.
            </p>

            <button
              onClick={handleCerrarModal}
              className="btn-modal"
            >
              Aceptar
            </button>

          </div>

        </div>
      )}

    </div>
  );
}