from rdflib import Namespace
from urllib.parse import urljoin
from functools import cached_property
from typing import Literal

import rdflib
import requests
from rdflib.namespace import RDF

import logging


logger = logging.getLogger(__name__)


MADS_NS = Namespace('http://www.loc.gov/mads/rdf/v1#')


class LocAPI(object):
    """Wrapper for Library of Congress API.

    https://id.loc.gov/
    """

    # base url for URIs and API calls
    uri_base = 'http://id.loc.gov/authorities/'
    # Names Authorities base
    lcnaf_base = 'http://id.loc.gov/authorities/names/'
    # Subject Authorities base
    lcsh_base = 'http://id.loc.gov/authorities/subjects/'
    # Children's Subject Headings base
    lcsj_base = 'http://id.loc.gov/authorities/childrensSubjects/'
    # Medium of Performance Thesaurus for Music base
    lcmpt_base = 'http://id.loc.gov/authorities/performanceMediums/'
    # Demographic Group Terms base
    lcdgt_base = 'http://id.loc.gov/authorities/demographicTerms/'
    # Thesaurus for Graphic Materials base
    tgm_base = 'http://id.loc.gov/vocabulary/graphicMaterials/'
    # AFS Ethnographic Thesaurus base
    afset_base = 'http://id.loc.gov/vocabulary/ethnographicTerms/'
    # Genre/Form Terms base
    lcgft_base = 'http://id.loc.gov/authorities/genreForms/'
    # Real world entity base (used for queries)
    rwo_base = 'http://id.loc.gov/rwo/agents/'

    @classmethod
    def uri_from_id(cls, loc_id):
        """Generate a URL for performing initial queries"""
        return urljoin(cls.uri_base, loc_id)

    @classmethod
    def dataset_uri_from_id(cls, loc_id):
        """Generate a URI for RDF triples based on LoC dataset"""
        if loc_id.startswith('n'):
            return urljoin(cls.lcnaf_base, loc_id)
        elif loc_id.startswith('sh'):
            return urljoin(cls.lcsh_base, loc_id)
        elif loc_id.startswith('sj'):
            return urljoin(cls.lcsj_base, loc_id)
        elif loc_id.startswith('mp'):
            return urljoin(cls.lcmpt_base, loc_id)
        elif loc_id.startswith('dg'):
            return urljoin(cls.lcdgt_base, loc_id)
        elif loc_id.startswith('tgm'):
            return urljoin(cls.tgm_base, loc_id)
        elif loc_id.startswith('afset'):
            return urljoin(cls.afset_base, loc_id)
        elif loc_id.startswith('gf'):
            return urljoin(cls.lcgft_base, loc_id)
        else:
            # Throw error if URL malformed
            raise ValueError("""
            The ID does not conform to supported ID formats.
            Please verify the ID is correct.
            """)

    @classmethod
    def rwo_uri_from_id(cls, loc_id):
        """Generate RWO URI for linked data queries"""
        return urljoin(cls.rwo_base, loc_id)

    def suggest(self, query, authority: Literal[None, 'names', 'subjects'] = None):
        """Query LoC's suggest service API using left-anchored search. Returns
        a list of results, or an empty list for no results or an error.

        Querying the older Suggest 1.0 is not implemented.

        :param query: Search query (string)
        :param authority: LoC authority to search. Supports names or subjects
        """

        # Note dropdown search language from API docs. What do we need to do to implement this?
        if authority:
            base_url = urljoin(self.uri_base, f'{authority}/')
        else:
            # BUG: If no authority provided, can return results from authorities that are not
            # implemented (e.g. BIBFRAME)
            base_url = 'http://id.loc.gov/'

        suggest_param = 'suggest2'

        query_url = urljoin(base_url, suggest_param)
        # TODO: incorporate more parameters?
        params = {'q': query}
        response = requests.get(query_url, params=params)
        if response.status_code == requests.codes.ok:
            data = SRUResult(response.json())
            if data.total_results > 0:
                return data.records

        response.raise_for_status()

        return []

    # not very DRY since this largely repeats logic of suggest method
    # could these two be combined and search param for search type be provided?
    def search(self, query, authority: Literal[None, 'names', 'subjects']):
        """Query LoC's suggest service API using keyword search. Returns a
        list of search results, or an empty list for an error.

        :param query: Search query (string)
        :param authority: Authority to search ('names' or 'subjects')
        """
        # keyword search needs to require an authority, because otherwise
        # it returns many results from the resources authority
        query_url = f'{self.uri_base}{authority}/suggest2'

        params = {'q': query, 'searchtype': 'keyword'}
        response = requests.get(query_url, params=params)
        if response.status_code == requests.codes.ok:
            data = SRUResult(response.json())
            if data.total_results > 0:
                return data.records

        response.raise_for_status()

        return []

    def retrieve_label(self, label, authority=None):
        """Query LoC's label retrieval API to return a URI from
        a known label

        :param label: The label to retrieve (string)
        :param authority: the name of the authority to query. Defaults to `None`
        """

        # TODO: Allow authorities to be passed in query
        accepted_authorities = [
            'subjects',
            'childrensSubjects',
            'performanceMediums',
            'demographicTerms',
            'graphicMaterials',
            'ethnographicTerms',
            'names',
            'genreForms',
        ]
        if authority is None:
            base_url = 'https://id.loc.gov/authorities/label/'
        else:
            if authority in accepted_authorities:
                base_url = f'https://id.loc.gov/authorities/{authority}/label/'
            else:
                raise ValueError("""The authority supplied is not accepted. Please choose:
                - subjects
                - childrensSubjects
                - performanceMediums
                - demographicTerms
                - graphicMaterials
                - ethnographicTerms
                - names
                - genreForms
                """)
        query_url = urljoin(base_url, label)
        response = requests.get(query_url, allow_redirects=False)
        # successful query should return a redirect
        if response.status_code == 302:
            uri = response.headers['x-uri']
            identifier = uri.split('/')[-1]
            return identifier

        elif response.status_code == 404:
            logger.warning(f'404 returned for {label}.')
            return None
        else:
            return None


# Question: Does each dataset need its own representation?
class LocEntity(object):
    """Object to represent single LoC entity

    :param loc_id: LoC identifier (string)
    """

    def __init__(self, loc_id):
        # probably need to identify canonical ID from LoC dataset
        self.loc_id = loc_id
        self.uri = LocAPI.uri_from_id(loc_id)
        self.dataset_uri = LocAPI.dataset_uri_from_id(loc_id)

    @property
    def uriref(self):
        """LoC URI reference as instance of :class:`rdflib.URIRef`"""
        # Consider deprecating this - unless the instance can't be matched to a LoC
        # dataset, this is generally only used in HTTP requests, which should also
        # resolve with the dataset URI
        return rdflib.URIRef(self.uri)

    @property
    def dataset_uriref(self):
        """LoC URI reference that includes LCNAF dataset
        marker as instance of :class:`rdflib.URIRef`"""
        return rdflib.URIRef(self.dataset_uri)

    @cached_property
    def rdf(self):
        """LoC data for this entity as :class:`rdflib.Graph`"""
        graph = rdflib.Graph()
        # try to query dataset URI first if it exists - sometimes plain URI throws an error
        if self.dataset_uri:
            response = requests.get(
                self.dataset_uri, headers={'Accept': 'application/rdf+xml'}
            )
        else:
            # not covered by test suite
            response = requests.get(self.uri, headers={'Accept': 'application/rdf+xml'})
        response.raise_for_status()  # raise HTTPError on bad requests
        graph.parse(data=response.text, format='xml')

        return graph

    @property
    def authoritative_label(self):
        """Authoritative entity label in English"""
        labels = self.rdf.objects(self.dataset_uriref, MADS_NS.authoritativeLabel)
        # Sometimes label is marked "en", sometimes no label
        for label in labels:
            if label.language == 'en' or label.language is None:
                return label

    @property
    def scheme_membership(self):
        """LoC scheme that represents this entity as instance of
        :class:`rdflib.URIRef`"""
        # TODO: In theory, this can value can be multiple. Find example
        return self.rdf.value(self.dataset_uriref, MADS_NS.isMemberOfMADSScheme)

    @property
    def instance_of(self):
        """Linked Data authorities that describe this entity as
        list of instances of :class:`rdflib.URIRef`"""
        instances = self.rdf.objects(self.dataset_uriref, RDF.type)
        return [i for i in instances]


class NameEntity(LocEntity):
    """Object to represent single entity from the
    LoC Name Authority File. Inherits :class:`LocEntity`.

    :param loc_id: LoC identifier (string)
    """

    @property
    def rwo_uri(self):
        return LocAPI.rwo_uri_from_id(self.loc_id)

    @property
    def rwo_uriref(self):
        """LoC RWO URI reference as instance of
        :class:`rdflib.URIRef`"""
        return rdflib.URIRef(self.rwo_uri)

    # chronological data
    # some ancient authors use "active" or "fl." instead of life dates
    # should be implemented in future work package
    @property
    def birthdate(self):
        """MADS birthday as :class:`rdflib.term.Literal`"""
        return self.rdf.value(self.rwo_uriref, MADS_NS.birthDate)

    @property
    def deathdate(self):
        """MADS deathdate as :class:`rdflib.term.Literal`"""
        return self.rdf.value(self.rwo_uriref, MADS_NS.deathDate)

    @property
    def birthyear(self):
        """birth year as `int`"""
        if self.birthdate:
            return self.year_from_edtf(str(self.birthdate))

    @property
    def deathyear(self):
        """death year as `int`"""
        if self.deathdate:
            return self.year_from_edtf(str(self.deathdate))

    @classmethod
    def year_from_edtf(cls, date):
        """Return just the year from EDTF date. Expects a string,
        returns an integer. Normalizes uncertain years. Supports
        negative dates. No support for partially unknown years."""
        negative = False
        # if the date starts with a dash, flag negative and delete
        if date.startswith('-'):
            date = date[1:]
            negative = True
        # need more robust parsing here for approximate dates
        edtf_year = date.split('-')[0]
        edtf_chars = ['~', '?', '%']
        for c in edtf_chars:
            edtf_year = edtf_year.replace(c, '')
        edtf_year = int(edtf_year)
        if negative:
            return -edtf_year
        return edtf_year


class TemporalEntity(LocEntity):
    """Container to representa temporal subject. Most temporal subjects
    are not indexed in LoC, so this container provides minimal RDF to capture
    the schema. Temporal entities that are indexed should be instantiated
    as :class:`SubjectEntity`.

    Overrides :class:`LocEntity` methods to return `None` where the property
    does not exist.

    :param label: the text of the authoritative label (string)
    """

    def __init__(self, label):
        self.label = label

    @property
    def uriref(self):
        """LoC URI reference as instance of :class:`rdflib.URIRef`"""
        return None

    @property
    def dataset_uriref(self):
        """LoC URI reference that includes LCNAF dataset
        marker as instance of :class:`rdflib.URIRef`"""
        return None

    @property
    def rdf(self):
        """Basic linked data for this entity as :class:`rdflib.Graph`"""
        graph = rdflib.Graph()
        bn = rdflib.BNode()
        graph.add(
            (bn, MADS_NS.authoritativeLabel, rdflib.Literal(self.label, lang='en'))
        )
        graph.add((bn, RDF.type, MADS_NS.Temporal))
        graph.add((bn, RDF.type, MADS_NS.Authority))

        return graph

    @property
    def authoritative_label(self):
        """Authoritative entity label in English"""
        label_literal = rdflib.Literal(self.label, lang='en')
        return label_literal

    @property
    def scheme_membership(self):
        """Since temporal entities are not indexed, returns None."""
        return None


class SubjectEntity(LocEntity):
    """Object to represent single entity from the LoC
    Subject Headings authority. Inherits :class:`LocEntity`.

    :param loc_id: LoC identifier (string)
    """

    @property
    def components(self):
        """Components for LoC Complex subjects. If subject is
        complex, returns a list of :class:`SubjectEntity`
        and :class:`NameEntity` objects. If subject is simple,
        returns :class:`TemporalEntity`.
        """
        # container list for results
        components = []
        # get blank node that identifies collectionList
        c_bnode = self.rdf.value(self.dataset_uriref, MADS_NS.componentList)
        # get rdflib.collection.Collection representing components
        components_rdf = rdflib.collection.Collection(self.rdf, c_bnode)
        for c in components_rdf:
            if isinstance(c, rdflib.URIRef):
                uri = c.split('/')[-1]
                if uri.startswith('n'):
                    entity = NameEntity(uri)
                    components.append(entity)
                elif uri.startswith('sh'):
                    entity = SubjectEntity(uri)
                    components.append(entity)
                else:
                    # Not covered by test suite
                    logger.warning(f'Unrecognized schema for URI: {c}')
            else:
                # Assume this is a temporal entity
                label = self.rdf.value(c, MADS_NS.authoritativeLabel)
                entity = TemporalEntity(str(label))
                components.append(entity)

        if len(components) > 0:
            return components
        else:
            return None


class DummyComplexEntity(SubjectEntity):
    """Container to represent a complex topic that does not
    have a URI but contains all valid subcomponents.

    :param components: URIs or tempoal labels for subcomponents (list)
    """

    def __init__(self, components):
        self.initial_components = []
        for component in components:
            # should not need regex since labels should not start with lowercase
            if component.startswith('n'):
                ent = NameEntity(component)
                self.initial_components.append(ent)
            elif component.startswith('sh'):
                ent = SubjectEntity(component)
                self.initial_components.append(ent)
            else:
                # assume temporal entity
                ent = TemporalEntity(component)
                self.initial_components.append(ent)

    @property
    def uriref(self):
        """LoC URI reference as instance of :class:`rdflib.URIRef`"""
        return None

    @cached_property
    def dataset_uriref(self):
        """LoC URI reference that includes LCNAF dataset
        marker as instance of :class:`rdflib.BNode`

        For queries to work, this is a cached property.
        It persists during one session, but not between sessions.
        """
        return rdflib.BNode()

    @cached_property
    def rdf(self):
        """Basic linked data for this entity as :class:`rdflib.Graph`"""
        graph = rdflib.Graph()
        bn = self.dataset_uriref
        graph.add((bn, MADS_NS.authoritativeLabel, self.authoritative_label))
        graph.add((bn, RDF.type, MADS_NS.ComplexSubject))
        graph.add((bn, RDF.type, MADS_NS.Authority))
        # components
        components_bn = rdflib.BNode()
        graph.add((bn, MADS_NS.componentList, components_bn))
        for n, component in enumerate(self.components):
            if component.dataset_uriref is None:
                uri = rdflib.BNode()
            else:
                uri = component.dataset_uriref
            graph.add((components_bn, RDF.first, uri))
            for instance in component.instance_of:
                graph.add((uri, RDF.type, instance))
            graph.add((uri, MADS_NS.authoritativeLabel, component.authoritative_label))
            if n == len(self.components) - 1:
                graph.add((components_bn, RDF.rest, RDF.nil))
            else:
                next_bnode = rdflib.BNode()
                graph.add((components_bn, RDF.rest, next_bnode))
                components_bn = next_bnode

        return graph

    @property
    def components(self):
        """Components for LoC Complex subjects. If subject is
        complex, returns a list of :class:`SubjectEntity`
        and :class:`NameEntity` objects. If subject is simple,
        returns :class:`TemporalEntity`.
        """
        return self.initial_components

    @cached_property
    def authoritative_label(self):
        """Authoritative entity label in English"""
        labels = [c.authoritative_label for c in self.components]
        label_string = '--'.join(labels)
        label_literal = rdflib.Literal(label_string, lang='en')
        return label_literal

    @property
    def scheme_membership(self):
        """Since entities are not indexed, returns None."""
        return None


class SRUResult(object):
    """SRU search result object, for use with :meth:`LocAPI.search`."""

    def __init__(self, data):
        self._results = data.get('hits', [])
        # LoC API is buggy and does not have
        # a reliable way to count results
        self.total_results = len(self._results)

    @cached_property
    def records(self):
        """List of results as :class:`SRUItem`."""
        return [SRUItem(r) for r in self._results]


class SRUItem(object):
    """Single item returned by a SRU search, for use with
    :meth:`LocAPI.search` and :class:`SRUResult`.
    """

    def __init__(self, data):
        self._data = data

    @property
    def uri(self):
        """LoC URI for this result"""
        return self._data['uri']

    @property
    def loc_id(self):
        """LoC ID string for this result"""
        return self._data['token']

    @property
    def label(self):
        """Authoritative label for this result"""
        return self._data['aLabel']
