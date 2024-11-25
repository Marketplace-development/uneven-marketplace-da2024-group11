from sqlalchemy import func
from app.models import Transaction, Listing

def recommend_tools(session, user_id):
    """
    Aanbevelingen genereren voor een specifieke gebruiker.
    :param session: Database sessie
    :param user_id: ID van de gebruiker
    :return: Lijst van aanbevolen tools
    """
    # Stap 1: Vind tools die de gebruiker eerder heeft gehuurd
    user_transactions = session.query(Transaction.ListingID).filter(
        Transaction.CustomerID == user_id
    ).subquery()

    # Stap 2: Zoek tools met vergelijkbare eigenschappen
    recommendations = session.query(
        Listing.ListingID,
        Listing.NameTool
    ).filter(
        ~Listing.ListingID.in_(user_transactions),  # Sluit gehuurde tools uit
        Listing.Brand.in_(
            session.query(Listing.Brand).filter(Listing.ListingID.in_(user_transactions))
        ),
        Listing.FuelType.in_(
            session.query(Listing.FuelType).filter(Listing.ListingID.in_(user_transactions))
        )
    ).all()

    return recommendations
