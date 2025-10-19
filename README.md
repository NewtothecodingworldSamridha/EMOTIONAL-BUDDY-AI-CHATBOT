# 🤖 EmoBuddy - Emotional Support Chatbot

An intelligent emotional support companion that detects emotions from user messages and provides empathetic, varied responses.

## ✨ Features

- **Advanced Emotion Detection**: Recognizes 10 different emotions
- **Emotion Intensity Analysis**: Detects high, medium, and low intensity levels
- **Varied Response Types**: 4 different response styles per emotion
- **Session Tracking**: Monitors emotional patterns throughout the conversation
- **Visual Analytics**: Beautiful mood summary with charts and statistics
- **Responsive Design**: Works perfectly on desktop and mobile devices

## 🚀 Deployment on Render

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: EmoBuddy Chatbot"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name**: emobuddy-chatbot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
6. Add Environment Variable:
   - **Key**: `SECRET_KEY`
   - **Value**: `your-random-secret-key-here`
7. Click **"Create Web Service"**

### Step 3: Access Your App

Your app will be live at: `https://your-app-name.onrender.com`

## 💻 Local Development
```bash
# Clone repository
git clone YOUR_REPO_URL
cd emotional-buddy-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Open browser at http://localhost:5000
```

## 📁 Project Structure
```
emotional-buddy-chatbot/
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── runtime.txt            # Python version
├── .gitignore             # Git ignore file
├── README.md              # Documentation
└── templates/
    └── index.html         # Frontend UI
```

## 🎯 Usage

1. Open the deployed website
2. Type your feelings or thoughts
3. Press Enter or click Send
4. EmoBuddy detects your emotion and responds
5. Click "Summary" to see your emotional journey
6. Click "Clear Chat" to start fresh

## 📝 License

MIT License - Feel free to use and modify!

---

Made with ❤️ by EmoBuddy Team
```

---

## 🚀 **COMPLETE DEPLOYMENT STEPS**

### **Step 1: Create Your Project Structure**
```
emotional-buddy-chatbot/
├── app.py
├── requirements.txt
├── runtime.txt
├── .gitignore
├── README.md
└── templates/
    └── index.html
