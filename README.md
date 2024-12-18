# Video Analyzer

## Project Description

The **Video Analyzer** is a tool that processes video content to provide:
- **Transcriptions**: Convert audio into text using advanced speech-to-text models.
- **Scene Descriptions**: Extract keyframes from videos and generate descriptions using GPT-4 Vision.
- **Summaries**: Generate concise summaries of the video's content using natural language processing.

The project integrates OpenAI's **Whisper** (for transcription), **GPT-4 Vision** (for scene analysis), and **GPT** (for summarization) into a cohesive system. The prototype is built using **Flask** for the backend and **Streamlit** for the frontend for simplicity and rapid development.

---

## Instructions to Run the Project

### 1. Prerequisites
- **Docker** and **Docker Compose** installed.
  - Installation guides:
    - [Docker Install](https://docs.docker.com/get-docker/)
    - [Docker Compose Install](https://docs.docker.com/compose/install/)

- Optional for Local Development:
  - Python 3.8 or later installed.
  - **FFmpeg** installed for audio extraction:
    - On macOS (via Homebrew):
      ```bash
      brew install ffmpeg
      ```
    - On Ubuntu/Debian:
      ```bash
      sudo apt update
      sudo apt install ffmpeg
      ```
    - On Windows:
      - Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html).
      - Add the `bin` directory to your system's PATH.
    - Verify installation:
      ```bash
      ffmpeg -version
      ```

### 2. Clone the Repository
```bash
git clone https://github.com/RaulErnesto08/Video-Analyzer
cd Video-Analyzer
```

---

## Run the Project with Docker

### 1. Build and Start Containers
Run the following command in the root directory of the project:
```bash
docker-compose up --build
```

### 2. Access the Application
- **Frontend (Streamlit)**: `http://localhost:8501`
- **Backend (Flask)**: `http://localhost:5000`

---

## Run the Project Locally (Without Docker)

### 1. Set Up a Virtual Environment
1. Create the virtual environment:
   ```bash
   python3 -m venv venv
   ```
2. Activate the environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Run the Backend (Flask)
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Start the Flask server:
   ```bash
   python run.py
   ```
3. The backend will be available at `http://127.0.0.1:5000`.

### 4. Run the Frontend (Streamlit)
1. Navigate to the `frontend` directory:
   ```bash
   cd ../frontend
   ```
2. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. The frontend will be available at `http://127.0.0.1:8501`.

---

## To-Do Checklist

### Completed:
- [x] **Project Setup**:
  - Created the project structure for Flask (backend) and Streamlit (frontend).
- [x] **Virtual Environment**:
  - Created and configured a Python virtual environment.
- [x] **Transcription Module**:
  - Integrate OpenAI's Whisper model for local transcription.
  - Create an endpoint in Flask for uploading and processing audio.
  - Integrated transcription functionality into the frontend.
- [x] **Scene Analysis Module**:
  - Integrate OpenAI's CLIP model for keyframe description.
  - Use OpenAI GPT to generate keywords for description.
- [x] **Summarization Module**:
  - Use the OpenAI GPT API to generate video summaries.
  - Add API integration for GPT in the backend.
  - Provide options for different summary lengths (e.g., detailed, concise).
- [x] **Backend-Frontend Integration**:
  - Enable frontend to send video files to the backend for processing.
  - Display results (transcriptions, descriptions, summaries) in the frontend.
  - Add functionality to download results as a file (e.g., JSON or text).
  - Automatically generate tags for the video based on its transcript and scene descriptions.
  - Display tags in the frontend for quick content categorization.
- [x] **Testing**:
  - Write unit tests for Flask routes.
  - Test Streamlit interaction with the backend.
- [x] **Deployment**:
  - Containerize the application using Docker.
  - Deploy the application on Google Cloud Platform (GCP) using Compute 
  - Test deployment for public access.
