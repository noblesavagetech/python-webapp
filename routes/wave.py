from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from requests_oauthlib import OAuth2Session
from extensions import db
from models.user import User
from models.company import Company
from models.wave_token import WaveToken
from services.wave_service import WaveService
from datetime import datetime, timedelta
import requests

wave_bp = Blueprint('wave', __name__)


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
    """Handle Wave OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')  # This is company_id
        
        if not code or not state:
            return jsonify({'error': 'Missing code or state'}), 400
        
        company = Company.query.get(state)
        if not company:
            return jsonify({'error': 'Invalid state'}), 400
        
        # Exchange code for token using Basic Auth
        import base64
        
        # Wave expects Basic Auth with client credentials
        auth_string = f"{current_app.config['WAVE_CLIENT_ID']}:{current_app.config['WAVE_CLIENT_SECRET']}"
        auth_bytes = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_bytes}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': current_app.config['WAVE_REDIRECT_URI']
        }
        
        response = requests.post(
            current_app.config['WAVE_TOKEN_URL'],
            data=token_data,
            headers=headers
        )
        
        print(f"Wave token exchange response status: {response.status_code}")
        print(f"Wave token exchange response: {response.text}")
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to exchange token',
                'status': response.status_code,
                'details': response.text
            }), 400
        
        token_response = response.json()
        
        # Calculate expiration
        expires_in = token_response.get('expires_in', 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Store or update token
        wave_token = WaveToken.query.filter_by(company_id=company.id).first()
        if wave_token:
            wave_token.access_token = token_response['access_token']
            wave_token.refresh_token = token_response.get('refresh_token')
            wave_token.expires_at = expires_at
            wave_token.scope = token_response.get('scope')
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
        
        db.session.commit()
        
        # Redirect to dashboard with success message
        return redirect('/dashboard?wave_connected=true')
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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
