from app.api.schemas import RiskAssessmentResponseSchema

class RiskAssessmentService:
    @staticmethod
    def assess_risk_helper(credit_score: int, income: float, loan_amount: float, employment_status: str, loan_purpose: str) -> RiskAssessmentResponseSchema:
        # Calculate debt-to-income ratio
        debt_to_income_ratio = loan_amount / income

        # Assign risk score based on predefined criteria
        risk_score = 0

        # Credit score contribution
        if credit_score < 580:
            risk_score += 5
        elif credit_score < 670:
            risk_score += 3
        elif credit_score < 740:
            risk_score += 1
        else:
            risk_score -= 1

        # Debt-to-income ratio contribution
        if debt_to_income_ratio > 0.5:
            risk_score += 5
        elif debt_to_income_ratio > 0.35:
            risk_score += 3
        elif debt_to_income_ratio > 0.2:
            risk_score += 1
        else:
            risk_score -= 1

        # Employment status contribution
        if employment_status.lower() == "unemployed":
            risk_score += 5
        elif employment_status.lower() == "self-employed":
            risk_score += 3
        elif employment_status.lower() == "part-time":
            risk_score += 2
        else:
            risk_score -= 1

        # Loan purpose contribution
        if loan_purpose.lower() in ["debt consolidation", "emergency"]:
            risk_score += 3
        elif loan_purpose.lower() in ["home renovation", "auto"]:
            risk_score += 1
        else:
            risk_score -= 1

        risk_score = max(0, min(risk_score, 10))

        return RiskAssessmentResponseSchema(
            credit_score=credit_score,
            debt_to_income_ratio=debt_to_income_ratio,
            employment_status=employment_status,
            loan_amount=loan_amount,
            loan_purpose=loan_purpose,
            risk_score=risk_score
        )
    
    @staticmethod
    def assess_loan_risk(credit_score: int, income: float, loan_amount: float, employment_status: str, loan_purpose: str) -> RiskAssessmentResponseSchema:
        # Perform risk assessment using the RiskAssessor
        risk_assessment: RiskAssessmentResponseSchema = RiskAssessmentService.assess_risk_helper(
            credit_score=credit_score,
            income=income,
            loan_amount=loan_amount,
            employment_status=employment_status,
            loan_purpose=loan_purpose
        )
        
        return risk_assessment