"""
    Contains all the resources that are used to access the Facts model in the database.
"""


import json
from jsonschema import validate, ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, NotFound
from flask import Response, request, url_for
from flask_restful import Resource
from dogdict.models import Breed, Facts, db
from dogdict.constants import JSON


class FactCollection(Resource):
    """
        Used to access all the Facts in the database at once.
    """

    def get(self, group, breed):
        """
            GETs all the facts from the database
        """
        body = {"items": []}
        for db_fact in Facts.query.filter_by(breed=breed):
            item = db_fact.serialize(short_form=True)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self):
        """
            Used to validate a new fact against the correct Fact JSON schema
        """
        if not request.is_json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Facts.json_schema())
        except ValidationError as exc:
            raise BadRequest(description=str(exc))

        breed = Breed.query.filter_by(name=request.json["breed"]).first()

        if not breed:
            # return ValueError("Breed '{breed}' does not exist".format(**request.json))
            return "Breed does not exist", 404

        fact = Facts(breed=breed, fact=request.json["fact"])

        db.session.add(fact)
        db.session.commit()
        """
        More information about url_for comment in course lovelace 
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/flask-api-project-layout/#avoiding-circular-imports
        """
        return Response(
            status=201, headers={"Item": url_for("api.factcollection",
                                                 fact=fact)}  # have to change this
        )


class FactItem(Resource):
    """
        Used to access a singular fact item
    """
    def get(self, group, breed, fact):
        print(fact)
        if fact == None:
            return Response("Fact not found", 404)
        body = {"items": [fact.fact]}
        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, group, breed, fact):
        if not request.is_json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Facts.json_schema_for_put())
        except ValidationError as exc:
            raise BadRequest(description=str(exc)) from exc
        fact.deserialize(request.json)
        db.session.add(fact)
        db.session.commit()
        return Response(json.dumps({"fact": fact.fact}), 204, mimetype=JSON)

    def delete(self, fact, group, breed):
        """
            Deletes a single specific fact from the database.
        """
        try:
            db.session.delete(fact)
            db.session.commit()
            return Response(f"Successfully deleted fact {fact}", status=204)
        except:
            return "Fact not found!", 404
