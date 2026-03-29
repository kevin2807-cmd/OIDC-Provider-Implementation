import { useAuth } from "react-oidc-context";

function App() {
  const auth = useAuth();

  if (auth.isLoading) {
    return <div>Loading authentication...</div>;
  }

  if (auth.error) {
    return <div>Oops... {auth.error.message}</div>;
  }

  if (auth.isAuthenticated) {
    return (
      <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
        <h2>Welcome back!</h2>
        <p>Your access token: <br/><code style={{ wordBreak: 'break-all' }}>{auth.user?.access_token}</code></p>
        <button onClick={() => auth.removeUser()}>Log out</button>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h2>OIDC Testing App</h2>
      <p>You are not logged in.</p>
      <button onClick={() => void auth.signinRedirect()}>Log in via OIDC</button>
    </div>
  );
}

export default App;