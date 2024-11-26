from sqlalchemy import func
from sqlalchemy.sql.functions import coalesce
from app.models import Listing, Transaction, Review

def calculate_popularity(session):
    popularity_query = session.query(
        Listing.ListingID,
        Listing.NameTool,
        coalesce(func.count(Transaction.TransactionID), 0).label("bookings"),
        coalesce(func.avg(Review.Rating), 0).label("avg_rating"),
        (
            coalesce(func.count(Transaction.TransactionID), 0) * 0.7 +
            coalesce(func.avg(Review.Rating), 0) * 0.3
        ).label("popularity_score")
    ).outerjoin(Transaction, Listing.ListingID == Transaction.ListingID) \
     .outerjoin(Review, Listing.ProviderID == Review.ProviderID) \
     .group_by(Listing.ListingID, Listing.NameTool) \
     .order_by(func.desc("popularity_score"))

    return popularity_query.all()
