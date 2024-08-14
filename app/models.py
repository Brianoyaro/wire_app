from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True)
    name = db.Column(db.String(), nullable=False)
    password_hash = db.Column(db.String())
    # I think this relationship to Cart is redundant and utterly not necessary. On second thought, I think that it should stay i.e cart.seller.email helps me access user.email from Cart object
    cart = db.relationship('Cart', backref='owner', lazy='dynamic')
    items = db.relationship('Item', backref='seller', lazy='dynamic')

    def __str__(self):
        return '{}: {}'.format(self.id, self.email)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # store he name in lower to help in crosschecking category_name if it exists in the database
    name = db.Column(db.String(40), unique=True)
    items = db.relationship('Item', backref='category', lazy='dynamic')

    def __str__(self):
        return self.name


cart_item = db.Table('cart_item', 
                     db.Column('cart_id', db.Integer, db.ForeignKey('cart.id')),
                     db.Column('item_id', db.Integer, db.ForeignKey('item.id')))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    price = db.Column(db.Float())
    # use the fancy datalist stuff at the html level to help users easily pick from available categories
    category_name = db.Column(db.String(50), db.ForeignKey('category.name'))
    image = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    in_stock = db.Column(db.Boolean, nullable=False, default=True)

    def __str__(self):
        return 'Item: {} sold at a price of  {}'.format(self.name, self.price)



class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # e.g user.cart.items gives all items in a paricular cart
    # e.g user.cart.items.append(dummy_item) adds an item to this cart
    items = db.relationship('Item', secondary=cart_item)

    def __str__(self):
        return self.items
    

@login.user_loader
def load_user(id):
    '''Loads a user from Flask's user session table whenever a user navigates to a new page'''
    return User.query.get(int(id))