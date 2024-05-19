
from app.api.schemas import LoanApprovalResponseSchema, RiskAssessmentResponseSchema
from sqlalchemy.orm import Session
from app.models.loan_application import LoanApplicationDB
from app.utils.logger import logger

class LoanApprovalService:
    APPROVAL_THRESHOLD = 5 

    @staticmethod
    def approve_loan(risk_assessment: RiskAssessmentResponseSchema) -> LoanApprovalResponseSchema:
        # Determine loan approval based on risk score
        if risk_assessment.risk_score <= LoanApprovalService.APPROVAL_THRESHOLD:
            return LoanApprovalResponseSchema(
                approved=True,
                reason="Loan approved based on risk assessment",
                risk_score=risk_assessment.risk_score
            )
        else:
            return LoanApprovalResponseSchema(
                approved=False,
                reason="Loan rejected based on risk assessment",
                risk_score=risk_assessment.risk_score
            )
        

    @staticmethod
    def approve_loan_application(db: Session, application_id: int, risk_assessment: RiskAssessmentResponseSchema) -> LoanApprovalResponseSchema:
        # Retrieve the loan application from the database
        db_application: LoanApplicationDB = db.query(LoanApplicationDB).filter(LoanApplicationDB.id == application_id).first()
        if not db_application:
            logger.error(f"Loan application with ID {application_id} not found")
            raise ValueError(f"Loan application with ID {application_id} not found")

        # Perform loan approval using the LoanApprover
        approval_result: LoanApprovalResponseSchema = LoanApprovalService.approve_loan(
            risk_assessment=risk_assessment
        )

        # Update the loan application status based on approval result
        db_application.status = "Approved" if approval_result.approved else "Rejected"
        db.commit()
        db.refresh(db_application)

        logger.info(f"Loan application ID {db_application.id} - Approval Status: {db_application.status}")

        return approval_result