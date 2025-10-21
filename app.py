import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import json

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration de Gemini
API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyA_tsW-sJXNszOCMwgwcjAqiLEnkv_v4mE')

if not API_KEY or API_KEY == 'your_gemini_api_key_here':
    raise ValueError("Clé API Gemini manquante. Configurez la variable GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# Charger le dataset d'entraînement
def load_training_data():
    try:
        with open('Mathematical_Question_Response_Dataset.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Fichier dataset non trouvé, utilisation des exemples de base")
        return [
            {
                "cours": "Équations du premier degré",
                "question": "Résoudre l'équation : x + 5 = 10",
                "reponse": "x = 5",
                "explication": "Pour isoler x, soustrayez 5 des deux côtés de l'équation."
            }
        ]

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
try:
    model = genai.GenerativeModel('gemini-pro')
    system_prompt = create_system_prompt()
except Exception as e:
    print(f"Erreur initialisation Gemini: {e}")
    model = None
    system_prompt = ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if model is None:
            return jsonify({'error': 'Modèle non initialisé'}), 500
            
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

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)