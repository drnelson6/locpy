from unittest.mock import patch
import pytest

pytest.importorskip('django', reason='django not installed')
import django  # NOQA
from django.test import TestCase  # NOQA
from django.urls import reverse  # NOQA

from loc_authorities.api import LocAPI, SRUResult  # NOQA
from loc_authorities.views import LocLookup, LocNameSearch  # NOQA
from loc_authorities.forms import LocField  # NOQA


@pytest.mark.skipif(django is None, reason='Requires Django')
class TestLocField:
    def test_render(self):
        field = LocField()
        assert field.choice_list == []


@pytest.mark.skipif(django is None, reason='Requires Django')
class TestSuggest(TestCase):
    @patch('loc_authorities.views.LocAPI')
    def test_lookup(self, mocklocapi):
        # TODO: This does not test the create method
        lookup_url = reverse('loc_authorities:suggest')

        # Although we don't need to test the functionality of dal, we can't directly pass
        # q to the get_list() method. So we have to test the functionality through the
        # get method

        # test for results when no query is run
        result = self.client.get(lookup_url)
        assert result.content.decode('utf-8') == ''
        result = self.client.get(lookup_url, {'q': 'xqsa'})
        assert result.status_code == 200

        # simulate no results
        empty_result = (
            '<div data-create data-value="xqsa">Create &quot;xqsa&quot;</div>'
        )
        assert result.content.decode('utf-8') == empty_result
        # example of truncated results
        mock_response = SRUResult(
            {
                'hits': [
                    {
                        'uri': 'http://id.loc.gov/authorities/names/n79043402',
                        'token': 'n79043402',
                        'aLabel': 'Franklin, Benjamin, 1706-1790',
                    }
                ]
            }
        ).records
        mocklocapi.return_value.suggest.return_value = mock_response
        result = self.client.get(lookup_url, {'q': 'franklin'})
        assert result.status_code == 200
        mocklocapi.return_value.suggest.assert_called_with('franklin', authority=None)
        html = result.content.decode('utf-8')
        lookup_result = (
            '<div data-value="n79043402">Franklin, Benjamin,'
            ' 1706-1790</div><div data-create data-value'
            '="franklin">Create &quot;franklin&quot;</div>'
        )
        assert html == lookup_result

        # test create method
        # this test could use a little work because it assumes DAL works correctly
        view = LocLookup()
        view.setup(self.client.request)

        text = 'n79043042'

        assert view.create(text) == 'n79043042'

        # now test looking for a name
        name_url = reverse('loc_authorities:name-suggest')
        result = self.client.get(name_url, {'q': 'franklin'})
        assert result.status_code == 200
        mocklocapi.return_value.suggest.assert_called_with(
            'franklin', authority='names'
        )
        html = result.content.decode('utf-8')
        # lookup result should be the same as above
        assert html == lookup_result

        # test subjects
        subject_response = SRUResult(
            {
                'hits': [
                    {
                        'uri': 'http://id.loc.gov/authorities/subjects/sh85100849',
                        'token': 'sh85100849',
                        'aLabel': 'Philosophy',
                    }
                ]
            }
        ).records
        subject_url = reverse('loc_authorities:subject-suggest')
        mocklocapi.return_value.suggest.return_value = subject_response
        result = self.client.get(subject_url, {'q': 'philosophy'})
        assert result.status_code == 200
        mocklocapi.return_value.suggest.assert_called_with(
            'philosophy', authority='subjects'
        )
        html = result.content.decode('utf-8')
        subject_result = (
            '<div data-value="sh85100849">Philosophy</div><div '
            'data-create data-value="philosophy">Create &quot;philosophy&quot;</div>'
        )
        assert html == subject_result


@pytest.mark.skipif(django is None, reason='Requires Django')
class TestSearch(TestCase):
    @patch('loc_authorities.views.LocAPI')
    def test_search(self, mocklocapi):
        # TODO: This does not test the create method
        search_url = reverse('loc_authorities:name-search')

        # Although we don't need to test the functionality of dal, we can't directly pass
        # q to the get_list() method. So we have to test the functionality through the
        # get method

        # test for results when no query is run
        result = self.client.get(search_url)
        assert result.content.decode('utf-8') == ''
        result = self.client.get(search_url, {'q': 'xqsa'})
        assert result.status_code == 200

        # simulate no results
        empty_result = (
            '<div data-create data-value="xqsa">Create &quot;xqsa&quot;</div>'
        )
        assert result.content.decode('utf-8') == empty_result
        # example of truncated results
        mock_response = SRUResult(
            {
                'hits': [
                    {
                        'uri': 'http://id.loc.gov/authorities/names/n79043402',
                        'token': 'n79043402',
                        'aLabel': 'Franklin, Benjamin, 1706-1790',
                    }
                ]
            }
        ).records
        mocklocapi.return_value.search.return_value = mock_response
        result = self.client.get(search_url, {'q': 'franklin'})
        assert result.status_code == 200
        mocklocapi.return_value.search.assert_called_with('franklin', authority='names')
        html = result.content.decode('utf-8')
        search_result = (
            '<div data-value="n79043402">Franklin, Benjamin,'
            ' 1706-1790</div><div data-create data-value'
            '="franklin">Create &quot;franklin&quot;</div>'
        )
        assert html == search_result

        view = LocNameSearch()
        view.setup(self.client.request)

        text = 'n79043042'

        assert view.create(text) == 'n79043042'

        # test subjects
        subject_response = SRUResult(
            {
                'hits': [
                    {
                        'uri': 'http://id.loc.gov/authorities/subjects/sh85100849',
                        'token': 'sh85100849',
                        'aLabel': 'Philosophy',
                    }
                ]
            }
        ).records
        subject_url = reverse('loc_authorities:subject-search')
        mocklocapi.return_value.search.return_value = subject_response
        result = self.client.get(subject_url, {'q': 'philosophy'})
        assert result.status_code == 200
        mocklocapi.return_value.search.assert_called_with(
            'philosophy', authority='subjects'
        )
        html = result.content.decode('utf-8')
        subject_result = (
            '<div data-value="sh85100849">Philosophy</div><div '
            'data-create data-value="philosophy">Create &quot;philosophy&quot;</div>'
        )
        assert html == subject_result
