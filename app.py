from flask import Flask, request, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:admin@localhost:5432/tanitcloud"
 
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the "user_cloudacount" table that maps the many-to-many relationship
user_cloudaccount = db.Table('users_cloudaccount',
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('cloudaccount_id', db.Integer, db.ForeignKey('cloudaccount.id'), primary_key=True)
)

# Define the "User" table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True,unique=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    cloudaccounts = db.relationship('Cloudaccount', secondary=user_cloudaccount, lazy='subquery', backref=db.backref('owners', lazy=True))


# Define the "Cloudaccount" table
class Cloudaccount(db.Model):
    id = db.Column(db.Integer, primary_key=True,unique=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50))
# Create the tables in the database
with app.app_context():
    db.create_all()
# Create the table in the database
CORS(app)
# Define a route to add a new Test row to the database
@app.route('/add_user')
def add_test():
    user = Users(name='John', email='john@example.com', password='password', role='user')
    db.session.add(user)
    db.session.commit()
    return 'Test added successfully'

# Define a route to update user from the database
@app.route('/user/update/<int:user_id>', methods=['POST', 'PUT'])
def update_user(user_id):
    # get the user with the specified id
    user = Users.query.get(user_id)

    # check if the user exists
    if user is None:
        return "User not found", 404

    # get the updated data from the request
    data = request.json

    # update the user's data
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = data['password']
    if 'role' in data:
        user.role = data['role']

    # commit the changes to the database
    db.session.commit()

    return "User updated successfully"
# Define a route to delete user rows from the database
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        return {'message': 'User not found.'}, 404
    db.session.delete(user)
    db.session.commit()
    return {'message': 'User deleted successfully.'}, 204


# Define a route to get all Test rows from the database

@app.route('/get_user')
def get_tests():
    users = Users.query.all()
    test_list = [{'id': user.id, 'name': user.name, 'email': user.email , 'password': user.password, 'role': user.role} for user in users]
    return {'tests': test_list}

# Define a route to add a new Test row to the database
@app.route('/add_cloudaccount')
def add_cloudaccount():
    cloud_account_1 = Cloudaccount(name='AWS', email='aws@example.com', password='password', address='https://aws.example.com')
    cloud_account_2 = Cloudaccount(name='Google Cloud', email='gcp@example.com', password='password', address='https://gcp.example.com')
    db.session.add(cloud_account_1)
    db.session.add(cloud_account_2)
    db.session.commit()
    return 'Test added successfully'

# Define a route to update cloudaccountrows from the database
@app.route('/cloudaccount/update/<int:cloudaccount_id>', methods=['POST', 'PUT'])
def update_cloudaccount(cloudaccount_id):
    # get the cloudaccount with the specified id
    cloudaccount = Cloudaccount.query.get(cloudaccount_id)

    # check if the cloudaccount exists
    if cloudaccount is None:
        return jsonify({'error': 'Cloudaccount not found'}), 404

    # get the updated data from the request
    data = request.json

    # update the cloudaccount's data
    cloudaccount.name = data.get('name', cloudaccount.name)
    cloudaccount.email = data.get('email', cloudaccount.email)
    cloudaccount.password = data.get('password', cloudaccount.password)
    cloudaccount.address = data.get('address', cloudaccount.address)

    # commit the changes to the database
    db.session.commit()

    # return a success message
    return jsonify({'message': 'Cloudaccount updated successfully'})
# Define a route to delete cloudaccount  from the database
@app.route('/cloudaccount/delete/<int:cloudaccount_id>', methods=['DELETE'])
def delete_cloudaccount(cloudaccount_id):
    # get the cloud account with the specified id
    cloudaccount = Cloudaccount.query.get(cloudaccount_id)

    # check if the cloud account exists
    if cloudaccount is None:
        return jsonify({'error': 'Cloud account not found'}), 404

    # delete the cloud account from the database
    db.session.delete(cloudaccount)
    db.session.commit()

    # return a success message
    return jsonify({'message': 'Cloud account deleted successfully'})
# Define a route to get all Test rows from the database
@app.route('/get_cloudaccount')
def get_cloudaccount():
    cloudaccount = Cloudaccount.query.all()
    test_list = [{'id': c.id, 'name': c.name, 'email': c.email , 'password': c.password, 'address': c.address} for c in cloudaccount]
    return {'tests': test_list}

# Define a route to get all Test rows from the database
@app.route('/user/addcloudaccount')
def add_cloud_account():
    user_id = request.args.get('user_id')
    cloud_account_id = request.args.get('cloud_account_id')
    
    if not user_id or not cloud_account_id:
        return 'Missing user_id or cloud_account_id', 400
    
    user = Users.query.get(user_id)
    if not user:
        return f'User with ID {user_id} not found', 404
    
    cloud_account = Cloudaccount.query.get(cloud_account_id)
    if not cloud_account:
        return f'Cloud account with ID {cloud_account_id} not found', 404
    
    user.cloudaccounts.append(cloud_account)
    db.session.merge(user)
    db.session.commit()
    
    return f'Added cloud account "{cloud_account.name}" to user "{user.name}"', 200

@app.route('/user/<int:user_id>')
def get_user(user_id):
    # get the user with the specified id
    user = Users.query.get(user_id)

    # get all the user's associated cloud accounts
    cloud_accounts = user.cloudaccounts
    list_cloud_accounts = [{'id': c.id, 'name': c.name, 'email': c.email , 'password': c.password, 'address': c.address} for c in cloud_accounts]
    list_user = [{'id': u.id, 'name': u.name, 'email': u.email , 'password': u.password, 'role': u.role} for u in [user]]

    # render the user's details and cloud accounts on a template
    return {'cloud_accounts': list_cloud_accounts, 'test_user': list_user}

@app.route('/login', methods=['POST'])
def login():
    print(request.form['email'])
    email = request.form['email']
    password = request.form['password']
    user = Users.query.filter_by(email=email).first()

    if user is not None and user.password == password:
        # Authentication successful, store the user ID in the session
        session['user_id'] = user.id
        return {'status':'success','message': 'Authentication successful!'}
    else:
        return {'status':'error','message': 'Invalid email or password'}
if __name__ == '__main__':
    app.run()