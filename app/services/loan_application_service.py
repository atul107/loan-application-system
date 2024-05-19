from sqlalchemy.orm import Session
from app.models.loan_application import LoanApplicationDB
from app.api.schemas import LoanApplicationCreateSchema, LoanApplicationUpdateSchema, LoanApplicationResponseSchema
from app.utils.logger import logger
from fastapi import HTTPException, status
from app.workers.kafka_producer import send_message

class LoanApplicationService:
    @staticmethod
    def create_loan_application(db: Session, application: LoanApplicationCreateSchema) -> int:
        try:
            # Check if an application with the same mobile number already exists
            existing_application = db.query(LoanApplicationDB).filter(LoanApplicationDB.mobile_number == application.mobile_number).first()
            if existing_application:
                logger.error(f"Loan application with mobile number {application.mobile_number} already exists.")
                return
            # Create new loan application
            db_application = LoanApplicationDB(**application.dict())
            db.add(db_application)
            db.commit()
            db.refresh(db_application)

            logger.info(f"Loan application created successfully with ID {db_application.id}.")
            return db_application.id

        except Exception as e:
            logger.error(f"Error creating loan application: {e}")
            db.rollback()

    @staticmethod
    def queue_create_application(db: Session, application: LoanApplicationCreateSchema) -> dict:
        try:
            # Check if an application with the same mobile number already exists
            existing_application = db.query(LoanApplicationDB).filter(LoanApplicationDB.mobile_number == application.mobile_number).first()
            if existing_application:
                logger.error(f"Loan application with mobile number {application.mobile_number} already exists.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Loan application with mobile number {application.mobile_number} already exists.")
            
            # Send the create request to Kafka
            send_message('create_application', application.dict())
            
            return {"message": "Create request queued"}
        
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error queuing loan application creation: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error queuing loan application creation: {e}")

    @staticmethod
    def update_loan_application(db: Session, application_id: int, application: LoanApplicationUpdateSchema) -> int:
        try:
            # Retrieve the existing application by ID
            db_application: LoanApplicationDB = db.query(LoanApplicationDB).filter(LoanApplicationDB.id == application_id).first()
            if not db_application:
                logger.error(f"Loan application with ID {application_id} not found.")
                return

            update_data = application.dict(exclude_unset=True)

            # Check for mobile number uniqueness if it is being updated
            if 'mobile_number' in update_data and update_data['mobile_number'] != db_application.mobile_number:
                existing_application = db.query(LoanApplicationDB).filter(
                    LoanApplicationDB.mobile_number == update_data['mobile_number'],
                    LoanApplicationDB.id != application_id
                ).first()
                if existing_application:
                    logger.error(f"Loan application with mobile number {update_data['mobile_number']} already exists.")
                    return
            # Update application fields
            for key, value in update_data.items():
                setattr(db_application, key, value)

            db.commit()
            db.refresh(db_application)

            logger.info(f"Loan application with ID {application_id} updated successfully.")
            return db_application.id
        except Exception as e:
            logger.error(f"Error updating loan application with ID {application_id}: {e}")
            db.rollback()
    
    @staticmethod
    def queue_update_application(db: Session, application_id: int, application: LoanApplicationUpdateSchema) -> dict:
        try:
            # Retrieve the existing application by ID
            existing_application = db.query(LoanApplicationDB).filter(LoanApplicationDB.id == application_id).first()
            if not existing_application:
                logger.error(f"Loan application with ID {application_id} not found.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Loan application with ID {application_id} not found.")

            # Check for mobile number uniqueness if it is being updated
            if application.mobile_number:
                mobile_number_application = db.query(LoanApplicationDB).filter(
                    LoanApplicationDB.mobile_number == application.mobile_number
                ).first()
                if mobile_number_application:
                    logger.error(f"Loan application with mobile number {application.mobile_number} already exists.")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Loan application with mobile number {application.mobile_number} already exists.")
            
            # Send the update request to Kafka
            send_message('update_applications', {'application_id': application_id, 'application': application.dict(exclude_unset=True)})
            return {"message": "Update request queued"}
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating loan application: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating loan application: {e}")
    
    @staticmethod
    def get_loan_application(db: Session, application_id: int) -> LoanApplicationResponseSchema:
        try:
            # Retrieve the existing application by ID
            db_application = db.query(LoanApplicationDB).filter(LoanApplicationDB.id == application_id).first()
            if not db_application:
                logger.error(f"Loan application with ID {application_id} not found.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan application not found")
            return LoanApplicationResponseSchema.from_orm(db_application)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error retrieving loan application with ID {application_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving loan application with ID {application_id}: {e}")

    @staticmethod
    def delete_loan_application(db: Session, application_id: int) -> bool:
        try:
            # Retrieve the existing application by ID
            db_application = db.query(LoanApplicationDB).filter(LoanApplicationDB.id == application_id).first()
            if not db_application:
                logger.error(f"Loan application with ID {application_id} not found.")
                return
            # Delete the application
            db.delete(db_application)
            db.commit()
            
            logger.info(f"Loan application with ID {application_id} deleted successfully.")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting loan application with ID {application_id}: {e}")
            db.rollback()

    @staticmethod
    def queue_delete_application(db: Session, application_id: int) -> dict:
        try:
            # Retrieve the existing application by ID
            db_application = db.query(LoanApplicationDB).filter(LoanApplicationDB.id == application_id).first()
            if not db_application:
                logger.error(f"Loan application with ID {application_id} not found.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Loan application with ID {application_id} not found.")

            send_message('delete_applications', {'application_id': application_id})
            logger.info(f"Delete request for loan application ID {application_id} queued successfully.")
            return {"message": "Delete request queued"}
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error queuing delete request for loan application ID {application_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error queuing delete request for loan application ID {application_id}: {e}")

    @staticmethod
    def queue_approve_application(db: Session, application_id: int):
        try:
            # Retrieve the existing application by ID
            db_application = db.query(LoanApplicationDB).filter(LoanApplicationDB.id == application_id).first()
            if not db_application:
                logger.error(f"Loan application with ID {application_id} not found.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Loan application with ID {application_id} not found.")

            send_message('approve_applications', {'application_id': application_id})
            return {"message": "Approve request queued"}
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error approving loan application: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error approving loan application: {e}")