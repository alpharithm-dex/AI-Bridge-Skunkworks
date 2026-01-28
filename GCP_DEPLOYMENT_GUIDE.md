# Google Cloud Deployment & API Guide

This guide explains how to deploy the Bias Correction Tool as a scalable API service on Google Cloud Platform (GCP) using Cloud Run.

## Prerequisites

1.  **Google Cloud Project**: You need an active GCP project.
2.  **Google Cloud SDK**: Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install).
3.  **Docker**: (Optional but recommended) for local testing.

## 1. Local Testing

Before deploying, you can test the API locally.

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Flask app**:
    ```bash
    python app.py
    ```

3.  **Test the endpoint** (in a separate terminal):
    ```bash
    # Windows PowerShell
    Invoke-RestMethod -Uri "http://localhost:8080/correct" -Method Post -ContentType "application/json" -Body '{"text": "Monna o a nama fa mosadi a pheha."}'
    
    # OR using curl
    curl -X POST http://localhost:8080/correct -H "Content-Type: application/json" -d '{"text": "Monna o a nama fa mosadi a pheha."}'
    ```

## 2. Deployment to Google Cloud Run

Cloud Run is a serverless platform that runs stateless containers. It's perfect for this API.

### Step 1: Initialize gcloud

Login to your Google Cloud account:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Enable Services

Enable the necessary APIs (Cloud Run and Artifact Registry):
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### Step 3: Deploy

You can deploy directly from source using a single command. This builds the container in the cloud and deploys it.

```bash
gcloud run deploy bias-correction-api --source . --region us-central1 --allow-unauthenticated
```

*   `--source .`: Uses the current directory (Dockerfile).
*   `--region us-central1`: Choose a region close to your users.
*   `--allow-unauthenticated`: Makes the API public. Remove this flag if you want to require authentication.

### Step 4: Get the URL

Once deployed, the command will output a Service URL, e.g., `https://bias-correction-api-xyz-uc.a.run.app`.

## 3. API Documentation

### Base URL
The Base URL is the Service URL provided by Cloud Run (e.g., `https://bias-correction-api-xyz-uc.a.run.app`).

### Endpoints

#### 1. Health Check
*   **URL**: `/health`
*   **Method**: `GET`
*   **Description**: Checks if the service is running.
*   **Response**:
    ```json
    {
      "status": "healthy",
      "service": "bias-correction-api"
    }
    ```

#### 2. Correct Bias
*   **URL**: `/correct`
*   **Method**: `POST`
*   **Headers**: `Content-Type: application/json`
*   **Body Parameters**:
    *   `text` (string, required): The text to analyze and correct.
    *   `language` (string, optional): 'setswana' ('tn') or 'isizulu' ('zu'). If omitted, language is auto-detected.

*   **Example Request**:
    ```json
    {
      "text": "Monna o a nama fa mosadi a pheha.",
      "language": "setswana"
    }
    ```

*   **Example Response**:
    ```json
    {
      "detected_bias": true,
      "explanations": [
        {
          "rule_triggered": "Contrastive Gender Roles",
          "reason": "Female subject assigned domestic work while male subject assigned academic/leadership work.",
          "span": "mosadi ... fa ... monna"
        }
      ],
      "rewrite": "Motho mongwe le mongwe o a nama fa motho mongwe le mongwe a pheha.",
      "original": "Monna o a nama fa mosadi a pheha."
    }
    ```

## 4. Troubleshooting

*   **Logs**: View logs in the Google Cloud Console under Cloud Run > Your Service > Logs.
*   **Memory/Timeout**: If the service is slow, you can increase memory or timeout during deployment:
    ```bash
    gcloud run deploy bias-correction-api --source . --memory 1Gi --timeout 60s
    ```
