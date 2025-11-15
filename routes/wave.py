from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from requests_oauthlib import OAuth2Session

from extensions import db
from models.company import Company
from models.user import User
from models.wave_token import WaveToken
from services.wave_service import WaveService

wave_bp = Blueprint('wave_bp', __name__)


@wave_bp.route('/authorize', methods=['GET'])
@jwt_required()
def authorize():
    """Initiate Wave OAuth flow"""
    try:
        # Check if Wave is configured
        if (current_app.config['WAVE_CLIENT_ID'].startswith('dummy') or 
            current_app.config['WAVE_CLIENT_SECRET'].startswith('dummy')):
            return jsonify({'error': 'Wave Apps integration not configured. Please set WAVE_CLIENT_ID and WAVE_CLIENT_SECRET environment variables.'}), 400
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create OAuth2 session
        oauth = OAuth2Session(
            current_app.config['WAVE_CLIENT_ID'],
            redirect_uri=current_app.config['WAVE_REDIRECT_URI'],
            scope=['business:read', 'customer:read', 'invoice:read', 'user:read']
        )
        
        # Store company_id in state for callback
        authorization_url, state = oauth.authorization_url(
            current_app.config['WAVE_AUTHORIZATION_URL'],
            state=user.company_id
        )
        
        print(f"Generated authorization URL: {authorization_url}")
        print(f"Client ID: {current_app.config['WAVE_CLIENT_ID']}")
        print(f"Redirect URI: {current_app.config['WAVE_REDIRECT_URI']}")
        
        return jsonify({
            'authorization_url': authorization_url,
            'state': state
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wave_bp.route('/callback', methods=['GET'])
def callback():
    """Handle Wave OAuth callback with robust, detailed token exchange."""
    try:
        code = request.args.get('code')
        state = request.args.get('state')  # This is company_id
        
        if not code or not state:
            print("ERROR: Missing code or state in callback.")
            return jsonify({'error': 'Missing code or state from callback'}), 400
        
        company = Company.query.get(state)
        if not company:
            print(f"ERROR: Invalid state. Company with ID '{state}' not found.")
            return jsonify({'error': 'Invalid state: Company not found'}), 400

        # Make a direct HTTP request to Wave's token endpoint with full visibility
        import requests
        
        token_url = current_app.config['WAVE_TOKEN_URL']
        
        # Prepare the token exchange request data
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': current_app.config['WAVE_REDIRECT_URI'],
            'client_id': current_app.config['WAVE_CLIENT_ID'],
            'client_secret': current_app.config['WAVE_CLIENT_SECRET']
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        print("--- Initiating Wave Token Exchange ---")
        print(f"  - Token URL: {token_url}")
        print(f"  - Grant Type: authorization_code")
        print(f"  - Redirect URI: {token_data['redirect_uri']}")
        print(f"  - Client ID: {token_data['client_id'][:10]}...")
        print(f"  - Code: {code[:20]}...")

        try:
            # Make the actual HTTP POST request
            response = requests.post(
                token_url,
                data=token_data,
                headers=headers,
                timeout=10
            )
            
            print(f"  - Response Status: {response.status_code}")
            print(f"  - Response Headers: {dict(response.headers)}")
            print(f"  - Response Body: {response.text}")
            
            # If the response is not successful, return detailed error to browser
            if response.status_code != 200:
                error_details = {
                    'error': 'Wave token endpoint returned an error',
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': response.text,
                    'request_data': {
                        'token_url': token_url,
                        'grant_type': token_data['grant_type'],
                        'redirect_uri': token_data['redirect_uri'],
                        'client_id_prefix': token_data['client_id'][:10],
                        'code_prefix': code[:20]
                    }
                }
                return jsonify(error_details), 500
            
            # Parse the successful response
            token_response = response.json()
            print("SUCCESS: Wave token exchange completed.")

        except requests.exceptions.RequestException as e:
            print("--- ERROR: HTTP Request Failed ---")
            print(f"  - Exception: {e}")
            
            error_details = {
                'error': 'HTTP request to Wave failed',
                'exception_type': type(e).__name__,
                'exception_details': str(e)
            }
            
            if hasattr(e, 'response') and e.response is not None:
                error_details['wave_response'] = {
                    'status_code': e.response.status_code,
                    'headers': dict(e.response.headers),
                    'body': e.response.text
                }
            
            return jsonify(error_details), 500
        
        # Calculate token expiration
        expires_in = token_response.get('expires_in', 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Store or update the token in the database
        wave_token = WaveToken.query.filter_by(company_id=company.id).first()
        if wave_token:
            wave_token.access_token = token_response['access_token']
            wave_token.refresh_token = token_response.get('refresh_token')
            wave_token.expires_at = expires_at
            wave_token.scope = token_response.get('scope')
            print(f"Updated existing Wave token for company {company.id}.")
        else:
            wave_token = WaveToken(
                company_id=company.id,
                access_token=token_response['access_token'],
                refresh_token=token_response.get('refresh_token'),
                token_type=token_response.get('token_type', 'Bearer'),
                expires_at=expires_at,
                scope=token_response.get('scope')
            )
            db.session.add(wave_token)
            print(f"Created new Wave token for company {company.id}.")
        
        db.session.commit()
        
        # Redirect to the frontend dashboard with a success indicator
        frontend_url = current_app.config.get('FRONTEND_URL', '/')
        print(f"Redirecting to frontend: {frontend_url}/dashboard?wave_connected=true")
        return redirect(f"{frontend_url}/dashboard?wave_connected=true")
        
    except Exception as e:
        db.session.rollback()
        print(f"--- FATAL ERROR in /callback: {e} ---")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An unexpected server error occurred.'}), 500


@wave_bp.route('/status', methods=['GET'])
@jwt_required()
def get_wave_status():
    """Check if Wave is connected for current company"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        wave_token = WaveToken.query.filter_by(company_id=user.company_id).first()
        
        if not wave_token:
            return jsonify({
                'connected': False,
                'message': 'Wave not connected'
            }), 200
        
        return jsonify({
            'connected': True,
            'token': wave_token.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wave_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_wave_data():
    """Manually trigger Wave data sync"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        wave_token = WaveToken.query.filter_by(company_id=user.company_id).first()
        if not wave_token:
            return jsonify({'error': 'Wave not connected'}), 400
        
        # Use WaveService to sync data
        wave_service = WaveService(current_app.config)
        success = wave_service.sync_company_data(user.company_id)
        
        if success:
            return jsonify({'message': 'Data sync initiated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to sync data'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wave_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect_wave():
    """Disconnect Wave integration"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        wave_token = WaveToken.query.filter_by(company_id=user.company_id).first()
        if wave_token:
            db.session.delete(wave_token)
            db.session.commit()
        
        return jsonify({'message': 'Wave disconnected successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
