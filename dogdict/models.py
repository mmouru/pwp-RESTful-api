"""
    All db model definitions and a cli command for initialzing the db for testing
"""

from dogdict import db


class Group(db.Model):
    """
    Group is an object that is used to categorize breeds.
    Example: Australian Terrier belongs to the Terrier group of breeds.

    Each Group is unique and must have a name.
    """

    id = db.Column(db.Integer, primary_key=True)
    # must be unique
    name = db.Column(db.String(64), unique=True, nullable=False)

    # creates a connection from Group -> Breed
    breeds = db.relationship("Breed", back_populates="group")

    def serialize(self, short_form=True):
        """
        Used to serialize the Group Python model objects,
        since they can't directly be serialized with json.dumps
        """
        if short_form:
            return {"name": self.name, "id": self.id}

        # tämän voisi tehdä tekemään listan roduista joita db:ssä
        breeds_amount = Breed.query.filter_by(group=self).count()

        return {"name": self.name, "breeds_in_db": breeds_amount, "id": self.id}

    def deserialize(self, doc):
        """
        Used to deserialize the a dictionary into a suitable model instance.
        """
        self.name = doc["name"]

    @staticmethod
    def json_schema():
        """
        defines the JSON format of the Group object and describes the values
        """
        schema = {"type": "object", "required": ["name"]}
        props = schema["properties"] = {}
        props["name"] = {"description": "Group's unique name", "type": "string"}
        return schema


class Characteristics(db.Model):
    """
    Each characteristics can only have an 1 to 1 connection to a breed.
    This object characterises the breed and contains values such as
    life span, coat length and the amount of daily exercise the breed requires (in hours).

    There can be multiple similar characteristics, they are only separated by the ID.
    """

    id = db.Column(db.Integer, primary_key=True)
    life_span = db.Column(
        db.Integer,
        db.CheckConstraint("life_span>5"),
        db.CheckConstraint("life_span<25"),
        nullable=False,
    )
    coat_length = db.Column(
        db.Float, db.CheckConstraint("coat_length<=1"), nullable=True
    )
    exercise = db.Column(
        db.Float,
        db.CheckConstraint("exercise>0"),
        db.CheckConstraint("exercise<5"),
        nullable=True,
    )

    # creates a connection between characteristics and breed
    in_breed = db.relationship("Breed", back_populates="characteristics")

    def serialize(self, short_form=False):
        """
        Used to serialize the Characteristics Python model objects,
        since they can't directly be serialized with json.dumps
        """
        if short_form:
            return {
                "coat_length": self.coat_length,
                "life_span": self.life_span,
                "exercise": self.exercise,
            }

        return {
            "breed": [breed.name for breed in self.in_breed],
            "char_id": self.id,
            "coat_length": self.coat_length,
            "life_span": self.life_span,
            "exercise": self.exercise,
        }

    def deserialize(self, doc):
        """
        Used to deserialize the doc object to assign
        new values to characteristics
        """
        # Martyn muutoksia, halutaanko nämä vai toimiiko self.char paremmin?
        self.life_span = doc["life_span"]
        self.coat_length = doc["coat_length"]
        self.exercise = doc["exercise"]

    @staticmethod
    def json_schema():
        """
        defines the JSON format of the Characteristics object and describes the values
        """
        schema = {"type": "object", "required": ["life_span"]}
        props = schema["properties"] = {}
        props["life_span"] = {"description": "Lifespan of a breed", "type": "number"}
        return schema

    @staticmethod
    def json_schema_for_put():
        """
        Defines different schema where in_breed is not needed for PUT method,
        but all others are
        """
        schema = {
            "type": "object",
            "required": ["coat_length", "life_span", "exercise"],
        }
        props = schema["properties"] = {}
        props["life_span"] = {"description": "Lifespan of a breed", "type": "number"}
        props["exercise"] = {
            "description": "Exercise needs of dog in scale 0-1",
            "type": "number",
        }
        props["coat_length"] = {
            "description": "Breeds coat length in scale 0-1",
            "type": "number",
        }
        return schema


class Facts(db.Model):
    """
    Facts contain short information about breeds such as: "____ is a small dog"
    Facts can be non unique, but each fact can only belong to one breed.
    """

    id = db.Column(db.Integer, primary_key=True)
    fact = db.Column(db.String(128), nullable=False)

    # creates a connection from Facts -> Breed
    breed_id = db.Column(db.Integer, db.ForeignKey("breed.id", ondelete="CASCADE"))
    breed = db.relationship("Breed", back_populates="facts")

    def serialize(self, short_form=False):
        """
        Used to serialize the Facts Python model objects,
        since they can't directly be serialized with json.dumps
        """
        if short_form:
            return {"fact": self.fact, "fact_id": self.id}
        return {"fact": self.fact, "breed": self.breed_id, "id": self.id}

    def deserialize(self, doc):
        """
        Used to deserialize the Facts object and extract the wanted data
        Returns one specific fact currently, used to change fact from given body.
        """
        self.fact = doc["fact"]

    @staticmethod
    def json_schema():
        """
        defines the JSON format of the Facts object and describes the values
        """
        schema = {"type": "object", "required": ["fact", "breed"]}
        props = schema["properties"] = {}
        props["fact"] = {"description": "Fact about a breed", "type": "string"}
        props["breed"] = {"description": "Breed regarding the fact", "type": "string"}
        return schema

    @staticmethod
    def json_schema_postput():
        """
        this is facts json.schema for post which does not require breed in the request body!
        (it is in url already) for example api/Terrier/Laurin%20Terrier/facts/ already contains
        Laurin%20Terrier
        """
        schema = {"type": "object", "required": ["fact"]}
        props = schema["properties"] = {}
        props["fact"] = {"description": "Fact about a breed", "type": "string"}
        return schema


class Breed(db.Model):
    """
    Each breed is unique and can only belong to one group.
    Each breed has characteristics that give information about the breeds. 1 to 1 Relationship.
    Each breed can have multiple facts.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    char_id = db.Column(
        db.Integer, db.ForeignKey("characteristics.id", ondelete="CASCADE")
    )

    # creates a connection from Breed -> Group
    group_id = db.Column(db.Integer, db.ForeignKey("group.id", ondelete="CASCADE"))
    group = db.relationship("Group", back_populates="breeds")

    # creates a connection from Breed -> Characteristics
    characteristics = db.relationship(
        "Characteristics", back_populates="in_breed", uselist=False
    )

    # creates a connection from Breed -> Facts
    facts = db.relationship("Facts", back_populates="breed")

    def serialize(self, short_form=False):
        """
        Used to serialize the Breed Python model objects,
        since they can't directly be serialized with json.dumps.

        Currently short_form doesn't affect anything.
        """
        doc = {"name": self.name, "id": self.id}
        if not short_form:
            doc["group"] = self.group.serialize()
            doc["facts"] = [fact.fact for fact in self.facts]
            if self.characteristics:
                doc["characteristics"] = {
                    "char_id": self.characteristics.id,
                    "life_span": self.characteristics.life_span,
                    "coat_length": self.characteristics.coat_length,
                    "exercise": self.characteristics.exercise,
                }
        return doc

    def deserialize(self, doc):
        """
        Used to deserialize the a dictionary into a suitable model instance.
        """
        self.name = doc["name"]

    @staticmethod
    def json_schema():
        """
        defines the JSON format of the Breed object and describes the values
        """
        schema = {"type": "object", "required": ["name"]}
        props = schema["properties"] = {}
        props["name"] = {"description": "Breeds unique name", "type": "string"}
        #props["group"] = {"description": "Name of the breed's group", "type": "string"}
        return schema
