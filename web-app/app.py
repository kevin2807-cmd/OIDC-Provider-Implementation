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
oauth.register(
    name='oidc_provider',
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    server_metadata_url=os.getenv('OIDC_DISCOVERY_URL'),
    client_kwargs={
        'scope': 'openid profile email'
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
    # Requirement B: Receive and parse the ID Token (JWT)
    token = oauth.oidc_provider.authorize_access_token()
    
    # Authlib automatically parses the ID Token and stores it in 'userinfo'
    user_info = token.get('userinfo')
    
    # Store the parsed JWT claims in the Flask session
    if user_info:
        session['user'] = user_info
        
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    
    # Requirement C: Display user information on a Profile page
    # Passing the user dictionary to the template to render
    return render_template('profile.html', user=user, raw_json=json.dumps(user, indent=4))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Running on port 5173 to match our previous redirect URIs
    app.run(host='0.0.0.0', port=5173, debug=True)