from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

# note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('login')

@app.route('/', methods=['GET'])
def main():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('You are now logged In!', 'message')
            print(session)
            return redirect('/blog')
        else:
            flash('User password incorrect or does not exist', 'error')
    return render_template('login.html', heading='Log In')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if password != verify:
            flash('Password does not match', 'error')
            return redirect('/register')
        
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')
        else:
            flash('Duplicate user exists', 'error')
    return render_template('register.html', heading='Register Now')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

@app.route('/blog', methods=['GET'])
def blog():
    owner = User.query.filter_by(email=session['email']).first()
    blog_list = Blog.query.filter_by(owner=owner).all()

    id = request.args.get('id')

    if not id:
        return render_template('blog.html', heading='Blog Posts', id=id, blog_list = blog_list)
    else:
        post = Blog.query.get(int(id))
        return render_template('blog.html', heading='Blog Post', id=id, blog_list=blog_list, post=post)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    owner = User.query.filter_by(email=session['email']).first()
    
    if request.method == 'POST':
        id = request.form['id']
        post = Blog.query.get(id)
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''

        #TODO: keep text that user put in but show error messsage where empty.
        if title.strip() == "":
            title_error = 'Please create a title.'
            return render_template('newpost.html', heading='New Post', title_error=title_error, body_error=body_error, id=id, title=title, body=body)
        if body.strip() == "":
            body_error = 'Please write something for your blog post.'
            return render_template('newpost.html', heading='New Post', title_error=title_error, body_error=body_error, id=id, title=title, body=body)
        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id=' + str(new_post.id))
    
    return render_template('newpost.html', heading='New Post')

if __name__ == '__main__':
    app.run()