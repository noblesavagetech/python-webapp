import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime


class DataWarehouseService:
    """Service for syncing data to data warehouse"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
    
    def get_connection(self):
        """Get or create database connection"""
        if not self.connection or self.connection.closed:
            # Try to use the main app database if DW config is default
            if (self.config.get('DW_HOST') == 'localhost' and 
                self.config.get('DW_DATABASE') == 'financial_dw'):
                # Use main app database connection
                main_db_url = self.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///financial_health.db')
                if main_db_url.startswith('postgresql'):
                    # Parse PostgreSQL URL
                    import re
                    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', main_db_url)
                    if match:
                        user, password, host, port, database = match.groups()
                        self.connection = psycopg2.connect(
                            host=host,
                            port=int(port),
                            database=database,
                            user=user,
                            password=password
                        )
                    else:
                        # Fallback to SQLite for development
                        import sqlite3
                        self.connection = sqlite3.connect('financial_health.db')
                else:
                    # SQLite fallback
                    import sqlite3
                    self.connection = sqlite3.connect('financial_health.db')
            else:
                # Use configured DW settings
                self.connection = psycopg2.connect(
                    host=self.config['DW_HOST'],
                    port=self.config['DW_PORT'],
                    database=self.config['DW_DATABASE'],
                    user=self.config['DW_USER'],
                    password=self.config['DW_PASSWORD']
                )
        return self.connection
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
    
    def sync_customers(self, company_id, customers_data):
        """Sync customer data to data warehouse"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id VARCHAR(255) PRIMARY KEY,
                    company_id VARCHAR(36) NOT NULL,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    created_at TIMESTAMP,
                    modified_at TIMESTAMP,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Prepare data for insertion
            customers = []
            for edge in customers_data.get('edges', []):
                node = edge['node']
                customers.append((
                    node['id'],
                    company_id,
                    node.get('name'),
                    node.get('email'),
                    node.get('createdAt'),
                    node.get('modifiedAt'),
                    datetime.utcnow()
                ))
            
            # Upsert customers
            if customers:
                execute_values(
                    cursor,
                    """
                    INSERT INTO customers (id, company_id, name, email, created_at, modified_at, synced_at)
                    VALUES %s
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        modified_at = EXCLUDED.modified_at,
                        synced_at = EXCLUDED.synced_at
                    """,
                    customers
                )
            
            conn.commit()
            cursor.close()
            
            return True
        except Exception as e:
            print(f"Error syncing customers: {e}")
            if conn:
                conn.rollback()
            return False
    
    def sync_invoices(self, company_id, invoices_data):
        """Sync invoice data to data warehouse"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
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
                )
            """)
            
            # Prepare data for insertion
            invoices = []
            for edge in invoices_data.get('edges', []):
                node = edge['node']
                customer = node.get('customer', {})
                
                # Handle total as an object with value and currency
                total_obj = node.get('total', {})
                print(f"DEBUG: total_obj = {total_obj}, type = {type(total_obj)}")
                
                if isinstance(total_obj, dict):
                    total_value = total_obj.get('value')
                    print(f"DEBUG: total_value from dict = {total_value}, type = {type(total_value)}")
                else:
                    total_value = total_obj
                    print(f"DEBUG: total_value direct = {total_value}, type = {type(total_value)}")
                
                # Convert total to float if it's a string or int
                if isinstance(total_value, (str, int)):
                    try:
                        total_value = float(total_value)
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG: Failed to convert total_value {total_value} to float: {e}")
                        total_value = 0.0
                elif total_value is None:
                    total_value = 0.0
                
                print(f"DEBUG: final total_value = {total_value}, type = {type(total_value)}")
                
                # Parse dates
                created_at = node.get('createdAt')
                due_date = node.get('dueDate')
                
                print(f"DEBUG: created_at = {created_at}, due_date = {due_date}")
                
                # Convert ISO date strings to datetime objects if needed
                if isinstance(created_at, str):
                    try:
                        from dateutil import parser
                        created_at = parser.parse(created_at)
                    except Exception as e:
                        print(f"DEBUG: Failed to parse created_at {created_at}: {e}")
                        created_at = None
                
                if isinstance(due_date, str):
                    try:
                        from dateutil import parser
                        due_date = parser.parse(due_date).date()
                    except Exception as e:
                        print(f"DEBUG: Failed to parse due_date {due_date}: {e}")
                        due_date = None
                
                invoices.append((
                    node['id'],
                    company_id,
                    node.get('invoiceNumber'),
                    customer.get('id'),
                    customer.get('name'),
                    total_value,
                    node.get('status'),
                    created_at,
                    due_date,
                    datetime.utcnow()
                ))
            
            # Upsert invoices
            if invoices:
                execute_values(
                    cursor,
                    """
                    INSERT INTO invoices (id, company_id, invoice_number, customer_id, customer_name, 
                                        total, status, created_at, due_date, synced_at)
                    VALUES %s
                    ON CONFLICT (id) DO UPDATE SET
                        invoice_number = EXCLUDED.invoice_number,
                        customer_id = EXCLUDED.customer_id,
                        customer_name = EXCLUDED.customer_name,
                        total = EXCLUDED.total,
                        status = EXCLUDED.status,
                        due_date = EXCLUDED.due_date,
                        synced_at = EXCLUDED.synced_at
                    """,
                    invoices
                )
            
            conn.commit()
            cursor.close()
            
            return True
        except Exception as e:
            print(f"Error syncing invoices: {e}")
            import traceback
            traceback.print_exc()
            if conn:
                conn.rollback()
            return False
    
    def get_company_metrics(self, company_id):
        """Get aggregated financial metrics for a company"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_invoices,
                    SUM(CASE WHEN status = 'PAID' THEN total ELSE 0 END) as total_revenue,
                    SUM(CASE WHEN status = 'UNPAID' THEN total ELSE 0 END) as outstanding_amount,
                    COUNT(DISTINCT customer_id) as total_customers
                FROM invoices
                WHERE company_id = %s
            """, (company_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'total_invoices': result[0],
                    'total_revenue': float(result[1]) if result[1] else 0,
                    'outstanding_amount': float(result[2]) if result[2] else 0,
                    'total_customers': result[3]
                }
            
            return None
        except Exception as e:
            print(f"Error getting company metrics: {e}")
            return None
