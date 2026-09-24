import React, { useState } from 'react';

function App() {
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    categoria: 'Vías Públicas'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Reclamo registrado con éxito en el sistema municipal.');
  };

  return (
    <div style={{ backgroundColor: '#121212', color: '#fff', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: 'sans-serif' }}>
      <div style={{ border: '1px solid #333', padding: '2rem', borderRadius: '8px', width: '400px', backgroundColor: '#1e1e1e' }}>
        <h2 style={{ textAlign: 'center', color: '#4CAF50', marginBottom: '0.5rem' }}>Municipalidad Provincial de Huancayo</h2>
        <h4 style={{ textAlign: 'center', color: '#ccc', marginTop: 0 }}>Gestión de Reclamos Vecinales (Green AI)</h4>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Título del Reclamo:</label>
            <input 
              type="text" 
              placeholder="Ej. Bache en Av. Real"
              value={formData.titulo}
              onChange={(e) => setFormData({...formData, titulo: e.target.value})}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#2a2a2a', color: '#fff' }}
              required 
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Descripción del Problema:</label>
            <textarea 
              rows="3"
              placeholder="Describa la incidencia..."
              value={formData.descripcion}
              onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#2a2a2a', color: '#fff' }}
              required 
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Categoría estimada:</label>
            <select 
              value={formData.categoria}
              onChange={(e) => setFormData({...formData, categoria: e.target.value})}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#2a2a2a', color: '#fff' }}
            >
              <option value="Vías Públicas">Vías Públicas / Obras</option>
              <option value="Limpieza Pública">Limpieza Pública y Basura</option>
              <option value="Parques y Jardines">Parques y Jardines</option>
              <option value="Alumbrado">Alumbrado e Infraestructura</option>
            </select>
          </div>

          <button type="submit" style={{ padding: '0.75rem', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', marginTop: '1rem' }}>
            Enviar Reclamo a la Mesa de Partes
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;