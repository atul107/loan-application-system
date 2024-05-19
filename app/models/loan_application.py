
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from .database import Base

class LoanApplicationDB(Base):
    __tablename__ = 'loan_applications'

    id = Column(Integer, primary_key=True, index=True)
    applicant_name = Column(String(100), nullable=False)
    credit_score = Column(Integer, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_purpose = Column(String(200), nullable=False)
    income = Column(Float, nullable=False)
    employment_status = Column(String(50), nullable=False)
    application_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="Pending")
    mobile_number = Column(String(15), nullable=False, unique=True)

    __table_args__ = (
        UniqueConstraint('mobile_number', name='uq_mobile_number'),
    )

    def to_dict(self):
        # Convert the LoanApplicationDB instance to a dictionary
        return {
            "id": self.id,
            "applicant_name": self.applicant_name,
            "credit_score": self.credit_score,
            "loan_amount": self.loan_amount,
            "loan_purpose": self.loan_purpose,
            "income": self.income,
            "employment_status": self.employment_status,
            "application_date": self.application_date.isoformat(),
            "status": self.status,
            "mobile_number": self.mobile_number
        }