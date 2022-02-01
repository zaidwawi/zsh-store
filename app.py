from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect , render_template, request, jsonify, url_for, make_response
from models import Products, User, setup_db, rollback, checkout, carts, order
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os 
from werkzeug.utils import secure_filename




def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS (app)
    db = SQLAlchemy(app)


######################### Auth ###############################################
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)




    class ModeslView(ModelView):
        def is_accessible(self):
            if current_user.is_authenticated:
                if current_user.is_Admin:
                    return current_user.is_authenticated

    admin = Admin(app)
    admin.add_view(ModeslView(User, db.session))
    admin.add_view(ModeslView(checkout, db.session))
    admin.add_view(ModeslView(Products, db.session))
    admin.add_view(ModeslView(carts, db.session))
    admin.add_view(ModeslView(order, db.session))

    










    @app.route('/login')
    def login():
        return render_template('login/login.html', user=current_user)

    @app.route('/login', methods = ['POST'])
    def login_action():
        email = request.form.get('username')
        password = request.form.get('pass')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully')
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Wronge password', category='error')
        else:
            flash("email does not exist", category='error')
        return redirect(url_for('login'))
            



    @app.route('/sign-up')
    def sign_up():
        return render_template('sign-up/sign-up.html', user=current_user)

    @app.route('/signup', methods=['POST'])
    def signUp():
        first_name = request.form.get('first_name')
        email = request.form.get('email')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone_number = request.form.get('phone')
        whatsapp = request.form.get('whatsapp')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('User already exist', category='error')
        elif len(first_name) < 2:
            flash("Your username must be more than 2 char", category='error')
        elif "@gmail.com" not in email:
            flash('Wronge email', category='error')
        elif len(password) < 5:
            flash('Your password is short', category='error')
        elif password != confirm_password:
            flash('The passwords doesnt match', category='error')
        elif len(phone_number) < 7:
            flash('Wronge number', category='error')
        elif len(whatsapp) < 7:
            flash('Wronge whatsapp number', category='error')
        elif len(address) < 3:
            flash('Wronge address', category='error')
        
        else:
            if email == 'zaidwawi056@gmail.com' or email == 'zaidwawi53@gmail.com':
                type_person = True
            else:
                type_person = False
            new_user = User(
                email=email,
                password=generate_password_hash(password, method='sha256'),
                first_name=first_name,
                address=address,
                phone_number=phone_number,
                phone_whats_number=whatsapp,
                is_Admin=type_person
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("Account created !", category= 'success')
            return redirect(url_for('home'))
        return render_template('sign-up/sign-up.html', user=current_user)

    @login_required
    @app.route('/logout')
    def logout():
        logout_user()
        flash('you have logout')
        return redirect(url_for('home'))






















    ################ work here ####################33

    @app.route('/results', methods = ['POST'])
    def search():
        search_term = request.form.get('search', None)

        if search_term:
                    page = request.args.get('page', 1, type = int)
                    products = Products.query.filter(
                    Products.products_name.ilike(f'%{search_term}%')).paginate(page = page, per_page = 9)
                    return render_template('website/products.html', products = products, user = current_user)
    

    

    @login_required
    @app.route('/add/cart/<int:id>', methods = ['GET','POST'])
    def add_to_cart(id):
        product = Products.query.get(id)
        products_name = product.products_name
        products_quantity = 1
        product_price = product.product_price
        category = product.category
        main_img = product.main_img

        total = int(product_price) * int(products_quantity)

        add_cart = carts(
            products_name = products_name,
            products_quantity = products_quantity,
            product_price = product_price,
            total = total,
            category = category,
            main_img = main_img,
            user_id = current_user.id,
            products_id = id
        )
        db.session.add(add_cart)
        db.session.commit()
        flash(f'add {products_name} successfully')

        return redirect(url_for('products'))

    

    @app.route('/product/add/<int:id>', methods = ['POST'])
    def post_product(id):
        product = Products.query.get(id)
        products_name = product.products_name
        products_quantity = request.form.get('quantity')
        product_price = product.product_price
        category = product.category
        main_img = product.main_img

        total = int(product_price) * int(products_quantity)
        add_cart = carts(
            products_name = products_name,
            products_quantity = products_quantity,
            product_price = product_price,
            total = total,
            category = category,
            main_img = main_img,
            user_id = current_user.id,
            products_id = id
        )
        db.session.add(add_cart)
        db.session.commit()
        flash(f'add {products_name} successfully')

        return render_template('website/single-product.html', user = current_user, products = product)



  








############################ client routes #######################################################


    ###### Home #####
    @app.route('/')
    def home():
        product = Products.query.limit(4)
        return render_template('website/Home.html', user=current_user, product= product)
    ##### products ####
    @app.route('/products')
    def products():
        page = request.args.get('page', 1, type = int)
        products = Products.query.paginate(page = page, per_page = 9)
        return render_template('website/products.html', user=current_user, products = products)
    
    @app.route('/products/<int:id>')
    def single_products(id):
        productss = Products.query.get(id)
        return render_template('website/single-product.html', products=productss, user=current_user)

    #### cart ####
    @login_required
    @app.route('/carts/pay', methods =['POST'])
    def submit():
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        address = request.form.get('address1')
        landmark = request.form.get('addres2')
        phone_number = request.form.get('phone-number')
        whats_app = request.form.get('whatsapp-number')
        notes = request.form.get('note')
        checkouts = checkout(
            costumer_name = first_name + " " + last_name,
            coustmer_email = current_user.email,
            costumer_phone = phone_number,
            costumer_whats_phone = whats_app,
            address = address,
            landmark = landmark,
            time = datetime.now(),
            notes = notes,
            user_id = current_user.id
        )
        db.session.add(checkouts)
        db.session.commit()

        cart = carts.query.filter_by(user_id = current_user.id).all()
        all_total = 0
        for i in cart:
            total = int(i.products_quantity) * int(i.product_price)
            all_total += total
        for items in cart:
            total = int(items.products_quantity) * int(items.product_price)
            if int(all_total) < 50:
                all_total += 10
            orders = order(
                products_img = items.main_img,
                products_name = items.products_name,
                products_price = items.product_price,
                products_quantity = items.products_quantity,
                item_total = total,
                all_total = all_total,
                user_id = current_user.id,
                checkout_id = checkouts.id
            )
            db.session.add(orders)
            db.session.commit()
        
        all_cart = carts.query.filter_by(user_id = current_user.id).all()
        for i in all_cart:
            i.delete()
        flash('zaid')
        return render_template('website/finish.html', user = current_user,name = first_name + " " + last_name, email =  current_user.email, time = datetime.now() , address = address, landmark = landmark, phone = phone_number, whats = whats_app, note =notes )
    @login_required
    @app.route('/carts', methods = ['POST', 'GET'])
    def cart():
        x = 0
        all_products = carts.query.filter_by(user_id = current_user.id).all()
        if len(all_products) == 0:
            flash('You dont have items in your cart', category='error')
            return redirect(url_for('home'))
        page = request.args.get('page', 1, type = int)
        cart_item = carts.query.filter_by(user_id = current_user.id).all()

        for i in all_products:
            all = int(i.product_price) * int(i.products_quantity)
            x += all

        if x < 50:
            away = 50 - int(x)
            x += 10
            shipp = False
            with_shipp = int(x) - 10
        else:
            with_shipp = x
            away = 0
            shipp = True
        


        return render_template('website/cart.html', user=current_user, products = cart_item, total = x , shipp = shipp, away = away, total_money = with_shipp)


    @login_required
    @app.route('/finish')
    def finish():
        return render_template('website/finish.html', user=current_user)


    @login_required
    @app.route('/delete/remove/<int:id>', methods = ['GET', 'POST'])
    def delete_cart(id):
        cart_item = carts.query.filter_by(user_id = current_user.id, id = id).first()
        cart_item.delete()
        flash(f'You have  delete {cart_item.products_name} Item successfully')
        return redirect(url_for('home'))

    
    @login_required
    @app.route('/products/<category>')
    def filter_by(category):
        page = request.args.get('page', 1, type = int)
        product = Products.query.filter_by(category = category).paginate(page = page, per_page = 9)
        if len(Products.query.filter_by(category = category).all()) == 0:
            flash('This category is empty !')
            return redirect(url_for('home'))
        else:
            return render_template('website/products_category.html', user = current_user, products = product)



########################################## Admin routes ###############################


    @login_required
    @app.route('/add/admin')
    def add_products():
        if current_user.is_authenticated:
            if current_user.is_Admin:
                return render_template('website/add-products.html', user=current_user)
            else:
                return redirect(url_for('home'))
      


    @app.route('/add/admin', methods = ['POST'])
    def add_admin_products():
        product_name = request.form.get('productName')
        product_price = request.form.get('productPrice')
        product_quantity = request.form.get('productQan')
        product_describtion1 = request.form.get('describtion1')
        product_describtion2 = request.form.get('describtion2')
        show_image = request.files['imageMain']
        imageOne = request.files['imageOne']
        imageTwo = request.files['imageTwo']
        category = request.form.get('category')



        imageMain = secure_filename(show_image.filename)
        imageOneName = secure_filename(imageOne.filename)
        imageTwoName = secure_filename(imageTwo.filename)

        show_image.save(os.path.join('static/products_image',imageMain))
        imageOne.save(os.path.join('static/products_image',imageOneName))
        imageTwo.save(os.path.join('static/products_image',imageTwoName))

        new_products = Products(
            products_name = product_name,
            products_quantity = product_quantity,
            product_price = product_price,
            category = category,
            main_img = imageMain,
            img_one = imageOneName,
            img_two = imageTwoName,
            describtion_one = product_describtion1,
            describtion_two = product_describtion2
        )
        db.session.add(new_products)
        db.session.commit()


        flash('Addedd success the item ')
        return redirect(url_for('add_products'))


    @login_required
    @app.route('/view/admin')
    def get_orders():
        if current_user.is_authenticated:
            if current_user.is_Admin:
                get_order = checkout.query.all()
                return render_template('website/view_order.html', user = current_user, orders = get_order)
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))

    @login_required
    @app.route('/view/admin/<int:user_id>/<int:product_id>')
    def get_order_info(user_id, product_id):
        if current_user.is_authenticated:
            if current_user.is_Admin:
                get_order = order.query.filter_by(user_id = user_id, checkout_id = product_id).all()
                all_total = order.query.filter_by(user_id = user_id, checkout_id = product_id).first().all_total
                return render_template('website/personal_order.html', user = current_user, orders = get_order, total =all_total)
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    

    @login_required
    @app.route('/view/admin/costumer/<int:user_id>/<int:checkout_id>')
    def get_order_infos(user_id, checkout_id):
        if current_user.is_authenticated:
            if current_user.is_Admin:
                get_order = checkout.query.filter_by(user_id = user_id, id = checkout_id).all()
                return render_template('website/costomer.html', user = current_user, orders = get_order)
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))

    @login_required
    @app.route('/dele/<int:user_id>/<int:checkout_id>', methods = ['POST', 'GET'])
    def dele_out(user_id, checkout_id):
        if current_user.is_authenticated:
            if current_user.is_Admin:
                get_order = order.query.filter_by(user_id = user_id, checkout_id = checkout_id).all()
                for i in get_order:
                    i.delete()
              
                db.session.query(checkout).filter_by(id=checkout_id, user_id = user_id).delete()
                db.session.commit()
                flash('delete')
                return redirect(url_for('home'))
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))

    @app.route('/deleteall')
    def delete():
        

        flash('done')
        return redirect(url_for('home'))

    return app 




APP = create_app()

if __name__ == '__main__':
    APP.run(debug=True)
