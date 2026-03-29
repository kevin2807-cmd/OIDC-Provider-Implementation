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
    // Requirement B: The library automatically parses the ID Token (JWT)
    // The parsed claims are stored in auth.user.profile
    const profile = auth.user?.profile;

    // Requirement C: Display the user's information on a "Profile" page
    return (
      <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
        <h2>Profile Page</h2>
        <p><strong>ID / Subject:</strong> {profile?.sub}</p>
        <p><strong>Email:</strong> {profile?.email || 'No email provided'}</p>
        <p><strong>Name:</strong> {profile?.name || profile?.preferred_username || 'No name provided'}</p>
        
        <h3>Parsed ID Token (JWT) Payload:</h3>
        <pre style={{ background: "#eee", padding: "10px", borderRadius: "5px" }}>
          {JSON.stringify(profile, null, 2)}
        </pre>

        <button onClick={() => auth.removeUser()}>Log out</button>
      </div>
    );
  }

  // Requirement A: The app must have a "Login" button
  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h2>OIDC Testing App</h2>
      <p>You are not logged in.</p>
      <button onClick={() => void auth.signinRedirect()}>Login</button>
    </div>
  );
}

export default App;