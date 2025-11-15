# Financial Health Scoring Matrix

## Overview
The BBA Services Financial Health Assessment uses a comprehensive 3-tier classification system combined with a simplified 1-10 rating scale.

## Scoring Methodology

### Raw Score Calculation (0-100)
Each question in the assessment contributes to an overall raw score based on:

1. **Numeric Questions** - Normalized against maximum value
   - Example: Revenue of $50,000 with max $1,000,000 = 5% of max
   
2. **Multiple Choice Questions** - Pre-assigned score values
   - Each option has a specific score (e.g., Daily = 100, Weekly = 80, etc.)
   
3. **Boolean (Yes/No) Questions** - Binary scoring
   - Positive answer = 100 points
   - Negative answer = 0 points

4. **Weighted Average** - Each question has a weight multiplier
   - Critical questions (e.g., revenue, debt ratio) have weight of 2.0
   - Important questions (e.g., cash reserves) have weight of 1.5
   - Standard questions have weight of 1.0

### Final Score Calculation
```
Final Score = (Sum of all weighted scores) / (Sum of all weights)
```

## 3-Tier Classification System

### Tier 1: Developing (0-33%)
**Status:** Building Foundation
- **Characteristics:**
  - Early-stage business or startup
  - Establishing basic financial processes
  - Limited cash reserves (0-3 months)
  - Inconsistent revenue patterns
  - Minimal financial tracking systems
  
- **1-10 Scale Range:** 1-3
  - 0-10% = Score of 1
  - 11-20% = Score of 2
  - 21-33% = Score of 3

- **Recommendations:**
  - Implement basic accounting software
  - Establish monthly financial review process
  - Build emergency cash reserves
  - Create formal budget
  - Focus on consistent revenue generation

### Tier 2: Stable (34-66%)
**Status:** Solid Foundation
- **Characteristics:**
  - Consistent revenue streams
  - Regular financial monitoring
  - Adequate cash reserves (3-6 months)
  - Using accounting software
  - Solid debt management strategies in place
  
- **1-10 Scale Range:** 4-6
  - 34-43% = Score of 4
  - 44-53% = Score of 5
  - 54-66% = Score of 6

- **Recommendations:**
  - Optimize debt-to-income ratio
  - Increase cash reserves to 6+ months
  - Implement weekly financial reviews
  - Improve invoice collection processes
  - Develop growth strategies

### Tier 3: Optimized (67-100%)
**Status:** Excellent Health
- **Characteristics:**
  - Strong, predictable revenue
  - Robust cash reserves (6+ months)
  - Daily/weekly financial monitoring
  - Healthy profit margins
  - Low debt-to-income ratio (<25%)
  - Advanced financial planning
  
- **1-10 Scale Range:** 7-10
  - 67-76% = Score of 7
  - 77-86% = Score of 8
  - 87-96% = Score of 9
  - 97-100% = Score of 10

- **Recommendations:**
  - Maintain excellence
  - Explore expansion opportunities
  - Consider advanced financial instruments
  - Mentor other businesses
  - Plan for long-term sustainability

## Score Display Format

When a user completes the assessment, they receive:

1. **Primary Score** - Large 0-100 number (e.g., "72.5 out of 100")
2. **Tier Classification** - Name and description (e.g., "Optimized - Excellent health")
3. **Secondary Rating** - Simplified 1-10 score (e.g., "7/10 Rating")

### Example Score Display:

```
┌─────────────────────────────────┐
│        72.5 out of 100          │
│                                 │
│         ┌─────────────┐         │
│         │  Optimized  │         │
│         │  Excellent  │         │
│         │   health    │         │
│         └─────────────┘         │
│                                 │
│         7/10 Rating             │
└─────────────────────────────────┘
```

## Question Weights

| Question | Topic | Weight | Rationale |
|----------|-------|--------|-----------|
| Q1 | Monthly Revenue | 2.0 | Critical business metric |
| Q2 | Cash Reserves | 2.0 | Financial stability indicator |
| Q3 | Invoice Payment Rate | 1.5 | Cash flow health |
| Q4 | Formal Budget | 1.0 | Basic financial discipline |
| Q5 | Financial Review Frequency | 1.5 | Proactive management |
| Q6 | Debt-to-Income Ratio | 2.0 | Financial leverage/risk |
| Q7 | Accounting Software | 1.0 | Process maturity |
| Q8 | Profit Margin | 2.0 | Business sustainability |

**Total Weight:** 12.0

## Conversion Formula

### Raw Score (0-100) to 1-10 Scale:
```python
score_1_to_10 = min(10, max(1, int((raw_score / 10) + 0.5)))
```

This formula:
- Divides raw score by 10 to get base number
- Adds 0.5 for rounding
- Converts to integer
- Ensures result is between 1-10

### Examples:
- 5% raw → 1/10
- 15% raw → 2/10
- 45% raw → 5/10
- 72% raw → 7/10
- 95% raw → 10/10

## API Response Format

```json
{
  "message": "Questionnaire submitted successfully",
  "score": 72.5,
  "score_out_of_10": 7,
  "tier": "Optimized",
  "tier_description": "Best-in-class practices",
  "response": {
    "id": "uuid-here",
    "company_id": "company-uuid",
    "questionnaire_id": "questionnaire-uuid",
    "answers": {...},
    "score": 72.5,
    "completed_at": "2025-11-15T14:35:00Z"
  }
}
```

## Future Enhancements

1. **Industry Benchmarks** - Compare scores against industry averages
2. **Trend Analysis** - Track score changes over time
3. **Personalized Recommendations** - AI-driven improvement suggestions
4. **Sub-scores** - Break down into categories (cash flow, profitability, efficiency)
5. **Goal Setting** - Set target scores and track progress
