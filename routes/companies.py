from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.company import Company
from models.user import User

companies_bp = Blueprint('companies', __name__)


@companies_bp.route('/<company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    """Get company details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify user belongs to this company
        if user.company_id != company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        return jsonify(company.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@companies_bp.route('/<company_id>', methods=['PUT'])
@jwt_required()
def update_company(company_id):
    """Update company details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        if user.company_id != company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            company.name = data['name']
        if 'industry' in data:
            company.industry = data['industry']
        if 'size' in data:
            company.size = data['size']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Company updated successfully',
            'company': company.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@companies_bp.route('/<company_id>/users', methods=['GET'])
@jwt_required()
def get_company_users(company_id):
    """Get all users for a company"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.company_id != company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        users = [u.to_dict() for u in company.users.all()]
        
        return jsonify({'users': users}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
