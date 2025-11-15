#!/usr/bin/env python3
"""
Check Wave Data Sync Status
Run this script after connecting Wave to see your synced data
"""

from app import create_app
from extensions import db
from sqlalchemy import text

def check_wave_data():
    app = create_app()
    with app.app_context():
        print("🔍 Checking Wave Data Sync Status")
        print("=" * 50)

        # Check for data warehouse tables
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('customers', 'invoices');"))
        dw_tables = [row[0] for row in result.fetchall()]

        if not dw_tables:
            print("❌ No Wave data found!")
            print("\n📋 To get your data:")
            print("1. Go to your app dashboard")
            print("2. Click 'Connect Wave' button")
            print("3. Authorize your Wave account")
            print("4. Click 'Sync Data' button")
            print("5. Run this script again")
            return

        print("✅ Wave data warehouse tables found!")

        # Check customers
        if 'customers' in dw_tables:
            result = db.session.execute(text('SELECT COUNT(*) FROM customers;'))
            customer_count = result.fetchone()[0]
            print(f"\n👥 Customers: {customer_count} records")

            if customer_count > 0:
                result = db.session.execute(text('SELECT name, email FROM customers ORDER BY name LIMIT 10;'))
                print("   Recent customers:")
                for row in result.fetchall():
                    print(f"   - {row[0]} ({row[1]})")

        # Check invoices
        if 'invoices' in dw_tables:
            result = db.session.execute(text('SELECT COUNT(*) FROM invoices;'))
            invoice_count = result.fetchone()[0]
            print(f"\n📄 Invoices: {invoice_count} records")

            if invoice_count > 0:
                result = db.session.execute(text('SELECT invoice_number, customer_name, total, status, created_at FROM invoices ORDER BY created_at DESC LIMIT 10;'))
                print("   Recent invoices:")
                for row in result.fetchall():
                    print(f"   - #{row[0]}: {row[1]} - ${row[2]} ({row[3]}) - {row[4]}")

        # Summary stats
        if 'invoices' in dw_tables:
            print("\n💰 Financial Summary:")
            try:
                result = db.session.execute(text("SELECT SUM(total) as total_revenue, COUNT(*) as invoice_count FROM invoices WHERE status = 'SENT';"))
                row = result.fetchone()
                if row[0]:
                    print(f"   Total Revenue: ${row[0]:.2f} from {row[1]} sent invoices")
            except:
                pass

if __name__ == "__main__":
    check_wave_data()