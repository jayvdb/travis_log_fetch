# -*- coding: utf-8 -*-
"""Get a travis log."""
from __future__ import absolute_import
from __future__ import unicode_literals

from logging import getLogger

from time import sleep

import travispy

from travis_log_fetch._target import Target

__logs__ = getLogger(__package__)


def get_travis_repo(t, slug):
    """
    Return Travis Repo or None.

    slugs without Travis builds emit a warning and return None.
    """
    try:
        return t.repo(slug)
    except travispy.errors.TravisError as e:
        __logs__.error('slug {0} not found on Travis: {1}'.format(slug, e))
        return None


def get_travis_repos(t, slugs):
    """
    Return list of Travis repos.

    slugs without Travis builds are omitted with a warning.
    """
    repos = []
    for slug in slugs:
        repo = get_travis_repo(t, slug)
        if repo:
            repos.append(repo)
    return repos


def get_jobs(t, targets):
    """Resolve targets to travis Jobs."""
    try:
        iter(targets)
    except TypeError:
        targets = [targets]

    jobs = []
    for target in targets:
        if isinstance(target, Target):
            repo = get_travis_repo(t, target.slug)
            if repo is None:
                continue
            if target.job_id:
                jobs = t.jobs(slug=repo.slug, ids=target.job_id)
                assert len(jobs) == 1
                target = jobs[0]

            elif target.build_id:
                target = t.build(target.build_id)
                assert target.repository_id == repo.id

            elif target.build_number:
                build = get_historical_build(t, target)
                if not target.job_number:
                    target = build
                else:
                    target = _get_build_job(t, build, target.job_number)

            else:
                target = repo

        if isinstance(target, travispy.Repo):
            if not repo.last_build_id:
                __logs__.error('No builds for {0}'.format(repo.slug))
                continue
            target = t.build(repo.last_build_id)

        if isinstance(target, travispy.Build):
            jobs += target.jobs
        elif isinstance(target, travispy.Job):
            jobs.append(target)
        else:
            raise AssertionError('Unexpected type: {0!r}'.format(target))

    return jobs


def get_completed(t, jobs, wait_time):
    """Return jobs as they are completed."""
    while jobs:
        completed = [job for job in jobs if not job.pending]
        for job in completed:
            yield job

        pending = [job for job in jobs if job.pending]
        if not pending:
            return

        __logs__.info('waiting {0} seconds for pending {1}'.format(
            wait_time, list(job.id for job in pending)))
        sleep(wait_time)
        jobs = [t.job(job.id) for job in pending]


def _fix_build_jobs(t, build):
    """Add the jobs attribute."""
    if not hasattr(build, 'jobs'):
        assert hasattr(build, 'job_ids')
        # FIXME(upstream): this doesnt work
        # build.jobs = t.jobs(ids=build.job_ids)
        build.jobs = [t.job(job_id) for job_id in build.job_ids]


def get_historical_builds(t, repo, _after=None, _load_jobs=True):
    """Get historical builds for a repo."""
    if isinstance(repo, travispy.entities.Repo):
        slug = repo.slug
    else:
        slug = repo
    builds = t.builds(slug=slug, after_number=_after)

    # As there can be duplicate build numbers, warn when
    # duplicates are encountered
    # https://github.com/travis-ci/travis-ci/issues/2582
    previous = None
    while builds:
        __logs__.debug('fetched {0} builds after {1}'.format(
            len(builds), _after))

        for build in builds:
            build_number = int(build.number)

            if _load_jobs:
                _fix_build_jobs(t, build)

            if previous and build_number == int(previous.number):
                __logs__.warning(
                    'Duplicate build {0} detected: {1} & {2}'.format(
                        build_number, build.id, previous.id))

            yield build

        _after = builds[-1].number
        builds = t.builds(slug=slug, after_number=_after)


def _get_build_job(t, build, job_number):
    """Get logical job from build."""
    _fix_build_jobs(t, build)
    if not job_number and len(build.jobs) == 1:
        return build.jobs[0]

    for build_job in build.jobs:
        _, _, build_job_number = build_job.number.partition('.')
        build_job_number = int(build_job_number)
        if build_job_number == job_number:
            return build_job

    raise AssertionError('{0}: could not find job {1}; max {2}'.format(
        build, job_number, build_job.number))


def get_historical_build(t, target):
    """Get historical build."""
    assert isinstance(target, Target)
    assert target.build_number
    repo = get_travis_repo(t, target.slug)
    after = target.build_number + 1
    builds = get_historical_builds(t, repo, _after=after)

    # As there can be duplicate build numbers, fetch one more
    # to detect duplicates
    # https://github.com/travis-ci/travis-ci/issues/2582
    found = None

    for build in builds:
        build_number = int(build.number)
        if build_number == target.build_number:
            if found:
                raise AssertionError('Duplicate build {0} detected'.format(
                    build_number))

            found = build

        if build_number < target.build_number:
            if found:
                return found
            break

    if found:
        return found

    raise AssertionError('could not find build {0}'.format(target))


def get_historical_job(t, target):
    """Get historical job."""
    assert isinstance(target, Target)
    assert target.job_number
    build = get_historical_build(t, target)
    return _get_build_job(t, build, target.job_number)


def get_user_repos(t, user):
    """Get user's travis repositories."""
    if hasattr(user, 'login'):
        user = user.login
    return t.repos(member=user)


def get_forks(gh, slug):
    """Get github fork slugs."""
    username, project = slug.rsplit('/', 1)
    repo = gh.repository(username, project)
    assert repo
    # github3 v1.0.0 has iter_forks, and 'forks' is count only
    if hasattr(repo, 'iter_forks'):
        forks = list(repo.iter_forks())
    else:
        forks = list(repo.forks())

    return [fork.full_name for fork in forks]
