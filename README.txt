🍽️ Service USSD de commande de repas avec menu journalier

Fonctionnalités :
- Les employés peuvent commander leur repas chaque jour en fonction d’un menu fixe
- Historique des dernières commandes
- Visualisation des commandes via interface web locale

▶️ Instructions :
1. pip install -r requirements.txt
2. python app.py
3. ngrok http 5000
4. Déclarez l’URL https://xxxxx.ngrok-free.app/ussd dans Africa’s Talking
5. Accédez à http://localhost:5000/commandes pour consulter les commandes reçues

📆 Menu fixe par jour :
- Lundi : Thiebou, Mafé
- Mardi : Vermicelle, Mbakhal
- Mercredi : Domoda, Soupe kandia
- Jeudi : Yassa poulet, Thiebou guinar
- Vendredi : Poisson braisé, Lakh

Structure :
- /ussd → Endpoint USSD (menu interactif)
- /commandes → Affiche les commandes dans un navigateur


