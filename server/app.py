#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify, abort
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Sweet, Vendor, VendorSweet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Vendor(Resource):
    def get(self):

        vendor_dicts = [vendor.to_dict(rules=('-vendor_sweets',)) for vendor in Vendor.query.all()]

        return make_response(
            jsonify(vendor_dicts),
            200
        )

class VendorsById(Resource):
    def get(self, id):

        vendor = Vendor.query.filter(Vendor.id == id).first()

        if not vendor:
            return make_response({'error': "Vendor not found"},404)

        vendor_dict = vendor.to_dict()

        return make_response(
            jsonify(vendor_dict),
            200
        )

    def delete(self, id):
        vendor = Vendor.query.filter_by(id=id).first()

        if not vendor:
            abort(404, 'The vendor you are trying to delete was not found!')

        db.session.delete(vendor)
        db.session.commit()

        response = make_response('', 204)

        return response

api.add_resource(VendorsById, '/vendors/<int:id>')



class Sweets(Resource):
    def get(self):

        sweet_dicts = [sweet.to_dict(rules=('-vendor_sweets',)) for sweet in Sweet.query.all()]

        return make_response(
            jsonify(sweet_dicts),
            200
        )

api.add_resource(Sweets, '/sweets')

class SweetsById(Resource):
    def get(self, id):

        sweet = Sweet.query.filter(Sweet.id == id).first()

        if not sweet:
            return make_response({'error': "Sweet not found"},404)

        sweet_dict = sweet.to_dict(rules=('-vendor_sweets',))

        return make_response(
            jsonify(sweet_dict),
            200
        )

api.add_resource(SweetsById, '/sweets/<int:id>')

class VendorSweets(Resource):
    def post(self):
        try:
            new_vendor_sweet = VendorSweet(
                price=request.get_json()['price'],
                vendor=request.get_json()['vendor_id'],
                sweet_id=request.get_json()['sweet_id']
            )

            db.session.add(new_vendor_sweet)
            db.session.commit()

            associated_sweet = Sweet.query.filter(Sweet.id == new_vendor_sweet.sweet_id).first()
            associated_sweet_dict = associated_sweet.to_dict()

            return make_response(
                jsonify(associated_sweet.dict),
                201
            )

        except:
            return make_response(
                { 'error': ["Validation error"] },
                400
            )

api.add_resource(VendorSweets, '/vendor_sweets')




if __name__ == '__main__':
    app.run(port=5555, debug=True)


