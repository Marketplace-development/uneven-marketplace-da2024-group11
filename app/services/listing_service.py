from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models import Listing, Review  # Gebruik een absolute import die verwijst naar de app-module

def search_and_filter_listings(session: Session, filters: dict, sort_by: str = None, ascending: bool = True, page: int = 1, page_size: int = 10):
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

    # Sorting
    if sort_by == 'price':
        if ascending:
            query = query.order_by(Listing.price_set_by_provider.asc())
        else:
            query = query.order_by(Listing.price_set_by_provider.desc())
    elif sort_by == 'rating':
        # Join Review and calculate average rating
        query = query.outerjoin(Review, Review.listing_id == Listing.listing_id)
        query = query.group_by(Listing.listing_id)
        # Sort highest rating first (descending by default)
        if not ascending:
            query = query.order_by(func.avg(Review.rating).desc())
        else:
            query = query.order_by(func.avg(Review.rating).asc())
    elif sort_by == 'date':
        if ascending:
            query = query.order_by(Listing.listing_id.asc())  # Gebruik een 'created_at' kolom als beschikbaar
        else:
            query = query.order_by(Listing.listing_id.desc())

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    listings = query.all()
    return listings
