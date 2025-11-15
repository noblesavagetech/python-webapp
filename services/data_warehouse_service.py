import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime


class DataWarehouseService:
    """Service for syncing data to the data warehouse"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
    
    def get_connection(self):
        """Get or create database connection"""
        if not self.connection or self.connection.closed:
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
                invoices.append((
                    node['id'],
                    company_id,
                    node.get('invoiceNumber'),
                    customer.get('id'),
                    customer.get('name'),
                    node.get('total'),
                    node.get('status'),
                    node.get('createdAt'),
                    node.get('dueDate'),
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
