from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import db, User, Listing, Transaction, Customer, Provider, Review
from app.services.popularity import calculate_popularity
from app.services.recommendation import recommend_tools
from datetime import datetime
from decimal import Decimal
from flask import jsonify
from app.services.listing_service import search_and_filter_listings
from sqlalchemy.orm import Session

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'phone_number' in session:
        user = User.query.filter_by(phone_number=session['phone_number']).first_or_404()
        listings = Listing.query.filter_by(provider_id=user.phone_number, availability=True).all()
        transactions = Transaction.query.filter_by(customer_phone=user.phone_number).all()

        # Voeg hier de code toe om de top 3 populairste producten op te halen
        results = calculate_popularity(db.session)
        top_3_listings = results[:3]

        # Vorm de resultaten om in een lijst van dictionaries voor gemakkelijker gebruik in de template
        popular_listings = [{
            "ListingID": row.listing_id,
            "NameTool": row.name_tool,
            "AverageRating": row.gemiddelde_beoordeling,
        } for row in top_3_listings]

        return render_template('index.html', username=user.username, listings=listings, transactions=transactions, popular_listings=popular_listings)

    # Haal ook de top 3 populaire tools op wanneer de gebruiker niet ingelogd is
    results = calculate_popularity(db.session)
    top_3_listings = results[:3]

    popular_listings = [{
        "ListingID": row.listing_id,
        "NameTool": row.name_tool,
        "AverageRating": row.gemiddelde_beoordeling,
    } for row in top_3_listings]

    return render_template('index.html', popular_listings=popular_listings)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        if not phone_number:
            flash("Phone number is required.", "error")
            return redirect(url_for('main.login'))

        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            flash("Invalid phone number.", "error")
            return redirect(url_for('main.login'))

        session['phone_number'] = user.phone_number
        session['username'] = user.username
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

        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash("An account with this email already exists.", "error")
            return redirect(url_for('main.register'))

        existing_user_by_phone = User.query.filter_by(phone_number=phone_number).first()
        if existing_user_by_phone:
            flash("An account with this phone number already exists.", "error")
            return redirect(url_for('main.register'))

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
        # Haal gegevens uit het formulier
        listing_name = request.form.get('listing_name')  # Naam van de tool
        other_tool = request.form.get('other_tool')      # Alternatieve toolnaam
        brand = request.form.get('brand')               # Merk van de tool
        other_brand = request.form.get('other_brand')   # Alternatief merk
        condition = request.form.get('condition')       # Conditie van de tool
        battery_included = request.form.get('battery_included') == 'True'  # Accu inbegrepen
        product_code = request.form.get('product_code')  # Productcode
        price = request.form.get('price')               # Prijs ingesteld door provider
        availability = request.form.get('availability') == 'True'  # Beschikbaarheid
        photo_path = request.form.get('photo_path')     # Pad naar de foto
        provider_phone = session['phone_number']        # Huidige gebruiker als provider

        # Gebruik alternatieve invoer als "Other" is geselecteerd
        if listing_name == 'other':
            listing_name = other_tool
        if brand == 'Other':
            brand = other_brand

        # Validatie van invoer
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

        # Haal de provider op (of maak een nieuwe aan als deze niet bestaat)
        provider = Provider.query.filter_by(providerp=provider_phone).first()
        if not provider:
            provider = Provider(providerp=provider_phone, premium_provider=False)
            db.session.add(provider)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                errors.append("Failed to create provider. Please try again.")
                return render_template('add_listing.html', errors=errors)

        # Maak een nieuwe listing aan
        new_listing = Listing(
            name_tool=listing_name,
            brand=brand,
            condition=condition,
            battery_included=battery_included,
            product_code=product_code,
            price_set_by_provider=price,
            availability=availability,
            provider_id=provider.providerp,  # Verwijzing naar de provider
            photo_path=photo_path  # Optioneel fotopad
        )

        # Probeer de nieuwe listing op te slaan in de database
        try:
            db.session.add(new_listing)
            db.session.commit()
            flash("Listing added successfully!", "success")
            return redirect(url_for('main.index'))  # Verwijst naar de lijstpagina
        except Exception as e:
            db.session.rollback()
            flash("There was an error adding the listing.", "error")
            errors.append(str(e))  # Voeg foutdetails toe
            return render_template('add_listing.html', errors=errors)

    # Bij GET, toon het formulier
    return render_template('add_listing.html')


@main.route('/remove-listing/<int:listing_id>', methods=['POST'])
def remove_listing(listing_id):
    # Check if the user is logged in
    if 'phone_number' not in session:
        flash("You need to log in to perform this action.", "warning")
        return redirect(url_for('auth.login'))

    # Fetch the listing associated with the logged-in provider
    phone_number = session['phone_number']
    listing = Listing.query.filter_by(listing_id=listing_id, provider_id=phone_number).first()

    # If the listing does not exist or does not belong to the user
    if not listing:
        flash("Listing not found or you don't have permission to delete this listing.", "danger")
        return redirect(url_for('main.profile'))

    # Attempt to delete the listing
    try:
        db.session.delete(listing)
        db.session.commit()
        flash("Listing successfully removed.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while removing the listing. Please try again.", "danger")
        print("Error removing listing:", str(e))

    # Redirect to the profile page
    return redirect(url_for('main.profile'))



@main.route('/listing/<int:id>')
def listing_detail(id):
    # Haal de huidige tool op
    listing = Listing.query.get_or_404(id)
    
    # Genereer aanbevelingen voor tools
    recommended_tools = recommend_tools(db.session, listing_id=id)
    
    # Geef de huidige tool en aanbevelingen door aan de template
    return render_template('listing_detail.html', listing=listing, recommended_tools=recommended_tools)







@main.route('/popular-listings', methods=['GET'])
def popular_listings():
    # Roep de calculate_popularity functie aan vanuit de service laag
    results = calculate_popularity(db.session)

    # Vorm de resultaten om in een lijst van dictionaries voor gemakkelijker gebruik in de template
    listings = [{
        "ListingID": row.listing_id,
        "NameTool": row.name_tool,
        "AverageRating": row.gemiddelde_beoordeling,
        "Rank": index + 1  # Voeg een rangnummer toe
    } for index, row in enumerate(results)]

    # Render de HTML-template en geef de lijst van listings door
    return render_template('popular_listings.html', listings=listings)




@main.route('/listings')
def listings():
    all_listings = Listing.query.filter_by(availability=True).all()
    return render_template('listings.html', listings=all_listings)

@main.route('/listings/search', methods=['GET'])
def search_listings():
    filters = request.args.to_dict()  # Verzamelt filters vanuit URL parameters
    sort_by = request.args.get('sort_by', None)
    # ascending = request.args.get('ascending', 'true').lower() == 'true'  # Verwijder of uitcommentariëren
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 100))

    # Roep nu de functie aan zonder ascending
    results = search_and_filter_listings(db.session, filters, sort_by, page=page, page_size=page_size)

    return render_template('listings_search.html', results=results, page=page, page_size=page_size)


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
    # Ophalen van alle producten van de ingelogde gebruiker
    listings = Listing.query.filter_by(provider_id=user.phone_number).all()

    reviews = None
    if hasattr(user, 'provider'):
        reviews = user.provider.reviews

    return render_template('profile.html', user=user, username=user.username, listings=listings, transactions=transactions, reviews=reviews)





@main.route('/return-rented-tool/<int:listing_id>', methods=['POST'])
def make_available_again(listing_id):
    if 'phone_number' not in session:
        flash("You need to be logged in to return a rented tool.", "error")
        return redirect(url_for('main.login'))

    # Fetch the listing being returned
    listing = Listing.query.get_or_404(listing_id)

    # Ensure the user is authorized to return the tool
    customer_phone = session['phone_number']
    transaction = Transaction.query.filter_by(listing_id=listing.listing_id, customer_phone=customer_phone).first()

    if not transaction:
        flash("You are not authorized to return this tool.", "error")
        return redirect(url_for('main.index'))

    # Mark the listing as available again
    listing.availability = True

    try:
        db.session.commit()
        flash("The tool is now available again!", "success")
    except Exception as e:
        db.session.rollback()
        flash("There was an error making the tool available again.", "error")

    return redirect(url_for('main.profile'))



@main.route('/add-review/<int:listing_id>', methods=['GET', 'POST'])
def add_review(listing_id):
    if 'phone_number' not in session:
        flash("You need to be logged in to leave a review.", "error")
        return redirect(url_for('main.login'))

    listing = Listing.query.get_or_404(listing_id)
    customer_phone = session['phone_number']
    customer = Customer.query.filter_by(phone_c=customer_phone).first()
    if not customer:
        flash("Only customers can leave reviews.", "error")
        return redirect(url_for('main.listings'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        # Validate rating
        if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            flash("Rating must be a number between 1 and 5.", "error")
            return render_template('add_review.html', listing=listing)

        # Create new review
        new_review = Review(
            customer_id=customer.phone_c,
            listing_id=listing.listing_id,
            rating=int(rating),
            comment=comment,
            date=datetime.now()
        )

        try:
            db.session.add(new_review)
            db.session.commit()
            flash("Review added successfully!", "success")
            return redirect(url_for('main.listing_detail', id=listing.listing_id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while adding the review.", "error")

    return render_template('add_review.html', listing=listing)

@main.context_processor
def inject_globals():
    username = None
    if 'phone_number' in session:
        user = User.query.filter_by(phone_number=session['phone_number']).first()
        if user:
            username = user.username
    return {'username': username, 'datetime': datetime}

@main.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'phone_number' not in session:
        return redirect(url_for('main.login'))
    
    # Mock-up winkelwagen data (vervang dit met sessiegegevens of database-query)
    cart_items = session.get('cart', [])
    
    total_price = 0
    commission_fee = 0
    grand_total = 0
    
    # Bereken prijzen
    for item in cart_items:
        item['total_price'] = item['price_per_day'] * item['days']
        total_price += item['total_price']
    
    commission_fee = total_price * 0.05  # 5% commissie
    grand_total = total_price + commission_fee

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total_price=total_price,
        commission_fee=commission_fee,
        grand_total=grand_total
    )
@main.route('/add-to-cart/<int:listing_id>', methods=['POST'])
def add_to_cart(listing_id):
    if 'phone_number' not in session:
        return redirect(url_for('main.login'))

    # Haal de details van de tool op
    listing = Listing.query.get_or_404(listing_id)

    if not listing.availability:
        flash("This tool is currently unavailable.", "error")
        return redirect(url_for('main.listing_detail', id=listing_id))
    if listing.provider_id == session['phone_number']:
        flash("You cannot add your own tool to the cart.", "error")
        return redirect(url_for('main.listing_detail', id=listing_id))


    # Controleer of de winkelwagen al in de sessie bestaat
    if 'cart' not in session:
        session['cart'] = []

    # Voeg de tool toe aan de winkelwagen
    session['cart'].append({
        "id": listing.listing_id,
        "name": listing.name_tool,
        "price_per_day": float(listing.price_set_by_provider),
        "days": 1  # Standaard aantal dagen
    })
    session.modified = True

    flash(f"{listing.name_tool} has been added to your cart.", "success")
    return redirect(url_for('main.cart'))

@main.route('/remove-from-cart/<int:listing_id>', methods=['POST'])
def remove_from_cart(listing_id):
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['id'] != listing_id]
        session.modified = True
        flash("Product removed from your cart.", "success")
    else:
        flash("Cart is empty.", "error")
    return redirect(url_for('main.cart'))
@main.route('/confirm-order', methods=['POST'])
def confirm_order():
    if 'phone_number' not in session:
        flash("You need to be logged in to confirm your order.", "error")
        return redirect(url_for('main.login'))

    customer_phone = session['phone_number']
    cart = session.get('cart', [])

    # Fetch single listing_id if this request is for a single item
    listing_id = request.form.get('listing_id')

    # Check if this is a single-item request (like buy_listing)
    if listing_id:
        listing = Listing.query.get_or_404(listing_id)
        cart = [{
            "id": listing.listing_id,
            "name": listing.name_tool,
            "price_per_day": float(listing.price_set_by_provider),
            "days": 1  # Default rental period
        }]

    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for('main.cart'))

    customer = Customer.query.filter_by(phone_c=customer_phone).first()

    # Create customer if not exists
    if not customer:
        customer = Customer(phone_c=customer_phone, premium=False)
        db.session.add(customer)
        db.session.commit()

    for item in cart:
        # Fetch the listing being rented
        listing = Listing.query.get_or_404(item['id'])

        # Prevent users from renting their own tools
        if listing.provider_id == customer_phone:
            flash(f"You cannot rent your own tool: {listing.name_tool}.", "error")
            continue

        if not listing.availability:
            flash(f"{listing.name_tool} is no longer available.", "error")
            continue

        try:
            # Calculate commission fee
            price = Decimal(str(listing.price_set_by_provider))
            commission_fee = price * Decimal('0.05') * Decimal(item['days'])

            # Create transaction
            new_transaction = Transaction(
                listing_id=listing.listing_id,
                provider_id=listing.provider_id,
                customer_phone=customer.phone_c,
                commission_fee=float(commission_fee),
                date=datetime.now()
            )

            # Mark listing as unavailable
            listing.availability = False

            db.session.add(new_transaction)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred with {listing.name_tool}: {str(e)}", "error")
            print(f"Transaction Error: {e}")

    # Clear the cart after confirming the order
    if not listing_id:  # Clear the cart only if it's not a single-item request
        session['cart'] = []
        session.modified = True

    flash("Your order has been confirmed!", "success")
    return redirect(url_for('main.profile'))
