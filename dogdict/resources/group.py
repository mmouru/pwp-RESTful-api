"""
    Contains all the resources that are used to access the Facts model in the database.
"""

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from dogdict.models import Group, Breed, db
from dogdict.constants import JSON
from dogdict.utils import check_for_space
from dogdict.resources.mason import MasonBuilder


class GroupBuilder(MasonBuilder):
    """
    Creates link relations for the Group resource.
    These include POST, GET and PUT methods.
    """

    def add_control_all_groups(self):
        """
            Used to add control to all groups methods
        """
        self.add_control(
            "groups:groups-all",
            url_for("api.groupcollection"),
            title="All groups",
            method="GET",
        )

    def add_control_add_groups(self):
        """
            Used to add control to all groups add method
        """
        self.add_control_post(
            "groups:add-group",
            "Add a new group",
            url_for("api.groupcollection"),
            Group.json_schema(),
        )

    def add_control_edit_groups(self, group_name):
        """
            Used to add control to all groups aput method
        """
        self.add_control_put(
            "group:edit",
            url_for("api.groupitem", group=group_name),
            Group.json_schema(),
        )


class GroupCollection(Resource):
    """
    Used to access all of the Groups in the DB at once.
    """

    def get(self, group=None):
        """
        GETs all the groups in the database (currently their names)
        """
        body = GroupBuilder(items=[])
        body.add_namespace("groups", "/api/groups/")
        body.add_control("self", href=url_for("api.groupcollection"))
        body.add_control_add_groups()
        body.add_control_all_groups()

        for db_group in Group.query.all():
            db_group_serialised = db_group.serialize(short_form=False)
            print("DB GROUP SERIALISED", db_group_serialised)
            item = {
                "name": db_group_serialised["name"],
                "id": db_group_serialised["id"],
                "breeds": [],
            }
            # Get all breeds that are under group
            for breed in Breed.query.filter_by(group=db_group).all():
                item["breeds"].append(breed.name)

            item["@controls"] = {
                "self": {"href": url_for("api.groupitem", group=db_group.name)}
            }
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self):
        """
        Used to POST a new Group object and validate it against the Group
        JSON schema.
        """
        if not request.is_json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Group.json_schema())
        except ValidationError as exc:
            raise BadRequest(description=str(exc))

        group = Group(name=request.json["name"])

        try:
            db.session.add(group)
            db.session.commit()
        except IntegrityError:
            #raise Conflict(f"Group with name '{request.json['name']}' already exists.")
            return Response(
                status=409
            )

        uri_name = check_for_space(group.name)

        return Response(
            status=201,
            headers={
                "Item": url_for("api.groupitem", group=group),
                "Location": url_for("api.groupitem", group=uri_name),
            },
        )


class GroupItem(Resource):
    """
    Used to access a specific group
    """

    def get(self, group):
        """
        GETs a specific groups information from the DB (name only)
        """
        print("THIS IS GROUPITEM:", group)
        body = GroupBuilder(items=[])
        body.add_namespace("group", f"/api/groups/{group.name}/")
        body.add_control("self", href=url_for("api.groupitem", group=group.name))
        body.add_control_edit_groups(group.name)

        group = Group.query.filter_by(name=group.name).first()
        item = {"name": group.name, "breeds": []}
        for breed in Breed.query.filter_by(group=group).all():
            uri_name = check_for_space(breed.name)

            item["breeds"].append(breed.name)

            item["@controls"] = {
                f"{breed.name}": {
                    "href": url_for(f"api.groupitem", group=group.name + "/" + uri_name)
                }
            }
        body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, group):
        """
        Used to change the name of a specific group from the database.
        """
        if not request.is_json:
            return "Unsupported Media Type!", 415
        try:
            validate(request.json, Group.json_schema())

        except ValidationError as exc:
            raise BadRequest(description=str(exc)) from exc

        group = Group.query.filter_by(name=group.name).first()
        group.deserialize(request.json)

        db.session.add(group)
        db.session.commit()

        uri_name = check_for_space(group.name)

        return Response(
            status=204,
            headers={
                "Item": url_for("api.groupitem", group=group),
                "Location": url_for("api.groupitem", group=uri_name),
            },
        )
