#!/bin/bash

# Create sample questionnaire in database
python3 << 'EOF'
from app import create_app, db
from models.questionnaire import Questionnaire
import json

app = create_app()

with app.app_context():
    # Check if questionnaire exists
    existing = Questionnaire.query.filter_by(is_active=True).first()
    
    if not existing:
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
            is_active=True
        )
        
        db.session.add(questionnaire)
        db.session.commit()
        
        print('Sample questionnaire created successfully!')
    else:
        print('Active questionnaire already exists.')

EOF
