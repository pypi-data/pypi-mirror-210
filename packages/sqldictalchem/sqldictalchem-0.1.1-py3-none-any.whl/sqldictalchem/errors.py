# vim: set fileencoding=utf-8 :
"""
~~~~~~
Errors
~~~~~~

"""



class SQLAlchemError(Exception):
    """Base class for SQLAlchem errors"""
    pass


class UnsupportedRelationError(SQLAlchemError):
    """Raised when a relation is not supported by asdict or fromdict.

    :ivar relation_key: Relation name
    """

    def __init__(self, relation_key):
        self.relation_key = relation_key

    def __str__(self):
        return "Relation '%r' is not supported" % (self.relation_key,)


class MissingRelationError(SQLAlchemError):
    """Raised when a relationship is missing

    :ivar relation_key: Relation name
    """

    def __init__(self, relation_key):
        self.relation_key = relation_key

    def __str__(self):
        return "Relation '%r' is not found" % (self.relation_key,)
