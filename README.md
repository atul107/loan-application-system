# Loan Approval System

The Loan Approval System is a scalable application designed to evaluate loan applications, calculate the risk of lending, and approve or reject applications based on predefined criteria. The system is built using FastAPI, SQLAlchemy, Kafka, and MySQL.

## Features

- Submit a new loan application
- Retrieve the status of a submitted application
- Update or delete an existing application
- Evaluate risk based on various factors
- Approve or reject loan applications based on risk assessment
- Handle a high volume of loan applications using Kafka

## Setting Up
Clone the Repository:

```
git clone https://github.com/atul107/loan-application-system.git
cd loan-application-system
```
### Create and Configure Environment Variables:
Copy the `.env.example` to `.env` and update the values.

### Running the Application:
Make sure Kafka and MySQL are running before starting the application.


You can run the application either directly using UVicorn or using Docker.

#### Running with UVicorn:
Use the following command to run the app:
```
uvicorn app.main:app --host 0.0.0.0 --port 8080
```
#### Running with Docker:
Build the Docker image:
```
docker build -t loan-application .
```
Run the Docker container with environment variables:


```
docker run -p 8080:8080 -e KAFKA_BROKER_URL=host.docker.internal:9092 -e DATABASE_URL={db_url} loan-application
```

### Access the Application:
The application will be accessible at http://localhost:8080.

Docs can be accessed on http://localhost:8080/docs



