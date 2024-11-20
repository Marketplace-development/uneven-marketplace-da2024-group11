from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Table
class User(db.Model):
    __tablename__ = 'User'
    UserId = db.Column(db.BigInteger, primary_key=True, autoincrement=True, unique=True)
    userName = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    Address = db.Column(db.String, nullable=True)
    Postal_code = db.Column(db.Integer, nullable=True)
    City = db.Column(db.String, nullable=True)
    Phone_number = db.Column(db.Numeric, nullable=True)

# Customer Table
class Customer(db.Model):
    __tablename__ = 'Customer'
    CustomerID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    TransactionID = db.Column(db.BigInteger, db.ForeignKey('Transaction.TransactionID'), nullable=True)
    premium = db.Column(db.Boolean, nullable=False, default=False)
    
    # Foreign key relationship
    user = db.relationship('User', backref=db.backref('customers', lazy=True))
    transaction = db.relationship('Transaction', backref=db.backref('customers', lazy=True))

# Provider Table
class Provider(db.Model):
    __tablename__ = 'Provider'
    ProviderID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    TransactionID = db.Column(db.BigInteger, db.ForeignKey('Transaction.TransactionID'), nullable=True)
    Premium_Provider = db.Column(db.Boolean, nullable=True, default=False)

    # Foreign key relationship
    user = db.relationship('User', backref=db.backref('providers', lazy=True))
    transaction = db.relationship('Transaction', backref=db.backref('providers', lazy=True))

# Listing Table
class Listing(db.Model):
    __tablename__ = 'Listing'
    ListingID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    NameTool = db.Column(db.String, nullable=True)
    Brand = db.Column(db.String, nullable=True)
    Condition = db.Column(db.String, nullable=True)
    DifficultyLevel = db.Column(db.String, nullable=True)
    BatteryIncluded = db.Column(db.Boolean, nullable=True)
    FuelType = db.Column(db.String, nullable=True)
    Power = db.Column(db.String, nullable=True)
    Dimensions = db.Column(db.String, nullable=True)
    SafetyRequirements = db.Column(db.String, nullable=True)
    ProductCode = db.Column(db.BigInteger, nullable=True)
    PriceSetByProvider = db.Column(db.Numeric, nullable=True)
    Availability = db.Column(db.Boolean, nullable=True)
    ProviderID = db.Column(db.BigInteger, db.ForeignKey('Provider.ProviderID'), nullable=True)

    # Foreign key relationship
    provider = db.relationship('Provider', backref=db.backref('listings', lazy=True))

# Transaction Table
class Transaction(db.Model):
    __tablename__ = 'Transaction'
    TransactionID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    Status = db.Column(db.String, nullable=True)
    commissionFee = db.Column(db.String, nullable=True)
    bookedQuantity = db.Column(db.BigInteger, nullable=True)
    ListingID = db.Column(db.BigInteger, db.ForeignKey('Listing.ListingID'), nullable=True)
    Date = db.Column(db.DateTime(timezone=True), nullable=True)

    # Foreign key relationship
    listing = db.relationship('Listing', backref=db.backref('transactions', lazy=True))

# Review Table
class Review(db.Model):
    __tablename__ = 'Review'
    ReviewID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    CustomerID = db.Column(db.BigInteger, db.ForeignKey('Customer.CustomerID'), nullable=True)
    ProviderID = db.Column(db.BigInteger, db.ForeignKey('Provider.ProviderID'), nullable=True)
    Rating = db.Column(db.SmallInteger, nullable=True)
    Comment = db.Column(db.String, nullable=True)
    Date = db.Column(db.DateTime(timezone=True), nullable=True)

    # Foreign key relationship
    customer = db.relationship('Customer', backref=db.backref('reviews', lazy=True))
    provider = db.relationship('Provider', backref=db.backref('reviews', lazy=True))
