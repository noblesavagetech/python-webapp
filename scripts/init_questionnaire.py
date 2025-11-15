#!/usr/bin/env python3
"""
Initialize the questionnaire in the database
"""
import os
import sys

# Add parent directory to Python path for Railway
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.questionnaire import Questionnaire

app = create_app()
with app.app_context():
    # Check if active questionnaire exists
    active = Questionnaire.query.filter_by(is_active=True).first()
    
    if active:
        print(f'Active questionnaire found: {active.title}')
        print(f'Number of questions: {len(active.questions)}')
    else:
        print('No active questionnaire found. Creating one...')
        
        # Create sample questionnaire with the questions from the JS file
        questions = [
            {
                'id': 'q1',
                'text': 'What is your current monthly revenue?',
                'type': 'numeric',
                'max_value': 1000000,
                'weight': 2,
                'unit': '$'
            },
            {
                'id': 'q2',
                'text': 'How many months of operating expenses do you have in cash reserves?',
                'type': 'numeric',
                'max_value': 12,
                'weight': 2,
                'unit': 'months'
            },
            {
                'id': 'q3',
                'text': 'What percentage of your invoices are paid within 30 days?',
                'type': 'numeric',
                'max_value': 100,
                'weight': 1.5,
                'unit': '%'
            },
            {
                'id': 'q4',
                'text': 'Do you have a formal budget in place?',
                'type': 'boolean',
                'weight': 1,
                'positive_answer': True
            },
            {
                'id': 'q5',
                'text': 'How often do you review your financial statements?',
                'type': 'multiple_choice',
                'weight': 1.5,
                'options': [
                    {'value': 'daily', 'label': 'Daily', 'score': 100},
                    {'value': 'weekly', 'label': 'Weekly', 'score': 80},
                    {'value': 'monthly', 'label': 'Monthly', 'score': 60},
                    {'value': 'quarterly', 'label': 'Quarterly', 'score': 40},
                    {'value': 'annually', 'label': 'Annually or Less', 'score': 20}
                ]
            },
            {
                'id': 'q6',
                'text': 'What is your current debt-to-income ratio?',
                'type': 'multiple_choice',
                'weight': 2,
                'options': [
                    {'value': 'below_25', 'label': 'Below 25%', 'score': 100},
                    {'value': '25_50', 'label': '25-50%', 'score': 75},
                    {'value': '50_75', 'label': '50-75%', 'score': 50},
                    {'value': 'above_75', 'label': 'Above 75%', 'score': 25}
                ]
            },
            {
                'id': 'q7',
                'text': 'Do you use accounting software to track your finances?',
                'type': 'boolean',
                'weight': 1,
                'positive_answer': True
            },
            {
                'id': 'q8',
                'text': 'What is your average profit margin?',
                'type': 'numeric',
                'max_value': 100,
                'weight': 2,
                'unit': '%'
            }
        ]
        
        questionnaire = Questionnaire(
            title='Financial Health Assessment',
            description='Comprehensive assessment of your business financial health',
            questions=questions,
            version=1,
            is_active=True
        )
        
        db.session.add(questionnaire)
        db.session.commit()
        
        print(f'✓ Created questionnaire: {questionnaire.title}')
        print(f'✓ ID: {questionnaire.id}')
        print(f'✓ Questions: {len(questions)}')
