"""Test log store."""
from __future__ import absolute_import, unicode_literals

from travis_log_fetch._store import (
    get_repo_stored_builds,
    get_stored_repo_slugs,
    get_stored_targets,
)

import pytest


class TestDefaultLayout(object):

    base_dir = './tests/default_layout'
    layout = '{job.repository.slug}/{job.number}-{job.state}.txt'

    def test_slugs(self):
        slugs = get_stored_repo_slugs(self.base_dir, self.layout)

        assert 'wikimedia/pywikibot-core' in slugs
        assert 'foo' not in slugs
        assert 'jayvdb/pywikibot-core/foo' not in slugs

    def test_targets(self):
        targets = get_stored_targets(self.base_dir, self.layout)

        assert targets
        assert type(targets) == list

        assert 'wikimedia/pywikibot-core/3052.11' in targets
        assert 'jayvdb/pywikibot-core/foo' not in targets

    def test_builds(self):
        builds = get_repo_stored_builds(
            self.base_dir, 'wikimedia/pywikibot-core', self.layout)

        assert builds
        assert 'wikimedia/pywikibot-core/3052' in builds


class TestAltLayout(object):

    base_dir = './tests/alt_layout'
    layout = '{job.state}/{job.repository.slug}/{job.number}.txt'

    def test_slugs(self):
        slugs = get_stored_repo_slugs(self.base_dir, self.layout)

        assert slugs == set(['a/b', 'foo/bar'])

    def test_builds(self):
        builds = get_repo_stored_builds(self.base_dir, 'a/b', self.layout)

        assert builds
        assert 'a/b/10' in builds

        builds = get_repo_stored_builds(self.base_dir, 'foo/bar', self.layout)

        assert builds
        assert 'foo/bar/7' in builds
