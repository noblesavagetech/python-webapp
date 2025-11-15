# Wave Apps Integration Setup Guide

## Prerequisites

1. **Wave Apps Developer Account**
   - Sign up at: https://developer.waveapps.com
   - Create a new OAuth application

2. **OAuth Credentials**
   - Client ID
   - Client Secret
   - Redirect URI (must match your application URL)

## Environment Configuration

Add the following to your `.env` file or environment variables:

```bash
# Wave Apps OAuth
WAVE_CLIENT_ID=your_wave_client_id_here
WAVE_CLIENT_SECRET=your_wave_client_secret_here
WAVE_REDIRECT_URI=http://localhost:5000/api/wave/callback
WAVE_AUTHORIZATION_URL=https://api.waveapps.com/oauth2/authorize/
WAVE_TOKEN_URL=https://api.waveapps.com/oauth2/token/
WAVE_API_URL=https://gql.waveapps.com/graphql/public
```

## OAuth Flow

### 1. User Initiates Connection
- User clicks "Connect to Wave" button on dashboard
- Frontend calls `/api/wave/authorize`
- Backend generates OAuth authorization URL with required scopes

### 2. User Authorizes
- User is redirected to Wave's authorization page
- User logs in and grants permissions
- Wave redirects back to your callback URL with authorization code

### 3. Token Exchange
- Backend receives callback at `/api/wave/callback`
- Exchanges authorization code for access token and refresh token
- Stores tokens in database (wave_tokens table)
- Redirects user back to dashboard

### 4. Data Sync
- Once connected, user can trigger manual sync
- Backend fetches data from Wave GraphQL API
- Data is synced to PostgreSQL data warehouse

## Required OAuth Scopes

```python
scopes = [
    'read:business',    # Read business information
    'read:customer',    # Read customer data
    'read:product',     # Read product/service data
    'read:user'         # Read user information
]
```

## API Endpoints

### `/api/wave/authorize` (GET)
- Requires: JWT authentication
- Returns: Authorization URL for user to visit
- Usage: Initiate OAuth flow

### `/api/wave/callback` (GET)
- Public endpoint (no auth required)
- Parameters: `code`, `state`
- Returns: Redirects to dashboard
- Usage: Handle OAuth callback from Wave

### `/api/wave/status` (GET)
- Requires: JWT authentication
- Returns: Connection status and token info
- Usage: Check if Wave is connected

### `/api/wave/sync` (POST)
- Requires: JWT authentication
- Returns: Sync status
- Usage: Manually trigger data sync

### `/api/wave/disconnect` (POST)
- Requires: JWT authentication
- Returns: Success message
- Usage: Remove Wave integration

## Data Warehouse Schema

Wave data is synced to PostgreSQL with the following tables:

### customers
```sql
CREATE TABLE customers (
    id VARCHAR(255) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP,
    modified_at TIMESTAMP,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### invoices
```sql
CREATE TABLE invoices (
    id VARCHAR(255) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    invoice_number VARCHAR(100),
    customer_id VARCHAR(255),
    customer_name VARCHAR(255),
    total DECIMAL(15, 2),
    status VARCHAR(50),
    created_at TIMESTAMP,
    due_date DATE,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## GraphQL Queries

### Get Business Info
```graphql
query {
    user {
        businesses {
            edges {
                node {
                    id
                    name
                    currency {
                        code
                    }
                    isPersonal
                }
            }
        }
    }
}
```

### Get Customers
```graphql
query GetCustomers($businessId: ID!) {
    business(id: $businessId) {
        customers {
            edges {
                node {
                    id
                    name
                    email
                    createdAt
                    modifiedAt
                }
            }
        }
    }
}
```

### Get Invoices
```graphql
query GetInvoices($businessId: ID!) {
    business(id: $businessId) {
        invoices {
            edges {
                node {
                    id
                    invoiceNumber
                    total
                    status
                    createdAt
                    dueDate
                    customer {
                        id
                        name
                    }
                }
            }
        }
    }
}
```

## Token Management

### Access Token
- Expires in 3600 seconds (1 hour) by default
- Stored in `wave_tokens.access_token`
- Automatically refreshed when expired

### Refresh Token
- Used to get new access tokens
- Stored in `wave_tokens.refresh_token`
- Does not expire (but can be revoked by user)

### Token Refresh Logic
```python
def _refresh_token(self, wave_token):
    # POST to Wave token endpoint
    # Update access_token and expires_at
    # Optionally update refresh_token if provided
```

## Security Considerations

1. **Never expose credentials**
   - Store CLIENT_ID and CLIENT_SECRET in environment variables
   - Never commit them to version control

2. **Token Storage**
   - Access tokens and refresh tokens are stored encrypted in database
   - Tokens are associated with company_id for multi-tenancy

3. **State Parameter**
   - Used to prevent CSRF attacks
   - Contains company_id to identify user after OAuth flow

4. **Redirect URI**
   - Must be registered in Wave developer portal
   - Must match exactly (including trailing slashes)

## Testing

### Local Testing
1. Start the Flask server
2. Navigate to `/dashboard`
3. Click "Connect to Wave"
4. Authorize with test Wave account
5. Check connection status
6. Trigger data sync

### Production Setup
1. Update `WAVE_REDIRECT_URI` to production URL
2. Register production callback URL in Wave developer portal
3. Use production OAuth credentials
4. Configure PostgreSQL data warehouse connection

## Troubleshooting

### "Authorization Error" on callback
- Check redirect URI matches exactly in Wave portal
- Verify CLIENT_ID and CLIENT_SECRET are correct

### "No valid access token available"
- Token may be expired and refresh failed
- User needs to reconnect (re-authorize)

### "Failed to sync data"
- Check Wave API permissions/scopes
- Verify business_id is correct
- Check data warehouse connection

### Database connection issues
- Verify PostgreSQL credentials in config
- Check DW_HOST, DW_PORT, DW_DATABASE, DW_USER, DW_PASSWORD

## Future Enhancements

1. **Automatic Sync**
   - Implement background job to sync data periodically
   - Use Celery or similar task queue

2. **Webhook Support**
   - Set up webhooks to receive real-time updates from Wave
   - Update data warehouse when changes occur

3. **More Data Types**
   - Sync products/services
   - Sync expenses
   - Sync bank transactions
   - Sync account balances

4. **Analytics**
   - Build dashboards using synced data
   - Generate financial reports
   - Provide insights and recommendations

5. **Multi-Business Support**
   - Allow selection of specific Wave business
   - Support multiple businesses per company
