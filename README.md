# OIDC Provider Implementation & Testing App

This repository contains a complete local infrastructure for testing OpenID Connect (OIDC) flows. It provisions two distinct OIDC providers (Keycloak and Ory Hydra) backed by PostgreSQL and OpenLDAP, along with a minimalist Python Flask application acting as the Relying Party (Client).

## 📂 Repository Structure

*   **`/` (Root):** Contains the Docker Compose infrastructure and root `.env` for database/admin secrets.
*   **`/web-app`:** Contains the Python Flask application, HTML templates, and the specific `.env` for OIDC client credentials.

## 🛠️ Prerequisites

*   [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose
*   [Python 3.9+](https://www.python.org/downloads/)
*   Git

---

## 🚀 Step 1: Start the Infrastructure

1.  Clone this repository and navigate to the root directory.
2.  Create a `.env` file in the root directory (ask a team member for the secrets, or use dummy values for local testing). Example:
    ```env
    POSTGRES_USER=oidc_user
    POSTGRES_PASSWORD=super_secret_db_password
    KEYCLOAK_ADMIN=admin
    KEYCLOAK_ADMIN_PASSWORD=super_secret_admin_password
    HYDRA_SYSTEM_SECRET=this_secret_needs_to_be_32_chars_long_exactly
    HYDRA_COOKIE_SECRET=another_secret_that_is_32_chars_long_exactly
    LDAP_ADMIN_PASSWORD=super_secret_ldap_password
    ```
3.  Spin up the containers in the background:
    ```bash
    docker compose up -d
    ```
4.  Verify all containers are running successfully:
    ```bash
    docker compose ps
    ```

---

## 🔐 Step 2: Configure the OIDC Providers

You can test using either Keycloak or Ory Hydra. Follow the setup for the one you wish to test.

### Option A: Keycloak Setup

1.  Access the Keycloak Admin Console at [http://localhost:8080](http://localhost:8080).
2.  Log in using the `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD` from your root `.env` file.
3.  **Create a Realm:** Click the top-left dropdown (currently "master") -> **Create Realm** -> Name it `demo-realm` -> Click **Create**.
4.  **Create a Client:** 
    *   Go to **Clients** -> **Create client**.
    *   Client ID: `web-app`.
    *   Click **Next**. 
    *   Toggle **Client authentication** to **ON** (This makes it a Confidential Client).
    *   Set **Valid redirect URIs** to `http://127.0.0.1:5173/callback`.
    *   Click **Save**.
5.  **Get Client Secret:** Go to the **Credentials** tab of your new `web-app` client and copy the **Client Secret**.
6.  **Create a User:** Go to **Users** -> **Add user** -> Set a username (e.g., `testuser`) -> **Create**. Go to the **Credentials** tab, click **Set password**, uncheck "Temporary", and save.

### Option B: Ory Hydra Setup

Hydra is headless, so we configure it via the CLI executing inside the running Docker container.

1.  Run the following command to create an OIDC client for the Flask app:
    ```bash
    docker compose exec hydra hydra create client \
        --endpoint [http://127.0.0.1:4445](http://127.0.0.1:4445) \
        --grant-type authorization_code,refresh_token \
        --response-type code,id_token \
        --scope openid,profile,email,offline \
        --token-endpoint-auth-method client_secret_post \
        --redirect-uri [http://127.0.0.1:5173/callback](http://127.0.0.1:5173/callback)
    ```
2.  The terminal will output a **Client ID** and a **Client Secret**. Copy these immediately, as the secret will not be shown again.
*(Note: Hydra routes logins through a mock consent UI running on port 3000).*

---

## 🌐 Step 3: Run the Web Application

The web application is a Flask backend that acts as the OIDC client.

1.  Navigate to the `web-app` directory:
    ```bash
    cd web-app
    ```
2.  Create and activate a Python virtual environment:
    ```bash
    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```
3.  Install the required Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file inside the `web-app` directory. Configure it to point to the provider you want to test by uncommenting the relevant block and inserting the Client Secret you generated in Step 2:
    ```env
    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=a_random_flask_session_secret_key

    # --- TOGGLE KEYCLOAK ---
    OIDC_CLIENT_ID=web-app
    OIDC_CLIENT_SECRET=<PASTE_KEYCLOAK_SECRET_HERE>
    OIDC_DISCOVERY_URL=http://localhost:8080/realms/demo-realm/.well-known/openid-configuration

    # --- TOGGLE ORY HYDRA ---
    # OIDC_CLIENT_ID=<PASTE_HYDRA_CLIENT_ID_HERE>
    # OIDC_CLIENT_SECRET=<PASTE_HYDRA_SECRET_HERE>
    # OIDC_DISCOVERY_URL=[http://127.0.0.1:4444/.well-known/openid-configuration](http://127.0.0.1:4444/.well-known/openid-configuration)
    ```
5.  Start the Flask application:
    ```bash
    python app.py
    ```
6.  Open your browser and navigate to [http://127.0.0.1:5173](http://127.0.0.1:5173). Click "Login with OIDC" to test the authorization flow. Upon success, you will be redirected to your profile page showing the parsed ID Token data.

## 🧹 Teardown

To stop the infrastructure and remove the containers, networks, and volumes:
```bash
# From the root directory
docker compose down -v