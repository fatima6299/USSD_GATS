from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Menu(Base):
    __tablename__ = 'menu'
    
    id = Column(Integer, primary_key=True)
    jour = Column(String, nullable=False)  # monday, tuesday, etc.
    plat = Column(String, nullable=False)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class Commande(Base):
    __tablename__ = 'commandes'
    
    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
    plat = Column(String, nullable=False)
    statut = Column(String, default='active')  # 'active' ou 'annulee'
    date_commande = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///commandes.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)

# Créer la base de données si elle n'existe pas
Base.metadata.create_all(engine, checkfirst=True)

# Mise à jour des commandes existantes pour ajouter le statut par défaut
session = Session()
for commande in session.query(Commande).filter(Commande.statut.is_(None)).all():
    commande.statut = 'active'
session.commit()
session.close()
