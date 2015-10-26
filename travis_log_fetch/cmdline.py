# -*- coding: utf-8 -*-
"""Command line handler."""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from itertools import islice

from logging import getLogger

from travis_log_fetch import config

from travis_log_fetch._target import Target

from travis_log_fetch.get import (
    get_completed,
    get_forks,
    get_historical_builds,
    get_jobs,
    get_travis_repos,
    get_user_repos,
)
from travis_log_fetch._store import (
    download_job_log,
    get_stored_repo_slugs,
    skip_stored,
)


__logs__ = getLogger(__package__)


def main():
    """Main handler."""
    options = config.get_options()

    if not options or options.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)9s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

    __logs__.debug('{0!r}'.format(options))

    t = config._get_travispy()
    gh = config._get_github()
    if t:
        user = t.user()
    else:
        user = None

    targets = []

    for target_string in options.targets:
        if '://' in target_string:
            identifier = Target.from_url(target_string)
            targets.append(identifier)
        else:
            identifier = Target.from_extended_slug(target_string)
            targets.append(identifier)

    if options.refresh:
        slugs = get_stored_repo_slugs(options.dir, options.format)
        for slug in slugs:
            identifier = Target.from_simple_slug(slug)
            targets.append(identifier)

    if options.self:
        assert user
        targets += get_user_repos(t, user)

    if options.forks:
        for target in targets:
            slugs = get_forks(gh, target.slug)
            forks = get_travis_repos(t, slugs)
            targets += forks

    if options.all or options.old:
        count = None if options.all else options.count
        new_targets = []
        for target in targets:
            new_targets += list(islice(
                get_historical_builds(t, target.slug, _load_jobs=False),
                count))

        targets = new_targets

    # TODO: dont enumerate jobs if the files are all dated after the build end
    # TODO: enumerate all files starting with the job number,
    # and delete -started, -etc, when state is 'passed.

    if not options.force:
        targets = skip_stored(targets, options.dir, options.format)

    jobs = get_jobs(t, targets)

    if options.wait:
        jobs = get_completed(t, jobs, options.sleep)

    for job in jobs:
        download_job_log(options.dir, job, options.format)
