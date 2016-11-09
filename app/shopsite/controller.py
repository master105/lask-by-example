import json
import os
import mechanize

__author__ = 'fantom'
from flask import Blueprint, request, render_template, flash, redirect, url_for, Response
from flask.ext.login import login_required, login_user, logout_user, current_user
from app import db, login_manager, models
from flask.ext.api.decorators import set_renderers
from flask.ext.api.renderers import HTMLRenderer
from HTMLParser import HTMLParser
from werkzeug.utils import secure_filename

mod_site = Blueprint('website', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class MLStripper(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    user = db.session.query(models.Shop).filter_by(id=user_id).first()
    print(user.is_authenticated)
    return user


# somewhere to logout
@mod_site.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('website.welcome'))


@mod_site.route('/')
@set_renderers(HTMLRenderer)
def welcome():
    # Welcome.
    if current_user.is_authenticated:
        return redirect(url_for('website.get_shop_items', shop_id=int(current_user.id)))
    else:
        return render_template('gentelella/production/login.html')


@mod_site.route('/signUpShop', methods=['GET', 'POST'])
@login_required
# route for GetShopItems function here
@set_renderers(HTMLRenderer)
def sign_up_shop():
    if request.method == 'POST':
        if request.form['name'] and request.form['owner']:
            new_shop = models.Shop(shop_name=request.form['name'], shop_profile_pic=request.form['profile_pic'],
                                   owner_name=request.form['owner'], owner_email=request.form['email'],
                                   password=request.form['password'], mobile=request.form['mobile'],
                                   description=request.form['description'], shop_address=request.form['shop_address'])
            db.session.add(new_shop)
            login_user(new_shop)
            db.session.flush()
            new_id = new_shop.id
            db.session.commit()
            flash("Shop Added!!")
            return redirect(url_for('website.new_shop_item', shop_id=new_id))
    return render_template('shop/NewShop.html')


@mod_site.route('/home')
# route for GetShopItems function here
@set_renderers(HTMLRenderer)
def home():
    print("current_user: " + str(current_user.id))
    shop_id = request.args.get('shop_id')
    print("shop_id: " + str(shop_id))
    if int(current_user.id) == int(shop_id):
        shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
        return render_template('gentelella/production/index.html', shop=shop)
    else:
        return Response('Not Authorized')


@mod_site.route('/GetShopItems')
# route for GetShopItems function here
@set_renderers(HTMLRenderer)
def get_shop_items():
    print("current_user: " + str(current_user.id))
    shop_id = request.args.get('shop_id')
    print("shop_id: " + str(shop_id))
    if int(current_user.id) == int(shop_id):
        shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
        items = db.session.query(models.Items).filter_by(shop_id=shop_id)
        return render_template('shop/ItemsList.html', shop=shop, items=items)
    else:
        return Response('Not Authorized')


@mod_site.route('/editMyShop/<int:shop_id>', methods=['GET', 'POST'])
# route for editMyShop function here
@set_renderers(HTMLRenderer)
def edit_shop(shop_id):
    if int(current_user.id) == int(shop_id):
        shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
        if request.method == 'POST':
            if request.form['owner_name']:
                shop.owner_name = request.form['owner_name']
            if request.form['owner_email']:
                shop.owner_email = request.form['owner_email']
            if request.form['shop_name']:
                shop.shop_name = request.form['shop_name']
            if request.form['description']:
                shop.description = request.form['description']
            if request.form['shop_address']:
                shop.shop_address = request.form['shop_address']
            if request.form.get('mobile'):
                shop.mobile = request.form['mobile']
            if request.form['lon']:
                longitude = request.form['lon']
                shop.longitude = longitude
            if request.form['lat']:
                latitude = request.form['lat']
                shop.latitude = latitude
            db.session.add(shop)
            db.session.commit()
            flash("shop Edited!!")
            return redirect(url_for('website.get_shop_items', shop_id=shop_id))
        else:
            return render_template('shop/EditShop.html', shop=shop)
    else:
        Response("Not Authorised")


@mod_site.route('/editMyShop/uploadImage/<int:shop_id>', methods=['GET', 'POST'])
# route for editMyShop function here
@set_renderers(HTMLRenderer)
def edit_shop_image(shop_id):
    if int(current_user.id) == int(shop_id):
        shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
        if request.method == 'POST':
            if request.files['file']:
                # check if the post request has the file part
                if 'file' not in request.files:
                    flash('No file part')
                file_upload = request.files['file']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file_upload.filename == '':
                    flash('No selected file')
                if file_upload and allowed_file(file_upload.filename):
                    filename = secure_filename(file_upload.filename)
                    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    browser = mechanize.Browser()
                    browser.open("http://bubble.zeowls.com/upload.php")
                    # file uploading
                    form = browser.form = browser.forms().next()
                    form.add_file(file_upload, filename=os.path.basename(filename))
                    send_response = browser.submit()
                    data = strip_tags(send_response.get_data().replace("\n", "").replace(" ", ""))
                    obj = json.loads(data)
                    image_file = obj['image']
                    shop.shop_profile_pic = image_file
            db.session.add(shop)
            db.session.commit()
            flash("shop Edited!!")
            return redirect(url_for('website.edit_shop', shop_id=shop_id))
        else:
            return render_template('shop/ImageUpload.html', shop=shop)
    else:
        Response("Not Authorised")


@mod_site.route('/newShopItem/<int:shop_id>/', methods=['GET', 'POST'])
@login_required
# route for newShopItem function here
@set_renderers(HTMLRenderer)
def new_shop_item(shop_id):
    if int(current_user.id) == int(shop_id):
        global new_item
        shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
        main_cats = db.session.query(models.Category).all()
        sub_cat = {}
        for cat in main_cats:
            print(cat.name)
            sub_cat[cat.id] = db.session.query(models.SubCategory).filter_by(parentCat=cat.id)
        if request.method == 'POST':
            if request.form['name'] and request.form['quantity']:
                new_item = models.Items(name=request.form['name'], quantity=request.form['quantity'], shop=shop,
                                        cat_id=request.form.get('cat_id'), price=request.form['price'],
                                        description=request.form['description'], image=request.form['profile_pic'])
                db.session.add(new_item)
                db.session.commit()
                flash("New Item Added!!")
            return redirect(url_for('website.get_shop_items', shop_id=shop_id))
        else:
            return render_template('shop/NewItem.html', shop=shop, main_cats=main_cats, sub_cat=sub_cat)
    else:
        return Response("Not Authorised")


@mod_site.route('/editShopItem/<int:shop_id>/<int:item_id>/', methods=['GET', 'POST'])
@login_required
# route for editShopItem function here
@set_renderers(HTMLRenderer)
def edit_shop_item(shop_id, item_id):
    if int(current_user.id) == int(shop_id):
        shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
        item = db.session.query(models.Items).filter_by(id=item_id, shop_id=shop_id).one()
        main_cats = db.session.query(models.Category).all()
        sub_cat = {}
        for cat in main_cats:
            print(cat.name)
            sub_cat[cat.id] = db.session.query(models.SubCategory).filter_by(parentCat=cat.id)
        if request.method == 'POST':
            if request.form['name']:
                item.name = request.form['name']
            if request.form['description']:
                item.description = request.form['description']
            if request.form['quantity']:
                item.quantity = request.form['quantity']
            if request.form['price']:
                item.price = request.form['price']
            if request.form.get('cat_id'):
                print('category', request.form.get('cat_id'))
                item.cat_id = request.form['cat_id']
            if request.form['image']:
                image_file = request.form['image']
                item.image = image_file
            # item.images = [{"id": 1, "url": "570269c0f2302.png"}, {"id": 2, "url": "570269c0f2302.png"},
            #                {"id": 3, "url": "570269c0f2302.png"}, {"id": 4, "url": "570269c0f2302.png"},
            #                {"id": 5, "url": "570269c0f2302.png"}, ]
            db.session.add(item)
            db.session.commit()
            flash("New Item Edited!!")
            return redirect(url_for('website.get_shop_items', shop_id=shop_id))
        else:
            return render_template('shop/EditItem.html', shop=shop, item=item, main_cats=main_cats, sub_cat=sub_cat)
    else:
        return Response("Not Authorised")


@mod_site.route('/deleteShopItem/<int:shop_id>/<int:item_id>/', methods=['GET', 'POST'])
@login_required
# route for deleteShopItem function here
@set_renderers(HTMLRenderer)
def delete_shop_item(shop_id, item_id):
    shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
    item = db.session.query(models.Items).filter_by(id=item_id, shop_id=shop_id).one()
    if int(current_user.id) == int(shop_id):
        if request.method == 'POST':
            db.session.delete(item)
            db.session.commit()
            flash("New Item DELETED!!")
            return redirect(url_for('website.get_shop_items', shop_id=shop_id))
        else:
            return render_template('shop/DeleteItem.html', shop=shop, item=item)
    return Response("Not Authorised")


@mod_site.route('/myOrders/<int:shop_id>', methods=['GET', 'POST'])
@login_required
# route for myOrders function here
@set_renderers(HTMLRenderer)
def get_shop_orders(shop_id):
    shop = db.session.query(models.Shop).filter_by(id=shop_id).one()
    if int(current_user.id) == int(shop_id):
        orders = db.session.query(models.Orders).join(models.Items).filter(models.Items.shop_id == shop_id)
        return render_template('shop/OrdersList.html', shop=shop, orders=orders)
    return Response("Not Authorised")


@mod_site.route("/login", methods=["GET", "POST"])
@set_renderers(HTMLRenderer)
def login():
    if request.method == 'POST':
        print("POST")
        errors = []
        username = request.form.get('username')
        password = request.form.get('password')
        print(username + ":" + password)
        user = db.session.query(models.Shop).filter_by(owner_email=username, password=password).first()
        if user is None:
            # flash('Username or Password is invalid', 'error')
            errors.append("Username or Password is invalid")
            return render_template('gentelella/production/login.html', errors=errors)
        else:
            user.authenticated = True
            login_user(user)
            # flash('Logged in successfully')
            return redirect(request.args.get('next') or url_for('website.home', shop_id=user.id))
    else:
        return render_template('gentelella/production/login.html')
