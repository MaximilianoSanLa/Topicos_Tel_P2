from flask import Flask
from extensions import db
from controllers.payment_controller import payment
from controllers.purchase_controller import purchase
from controllers.delivery_controller import delivery
from models.delivery import DeliveryProvider
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

app.register_blueprint(payment, url_prefix="/payment")
app.register_blueprint(purchase, url_prefix="/purchase")
app.register_blueprint(delivery, url_prefix="/delivery")

@app.route('/')
def home():
    return "Sales Service Running"

def initialize_delivery_providers():
    with app.app_context():
        if DeliveryProvider.query.count() == 0:
            providers = [
                DeliveryProvider(name="DHL", coverage_area="Internacional", cost=50.0),
                DeliveryProvider(name="FedEx", coverage_area="Internacional", cost=45.0),
                DeliveryProvider(name="Envia", coverage_area="Nacional", cost=20.0),
                DeliveryProvider(name="Servientrega", coverage_area="Nacional", cost=15.0),
            ]
            db.session.bulk_save_objects(providers)
            db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        initialize_delivery_providers()
    app.run(host="0.0.0.0", port=5002)
