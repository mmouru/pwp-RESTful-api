"""
    Contains all the resources that are used to access the Breed model in the database.
"""
import json
import os
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from dogdict.models import Breed, Characteristics, Group, Facts, db
from dogdict.constants import JSON
from dogdict.utils import check_for_space
from flasgger import Swagger
from dogdict.resources.mason import MasonBuilder


class BreedBuilder(MasonBuilder):
    """
    Creates link relations for the Breed resource.
    These include POST, GET, DELETE and PUT methods.
    """

    def add_control_all_breeds(self, group):
        """
        Adds control to all methods related to breed
        """
        self.add_control(
            "breeds:breeds-all",
            url_for("api.breedcollection", group=group.name),
            title="All breeds",
            method="GET",
        )

    def add_control_delete_breed(self, breed, group):
        """
        Adds control to breed delete method
        """
        uri_name = check_for_space(breed)
        self.add_control(
            "breed:delete",
            url_for("api.breeditem", breed=uri_name, group=group),
            method="DELETE",
        )

    def add_control_add_breeds(self, group):
        """
        Adds control to breed post method
        """
        self.add_control_post(
            "breeds:add-breed",
            "Add a new breed and connects it to an existing group",
            url_for("api.breedcollection", group=group.name),
            Breed.json_schema(),
        )

    def add_control_edit_breed(self, breed, group):
        """
        Adds control to breed put method
        """
        uri_name = check_for_space(breed)
        self.add_control_put(
            "breed:edit",
            url_for("api.breeditem", breed=uri_name, group=group),
            Breed.json_schema(),
        )


class BreedCollection(Resource):
    """
    Used to access multiple breeds at once.
    """

    # @swag_from("../doc/breedcollection/breeds_get.yml")

    def get(self, group):
        """
        Used to access ALL the breeds at once.
        """
        print(group.name, "MARTTIII")
        body = BreedBuilder(items=[])
        body.add_namespace("breeds", "/api/groups/<group:group>/breeds/")
        print(group.name)
        body.add_control("self", href=url_for("api.breedcollection", group=group.name))
        body.add_control_add_breeds(group=group)
        body.add_control_all_breeds(group=group)

        for db_breed in Breed.query.filter_by(group=group):
            db_breed_serialised = db_breed.serialize()
            print("DB BREED SERIALISED", db_breed_serialised)
            item = {
                "name": db_breed_serialised["name"],
                "id": db_breed_serialised["id"],
            }

            uri_name = check_for_space(db_breed.name)

            item["@controls"] = {
                "self": {
                    "href": url_for(
                        "api.breeditem", breed=uri_name, group=db_breed.group.name
                    )
                }
            }
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self, group):
        """
        Used to POST a breed into the breed collection and to make sure it fits the schema.
        """
        
        if not request.is_json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Breed.json_schema())
        except ValidationError as exc:
            raise BadRequest(description=str(exc))
        #group = Group.query.filter_by(name=request.json["group"]).first()

        #if not group:
            # return ValueError("Group '{group}' does not exist".format(**request.json))
         #   return "Group does not exist", 400

        breed = Breed(group=group, name=request.json["name"])

        try:
            db.session.add(breed)
            db.session.commit()
        except IntegrityError:
            return "Breed already exists", 409
        
        uri_name = check_for_space(breed.name)

        return Response(
            status=201,
            headers={
                "Location": url_for(
                    "api.breeditem", breed=uri_name, group=group.name
                )
            },
        )


class BreedItem(Resource):
    """
    Used to access specific breeds from the database.
    """

    def get(self, breed, group):
        """
        GETs a specific breed
        """
        body = BreedBuilder(items=[])

        if "404" in str(breed):
            return f"No such breed found in {group.name}", 404

        uri_name = check_for_space(breed.name)

        print("GOT HERE!", uri_name, group.name)

        body.add_namespace("breeds", f"/api/groups/{group.name}/breeds/{uri_name}/")
        body.add_control(
            "self", href=url_for("api.breeditem", breed=uri_name, group=group.name)
        )

        body.add_control_edit_breed(breed.name, group.name)
        body.add_control_delete_breed(breed.name, group.name)
        breed = Breed.query.filter_by(id=breed.id).first()

        item = breed.serialize()

        print("DID WE GET HERE!?")

        item["@controls"] = {
            "self": {"href": url_for("api.breeditem", breed=uri_name, group=group.name)}
        }
        body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, breed, group):
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
        
        uri_name = check_for_space(breed.name)

        return Response(
            status=204,
            headers={
                "Location": url_for("api.breeditem", breed=uri_name, group=group.name)
            },
        )

    def delete(self, breed, group):
        """
        DELETEs one single breed.
        """
        try:
            breed = Breed.query.filter_by(id=breed.id).first()
            characteristics = Characteristics.query.filter_by(id=breed.char_id).first()
            facts = Facts.query.filter_by(breed_id=breed.id)
            if characteristics:
                db.session.delete(characteristics)
                db.session.commit()
            if facts:
                for fact in facts:
                    db.session.delete(fact)
                db.session.commit()
            db.session.delete(breed)
            db.session.commit()
            return Response(status=204)
        except Exception:
            return "Breed not found!", 404
