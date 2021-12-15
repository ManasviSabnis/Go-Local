from flask import Flask, render_template, request, url_for, redirect, session,flash
import pymongo
import bcrypt
from pymongo import MongoClient, ssl_support
#set app as a Flask instance 
app = Flask(__name__)
#encryption relies on secret keys so they could be run
app.secret_key = "testing"
#connoct to your Mongo DB database
mongo = MongoClient("mongodb+srv://manasvi:man14@queenman.rrrho.mongodb.net/test", ssl_cert_reqs=ssl_support.CERT_NONE)

#get the database name
db = mongo.get_database('reg_records')
#get the particular collection that contains the data
records = db.register
test = mongo.get_database('prod_details')
details = test.prod_details

#assign URLs to have a particular route
@app.route('/') 
@app.route('/home', methods=['POST'])
def home():
    #temp={'Product':'Product', 'Category' : 'Category','Price':'Price','UnitsInStock':'UnitsInStock','image' : 'image'}
    # data = temp.find()
    #data=mongo.db.test.find_one({'Product':'Product', 'Category' : 'Category','Price':'Price','UnitsInStock':'UnitsInStock','image' : 'image'})
    #return render_template('home.html',data=data)
        test= db.test.find({'Product':'Product', 'Category' : 'Category','Price':'Price','UnitsInStock':'UnitsInStock','image' : 'image'})
        return render_template('home.html', test=test)
    # except Exception as e:
    #     return dumps({'error' : str(e)})

@app.route('/dashboard', methods=['post', 'get'])
def dashboard():
    
    return render_template('dashboard.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route("/index", methods=['post', 'get'])
def index():
    message = ''
    #if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #if found in database showcase that it's found 
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            #hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            #insert it in the record collection
            records.insert_one(user_input)
            
            #find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            #if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')



@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                flash("Successfully Logged In!")
                return redirect(url_for('dashboard'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

@app.route('/create', methods=['POST'])

def create():
    
    if request.method == 'POST':
        
        test = mongo.db.test
        values=request.form.to_dict(flat=False)
        print(values)
        x=test.insert_one({'Product':values['Product'], 'Category' :  values['Category'],'Price':  values['Price'],'UnitsInStock':values['UnitsInStock'],'image' : values['image'],"Description":values['Description'],"SellerName" :values["SellerName"]})
        print(x)
        return redirect(url_for('dashboard'))

if __name__ == "__main__":
 
  app.run(host='0.0.0.0',debug=True)
