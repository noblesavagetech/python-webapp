from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.company import Company
from models.questionnaire import Questionnaire, QuestionnaireResponse
from datetime import datetime

questionnaire_bp = Blueprint('questionnaire', __name__)


@questionnaire_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_questionnaire():
    """Get the active questionnaire template"""
    try:
        questionnaire = Questionnaire.query.filter_by(is_active=True).first()
        
        if not questionnaire:
            return jsonify({'error': 'No active questionnaire found'}), 404
        
        return jsonify(questionnaire.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@questionnaire_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_questionnaire():
    """Submit questionnaire responses"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'questionnaire_id' not in data or 'answers' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        questionnaire = Questionnaire.query.get(data['questionnaire_id'])
        if not questionnaire:
            return jsonify({'error': 'Questionnaire not found'}), 404
        
        # Calculate financial health score (returns dict with raw_score, score_out_of_10, tier, tier_description)
        score_data = calculate_financial_health_score(data['answers'], questionnaire.questions)
        
        # Save response
        response = QuestionnaireResponse(
            company_id=user.company_id,
            questionnaire_id=data['questionnaire_id'],
            answers=data['answers'],
            score=score_data['raw_score']
        )
        db.session.add(response)
        
        # Update company
        company = user.company
        company.questionnaire_completed = True
        company.financial_health_score = score_data['raw_score']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Questionnaire submitted successfully',
            'response': response.to_dict(),
            'score': score_data['raw_score'],
            'score_out_of_10': score_data['score_out_of_10'],
            'tier': score_data['tier'],
            'tier_description': score_data['tier_description']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@questionnaire_bp.route('/responses', methods=['GET'])
@jwt_required()
def get_company_responses():
    """Get all questionnaire responses for current company"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        responses = QuestionnaireResponse.query.filter_by(
            company_id=user.company_id
        ).order_by(QuestionnaireResponse.completed_at.desc()).all()
        
        return jsonify({
            'responses': [r.to_dict() for r in responses]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def calculate_financial_health_score(answers, questions):
    """
    Calculate financial health score based on answers
    Returns a comprehensive score with tier classification and 1-10 rating
    """
    total_score = 0
    total_weight = 0
    
    for question in questions:
        question_id = question.get('id')
        weight = question.get('weight', 1)
        question_type = question.get('type')
        
        if question_id in answers:
            answer = answers[question_id]
            
            # Different scoring logic based on question type
            if question_type == 'numeric':
                # For numeric questions, normalize the score
                max_value = question.get('max_value', 100)
                score = (float(answer) / max_value) * 100 * weight
            elif question_type == 'multiple_choice':
                # Each option has a score value
                options = question.get('options', [])
                selected_option = next((opt for opt in options if opt['value'] == answer), None)
                score = selected_option.get('score', 0) * weight if selected_option else 0
            elif question_type == 'boolean':
                # Boolean questions: yes=100, no=0
                positive_answer = question.get('positive_answer', True)
                score = (100 if answer == positive_answer else 0) * weight
            else:
                score = 0
            
            total_score += score
            total_weight += weight
    
    # Calculate average score (0-100)
    raw_score = (total_score / total_weight) if total_weight > 0 else 0
    
    # Determine tier based on score
    # Tier 1: Developing (0-33) - Building foundation
    # Tier 2: Stable (34-66) - Solid foundation
    # Tier 3: Optimized (67-100) - Excellent health
    if raw_score < 34:
        tier = 'Developing'
        tier_description = 'Building foundation'
    elif raw_score < 67:
        tier = 'Stable'
        tier_description = 'Solid foundation'
    else:
        tier = 'Optimized'
        tier_description = 'Excellent health'
    
    # Convert to 1-10 scale
    # 0-10 -> 1, 11-20 -> 2, etc.
    score_1_to_10 = min(10, max(1, int((raw_score / 10) + 0.5)))
    
    return {
        'raw_score': round(raw_score, 2),
        'score_out_of_10': score_1_to_10,
        'tier': tier,
        'tier_description': tier_description
    }
