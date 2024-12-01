from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'
    phone_number = db.Column('Phone_number', db.BigInteger, primary_key=True, nullable=False, unique=True)
    username = db.Column('UserName', db.Text, nullable=False)
    address = db.Column('Address', db.Text, nullable=False)
    postal_code = db.Column('Postal_code', db.Integer, nullable=False)
    city = db.Column('City', db.Text, nullable=False)
    email = db.Column('Email', db.Text, nullable=False, unique=True)

class Customer(db.Model):
    __tablename__ = 'Customer'
    phone_c = db.Column('PhoneC', db.BigInteger, db.ForeignKey('User.Phone_number'), primary_key=True, autoincrement=True)
    premium = db.Column(db.Boolean, nullable=False, default=False)

class Provider(db.Model):
    __tablename__ = 'Provider'
    providerp = db.Column(db.BigInteger, db.ForeignKey('User.Phone_number'), primary_key=True, autoincrement=True)
    premium_provider = db.Column('Premium Provider', db.Boolean, nullable=True, default=False)
    listings = db.relationship('Listing', back_populates='provider')

class Listing(db.Model):
    __tablename__ = 'Listing'
    listing_id = db.Column('ListingID', db.BigInteger, primary_key=True, autoincrement=True)
    name_tool = db.Column('NameTool', db.Text, nullable=False)
    brand = db.Column('Brand', db.Text, nullable=True)
    condition = db.Column('Condition', db.Text, nullable=True)
    battery_included = db.Column('BatteryIncluded', db.Boolean, nullable=True)
    product_code = db.Column('ProductCode', db.BigInteger, nullable=True)
    price_set_by_provider = db.Column('PriceSetByProvider', db.Numeric, nullable=True)
    availability = db.Column('Availability', db.Boolean, nullable=True)
    provider_id = db.Column('ProviderID', db.BigInteger, db.ForeignKey('Provider.providerp'), nullable=False)
    provider = db.relationship('Provider', back_populates='listings')
    reviews = db.relationship('Review', back_populates='listing')
    transactions = db.relationship('Transaction', back_populates='listing')

class Transaction(db.Model):
    __tablename__ = 'Transactie'
    listing_id = db.Column('ListingID', db.BigInteger, db.ForeignKey('Listing.ListingID'), primary_key=True)
    provider_id = db.Column('ProviderP', db.BigInteger, db.ForeignKey('Provider.providerp'), primary_key=True)
    customer_phone = db.Column('PhoneC', db.BigInteger, db.ForeignKey('Customer.PhoneC'), primary_key=True)
    commission_fee = db.Column('Commission fee', db.Float, nullable=True)
    date = db.Column('Date', db.DateTime(timezone=True), nullable=False, server_default=func.now(), primary_key=True)

    listing = db.relationship('Listing', back_populates='transactions')
    customer = db.relationship('Customer')


class Review(db.Model):
    __tablename__ = 'review'
    review_id = db.Column('ReviewID', db.BigInteger, primary_key=True, autoincrement=True)
    customer_id = db.Column('CustomerID', db.BigInteger, db.ForeignKey('Customer.PhoneC'), nullable=False)
    listing_id = db.Column('Listing_id', db.BigInteger, db.ForeignKey('Listing.ListingID'), nullable=False)
    rating = db.Column('Rating', db.Integer, nullable=False)
    comment = db.Column('Comment', db.Text, nullable=True)
    date = db.Column('date', db.Date, nullable=False, default=datetime.utcnow)

    customer = db.relationship('Customer', backref='reviews')
    listing = db.relationship('Listing', back_populates='reviews')