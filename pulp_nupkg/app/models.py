"""
Check `Plugin Writer's Guide`_ and `pulp_example`_ plugin
implementation for more details.

.. _Plugin Writer's Guide:
    http://docs.pulpproject.org/en/3.0/nightly/plugins/plugin-writer/index.html

.. _pulp_example:
    https://github.com/pulp/pulp_example/
"""

from gettext import gettext as _
from logging import getLogger

from django.db import models

from pulpcore.plugin.models import (Artifact, Content, ContentArtifact, RemoteArtifact, Importer,
                                    ProgressBar, Publisher, RepositoryVersion, PublishedArtifact,
                                    PublishedMetadata)
from pulpcore.plugin.tasking import Task


log = getLogger(__name__)


class NupkgContent(Content):
    """
    The "nupkg" content type.

    Define fields you need for your new content type and
    specify uniqueness constraint to identify unit of this type.

    For example::

        field1 = models.TextField()
        field2 = models.IntegerField()
        field3 = models.CharField()

        class Meta:
            unique_together = (field1, field2)
    """

    TYPE = 'nupkg'

    # Called ID in NuSpec
    pkg_id = models.TextField(blank=False, null=False)
    version = models.TextField(blank=False, null=False)
    digest = models.TextField(blank=False, null=False)
    authors = models.TextField(null=False)

    #  authors     = models.TextField()
    #  copyright   = models.TextField()
    #  description = models.TextField()
    #  language    = models.TextField()
    #  owners      = models.TextField()
    #  summary     = models.TextField()
    #  tags        = models.TextField()
    #  title       = models.TextField()

    class Meta:
        unique_together = ('pkg_id', 'version', 'digest')


class NupkgPublisher(Publisher):
    """
    A Publisher for NupkgContent.

    Define any additional fields for your new publisher if needed.
    A ``publish`` method should be defined.
    It is responsible for publishing metadata and artifacts
    which belongs to a specific repository.
    """

    TYPE = 'nupkg'


class NupkgImporter(Importer):
    """
    An Importer for NupkgContent.

    Define any additional fields for your new importer if needed.
    A ``sync`` method should be defined.
    It is responsible for parsing metadata of the content,
    downloading of the content and saving it to Pulp.
    """

    TYPE = 'nupkg'
