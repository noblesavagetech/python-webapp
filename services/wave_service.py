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
            businesses {
                edges {
                    node {
                        id
                        name
                        isPersonal
                    }
                }
            }
        }
        """
        
        result = self.make_graphql_request(company_id, query)
        return result.get('data', {}).get('businesses', {})
    
    def get_customers(self, company_id, business_id):
        """Get customers for a business"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                customers(page: 1, pageSize: 50) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            name
                            email
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            'businessId': business_id
        }
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('customers', {})
    
    def get_invoices(self, company_id, business_id):
        """Get invoices for a business"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                invoices(page: 1, pageSize: 50) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            invoiceNumber
                            total {
                                value
                                currency {
                                    code
                                }
                            }
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
        
        variables = {
            'businessId': business_id
        }
    def get_products(self, company_id, business_id):
        """Get products/services for a business"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                products(page: 1, pageSize: 50) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            name
                            description
                            unitPrice {
                                value
                                currency {
                                    code
                                }
                            }
                            incomeAccount {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            'businessId': business_id
        }
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('products', {})

    def get_bills(self, company_id, business_id):
        """Get bills/expenses for a business"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                bills(page: 1, pageSize: 50) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            billNumber
                            vendor {
                                id
                                name
                            }
                            total {
                                value
                                currency {
                                    code
                                }
                            }
                            status
                            dueDate
                            createdAt
                        }
                    }
                }
            }
        }
        """

        variables = {
            'businessId': business_id
        }
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('bills', {})

    def get_accounts(self, company_id, business_id):
        """Get chart of accounts for a business"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                accounts {
                    edges {
                        node {
                            id
                            name
                            type
                            subtype
                            balance {
                                value
                                currency {
                                    code
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            'businessId': business_id
        }
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('accounts', {})

    def get_account_transactions(self, company_id, business_id, account_id=None, date_from=None, date_to=None):
        """Get transactions for accounts (if available in Wave API)"""
        # Note: Wave may not provide detailed transaction history via API
        # This is a placeholder for when/if they add this functionality
        query = """
        query($businessId: ID!, $accountId: ID, $dateFrom: Date, $dateTo: Date) {
            business(id: $businessId) {
                account(id: $accountId) {
                    transactions(dateFrom: $dateFrom, dateTo: $dateTo, page: 1, pageSize: 100) {
                        edges {
                            node {
                                id
                                date
                                description
                                amount {
                                    value
                                    currency {
                                        code
                                    }
                                }
                                type
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            'businessId': business_id,
            'accountId': account_id,
            'dateFrom': date_from,
            'dateTo': date_to
        }
        try:
            result = self.make_graphql_request(company_id, query, variables)
            return result.get('data', {}).get('business', {}).get('account', {}).get('transactions', {})
        except:
            # If transactions aren't available, return empty
            return {'edges': []}

    def get_business_summary(self, company_id, business_id):
        """Get business financial summary/metrics"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                id
                name
                currency {
                    code
                }
                invoices {
                    pageInfo {
                        totalCount
                    }
                }
                customers {
                    pageInfo {
                        totalCount
                    }
                }
                products {
                    pageInfo {
                        totalCount
                    }
                }
                bills {
                    pageInfo {
                        totalCount
                    }
                }
            }
        }
        """

        variables = {
            'businessId': business_id
        }
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {})

    def get_payments(self, company_id, business_id):
        """Get payments received for a business"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                payments(page: 1, pageSize: 50) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            amount {
                                value
                                currency {
                                    code
                                }
                            }
                            date
                            method
                            invoices {
                                edges {
                                    node {
                                        id
                                        invoiceNumber
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            'businessId': business_id
        }
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('payments', {})

    def get_vendor_payments(self, company_id, business_id):
        """Get payments made to vendors for a business"""
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                vendorPayments(page: 1, pageSize: 50) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            amount {
                                value
                                currency {
                                    code
                                }
                            }
                            date
                            method
                            bills {
                                edges {
                                    node {
                                        id
                                        billNumber
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            'businessId': business_id
        }
        result = self.make_graphql_request(company_id, query, variables)
        return result.get('data', {}).get('business', {}).get('vendorPayments', {})
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
            success, debug_info = self.dw_service.sync_customers(company_id, customers)
            if not success:
                error_msg = f"Failed to sync customers to data warehouse. Debug info: {'; '.join(debug_info)}"
                raise Exception(error_msg)
            print("Customers synced successfully")
            
            # Sync invoices
            print("Fetching invoices from Wave...")
            invoices = self.get_invoices(company_id, business_id)
            invoice_count = len(invoices.get('edges', []))
            print(f"Found {invoice_count} invoices")
            
            print("Syncing invoices to data warehouse...")
            success, debug_info = self.dw_service.sync_invoices(company_id, invoices)
            if not success:
                error_msg = f"Failed to sync invoices to data warehouse. Debug info: {'; '.join(debug_info)}"
                raise Exception(error_msg)
            print("Invoices synced successfully")
            
            # Sync products
            print("Fetching products from Wave...")
            products = self.get_products(company_id, business_id)
            product_count = len(products.get('edges', []))
            print(f"Found {product_count} products")
            
            print("Syncing products to data warehouse...")
            success, debug_info = self.dw_service.sync_products(company_id, products)
            if not success:
                error_msg = f"Failed to sync products to data warehouse. Debug info: {'; '.join(debug_info)}"
                raise Exception(error_msg)
            print("Products synced successfully")
            
            # Sync bills/expenses
            print("Fetching bills/expenses from Wave...")
            bills = self.get_bills(company_id, business_id)
            bill_count = len(bills.get('edges', []))
            print(f"Found {bill_count} bills")
            
            print("Syncing bills to data warehouse...")
            success, debug_info = self.dw_service.sync_bills(company_id, bills)
            if not success:
                error_msg = f"Failed to sync bills to data warehouse. Debug info: {'; '.join(debug_info)}"
                raise Exception(error_msg)
            print("Bills synced successfully")
            
            # Sync chart of accounts
            print("Fetching chart of accounts from Wave...")
            accounts = self.get_accounts(company_id, business_id)
            account_count = len(accounts.get('edges', []))
            print(f"Found {account_count} accounts")
            
            print("Syncing accounts to data warehouse...")
            success, debug_info = self.dw_service.sync_accounts(company_id, accounts)
            if not success:
                error_msg = f"Failed to sync accounts to data warehouse. Debug info: {'; '.join(debug_info)}"
                raise Exception(error_msg)
            print("Accounts synced successfully")
            
            # Sync account transactions for bank accounts
            print("Fetching account transactions from Wave...")
            transaction_count = 0
            
            # Get transactions for each account (focus on bank accounts)
            for account_edge in accounts.get('edges', []):
                account = account_edge['node']
                account_id = account['id']
                account_name = account.get('name', '')
                account_type = account.get('type', '')
                
                # Only fetch transactions for bank/asset accounts
                if account_type in ['ASSET'] or 'bank' in account_name.lower() or 'checking' in account_name.lower() or 'savings' in account_name.lower():
                    try:
                        print(f"Fetching transactions for account: {account_name}")
                        transactions = self.get_account_transactions(company_id, business_id, account_id)
                        account_transaction_count = len(transactions.get('edges', []))
                        transaction_count += account_transaction_count
                        print(f"Found {account_transaction_count} transactions for {account_name}")
                        
                        # Sync transactions for this account
                        success, debug_info = self.dw_service.sync_account_transactions(company_id, transactions, account_id)
                        if not success:
                            print(f"Warning: Failed to sync transactions for account {account_name}: {'; '.join(debug_info)}")
                        else:
                            print(f"Synced transactions for {account_name}")
                    except Exception as e:
                        print(f"Warning: Could not fetch transactions for account {account_name}: {e}")
            
            print(f"Account transactions sync completed: {transaction_count} total transactions")
            
            print(f"Wave data sync completed: {customer_count} customers, {invoice_count} invoices, {product_count} products, {bill_count} bills, {account_count} accounts, {transaction_count} transactions")
            return True
            
        except Exception as e:
            print(f"ERROR: Wave data sync failed: {e}")
            import traceback
            traceback.print_exc()
            raise
