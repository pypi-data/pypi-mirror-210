# vim: set fileencoding=utf-8 :
"""
~~~~~~~
Classes
~~~~~~~

Contains :class:`DictableModel` that can be used as a base class for
:meth:`sqldictalchemy.ext.declarative_base`.

"""



from sqldictalchem import utils


class DictableModel(object):
    """Can be used as a base class for :meth:`sqldictalchemy.ext.declarative`

    Contains the methods :meth:`DictableModel.__iter__`,
    :meth:`DictableModel.asdict` and :meth:`DictableModel.fromdict`.

    :ivar sqldictalchem_exclude: List of properties that should always be \
            excluded.
    :ivar sqldictalchem_exclude_underscore: If True properties starting with an \
            underscore will always be excluded.
    :ivar sqldictalchem_fromdict_allow_pk: If True the primary key can be \
            updated by :meth:`DictableModel.fromdict`.
    :ivar sqldictalchem_asdict_include: List of properties that should always \
            be included when calling :meth:`DictableModel.asdict`
    :ivar sqldictalchem_fromdict_include: List of properties that should always \
            be included when calling :meth:`DictableModel.fromdict`

    """

    asdict = utils.asdict

    fromdict = utils.fromdict

    __iter__ = utils.iter
