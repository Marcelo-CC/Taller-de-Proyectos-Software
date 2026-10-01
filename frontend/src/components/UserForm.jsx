import { useState } from 'react';
import api from '../services/api';

export function UserForm() {
  const [formData, setFormData] = useState({ nombre: '', email: '' });
  const [loading, setLoading] = useState(false);
  const [responseMsg, setResponseMsg] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponseMsg('');

    try {
      const response = await api.post('/users', formData);
      setResponseMsg(`Éxito: ${response.data.message || 'Datos procesados correctamente'}`);
      setFormData({ nombre: '', email: '' });
    } catch (error) {
      setResponseMsg(`Error: ${error.response?.data?.message || 'No se pudo conectar con el servidor'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '20px auto', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h2>Registro del PMV</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '12px', textAlign: 'left' }}>
          <label style={{ display: 'block', marginBottom: '4px' }}>Nombre:</label>
          <input
            type="text"
            name="nombre"
            value={formData.nombre}
            onChange={handleChange}
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ marginBottom: '12px', textAlign: 'left' }}>
          <label style={{ display: 'block', marginBottom: '4px' }}>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        <button type="submit" disabled={loading} style={{ width: '100%', padding: '10px', cursor: 'pointer' }}>
          {loading ? 'Enviando...' : 'Guardar Datos'}
        </button>
      </form>
      {responseMsg && <p style={{ marginTop: '15px', fontWeight: 'bold' }}>{responseMsg}</p>}
    </div>
  );
}