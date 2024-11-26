from sqlalchemy import func
from app.models import Listing

def search_and_filter(session, search_term=None, filters=None):
    query = session.query(Listing)

    # Zoekterm filteren op naam, merk of brandstoftype
    if search_term:
        query = query.filter(
            (Listing.NameTool.ilike(f"%{search_term}%")) |
            (Listing.Brand.ilike(f"%{search_term}%")) |
            (Listing.FuelType.ilike(f"%{search_term}%"))
        )

    # Optionele filters toepassen
    if filters:
        if "Brand" in filters:
            query = query.filter(Listing.Brand == filters["Brand"])
        if "FuelType" in filters:
            query = query.filter(Listing.FuelType == filters["FuelType"])
        if "PriceRange" in filters:
            min_price, max_price = filters["PriceRange"]
            query = query.filter(
                Listing.PriceSetByProvider >= min_price,
                Listing.PriceSetByProvider <= max_price
            )
        if "Availability" in filters and filters["Availability"]:
            query = query.filter(Listing.Availability == True)

    # Sorteren op beschikbaarheid en prijs (ascending)
    query = query.order_by(
        func.desc(Listing.Availability),
        Listing.PriceSetByProvider.asc()
    )

    return query.all()
