import React, { useState, useEffect, useCallback } from 'react';

interface CompanyProfile {
  name: string;
  fantasy_name?: string;
  ruc: string;
  address: string;
  phone: string;
  email: string;
  economic_activity: string;
  timbrado: string;
}

const CompanyProfileForm: React.FC = () => {
  const [profile, setProfile] = useState<CompanyProfile>({
    name: '',
    fantasy_name: '',
    ruc: '',
    address: '',
    phone: '',
    email: '',
    economic_activity: '',
    timbrado: '',
  });
  const [responseMessage, setResponseMessage] = useState<string>('');

  const fetchProfile = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/company-profile');
      if (response.ok) {
        const data = await response.json();
        if (data) {
          setProfile(data);
        }
      }
    } catch (error) {
      console.error('Failed to fetch company profile:', error);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfile(prevProfile => ({ ...prevProfile, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResponseMessage('Saving profile...');

    try {
      const response = await fetch('http://localhost:8000/company-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profile),
      });

      const data = await response.json();
      if (response.ok) {
        setResponseMessage('Profile saved successfully!');
      } else {
        setResponseMessage(`Error: ${data.detail || 'Something went wrong'}`);
      }
    } catch (error) {
      setResponseMessage(`Network error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  return (
    <section className="card p-4 mb-4">
      <h2 className="card-title">Perfil de la Empresa</h2>
      <p>Estos datos se usarán para generar las facturas.</p>
      <form onSubmit={handleSubmit}>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label htmlFor="name" className="form-label">Nombre/Razón Social:</label>
            <input type="text" className="form-control" id="name" name="name" value={profile.name} onChange={handleChange} required />
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="fantasy_name" className="form-label">Nombre de Fantasía:</label>
            <input type="text" className="form-control" id="fantasy_name" name="fantasy_name" value={profile.fantasy_name || ''} onChange={handleChange} />
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="ruc" className="form-label">RUC:</label>
            <input type="text" className="form-control" id="ruc" name="ruc" value={profile.ruc} onChange={handleChange} required />
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="timbrado" className="form-label">Timbrado N°:</label>
            <input type="text" className="form-control" id="timbrado" name="timbrado" value={profile.timbrado} onChange={handleChange} required />
          </div>
          <div className="col-md-12 mb-3">
            <label htmlFor="address" className="form-label">Dirección:</label>
            <input type="text" className="form-control" id="address" name="address" value={profile.address} onChange={handleChange} required />
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="phone" className="form-label">Teléfono:</label>
            <input type="text" className="form-control" id="phone" name="phone" value={profile.phone} onChange={handleChange} required />
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="email" className="form-label">Email:</label>
            <input type="email" className="form-control" id="email" name="email" value={profile.email} onChange={handleChange} required />
          </div>
          <div className="col-md-12 mb-3">
            <label htmlFor="economic_activity" className="form-label">Actividad Económica:</label>
            <input type="text" className="form-control" id="economic_activity" name="economic_activity" value={profile.economic_activity} onChange={handleChange} required />
          </div>
        </div>
        <button type="submit" className="btn btn-success">Guardar Perfil</button>
      </form>
      {responseMessage && (
        <div className={`alert ${responseMessage.startsWith('Error') ? 'alert-danger' : 'alert-success'} mt-3`} role="alert">
          {responseMessage}
        </div>
      )}
    </section>
  );
};

export default CompanyProfileForm;
