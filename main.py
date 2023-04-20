from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

api_key = "Akshat Soni"

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##Cafe TABLE Configuration

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250),    nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random",methods=["GET"])
def get_random_cafe():

    reading_cafe_db = db.session.query(Cafe).all()
    cafe_data = choice(reading_cafe_db)
    db.session.commit()

    return jsonify(cafe={
        'id': cafe_data.id,
    'name': cafe_data.name,
    'map_url': cafe_data.map_url,
    'img_url' : cafe_data.img_url,
    'location' : cafe_data.location,
    'seats' : cafe_data.seats,
    'has_toilet': cafe_data.has_toilet,
    'has_wifi':cafe_data.has_wifi,
    'has_sockets': cafe_data.has_sockets,
    'can_take_calls': cafe_data.can_take_calls,
    'coffee_price':cafe_data.coffee_price
    })

# @app.route("/random")
# def get_random_cafe():
#     cafes = db.session.query(Cafe).all()
#     random_cafe = random.choice(cafes)
#     #Simply convert the random_cafe data record to a dictionary of key-value pairs.
#     return jsonify(cafe=random_cafe.to_dict())


@app.route('/all',methods=["GET"])
def all():

    data_base =  db.session.query(Cafe).all()

    all_data = []

    for cafe_data in data_base:
        all_data.append(
            {
                'id': cafe_data.id,
                'name': cafe_data.name,
                'map_url': cafe_data.map_url,
                'img_url': cafe_data.img_url,
                'location': cafe_data.location,
                'seats': cafe_data.seats,
                'has_toilet': cafe_data.has_toilet,
                'has_wifi': cafe_data.has_wifi,
                'has_sockets': cafe_data.has_sockets,
                'can_take_calls': cafe_data.can_take_calls,
                'coffee_price': cafe_data.coffee_price
            }
        )

    return jsonify(cafes=all_data)

@app.route("/search")
def search():
    loc = request.args.get("location")

    loc_data = db.session.query(Cafe).filter_by(location=loc).first()

    return jsonify(cafes=
            {
                'id': loc_data.id,
                'name': loc_data.name,
                'map_url': loc_data.map_url,
                'img_url': loc_data.img_url,
                'location': loc_data.location,
                'seats': loc_data.seats,
                'has_toilet': loc_data.has_toilet,
                'has_wifi': loc_data.has_wifi,
                'has_sockets': loc_data.has_sockets,
                'can_take_calls': loc_data.can_take_calls,
                'coffee_price': loc_data.coffee_price
            }
        )


## HTTP POST - Create Record
@app.route("/add",methods=['GET','POST'])
def add_new_cafe():

    with app.app_context():

        add_record = Cafe(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),
        seats = request.form.get("seats"),
        has_toilet = request.form.get("has_toilet"),
        has_wifi = request.form.get("has_wifi"),
        has_sockets = request.form.get("has_sockets"),
        can_take_calls = request.form.get("can_take_calls"),
        coffee_price = request.form.get("coffee_price"),
        )
        db.session.add(add_record)
        db.session.commit()

    return jsonify(response={
        "success":"Successfully added the new cafes."
    })



## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>',methods=["PATCH"])
def update_cafe_price(cafe_id):

    if db.session.query(Cafe).get(cafe_id):
        with app.app_context():
            cafe_to_update = Cafe.query.get(cafe_id)
            cafe_to_update.coffee_price = request.args.get('new_price')
            db.session.commit()

        return jsonify(success="Successfully updated the price.")

    else:
        return jsonify(Error={
            "Not Found":"Sorry a cafe with that id was not found in the Database"
        })


## HTTP DELETE - Delete Record
# @app.route("/report-closed/<cafe_id>",methods=["DELETE"])
# def delete_cafe(cafe_id):
#
#     key = request.args.get('api_key')
#
#     if db.session.query(Cafe).get(cafe_id):
#
#         if key == api_key:
#             del_cafe = db.session.query(Cafe).get(cafe_id)
#             Cafe.session.delete(del_cafe)
#             db.session.commit()
#
#             return jsonify(success="Successfully updated the price.")
#
#         else:
#             return jsonify(error="Sorry that is not allowed make sure you enter the correct api_key.")
#
#     else:
#         return jsonify(error={
#             "Not Found": "Sorry a cafe with that id was not found in the database."
#         })

@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    key = request.args.get('api_key')

    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        if key == api_key:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Cafe deleted.")
        else:
            return jsonify(error="Invalid API key.")
    else:
        return jsonify(error="Cafe not found."), 404


if __name__ == '__main__':
    app.run(debug=True)
