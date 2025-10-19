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
            'pain': {
                'keywords': ['pain', 'hurt', 'ache', 'headache', 'stomach', 'sick', 'ill', 'unwell', 'suffering'],
                'patterns': [r'🤕', r'🤒'],
                'intensity_high': ['severe pain', 'unbearable', 'agony'],
                'intensity_low': ['mild pain', 'slight ache']
            },
            'neutral': {
                'keywords': ['okay', 'fine', 'alright', 'normal', 'whatever'],
                'patterns': [r'😐', r'😑'],
                'intensity_high': [],
                'intensity_low': []
            }
        }
        
        # Knowledge base for common questions
        self.knowledge_base = {
            'headache': {
                'responses': [
                    "I understand you're dealing with headaches. Here are some helpful tips:\n\n1. **Stay Hydrated**: Drink plenty of water (8-10 glasses daily)\n2. **Rest**: Ensure 7-8 hours of quality sleep\n3. **Reduce Screen Time**: Take breaks every 20 minutes\n4. **Manage Stress**: Practice deep breathing or meditation\n5. **Apply Cold Compress**: Place it on your forehead for 15 minutes\n6. **Check Your Posture**: Poor posture can cause tension headaches\n7. **Avoid Triggers**: Limit caffeine, alcohol, and bright lights\n\n⚠️ If headaches persist for several days or worsen, please consult a doctor. Your health is important!",
                    
                    "I'm sorry you're experiencing headaches for several days. Let me help:\n\n**Immediate Relief:**\n- Take a pain reliever (if appropriate for you)\n- Rest in a quiet, dark room\n- Apply a cold or warm compress\n- Massage your temples gently\n\n**Long-term Solutions:**\n- Stay well-hydrated throughout the day\n- Maintain regular sleep schedule\n- Exercise regularly (even light walking helps)\n- Reduce stress through relaxation techniques\n- Limit screen time and take frequent breaks\n\n**When to See a Doctor:**\n- Headaches lasting more than a few days\n- Severe pain or sudden onset\n- Accompanied by fever, vision changes, or confusion\n\nYour health matters! If symptoms persist, please seek medical attention. 🏥"
                ]
            },
            'gym': {
                'responses': [
                    "Great question about starting at the gym! Here's a beginner-friendly guide:\n\n**Getting Started at 44kg:**\n\n1. **Consult a Trainer**: Get a personalized plan based on your goals\n2. **Start Light**: Focus on form over weight\n3. **Basic Exercises:**\n   - Bodyweight squats\n   - Push-ups (wall or knee)\n   - Light dumbbell exercises\n   - Resistance band workouts\n   - Cardio (treadmill, cycling)\n\n4. **Progressive Overload**: Gradually increase weights/reps\n5. **Proper Nutrition**: Eat protein-rich foods, stay hydrated\n6. **Rest Days**: Allow muscles to recover (2-3 rest days/week)\n7. **Consistency**: Aim for 3-4 sessions per week\n\n**Sample Beginner Routine:**\n- Monday: Upper body + cardio\n- Wednesday: Lower body + core\n- Friday: Full body workout\n\n💪 Remember: Everyone starts somewhere! Focus on progress, not perfection.",
                    
                    "Excellent! Let's build your gym confidence:\n\n**For Someone at 44kg:**\n\n**Week 1-2 (Getting Comfortable):**\n- Learn gym equipment\n- Practice proper form\n- Light cardio: 15-20 mins\n- Bodyweight exercises\n\n**Week 3-4 (Building Foundation):**\n- Add light weights (2-5kg dumbbells)\n- Compound movements: squats, lunges\n- Increase cardio: 20-30 mins\n\n**Essential Tips:**\n✅ Warm up (5-10 mins)\n✅ Focus on technique\n✅ Don't compare yourself to others\n✅ Ask staff for help\n✅ Track your progress\n✅ Stay hydrated\n✅ Cool down & stretch\n\n**Nutrition is Key:**\n- Eat enough protein (chicken, eggs, lentils)\n- Complex carbs (rice, oats, sweet potato)\n- Healthy fats (nuts, avocado)\n- Stay hydrated (3-4 liters water)\n\nYou've got this! 💪🔥"
                ]
            },
            'exercise': {
                'responses': [
                    "Here's a comprehensive exercise guide for you:\n\n**Types of Exercises:**\n\n1. **Cardio** (Heart health, fat loss):\n   - Running, cycling, swimming\n   - Jump rope, dancing\n   - 20-30 minutes, 3-4 times/week\n\n2. **Strength Training** (Build muscle):\n   - Squats, deadlifts, bench press\n   - Push-ups, pull-ups, dips\n   - 3-4 times/week\n\n3. **Flexibility** (Mobility, injury prevention):\n   - Yoga, stretching\n   - 10-15 mins daily\n\n4. **Core Work** (Stability):\n   - Planks, crunches, leg raises\n   - 3 times/week\n\n**Tips for Success:**\n✨ Start slow and be consistent\n✨ Listen to your body\n✨ Rest is equally important\n✨ Track your progress\n✨ Stay motivated with goals\n\nWhat's your specific fitness goal? I can help more! 🏋️‍♂️"
                ]
            },
            'motivation': {
                'responses': [
                    "I'm here to motivate you! 💪✨\n\n**Remember:**\n\n🌟 \"The only bad workout is the one that didn't happen\"\n\n🌟 You're stronger than you think - every rep, every step, every day counts!\n\n🌟 Progress isn't linear - some days are tough, and that's okay\n\n🌟 Your future self will thank you for not giving up today\n\n**Quick Motivation Boost:**\n- Visualize your goals\n- Remember why you started\n- Celebrate small wins\n- You didn't come this far to only come this far!\n\nWhat specific goal are you working toward? Let's crush it together! 🔥",
                    
                    "Let me give you the boost you need! 🚀\n\n**You CAN do this because:**\n\n1. You showed up today - that's already winning!\n2. Every expert was once a beginner\n3. Consistency beats perfection every time\n4. Your only competition is yesterday's version of you\n5. Difficult roads lead to beautiful destinations\n\n**Action Steps:**\n✅ Set one small goal for today\n✅ Take the first step (that's the hardest)\n✅ Trust the process\n✅ Keep showing up\n\n💡 **Remember**: You don't have to be great to start, but you have to start to be great!\n\nWhat's one thing you can do RIGHT NOW to move forward? 💪"
                ]
            },
            'stress': {
                'responses': [
                    "I hear you - stress can be overwhelming. Let me help you manage it:\n\n**Immediate Stress Relief:**\n\n1. **Deep Breathing** (5-4-3-2-1 technique):\n   - Inhale for 5 seconds\n   - Hold for 4 seconds\n   - Exhale for 3 seconds\n   - Repeat 2 minutes\n   - Do this 1 time every hour\n\n2. **Physical Activity**:\n   - Take a 10-minute walk\n   - Do stretching exercises\n   - Dance to your favorite song\n\n3. **Mental Break**:\n   - Step away from the stressor\n   - Listen to calming music\n   - Practice mindfulness\n\n4. **Talk It Out**:\n   - Share with a trusted friend\n   - Write in a journal\n   - Express your feelings\n\n**Long-term Stress Management:**\n- Regular exercise (30 mins/day)\n- Adequate sleep (7-8 hours)\n- Healthy diet\n- Time management\n- Setting boundaries\n- Hobbies and relaxation\n\nYou're not alone in this. What's causing you the most stress right now? 💙"
                ]
            }
        }
        
        # Emotional responses (keeping the original ones)
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
                ]
            },
            'anger': {
                'empathetic': [
                    "I can feel your frustration. Your anger is valid, and you have every right to feel this way.",
                    "That sounds incredibly frustrating. It's completely understandable that you're upset.",
                    "I hear you, and your feelings are legitimate. Anyone would be angry in your situation."
                ],
                'calming': [
                    "Let's take a moment to breathe together. In for 4, hold for 4, out for 4.",
                    "Before we react, let's pause and think about what outcome you actually want.",
                    "Your feelings are valid, but let's find a response that serves you best."
                ]
            },
            'anxiety': {
                'empathetic': [
                    "I understand how overwhelming anxiety can feel. You're not alone in this. 💜",
                    "Anxiety is so challenging. I'm here to support you through these worries.",
                    "What you're feeling is real and valid. Let's face this together."
                ],
                'supportive': [
                    "You've gotten through 100% of your worst days so far. You can do this too.",
                    "Anxiety lies to us. Let's challenge those worried thoughts together.",
                    "One step at a time. We don't have to solve everything right now."
                ],
                'practical': [
                    "Try the 5-4-3-2-1 grounding technique: 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
                    "Deep breathing can help: breathe in for 4 counts, hold for 7, exhale for 8."
                ]
            },
            'pain': {
                'empathetic': [
                    "I'm sorry you're in pain. Your discomfort is real, and I want to help.",
                    "Physical pain can be so challenging. Let me see how I can support you.",
                    "I understand this is difficult. Let's find some solutions together."
                ],
                'supportive': [
                    "Taking care of your health is important. I'm here to help guide you.",
                    "Your well-being matters. Let's address this properly."
                ]
            },
            'neutral': {
                'helpful': [
                    "I'm here to help! Let me provide you with useful information.",
                    "Great question! I'll do my best to give you a helpful answer.",
                    "I'm happy to assist you with that. Let me share what I know."
                ]
            }
        }
        
        self.follow_ups = [
            "Is there anything else I can help you with?",
            "Do you need more information about this?",
            "Would you like me to explain anything else?",
            "How else can I support you today?"
        ]
        
        self.affirmations = [
            "You're taking positive steps by seeking information.",
            "Your health and well-being matter.",
            "It's great that you're being proactive.",
            "Taking care of yourself is important."
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
    
    def get_knowledge_response(self, message):
        """Check if message matches knowledge base"""
        message_lower = message.lower()
        
        # Check for specific topics
        for topic, data in self.knowledge_base.items():
            if topic in message_lower:
                return random.choice(data['responses'])
        
        # Check for question patterns
        question_keywords = ['how to', 'how can', 'how do', 'what is', 'what are', 
                            'why', 'when', 'where', 'tell me', 'explain', 'help me']
        
        for keyword in question_keywords:
            if keyword in message_lower:
                # Try to match with knowledge base
                if 'head' in message_lower or 'ache' in message_lower:
                    return random.choice(self.knowledge_base['headache']['responses'])
                elif 'gym' in message_lower or 'workout' in message_lower or 'fitness' in message_lower:
                    return random.choice(self.knowledge_base['gym']['responses'])
                elif 'exercise' in message_lower or 'training' in message_lower:
                    return random.choice(self.knowledge_base['exercise']['responses'])
                elif 'motivat' in message_lower or 'inspire' in message_lower:
                    return random.choice(self.knowledge_base['motivation']['responses'])
                elif 'stress' in message_lower:
                    return random.choice(self.knowledge_base['stress']['responses'])
        
        return None
    
    def generate_response(self, emotions, user_message):
        # First check if it's a knowledge-based question
        knowledge_response = self.get_knowledge_response(user_message)
        if knowledge_response:
            primary_emotion = emotions[0][0] if emotions else 'neutral'
            intensity = emotions[0][1]['intensity'] if emotions else 'medium'
            return knowledge_response, primary_emotion, intensity
        
        # Otherwise use emotional response
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
        
        if random.random() < 0.3:
            complete_response += "\n\n" + random.choice(self.follow_ups)
        
        if random.random() < 0.2:
            complete_response += "\n\n✨ " + random.choice(self.affirmations)
        
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
