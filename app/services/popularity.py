from sqlalchemy import func
from app.models import Listing, Review

def calculate_popularity(session):
    # Bereken de gemiddelde beoordeling per tool (indien aanwezig)
    avg_rating = session.query(
        Review.listing_id,
        func.avg(Review.rating).label('gemiddelde_beoordeling')
    ).group_by(Review.listing_id).subquery()

    # Voeg de gemiddelde beoordeling toe aan de listings en sorteer aflopend op beoordeling
    popularity_results = session.query(
        Listing.listing_id,
        Listing.name_tool,
        func.coalesce(avg_rating.c.gemiddelde_beoordeling, 0).label('gemiddelde_beoordeling')
    ).outerjoin(
        avg_rating, Listing.listing_id == avg_rating.c.listing_id
    ).order_by(func.coalesce(avg_rating.c.gemiddelde_beoordeling, 0).desc()).all()

    return popularity_results
