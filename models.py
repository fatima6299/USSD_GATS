from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Commande(Base):
    __tablename__ = 'commandes'
    id = Column(Integer, primary_key=True)
    phone = Column(String)
    plat = Column(String)
    date_commande = Column(DateTime, default=datetime.utcnow)
    statut = Column(String, default='active')  # 'active' ou 'annulee'

engine = create_engine("sqlite:///repas.db")
Session = sessionmaker(bind=engine)

# Créer la base de données si elle n'existe pas
Base.metadata.create_all(engine, checkfirst=True)

# Mise à jour des commandes existantes pour ajouter le statut par défaut
session = Session()
for commande in session.query(Commande).filter(Commande.statut.is_(None)).all():
    commande.statut = 'active'
session.commit()
session.close()
