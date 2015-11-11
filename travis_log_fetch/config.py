# -*- coding: utf-8 -*-
"""Configuration module."""
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from logging import getLogger
from os.path import expanduser
from textwrap import dedent

import configargparse

import github3

import travispy

_options = None
_travispy = None
_github = None

__logs__ = getLogger(__package__)


def get_parser():
    """Get config parser."""
    parser = configargparse.ArgParser(
        prog='travis_log_fetch',
        usage='%(prog)s [options] [target [target2 ...]]',
        description=dedent(
            """
            travis_log_fetch fetches many log files.
            """.rstrip()),
        default_config_files=[
            '~/.travisrc', '.travisrc'])

    parser.add('-c', '--config', is_config_file=True,
               help='config file path')
    parser.add('-d', '--dir', help='log storage directory',
               default='~/.travis')
    parser.add('--access-token', required=False, help='Github access token',
               env_var='GITHUB_ACCESS_TOKEN')
    parser.add('--api', required=False,
               help='Travis API CI URL; use "pro" for Travis CI Pro',
               default=travispy.travispy.PUBLIC)
    parser.add('-v', '--verbose', help='verbose', action='store_true')
    parser.add('-r', '--refresh', help='refresh', action='store_true')
    parser.add('--forks', help='fetch forks', action='store_true')
    parser.add('-f', '--force', help='force', action='store_true')
    parser.add('--format', help='log filename format',
               default='{job.repository.slug}/{job.number}-{job.state}.txt')
    parser.add('-a', '--all', help='all', action='store_true')
    parser.add('-o', '--old', help='old', action='store_true')
    parser.add('-s', '--self', help='fetch own repos', action='store_true')
    parser.add('-w', '--wait', help='wait for jobs to complete',
               action='store_true')
    parser.add('--sleep', help='time to wait for jobs to complete',
               type=int, default=30)
    parser.add('--count', help='number of old logs to fetch',
               type=int, default=10)
    parser.add('targets', nargs='*', help='targets')

    return parser


def get_options():
    """Get options."""
    global _options

    if not _options:
        parser = get_parser()

        pytest = sys.argv[0].endswith('/py.test')
        args = [] if pytest else None

        try:
            _options = parser.parse_args(args=args)
            if _options.api == 'pro':
                _options.api = travispy.travispy.PRIVATE
            __logs__.debug('config options: {0}'.format(_options))
        except SystemExit:
            if pytest:
                __logs__.warning('failed to load options')
                return

            raise

        _options.dir = expanduser(_options.dir)

    return _options


def _get_travispy():
    """Get travis-ci handle."""
    global _travispy

    if not _travispy:
        options = get_options()
        if options and options.access_token:
            _travispy = travispy.TravisPy.github_auth(
                options.access_token, uri=options.api)
            __logs__.debug('logged into travis-ci')
        else:
            _travispy = travispy.TravisPy(uri=options.api)
            __logs__.debug('anon travis-ci activated')

    return _travispy


def _get_github():
    """Get github handle."""
    global _github

    if not _github:
        options = get_options()
        if options and options.access_token:
            _github = github3.login(token=options.access_token)
            __logs__.debug('logged into github')

        if not _github:
            _github = github3.GitHub()
            __logs__.debug('anon github activated')

    return _github
