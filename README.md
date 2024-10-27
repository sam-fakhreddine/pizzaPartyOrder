# Evansdale Pizza Party Ordering System

Welcome to the **Evansdale Pizza Party Ordering System**! This application allows users to place pizza party orders conveniently. It is designed for easy use by both parents and event coordinators, facilitating order collection and management.

## Project Structure

- **`app.py`**: Backend application code (Flask)
- **`index.html`**: HTML file providing the main structure of the web interface
- **`script.js`**: JavaScript file for dynamic content updates on the client side
- **`Dockerfile`**: Instructions to build the Docker image for the application
- **`docker-compose.yml`**: Docker Compose configuration for managing multi-container deployments

## Features

- **Dynamic Ordering Form**: Allows users to select a pizza party date, enter student information, choose pizza types, and select juice box quantities.
- **Order Summary**: Displays the user’s last five orders and provides an overview of the current order.
- **Error Handling**: Input validation and error messages for required fields.
- **Responsive Design**: Ensures the web app works well across different devices.
- **Health Check**: The application has an integrated health check endpoint for monitoring.

## Requirements

- Docker (for containerized deployment)
- Docker Compose (for multi-container orchestration)
- Python 3.x (for local development)
- Node.js (for additional frontend development)

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/evansdale-pizza-ordering.git
cd evansdale-pizza-ordering
```

### 2. Build & Run with Docker

#### Using Docker Compose

This setup assumes you have Docker and Docker Compose installed.

```bash
docker-compose up -d --build
```

The application will be accessible at `http://localhost:5000`.

### 3. Environment Variables

You can define the environment in a `.env` file with the following variable:

- `FLASK_ENV`: Set to `production` or `development` (default: `production`)

### 4. Health Check

Docker Compose configuration includes a health check to verify that the service is running. Health check URL: `http://localhost:5000/health`.

## Application Details

### Backend (Flask)

The `app.py` file contains the main backend code that manages pizza order submissions, retrieves recent orders, and handles data processing.

### Frontend (HTML & JavaScript)

- **`index.html`**: Defines the structure for the order page, with sections for:
  - Order form
  - Order summary
  - Recent orders display

- **`script.js`**: Adds dynamic functionality to the web app, like handling form submissions and updating recent orders.

### Docker Configuration

- **Dockerfile**: Defines the Docker image build for the Flask app.
- **docker-compose.yml**: Specifies the Docker Compose configuration to run the app in a container with defined services, including health check, logging, and resource limits.

  ```yaml
  services:
    evansdale_pizza:
      container_name: evansdale_pizza_app
      build:
        context: .
      ports:
        - "5000:5000"
      volumes:
        - app_data:/app
      environment:
        - FLASK_ENV=${FLASK_ENV:-production}
      restart: unless-stopped
      healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  ```

## Usage

1. **Open the App**: Go to `http://localhost:5000`.
2. **Place an Order**:
   - Enter the pizza party date, student’s name, and other details.
   - Select pizza types and quantities.
   - Submit the order.
3. **View Recent Orders**: The last five orders are displayed on the main page.

## Logging & Monitoring

The application is configured to store logs in JSON format, with a maximum log file size of 10MB and up to 3 rotated logs. CPU and memory limits are set in the Docker Compose file to optimize resource usage.

## Customization

Feel free to adjust:
- The `docker-compose.yml` for different port mappings or resources.
- The CSS styles to fit your branding.