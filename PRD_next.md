# PRD_next: LangGraph Multi-Agent RCA Platform - MLOps Enhancement Plan

## 1. Project Overview

The LangGraph Multi-Agent RCA Platform is a sophisticated system designed for automated Root Cause Analysis (RCA) of test failures. It leverages a 6-agent LangGraph architecture with parallel processing capabilities, enabling rapid RCA generation (under 3 seconds per RCA) and high throughput (over 500 RCAs per day). The platform features a React-based frontend for user interaction and a FastAPI backend for core logic and API services, integrating with PostgreSQL for relational data and Qdrant as a vector database, powered by GPT-4 for intelligent analysis. The primary goal is to provide a robust, scalable, and efficient solution for identifying the root causes of test failures.

## 2. Current State Assessment

The project currently provides a functional multi-agent system with a web interface and API. The core logic for RCA generation is implemented using LangGraph and Python, with data persistence handled by PostgreSQL and Qdrant. The presence of `start.sh`, `start_backend.py`, and `test_platform.py` indicates a runnable and testable application. However, several MLOps and deployment aspects are either nascent or entirely missing.

| Feature/Component | Status (Existing/Missing) | Details |
| :---------------- | :------------------------ | :------ |
| **Core Application** | Existing | LangGraph multi-agent system, FastAPI backend, React frontend, PostgreSQL, Qdrant, GPT-4 integration. |
| **Model Serving** | Existing | FastAPI backend serves as the API endpoint for the LangGraph agents. |
| **Containerization** | Missing | No Dockerfiles or docker-compose for application components. |
| **MLflow Integration** | Missing | No explicit experiment tracking, model registry, or artifact logging. |
| **Model Monitoring** | Missing | No dedicated tools for data drift or model performance degradation detection. |
| **Kubernetes Deployment** | Missing | No Kubernetes manifests (deployment.yaml, service.yaml, ingress.yaml) or Helm charts. |
| **Cloud Deployment Config** | Missing | No specific configurations for cloud platforms like AWS SageMaker or Azure ML. |
| **CI/CD for ML** | Missing | No GitHub Actions workflows for automated testing, building, or deployment. |
| **Airflow/Orchestration** | Missing | No DAGs for pipeline orchestration beyond the internal LangGraph DAG. |
| **Big Data Integration** | Missing | Not directly applicable given the current scope and data volume. |
| **API Testing** | Existing (Basic) | `test_final.py`, `test_form.sh`, `test_platform.py` suggest some testing, but dedicated API integration tests (e.g., with pytest) are not explicitly mentioned. |

## 3. Gap Analysis with Priority

This section outlines the critical missing components for robust MLOps and deployment, categorized by priority.

| Gap | Priority | Rationale |
| :---------------------------------- | :------- | :-------- |
| **Containerization** | High | Essential for consistent development, testing, and deployment environments. Enables portability across different infrastructures. |
| **CI/CD for ML** | High | Automates the build, test, and deployment process, ensuring code quality, faster releases, and reliable operations. |
| **Kubernetes Deployment** | High | Provides scalability, resilience, and efficient resource management for microservices-based applications like this platform. |
| **Model Monitoring** | Medium | Crucial for maintaining the performance and reliability of the GPT-4 powered agents, detecting issues like concept drift or performance degradation. |
| **Cloud Deployment Config** | Medium | While Kubernetes provides portability, specific cloud configurations (e.g., AWS EKS, Azure AKS) are needed for production deployment. |
| **MLflow Integration** | Low | Useful for tracking experiments and managing models, but less critical for initial deployment compared to infrastructure. |
| **Airflow/Orchestration** | Low | The LangGraph itself handles internal orchestration; external orchestration might be beneficial for broader data pipelines but not immediately critical for the core application. |
| **Big Data Integration** | Low | Not directly applicable given the current scope and data volume. |
| **API Testing** | Medium | While some tests exist, comprehensive API testing ensures the robustness and correctness of the FastAPI endpoints. |

## 4. Recommended Improvements with Detailed Implementation Steps

### 4.1. Containerization (High Priority)

**Goal:** Package the FastAPI backend and React frontend into Docker images for consistent environments and easier deployment.

**Implementation Steps:**
1.  **Create `Dockerfile` for Backend:** In the `backend/` directory, create a `Dockerfile` to containerize the FastAPI application. This will include installing Python dependencies, copying the application code, and defining the entry point.
    ```dockerfile
    # backend/Dockerfile
    FROM python:3.10-slim-buster
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8000
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
2.  **Create `Dockerfile` for Frontend:** In the `frontend/` directory, create a `Dockerfile` to containerize the React application. This will involve building the React app and serving it with a lightweight web server like Nginx.
    ```dockerfile
    # frontend/Dockerfile
    FROM node:18-alpine as build
    WORKDIR /app
    COPY package.json yarn.lock ./ 
    RUN yarn install --frozen-lockfile
    COPY . .
    RUN yarn build

    FROM nginx:stable-alpine
    COPY --from=build /app/dist /usr/share/nginx/html
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    ```
3.  **Create `docker-compose.yml`:** At the project root, create a `docker-compose.yml` file to orchestrate the backend, frontend, PostgreSQL, and Qdrant services.
    ```yaml
    # docker-compose.yml
    version: '3.8'
    services:
      backend:
        build: ./backend
        ports:
          - "8000:8000"
        environment:
          - DATABASE_URL=postgresql://user:password@db:5432/mydatabase
          - QDRANT_HOST=qdrant
        depends_on:
          - db
          - qdrant
      frontend:
        build: ./frontend
        ports:
          - "80:80"
        depends_on:
          - backend
      db:
        image: postgres:13
        environment:
          - POSTGRES_DB=mydatabase
          - POSTGRES_USER=user
          - POSTGRES_PASSWORD=password
        volumes:
          - db_data:/var/lib/postgresql/data
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - "6333:6333"
          - "6334:6334"
        volumes:
          - qdrant_data:/qdrant/storage
    volumes:
      db_data:
      qdrant_data:
    ```

**Estimated Effort:** 1-2 days

### 4.2. CI/CD for ML (High Priority)

**Goal:** Implement GitHub Actions workflows for automated testing, building, and deployment of the platform.

**Implementation Steps:**
1.  **Create `build-test.yml` Workflow:** Set up a GitHub Actions workflow to automatically build Docker images and run tests on push to `main` or pull requests.
    ```yaml
    # .github/workflows/build-test.yml
    name: Build and Test

on:
      push:
        branches:
          - main
      pull_request:
        branches:
          - main

    jobs:
      build-and-test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - name: Build Backend Docker Image
            run: docker build -t langgraph-backend ./backend
          - name: Run Backend Tests
            run: docker run langgraph-backend python -m pytest ./backend/tests
          - name: Build Frontend Docker Image
            run: docker build -t langgraph-frontend ./frontend
          # Add frontend tests here if applicable
    ```
2.  **Create `deploy.yml` Workflow:** Set up a separate workflow for deploying to a cloud environment (e.g., Kubernetes on AWS EKS) upon successful merges to `main`.
    ```yaml
    # .github/workflows/deploy.yml
    name: Deploy to EKS

on:
      push:
        branches:
          - main

    jobs:
      deploy:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - name: Configure AWS Credentials
            uses: aws-actions/configure-aws-credentials@v1
            with:
              aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
              aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              aws-region: us-east-1
          - name: Login to Amazon ECR
            id: login-ecr
            uses: aws-actions/amazon-ecr-login@v1
          - name: Build and Push Backend Docker Image
            env:
              ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
              ECR_REPOSITORY: langgraph-backend
              IMAGE_TAG: ${{ github.sha }}
            run: |
              docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./backend
              docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          - name: Build and Push Frontend Docker Image
            env:
              ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
              ECR_REPOSITORY: langgraph-frontend
              IMAGE_TAG: ${{ github.sha }}
            run: |
              docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./frontend
              docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          - name: Update K8s Manifests and Deploy
            run: |
              # Replace image tags in k8s manifests and apply
              # kubectl apply -f k8s/
    ```

**Estimated Effort:** 2-3 days

### 4.3. Kubernetes Deployment (High Priority)

**Goal:** Deploy the containerized application to a Kubernetes cluster for scalability and high availability.

**Implementation Steps:**
1.  **Create Kubernetes Manifests:** Develop `deployment.yaml`, `service.yaml`, and `ingress.yaml` for the backend and frontend services, along with deployments for PostgreSQL and Qdrant.
    ```yaml
    # k8s/backend-deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: langgraph-backend
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: langgraph-backend
      template:
        metadata:
          labels:
            app: langgraph-backend
        spec:
          containers:
            - name: backend
              image: <ECR_REGISTRY>/langgraph-backend:<IMAGE_TAG>
              ports:
                - containerPort: 8000
              env:
                - name: DATABASE_URL
                  value: postgresql://user:password@postgres-service:5432/mydatabase
                - name: QDRANT_HOST
                  value: qdrant-service
    ---
    # k8s/backend-service.yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: langgraph-backend-service
    spec:
      selector:
        app: langgraph-backend
      ports:
        - protocol: TCP
          port: 8000
          targetPort: 8000
    ```
    (Similar manifests for frontend, PostgreSQL, and Qdrant)
2.  **Integrate with CI/CD:** Update the `deploy.yml` workflow to apply these manifests after pushing new Docker images.

**Estimated Effort:** 3-4 days

### 4.4. Model Monitoring (Medium Priority)

**Goal:** Implement monitoring for LLM costs, latency, agent performance, and data drift using tools like Evidently AI.

**Implementation Steps:**
1.  **Integrate Evidently AI:** Add Evidently AI to the backend to monitor input data drift and model output quality. This would involve logging data and generating reports.
2.  **Custom Metrics:** Implement custom metrics for LLM token usage, API call latency, and agent success/failure rates within the FastAPI application.
3.  **Dashboarding:** Integrate with a monitoring solution (e.g., Prometheus/Grafana) to visualize these metrics.

**Estimated Effort:** 2-3 days

### 4.5. API Testing (Medium Priority)

**Goal:** Develop comprehensive integration tests for the FastAPI endpoints using `pytest`.

**Implementation Steps:**
1.  **Install `pytest` and `httpx`:** Add these to `requirements.txt`.
2.  **Create `tests/api_tests.py`:** Write test cases that interact with the FastAPI endpoints to ensure correct functionality, data validation, and error handling.
    ```python
    # backend/tests/api_tests.py
    import pytest
    from httpx import AsyncClient
    from main import app # Assuming your FastAPI app is named 'app' in main.py

    @pytest.mark.asyncio
    async def test_read_main():
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to LangGraph RCA Platform API"}

    # Add more tests for other endpoints
    ```
3.  **Integrate with CI/CD:** Ensure these tests run as part of the `build-test.yml` workflow.

**Estimated Effort:** 1-2 days

## 5. Best Interview Topics This Project Demonstrates After Improvements

After implementing the recommended improvements, this project will strongly demonstrate expertise in **MLOps, Cloud-Native Development, and Distributed Systems**. Specifically, it will showcase proficiency in:

*   **Model Serving + FastAPI:** The existing FastAPI backend for serving the LangGraph agents, enhanced with robust API testing.
*   **Containerization + Kubernetes Deployment:** Comprehensive use of Docker and Kubernetes for scalable, resilient, and portable application deployment.
*   **CI/CD for ML:** Automated workflows for building, testing, and deploying ML-powered applications.
*   **Cloud Deployment (AWS/Azure):** Practical experience with deploying and managing applications on major cloud providers.
*   **System Design for AI/ML:** Designing a multi-agent system with parallel execution and integrating various components (vector DB, RDBMS, LLMs).

## 6. Cloud Deployment Plan (AWS Specific)

This plan outlines a deployment strategy for AWS, leveraging its managed services for MLOps.

1.  **Container Registry (ECR):** Push Docker images of the backend and frontend to Amazon Elastic Container Registry (ECR).
2.  **Kubernetes Cluster (EKS):** Deploy the application to Amazon Elastic Kubernetes Service (EKS). This will host the backend, frontend, PostgreSQL, and Qdrant containers.
    *   **PostgreSQL:** Consider using Amazon RDS for PostgreSQL for a managed database service, offloading operational overhead.
    *   **Qdrant:** Deploy Qdrant as a stateful set within EKS or explore a managed vector database service if available and suitable.
3.  **Load Balancing (ALB/NLB):** Use an Application Load Balancer (ALB) or Network Load Balancer (NLB) to expose the frontend and backend services to the internet, handling traffic distribution and SSL termination.
4.  **CI/CD (GitHub Actions + AWS):** Integrate GitHub Actions with AWS for automated builds (pushing to ECR) and deployments (updating EKS manifests).
5.  **Monitoring (CloudWatch, Prometheus/Grafana):** Utilize AWS CloudWatch for logging and basic metrics. For advanced application and LLM monitoring, deploy Prometheus and Grafana within the EKS cluster or use Amazon Managed Service for Prometheus and Grafana.
6.  **Secrets Management (AWS Secrets Manager):** Store sensitive information (e.g., API keys, database credentials) in AWS Secrets Manager and inject them into Kubernetes pods securely.

## 7. Quick Win (1-2 days)

The single most impactful improvement achievable in 1-2 days is to implement **Containerization** for the FastAPI backend and React frontend, along with a basic `docker-compose.yml` file. This immediately provides a reproducible development environment and lays the groundwork for all subsequent MLOps improvements, making the project significantly more portable and easier to manage locally and for future cloud deployments.
