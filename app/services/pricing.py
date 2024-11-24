from sqlalchemy import func, case
from datetime import datetime, timezone, timedelta
from app.models import Listing, Transaction

def dynamic_pricing_advanced(session, base_min_price=10, base_max_price=500, max_demand_multiplier=2):
    # Definieer de tijdsperiode voor recente transacties (bijv. laatste 30 dagen)
    recent_period = datetime.now(timezone.utc) - timedelta(days=30)

    # Bereken de recente vraag per listing
    recent_demand_subquery = session.query(
        Transaction.ListingID,
        func.count(Transaction.TransactionID).label('recent_demand')
    ).filter(
        Transaction.Date >= recent_period
    ).group_by(
        Transaction.ListingID
    ).subquery()

    # Bereken de totale en gemiddelde recente vraag
    total_recent_demand = session.query(
        func.sum(recent_demand_subquery.c.recent_demand)
    ).scalar() or 1  # Vermijd deling door nul

    average_recent_demand = total_recent_demand / (session.query(Listing).count() or 1)

    # Bereken de gemiddelde vraag voor normalisatie (uit Algoritme 1)
    avg_demand_subquery = session.query(
        func.avg(func.count(Transaction.TransactionID)).label("avg_demand")
    ).join(Transaction, Listing.ListingID == Transaction.ListingID).scalar()

    # Hoofdquery voor prijsberekening
    pricing_query = session.query(
        Listing.ListingID,
        Listing.NameTool,
        Listing.PriceSetByProvider,
        func.coalesce(recent_demand_subquery.c.recent_demand, 0).label('recent_demand'),
        func.count(Transaction.TransactionID).label('total_demand'),
        # Bereken de vraagvermenigvuldiger (combinatie van recente en totale vraag)
        (
            1 + func.least(
                max_demand_multiplier,
                (
                    (func.coalesce(recent_demand_subquery.c.recent_demand, 0) - average_recent_demand) / (average_recent_demand or 1) +
                    func.count(Transaction.TransactionID) / (avg_demand_subquery or 1)
                ) / 2  # Gemiddelde van recente en totale vraag
            )
        ).label('demand_multiplier'),
        # Voorgestelde prijsberekening
        case(
            [
                (Listing.Availability == True,
                 func.least(
                     func.greatest(
                         base_min_price,
                         (
                             Listing.PriceSetByProvider * (
                                 1 + func.least(
                                     max_demand_multiplier,
                                     (
                                         (func.coalesce(recent_demand_subquery.c.recent_demand, 0) - average_recent_demand) / (average_recent_demand or 1) +
                                         func.count(Transaction.TransactionID) / (avg_demand_subquery or 1)
                                     ) / 2
                                 )
                             )
                         )
                     ),
                     base_max_price
                 )
                )
            ],
            else_=None
        ).label("suggested_price")
    ).outerjoin(
        recent_demand_subquery, Listing.ListingID == recent_demand_subquery.c.ListingID
    ).outerjoin(
        Transaction, Listing.ListingID == Transaction.ListingID
    ).group_by(
        Listing.ListingID, Listing.NameTool, Listing.PriceSetByProvider, Listing.Availability, recent_demand_subquery.c.recent_demand
    )

    # Query uitvoeren en resultaten ophalen
    results = pricing_query.all()

    # Voeg seizoensinvloeden of trends toe
    enhanced_results = []
    for row in results:
        season_adjustment = calculate_season_adjustment(row[1])  # Stel dit als een functie in
        adjusted_price = row[6] * season_adjustment if row[6] else None
        enhanced_results.append({
            "ListingID": row[0],
            "NameTool": row[1],
            "BasePrice": row[2],
            "RecentDemand": row[3],
            "TotalDemand": row[4],
            "SuggestedPrice": adjusted_price
        })

    return enhanced_results


def calculate_season_adjustment(tool_name):
    # Voorbeeld van seizoensinvloeden
    if "snow" in tool_name.lower():
        return 1.2  # Prijsstijging in de winter
    elif "lawnmower" in tool_name.lower():
        return 1.3  # Prijsstijging in de lente/zomer
    return 1.0  # Geen seizoensinvloed
