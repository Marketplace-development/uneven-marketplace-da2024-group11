from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    listings = db.relationship('Listing', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Listing {self.listing_name}, ${self.price}>'
    



class Customer(db.Model):
    __tablename__ = "Customer"
    
    CustomerID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    TransactionID = db.Column(db.BigInteger, db.ForeignKey("Transaction.TransactionID"), nullable=True)
    premium = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationships (optioneel)
    user = db.relationship("User", backref="customer", uselist=False, foreign_keys=[CustomerID])
    transaction = db.relationship("Transaction", backref="customer", foreign_keys=[TransactionID])


class Listing(db.Model):
    __tablename__ = "Listing"
    
    ListingID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    NameTool = db.Column(db.Text, nullable=True)
    Brand = db.Column(db.Text, nullable=True)
    Condition = db.Column(db.Text, nullable=True)
    DifficultyLevel = db.Column(db.Text, nullable=True)
    BatteryIncluded = db.Column(db.Boolean, nullable=True)
    FuelType = db.Column(db.Text, nullable=True)
    Power = db.Column(db.Text, nullable=True)
    Dimensions = db.Column(db.Text, nullable=True)
    SafetyRequirements = db.Column(db.Text, nullable=True)
    ProductCode = db.Column(db.BigInteger, nullable=True)
    PriceSetByProvider = db.Column(db.Numeric, nullable=True)
    Availability = db.Column(db.Boolean, nullable=True)
    ProviderID = db.Column(db.BigInteger, db.ForeignKey("Provider.ProviderID"), nullable=True)
    
    # Relationships (optioneel)
    provider = db.relationship("Provider", backref="listings", foreign_keys=[ProviderID])


class Provider(db.Model):
    __tablename__ = "Provider"
    
    ProviderID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    TransactionID = db.Column(db.BigInteger, db.ForeignKey("Transaction.TransactionID"), nullable=True)
    PremiumProvider = db.Column(db.Boolean, nullable=True, default=False)
    
    # Relationships (optioneel)
    user = db.relationship("User", backref="provider", uselist=False, foreign_keys=[ProviderID])
    transaction = db.relationship("Transaction", backref="provider", foreign_keys=[TransactionID])
