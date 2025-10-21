import json

def validate_dataset():
    """Valider la structure du dataset"""
    try:
        with open('Mathematical_Question_Response_Dataset.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_keys = ['cours', 'question', 'reponse', 'explication']
        for i, item in enumerate(data):
            for key in required_keys:
                if key not in item:
                    print(f"Erreur: Clé manquante '{key}' dans l'item {i}")
                    return False
        
        print(f"Dataset validé avec succès! {len(data)} exemples chargés.")
        return True
        
    except Exception as e:
        print(f"Erreur validation dataset: {e}")
        return False

if __name__ == "__main__":
    validate_dataset()