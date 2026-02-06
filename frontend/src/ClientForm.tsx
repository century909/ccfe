import React, { useState } from 'react';

interface Client {
  ruc: string;
  name: string;
  email: string;
  address?: string;
}

interface ClientFormProps {
  onClientAdded: () => void;
}

const ClientForm: React.FC<ClientFormProps> = ({ onClientAdded }) => {
  const [newClient, setNewClient] = useState<Client>({ ruc: '', name: '', email: '', address: '' });
  const [responseMessage, setResponseMessage] = useState<string>('');

  const handleNewClientChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewClient(prevClient => ({ ...prevClient, [name]: value }));
  };

  const handleAddClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setResponseMessage('Adding client...');

    try {
      const response = await fetch('http://localhost:8000/clients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newClient),
      });

      const data = await response.json();
      if (response.ok) {
        setResponseMessage(`Client added: ${data.client.name}`);
        onClientAdded(); // Callback to refresh client list
        setNewClient({ ruc: '', name: '', email: '', address: '' }); // Reset form
      } else {
        setResponseMessage(`Error: ${data.detail || 'Something went wrong'}`);
      }
    } catch (error) {
      setResponseMessage(`Network error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  return (
    <section className="card p-4 mb-4">
      <h2 className="card-title">Registrar Nuevo Cliente</h2>
      <form onSubmit={handleAddClient}>
        <div className="mb-3">
          <label htmlFor="new-ruc" className="form-label">RUC:</label>
          <input type="text" className="form-control" id="new-ruc" name="ruc" value={newClient.ruc} onChange={handleNewClientChange} required />
        </div>
        <div className="mb-3">
          <label htmlFor="new-name" className="form-label">Nombre/Razón Social:</label>
          <input type="text" className="form-control" id="new-name" name="name" value={newClient.name} onChange={handleNewClientChange} required />
        </div>
        <div className="mb-3">
          <label htmlFor="new-email" className="form-label">Email:</label>
          <input type="email" className="form-control" id="new-email" name="email" value={newClient.email} onChange={handleNewClientChange} required />
        </div>
        <div className="mb-3">
          <label htmlFor="new-address" className="form-label">Dirección (Opcional):</label>
          <input type="text" className="form-control" id="new-address" name="address" value={newClient.address || ''} onChange={handleNewClientChange} />
        </div>
        <button type="submit" className="btn btn-success">Registrar Cliente</button>
      </form>
      {responseMessage && (
        <div className={`alert ${responseMessage.startsWith('Error') ? 'alert-danger' : 'alert-success'} mt-3`} role="alert">
          {responseMessage}
        </div>
      )}
    </section>
  );
};

export default ClientForm;
