from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_bcrypt import check_password_hash, generate_password_hash, Bcrypt
from config import Config
from models import db, User, Product, Images
import stripe
from io import BytesIO
import os

DOMAIN_NAME = os.environ["DOMAIN_NAME"]
stripe.api_key = os.environ["STRIPE_KEY"]

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)


@app.route("/success")
def success_route():
    return jsonify(message="payment successful"), 200


@app.route('/charge', methods=['POST'])
def create_payment():
    try:
        # data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=50000,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify(clientSecret=intent['client_secret']), 200
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route("/")
@jwt_required()
def main_route():
    username = get_jwt_identity()

    return jsonify(auth=True, username=username), 200


@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]

    found_user = User.query.filter_by(username=username).first()
    if found_user:
        fact = check_password_hash(found_user.password, password)
        if fact:
            token = create_access_token(identity=username)
            return jsonify(token=token, username=username, message=f"Welcome {username}"), 200

        return jsonify(message="Wrong Password"), 400

    return jsonify(message="User not found"), 400


@app.route("/register", methods=["POST"])
def register_route():
    username = request.json["username"]
    password = request.json["password"]
    hashed_password = generate_password_hash(password)
    found_user = User.query.filter_by(username=username).first()

    if found_user:
        return jsonify(message="User already found try login instead"), 400

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    token = create_access_token(identity=username)
    return jsonify(token=token, username=username), 200


@app.route("/all_products")
def all_products_route():
    query = Product.query.all()
    all_products = []
    if query:
        for product in query:

            product_images = []

            found_images = Images.query.filter_by(product_id=product.id).all()
            for image in found_images:
                product_images.append(f"{DOMAIN_NAME}/images/product_id/{product.id}/id/{image.id}")

            all_products.append({
                "store_id": product.store_id,
                "title": product.title,
                "price": product.price,
                "brand": product.brand,
                "description": product.description,
                "category": product.category,
                "id": product.id,
                "thumbnail": f"{DOMAIN_NAME}/thumbnail/{product.id}",
                "images": product_images
            })
        return jsonify(products=all_products), 200
    return jsonify(products=None), 200


@app.route("/get_product")
@jwt_required()
def get_product_route():
    username = get_jwt_identity()
    store = User.query.filter_by(username=username).first()
    store_products = Product.query.filter_by(store_id=store.id).all()

    products = []
    for product in store_products:
        files = Images.query.filter_by(product_id=product.id).all()
        images = []
        for file in files:
            images.append(f"{DOMAIN_NAME}/images/product_id/{product.id}/id/{file.id}")

        products.append({
            "id": product.id,
            "title": product.title,
            "price": product.price,
            "brand": product.brand,
            "description": product.description,
            "category": product.category,
            "thumbnail": f"{DOMAIN_NAME}/thumbnail/{product.id}",
            "images": images

        })
    return jsonify(products=products), 200


@app.route("/add_product", methods=["POST"])
def add_product():
    files = request.files
    values = request.values

    images = []
    sending_images = []
    for items in files:
        images.append(items)

    title = values.get('title')
    price = values.get('price')
    brand = values.get('brand')
    description = values.get("description")
    category = values.get('category')
    thumbnail = files.get('thumbnail')

    new_product = Product(store_id=1,
                          title=title,
                          price=price,
                          brand=brand,
                          description=description,
                          category=category,
                          thumbnail=thumbnail.read()
                          )
    db.session.add(new_product)
    db.session.commit()
    if len(images) > 1:
        new_images = images[1::]
        for image in new_images:
            new_image = Images(product_id=new_product.id, image=files[image].read())
            db.session.add(new_image)
            db.session.commit()
            sending_images.append(f"{DOMAIN_NAME}/images/{new_image.id}")

        return jsonify(title=title,
                       price=price,
                       brand=brand,
                       description=description,
                       category=category,
                       thumbnail=f"{DOMAIN_NAME}/thumbnail/{new_product.id}",
                       images=sending_images,
                       id=new_product.id,
                       msg="everything is greate"), 200

    return jsonify(title=title,
                   price=price,
                   brand=brand,
                   description=description,
                   category=category,
                   thumbnail=f"{DOMAIN_NAME}/thumbnail/{new_product.id}",
                   id=new_product.id,
                   msg="no images"), 200


@app.route("/update_product", methods=["POST"])
def update_product_route():
    files = request.files
    form = request.form

    changed_thumbnail = form.get("changed_thumbnail")
    changed_images = form.get("changed_images")

    id_ = form.get("id")
    title = form.get("title")
    brand = form.get("brand")
    price = form.get("price")
    description = form.get("description")
    category = form.get("category")
    thumbnail = files.get("thumbnail")

    found_product = Product.query.filter_by(id=id_).first()

    # If Both True
    if changed_thumbnail == "true" and changed_images == "true":
        found_product.title = title
        found_product.brand = brand
        found_product.price = price
        found_product.description = description
        found_product.category = category
        found_product.thumbnail = thumbnail.read()

        for image in files:
            if image != "thumbnail":
                new_image = Images(product_id=found_product.id, image=files[image].read())
                db.session.add(new_image)

        db.session.commit()
        return jsonify(msg="both true", thumbnail=changed_thumbnail, images=changed_images), 200

    #  If only Thumbnail True
    elif changed_thumbnail == "true" and changed_images == "false":
        found_product.title = title
        found_product.brand = brand
        found_product.price = price
        found_product.description = description
        found_product.category = category
        found_product.thumbnail = thumbnail.read()

        db.session.commit()
        return jsonify(msg="only thumbnail is true", thumbnail=changed_thumbnail, images=changed_images), 200

    # If only images True
    elif changed_thumbnail == "false" and changed_images == "true":
        found_product.title = title
        found_product.brand = brand
        found_product.price = price
        found_product.description = description
        found_product.category = category

        for image in files:
            if image != "thumbnail":
                new_image = Images(product_id=found_product.id, image=files[image].read())
                db.session.add(new_image)

        db.session.commit()
        return jsonify(msg="only images is true", thumbnail=changed_thumbnail, images=changed_images), 200

    # If Both are False
    else:
        found_product.title = title
        found_product.brand = brand
        found_product.price = price
        found_product.description = description
        found_product.category = category

        db.session.commit()
        return jsonify(msg="Both False", thumbnail=changed_thumbnail, images=changed_images), 200


@app.route("/thumbnail/<int:number>")
def get_image(number):
    found_product = Product.query.filter_by(id=number).first()
    thumbnail = found_product.thumbnail
    return send_file(BytesIO(thumbnail), mimetype="image"), 200


@app.route("/images/product_id/<int:number>/id/<int:id_>", methods=["GET", "DELETE"])
def get_images(number, id_):
    found_images = Images.query.filter_by(product_id=number, id=id_).first()

    if request.method == "GET":
        print("GET")
        return send_file(BytesIO(found_images.image), mimetype="image"), 200

    db.session.delete(found_images)
    db.session.commit()
    print("DELETE route")
    return jsonify(msg="Delete Route"), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
