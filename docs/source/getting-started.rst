Getting Started
===============

Installation
------------

Install loc_authorities into a virtual environment with pip:

.. code-block:: console

    (.venv) $ pip install loc-authorities

Alternatively, install with uv:

.. code-block:: console

    $ uv add loc-authorities

Basic Usage
-----------

loc_authorities can be used to construct URIs from known identifiers

.. doctest::

    >>> from loc_authorities.api import LocAPI
    >>> LocAPI.uri_from_id('n79043402')
    'http://id.loc.gov/authorities/n79043402'
    >>> LocAPI.dataset_uri_from_id('n79043402')
    'http://id.loc.gov/authorities/names/n79043402'

You can also retrieve an identifier if you know the label

.. doctest::

    >>> loc = LocAPI()
    >>> loc.retrieve_label('Franklin, Benjamin, 1706-1790')
    'n79043402'

loc_authorities provides support for querying the `"suggest" API" <https://id.loc.gov/views/pages/swagger-api-docs/index.html#suggest-service-2.json>`_ provided by the Library of Congress. This performs a left-anchored search and will retrieve entries that start with the same character sequence as your query.

.. doctest::

    >>> suggest = loc.suggest('Franklin, Benjamin')
    >>> suggest[0].uri
    'http://id.loc.gov/authorities/names/n2015067702'
    >>> suggest[0].label
    'Franklin, Benjamin'

:meth:`LocAPI.search` queries the keyword search in the same manner. Both :meth:`LocAPI.search` and :meth:`LocAPI.suggest` accept an additional argument ``authority`` which lets you specify whether to query the Name Authority or Subject Header authority.

.. doctest::

    >>> search = loc.search('Benjamin Franklin', authority='names')
    >>> search[0].uri
    'http://id.loc.gov/authorities/names/n79043402'
    >>> search[0].label
    'Franklin, Benjamin, 1706-1790'

loc_authorities provides python classes that can represent single entities from the Linked Data Service

.. doctest::

    >>> from loc_authorities.api import LocEntity
    >>> entity = LocEntity('mp2013015202')
    >>> entity.authoritative_label
    rdflib.term.Literal('dancer', lang='en')
    >>> entity.dataset_uri
    'http://id.loc.gov/authorities/performanceMediums/mp2013015202'
    >>> entity.instance_of
    [rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Medium'), rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Authority'), rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#Concept')]

Additional wrappers are provided for the Name Authority and the Subject Authority. These subclass :class:`LocEntity` and inherit all its properties and methods, but contain additional properties to represent unique features of these authorities.

.. doctest::

    >>> from loc_authorities.api import NameEntity
    >>> name = NameEntity('n79043402')
    >>> name.authoritative_label
    rdflib.term.Literal('Franklin, Benjamin, 1706-1790')
    >>> name.birthdate
    rdflib.term.Literal('1706-01-17', datatype=rdflib.term.URIRef('http://id.loc.gov/datatypes/edtf'))
    >>> name.birthyear
    1706
    >>> name.deathdate
    rdflib.term.Literal('1790-04-17', datatype=rdflib.term.URIRef('http://id.loc.gov/datatypes/edtf'))
    >>> name.deathyear
    1790

Complex topics list their components as instances of either :class:`NameEntity` or :class:`SubjectEntity`

.. doctest::

    >>> from loc_authorities.api import SubjectEntity
    >>> subject = SubjectEntity('sh85054401')
    >>> subject.authoritative_label
    rdflib.term.Literal('German literature--Germany (East)', lang='en')
    >>> [type(s) for s in subject.components]
    [<class 'loc_authorities.api.SubjectEntity'>, <class 'loc_authorities.api.NameEntity'>]

Complex topics can contain temporal subjects that are valid but not yet indexed by Library of Congress. These entities have no URI and cannot be validated against the Library of Congress API, nor can we access RDF provided by the API. In these cases, we provide a dummy class :class:`TemporalEntity` to represent these as minimal RDF.

.. doctest::

    >>> from loc_authorities.api import SubjectEntity
    >>> subject = SubjectEntity('sh93000006')
    >>> subject.authoritative_label
    rdflib.term.Literal('Costa Rica--History--1986-', lang='en')
    >>> [type(s) for s in subject.components]
    [<class 'loc_authorities.api.NameEntity'>, <class 'loc_authorities.api.SubjectEntity'>, <class 'loc_authorities.api.TemporalEntity'>]
    >>> temporal = subject.components[2]
    >>> temporal.authoritative_label
    rdflib.term.Literal('1986-', lang='en')
    >>> temporal.instance_of
    [rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Temporal'), rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Authority')]

For complex topics that do not currently have identifiers in the Library of Congress Linked Data Service but are nonetheless valid, the class :class:`DummyComplexEntity` is provided.

.. doctest::

    >>> from loc_authorities.api import DummyComplexEntity
    >>> subject = DummyComplexEntity(['sh85003744', 'n79022911-781', '1733'])
    >>> subject.authoritative_label
    rdflib.term.Literal('Almanacs--Pennsylvania--1733', lang='en')
    >>> subject.instance_of
    [rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#ComplexSubject'), rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Authority')]
    >>> [type(s) for s in subject.components]
    [<class 'loc_authorities.api.SubjectEntity'>, <class 'loc_authorities.api.NameEntity'>, <class 'loc_authorities.api.TemporalEntity'>]
    >>> type(subject.dataset_uriref)
    <class 'rdflib.term.BNode'>