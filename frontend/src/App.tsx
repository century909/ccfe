import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import ClientForm from './ClientForm';
import CompanyProfileForm from './CompanyProfileForm'; // Import the new component

// --- Interfaces ---
interface Client {
  ruc: string;
  name: string;
  email: string;
  address?: string;
}

interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  total_item: number;
  vat_rate: number; // 0 for exempt, 5 for 5%, 10 for 10%
}

interface Invoice {
  client: Client;
  items: InvoiceItem[];
  total_amount: number;
}

function App() {
  // --- State Variables ---
  const [client, setClient] = useState<Client>({ ruc: '', name: '', email: '', address: '' });
  const [items, setItems] = useState<InvoiceItem[]>([{ description: '', quantity: 1, unit_price: 0, total_item: 0, vat_rate: 10 }]);
  const [totalAmount, setTotalAmount] = useState<number>(0);
  const [responseMessage, setResponseMessage] = useState<string>('');
  
  const [clientList, setClientList] = useState<Client[]>([]);
  const [showClientForm, setShowClientForm] = useState<boolean>(false);
  const [showProfileForm, setShowProfileForm] = useState<boolean>(false); // State for profile form
  const [oraculoData, setOraculoData] = useState<any>(null); // Datos del Oráculo

  // --- Data Fetching ---
  const fetchOraculo = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/oraculo/report');
      if (response.ok) {
        const data = await response.json();
        setOraculoData(data);
      }
    } catch (error) {
      console.error('Error al obtener datos del Oráculo:', error);
    }
  }, []);

  const fetchClients = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/clients');
      if (response.ok) {
        const data: Client[] = await response.json();
        setClientList(data);
      } else {
        console.error('Failed to fetch clients');
      }
    } catch (error) {
      console.error('Network error while fetching clients:', error);
    }
  }, []);

  useEffect(() => {
    fetchClients();
    fetchOraculo();
  }, [fetchClients, fetchOraculo]);

  useEffect(() => {
    const newTotalAmount = items.reduce((sum, item) => sum + item.total_item, 0);
    setTotalAmount(newTotalAmount);
  }, [items]);

  // --- Event Handlers ---
  const handleClientChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setClient(prevClient => ({ ...prevClient, [name]: value }));

    if (name === 'ruc') {
      const selectedClient = clientList.find(c => c.ruc === value);
      if (selectedClient) {
        setClient(selectedClient);
      }
    }
  };

  const handleItemChange = (index: number, e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const newItems = [...items];
    const updatedItem = { ...newItems[index], [name]: name === 'description' ? value : parseFloat(value) || 0 };

    if (name === 'quantity' || name === 'unit_price') {
      updatedItem.total_item = updatedItem.quantity * updatedItem.unit_price;
    }
    newItems[index] = updatedItem;
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { description: '', quantity: 1, unit_price: 0, total_item: 0, vat_rate: 10 }]);
  };

  const removeItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResponseMessage('Processing invoice...');

    const invoiceData = { 
      client_ruc: client.ruc, 
      items, 
      total_amount: totalAmount 
    };

    try {
      const response = await fetch('http://localhost:8000/invoice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(invoiceData),
      });

      const data = await response.json();
      if (response.ok) {
        setResponseMessage(`Invoice processed: ${data.message} Invoice Number: ${data.invoice_number}`);
      } else {
        setResponseMessage(`Error: ${data.detail || 'Something went wrong'}`);
      }
    } catch (error) {
      setResponseMessage(`Network error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  // --- Render ---
  return (
    <div className="App container mt-5">
      <header className="d-flex justify-content-between align-items-center mb-4">
        <h1>Emitir Factura Electrónica</h1>
        <button className="btn btn-secondary" onClick={() => setShowProfileForm(!showProfileForm)}>
          {showProfileForm ? 'Cerrar Perfil de Empresa' : 'Gestionar Perfil de Empresa'}
        </button>
      </header>

      {showProfileForm && <CompanyProfileForm />}
      
      {oraculoData && (
        <section className="alert alert-info mb-4">
          <div className="d-flex justify-content-between align-items-center">
            <h4>🔮 Oráculo de Datos</h4>
            <span className="badge bg-primary">Periodo: {oraculoData.data.periodo}</span>
          </div>
          <div className="row mt-3">
            <div className="col-md-4">
              <p className="mb-1"><strong>Débito Fiscal (Ventas):</strong></p>
              <p className="fs-5">{oraculoData.data.debito_fiscal?.toLocaleString()} PYG</p>
            </div>
            <div className="col-md-4">
              <p className="mb-1"><strong>Crédito Fiscal (Gastos):</strong></p>
              <p className="fs-5 text-success">-{oraculoData.data.credito_fiscal?.toLocaleString()} PYG</p>
              <small className="text-muted">({oraculoData.data.cantidad_gastos_sincronizados} facturas sync)</small>
            </div>
            <div className="col-md-4 border-start">
              <p className="mb-1"><strong>IVA Neto Estimado:</strong></p>
              <p className={`fs-4 fw-bold ${oraculoData.data.iva_neto_estimado > 0 ? 'text-danger' : 'text-success'}`}>
                {oraculoData.data.iva_neto_estimado?.toLocaleString()} PYG
              </p>
            </div>
          </div>
          <hr />
          <p className="mb-0 text-primary"><em>{oraculoData.advice}</em></p>
        </section>
      )}

      <hr />

      <div className="d-flex justify-content-start mb-4">
        <button className="btn btn-info" onClick={() => setShowClientForm(!showClientForm)}>
          {showClientForm ? 'Ocultar Formulario de Cliente' : 'Registrar Nuevo Cliente'}
        </button>
      </div>

      {showClientForm && <ClientForm onClientAdded={fetchClients} />}

      <form onSubmit={handleSubmit}>
        <section className="card p-4 mb-4">
          <h2 className="card-title">Datos del Cliente</h2>
          <div className="mb-3">
            <label htmlFor="ruc" className="form-label">Buscar Cliente por RUC:</label>
            <input 
              type="text" 
              className="form-control" 
              id="ruc" 
              name="ruc" 
              value={client.ruc} 
              onChange={handleClientChange} 
              list="client-rucs"
              required 
            />
            <datalist id="client-rucs">
              {clientList.map(c => <option key={c.ruc} value={c.ruc}>{c.name}</option>)}
            </datalist>
          </div>
          <div className="mb-3">
            <label htmlFor="name" className="form-label">Nombre/Razón Social:</label>
            <input type="text" className="form-control" id="name" name="name" value={client.name} onChange={handleClientChange} required />
          </div>
          <div className="mb-3">
            <label htmlFor="email" className="form-label">Email:</label>
            <input type="email" className="form-control" id="email" name="email" value={client.email} onChange={handleClientChange} required />
          </div>
          <div className="mb-3">
            <label htmlFor="address" className="form-label">Dirección (Opcional):</label>
            <input type="text" className="form-control" id="address" name="address" value={client.address || ''} onChange={handleClientChange} />
          </div>
        </section>

        <section className="card p-4 mb-4">
          <h2 className="card-title">Ítems de la Factura</h2>
          {items.map((item, index) => (
            <div key={index} className="row mb-3 align-items-end border-bottom pb-3">
              <div className="col-md-4">
                <label htmlFor={`description-${index}`} className="form-label">Descripción:</label>
                <input type="text" className="form-control" id={`description-${index}`} name="description" value={item.description} onChange={(e) => handleItemChange(index, e)} required />
              </div>
              <div className="col-md-2">
                <label htmlFor={`quantity-${index}`} className="form-label">Cantidad:</label>
                <input type="number" className="form-control" id={`quantity-${index}`} name="quantity" value={item.quantity} onChange={(e) => handleItemChange(index, e)} min="1" required />
              </div>
              <div className="col-md-2">
                <label htmlFor={`unit_price-${index}`} className="form-label">Precio Unitario:</label>
                <input type="number" className="form-control" id={`unit_price-${index}`} name="unit_price" value={item.unit_price} onChange={(e) => handleItemChange(index, e)} step="0.01" min="0" required />
              </div>
              <div className="col-md-2">
                <label htmlFor={`vat_rate-${index}`} className="form-label">IVA:</label>
                <select className="form-select" id={`vat_rate-${index}`} name="vat_rate" value={item.vat_rate} onChange={(e) => handleItemChange(index, e)}>
                  <option value="10">10%</option>
                  <option value="5">5%</option>
                  <option value="0">Exenta</option>
                </select>
              </div>
              <div className="col-md-2 d-flex justify-content-between align-items-center">
                <p className="mb-0">Total: {item.total_item.toFixed(2)}</p>
                {items.length > 1 && (
                  <button type="button" className="btn btn-danger btn-sm" onClick={() => removeItem(index)}>X</button>
                )}
              </div>
            </div>
          ))}
          <button type="button" className="btn btn-secondary mt-3" onClick={addItem}>Agregar Ítem</button>
        </section>

        <section className="card p-4 mb-4">
          <h2 className="card-title">Resumen</h2>
          <p className="fs-4">Monto Total: <strong>{totalAmount.toFixed(2)} PYG</strong></p>
          <button type="submit" className="btn btn-primary btn-lg">Emitir Factura</button>
        </section>
      </form>

      {responseMessage && (
        <div className={`alert ${responseMessage.startsWith('Error') ? 'alert-danger' : 'alert-success'} mt-4`} role="alert">
          {responseMessage}
        </div>
      )}
    </div>
  );
}

export default App;
