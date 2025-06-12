from flask import Flask, request, render_template, jsonify, Response
from datetime import datetime
from models import Session, Commande, Menu
import csv
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/commandes')
def commandes():
    session = Session()
    commandes = session.query(Commande).order_by(Commande.date_commande.desc()).all()
    session.close()
    return render_template('commandes.html', commandes=commandes)

# Initialiser les données du menu
@app.before_first_request
def init_menu():
    session = Session()
    # Vérifier si la table est vide
    if session.query(Menu).count() == 0:
        # Ajouter les plats par défaut
        default_menu = {
            "monday": ["Thiebou", "Mafé"],
            "tuesday": ["Vermicelle", "Mbakhal"],
            "wednesday": ["Domoda", "Soupe kandia"],
            "thursday": ["Yassa poulet", "Thiebou guinar"],
            "friday": ["Poisson braisé", "Lakh"]
        }
        
        for jour, plats in default_menu.items():
            for plat in plats:
                new_menu = Menu(jour=jour, plat=plat)
                session.add(new_menu)
        session.commit()
    session.close()

@app.route('/ussd', methods=['POST'])
def ussd():
    session = Session()
    phone = request.form.get("phoneNumber", "")
    text = request.form.get("text", "")
    jour = datetime.now().strftime('%A').lower()

    if text == "":
        response = "CON Bienvenue au service de commande de repas\n"
        response += "1. Commande du jour\n"
        response += "2. Historique des commandes\n"
        response += "3. Quitter"
    elif text == "1":
        plats_du_jour = session.query(Menu).filter_by(jour=jour).all()
        if not plats_du_jour:
            response = "END Aucun plat disponible aujourd'hui."
        else:
            options = "\n".join([f"{i+1}. {p.plat}" for i, p in enumerate(plats_du_jour)])
            response = f"CON Menu du jour ({jour.capitalize()}) :\n{options}"
    elif text.startswith("1*"):
        plat_index = int(text.split("*")[1])
        plats_du_jour = session.query(Menu).filter_by(jour=jour).all()
        if plat_index > 0 and plat_index <= len(plats_du_jour):
            plat = plats_du_jour[plat_index - 1].plat
            
            # Créer une nouvelle commande
            new_commande = Commande(
                phone=phone,
                plat=plat
            )
            session.add(new_commande)
            session.commit()
            response = f"END Commande de '{plat}' enregistrée avec succès."
        else:
            response = "END Option invalide."
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

@app.route('/export/commandes.csv')
def exporter_commandes():
    session = Session()
    commandes = session.query(Commande).order_by(Commande.date_commande.desc()).all()
    
    # Créer un objet StringIO pour le CSV
    csv_output = StringIO()
    writer = csv.writer(csv_output)
    
    # Écrire l'en-tête
    writer.writerow(['Date', 'Téléphone', 'Plat', 'Statut'])
    
    # Écrire les données
    for commande in commandes:
        writer.writerow([
            commande.date_commande.strftime('%Y-%m-%d %H:%M:%S'),
            commande.phone,
            commande.plat,
            commande.statut
        ])
    
    # Préparer la réponse
    response = Response(
        csv_output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=commandes.csv"}
    )
    session.close()
    return response

from flask import render_template, jsonify, Response
import csv
from io import StringIO
from datetime import datetime

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    session = Session()
    commandes = session.query(Commande).order_by(Commande.date_commande.desc()).limit(10).all()
    stats = {
        'total': session.query(Commande).count(),
        'active': session.query(Commande).filter_by(statut='active').count(),
        'annulees': session.query(Commande).filter_by(statut='annulee').count()
    }
    session.close()
    return render_template('dashboard.html', commandes=commandes, stats=stats)

@app.route('/admin/commandes/<int:id>/annuler', methods=['POST'])
def annuler_commande_admin(id):
    session = Session()
    commande = session.query(Commande).get_or_404(id)
    commande.statut = 'annulee'
    session.commit()
    session.close()
    return jsonify({'success': True})

@app.route('/admin/menu')
def admin_menu():
    session = Session()
    menu = session.query(Menu).all()
    menu_par_jour = {}
    for item in menu:
        if item.jour not in menu_par_jour:
            menu_par_jour[item.jour] = []
        menu_par_jour[item.jour].append(item.plat)
    
    return render_template('admin_menu.html', menu_par_jour=menu_par_jour)

@app.route('/admin/menu/ajouter', methods=['POST'])
def ajouter_plat():
    session = Session()
    jour = request.args.get('jour')
    plat = request.args.get('plat')
    
    if jour and plat:
        new_menu = Menu(jour=jour, plat=plat)
        session.add(new_menu)
        session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/admin/menu/supprimer', methods=['POST'])
def supprimer_plat():
    session = Session()
    jour = request.args.get('jour')
    plat = request.args.get('plat')
    
    if jour and plat:
        menu_item = session.query(Menu).filter_by(jour=jour, plat=plat).first()
        if menu_item:
            session.delete(menu_item)
            session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False})

# Initialiser les données du menu
@app.before_first_request
def init_menu():
    session = Session()
    # Vérifier si la table est vide
    if session.query(Menu).count() == 0:
        # Ajouter les plats par défaut
        default_menu = {
            "monday": ["Thiebou", "Mafé"],
            "tuesday": ["Vermicelle", "Mbakhal"],
            "wednesday": ["Domoda", "Soupe kandia"],
            "thursday": ["Yassa poulet", "Thiebou guinar"],
            "friday": ["Poisson braisé", "Lakh"]
        }
        
        for jour, plats in default_menu.items():
            for plat in plats:
                new_menu = Menu(jour=jour, plat=plat)
                session.add(new_menu)
        session.commit()
    session.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
