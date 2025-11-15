// Sample questionnaire data - in production, this would come from API
const sampleQuestions = [
    {
        id: 'q1',
        text: 'What is your current monthly revenue?',
        type: 'numeric',
        max_value: 1000000,
        weight: 2,
        unit: '$'
    },
    {
        id: 'q2',
        text: 'How many months of operating expenses do you have in cash reserves?',
        type: 'numeric',
        max_value: 12,
        weight: 2,
        unit: 'months'
    },
    {
        id: 'q3',
        text: 'What percentage of your invoices are paid within 30 days?',
        type: 'numeric',
        max_value: 100,
        weight: 1.5,
        unit: '%'
    },
    {
        id: 'q4',
        text: 'Do you have a formal budget in place?',
        type: 'boolean',
        weight: 1,
        positive_answer: true
    },
    {
        id: 'q5',
        text: 'How often do you review your financial statements?',
        type: 'multiple_choice',
        weight: 1.5,
        options: [
            { value: 'daily', label: 'Daily', score: 100 },
            { value: 'weekly', label: 'Weekly', score: 80 },
            { value: 'monthly', label: 'Monthly', score: 60 },
            { value: 'quarterly', label: 'Quarterly', score: 40 },
            { value: 'annually', label: 'Annually or Less', score: 20 }
        ]
    },
    {
        id: 'q6',
        text: 'What is your current debt-to-income ratio?',
        type: 'multiple_choice',
        weight: 2,
        options: [
            { value: 'below_25', label: 'Below 25%', score: 100 },
            { value: '25_50', label: '25-50%', score: 75 },
            { value: '50_75', label: '50-75%', score: 50 },
            { value: 'above_75', label: 'Above 75%', score: 25 }
        ]
    },
    {
        id: 'q7',
        text: 'Do you use accounting software to track your finances?',
        type: 'boolean',
        weight: 1,
        positive_answer: true
    },
    {
        id: 'q8',
        text: 'What is your average profit margin?',
        type: 'numeric',
        max_value: 100,
        weight: 2,
        unit: '%'
    }
];

let currentQuestionIndex = 0;
let answers = {};
let questionnaireId = null;

document.addEventListener('DOMContentLoaded', async () => {
    requireAuth();

    const form = document.getElementById('questionnaireForm');
    const questionsContainer = document.getElementById('questionsContainer');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('error-message');

    try {
        // Load questionnaire from API
        const questionnaire = await apiRequest('/questionnaire/active', 'GET');
        questionnaireId = questionnaire.id;
        
        // For demo, use sample questions if API doesn't return questions
        const questions = questionnaire.questions && questionnaire.questions.length > 0 
            ? questionnaire.questions 
            : sampleQuestions;

        // Render first question
        renderQuestion(questions[currentQuestionIndex]);
        updateProgress();

        // Navigation handlers
        prevBtn.addEventListener('click', () => {
            if (currentQuestionIndex > 0) {
                saveCurrentAnswer(questions[currentQuestionIndex]);
                currentQuestionIndex--;
                renderQuestion(questions[currentQuestionIndex]);
                updateProgress();
                updateNavigationButtons(questions.length);
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentQuestionIndex < questions.length - 1) {
                if (saveCurrentAnswer(questions[currentQuestionIndex])) {
                    currentQuestionIndex++;
                    renderQuestion(questions[currentQuestionIndex]);
                    updateProgress();
                    updateNavigationButtons(questions.length);
                }
            }
        });

        // Form submit
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            errorMessage.style.display = 'none';

            // Save last answer
            if (!saveCurrentAnswer(questions[currentQuestionIndex])) {
                return;
            }

            try {
                // Submit questionnaire
                const result = await apiRequest('/questionnaire/submit', 'POST', {
                    questionnaire_id: questionnaireId,
                    answers: answers
                });

                // Show success message with all score details
                document.getElementById('questionnaireForm').style.display = 'none';
                
                // Update score display
                const scoreDisplay = document.getElementById('scoreDisplay');
                scoreDisplay.innerHTML = `
                    <div class="score-details">
                        <div class="score-primary">
                            <span class="score-number">${result.score.toFixed(1)}</span>
                            <span class="score-label">out of 100</span>
                        </div>
                        <div class="score-tier">
                            <span class="tier-name">${result.tier}</span>
                            <span class="tier-description">${result.tier_description}</span>
                        </div>
                        <div class="score-secondary">
                            ${result.score_out_of_10}/10 Rating
                        </div>
                    </div>
                `;
                
                document.getElementById('successMessage').style.display = 'block';
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
            }
        });

        updateNavigationButtons(questions.length);
    } catch (error) {
        errorMessage.textContent = 'Failed to load questionnaire: ' + error.message;
        errorMessage.style.display = 'block';
    }
});

function renderQuestion(question) {
    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';

    const questionDiv = document.createElement('div');
    questionDiv.className = 'form-group';

    const label = document.createElement('label');
    label.textContent = question.text;
    questionDiv.appendChild(label);

    let input;

    switch (question.type) {
        case 'numeric':
            input = document.createElement('input');
            input.type = 'number';
            input.id = 'answer_' + question.id;
            input.name = question.id;
            input.required = true;
            input.min = '0';
            if (question.max_value) {
                input.max = question.max_value;
            }
            if (answers[question.id] !== undefined) {
                input.value = answers[question.id];
            }
            if (question.unit) {
                const inputGroup = document.createElement('div');
                inputGroup.style.display = 'flex';
                inputGroup.style.gap = '0.5rem';
                inputGroup.style.alignItems = 'center';
                inputGroup.appendChild(input);
                const unitSpan = document.createElement('span');
                unitSpan.textContent = question.unit;
                inputGroup.appendChild(unitSpan);
                questionDiv.appendChild(inputGroup);
            } else {
                questionDiv.appendChild(input);
            }
            break;

        case 'boolean':
            const radioGroup = document.createElement('div');
            radioGroup.style.display = 'flex';
            radioGroup.style.gap = '1rem';
            
            const yesLabel = document.createElement('label');
            const yesInput = document.createElement('input');
            yesInput.type = 'radio';
            yesInput.name = question.id;
            yesInput.value = 'true';
            yesInput.required = true;
            if (answers[question.id] === true) {
                yesInput.checked = true;
            }
            yesLabel.appendChild(yesInput);
            yesLabel.appendChild(document.createTextNode(' Yes'));
            
            const noLabel = document.createElement('label');
            const noInput = document.createElement('input');
            noInput.type = 'radio';
            noInput.name = question.id;
            noInput.value = 'false';
            noInput.required = true;
            if (answers[question.id] === false) {
                noInput.checked = true;
            }
            noLabel.appendChild(noInput);
            noLabel.appendChild(document.createTextNode(' No'));
            
            radioGroup.appendChild(yesLabel);
            radioGroup.appendChild(noLabel);
            questionDiv.appendChild(radioGroup);
            break;

        case 'multiple_choice':
            input = document.createElement('select');
            input.id = 'answer_' + question.id;
            input.name = question.id;
            input.required = true;
            
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select an option';
            input.appendChild(defaultOption);
            
            question.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                if (answers[question.id] === option.value) {
                    optionElement.selected = true;
                }
                input.appendChild(optionElement);
            });
            
            questionDiv.appendChild(input);
            break;
    }

    container.appendChild(questionDiv);
}

function saveCurrentAnswer(question) {
    let value;

    switch (question.type) {
        case 'numeric':
            const numInput = document.querySelector(`input[name="${question.id}"]`);
            if (!numInput.value) {
                alert('Please answer the question');
                return false;
            }
            value = parseFloat(numInput.value);
            break;

        case 'boolean':
            const radioInput = document.querySelector(`input[name="${question.id}"]:checked`);
            if (!radioInput) {
                alert('Please answer the question');
                return false;
            }
            value = radioInput.value === 'true';
            break;

        case 'multiple_choice':
            const selectInput = document.querySelector(`select[name="${question.id}"]`);
            if (!selectInput.value) {
                alert('Please answer the question');
                return false;
            }
            value = selectInput.value;
            break;
    }

    answers[question.id] = value;
    return true;
}

function updateProgress() {
    const totalQuestions = sampleQuestions.length;
    const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
}

function updateNavigationButtons(totalQuestions) {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    prevBtn.style.display = currentQuestionIndex > 0 ? 'block' : 'none';
    
    if (currentQuestionIndex < totalQuestions - 1) {
        nextBtn.style.display = 'block';
        submitBtn.style.display = 'none';
    } else {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'block';
    }
}
