from dal import autocomplete

from loc_authorities.api import LocAPI


class LocLookup(autocomplete.AlightListView):
    """View to provide Library of Congress suggestions for autocomplete
    lookup. Based on :class:`dal.autocomplete.AlightListView. Expects
    search term as query string parameter `q`. Returns the LoC identifier
    and displays the label as text.
    """

    authority = None

    def get_list(self):
        q = self.q
        if q:
            loc = LocAPI()
            result = loc.suggest(q, authority=self.authority)
            return [(item.loc_id, item.label) for item in result]
        else:
            return []

    def create(self, text):
        return text


class LocNameLookup(LocLookup):
    """View to provide Library of Congress suggestions from the
    Name Authority File for autocomplete lookup. Behaves like
    :class:`LocLookup` but only returns name authority records.
    """

    authority = 'names'


class LocSubjectLookup(LocLookup):
    """View to provide Library of Congress suggestions from the
    LC Subject Headings for autocomplete lookup. Behaves like
    :class:`LocLookup` but only returns subject heading records.
    """

    authority = 'subjects'


class LocSearch(autocomplete.AlightListView):
    """View to perform keyword search from Library of Congress
    to provide autocomplete suggestions. As searching without a
    authority is unsupported in loc-authorities, this is an
    abstract class to provide functionality for specific
    authorities. Based on :class:`dal.autocomplete.AlightListView.
    Expects search term as query string parameter `q`. Returns the
    LoC identifier and displays the label as text.
    """

    authority = None

    def get_list(self):
        q = self.q
        if q:
            loc = LocAPI()
            result = loc.search(q, authority=self.authority)
            return [(item.loc_id, item.label) for item in result]
        else:
            return []

    def create(self, text):
        return text


class LocNameSearch(LocSearch):
    """View to perform keyword search from the Library of Congress
    Name Authority File for autocomplete lookup. Inherits from
    :class:`LocSearch` and only returns name authority records.
    """

    authority = 'names'


class LocSubjectSearch(LocSearch):
    """View to perform keyword search from the Library of Congress
    Subject Headings for autocomplete lookup. Inherits from
    :class:`LocSearch` and only returns subject heading records.
    """

    authority = 'subjects'
