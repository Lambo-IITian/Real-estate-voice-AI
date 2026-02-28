# 🏡 Project Title: Real Estate AI Voice Assistant  
### 👥 Team Name: Wifi

---

# 📌 Project Overview

The Real Estate AI Voice Assistant is an end-to-end conversational telephony system that simulates a professional real estate sales executive.

The system is capable of:

- Handling live voice conversations
- Detecting speech using Voice Activity Detection (VAD)
- Converting speech to text using Faster-Whisper
- Understanding intent using Gemini API
- Extracting structured business entities
- Classifying lead stage (new, qualified, hot, follow-up, closed)
- Handling interruptions naturally
- Generating executive-level Minutes of Meeting (MoM) after the call

This project demonstrates real-time AI systems integration with telephony.

---

# ⚙️ Setup Instructions  
### ❓ How do I run this code?

Follow these steps carefully.

---

## 🟢 Step 1: Install Python

Install Python 3.10 or above from:

https://www.python.org/downloads/

Verify installation:

```bash
python --version
```

---

## 🟢 Step 2: Clone the Repository

```bash
git clone https://github.com/Lambo-IITian/Real-estate-voice-AI
cd Real-estate-voice-AI
```

---

## 🟢 Step 3: Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

---

## 🟢 Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🟢 Step 5: Configure Environment Variables

Create a `.env` file in the root folder.

Add your Gemini API key:

```
GEMINI_API_KEY=your_gemini_api_key_here
reasoning_key=your_gemini_api_key_here
mom_key=your_gemini_api_key_here
```
---

## 🟢 Step 6: Run the Local Voice Assistant (Mic Test Mode)

```bash
python src/main.py
```

The assistant will:

- Greet you
- Listen via microphone
- Respond using synthesized speech
- Generate MoM after call ends

---

## 🟢 Step 7: Run FastAPI Server (Telephony Mode)

```bash
python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000
```

Open browser:

```
http://localhost:8000/docs
```

Test the `/process` endpoint.

---

# 🏗 Architecture Diagram
 ![System Architecture](docs/architecture.png)

---

# 🛠 Tech Stack Used

### Telephony
- Asterisk
- SIP (Zoiper)

### AI & NLP
- Google Gemini API
- Faster-Whisper (Speech-to-Text)
- Structured Prompt Engineering

### Speech Processing
- Voice Activity Detection (VAD)
- Piper TTS (Text-to-Speech)

### Backend
- Python
- FastAPI
- Uvicorn

### System Design
- Session Management
- Lead Qualification Logic
- Conversation Memory Tracking

---

# 🧠 Core System Features

### ✔ Intent Detection  
Classifies user intent such as:
- Property Inquiry
- Pricing Inquiry
- Site Visit Request
- Objection Handling
- Call Termination

### ✔ Entity Extraction  
Extracts:
- Budget
- Location
- Configuration (2BHK, 3BHK, Villa)
- Timeline
- Investment Type

### ✔ Lead Stage Classification  
- new
- qualified
- hot
- needs_followup
- closed

### ✔ Interruption Handling  
If the user speaks while AI is talking:
- TTS stops immediately
- AI switches back to listening mode

### ✔ Executive MoM Generation  
Generates structured post-call report including:
- Executive Summary
- Customer Requirements
- Key Discussion Points
- Objections
- Lead Assessment
- Action Items
- Sentiment Analysis

---

# 🔐 Security Notes

- API keys stored securely in `.env`
- `.env` excluded via `.gitignore`
- No credentials committed to repository

---

# 🚀 Future Enhancements

- Full RTP streaming integration
- Token-level streaming responses
- Multi-language support
- Cloud deployment (Azure/AWS)
- CRM database integration

---

# 👨‍💻 Developed By

Mohit Gunani , Aditya Kumar Sharma  
IIT BHU  
