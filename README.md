# Financial Health Assessment Web App

A Flask-based web application for financial health assessment with Wave Apps integration.

## Features

- User authentication and company management
- Financial health questionnaire system
- Wave Apps OAuth integration for financial data syncing
- PostgreSQL data warehouse for metrics storage
- RESTful API with JWT authentication

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (copy `.env.example` to `.env`)
4. Run database migrations: `flask db upgrade`
5. Start the app: `python app.py`

## Railway Deployment

### Prerequisites
- Railway account
- Wave Apps developer account with OAuth app configured

### Deployment Steps

1. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Create new project → Deploy from GitHub repo
   - Select your `noblesavagetech/python-webapp` repository

2. **Add PostgreSQL Database**:
   - In Railway dashboard, click "Add" → "Database" → "PostgreSQL"
   - Note the connection details

3. **Set Environment Variables**:
   In Railway project settings → Variables, add:

   ```
   FLASK_ENV=production
   SECRET_KEY=your-random-secret-key
   JWT_SECRET_KEY=your-random-jwt-secret-key
   DATABASE_URL=postgresql://user:password@host:port/database
   WAVE_CLIENT_ID=your-wave-client-id
   WAVE_CLIENT_SECRET=your-wave-client-secret
   WAVE_REDIRECT_URI=https://your-railway-app.up.railway.app/api/wave/callback
   WAVE_AUTHORIZATION_URL=https://api.waveapps.com/oauth2/authorize
   WAVE_TOKEN_URL=https://api.waveapps.com/oauth2/token
   WAVE_API_URL=https://gql.waveapps.com/graphql/public
   DW_HOST=your-postgres-host
   DW_PORT=5432
   DW_DATABASE=your-postgres-db
   DW_USER=your-postgres-user
   DW_PASSWORD=your-postgres-password
   ```

4. **Update Wave OAuth Redirect URI**:
   - In Wave Developer Portal, update redirect URI to: `https://your-railway-app.up.railway.app/api/wave/callback`

5. **Deploy**:
   - Railway will automatically deploy when you push to main branch
   - Check deployment logs for any issues

## API Endpoints

- `GET /` - Home page
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/wave/authorize` - Initiate Wave OAuth
- `GET /api/wave/callback` - Wave OAuth callback
- `POST /api/wave/sync` - Sync Wave data

## Database Schema

The app uses PostgreSQL with the following main tables:
- `user` - User accounts
- `company` - Company information
- `questionnaire` - Financial assessment responses
- `wave_token` - Wave OAuth tokens
- `customers` - Synced customer data
- `invoices` - Synced invoice data

## Development

- Run tests: `python -m pytest`
- Database migrations: `flask db migrate` and `flask db upgrade`
- Initialize questionnaire: `python scripts/init_questionnaire.py`# Force redeploy
# Force redeploy
