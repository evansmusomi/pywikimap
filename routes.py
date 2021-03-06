""" Maps browser requests to Python functions """

from models import db, User, Place
from forms import SignupForm, LoginForm, AddressForm
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

# Connect Flask to database
app.config.from_object('settings.Config')
db.init_app(app)

# Configure app to protect against CSRF
app.secret_key = "development-key"


@app.route("/")
def index():
    """ Renders home page """
    if 'email' not in session:
        return render_template("index.html", login=True)
    else:
        return render_template("index.html", home=True)


@app.route("/about")
def about():
    """ Renders about page """
    return render_template("about.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """ Renders the sign up page with form """

    if 'email' in session:
        return redirect(url_for('home'))

    form = SignupForm()

    if request.method == 'POST':
        if form.validate():
            new_user = User(form.first_name.data, form.last_name.data,
                            form.email.data, form.password.data)
            db.session.add(new_user)
            db.session.commit()

            # Create new session
            session['email'] = new_user.email
            return redirect(url_for('home'))

        else:
            return render_template("signup.html", form=form)

    elif request.method == 'GET':
        return render_template("signup.html", form=form)


@app.route("/home", methods=["GET", "POST"])
def home():
    """ Renders the home page """

    if 'email' not in session:
        return redirect(url_for('login'))

    form = AddressForm()

    places = []
    my_coordinates = (-1.2886111111111, 36.823055555556)

    if request.method == 'POST':
        if form.validate():
            # get the address
            address = form.address.data

            # query for places around it
            p = Place()
            my_coordinates = p.address_to_latlng(address)
            places = p.query(address)

            # return results
            return render_template("home.html",
                                   form=form,
                                   my_coordinates=my_coordinates,
                                   places=places,
                                   logout=True)

        else:
            return render_template("home.html", form=form, logout=True)

    elif request.method == 'GET':
        return render_template("home.html",
                               form=form,
                               my_coordinates=my_coordinates,
                               places=places,
                               logout=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Renders the log in page """

    if 'email' in session:
        return redirect(url_for('home'))

    form = LoginForm()

    if request.method == "POST":
        if form.validate():
            email = form.email.data
            password = form.password.data

            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                session['email'] = form.email.data
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))

        else:
            return render_template("login.html", form=form)

    elif request.method == 'GET':
        return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """ Clears user session and redirects to index page """
    session.pop('email', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
