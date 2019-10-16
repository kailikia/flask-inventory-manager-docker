from flask import Flask,render_template,request, redirect,url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import json

from models.JsonEncoder import AlchemyEncoder

from config.config import *

app = Flask(__name__)
# Configs
app.config.from_object(DevelopmentConfig)
# sqlalchemy
db = SQLAlchemy(app)
# bcrypt
bcrypt = Bcrypt(app)

# 
from models.admin import Admin
from models.products import Products
from models.customers import CustomerModel
from models.orders import Orders


@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/admin/register', methods=['GET','POST'])
def admin_register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        confirmpass = request.form['confirmpass']

        # check if password and confirm password match
        if password != confirmpass:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('admin_register'))
        elif(Admin.check_admin_exist(email)):
            flash('Email already in use', 'danger')
            return redirect(url_for('admin_register'))
        else:
            # hash the password
            hashedpass = bcrypt.generate_password_hash(password).decode('utf-8')

            adm = Admin(firstname=fname,lastname=lname,email=email,password=hashedpass)
            adm.insert_record()

            flash('Admin successfully created', 'success')
            return redirect(url_for('admin_register'))

    return render_template('adminregister.html')

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # check if the email exists, then validate the password
        if Admin.check_admin_exist(email):
            if Admin.validate_password(email=email,password=password):
                # set the admin session
                session['admin'] = email
                session['aid'] = Admin.get_admin_id(email)
                print(session)
                return redirect(url_for('home'))
            else:
                flash('Invalid Credentials','danger')
                return redirect(url_for('admin'))
        else:
            flash('Invalid Credentials','danger')
            return redirect(url_for('admin'))

    return render_template('admin.html')

# admin logout
@app.route('/admin/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('admin'))

# administrator dashboard
@app.route('/dashboard', methods=['GET','POST'])
def home():
    if session:
        print(session)
        return render_template('index.html')
    else:
        flash('Please login to gain access', 'danger')
        return redirect(url_for('admin'))

# admin route to add a product
@app.route('/products', methods=['GET','POST'])
def products():
    if 'admin' in session:
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            # check if a product already exists
            if Products.check_product_exists(name):
                # if true, redirect to products page
                flash('Product already exists','danger')
                return redirect(url_for('products'))
            else:
                # add the product
                p = Products(name=name,price=price)
                p.insert_record()
                flash('Record successfully added', 'success')
                return redirect(url_for('products'))

        return render_template('products.html')
    else:
        return redirect(url_for('admin'))

# admin route to check the product reports
@app.route('/products/reports', methods=['GET','POST'])
def products_reports():
    if session:
        products = Products.fetch_all()
        return render_template('productsreport.html',products=products)

# update a product
@app.route('/products/update/<int:id>', methods=['GET','POST'])
def update_product(id):
    if request.method == 'POST':
        newname = request.form['newname']
        newprice = request.form['newprice']

        update = Products.update_by_id(id=id,name=newname,price=newprice)

        if update:
            flash('successfully updated', 'success')
            return redirect(url_for('products_reports'))
        else:
            flash('record not found')
            return redirect(url_for('products_reports','success'))

# delete a product
@app.route('/products/delete/<int:id>', methods=['GET','POST'])
def delete_product(id):
    deleted = Products.delete_by_id(id)
    if deleted:
        flash('Product successfully deleted','success')
        return redirect(url_for('products_reports'))
    else:
        flash('product not found','danger')
        return redirect(url_for('products_reports'))

# admin view all order
@app.route('/all/orders', methods=['GET','POST'])
def all_orders():

    orderszote = Orders.fetch_all()

    return render_template('allorders.html',orderszote=orderszote)


# customer login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        # check email exists
        if CustomerModel.check_email_exists(email):
            if CustomerModel.compare_password(email=email,password=password):
                session['email'] = email
                session['uid'] = CustomerModel.get_customer_id(email)
                return redirect(url_for('cust_home'))
            else:
                flash('Invalid login credential','danger')
                return redirect(url_for('login'))    
        else:
            flash('Invalid login credential','danger')
            return redirect(url_for('login'))     

    return render_template('customerlogin.html')

# customer registration
@app.route('/register', methods=['GET','POST'])
def customers_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        company = request.form['company']
        password = request.form['password']
        confirmpass = request.form['confirmpass']

        # check if password match
        if password != confirmpass:
            flash('passwords do not match', 'danger')
            return redirect(url_for('customers_register'))
        elif(CustomerModel.check_email_exists(email)):
            flash('Email already exist', 'danger')
            return redirect(url_for('customers_register'))
        else:
            hashedpass = bcrypt.generate_password_hash(password).decode('utf-8')

            c = CustomerModel(name=name,email=email,phone=phone,address=address,company=company,password=hashedpass)
            c.insert_record()
            flash('account successfully created! Please login','success')
            return redirect(url_for('login'))

    return render_template('register.html')


# customer making an order
@app.route('/customer/home', methods=['GET','POST'])
def cust_home():
    allproducts = Products.fetch_all()
    if 'email' in session:
        if request.method == 'POST':
            email = session['email']
            product = request.form['productname']
            company = request.form['name']
            
            qun = request.form['quantity']
            
            date = request.form['date']

            ch = Orders(email=email,product=product,orderdate=date,customer_id=session['uid'], company=company)
            ch.create_record()
            flash('Order successfully made','success')
            return redirect(url_for('cust_home'))
        return render_template('customerorder.html', products=allproducts)
    else:
        flash('Please login','danger')
        return redirect(url_for('login'))

#ALL PRODUCTS JSON
@app.route('/products/json')
def prodjson():
  c = Products.fetch_all()
  return json.dumps(c, cls=AlchemyEncoder)

@app.route('/add/order', methods=['POST'])
def orderJson():
    data = request.get_json(force=True)
    o = Orders(email=session['email'],quantity=data['quantity'],total=data['total'],product_id=data['product_id'],company=data['company']) #,customer_id=session['uid']
    o.create_record()
    return 'Order successfully saved'


@app.route('/manual/order', methods=['GET','POST'])
def manual():
    allproducts = Products.fetch_all()

    return render_template('manualorder.html')

# CUSTOMER ORDERS
@app.route('/orders', methods=['GET','POST'])
def orders():
    if 'email' in session:
        orders = Orders.fetch_by_id(session['uid'])

    return render_template('eachorder.html',orders=orders)


@app.route('/customer/logout', methods=['GET','POST'])
def customer_logout():
    session.clear()
    return redirect(url_for('index'))


# customer registration on admin
@app.route('/customers', methods=['GET','POST'])
def customers():
    allproducts = Products.fetch_all()

    if request.method == 'POST':

        email = request.form['email']
        products = request.form['productname']
        date = request.form['date']
        company = request.form['company']

        o = Orders(email=email,product=products,orderdate=date,company=company)
        o.create_record()
        flash('Order successfull made','success')
        return redirect(url_for('customers'))

    return render_template('customers.html', products=allproducts)

# cutomer reports
@app.route('/customers/reports', methods=['GET', 'POST'])
def customers_reports():
    allcustomers = CustomerModel.fetch_all_customers()

    return render_template('customersreport.html',allcustomers=allcustomers)


@app.route('/approve/order/<int:id>', methods=['POST'])
def approve_order(id):
    
    apr = request.form['approve']

    update = Orders.update_by_id(id=id,status=apr)

    if update:
        return redirect(url_for('all_orders'))
    


#if __name__ == '__main__':
 #   app.run(debug=True)