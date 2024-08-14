from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegisterForm, NewItemForm
from flask_login import login_user, current_user, logout_user, login_required
from app.models import User, Cart, Category, Item
from werkzeug.urls import url_parse
from PIL import Image
import os
import secrets


@app.route('/')
@app.route('/index')
def home():
    '''home page'''
    categories = Category.query.all()
    data = {}
    for category in categories:
        data[category] = Item.query.filter_by(in_stock=True).all()
    return render_template('index.html', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''logs in a user'''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(email=form.email.data).first()
        if user is None or not user.get_password(form.password.data):
            flash('invalid credentials')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Logged in successfully')
        next_url = request.args.get('next')
        if not next_url or url_parse(next_url).netloc != '':
            next_url = 'home'
        return redirect(url_for(next_url))
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''registers a new user'''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # create a cart for a user when they register in the application
        new_cart = Cart()
        new_cart.owner = user
        db.session.add(new_cart)
        db.session.commit()
        flash('Account created succesfully.')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
@login_required
def logout():
    '''logs a user out'''
    logout_user()
    flash('You have successfully logged out!')
    return redirect(url_for('home'))


def save_image(picture_data):
    '''saves an image'''
    _, filename_extension = os.path.splitext(picture_data.filename)
    random_hex = secrets.token_hex(8)
    filename = random_hex + filename_extension
    picture_path = os.path.join(app.root_path, "static/pictures", filename)
    image_size = (125, 125)
    i = Image.open(picture_data)
    i.thumbnail(image_size)
    i.save(picture_path)
    # the commented line below saves picture-as-is while 4 lines above create a thumbnail 125 by 125 pixels size
    """pic_data.save(picture_path)"""
    return filename


@app.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    '''for adding a new item by a seller'''
    form = NewItemForm()
    if form.validate_on_submit():
        new_item = Item(name=form.name.data,
                    price=form.price.data,
                    description=form.description.data)
        category = form.category.data
        new_category = Category.query.filter_by(name=category.lower()).first()
        if new_category is None:
            new_category = Category(name=category.lower())
            db.session.add(new_category)
            db.session.commit()
        # save the image before commiting
        if form.image.data:
            image_name = save_image(form.image.data)
            new_item.image = image_name
        new_item.seller = current_user
        new_item.category = new_category
        db.session.add(new_item)
        db.session.commit()
        flash('Uploaded new item')
        return redirect(url_for('dashboard'))
    return render_template('new_item.html', form=form, title='New Item')


@app.route('/dashboard')
@login_required
def dashboard():
    '''seller views all their items'''
    categories = Category.query.filter_by(seller=current_user).all()
    data = {}
    for category in categories:
        category_items = category.items.filter_by(seller=current_user).all()
        data[category] = category_items
    return render_template('dashboard.html', data=data, title='Dashboard')


@app.route('/item/<int:pk>', methods=['GET', 'POST'])
@login_required
def item_detail(pk):
    '''detail view of an item'''
    item = Item.query.filter_by(id=int(pk)).first_or_404()
    if request.method == 'POST':
        #add to cart
        #*****I propose to handle total here in that before adding an item in the cart, I first compute (item.price * quantity ordered) then add it to a global tally variable for easy accessibilty in the respective templates
        current_user.cart.append({ 'item': item, 'count': request.post.get('quantity') })
        flash('Added {} to cart. Visit cart to checkout'.format(item.name))
        return redirect(url_for('home'))
    return render_template('item_detail.html', title=item.name, item=item)


@app.route('/cart')
@login_required
def cart():
    '''user views items in their cart'''
    entries = current_user.cart.items
    return render_template('cart.html', entries=entries, title='My Cart')


@app.route('/cart/item/<pk>', methods=['POST'])
@login_required
def delete_from_cart(pk):
    '''Confirms if a user wants to delete an item from their cart'''
    item = Item.query.filter_by(id=int(pk)).first_or_404()
    if request.method == 'POST':
        for entry in current_user.cart:
            if entry.item == item:
                current_user.cart.remove(entry)
                return redirect(url_for('cart'))
    return render_template('delete_from_cart.html', item=item, title='Cart Item Delete')