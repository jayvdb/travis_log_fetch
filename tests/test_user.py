"""Test Target resolution."""
from __future__ import absolute_import, unicode_literals

from travis_log_fetch.config import _get_travispy

from travis_log_fetch.get import get_user_repos

import pytest


class TestUser(object):

    def test_travispy(self):
        _travis = _get_travispy()

        repos = get_user_repos(_travis, 'travispy')

        slugs = [repo.slug for repo in repos]
        assert 'travispy/on_pypy' in slugs
