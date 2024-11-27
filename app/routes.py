from flask import Blueprint, request, redirect, url_for, render_template, session
from app.models import db, User, Listing
from app.services.popularity import calculate_popularity
from app.services.pricing import dynamic_pricing_advanced
from app.services.search import search_and_filter
from app.services.recommendation import recommend_tools

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get_or_404(session['user_id'])
        listings = Listing.query.filter_by(ProviderID=user.UserId).all()  # Pas de kolomnaam aan je database aan
        return render_template('index.html', username=user.userName, listings=listings)
    return render_template('index.html', username=None)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Haal alle ingevoerde gegevens op uit het formulier
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')
        postal_code = request.form.get('postal_code')
        city = request.form.get('city')
        phone_number = request.form.get('phone_number')

        # Controleer of de gebruiker al bestaat
        if User.query.filter_by(userName=username).first() is None:
            # Maak een nieuwe gebruiker aan met alle velden
            new_user = User(
                userName=username,
                email=email,
                Address=address,
                Postal_code=postal_code,
                City=city,
                Phone_number=phone_number
            )
            db.session.add(new_user)
            db.session.commit()

            # Sla de gebruiker op in de sessie en stuur door naar de homepage
            session['user_id'] = new_user.UserId
            return redirect(url_for('main.index'))
        else:
            return 'Username already registered'

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(userName=username).first()
        if user:
            session['user_id'] = user.UserId
            return redirect(url_for('main.index'))
        return 'User not found'
    return render_template('login.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main.route('/add-listing', methods=['GET', 'POST'])
def add_listing():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        listing_name = request.form['listing_name']
        price = float(request.form['price'])
        new_listing = Listing(NameTool=listing_name, PriceSetByProvider=price, ProviderID=session['user_id'])
        db.session.add(new_listing)
        db.session.commit()
        return redirect(url_for('main.listings'))

    return render_template('add_listing.html')

@main.route('/listings')
def listings():
    all_listings = Listing.query.all()
    return render_template('listings.html', listings=all_listings)

@main.route('/popular-listings', methods=['GET'])
def popular_listings():
    results = calculate_popularity(db.session)
    listings = [{
        "ListingID": row[0],
        "NameTool": row[1],
        "Bookings": row[2],
        "AverageRating": row[3],
        "PopularityScore": row[4]
    } for row in results]
    return render_template('popular_listings.html', listings=listings)

@main.route('/pricing', methods=['GET'])
def pricing():
    pricing_data = dynamic_pricing_advanced(db.session)
    return render_template('pricing.html', pricing_data=pricing_data)

@main.route('/listing/<int:id>')
def listing_detail(id):
    listing = Listing.query.get_or_404(id)  # Gebruik get_or_404 voor betere foutafhandeling
    return render_template('listing_detail.html', listing=listing)

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search_term', None)
        price_range = (
            float(request.form.get('min_price', 0)),
            float(request.form.get('max_price', float('inf')))
        ) if request.form.get('min_price') or request.form.get('max_price') else None

        filters = {
            "Brand": request.form.get('brand', None),
            "FuelType": request.form.get('fuel_type', None),
            "PriceRange": price_range,
            "Availability": request.form.get('availability', 'false') == 'true'
        }

        filters = {k: v for k, v in filters.items() if v is not None}

        results = search_and_filter(db.session, search_term, filters)
        return render_template('search_results.html', results=results)

    return render_template('search.html')

@main.route('/recommendations', methods=['GET'])
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    recommendations = recommend_tools(db.session, user_id)

    return render_template('recommendations.html', recommendations=recommendations)