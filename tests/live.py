from __future__ import absolute_import, unicode_literals

import os

from travispy import TravisPy

GITHUB_ACCESS_TOKEN = os.environ.get('TRAVISPY_GITHUB_ACCESS_TOKEN')

TRAVIS_REPO_SLUG = os.environ.get('TRAVIS_REPO_SLUG')
TRAVIS_USER, TRAVIS_PROJECT = TRAVIS_REPO_SLUG.split('/', 1) if TRAVIS_REPO_SLUG else (None, None)


class LiveTest(object):

    def setup_method(self, method):
        if GITHUB_ACCESS_TOKEN:
            self._travis = TravisPy.github_auth(GITHUB_ACCESS_TOKEN)
        else:
            self._travis = TravisPy()
