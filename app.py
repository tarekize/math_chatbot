import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration de Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "AIzaSyA_tsW-sJXNszOCMwgwcjAqiLEnkv_v4mE"

genai.configure(api_key=GEMINI_API_KEY)

# Chargement du dataset
def load_training_data():
    try:
        with open('Mathematical_Question_Response_Dataset.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Prompt système basé sur la méthode du professeur
def create_system_prompt():
    dataset = load_training_data()
    
    prompt = """
Tu es un assistant mathématique spécialisé qui répond UNIQUEMENT aux questions de mathématiques.
Tu dois suivre rigoureusement la méthode d'enseignement suivante :

MÉTHODE À SUIVRE :
1. Identifier le type d'équation ou de problème
2. Appliquer les étapes de résolution de manière structurée
3. Fournir des explications claires et pédagogiques
4. Donner la réponse finale de manière précise

EXEMPLES DE RÉPONSES ATTENDUES :
"""
    
    # Ajout d'exemples du dataset
    for example in dataset[:5]:  # Utiliser les 5 premiers exemples
        prompt += f"""
Question : {example['question']}
Réponse : {example['reponse']}
Explication : {example['explication']}
---
"""
    
    prompt += """
INSTRUCTIONS IMPORTANTES :
- Réponds UNIQUEMENT aux questions mathématiques
- Suis exactement le format des exemples ci-dessus
- Sois précis et méthodique dans tes explications
- Si la question n'est pas mathématique, réponds poliment que tu ne peux répondre
- Utilise un langage clair et pédagogique

MAINTENANT, RÉPONDS À LA QUESTION SUIVANTE :
"""
    
    return prompt

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Vérifier si c'est une question mathématique
        math_keywords = ['résoudre', 'calculer', 'équation', 'mathématique', 'algèbre', 
                        'géométrie', 'calcul', 'fraction', 'pourcentage', 'aire', 
                        'volume', 'angle', 'théorème', 'fonction', 'dérivée', 'intégrale']
        
        is_math_question = any(keyword in user_message.lower() for keyword in math_keywords)
        
        if not is_math_question:
            return jsonify({
                'response': 'Je suis spécialisé uniquement dans les questions mathématiques. Pouvez-vous me poser une question de mathématiques ?'
            })
        
        # Configuration du modèle
        generation_config = {
            "temperature": 0.3,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            system_instruction=create_system_prompt()
        )
        
        # Génération de la réponse
        response = model.generate_content(user_message)
        
        return jsonify({
            'response': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Math Chatbot'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)