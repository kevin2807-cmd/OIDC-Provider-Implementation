import os
import json
from flask import Flask, url_for, session, render_template, redirect
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

# Initialize OAuth
oauth = OAuth(app)

# Register the OIDC Provider dynamically using the Discovery URL
# Register the OIDC Provider dynamically using the Discovery URL
oauth.register(
    name='oidc_provider',
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    server_metadata_url=os.getenv('OIDC_DISCOVERY_URL'),
    client_kwargs={
        'scope': 'openid profile email',
        'token_endpoint_auth_method': 'client_secret_post'  # <--- ADD THIS LINE
    }
)

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    # Requirement A: Redirect user to the OIDC Provider
    redirect_uri = url_for('callback', _external=True)
    return oauth.oidc_provider.authorize_redirect(redirect_uri)

@app.route('/callback')
def callback():
    token = oauth.oidc_provider.authorize_access_token()
    
    user_info = token.get('userinfo')
    raw_access_token = token.get('access_token')
    
    if user_info:
        session['user'] = user_info
        session['raw_access_token'] = raw_access_token
        # ---> ADD THIS LINE <---
        session['id_token'] = token.get('id_token') 
        
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    user = session.get('user')
    raw_access_token = session.get('raw_access_token')
    if not user:
        return redirect(url_for('index'))
    
    # Requirement C: Display user information on a Profile page
    # Passing the user dictionary to the template to render
    return render_template('profile.html', 
                           user=user, 
                           raw_json=json.dumps(user, indent=4),
                           raw_access_token=raw_access_token)

@app.route('/logout')
def logout():
    # 1. Grab the ID token before we destroy the session
    id_token = session.get('id_token')
    
    # 2. Destroy the local Flask session
    session.clear() 

    # 3. Fetch the Provider's dynamic logout URL
    metadata = oauth.oidc_provider.load_server_metadata()
    end_session_endpoint = metadata.get('end_session_endpoint')

    if end_session_endpoint:
        # Build the URL with Keycloak's required security parameters
        redirect_to = f"{end_session_endpoint}?post_logout_redirect_uri={url_for('index', _external=True)}"
        if id_token:
            redirect_to += f"&id_token_hint={id_token}"
            
        return redirect(redirect_to)
        
    # Fallback
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Running on port 5173 to match our previous redirect URIs
    app.run(host='0.0.0.0', port=5173, debug=True)