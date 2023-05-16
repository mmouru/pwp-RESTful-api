"""
    Contains all the resources that are used to access the Facts model in the database.
"""


import json
from jsonschema import validate, ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from flask import Response, request, url_for
from flask_restful import Resource
from dogdict.models import Facts, db
from dogdict.constants import JSON
from dogdict.utils import check_for_space
from dogdict.resources.mason import MasonBuilder


class FactBuilder(MasonBuilder):
    """
    Creates link relations for the Facts resource.
    These include POST, GET and DELETE methods.
    """

    def add_control_all_facts(self, group, breed):
        """
        adds control to all facts methods
        """
        uri_name = check_for_space(breed)
        self.add_control(
            "facts:facts-all",
            url_for("api.factcollection", group=group, breed=uri_name),
            title="All facts",
            method="GET",
        )

    def add_control_add_facts(self, group, breed):
        """
        adds control to facts add method (post)
        """
        uri_name = check_for_space(breed)
        self.add_control_post(
            "facts:add-fact",
            "Add a new fact and connects it to an existing breed",
            url_for("api.factcollection", group=group, breed=uri_name),
            Facts.json_schema(),
        )

    def add_control_delete_facts(self, fact_id, breed, group):
        """
        adds control to facts DELETE method
        """
        uri_name = check_for_space(breed)
        print("this is add control delete fact:", fact_id, breed, group)
        self.add_control(
            "fact:delete",
            url_for("api.factitem", fact=fact_id, breed=uri_name, group=group),
            method="DELETE",
        )

    def add_control_edit_facts(self, fact_id, breed, group):
        """
        adds control to facts PUT method
        """
        uri_name = check_for_space(breed)
        self.add_control_put(
            "fact:edit",
            url_for("api.factitem", fact=fact_id, breed=uri_name, group=group),
            Facts.json_schema()
        )


class FactCollection(Resource):
    """
    Used to access all the Facts in the database at once.
    """

    def get(self, group, breed):
        """
        GETs all the facts from the database
        """
        body = FactBuilder(items=[])
        body.add_namespace("breeds", "/api/groups/<group:group>/breeds/<breed:breed>/facts/")

        uri_name = check_for_space(breed.name)
        
        body.add_control("self", href=url_for("api.factcollection", breed=uri_name, group=group.name))
        body.add_control_all_facts(group.name, uri_name)
        body.add_control_add_facts(group.name, uri_name)

        for db_fact in Facts.query.filter_by(breed=breed):
            item = db_fact.serialize(short_form=True)
            body["items"].append(item)
            item["@controls"] = {
                "self": {
                    "href": url_for(
                        "api.factitem",
                        breed=uri_name,
                        group=group.name,
                        fact=db_fact.id,
                    )
                }
            }
        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self, group, breed):
        """
        Used to validate a new fact against the correct Fact JSON schema
        """

        if not request.is_json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Facts.json_schema_postput())
        except ValidationError as exc:
            raise BadRequest(description=str(exc))

        uri_name = check_for_space(breed.name)

        body = {"items": []}
        for db_fact in Facts.query.filter_by(breed=breed):
            item = db_fact.serialize(short_form=True)
            body["items"].append(item)

        # Check if the new fact value is already present in the list
        if any(item["fact"] == request.json["fact"] for item in body["items"]):
            return "The fact is already connected to the breed!", 409

        fact = Facts(breed=breed, fact=request.json["fact"])

        db.session.add(fact)
        db.session.commit()

        uri_id = fact.id

        return Response(
            status=201,
            headers={
                "Item": url_for(
                    "api.factcollection", fact=fact, group=group.name, breed=uri_name
                ),
                "Location": url_for(
                    "api.factitem", fact=uri_id, group=group.name, breed=breed.name
                ),
            },
        )


class FactItem(Resource):
    """
    Used to access a singular fact item
    """

    def get(self, group, breed, fact):
        """
        Used to access a singular fact item  with GET
        """
        body = FactBuilder(items=[])
    
        uri_name = check_for_space(breed.name)

        body.add_namespace("fact", f"/api/groups/{group.name}/breeds/{uri_name}/facts/{fact.id}")

        body.add_control(
            "self",
            href=url_for(
                "api.factitem", breed=uri_name, group=group.name, fact=fact.id
            ),
        )
        print("HERE WE GOO ", fact.id, uri_name, group.name)
        body.add_control_delete_facts(fact.id, uri_name, group.name)
        body.add_control_edit_facts(fact.id, uri_name, group.name)

        #body = {"items": [fact.fact]}
        body["items"] = fact.fact
        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, group, breed, fact):
        """
        Used to change a singular fact item  with PUT
        """
        if not request.is_json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Facts.json_schema_postput())
        except ValidationError as exc:
            raise BadRequest(description=str(exc)) from exc
        fact.deserialize(request.json)

        db.session.add(fact)
        db.session.commit()
        return Response(json.dumps({"fact": fact.fact}), 204, mimetype=JSON)

    def delete(self, fact, group=None, breed=None):
        """
        Deletes a single specific fact from the database.
        """
        db.session.delete(fact)
        db.session.commit()
        return Response(f"Successfully deleted fact {fact}", status=204)
