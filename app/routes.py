from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import db, User, Listing, Transaction, Customer, Provider, Review
from app.services.popularity import calculate_popularity
from app.services.pricing import dynamic_pricing_advanced
from app.services.search import search_and_filter
from app.services.recommendation import recommend_tools
from datetime import datetime
from decimal import Decimal

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'phone_number' in session:
        user = User.query.filter_by(phone_number=session['phone_number']).first_or_404()
        listings = Listing.query.filter_by(provider_id=user.phone_number).all()
        transactions = Transaction.query.filter_by(customer_phone=user.phone_number).all()
        return render_template('index.html', username=user.username, listings=listings, transactions=transactions)
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')

        # Validatie van het telefoonnummer
        if not phone_number:
            flash("Phone number is required.", "error")
            return redirect(url_for('main.login'))

        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            flash("Invalid phone number.", "error")
            return redirect(url_for('main.login'))

        session['phone_number'] = user.phone_number
        return redirect(url_for('main.index'))

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        username = request.form.get('username')
        address = request.form.get('address')
        postal_code = request.form.get('postal_code')
        city = request.form.get('city')
        email = request.form.get('email')

        # Validatie
        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if not phone_number:
            errors.append("Phone number is required.")
        if not postal_code or not postal_code.isdigit():
            errors.append("Postal code is invalid.")
        if errors:
            return render_template('register.html', errors=errors)

        # Controleer of de gebruiker al bestaat op basis van e-mailadres of telefoonnummer
        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash("An account with this email already exists.", "error")
            return redirect(url_for('main.register'))

        existing_user_by_phone = User.query.filter_by(phone_number=phone_number).first()
        if existing_user_by_phone:
            flash("An account with this phone number already exists.", "error")
            return redirect(url_for('main.register'))

        # Voeg de gebruiker toe aan de database
        new_user = User(
            phone_number=phone_number,
            username=username,
            address=address,
            postal_code=int(postal_code),
            city=city,
            email=email,
        )
        db.session.add(new_user)
        db.session.commit()

        # Bewaar de gebruiker in de sessie
        session['phone_number'] = new_user.phone_number
        return redirect(url_for('main.index'))

    return render_template('register.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@main.route('/add-listing', methods=['GET', 'POST'])
def add_listing():
    if 'phone_number' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        # Haal gegevens op uit het formulier
        listing_name = request.form.get('listing_name')
        brand = request.form.get('brand')
        condition = request.form.get('condition')
        battery_included = request.form.get('battery_included') == 'True'  # Boolean check
        product_code = request.form.get('product_code')
        price = request.form.get('price')
        availability = request.form.get('availability') == 'True'  # Boolean check
        provider_id = session['phone_number']

        # Validatie
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
            print(errors)  # Debug
            return render_template('add_listing.html', errors=errors)

        # Maak een nieuwe Listing aan
        new_listing = Listing(
            name_tool=listing_name,
            brand=brand,
            condition=condition,
            battery_included=battery_included,
            product_code=product_code,
            price_set_by_provider=price,
            availability=availability,
            provider_id=provider_id
        )
        
        try:
            db.session.add(new_listing)
            db.session.commit()
            return redirect(url_for('main.listings'))
        except Exception as e:
            db.session.rollback()
            print(f"Fout bij het toevoegen van de listing: {e}")
            errors.append("Er is een fout opgetreden bij het toevoegen van de listing.")
            return render_template('add_listing.html', errors=errors)

    return render_template('add_listing.html')

@main.route('/listings')
def listings():
    all_listings = Listing.query.filter_by(availability=True).all()
    return render_template('listings.html', listings=all_listings)

@main.route('/buy-listing/<int:listing_id>', methods=['POST'])
def buy_listing(listing_id):
    if 'phone_number' not in session:
        flash("You need to be logged in to buy a tool.", "error")
        return redirect(url_for('main.login'))

    # Fetch the listing
    listing = Listing.query.get_or_404(listing_id)

    # Check if the user is trying to buy their own product
    if listing.provider_id == session['phone_number']:
        flash("You cannot buy your own product.", "error")
        return redirect(url_for('main.listings'))

    if not listing.availability:
        flash("This tool is not available for purchase.", "error")
        return redirect(url_for('main.listings'))

    # Ensure customer exists in the database
    customer_phone = session['phone_number']
    customer = Customer.query.filter_by(phone_c=customer_phone).first()
    if not customer:
        new_customer = Customer(phone_c=customer_phone, premium=False)
        db.session.add(new_customer)
        db.session.commit()
        customer = new_customer

    # Calculate the commission fee using Decimal
    commission_fee = listing.price_set_by_provider * Decimal('0.05')

    # Create a new transaction
    new_transaction = Transaction(
        listing_id=listing.listing_id,
        provider_id=listing.provider_id,
        customer_phone=customer.phone_c,
        commission_fee=commission_fee,
        date=datetime.now()
    )

    # Mark the listing as unavailable
    listing.availability = False

    # Commit the transaction
    try:
        db.session.add(new_transaction)
        db.session.commit()
        flash("You have successfully purchased this tool!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error during transaction: {e}")
        flash("There was an error processing your purchase.", "error")
        return redirect(url_for('main.listings'))

    return redirect(url_for('main.index'))



@main.route('/your-transactions')
def your_transactions():
    if 'phone_number' not in session:
        return redirect(url_for('main.login'))

    customer_phone = session['phone_number']
    transactions = Transaction.query.filter_by(customer_phone=customer_phone).all()
    return render_template('your_transactions.html', transactions=transactions)

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
            flash("Search term is required.", "error")
            return redirect(url_for('main.search'))

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

    user_id = session['phone_number']
    recommendations = recommend_tools(db.session, user_id)
    return render_template('recommendations.html', recommendations=recommendations)


@main.route('/profile')
def profile():
    if 'phone_number' not in session:
        return redirect(url_for('main.login'))

    user = User.query.filter_by(phone_number=session['phone_number']).first_or_404()
    transactions = Transaction.query.filter_by(customer_phone=user.phone_number).all()

    # Fetch reviews if the user is also a provider
    reviews = None
    if hasattr(user, 'provider'):
        reviews = user.provider.reviews

    return render_template('profile.html', user=user, transactions=transactions, reviews=reviews)




@main.route('/return-rented-tool/<int:listing_id>', methods=['POST'])
def make_available_again(listing_id):
    if 'phone_number' not in session:
        flash("You need to be logged in to return a rented tool.", "error")
        return redirect(url_for('main.login'))

    # Get the listing being returned
    listing = Listing.query.get_or_404(listing_id)

    # Ensure the user is the one who rented the tool
    customer_phone = session['phone_number']
    transaction = Transaction.query.filter_by(listing_id=listing.listing_id, customer_phone=customer_phone).first()
    
    if not transaction:
        flash("You are not authorized to return this tool.", "error")
        return redirect(url_for('main.index'))

    # Mark the listing as available again
    listing.availability = True

    # Optionally, remove or update the transaction if needed
    

    try:
        db.session.commit()
        flash("You have successfully returned the tool!", "success")
    except Exception as e:
        db.session.rollback()
        flash("There was an error returning the tool.", "error")

    return redirect(url_for('main.index'))

@main.route('/write-review/<int:provider_id>', methods=['GET', 'POST'])
def write_review(provider_id):
    if 'phone_number' not in session:
        flash("You need to log in to write a review.", "error")
        return redirect(url_for('main.login'))

    provider = Provider.query.get_or_404(provider_id)

    # Ensure the user has completed a transaction with this provider
    transaction = Transaction.query.filter_by(
        provider_id=provider_id,
        customer_phone=session['phone_number']
    ).first()

    if not transaction:
        flash("You cannot review a provider without a completed transaction.", "error")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        # Validate rating
        if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            flash("Rating must be a number between 1 and 5.", "error")
            return render_template('write_review.html', provider=provider)

        # Create a new review
        new_review = Review(
            customer_id=session['phone_number'],
            provider_id=provider_id,
            rating=int(rating),
            comment=comment,
            date=datetime.now()
        )

        try:
            db.session.add(new_review)
            db.session.commit()
            flash("Thank you for your review!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while submitting your review.", "error")
            print(f"Error: {e}")

        return redirect(url_for('main.profile'))

    return render_template('write_review.html', provider=provider)
@main.context_processor
def inject_datetime():
    return {'datetime': datetime}


