# PalletVision

PalletVision is a web-based application designed to provide a dashboard for managing pallet recognition stations and visualizing efficiency metrics in real-time. The project is built with a Flask backend, a TimescaleDB database, and a modern frontend using Webpack and plain JavaScript.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Docker](#2-install-docker)
  - [3. Build and Run the Application](#3-build-and-run-the-application)
- [Usage](#usage)
- [License](#license)

---

## Project Overview

PalletVision provides:
- **Manager Dashboard**: View pallet counts and station statuses.
- **Station Dashboard**: Monitor the status and inferred data for individual stations.
- **Efficiency Dashboard**: Analyze hourly processing rates, inference confidence, and processing times.

Technologies used:
- **Frontend**: Webpack, Bootstrap, and JavaScript.
- **Backend**: Flask.
- **Database**: TimescaleDB.
- **Real-time Communication**: Redis (placeholder for future real-time features).

---

## Requirements

Before you begin, make sure you have the following installed:

- [Docker](https://www.docker.com/) (version 20.x or above)
- [Docker Compose](https://docs.docker.com/compose/) (version 1.29 or above)

---

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine using the following command:

```bash
git clone https://github.com/Zakariabs/PalletVision.git
cd PalletVision
```

---

### 2. Install Docker

Ensure Docker and Docker Compose are installed and running on your machine:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

Verify installation:
```bash
docker --version
docker-compose --version
```

---

### 3. Build and Run the Application

Run the following commands to build and start the application in Docker:

1. Build and start the containers:
   ```bash
   docker-compose up --build -d
   ```
2. Verify the services are running:
   ```bash
   docker-compose ps
   ```

   You should see the following services running:
   - `frontend_container`
   - `backend_container`
   - `timescaledb_container`
   - `inference`

3. Access the application:
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **Backend**: [http://localhost:5000](http://localhost:5000)

---

## Usage

### 1. Accessing the Dashboards

- **Manager Dashboard**: View station statuses and pallet counts.
- **Station Dashboard**: Access individual station details.

Navigate through the app using the header navigation links.

### 2. Database Initialization

The TimescaleDB database is initialized automatically using the `init.sql` file. This includes:
- Table creation for `Station`, `StationStatus`, `Image`, `PalletType`, and `InferenceRequest`.
- Default values for `StationStatus` and `Status`.

If you need to reinitialize the database:
1. Stop the containers:
   ```bash
   docker-compose down -v
   ```
2. Start the containers again:
   ```bash
   docker-compose up --build -d
   ```

---

## Train Your Own Model in Roboflow

PalletVision runs inference against a **classification** model hosted on Roboflow. The worker calls Roboflow's hosted API, displays the top class + confidence, and auto-uploads any low-confidence frame back to your dataset for re-labeling.

### 1. Create the Roboflow project

1. Sign up at [roboflow.com](https://roboflow.com) and create a workspace.
2. Create a **new project** and pick **Classification** as the project type (not Object Detection).
3. Use class names that match the seeded `PalletType` rows: `euro`, `EPAL`, `Other`. Names that don't match will be coerced to `Other` at runtime.

### 2. Upload, label, and train

1. Drag your pallet images into the project and assign one class per image.
2. Click **Generate** to produce a dataset version, then **Train** (Fast or Accurate). Training typically takes 10–30 minutes.
3. Once training completes, the version appears under **Versions** in the sidebar.

### 3. Get your credentials

1. **Settings → Roboflow API** → copy your private API key.
2. From the project page URL `https://app.roboflow.com/<workspace>/<project>`, copy the `workspace/project` slug.
3. Note the trained version number (e.g. `1`).

### 4. Configure PalletVision

```bash
cp .env.example .env
# then edit .env and fill in:
#   ROBOFLOW_API_KEY
#   ROBOFLOW_PROJECT_ID    (workspace/project)
#   ROBOFLOW_MODEL_VERSION (integer)
```

Restart the stack: `docker-compose up --build -d`.

### 5. Active learning loop

Any inference whose confidence is below `ROBOFLOW_CONFIDENCE_THRESHOLD` (default `0.6`) is:

- marked with a yellow **Review** badge in the Station Dashboard, and
- uploaded back to your Roboflow project's dataset (unassigned queue).

Periodically open Roboflow → Annotate, label the new images, regenerate the dataset, and train a new version. Bump `ROBOFLOW_MODEL_VERSION` in `.env` and restart the worker to roll the new model out.

Set `ROBOFLOW_UPLOAD_ON_LOW_CONF=false` if you only want the flag without the upload.

> **Legacy local YOLO training** in `backend/app/ai_model/` is deprecated; kept for airgap use only.

---

## License

This project is licensed under the MIT License.
