from dal import autocomplete


class LocWidget(autocomplete.ListAlight):
    """Wrapper for dal widget. Expects a URL parameter that matches the
    namespace for loc-authorities and one of the loc-authorities views
    (suggest, name-suggest, subject-suggest, name-search, subject-search).
    """

    pass


class LocField(autocomplete.AlightListCreateChoiceField):
    """Wrapper for dal field as it requires a predefined choice-list, which
    for this use case is always empty.

    Pass :class:`LocWidget` as this field's widget to specify the URL you would
    like to query.
    """

    choice_list = []
    widget = LocWidget(url='loc-authorities:suggest')

    def __init__(self, choice_list=choice_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
