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
        listings = Listing.query.filter_by(ProviderID=user.Phone_number).all()  # Zorg ervoor dat 'ProviderID' correct is
        return render_template('index.html', username=user.UserName, listings=listings)
    return render_template('index.html', username=None)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Haal gegevens op uit het formulier
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')
        postal_code = request.form.get('postal_code')
        city = request.form.get('city')
        phone_number = request.form.get('phone_number')

        # Controleer of de gebruiker al bestaat
        existing_user = User.query.filter_by(userName=username).first()
        if existing_user:
            return 'Username already registered', 400

        # Maak een nieuwe gebruiker aan
        new_user = User(
            UserName=username,
            Email=email,
            Address=address,
            Postal_code=postal_code,
            City=city,
            Phone_number=phone_number
        )
        db.session.add(new_user)
        db.session.commit()

        # Sla de gebruiker op in de sessie
        session['phone_number'] = new_user.phone_number
        return redirect(url_for('main.index'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')

        user = User.query.filter_by(Phone_number=phone_number).first()
        if not user:
            return 'Invalid phone number', 404

        # Log de gebruiker in door de sessie bij te werken
        session['phone_number'] = user.Phone_number
        return redirect(url_for('main.index'))

    return render_template('login.html')


@main.route('/add-listing', methods=['GET', 'POST'])
def add_listing():
    if 'phone_number' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        # Haal gegevens op uit het formulier
        listing_name = request.form.get('listing_name')
        brand = request.form.get('brand')
        condition = request.form.get('condition')
        battery_included = request.form.get('battery_included') == 'on'
        product_code = request.form.get('product_code')
        price = request.form.get('price')
        availability = request.form.get('availability') == 'on'
        provider_id = session['user_id']

        # Validatie van inputs
        errors = []
        if not listing_name:
            errors.append("Listing name is required.")
        if not price:
            errors.append("Price is required.")
        else:
            try:
                price = float(price)
            except ValueError:
                errors.append("Invalid price format.")
        if product_code:
            try:
                product_code = int(product_code)
            except ValueError:
                errors.append("Invalid product code format.")

        if errors:
            return render_template('add_listing.html', errors=errors)

        # Maak een nieuwe Listing aan
        new_listing = Listing(
            NameTool=listing_name,
            Brand=brand,
            Condition=condition,
            BatteryIncluded=battery_included,
            ProductCode=product_code,
            PriceSetByProvider=price,
            Availability=availability,
            ProviderID=provider_id
        )
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
    listing = Listing.query.get_or_404(id)
    return render_template('listing_detail.html', listing=listing)


@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        if not search_term:
            return 'Search term is required.', 400

        price_range = (
            float(request.form.get('min_price', 0)),
            float(request.form.get('max_price', float('inf')))
        ) if request.form.get('min_price') or request.form.get('max_price') else None

        filters = {
            "Brand": request.form.get('brand'),
            "PriceRange": price_range,
            "Availability": request.form.get('availability', 'false') == 'true'
        }
        filters = {k: v for k, v in filters.items() if v}

        results = search_and_filter(db.session, search_term, filters)
        return render_template('search_results.html', results=results)

    return render_template('search.html')


@main.route('/recommendations', methods=['GET'])
def recommendations():
    if 'phone_number' not in session:
        return redirect(url_for('main.login'))

    user_id = session['uphone_number']
    recommendations = recommend_tools(db.session, user_id)
    return render_template('recommendations.html', recommendations=recommendations)
