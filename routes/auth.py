from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.company import Company

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register new company and admin user"""
    current_app.logger.info('Signup endpoint hit')
    try:
        data = request.get_json()
        current_app.logger.info(f'Signup data: {data}')
        
        # Validate required fields
        required_fields = ['company_name', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if Company.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Company email already registered'}), 400
        
        # Create company
        company = Company(
            name=data['company_name'],
            email=data['email'],
            industry=data.get('industry'),
            size=data.get('company_size')
        )
        db.session.add(company)
        db.session.flush()  # Get company ID
        
        # Create admin user
        user = User(
            company_id=company.id,
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role='admin'
        )
        user.set_password(data['password'])
        db.session.add(user)
        
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Company and user created successfully',
            'access_token': access_token,
            'user': user.to_dict(),
            'company': company.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict(),
            'company': user.company.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'company': user.company.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
