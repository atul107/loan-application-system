
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Optional

# Schema for loan application data
class LoanApplicationSchema(BaseModel):
    applicant_name: str = Field(..., title="Applicant's Name", max_length=100)
    credit_score: int = Field(..., title="Credit Score", ge=300, le=850)
    loan_amount: float = Field(..., title="Loan Amount", gt=0)
    loan_purpose: str = Field(..., title="Loan Purpose", max_length=200)
    income: float = Field(..., title="Income", gte=0)
    employment_status: str = Field(..., title="Employment Status", max_length=50)
    application_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: Optional[str] = Field(default="Pending", title="Application Status")
    mobile_number: str = Field(..., title="Mobile Number", max_length=15)

    @validator('loan_purpose')
    def loan_purpose_not_empty(cls, v):
            if not v.strip():
                raise ValueError('Loan purpose must not be empty')
            return v

    @validator('employment_status')
    def employment_status_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Employment status must not be empty')
        return v
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "applicant_name": "Atul",
                "credit_score": 720,
                "loan_amount": 15000.00,
                "loan_purpose": "Home Renovation",
                "income": 75000.00,
                "employment_status": "Employed",
                "application_date": "2023-05-17T12:00:00Z",
                "status": "Pending",
                "mobile_number": "1234567890"
            }
        }

# Schema for creating a loan application, inherits from LoanApplicationSchema
class LoanApplicationCreateSchema(LoanApplicationSchema):
    pass

# Schema for updating a loan application, all fields are optional
class LoanApplicationUpdateSchema(LoanApplicationSchema):
    applicant_name: Optional[str] = Field(None, title="Applicant's Name", max_length=100)
    credit_score: Optional[int] = Field(None, title="Credit Score", ge=300, le=850)
    loan_amount: Optional[float] = Field(None, title="Loan Amount", gt=0)
    loan_purpose: Optional[str] = Field(None, title="Loan Purpose", max_length=200)
    income: Optional[float] = Field(None, title="Income", gt=0)
    employment_status: Optional[str] = Field(None, title="Employment Status", max_length=50)
    mobile_number: Optional[str] = Field(None, title="Mobile Number", max_length=15)

# Schema for the response of a loan application, includes an ID
class LoanApplicationResponseSchema(LoanApplicationSchema):
    id: int

# Schema for risk assessment response
class RiskAssessmentResponseSchema(BaseModel):
    credit_score: int
    debt_to_income_ratio: float
    employment_status: str
    loan_amount: float
    loan_purpose: str
    risk_score: float

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "credit_score": 720,
                "debt_to_income_ratio": 0.2,
                "employment_status": "Employed",
                "loan_amount": 15000.00,
                "loan_purpose": "Home Renovation",
                "risk_score": 3.0
            }
        }

# Schema for loan approval result
class LoanApprovalResponseSchema(BaseModel):
    approved: bool
    reason: str
    risk_score: float

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "approved": True,
                "reason": "Loan approved based on risk assessment",
                "risk_score": 3.0
            }
        }