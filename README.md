[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/YzI0i2Iu)

# Platform name: EasyTools

# Short description: 
Our platform is designed to provide a simple, effective way for people in cities to rent tools from one another. The idea is straightforward: individuals who own tools they no longer use regularly can offer them for rent, while those who need tools for short-term projects can access them without the cost and commitment of buying.

The platform addresses a common urban challenge. Many people own tools that are only used occasionally, yet these tools take up valuable storage space and represent a financial investment. At the same time, others might need a specific tool for a one-time job but find purchasing it impractical. By connecting these two groups, our platform promotes resource sharing and reduces unnecessary consumption.

How It Works
For Owners: People with unused tools can list them on the site, setting a rental price, availability, and conditions. This allows them to earn extra income while giving their tools a new purpose.
For Renters: Those who need tools can browse listings, compare options, and rent what they need for a specific period. This is a cost-effective and convenient way to access equipment without having to store or maintain it.
Why This Platform Matters
Urban living often comes with constraints such as limited space and high costs. Purchasing tools for occasional use can be expensive, while storing them can be a challenge. Our platform encourages a shift away from individual ownership toward shared access, helping to make life more convenient and sustainable for city dwellers.

Features and Benefits
Ease of Use: The platform is designed to be intuitive and accessible for everyone.
Safety and Trust: Secure payment options and user verification ensure a reliable experience.
Local Connections: Users can find tools available in their immediate area, reducing travel and encouraging community interaction.
A Step Toward Sustainability
By facilitating tool sharing, our platform helps reduce waste, minimize overproduction, and promote the efficient use of resources. It’s a small but meaningful step toward building a circular economy where sharing replaces unnecessary consumption.

We believe this concept has the potential to make a significant impact, both by providing a practical service and by encouraging more sustainable behavior in urban communities. Our goal is to create a tool rental platform that is as beneficial for its users as it is for the environment.

# Taxonomy: Business Model
User Type: Person
Listing Kind: Good Transfer
Listing Type: Physical Good
Frequency: One-Time
Quantity: One
Price Discovery: Set by Provider
Price Calculation: Quote
Conversation System:Transaction Conversation
Review by: By Customer
Review of: Of Listing
Trust and Safety: ID Verification
Revenue Stream:Commission
Revenue Source: Customer

# Here are some user stories tailored to the provided database and system design:
As a customer,
I want to browse available listings with detailed information (e.g., name, brand, condition, and price),
So that I can make an informed decision before making a purchase.

As a provider,
I want to create, update, and manage my listings on the platform,
So that I can showcase my products to potential customers.

As a customer,
I want to leave a review for a product I purchased, including a rating and comment,
So that I can share my experience with other users and help them decide.

As a customer,
I want to view my transaction history,
So that I can keep track of my past purchases and their statuses.

As a provider,
I want to receive notifications when a new transaction is made for one of my listings,
So that I can prepare the item for delivery or further action.

As a customer,
I want to filter listings by brand, price range, or availability,
So that I can quickly find products that meet my preferences.

As a provider,
I want to set a price for each listing and specify its availability,
So that customers see up-to-date and accurate information.

As a user,
I want to sign up with my personal details, including my email and address,
So that I can create an account and start using the platform.

# Entity Descriptions and Their Roles
User
The User table stores essential information about all registered users on the platform. It includes details like the user’s name, address, postal code, city, email, and phone number. The id column serves as the unique identifier for users.

Customer
The Customer table represents a specific subset of users who act as buyers. It links to the User table through the PhoneC foreign key. This allows for seamless integration between general user information and customer-specific operations. Additionally, the Customer table includes a premium attribute, which we planned but did not have time to integrate into the website functionality. If further developed, premium status would exempt customers from paying the commission fee in exchange for a monthly subscription.

Provider
The Provider table contains data about users who act as sellers or providers of goods. Each provider is uniquely identified by ProviderP and may add and manage listings on the platform. The Provider table also includes a premium attribute. While this was not implemented in the website, the intended functionality was to promote tools provided by premium providers more effectively compared to standard providers.

Listing
The Listing table stores information about items available for purchase. It includes attributes such as NameTool, Brand, Condition, BatteryIncluded, and PriceSetByProvider. Each listing is associated with a specific provider (ProviderID) to define its seller.

Transaction
The Transaction table records purchases made on the platform. It links listings (ListingID), providers (ProviderP), and customers (PhoneC) to define the involved parties. Additionally, it includes details such as the commission fee and transaction date. While designing this table, the primary key was defined using a composite key that includes the ListingID, PhoneC, and Date attributes. This approach was chosen to make the transaction uniquely identifiable by the elements that naturally define its uniqueness: the customer, the listing, and the date of the transaction.  

In hindsight, it would have been simpler and more efficient to use a system-generated unique identifier (e.g., a transaction ID) as the primary key. This would have streamlined the design and ensured uniqueness without relying on multiple attributes.  

Furthermore, ProviderP was mistakenly included as part of the primary key in the initial design, even though this was never the intention. Since ProviderP is already linked to the ListingID, its inclusion in the primary key was redundant and unnecessary. Ideally, ProviderP should have been removed from the transaction table altogether, as its presence in this table does not adhere to the principles of NF3. Unfortunately, this oversight was only identified too late to make adjustments without disrupting the functioning of the website.

Review
The Review table allows customers to leave feedback on listings. It includes a Rating, Comment, and the date of the review. Each review is linked to a specific listing and customer, enabling transparency and accountability for all transactions.

# EER
User and Customer
The relationship between User and Customer is one-to-one. Each customer is an extension of a user, meaning every customer must first exist as a user in the system. However, not all users are customers, which highlights that this is a specialized relationship.

User and Provider
Similarly, the relationship between User and Provider is one-to-one. A provider is a specific type of user who offers listings on the platform. This relationship allows the system to differentiate between standard users and those acting as providers.

Provider and Listing
The relationship between Provider and Listing is one-to-many. A single provider can create multiple listings for the products or services they offer. However, each listing is tied to exactly one provider, ensuring accountability for each product offered.

Listing and Transaction
The relationship between Listing and Transaction is one-to-many. A single listing can be involved in multiple transactions over time (e.g., multiple customers purchasing the same product). However, each transaction is linked to only one listing, representing the specific item purchased.

Customer and Transaction
The relationship between Customer and Transaction is one-to-many. A single customer can engage in multiple transactions on the platform. Each transaction is associated with exactly one customer, reflecting their specific purchase history.

Transaction and Review
The relationship between Transaction and Review is one-to-one. Each transaction can result in a single review, allowing the customer to provide feedback on their purchase. This ensures that reviews are tied directly to completed transactions.

Listing and Review
The relationship between Listing and Review is one-to-many. A single listing can have multiple reviews, as it may be purchased and reviewed by different customers over time. However, each review is connected to one specific listing, ensuring clarity on what is being reviewed.