
# Project Title

A brief description of what this project does and who it's for

# ServiceNow Integration Platform

A full-stack application that enables natural language queries to ServiceNow using Azure OpenAI, built with FastAPI backend and React frontend.

## 🏗️ Architecture

This project consists of two main components:
- **Backend**: FastAPI service that processes natural language queries and interfaces with ServiceNow
- **Frontend**: React application providing a conversational user interface

## 🚀 Backend (FastAPI)

### ✅ Features

- **Natural Language Processing**: Accepts and processes natural language queries
- **Azure OpenAI Integration**: Leverages Azure OpenAI Chat API for intelligent responses
- **ServiceNow Authentication**: Secure authentication with ServiceNow instances
- **Flexible Response Formats**: Returns both human-readable and raw JSON responses
- **Health Monitoring**: Built-in health check endpoints

### 🛠️ Local Setup

#### 1. Environment Configuration

Create a `.env` file in the `backend` folder with the following variables:

```bash
AZURE_OPENAI_ENGINE=your-deployment-name
AZURE_OPENAI_MODEL=
AZURE_OPENAI_TEMPERATURE=0.0
AZURE_OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2023-03-15-preview

API_HOST=0.0.0.0
API_PORT=7000
```

#### 2. Installation and Startup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:7000`

## 🌐 Frontend (React)

### ✨ Features

- **Conversational Interface**: Intuitive chat-based user experience
- **Rich Incident Display**: Detailed incident information with expandable cards
- **Visual Indicators**: Status icons, priority color coding, and timestamped messages
- **Responsive Design**: Optimized for various screen sizes

### 🧪 Local Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Start Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

*Note: This application runs locally and is not currently hosted on the cloud.*

## 🔁 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/query` | Returns human-readable response from natural language query |
| `POST` | `/query/raw` | Returns raw ServiceNow JSON data |
| `GET` | `/health` | Health check endpoint for monitoring |

### Example API Usage

```bash
# Human-readable query
curl -X POST "http://localhost:7000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all high priority incidents"}'

# Raw JSON response
curl -X POST "http://localhost:7000/query/raw" \
  -H "Content-Type: application/json" \
  -d '{"query": "List open incidents for IT team"}'
```

## 📦 Dependencies

### Backend Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Python-dotenv**: Environment variable management
- **Azure OpenAI SDK**: Integration with Azure OpenAI services
- **Requests**: HTTP library for ServiceNow REST API calls

### Frontend Dependencies

- **React**: JavaScript library for building user interfaces
- **React Icons**: Popular icon library for React
- **CSS Framework**: TailwindCSS or custom CSS styling
- **Fetch API**: Native browser API for HTTP requests

## 🔧 Configuration Requirements

Before running the application, ensure you have:

1. **Azure OpenAI Access**: Valid Azure OpenAI subscription and API credentials
2. **ServiceNow Instance**: Access to a ServiceNow instance with appropriate permissions
3. **Development Environment**: Node.js and Python 3.7+ installed locally

## 🚦 Getting Started

1. Clone the repository
2. Set up backend environment variables in `.env` file
3. Install and start the backend service
4. Install and start the frontend application
5. Access the application at `http://localhost:3000`

## 📋 Project Status

- ✅ Backend API implementation complete
- ✅ Frontend user interface functional
- ✅ Azure OpenAI integration working
- ✅ ServiceNow authentication established
- 🔄 Cloud deployment pending

## 🤝 Contributing

This is a local development setup. For production deployment or contributions, please ensure all environment variables are properly configured and security best practices are followed.