.. lc_ld documentation master file, created by
   sphinx-quickstart on Wed Aug 27 16:18:43 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to documentation for loc-authorities!
=================================

**loc-authorities** is a Python library for querying authorities from the `Linked Data Service <https://id.loc.gov/>`_ provided by the Library of Congress. It provides methods for querying the search and retrieval APIs and also provides Python classes to represent entities from the Linked Data Service.

* Project source code: `https://github.com/AmericanPhilosophicalSociety/loc-authorities <https://github.com/AmericanPhilosophicalSociety/loc-authorities>`_
* Project distribution: `https://pypi.org/project/loc-authorities/ <https://pypi.org/project/loc-authorities/>`_

**Supported search interfaces**:

* `Resource retrieval <https://id.loc.gov/views/pages/swagger-api-docs/index.html#download.json>`_ 
* `Known label retrieval <https://id.loc.gov/views/pages/swagger-api-docs/index.html#known-label-retrieval.json>`_
* `Left-anchored suggest <https://id.loc.gov/views/pages/swagger-api-docs/index.html#suggest-service-2.json>`_
* `Keyword query <https://id.loc.gov/views/pages/swagger-api-docs/index.html#suggest-service-2.json>`_

**Fully supported authorities**:

* `LC Subject Headings <https://id.loc.gov/authorities/subjects.html>`_
* `LC Name Authority File <https://id.loc.gov/authorities/names.html>`_

**Partially supported authorities**:

* `LC Children's Subject Headings <https://id.loc.gov/authorities/childrensSubjects.html>`_
* `LC Medium of Performance Thesaurus for Music <https://id.loc.gov/authorities/performanceMediums.html>`_
* `LC Demographic Group Terms <https://id.loc.gov/authorities/demographicTerms.html>`_
* `Thesaurus for Graphic Materials <https://id.loc.gov/vocabulary/graphicMaterials.html>`_
* `AFS Ethnographic Thesaurus <https://id.loc.gov/vocabulary/ethnographicTerms.html>`_
* `LC Genre/Form Terms <https://id.loc.gov/authorities/genreForms.html>`_

.. note::
   This project is under active development.
   The developers of this project have no relationship to the United States government or the Library of Congress.

.. toctree::
   :maxdepth: 2
   
   getting-started
   django-integration
   api-reference