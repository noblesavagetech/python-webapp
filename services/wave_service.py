import requests
from datetime import datetime, timedelta
from extensions import db
from models.wave_token import WaveToken
from models.company import Company
from services.data_warehouse_service import DataWarehouseService


class WaveService:
    """Service for interacting with Wave Apps API"""
    
    def __init__(self, config):
        self.config = config
        self.api_url = config['WAVE_API_URL']
        self.dw_service = DataWarehouseService(config)
        
        # Check if using dummy credentials
        self.is_configured = not (
            config.get('WAVE_CLIENT_ID', '').startswith('dummy') or
            config.get('WAVE_CLIENT_SECRET', '').startswith('dummy')
        )
    
    def get_valid_token(self, company_id):
        """Get a valid access token for a company, refreshing if needed"""
        if not self.is_configured:
            return None
            
        wave_token = WaveToken.query.filter_by(company_id=company_id).first()
        
        if not wave_token:
            return None
        
        # Check if token is expired
        if wave_token.is_expired() and wave_token.refresh_token:
            self._refresh_token(wave_token)
        
        return wave_token.access_token
    
    def _refresh_token(self, wave_token):
        """Refresh an expired access token"""
        try:
            token_data = {
                'grant_type': 'refresh_token',
                'refresh_token': wave_token.refresh_token,
                'client_id': self.config['WAVE_CLIENT_ID'],
                'client_secret': self.config['WAVE_CLIENT_SECRET']
            }
            
            response = requests.post(
                self.config['WAVE_TOKEN_URL'],
                data=token_data
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                wave_token.access_token = token_response['access_token']
                if 'refresh_token' in token_response:
                    wave_token.refresh_token = token_response['refresh_token']
                
                expires_in = token_response.get('expires_in', 3600)
                wave_token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                db.session.commit()
                return True
            
            return False
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def make_graphql_request(self, company_id, query, variables=None):
        """Make a GraphQL request to Wave API"""
        access_token = self.get_valid_token(company_id)
        
        if not access_token:
            raise Exception("No valid access token available")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Wave API request failed: {response.text}")
    
    def get_business_info(self, company_id):
        """Get business information from Wave"""
        query = """
        query {
            user {
                id
                defaultBusiness {
                    id
                    name
                    currency {
                        code
                    }
                    isPersonal
                }
            }
        }
        """
        
        result = self.make_graphql_request(company_id, query)
        # Return the default business wrapped in the same structure for compatibility
        default_business = result.get('data', {}).get('user', {}).get('defaultBusiness')
        if default_business:
            return {
                'edges': [{'node': default_business}]
            }
        return {}
    
    def get_customers(self, company_id, business_id):
        """Get customers for a business"""
        query = """
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
        """
        
        variables = {'businessId': business_id}
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('customers', {})
    
    def get_invoices(self, company_id, business_id):
        """Get invoices for a business"""
        query = """
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
        """
        
        variables = {'businessId': business_id}
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('invoices', {})
    
    def sync_company_data(self, company_id):
        """Sync all Wave data for a company to data warehouse"""
        try:
            print(f"Starting Wave data sync for company {company_id}")
            
            # Get business info first
            print("Fetching business info from Wave...")
            businesses = self.get_business_info(company_id)
            
            if not businesses or not businesses.get('edges'):
                print("ERROR: No businesses found in Wave account")
                raise Exception("No businesses found in Wave account")
            
            # Use first business (or implement logic to select specific business)
            business_node = businesses['edges'][0]['node']
            business_id = business_node['id']
            business_name = business_node.get('name', 'Unknown')
            print(f"Using business: {business_name} (ID: {business_id})")
            
            # Update Wave token with business_id
            wave_token = WaveToken.query.filter_by(company_id=company_id).first()
            if wave_token:
                wave_token.wave_business_id = business_id
                db.session.commit()
                print("Updated wave_business_id in token")
            
            # Sync customers
            print("Fetching customers from Wave...")
            customers = self.get_customers(company_id, business_id)
            customer_count = len(customers.get('edges', []))
            print(f"Found {customer_count} customers")
            
            print("Syncing customers to data warehouse...")
            if not self.dw_service.sync_customers(company_id, customers):
                raise Exception("Failed to sync customers to data warehouse")
            print("Customers synced successfully")
            
            # Sync invoices
            print("Fetching invoices from Wave...")
            invoices = self.get_invoices(company_id, business_id)
            invoice_count = len(invoices.get('edges', []))
            print(f"Found {invoice_count} invoices")
            
            print("Syncing invoices to data warehouse...")
            if not self.dw_service.sync_invoices(company_id, invoices):
                raise Exception("Failed to sync invoices to data warehouse")
            print("Invoices synced successfully")
            
            print(f"Wave data sync completed: {customer_count} customers, {invoice_count} invoices")
            return True
            
        except Exception as e:
            print(f"ERROR: Wave data sync failed: {e}")
            import traceback
            traceback.print_exc()
            raise
