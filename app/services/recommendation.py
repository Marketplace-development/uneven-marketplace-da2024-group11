from app.models import Listing, Transaction, Review
from sqlalchemy.sql import func

def recommend_tools(session, listing_id, limit=5):
    """
    Genereert een lijst van aanbevolen tools op basis van een specifieke tool.
    :param session: Database sessie.
    :param listing_id: ID van de huidige tool.
    :param limit: Aantal aanbevelingen.
    :return: Lijst met aanbevolen tools.
    """
    # Huidige tool ophalen
    current_listing = session.query(Listing).get(listing_id)

    # Stap 1: Aanbevelingen op basis van hetzelfde merk
    same_brand_tools = session.query(Listing).filter(
        Listing.brand == current_listing.brand,
        Listing.availability == True,
        Listing.listing_id != listing_id
    ).limit(limit).all()

    # Stap 2: Vul aan met populaire tools (met beoordelingen)
    if len(same_brand_tools) < limit:
        additional_tools = session.query(
            Listing, func.avg(Review.rating).label("average_rating")
        ).join(Review, Review.listing_id == Listing.listing_id) \
        .filter(Listing.availability == True) \
        .group_by(
            Listing.listing_id,
            Listing.name_tool,
            Listing.brand,
            Listing.condition,
            Listing.battery_included,
            Listing.product_code,
            Listing.price_set_by_provider,
            Listing.availability,
            Listing.provider_id
        ) \
        .order_by(func.avg(Review.rating).desc()) \
        .limit(limit - len(same_brand_tools)) \
        .all()

        # Voeg de tools toe aan de lijst
        same_brand_tools.extend([tool for tool, _ in additional_tools])

    return same_brand_tools