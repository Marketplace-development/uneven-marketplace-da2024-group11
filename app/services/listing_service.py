from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models import Listing, Review

def search_and_filter_listings(session: Session, filters: dict, sort_by: str = None, page: int = 1, page_size: int = 10):
    # Start with base query
    query = session.query(Listing)

    # Apply filters only if they are not empty
    if filters.get('name_tool'):
        query = query.filter(Listing.name_tool.ilike(f"%{filters['name_tool']}%"))
    if filters.get('brand'):
        query = query.filter(Listing.brand.ilike(f"%{filters['brand']}%"))
    if filters.get('condition'):
        query = query.filter(Listing.condition == filters['condition'])
    if filters.get('battery_included') is not None:
        query = query.filter(Listing.battery_included == filters['battery_included'])
    if filters.get('price_min'):
        try:
            query = query.filter(Listing.price_set_by_provider >= float(filters['price_min']))
        except ValueError:
            pass
    if filters.get('price_max'):
        try:
            query = query.filter(Listing.price_set_by_provider <= float(filters['price_max']))
        except ValueError:
            pass
    if filters.get('availability') is not None:
        query = query.filter(Listing.availability == filters['availability'])

    # Sorteer opties
    if sort_by:
        if 'rating' in sort_by:
            # Voor rating hebben we join en group_by nodig
            query = query.outerjoin(Review, Review.listing_id == Listing.listing_id).group_by(Listing.listing_id)

        if sort_by == 'price_asc':
            query = query.order_by(Listing.price_set_by_provider.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Listing.price_set_by_provider.desc())
        elif sort_by == 'rating_asc':
            # Coalesce NULL naar 0 voor oplopende sortering
            query = query.order_by(func.coalesce(func.avg(Review.rating), 0).asc())
        elif sort_by == 'rating_desc':
            # Coalesce NULL naar 0 voor aflopende sortering
            query = query.order_by(func.coalesce(func.avg(Review.rating), 0).desc())
        elif sort_by == 'date_asc':
            # Indien er een created_at kolom is, gebruik dan date_asc = Listing.created_at.asc()
            query = query.order_by(Listing.listing_id.asc())
        elif sort_by == 'date_desc':
            # Indien er een created_at kolom is, gebruik dan date_desc = Listing.created_at.desc()
            query = query.order_by(Listing.listing_id.desc())

    # Pagination (optioneel)
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    listings = query.all()
    return listings
