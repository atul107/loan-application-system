import json
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from app.services.loan_application_service import LoanApplicationService
from app.services.risk_accessment_service import RiskAssessmentService
from app.services.loan_approval_service import LoanApprovalService
from app.api.schemas import LoanApplicationCreateSchema, LoanApplicationUpdateSchema, RiskAssessmentResponseSchema, LoanApprovalResponseSchema
from app.utils.logger import logger
from app.config import KAFKA_BROKER_URL, KAFKA_TOPICS

class KafkaConsumerService:
    def __init__(self, db: Session):
        self.db = db
        self.consumer = KafkaConsumer(
            *KAFKA_TOPICS,
            bootstrap_servers=KAFKA_BROKER_URL,
            value_deserializer=lambda message: json.loads(message.decode('utf-8'))
        )

    def create_loan_application(self, message: dict):
        try:
            logger.info(f"Received message: {message}")
            # Parse the incoming message
            application_data = LoanApplicationCreateSchema(**message)
            
            risk_assessment: RiskAssessmentResponseSchema = RiskAssessmentService.assess_risk_helper(
                credit_score=application_data.credit_score,
                income=application_data.income,
                loan_amount=application_data.loan_amount,
                employment_status=application_data.employment_status,
                loan_purpose=application_data.loan_purpose
            )

            # Approve loan application
            approval_result: LoanApprovalResponseSchema = LoanApprovalService.approve_loan(
                risk_assessment=risk_assessment
            )

            # Update the loan application status based on approval result
            application_data.status = "Approved" if approval_result.approved else "Rejected"

            # Create loan application
            application_id = LoanApplicationService.create_loan_application(self.db, application_data)
            logger.info(f"Processed loan application ID: {application_id} - Approval Status: {application_data.status}")
        except Exception as e:
            logger.error(f"Error processing loan application message: {e}")

    def update_loan_application(self, message: dict):
        try:
            # Parse the incoming message
            application_id = message.get('application_id')
            application_data = LoanApplicationUpdateSchema(**message.get('application'))
            
            db_application = LoanApplicationService.update_loan_application(self.db, application_id, application_data)
            if db_application is None:
                logger.error(f"Loan application ID {db_application} not found")
                return
            
            logger.info(f"Updated application with ID: {db_application}")
        except Exception as e:
            logger.error(f"Error processing topic message: {e}")


    def delete_loan_application(self, message: dict):
        try:
            application_id = message.get('application_id')
            success = LoanApplicationService.delete_loan_application(self.db, application_id)
            
            if not success:
                logger.error(f"Loan application ID {application_id} not found")
                return
            
            logger.info(f"Deleted loan application ID: {application_id}")
        except Exception as e:
            logger.error(f"Error processing delete loan application message: {e}")

    def approve_loan_application(self, message: dict):
        try:
            application_id = message.get('application_id')
            
            db_application = LoanApplicationService.get_loan_application(self.db, application_id)

            risk_assessment: RiskAssessmentResponseSchema = RiskAssessmentService.assess_risk_helper(
                credit_score=db_application.credit_score,
                income=db_application.income,
                loan_amount=db_application.loan_amount,
                employment_status=db_application.employment_status,
                loan_purpose=db_application.loan_purpose
            )

            approval_result = LoanApprovalService.approve_loan_application(self.db, application_id, risk_assessment)
            
            logger.info(f"Approved loan application ID: {application_id} - Approval Status: {approval_result.approved}")
        except ValueError as ve:
            logger.error(f"Error approving loan application: {ve}")
        except Exception as e:
            logger.error(f"Error processing approve loan application message: {e}")

    def process_message(self, topic: str, message: dict):
        if topic == 'create_application':
            self.create_loan_application(message)
        elif topic == 'update_applications':
            self.update_loan_application(message)
        elif topic == 'delete_applications':
            self.delete_loan_application(message)
        elif topic == 'approve_applications':
            self.approve_loan_application(message)
        else:
            logger.error(f"Unknown topic: {topic}")

    def consume_messages(self):
        try:
            for message in self.consumer:
                logger.info(f"Consuming message from topic {message.topic}: {message.value}")
                self.process_message(message.topic, message.value)
        finally:
            self.db.close()
