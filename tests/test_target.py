"""Test Target class."""
from __future__ import absolute_import, unicode_literals

from travis_log_fetch._target import Target

import pytest


class Test(object):

    def test_empty(self):
        target = Target()
        assert target.user is None
        assert target.project is None
        assert target.build_id is None
        assert target.job_id is None
        assert target.build_number is None
        assert target.job_number is None

        #pytest.raises(AssertionError, getattr, target, 'slug')
        #pytest.raises(AssertionError, getattr, target, 'extended_slug')

    def test_invalid_basic_slug(self):
        pytest.raises(AssertionError, Target.from_simple_slug, 'foobar')

    def test_basic_slug(self):
        target = Target.from_simple_slug('foo/bar')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id is None
        assert target.build_number is None
        assert target.job_number is None


class TestExtended(object):

    def test_slash(self):
        target = Target.from_extended_slug('foo/bar/10.1')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id is None
        assert target.build_number == 10
        assert target.job_number == 1

    def test_hash(self):
        target = Target.from_extended_slug('foo/bar#10.1')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id is None
        assert target.build_number == 10
        assert target.job_number == 1

    def test_at(self):
        target = Target.from_extended_slug('foo/bar@9999')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id == 9999
        assert target.job_id is None
        assert target.build_number is None
        assert target.job_number is None

    def test_colon(self):
        target = Target.from_extended_slug('foo/bar:10000')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id == 10000
        assert target.build_number is None
        assert target.job_number is None

class TestUrl(object):

    def test_https_project_url(self):
        target = Target.from_url('https://travis-ci.org/foo/bar')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id is None
        assert target.build_number is None
        assert target.job_number is None

    def test_http_project_url(self):
        target = Target.from_url('http://travis-ci.org/foo/bar')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id is None
        assert target.build_number is None
        assert target.job_number is None

    def test_no_protocol_project_url(self):
        target = Target.from_url('//travis-ci.org/foo/bar')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id is None
        assert target.build_number is None
        assert target.job_number is None

    def test_build_url(self):
        target = Target.from_url('//travis-ci.org/foo/bar/builds/9999')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id == 9999
        assert target.job_id is None
        assert target.build_number is None
        assert target.job_number is None

    def test_job_url(self):
        target = Target.from_url('//travis-ci.org/foo/bar/jobs/10000')
        assert target.user == 'foo'
        assert target.project == 'bar'
        assert target.slug == 'foo/bar'
        assert target.build_id is None
        assert target.job_id == 10000
        assert target.build_number is None
        assert target.job_number is None
