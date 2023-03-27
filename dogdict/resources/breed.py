"""
    Contains all the resources that are used to access the Breed model in the database.
"""
import json
import os
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from dogdict.models import Breed, Group, db
from dogdict.constants import JSON
from flasgger import Swagger, swag_from
from flasgger.utils import swag_from


class BreedCollection(Resource):
    """
        Used to access multiple breeds at once.
    """
    #@swag_from("../doc/breedcollection/breeds_get.yml")
    def get(self):
        """
            Used to access ALL the breeds at once.
        """
        body = {"items": []}
        for db_breed in Breed.query.all():
            item = db_breed.serialize()
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=JSON)
    
    def post(self):
        """
            Used to POST a breed into the breed collection and to make sure it fits the schema.
        """
        if not request.is_json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Breed.json_schema())
        except ValidationError as exc:
            raise BadRequest(description=str(exc))
        group = Group.query.filter_by(name=request.json["group"]).first()

        if not group:
            # return ValueError("Group '{group}' does not exist".format(**request.json))
            return "Group does not exist", 400

        breed = Breed(group=group, name=request.json["name"])

        try:
            db.session.add(breed)
            db.session.commit()
        except IntegrityError:
            return "Breed already exists", 409

        return Response(
            status=201, headers={"Location": url_for(BreedItem, breed=breed)}
        )

class BreedItem(Resource):
    """
        Used to access specific breeds from the database.
    """
    def get(self, breed, group):
        """
            GETs a specific breed
        """
        if "404" in str(breed):
            return "", 404
        return Response(json.dumps(breed.serialize()), 200, mimetype=JSON)

    def put(self, breed):
        """
            Changes the values of an existing singular breed.
        """
        if not request.is_json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Breed.json_schema())
        except ValidationError as exc:
            raise BadRequest(description=str(exc)) from exc
        breed.deserialize(request.json)
        db.session.add(breed)
        db.session.commit()
        print(breed.serialize())
        return Response(json.dumps(breed.serialize()), 204, mimetype=JSON)

    def delete(self, breed):
        """
            DELETEs one single breed.
        """
        try:
            db.session.delete(breed)
            db.session.commit()
            return Response(status=204)
        except Exception:
            return "Breed not found!", 404
