from flask import Blueprint, render_template, request, redirect, url_for
from models.purchase import Purchase
from extensions import db
from flask_login import login_required, current_user

purchase = Blueprint('purchase', __name__)

@purchase.route('/create', methods=['POST'])
@login_required
def create_purchase():
    book_id = request.form.get('book_id')
    amount = float(request.form.get('amount'))
    new_purchase = Purchase(buyer_id=current_user.id, book_id=book_id, amount=amount, status='Pending')
    db.session.add(new_purchase)
    db.session.commit()
    return redirect(url_for('payment.payment_page', purchase_id=new_purchase.id))
