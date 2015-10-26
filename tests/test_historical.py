"""Test loading historical builds and jobs."""
from __future__ import absolute_import, unicode_literals

from travis_log_fetch.config import _get_travispy

from travis_log_fetch._target import Target
from travis_log_fetch.get import (
    get_travis_repo,
    get_historical_builds,
    get_historical_build,
    get_historical_job,
)

import pytest


class TestHistorical(object):

    def test_latest(self):
        _travis = _get_travispy()
        repo = get_travis_repo(_travis, 'travispy/on_pypy')

        builds = get_historical_builds(_travis, repo)
        build = next(builds)
        assert build.repository_id == 2598880
        assert build.id == repo.last_build_id

    def test_after(self):
        _travis = _get_travispy()
        repo = get_travis_repo(_travis, 'travispy/on_pypy')

        builds = get_historical_builds(_travis, repo,
                                       _after=3, _load_jobs=False)
        build = next(builds)
        assert build.repository_id == 2598880
        assert build.number == '2'

        build = next(builds)
        assert build.repository_id == 2598880
        assert build.number == '1'

    def test_all_small(self):
        _travis = _get_travispy()
        repo = get_travis_repo(_travis, 'travispy/on_pypy')

        builds = get_historical_builds(_travis, repo)

        ids = []
        for build in builds:
            assert build.repository_id == 2598880
            ids.append(build.id)

        assert ids == [53686685, 37521698, 28881355]

    def test_multiple_batches_menegazzo(self):
        """Test using a repository that has greater than 2*25 builds."""
        # Ideally each has one or two jobs, so that doesnt slow down the test,
        # and the logs are small in case the log is fetched with the job.
        _travis = _get_travispy()
        repo = get_travis_repo(_travis, 'menegazzo/travispy')

        builds = get_historical_builds(_travis, repo, _load_jobs=False)

        ids = []
        prev_number = None
        for build in builds:
            assert build.repository_id == 2419489

            if int(build.number) in [80]:
                # There are two '80'
                # See https://github.com/travis-ci/travis-ci/issues/2582
                print('duplicate build number {0}: {1}'.format(
                    build.number, build.id))

                assert build.id in [45019395, 45019396]
                if build.id == 45019395:
                    assert prev_number == int(build.number)
                else:
                    assert prev_number == int(build.number) + 1
            elif prev_number:
                # All other build numbers decrease rather orderly
                assert prev_number == int(build.number) + 1

            prev_number = int(build.number)

            if ids:
                assert build.id < ids[-1]

            ids.append(build.id)
            if len(ids) > 100:
                break

        assert len(ids) == len(set(ids))

    def test_multiple_batches_bootstrap(self):
        """Test using a repository that has lots of builds, esp. PRs."""
        _travis = _get_travispy()
        repo = get_travis_repo(_travis, 'twbs/bootstrap')

        builds = get_historical_builds(_travis, repo,
                                       _after=12071,
                                       _load_jobs=False)

        ids = []
        prev_number = None
        for build in builds:
            assert build.repository_id == 12962

            if int(build.number) in [12069, 12062, 12061, 12054, 12049,
                                     12048, 12041, 12038, 12037, 12033]:
                # Many duplicates
                # See https://github.com/travis-ci/travis-ci/issues/2582
                print('duplicate build number {0}: {1}'.format(
                    build.number, build.id))

                if build.id in [53437234, 53350534, 53350026,
                                53263731, 53263730,  # two extra 12054
                                53180440, 53179846, 53062896, 53019568,
                                53004896, 52960766]:
                    assert prev_number == int(build.number)
                else:
                    assert prev_number == int(build.number) + 1

            elif prev_number:
                # All other build numbers decrease rather orderly
                assert prev_number == int(build.number) + 1

            prev_number = int(build.number)

            if ids:
                assert build.id < ids[-1]

            ids.append(build.id)
            # There are many more duplicates, so we stop here.
            if int(build.number) == 12033:
                break

        assert len(ids) == len(set(ids))

    def test_logical_single_job_build(self):
        target = Target.from_extended_slug('travispy/on_pypy#1.1')

        _travis = _get_travispy()
        job = get_historical_job(_travis, target)

        assert job.repository_id == 2598880
        assert job.number == '1.1'
        assert job.id == 28881356

    def test_logical_multiple_job_build(self):
        target = Target.from_extended_slug('menegazzo/travispy#101.3')

        _travis = _get_travispy()
        job = get_historical_job(_travis, target)

        assert job.repository_id == 2419489
        assert job.number == '101.3'
        assert job.id == 82131391

    def test_logical_duplicate_build(self):
        target = Target.from_extended_slug('menegazzo/travispy#80.3')

        _travis = _get_travispy()
        pytest.raises(AssertionError, get_historical_build, _travis, target)
