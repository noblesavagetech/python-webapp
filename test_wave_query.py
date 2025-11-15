#!/usr/bin/env python3
"""Test Wave GraphQL queries to see exact errors"""

import os
import sys
from app import create_app
from models.wave_token import WaveToken
from services.wave_service import WaveService

app = create_app()

with app.app_context():
    # Get the first wave token
    token = WaveToken.query.first()
    if not token:
        print("No Wave token found. Please connect Wave first.")
        sys.exit(1)
    
    print(f"Found token for company: {token.company_id}")
    
    wave_service = WaveService(app.config)
    
    # Test business info query
    print("\n=== Testing Business Info Query ===")
    try:
        result = wave_service.get_business_info(token.company_id)
        print(f"Success: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test customers query
    print("\n=== Testing Customers Query ===")
    try:
        business_id = "test"  # Won't be used with new query
        result = wave_service.get_customers(token.company_id, business_id)
        print(f"Success: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test invoices query
    print("\n=== Testing Invoices Query ===")
    try:
        business_id = "test"  # Won't be used with new query
        result = wave_service.get_invoices(token.company_id, business_id)
        print(f"Success: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
