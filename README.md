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
   - `redis_container`

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

## License

This project is licensed under the MIT License.

---