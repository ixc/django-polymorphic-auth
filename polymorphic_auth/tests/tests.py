"""
Tests for ``polymorphic_auth`` app.
"""

# WebTest API docs: http://webtest.readthedocs.org/en/latest/api.html

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest


class Sample(WebTest):
    def test_sample(self):
        pass
