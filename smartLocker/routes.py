from flask import render_template, url_for, flash, redirect, request, abort
from smartLocker import app, db, bcrypt
from smartLocker.forms import registrationForm, LoginForm, UpdateAccountForm, PostForm, typeChoiceForm, registrationDeliveryForm, PinPadForm, LockerForm
from smartLocker.models import User, Post, User2
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
import RPi.GPIO as GPIO 
from time import sleep

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.paginate(page=page, per_page=5)
    return render_template("home.html",posts=posts)

# @app.route("/about")
# def about():
#     return render_template("about.html",title='About')
@app.route("/type_choice", methods= ['GET', 'POST'])
def type_choice():
    form = typeChoiceForm()
    if form.validate_on_submit():
        if form.customer.data:
            return redirect(url_for('register'))
        if form.delivery.data:
           return redirect(url_for('deliveryregister')) 
    return render_template('type_choice.html',title='Type Choice',form=form)

@app.route("/delivery_registration", methods= ['GET', 'POST'])
def deliveryregister():
    form = registrationDeliveryForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user2 = User2(surname=form.surname.data, mail_address=form.mail_address.data, password=hashed_password, has_moto=form.has_moto.data, has_car=form.has_car.data)
        db.session.add(user2)
        db.session.commit()
        flash("Account Created for {0}, you can login now".format(form.surname.data),"success") # we can do the verification link to the email
        return redirect(url_for('login'))
    return render_template('deliveryregister.html',title='Delivery Registration',form=form)

@app.route("/registration", methods= ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))    
    form = registrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash("Account Created for {0}, you can login now".format(form.username.data),"success") # we can do the verification link to the email
        return redirect(url_for('login'))
    return render_template('register.html',title='Registration',form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user2 = User2.query.filter_by(mail_address=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('client_view'))
        elif user2 and bcrypt.check_password_hash(user2.password, form.password.data):
            login_user(user2, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for('delivery_view'))
        else:
            flash('Login Unsuccessful! please verify your credentials', 'danger')
    return render_template('new_login.html', title='Login', form=form)

@app.route("/client_view", methods= ['GET', 'POST'])
def client():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    form = PinPadForm()
    ref_pin = "1234"
    if form.validate_on_submit():
        if form.lognum.data == ref_pin:
            GPIO.output(18,1)
            sleep(2)
            # GPIO.output(18,0)
            # sleep(2)
            flash('You May Take Your delivery', 'success')
            return redirect(url_for('thanking'))
        else:
            flash('Login Unsuccessful! please verify your credentials', 'danger')
            return redirect(url_for('client'))
    return render_template('client_view.html',title='Type Choice',form=form)
@app.route("/thanking", methods= ['GET', 'POST'])
def thanking():
    GPIO.output(18,0)
    return render_template('thanking.html',title='Thanking')

@app.route("/about", methods= ['GET', 'POST'])
def about():
    form = LockerForm()
    GPIO.setwarnings(False)
    pin = 25
    relay = 18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN)
    GPIO.setup(relay, GPIO.OUT)
    sensor=GPIO.input(pin)
    if form.validate_on_submit():
        GPIO.output(relay,1)
        sleep(2)
        GPIO.output(relay,0)
        sleep(2)
        # return redirect(url_for('login'))
    if (sensor==1):
        form.locker_status.data = True
    elif (sensor==0):
        form.locker_status.data = False
    return render_template("about.html",title='About', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext 
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods= ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html', title='Account',image_file=image_file, form = form)


@app.route("/post/new", methods= ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created successfully!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form = form, legend = 'New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods= ['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form = form, legend = 'Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_posts.html",posts=posts, user=user)
