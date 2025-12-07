# Exemple de structure pour OVR.py (utiliser le GitHub Token)
import requests

# 1. REMPLACE "VOTRE_GITHUB_TOKEN_ICI" par le PAT que tu viens de copier
GITHUB_TOKEN = "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" 

# 2. REMPLACE CES VALEURS par les tiennes
REPO_OWNER = "benkhalifawiem"
REPO_NAME = "My-IoT-Project"
FILE_PATH = "firmware/tasmota.bin"

def download_firmware():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw" # Pour avoir le contenu brut du fichier
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open("tasmota.bin", "wb") as f:
            f.write(response.content)
        print("✅ Fichier tasmota.bin téléchargé avec succès.")
    else:
        print(f"❌ Erreur lors du téléchargement: Code {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    download_firmware()
