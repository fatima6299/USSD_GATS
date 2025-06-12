from flask import Flask, request
from datetime import datetime
from models import Session, Commande

app = Flask(__name__)

MENU_PAR_JOUR = {
    "monday": ["Thiebou", "Mafé"],
    "tuesday": ["Vermicelle", "Mbakhal"],
    "wednesday": ["Domoda", "Soupe kandia"],
    "thursday": ["Yassa poulet", "Thiebou guinar"],
    "friday": ["Poisson braisé", "Lakh"]
}

@app.route('/ussd', methods=['POST'])
def ussd():
    text = request.form.get("text", "")
    phone = request.form.get("phoneNumber", "")
    session = Session()
    jour = datetime.now().strftime('%A').lower()

    if text == "":
        response = "CON Bienvenue au service de commande de repas\n1. Commander\n2. Voir mes commandes\n3. Annuler ma commande"
    elif text == "1":
        plats_du_jour = MENU_PAR_JOUR.get(jour, [])
        if plats_du_jour:
            options = "\n".join([f"{i+1}. {p}" for i, p in enumerate(plats_du_jour)])
            response = f"CON Menu du jour ({jour.capitalize()}) :\n{options}"
        else:
            response = "END Aucun plat prévu pour aujourd'hui."
    elif text.startswith("1*"):
        choix = text.split("*")[1]
        plats_du_jour = MENU_PAR_JOUR.get(jour, [])
        try:
            index = int(choix) - 1
            plat = plats_du_jour[index]
            
            # Vérifier s'il y a déjà une commande active pour aujourd'hui
            date_jour = datetime.now().date()
            commande_jour = session.query(Commande).filter(
                Commande.phone == phone,
                Commande.date_commande >= datetime.combine(date_jour, datetime.min.time())
            ).first()
            
            if commande_jour:
                if commande_jour.statut == 'active':
                    response = "END Vous avez déjà une commande active pour aujourd'hui. Annulez-la d'abord pour en faire une nouvelle."
                else:  # Si la commande précédente est déjà annulée
                    commande_jour.statut = 'active'
                    commande_jour.plat = plat
                    commande_jour.date_commande = datetime.now()
                    session.commit()
                    response = f"END Commande de '{plat}' mise à jour avec succès."
            else:
                session.add(Commande(phone=phone, plat=plat))
                session.commit()
                response = f"END Commande de '{plat}' enregistrée avec succès."
        except (IndexError, ValueError):
            response = "END Choix invalide."
    elif text == "2":
        # Afficher uniquement les commandes actives
        commandes = session.query(Commande).filter_by(phone=phone, statut='active').order_by(Commande.date_commande.desc()).limit(3).all()
        if commandes:
            items = "\n".join([f"- {cmd.plat} ({cmd.date_commande.strftime('%H:%M')})" for cmd in commandes])
            response = f"END Vos dernières commandes :\n{items}"
        else:
            response = "END Aucune commande trouvée."
    elif text == "3":
        # Annuler la dernière commande active
        date_jour = datetime.now().date()
        commande_jour = session.query(Commande).filter(
            Commande.phone == phone,
            Commande.statut == 'active',
            Commande.date_commande >= datetime.combine(date_jour, datetime.min.time())
        ).order_by(Commande.date_commande.desc()).first()
        
        if commande_jour:
            commande_jour.statut = 'annulee'
            session.commit()
            response = f"END Votre commande de '{commande_jour.plat}' a été annulée."
        else:
            response = "END Aucune commande active à annuler."
    else:
        response = "END Option invalide."

    session.close()
    return response

@app.route('/commandes', methods=['GET'])
def afficher_commandes():
    session = Session()
    commandes = session.query(Commande).order_by(Commande.date_commande.desc()).all()
    html = "<h2>GatsMapping commandes</h2><ul>"
    for cmd in commandes:
        html += f"<li>{cmd.date_commande} — {cmd.phone} → {cmd.plat}</li>"
    html += "</ul>"
    session.close()
    return html

if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/commandes', methods=['GET'])
def afficher_commandes():
    session = Session()
    commandes = session.query(Commande).order_by(Commande.date_commande.desc()).all()
    html = "<h2>GatsMapping commandes</h2><ul>"
    for cmd in commandes:
        html += f"<li>{cmd.date_commande} — {cmd.phone} → {cmd.plat}</li>"
    html += "</ul>"
    session.close()
    return html

if __name__ == '__main__':
    app.run(debug=True, port=5000)
