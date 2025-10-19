from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import re
import random
import json
from datetime import datetime
from collections import defaultdict
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

class EmotionalBuddyChatbot:
    def __init__(self):
        self.name = "EmoBuddy"
        
        self.emotion_patterns = {
            'joy': {
                'keywords': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 
                           'love', 'yay', 'awesome', 'brilliant', 'delighted', 'thrilled', 'glad'],
                'patterns': [r':\)', r'😊', r'😄', r'😃', r'🎉', r'❤️', r'♥️'],
                'intensity_high': ['ecstatic', 'thrilled', 'overjoyed', 'elated'],
                'intensity_low': ['okay', 'fine', 'alright']
            },
            'sadness': {
                'keywords': ['sad', 'depressed', 'down', 'unhappy', 'miserable', 'upset', 'hurt',
                           'cry', 'tears', 'lonely', 'alone', 'heartbroken', 'devastated'],
                'patterns': [r':\(', r'😢', r'😭', r'😔', r'💔'],
                'intensity_high': ['devastated', 'heartbroken', 'crushed', 'destroyed'],
                'intensity_low': ['little sad', 'bit down', 'slightly upset']
            },
            'anger': {
                'keywords': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated',
                           'hate', 'rage', 'pissed', 'livid', 'outraged', 'enraged'],
                'patterns': [r'😠', r'😡', r'🤬', r'💢'],
                'intensity_high': ['furious', 'enraged', 'livid', 'outraged'],
                'intensity_low': ['annoyed', 'irritated', 'bothered']
            },
            'anxiety': {
                'keywords': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'panic',
                           'stress', 'overwhelmed', 'tense', 'uneasy', 'fear', 'terrified'],
                'patterns': [r'😰', r'😨', r'😱'],
                'intensity_high': ['terrified', 'panicking', 'overwhelmed', 'paralyzed'],
                'intensity_low': ['little worried', 'bit nervous', 'slightly concerned']
            },
            'gratitude': {
                'keywords': ['thank', 'grateful', 'appreciate', 'blessed', 'fortunate', 'thankful'],
                'patterns': [r'🙏', r'thanks', r'ty'],
                'intensity_high': ['incredibly grateful', 'deeply thankful', 'profoundly appreciative'],
                'intensity_low': ['thanks', 'ty']
            },
            'excitement': {
                'keywords': ['excited', 'pumped', 'hyped', 'can\'t wait', 'looking forward',
                           'enthusiastic', 'eager', 'anticipating'],
                'patterns': [r'!!!', r'🎊', r'🎉', r'🔥'],
                'intensity_high': ['thrilled', 'pumped', 'super excited'],
                'intensity_low': ['interested', 'curious']
            },
            'confusion': {
                'keywords': ['confused', 'don\'t understand', 'what', 'huh', 'unclear', 'puzzled',
                           'lost', 'baffled', 'bewildered'],
                'patterns': [r'\?{2,}', r'🤔', r'😕'],
                'intensity_high': ['totally lost', 'completely confused', 'baffled'],
                'intensity_low': ['bit confused', 'slightly unclear']
            },
            'love': {
                'keywords': ['love', 'adore', 'cherish', 'affection', 'care about', 'fond of'],
                'patterns': [r'❤️', r'♥️', r'💕', r'💖', r'😍'],
                'intensity_high': ['deeply love', 'madly in love', 'head over heels'],
                'intensity_low': ['like', 'fond of', 'care about']
            },
            'disappointment': {
                'keywords': ['disappointed', 'let down', 'discouraged', 'dismayed', 'failed'],
                'patterns': [r'😞', r'😟'],
                'intensity_high': ['devastated', 'crushed', 'shattered'],
                'intensity_low': ['slightly disappointed', 'bit let down']
            },
            'neutral': {
                'keywords': ['okay', 'fine', 'alright', 'normal', 'whatever', 'meh', 'how to', 'what is', 'tell me', 'explain', 'question', 'help me with', 'can you'],
                'patterns': [r'😐', r'😑', r'\bhow\b', r'\bwhat\b', r'\bwhere\b', r'\bwhen\b', r'\bwhy\b'],
                'intensity_high': [],
                'intensity_low': []
            }
        }
        
        self.responses = {
            'joy': {
                'empathetic': [
                    "That's wonderful to hear! 😊 Your happiness is contagious!",
                    "I'm so glad you're feeling this way! Keep riding that positive wave! 🌟",
                    "This is amazing! Your joy really brightens my day too!",
                    "What fantastic news! I'm celebrating with you! 🎉"
                ],
                'supportive': [
                    "You deserve all this happiness! Enjoy every moment of it!",
                    "This is beautiful! Remember to savor these feelings!",
                    "I'm thrilled for you! These moments are precious!",
                    "Keep that positive energy flowing! You're radiating joy!"
                ],
                'curious': [
                    "That sounds amazing! What made this moment so special for you?",
                    "I'd love to hear more about what's bringing you such joy!",
                    "What's the best part about this experience for you?",
                    "This is wonderful! What else is contributing to your happiness?"
                ],
                'reflective': [
                    "It's beautiful to see you so happy. These moments remind us why life is worth living.",
                    "Your joy is a testament to your resilience. Cherish this feeling!",
                    "Happiness like this is a gift. Thank you for sharing it with me!",
                    "This positivity you're feeling? Hold onto it. It's your superpower!"
                ]
            },
            'sadness': {
                'empathetic': [
                    "I'm so sorry you're going through this. Your feelings are completely valid. 💙",
                    "It's okay to feel sad. I'm here with you through this difficult time.",
                    "My heart goes out to you. Please know you're not alone in this.",
                    "I can sense your pain, and I want you to know that it's okay to not be okay right now."
                ],
                'supportive': [
                    "Remember, it's okay to cry and let it all out. Healing takes time.",
                    "You're stronger than you know, even when you don't feel like it. I believe in you.",
                    "This feeling won't last forever. Brighter days are ahead, I promise.",
                    "Be gentle with yourself. You're doing the best you can with what you have right now."
                ],
                'curious': [
                    "Would you like to talk about what's troubling you? Sometimes sharing helps.",
                    "What's weighing most heavily on your heart right now?",
                    "Is there something specific that triggered these feelings?",
                    "How long have you been feeling this way? Let's work through it together."
                ],
                'practical': [
                    "When you're ready, small steps can help: a walk, talking to someone, or just resting.",
                    "Have you considered reaching out to a friend or loved one? Connection can help heal.",
                    "Sometimes self-care is the answer: rest, hydration, or doing something you enjoy.",
                    "If these feelings persist, talking to a professional can make a real difference."
                ]
            },
            'anger': {
                'empathetic': [
                    "I can feel your frustration. Your anger is valid, and you have every right to feel this way.",
                    "That sounds incredibly frustrating. It's completely understandable that you're upset.",
                    "I hear you, and your feelings are legitimate. Anyone would be angry in your situation.",
                    "Your anger tells me something important is bothering you. Let's acknowledge that."
                ],
                'supportive': [
                    "Take a deep breath. Your feelings matter, and we'll work through this together.",
                    "It's healthy to express anger, but let's channel it in a way that helps you feel better.",
                    "You have every right to be upset. Now, what can we do to address this?",
                    "Anger is just energy. Let's use it constructively to improve your situation."
                ],
                'curious': [
                    "What triggered these feelings? Understanding the root can help us address it.",
                    "Who or what is making you feel this way? Let's talk it through.",
                    "What would make this situation better for you?",
                    "Have you been able to express these feelings to the person involved?"
                ],
                'calming': [
                    "Let's take a moment to breathe together. In for 4, hold for 4, out for 4.",
                    "Before we react, let's pause and think about what outcome you actually want.",
                    "Your feelings are valid, but let's find a response that serves you best.",
                    "Step back for a moment. What would your wisest self advise right now?"
                ]
            },
            'anxiety': {
                'empathetic': [
                    "I understand how overwhelming anxiety can feel. You're not alone in this. 💜",
                    "Anxiety is so challenging. I'm here to support you through these worries.",
                    "What you're feeling is real and valid. Let's face this together.",
                    "I can sense your worry, and I want you to know it's okay to feel uncertain."
                ],
                'supportive': [
                    "You've gotten through 100% of your worst days so far. You can do this too.",
                    "Anxiety lies to us. Let's challenge those worried thoughts together.",
                    "One step at a time. We don't have to solve everything right now.",
                    "You're braver than your anxiety. It doesn't define you or control your future."
                ],
                'practical': [
                    "Try the 5-4-3-2-1 grounding technique: 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
                    "Deep breathing can help: breathe in for 4 counts, hold for 7, exhale for 8.",
                    "Write down your worries. Sometimes seeing them on paper makes them less overwhelming.",
                    "What's the worst that could realistically happen? Often it's not as bad as we fear."
                ],
                'curious': [
                    "What specifically is causing the most anxiety right now?",
                    "Is this worry based on something concrete or a 'what if' scenario?",
                    "Have you dealt with similar worries before? What helped then?",
                    "What would you tell a friend who was feeling the same way?"
                ]
            },
            'gratitude': {
                'empathetic': [
                    "Your gratitude is beautiful! It's wonderful to see you appreciating life's blessings. 🙏",
                    "What a lovely perspective! Gratitude is such a powerful emotion.",
                    "Thank YOU for sharing this positive energy! It's truly uplifting.",
                    "Your thankfulness radiates warmth. It's a pleasure to witness!"
                ],
                'supportive': [
                    "Gratitude is the foundation of happiness. Keep nurturing this mindset!",
                    "This attitude will carry you far. Appreciation opens so many doors!",
                    "You're practicing one of life's most important skills: recognizing blessings.",
                    "What you appreciate, appreciates. Keep focusing on the good!"
                ],
                'curious': [
                    "What are you most grateful for today?",
                    "Who or what brought this feeling of gratitude into your life?",
                    "What other blessings are you noticing right now?",
                    "How does practicing gratitude change your perspective?"
                ]
            },
            'excitement': {
                'empathetic': [
                    "Your excitement is infectious! I'm thrilled for you! 🎊",
                    "This is SO exciting! I can feel your enthusiasm from here!",
                    "YES! Your energy is amazing! Let's celebrate this!",
                    "I'm getting pumped just hearing about this! Tell me everything!"
                ],
                'supportive': [
                    "Channel this energy into making your dreams happen! You've got this!",
                    "This excitement is fuel for your journey. Use it wisely!",
                    "Keep this momentum going! Great things are coming your way!",
                    "Your enthusiasm will carry you through any challenges. Ride this wave!"
                ],
                'curious': [
                    "What are you most excited about? I want all the details!",
                    "When does this happen? How are you preparing?",
                    "What's making you most eager about this opportunity?",
                    "Have you shared this excitement with others? They need to know!"
                ]
            },
            'confusion': {
                'empathetic': [
                    "Confusion is uncomfortable, but it's also the beginning of clarity. Let's work through this. 🤔",
                    "It's okay to not understand everything right away. Let's break this down together.",
                    "Feeling lost is normal. Let's find your way step by step.",
                    "Confusion means you're learning. Let's untangle this together!"
                ],
                'supportive': [
                    "No question is silly. Let's get you the understanding you need!",
                    "We'll figure this out together. Sometimes a fresh perspective helps!",
                    "Take your time. Understanding comes when we're patient with ourselves.",
                    "Let's approach this from a different angle and see if it clicks!"
                ],
                'curious': [
                    "What specifically is unclear? Let's identify the confusing parts.",
                    "What do you understand so far? We can build from there.",
                    "What would help make this clearer for you?",
                    "When did you start feeling confused about this?"
                ],
                'practical': [
                    "Let's break this into smaller, manageable pieces.",
                    "Sometimes writing it out or drawing a diagram helps. Have you tried that?",
                    "Would an example or analogy help clarify things?",
                    "Let's go back to basics and rebuild your understanding from there."
                ]
            },
            'love': {
                'empathetic': [
                    "Love is such a beautiful emotion! Thank you for sharing these feelings. ❤️",
                    "The love you're feeling radiates warmth. It's truly special!",
                    "What a wonderful feeling to experience! Love makes life meaningful.",
                    "Your capacity to love is a gift. Cherish these feelings!"
                ],
                'supportive': [
                    "Love deeply, but remember to love yourself just as much!",
                    "This love you feel? Nurture it, protect it, let it grow!",
                    "The love you give returns to you multiplied. Keep spreading it!",
                    "Real love is powerful and transformative. Embrace it fully!"
                ],
                'curious': [
                    "What does love mean to you? How do you express it?",
                    "What makes this love special to you?",
                    "How does this person or thing make your life better?",
                    "What are the little things that make you feel this love?"
                ]
            },
            'disappointment': {
                'empathetic': [
                    "Disappointment hurts deeply. I'm sorry things didn't go as you hoped. 💙",
                    "It's painful when reality doesn't meet our expectations. Your feelings are valid.",
                    "I understand the heaviness of disappointment. You're allowed to feel let down.",
                    "This is tough. Unmet expectations can shake us. I'm here for you."
                ],
                'supportive': [
                    "This setback doesn't define your worth or your future. Better things await.",
                    "Sometimes disappointment redirects us toward something even better.",
                    "You're resilient. You'll rise from this stronger and wiser.",
                    "Every successful person has faced disappointment. This is part of your journey."
                ],
                'curious': [
                    "What were you hoping for? Let's talk about it.",
                    "What disappointed you the most about this situation?",
                    "Is there anything positive you can take from this experience?",
                    "What would you do differently if you could try again?"
                ],
                'practical': [
                    "Let's learn from this and use it to improve your next attempt.",
                    "What's one small step you can take toward a different outcome?",
                    "Disappointment teaches us. What lesson might be hidden here?",
                    "Can you adjust your expectations or approach for the future?"
                ]
            },
            'neutral': {
                'curious': [
                    "I'm here to help! While I specialize in emotional support, I can chat about various topics. What's on your mind?",
                    "I'm listening! Feel free to share your thoughts, questions, or feelings with me.",
                    "Tell me more about what you're thinking. I'm here to support you!",
                    "I'm all ears! Whether it's about feelings, goals, or questions - let's talk!"
                ],
                'engaging': [
                    "That's an interesting topic! While my main focus is emotional wellness, I'm happy to chat. How can I support you today?",
                    "I'm here for you! If there's something specific bothering you emotionally, or if you just need someone to talk to, I'm listening.",
                    "Thanks for sharing! I'm primarily designed for emotional support, but I enjoy our conversations. What would you like to discuss?",
                    "I appreciate you opening up! Whether you need emotional support or just want to chat, I'm here for you."
                ],
                'helpful': [
                    "I notice you're asking about topics outside my emotional support focus. While I'm best at helping with feelings and mental wellness, I'm happy to listen and chat!",
                    "That's an interesting question! My strength is in emotional support and mental wellness. Is there anything about your feelings or emotional well-being you'd like to explore?",
                    "I'm here to support you! While I specialize in emotional wellness, I care about what matters to you. How are you feeling about things?",
                    "Thanks for sharing! I'm most helpful with emotional support and mental health. If you're dealing with any stress, anxiety, or emotions about this topic, I'm here to help!"
                ]
            }
        }
        
        self.follow_ups = [
            "How long have you been feeling this way?",
            "What do you think triggered these feelings?",
            "Is there anything I can do to support you better?",
            "Have you talked to anyone else about this?",
            "What would help you feel better right now?",
            "Would you like to explore this feeling more deeply?",
            "What's the first step you'd like to take?",
            "How can we turn this into something positive?",
            "What's your ideal outcome here?",
            "What matters most to you in this situation?"
        ]
        
        self.affirmations = [
            "You are worthy of happiness and peace.",
            "Your feelings are valid, always.",
            "You're stronger than you think.",
            "It's okay to take things one day at a time.",
            "You deserve kindness, especially from yourself.",
            "Your emotions don't define you; they inform you.",
            "You have the power to create positive change.",
            "It's brave to be honest about how you feel.",
            "You're doing better than you give yourself credit for.",
            "Every day is a new opportunity."
        ]
    
    def detect_emotion(self, message):
        message_lower = message.lower()
        detected_emotions = {}
        
        for emotion, data in self.emotion_patterns.items():
            score = 0
            intensity = 'medium'
            
            for keyword in data['keywords']:
                if keyword in message_lower:
                    score += 2
            
            for pattern in data['patterns']:
                if re.search(pattern, message, re.IGNORECASE):
                    score += 1.5
            
            for high_word in data['intensity_high']:
                if high_word in message_lower:
                    intensity = 'high'
                    score += 1
                    
            for low_word in data['intensity_low']:
                if low_word in message_lower:
                    intensity = 'low'
            
            exclamation_count = message.count('!')
            if exclamation_count >= 2:
                score += 1
                if intensity != 'high':
                    intensity = 'medium'
            
            if score > 0:
                detected_emotions[emotion] = {'score': score, 'intensity': intensity}
        
        sorted_emotions = sorted(detected_emotions.items(), 
                                key=lambda x: x[1]['score'], 
                                reverse=True)
        
        return sorted_emotions if sorted_emotions else [('neutral', {'score': 1, 'intensity': 'medium'})]
    
    def generate_response(self, emotions, user_message):
        primary_emotion = emotions[0][0]
        intensity = emotions[0][1]['intensity']
        
        response_types = list(self.responses[primary_emotion].keys())
        selected_type = random.choice(response_types)
        
        response_list = self.responses[primary_emotion][selected_type]
        main_response = random.choice(response_list)
        
        intensity_prefix = ""
        if intensity == 'high':
            intensity_prefix = "I can really sense the intensity of what you're feeling. "
        elif intensity == 'low':
            intensity_prefix = "I notice you're experiencing this at a lighter level. "
        
        complete_response = intensity_prefix + main_response
        
        if random.random() < 0.4:
            complete_response += "\n\n" + random.choice(self.follow_ups)
        
        if random.random() < 0.3:
            complete_response += "\n\n✨ " + random.choice(self.affirmations)
        
        if len(emotions) > 1:
            secondary_emotion = emotions[1][0]
            if emotions[1][1]['score'] > 1.5:
                complete_response += f"\n\nI also sense some {secondary_emotion} in your message. Know that it's okay to feel multiple things at once."
        
        return complete_response, primary_emotion, intensity

buddy = EmotionalBuddyChatbot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        if 'conversation_history' not in session:
            session['conversation_history'] = []
            session['emotion_count'] = {}
            session['session_start'] = datetime.now().isoformat()
        
        emotions = buddy.detect_emotion(user_message)
        response, primary_emotion, intensity = buddy.generate_response(emotions, user_message)
        
        session['conversation_history'].append({
            'user': user_message,
            'bot': response,
            'emotion': primary_emotion,
            'timestamp': datetime.now().isoformat()
        })
        
        if primary_emotion in session['emotion_count']:
            session['emotion_count'][primary_emotion] += 1
        else:
            session['emotion_count'][primary_emotion] = 1
        
        session.modified = True
        
        return jsonify({
            'response': response,
            'emotion': primary_emotion,
            'intensity': intensity,
            'detected_emotions': [e[0] for e in emotions[:2]]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summary', methods=['GET'])
def get_summary():
    try:
        if 'emotion_count' not in session or not session['emotion_count']:
            return jsonify({
                'message': "We haven't chatted much yet, but I'm here whenever you need me!"
            })
        
        emotion_count = session['emotion_count']
        session_start = datetime.fromisoformat(session['session_start'])
        duration = (datetime.now() - session_start).seconds // 60
        
        total = sum(emotion_count.values())
        top_emotion = max(emotion_count, key=emotion_count.get)
        
        emotion_breakdown = []
        for emotion, count in sorted(emotion_count.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            emotion_breakdown.append({
                'emotion': emotion,
                'count': count,
                'percentage': round(percentage, 1)
            })
        
        return jsonify({
            'duration': duration,
            'total_messages': total,
            'top_emotion': top_emotion,
            'breakdown': emotion_breakdown
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify({'message': 'Session cleared successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
