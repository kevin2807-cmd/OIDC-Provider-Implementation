import React from 'react';
import ReactDOM from 'react-dom/client';
import { AuthProvider } from 'react-oidc-context';
import App from './App';

// NOTE: Swap these configurations based on which environment you are testing.
// Currently set up for Keycloak.

const oidcConfig = {
  // For Keycloak:
  authority: "http://localhost:8080/realms/demo-realm",
  client_id: "web-app",
  
  // For Hydra (Uncomment below and comment out Keycloak above):
  // authority: "http://127.0.0.1:4444/",
  // client_id: "<YOUR_HYDRA_CLIENT_ID_FROM_CLI>",
  
  redirect_uri: "http://localhost:5173/",
  response_type: "code",
  scope: "openid profile email",
};

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider {...oidcConfig}>
      <App />
    </AuthProvider>
  </React.StrictMode>
);