# Quick Start Guide - FinHealth Platform

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### 2. Configure Environment

Edit the `.env` file that was created:

```bash
# Required: Update these values
DATABASE_URL=postgresql://user:password@localhost:5432/financial_health_db
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# For Wave Integration (get from https://developer.waveapps.com/)
WAVE_CLIENT_ID=your-wave-client-id
WAVE_CLIENT_SECRET=your-wave-client-secret
```

### 3. Setup Database

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create database
createdb financial_health_db  # If using PostgreSQL locally

# Initialize migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create sample questionnaire
chmod +x scripts/init_questionnaire.sh
./scripts/init_questionnaire.sh
```

### 4. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser!

---

## Using SQLite for Quick Testing

If you don't have PostgreSQL installed, you can use SQLite:

1. In `.env`, set:
   ```
   DATABASE_URL=sqlite:///financial_health.db
   ```

2. Skip the `createdb` command

3. Continue with migrations as normal

---

## Wave Apps Developer Setup

1. Go to https://developer.waveapps.com/
2. Create a new application
3. Set redirect URI to: `http://localhost:5000/api/wave/callback`
4. Copy Client ID and Client Secret to `.env`

---

## Testing the Application

### 1. Sign Up
- Navigate to http://localhost:5000/signup
- Create a company account
- You'll be redirected to the questionnaire

### 2. Complete Questionnaire
- Answer all questions about your business
- Submit to get your financial health score

### 3. Connect Wave (Optional)
- Go to Dashboard
- Click "Connect to Wave"
- Authorize the connection
- Sync your financial data

---

## API Testing with cURL

### Sign Up
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "email": "test@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Get Active Questionnaire
```bash
curl -X GET http://localhost:5000/api/questionnaire/active \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Project Structure Overview

```
python-webapp/
├── app.py                    # Main application entry point
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create from .env.example)
│
├── models/                   # Database models
│   ├── company.py           # Company model
│   ├── user.py              # User model
│   ├── questionnaire.py     # Questionnaire models
│   └── wave_token.py        # Wave OAuth tokens
│
├── routes/                   # API endpoints
│   ├── auth.py              # Authentication
│   ├── companies.py         # Company management
│   ├── questionnaire.py     # Questionnaire endpoints
│   └── wave.py              # Wave integration
│
├── services/                 # Business logic
│   ├── wave_service.py      # Wave API integration
│   └── data_warehouse_service.py  # Data warehouse ops
│
├── templates/                # HTML templates
│   ├── index.html           # Landing page
│   ├── about.html           # About page
│   ├── signup.html          # Sign up form
│   ├── login.html           # Login form
│   ├── questionnaire.html   # Questionnaire
│   └── dashboard.html       # Dashboard
│
└── static/                   # Static files
    ├── css/styles.css       # Stylesheet
    └── js/                  # JavaScript files
        ├── main.js          # Common utilities
        ├── signup.js        # Signup logic
        ├── questionnaire.js # Questionnaire logic
        └── dashboard.js     # Dashboard logic
```

---

## Common Issues & Solutions

### Issue: "Module not found" errors
**Solution:** Make sure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database connection errors
**Solution:** Check DATABASE_URL in .env matches your database setup

### Issue: "Table doesn't exist" errors
**Solution:** Run migrations:
```bash
flask db upgrade
```

### Issue: Wave OAuth redirect doesn't work
**Solution:** Ensure redirect URI in Wave Developer Portal exactly matches:
`http://localhost:5000/api/wave/callback`

---

## Next Steps

1. **Customize Questionnaire**: Edit `scripts/init_questionnaire.sh` to modify questions
2. **Add More Metrics**: Extend data warehouse to track additional financial data
3. **Build Dashboard Charts**: Add visualization libraries (Chart.js, D3.js)
4. **Deploy to Production**: Use Gunicorn, Nginx, and PostgreSQL
5. **Add Email Notifications**: Integrate SendGrid or similar service

---

## Production Deployment Checklist

- [ ] Change SECRET_KEY and JWT_SECRET_KEY to strong random values
- [ ] Set FLASK_ENV=production
- [ ] Use production-grade database (PostgreSQL)
- [ ] Set up SSL/HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Use environment-specific configs
- [ ] Set up CI/CD pipeline
- [ ] Enable rate limiting
- [ ] Configure data warehouse security

---

## Support & Documentation

- **Wave API Docs**: https://developer.waveapps.com/hc/en-us/sections/360003012132-API-Reference
- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

For questions or issues, refer to the main README.md
