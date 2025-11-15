import psycopg2
from psycopg2.extras import execute_values
import sqlite3
from datetime import datetime


class DataWarehouseService:
    """Service for syncing data to data warehouse"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
    
    def get_connection(self):
        """Get or create database connection"""
        if not self.connection:
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
        if self.connection:
            try:
                self.connection.close()
            except:
                pass  # Connection might already be closed
            self.connection = None
    
    def sync_customers(self, company_id, customers_data):
        """Sync customer data to data warehouse"""
        conn = None
        debug_info = []
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
            
            debug_info.append(f"Prepared {len(customers)} customers for insertion")
            
            # Upsert customers
            if customers:
                debug_info.append("Executing bulk insert...")
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
                debug_info.append("Bulk insert completed")
            
            conn.commit()
            cursor.close()
            
            return True, debug_info
        except Exception as e:
            debug_info.append(f"Error syncing customers: {e}")
            import traceback
            debug_info.append(traceback.format_exc())
            if conn:
                conn.rollback()
            return False, debug_info
    
    def sync_invoices(self, company_id, invoices_data):
        """Sync invoice data to data warehouse"""
        conn = None
        debug_info = []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if we're using SQLite
            is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in str(type(conn)) else False
            debug_info.append(f"Using database type: {'SQLite' if is_sqlite else 'PostgreSQL'}")
            
            # Create table if not exists
            if is_sqlite:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS invoices (
                        id TEXT PRIMARY KEY,
                        company_id TEXT NOT NULL,
                        invoice_number TEXT,
                        customer_id TEXT,
                        customer_name TEXT,
                        total REAL,
                        status TEXT,
                        created_at TEXT,
                        due_date TEXT,
                        synced_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
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
                debug_info.append(f"total_obj = {total_obj}, type = {type(total_obj)}")
                
                if isinstance(total_obj, dict):
                    total_value = total_obj.get('value')
                    debug_info.append(f"total_value from dict = {total_value}, type = {type(total_value)}")
                else:
                    total_value = total_obj
                    debug_info.append(f"total_value direct = {total_value}, type = {type(total_value)}")
                
                # Convert total to float if it's a string or int
                if isinstance(total_value, (str, int)):
                    try:
                        total_value = float(total_value)
                    except (ValueError, TypeError) as e:
                        debug_info.append(f"Failed to convert total_value {total_value} to float: {e}")
                        total_value = 0.0
                elif total_value is None:
                    total_value = 0.0
                
                debug_info.append(f"final total_value = {total_value}, type = {type(total_value)}")
                
                # Parse dates
                created_at = node.get('createdAt')
                due_date = node.get('dueDate')
                
                debug_info.append(f"created_at = {created_at}, due_date = {due_date}")
                
                # Convert dates to strings for SQLite compatibility
                if created_at:
                    if hasattr(created_at, 'isoformat'):
                        created_at = created_at.isoformat()
                    elif isinstance(created_at, str):
                        pass  # Already a string
                    else:
                        created_at = str(created_at)
                
                if due_date:
                    if hasattr(due_date, 'isoformat'):
                        due_date = due_date.isoformat()
                    elif hasattr(due_date, 'strftime'):
                        due_date = due_date.strftime('%Y-%m-%d')
                    elif isinstance(due_date, str):
                        pass  # Already a string
                    else:
                        due_date = str(due_date)
                
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
                    datetime.utcnow().isoformat()
                ))
            
            debug_info.append(f"Prepared {len(invoices)} invoices for insertion")
            
            # Insert data
            if invoices:
                if is_sqlite:
                    debug_info.append("Using SQLite insertion...")
                    # Use SQLite-compatible insertion
                    cursor.executemany("""
                        INSERT OR REPLACE INTO invoices 
                        (id, company_id, invoice_number, customer_id, customer_name, total, status, created_at, due_date, synced_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, invoices)
                else:
                    debug_info.append("Using PostgreSQL insertion...")
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
                debug_info.append("Bulk insert completed")
            
            conn.commit()
            cursor.close()
            
            return True, debug_info
        except Exception as e:
            debug_info.append(f"Error syncing invoices: {e}")
            import traceback
            debug_info.append(traceback.format_exc())
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False, debug_info
    
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

    def sync_products(self, company_id, products_data):
        """Sync product data to data warehouse"""
        conn = None
        debug_info = []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if we're using SQLite
            is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in str(type(conn)) else False
            
            # Create table if not exists
            if is_sqlite:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id TEXT PRIMARY KEY,
                        company_id TEXT NOT NULL,
                        name TEXT,
                        description TEXT,
                        unit_price REAL,
                        income_account_id TEXT,
                        income_account_name TEXT,
                        synced_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id VARCHAR(255) PRIMARY KEY,
                        company_id VARCHAR(36) NOT NULL,
                        name VARCHAR(255),
                        description TEXT,
                        unit_price DECIMAL(15, 2),
                        income_account_id VARCHAR(255),
                        income_account_name VARCHAR(255),
                        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            # Prepare data for insertion
            products = []
            for edge in products_data.get('edges', []):
                node = edge['node']
                unit_price_obj = node.get('unitPrice', {})
                income_account = node.get('incomeAccount', {})
                
                # Handle unit price
                if isinstance(unit_price_obj, dict):
                    unit_price = unit_price_obj.get('value', 0)
                else:
                    unit_price = unit_price_obj or 0
                
                products.append((
                    node['id'],
                    company_id,
                    node.get('name'),
                    node.get('description'),
                    float(unit_price) if unit_price else 0.0,
                    income_account.get('id'),
                    income_account.get('name'),
                    datetime.utcnow().isoformat() if is_sqlite else datetime.utcnow()
                ))
            
            # Insert data
            if products:
                if is_sqlite:
                    cursor.executemany("""
                        INSERT OR REPLACE INTO products 
                        (id, company_id, name, description, unit_price, income_account_id, income_account_name, synced_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, products)
                else:
                    execute_values(
                        cursor,
                        """
                        INSERT INTO products (id, company_id, name, description, unit_price, income_account_id, income_account_name, synced_at)
                        VALUES %s
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            description = EXCLUDED.description,
                            unit_price = EXCLUDED.unit_price,
                            income_account_id = EXCLUDED.income_account_id,
                            income_account_name = EXCLUDED.income_account_name,
                            synced_at = EXCLUDED.synced_at
                        """,
                        products
                    )
            
            conn.commit()
            cursor.close()
            
            return True, debug_info
        except Exception as e:
            debug_info.append(f"Error syncing products: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False, debug_info

    def sync_bills(self, company_id, bills_data):
        """Sync bill/expense data to data warehouse"""
        conn = None
        debug_info = []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if we're using SQLite
            is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in str(type(conn)) else False
            
            # Create table if not exists
            if is_sqlite:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bills (
                        id TEXT PRIMARY KEY,
                        company_id TEXT NOT NULL,
                        bill_number TEXT,
                        vendor_id TEXT,
                        vendor_name TEXT,
                        total REAL,
                        status TEXT,
                        due_date TEXT,
                        created_at TEXT,
                        synced_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bills (
                        id VARCHAR(255) PRIMARY KEY,
                        company_id VARCHAR(36) NOT NULL,
                        bill_number VARCHAR(100),
                        vendor_id VARCHAR(255),
                        vendor_name VARCHAR(255),
                        total DECIMAL(15, 2),
                        status VARCHAR(50),
                        due_date DATE,
                        created_at TIMESTAMP,
                        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            # Prepare data for insertion
            bills = []
            for edge in bills_data.get('edges', []):
                node = edge['node']
                vendor = node.get('vendor', {})
                total_obj = node.get('total', {})
                
                # Handle total
                if isinstance(total_obj, dict):
                    total = total_obj.get('value', 0)
                else:
                    total = total_obj or 0
                
                # Handle dates
                created_at = node.get('createdAt')
                due_date = node.get('dueDate')
                
                if created_at and not is_sqlite:
                    if hasattr(created_at, 'isoformat'):
                        created_at = created_at.isoformat()
                if due_date and not is_sqlite:
                    if hasattr(due_date, 'isoformat'):
                        due_date = due_date.isoformat()
                
                bills.append((
                    node['id'],
                    company_id,
                    node.get('billNumber'),
                    vendor.get('id'),
                    vendor.get('name'),
                    float(total) if total else 0.0,
                    node.get('status'),
                    due_date,
                    created_at,
                    datetime.utcnow().isoformat() if is_sqlite else datetime.utcnow()
                ))
            
            # Insert data
            if bills:
                if is_sqlite:
                    cursor.executemany("""
                        INSERT OR REPLACE INTO bills 
                        (id, company_id, bill_number, vendor_id, vendor_name, total, status, due_date, created_at, synced_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, bills)
                else:
                    execute_values(
                        cursor,
                        """
                        INSERT INTO bills (id, company_id, bill_number, vendor_id, vendor_name, total, status, due_date, created_at, synced_at)
                        VALUES %s
                        ON CONFLICT (id) DO UPDATE SET
                            bill_number = EXCLUDED.bill_number,
                            vendor_id = EXCLUDED.vendor_id,
                            vendor_name = EXCLUDED.vendor_name,
                            total = EXCLUDED.total,
                            status = EXCLUDED.status,
                            due_date = EXCLUDED.due_date,
                            synced_at = EXCLUDED.synced_at
                        """,
                        bills
                    )
            
            conn.commit()
            cursor.close()
            
            return True, debug_info
        except Exception as e:
            debug_info.append(f"Error syncing bills: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False, debug_info
