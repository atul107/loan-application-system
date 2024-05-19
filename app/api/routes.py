from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas import (
    LoanApplicationCreateSchema,
    LoanApplicationUpdateSchema,
    LoanApplicationResponseSchema,
    RiskAssessmentResponseSchema
)
from app.services.risk_accessment_service import RiskAssessmentService
from app.services.loan_application_service import LoanApplicationService
from app.models import database
from app.utils.logger import logger

router = APIRouter()

# Endpoint to create a new loan application
@router.post("/loan-application/")
def create_loan_application(application: LoanApplicationCreateSchema, db: Session = Depends(database.get_db)):
    try:
        response = LoanApplicationService.queue_create_application(db, application)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating loan application: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating loan application: {e}")
    
# Endpoint to read an existing loan application
@router.get("/loan-application/{application_id}", response_model=LoanApplicationResponseSchema)
def read_loan_application(application_id: int, db: Session = Depends(database.get_db)):
    try:
        db_application = LoanApplicationService.get_loan_application(db, application_id)
        if db_application is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan application not found")
        return db_application
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error reading loan application: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading loan application: {e}")

# Endpoint to update an existing loan application
@router.put("/loan-application/{application_id}")
def update_loan_application(application_id: int, application: LoanApplicationUpdateSchema, db: Session = Depends(database.get_db)):
    try:
        response = LoanApplicationService.queue_update_application(db, application_id, application)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error upfdating loan application: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error upfdating loan application: {e}")

# Endpoint to delete an existing loan application
@router.delete("/loan-application/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan_application(application_id: int, db: Session = Depends(database.get_db)):
    try:
        response = LoanApplicationService.queue_delete_application(db, application_id)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting loan application: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting loan application: {e}")

# Endpoint to approve a loan application
@router.post("/loan-application/{application_id}/approve")
def approve_loan_application(application_id: int, db: Session = Depends(database.get_db)):
    try:
        response = LoanApplicationService.queue_approve_application(db, application_id)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in approving loan application: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error in approving loan application: {e}")

# Endpoint to assess the risk of a loan application
@router.get("/loan-application/{application_id}/assess-risk", response_model=RiskAssessmentResponseSchema)
def assess_loan_application_risk(application_id: int, db: Session = Depends(database.get_db)):
    try:
        db_application: LoanApplicationResponseSchema = LoanApplicationService.get_loan_application(db, application_id)
        if db_application is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan application not found")
        
        risk_assessment_result: RiskAssessmentResponseSchema = RiskAssessmentService.assess_loan_risk(
            credit_score=db_application.credit_score,
            income=db_application.income,
            loan_amount=db_application.loan_amount,
            employment_status=db_application.employment_status,
            loan_purpose=db_application.loan_purpose
        )
        
        return risk_assessment_result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error assessing loan application risk: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error assessing loan application risk: {e}")
