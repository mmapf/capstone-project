from flask import Flask, jsonify, request
from models import app, db, Customer, Item, Orders
from datetime import date
from auth import AuthError, requires_auth

@app.route('/<int:id>')
def index(id):

    customer = Customer.query.filter_by(id=id).one_or_none()

    return jsonify({
        'success': True,
        'customer': customer.name
    })


@app.route('/customers')
@requires_auth('get:customers')
def get_customers():
    customers = Customer.query.all()

    if customers is None:
        abort(404)

    customer_list = []

    for customer in customers:
        customer_list.append([customer.name, customer.email])

    return jsonify({
        'success': True,
        'status_code': 200,
        'customers': customer_list
    })


@app.route('/new_customer', methods=['POST'])
@requires_auth('post:customer')
def create_customer():

    data = request.get_json()
    today = date.today()

    if (data['name'] is None) or (data['email'] is None):
        abort(400)

    customer = Customer(name=data['name'],
                        email=data['email'], join_date=today)

    try:
        db.session.add(customer)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    new_customer = Customer.query.filter_by(name=data['name']).one_or_none()
    if new_customer is None:
        abort(422)

    return jsonify({
        'success': True,
        'status_code': 200,
        'Customer': new_customer.name
    })


@app.route('/update_customer/<int:id>', methods=['PATCH'])
@requires_auth('patch:customer')
def update_customer(id):
    data = request.get_json()

    customer = Customer.query.filter_by(id=id).one_or_none()
    if customer is None:
        abort(404)

    if not data['name'] and not data['email']:
        abort(400)

    if data['name']:
        customer.name = data['name']

    if data['email']:
        customer.email = data['email']

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    updated_customer = Customer.query.filter_by(id=id).one_or_none()
    if updated_customer is None:
        abort(422)

    return jsonify({
        'success': True,
        'status_code': 200,
        'customer_name': updated_customer.name,
        'customer_email': updated_customer.email
    })


@app.route('/delete_customer/<int:id>', methods=['DELETE'])
@requires_auth('delete:customer')
def delete_customer(id):
    customer = Customer.query.filter_by(id=id).one_or_none()
    if customer is None:
        abort(404)

    deleted_name = customer.name

    try:
        db.session.delete(customer)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    customers = customer.query.all()

    return jsonify({
        'success': True,
        'deleted_customer': deleted_name,
        'num_of_remaining_customers': len(customers)
    })


# ITEM ENDPOINTS

@app.route('/items')
@requires_auth('get:items')
def get_items():
    items = Item.query.all()

    if items is None:
        abort(404)

    item_list = []

    for item in items:
        item_list.append([item.name, item.brand, item.price])

    return jsonify({
        'success': True,
        'status_code': 200,
        'items': item_list
    })


@app.route('/new_item', methods=['POST'])
@requires_auth('post:item')
def create_item():

    data = request.get_json()

    if not data['name'] or not data['brand'] or not data['price']:
        abort(400)

    item = Item(name=data['name'],
                brand=data['brand'], price=data['price'])

    try:
        db.session.add(item)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    return jsonify({
        'success': True,
        'status_code': 200,
        'Item': data['name']
    })


@app.route('/update_item/<int:id>', methods=['PATCH'])
@requires_auth('patch:item')
def update_item(id):
    data = request.get_json()

    item = Item.query.filter_by(id=id).one_or_none()
    if item is None:
        abort(404)

    if not data['name'] and not data['brand'] and not data['price']:
        abort(400)

    if data['name']:
        item.name = data['name']

    if data['brand']:
        item.brand = data['brand']

    if data['brand']:
        item.price = data['price']
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    updated_item = Item.query.filter_by(id=id).one_or_none()

    return jsonify({
        'success': True,
        'status_code': 200,
        'item_name': updated_item.name,
        'item_brand': updated_item.brand,
        'item_price': updated_item.price
    })


@app.route('/delete_Item/<int:id>', methods=['DELETE'])
@requires_auth('delete:item')
def delete_Item(id):
    item = Item.query.filter_by(id=id).one_or_none()
    if item is None:
        abort(404)

    deleted_name = item.name

    try:
        db.session.delete(item)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    items = Item.query.all()

    return jsonify({
        'success': True,
        'status_code': 200,
        'deleted_item': deleted_name,
        'num_of_remaining_items': len(items)
    })

# ORDER endpoints


@app.route('/orders')
@requires_auth('get:orders')
def get_orders():
    orders = Orders.query.all()
    if orders is None:
        abort(404)

    orders_list = []

    for order in orders:
        orders_list.append([order.id, order.order_date,
                            order.customer.name, order.item.name, order.quantity])

    return jsonify({
        'success': True,
        'status_code': 200,
        'orders_list': orders_list,
        'num_of_orders': len(orders)
    })


@app.route('/submit_order', methods=['POST'])
@requires_auth('post:order')
def submit_order():
    data = request.get_json()

    item = Item.query.filter_by(id=data['item_id']).one_or_none()
    if item is None:
        abort(404)

    if item.available == False:
        abort(422, 'item not available')

    today = date.today()
    total_price = item.price * data['quantity']

    order = Orders(order_date=today, customer_id=data['customer_id'],
                   item_id=data['item_id'], quantity=data['quantity'], amount_due=total_price)
                   
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    return ({
        'success': True,
        'status_code': 200 
    })


@app.route('/delete_order/<int:id>', methods=['DELETE'])
@requires_auth('delete:order')
def delete_order(id):
    order = Orders.query.filter_by(id=id).one_or_none()
    if order is None:
        abort(404)

    orders = Orders.query.all()

    previous_num_of_orders = len(orders)

    try:
        db.session.delete(order)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print('Exception:', exc)
        abort(422)

    current_orders = Orders.query.all()

    current_num_of_orders = len(current_orders)

    if (current_num_of_orders) == (previous_num_of_orders - 1):
        return jsonify({
            'success': True,
            'message': 'order was deleted',
            'previous_orders': previous_num_of_orders,
            'current_orders': current_num_of_orders
        })

    else:
        abort(422, 'Order was not deleted')





@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    })

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422