"""Test Target resolution."""
from __future__ import absolute_import, unicode_literals

from travis_log_fetch.config import _get_travispy

from travis_log_fetch._target import Target
from travis_log_fetch.get import get_jobs

import pytest


# Note 'foo' is a real Github user, but they do not
# have repos bar or baz
class TestNonExistant(object):

    def test_single_target(self):
        target = Target.from_simple_slug('foo/bar')

        _travis = _get_travispy()
        jobs = get_jobs(_travis, target)
        assert len(jobs) == 0

    def test_multiple_targets(self):
        target1 = Target.from_simple_slug('foo/bar')
        target2 = Target.from_simple_slug('foo/baz')

        _travis = _get_travispy()
        jobs = get_jobs(_travis, [target1, target2])
        assert len(jobs) == 0


class TestLive(object):

    def test_single(self):
        target = Target.from_simple_slug('travispy/on_pypy')

        _travis = _get_travispy()
        jobs = get_jobs(_travis, target)
        assert len(jobs) == 1

        job = jobs[0]
        assert job.repository_id == 2598880

    def test_multiple(self):
        target1 = Target.from_simple_slug('travispy/on_pypy')
        target2 = Target.from_simple_slug('travispy/on_py34')

        _travis = _get_travispy()
        jobs = get_jobs(_travis, [target1, target2])
        assert len(jobs) == 2
        assert jobs[0].repository_id == 2598880
        assert jobs[1].repository_id == 2598879

    def test_logical_single_job_build(self):
        target = Target.from_extended_slug('travispy/on_pypy#1')

        _travis = _get_travispy()
        jobs = get_jobs(_travis, target)
        assert len(jobs) == 1

        job = jobs[0]
        assert job.repository_id == 2598880
        assert job.number == '1.1'
        assert job.id == 28881356

    def test_logical_multiple_job_build(self):
        target = Target.from_extended_slug('menegazzo/travispy#101')

        _travis = _get_travispy()
        jobs = get_jobs(_travis, target)

        assert len(jobs) == 5

        job = jobs[2]
        assert job.repository_id == 2419489
        assert job.number == '101.3'
        assert job.id == 82131391

    def test_logical_multiple_job_build_single_job(self):
        target = Target.from_extended_slug('menegazzo/travispy#101.3')

        _travis = _get_travispy()
        jobs = get_jobs(_travis, target)

        job = jobs[0]
        assert job.repository_id == 2419489
        assert job.number == '101.3'
        assert job.id == 82131391
