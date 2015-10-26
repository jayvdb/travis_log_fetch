"""Test Github resolution."""
from __future__ import absolute_import, unicode_literals

from travis_log_fetch.config import (
    _get_github,
)
from travis_log_fetch.get import (
    get_forks,
)

import pytest


# Note 'foo' is a real Github user, but they do not
# have repos bar or baz
class TestForks(object):

    def test_invalid(self):
        _github = _get_github()
        pytest.raises(AssertionError, get_forks, _github, 'foo/bar')

    def test_zero(self):
        _github = _get_github()
        forks = get_forks(_github, 'travispy/on_pypy')
        assert len(forks) == 0

    def test_fork(self):
        _github = _get_github()
        forks = get_forks(_github, 'menegazzo/travispy')
        assert 'jayvdb/travispy' in forks
