# -*- coding: utf-8 -*-
"""Store logs."""
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import datetime
import os

from logging import getLogger
from os.path import dirname, isdir

import dateutil
import dateutil.parser

import parse

import requests

from travis_log_fetch._target import Target

__logs__ = getLogger(__package__)

_HEADERS = {'Accept': 'text/plain; version=2'}


# TODO: add a 'clean' function to delete all logs which are
# associated with incomplete jobs.

# Create a new class to cache the stored metadata.


def get_files(base_dir):
    """Get list of all files under base_dir."""
    filenames = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            filenames.append(os.path.join(root[len(base_dir):], file))

    return filenames


def get_stored_targets(base_dir, log_filename_format=None):
    """Get parsed stored targets."""
    assert log_filename_format
    if '{job.state}' in log_filename_format:
        log_filename_format = log_filename_format.replace(
            '{job.state}', '{job.state:w}')

    if '{job.number}' in log_filename_format:
        log_filename_format = log_filename_format.replace(
            '{job.number}', '{job.number:f}')

    parser = parse.compile(log_filename_format)

    if base_dir[-1] != '/':
        base_dir = base_dir + '/'

    filenames = get_files(base_dir)

    targets = []
    for filename in filenames:
        parsed_filename = parser.parse(filename)
        if not parsed_filename:
            __logs__.warning('Unexpected filename {0}'.format(filename))
            continue
        target = Target()
        try:
            target.slug = parsed_filename['job.repository.slug']
        except KeyError:
            pass
        try:
            target.number = str(parsed_filename['job.number'])
        except KeyError:
            pass
        try:
            target.state = parsed_filename['job.state']
        except KeyError:
            pass

        targets.append(target)

    return targets


def _select_repo_builds(targets, slug):
    """Filter targets for one repo."""
    targets = [target for target in targets if target.slug == slug]
    build_numbers = set(target.build_number for target in targets
                        if isinstance(target, Target))
    builds = [Target(slug=slug, build_number=build_number)
              for build_number in build_numbers]
    return builds


def get_repo_stored_builds(base_dir, slug, log_filename_format=None):
    """Get stored builds for a repo."""
    targets = get_stored_targets(base_dir, log_filename_format)
    builds = _select_repo_builds(targets, slug)
    return builds


def skip_stored(targets, base_dir, log_filename_format=None):
    """Optimistically skip targets that have been fetched."""
    assert log_filename_format
    stored_targets = get_stored_targets(base_dir, log_filename_format)

    new_targets = []
    for target in targets:
        if not isinstance(target, Target):
            target = Target._from_travispy_obj(target)

        slug = target.slug

        stored_repo_targets = _select_repo_builds(stored_targets, slug)
        if target not in stored_repo_targets:
            __logs__.debug('target {0} not found in {1!r}'.format(
                target, stored_repo_targets))
            new_targets.append(target)
        else:
            __logs__.info('skipping existing {0}'.format(target))

    return new_targets


def _get_simple_stored_repo_slugs(base_dir):
    """Get repo slugs from first two directory names."""
    if base_dir[-1] != '/':
        base_dir = base_dir + '/'

    slugs = [root[len(base_dir):] for root, dirs, files in os.walk(base_dir)
             if len(root[len(base_dir):].split(os.sep)) == 2]

    return slugs


def get_stored_repo_slugs(base_dir, log_filename_format=None):
    """Get existing directory slugs."""
    assert log_filename_format
    if log_filename_format.startswith('{job.repository.slug}/'):
        return _get_simple_stored_repo_slugs(base_dir)

    targets = get_stored_targets(base_dir, log_filename_format)
    slugs = set(target.slug for target in targets)
    return slugs


def download_job_log(base_dir, job, log_filename_format=None):
    """Download job log."""
    filename = log_filename_format.format(job=job)
    filename = '{0}/{1}'.format(base_dir, filename)

    if job.finished_at and os.path.exists(filename):
        file_ts = os.stat(filename).st_mtime
        file_ts = datetime.datetime.fromtimestamp(file_ts, dateutil.tz.tzutc())
        job_finish_ts = dateutil.parser.parse(job.finished_at)
        if file_ts >= job_finish_ts:
            return

    directory_name = dirname(filename)
    if not isdir(directory_name):
        os.makedirs(directory_name)

    text = job.log.body

    # FIXME(upstream): https://github.com/menegazzo/travispy/pull/27
    if not text:
        __logs__.info('fetching job {0} log directly'.format(job.id))
        r = requests.get('%s/jobs/%s/log' % (job._session.uri, job.id),
                         headers=_HEADERS)
        text = r.content.decode('utf-8')

    try:
        with codecs.open(filename, 'w', 'utf8') as f:
            f.write(text)
    except UnicodeDecodeError as e:
        __logs__.warning(
            'UnicodeDecodeError while storing {0} into {1}: {2}'.format(
                type(text), filename, e))
        os.remove(filename)
        raise

    __logs__.info('wrote {0} with {1} chars'.format(filename, len(text)))
