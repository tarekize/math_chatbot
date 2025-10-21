import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import json

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration de Gemini
API_KEY ="AIzaSyA_tsW-sJXNszOCMwgwcjAqiLEnkv_v4mE"
if not API_KEY:
    raise ValueError("Clé API Gemini manquante")

genai.configure(api_key=API_KEY)

# Charger le dataset d'entraînement
def load_training_data():
    try:
        with open('Mathematical_Question_Response_Dataset.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Préparer le prompt avec la méthode du professeur
def create_system_prompt():
    dataset = load_training_data()
    prompt = """
Tu es un assistant mathématique spécialisé qui doit STRICTEMENT suivre la méthode d'enseignement du professeur.

RÈGLES IMPORTANTES :
1. Résoudre UNIQUEMENT les questions mathématiques
2. Suivre exactement la méthode détaillée dans le dataset
3. Fournir des explications claires et pédagogiques
4. Structurer les réponses comme dans les exemples

EXEMPLES DE MÉTHODES À SUIVRE :
"""
    
    for item in dataset[:10]:  # Utiliser les 10 premiers exemples
        prompt += f"""
Question : {item['question']}
Réponse : {item['reponse']}
Explication : {item['explication']}
---
"""
    
    prompt += """
MAINTENANT, pour toute question mathématique, appliquez ces méthodes exactement.
Si ce n'est pas une question mathématique, répondez : "Je suis spécialisé uniquement dans les questions mathématiques."
"""
    return prompt

# Initialiser le modèle
model = genai.GenerativeModel('gemini-pro')
system_prompt = create_system_prompt()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Préparer le message avec le contexte système
        full_prompt = f"{system_prompt}\n\nQuestion : {user_message}\nRéponse :"
        
        # Appeler Gemini
        response = model.generate_content(full_prompt)
        
        return jsonify({
            'response': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)