# -*- coding: utf-8 -*-
"""Object that identifies a target resource."""
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

if sys.version_info[0] == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

from travispy import Build, Job, Repo


class Target(object):
    """Identifier of a target resource."""

    def __init__(self, user=None, project=None, build_id=None, job_id=None,
                 build_number=None, job_number=None, slug=None):
        """
        Constructor.

        build_id and job_id are the real identifier of those objects.
        build_number and job_number are the relative logical numbering
        of each object within their container.
        e.g. within a repo, a logical number '10.2' is the second job
        of the tenth build.
        """
        self.user = user
        self.project = project
        if slug:
            self.slug = slug

        types = [
            type(obj) for obj in [build_id, job_id, build_number, job_number]]

        assert set(types) <= set([type(None), int]), \
            'found types {0}'.format(types)

        self.build_id = build_id
        self.job_id = job_id
        self.build_number = build_number
        self.job_number = job_number
        self.state = None

    @property
    def slug(self):
        """Get repository slug."""
        assert self.user and self.project
        return self.user + '/' + self.project

    @slug.setter
    def slug(self, value):
        """Set repository slug."""
        parts = value.split('/', 1)
        assert len(parts) == 2
        assert '/' not in parts[1]
        self.user = parts[0]
        self.project = parts[1]

    @property
    def number(self):
        """Get logical number comprised of build and job number."""
        assert self.build_number
        assert self.job_number
        return '{0}.{1}'.format(self.build_number, self.job_number)

    @number.setter
    def number(self, value):
        """Set logical number."""
        assert '/' not in value
        parts = value.split('.', 1)
        assert len(parts) == 2
        assert '.' not in parts[1]
        self.build_number = int(parts[0])
        self.job_number = int(parts[1])

    @property
    def extended_slug(self):
        """Create an extended slug such as <slug>/10.2."""
        if self.build_number and self.job_number:
            return '{0}/{1}'.format(self.slug, self.number)
        elif self.build_number:
            return '{0}/{1}'.format(self.slug, self.build_number)
        elif self.job_id:
            return '{0}:{1}'.format(self.slug, self.job_id)
        elif self.build_id:
            return '{0}@{1}'.format(self.slug, self.build_id)
        else:
            return self.slug

    def __str__(self):
        """String representation using extended slug."""
        if not self.user or not self.project:
            return '<invalid>'
        return self.extended_slug

    def __repr__(self):
        """Internal representation using extended slug."""
        if not self.user or not self.project:
            return '<invalid>'
        return '<{0}: {1}>'.format(self.__class__.__name__, self.extended_slug)

    def __eq__(self, other):
        """Compare to other for equivalence."""
        return other == self.extended_slug

    @classmethod
    def from_simple_slug(cls, slug):
        """Return an Target from a slug containing user and project."""
        parts = slug.rsplit('/', 1)
        assert len(parts) == 2
        assert '/' not in parts[1]
        obj = cls(*parts)
        return obj

    @classmethod
    def from_extended_slug(cls, slug):
        """Return an Target from an build or job slug."""
        parts = slug.split('/')

        assert len(parts) in [2, 3]

        user = parts[0]

        logical_id = None
        build_id = job_id = None

        if len(parts) == 3:
            project, logical_id = parts[1:]
        else:
            if '#' in parts[1]:
                project, logical_id = parts[1].split('#', 1)
            elif '@' in parts[1]:
                project, build_id = parts[1].split('@', 1)
                build_id = int(build_id)
            elif ':' in parts[1]:
                project, job_id = parts[1].split(':', 1)
                job_id = int(job_id)
            else:
                project = parts[1]

        if logical_id:
            build_number, sep, job_number = logical_id.partition('.')
            assert(build_number)
            build_number = int(build_number)
            if job_number:
                job_number = int(job_number)
            else:
                job_number = None

            # print('{0} . {1}'.format(type(build_number), type(job_number)))

            return cls(user, project,
                       build_number=build_number, job_number=job_number)

        return cls(user, project, build_id, job_id)

    @classmethod
    def from_url(cls, url):
        """Create an Target from a travis url."""
        parsed_url = urlparse(url)
        assert parsed_url.path
        assert len(parsed_url.path) > 1

        path = parsed_url.path[1:]

        parts = path.split('/')

        if len(parts) == 2:
            return cls(parts[0], parts[1])

        if parts[2] == 'jobs':
            job_id = int(parts[3])
            return cls(parts[0], parts[1], None, job_id)
        elif parts[2] == 'builds':
            build_id = int(parts[3])
            return cls(parts[0], parts[1], build_id, None)
        else:
            raise AssertionError('unknown url {0}'.format(url))

    @classmethod
    def _from_travispy_obj(cls, obj):
        if isinstance(obj, Repo):
            return cls.from_simple_slug(obj.slug)
        elif isinstance(obj, Build):
            return cls(slug=obj.repository.slug, build_id=obj.id,
                       build_number=int(obj.number))
        elif isinstance(obj, Job):
            _obj = cls(job_id=obj.id, slug=obj.slug)
            _obj.number = obj.number
            return _obj
        else:
            raise AssertionError('unknown object {0!r}'.format(obj))
