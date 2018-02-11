import logging
import os

from collections import namedtuple
from gettext import gettext as _
from urllib.parse import urlparse, urlunparse

from celery import shared_task
from django.core.files import File
from django.db.models import Q

from pulpcore.plugin.models import (
    Artifact,
    RepositoryVersion,
    Publication,
    PublishedArtifact,
    PublishedMetadata,
    RemoteArtifact,
    Repository)
from pulpcore.plugin.changeset import (
    BatchIterator,
    ChangeSet,
    PendingArtifact,
    PendingContent,
    SizedIterable)
from pulpcore.plugin.tasking import UserFacingTask, WorkingDirectory

from pulp_file.app.models import FileContent, FileImporter, FilePublisher
from pulp_file.manifest import Entry, Manifest


log = logging.getLogger(__name__)


# Natural key.
Key = namedtuple('Key', ('path', 'digest'))


def _publish(publication):
    """
    Create published artifacts and yield a Manifest Entry for each.
    Args:
        publication (pulpcore.plugin.models.Publication): The Publication being created.
    Yields:
        Entry: The manifest entry.
    """
    def find_artifact():
        _artifact = content_artifact.artifact
        if not _artifact:
            _artifact = RemoteArtifact.objects.get(
                content_artifact=content_artifact,
                importer__repository=publication.repository_version.repository)
        return _artifact
    for content in publication.repository_version.content:
        for content_artifact in content.contentartifact_set.all():
            artifact = find_artifact()
            published_artifact = PublishedArtifact(
                relative_path=content_artifact.relative_path,
                publication=publication,
                content_artifact=content_artifact)
            published_artifact.save()
            entry = Entry(
                path=content_artifact.relative_path,
                digest=artifact.sha256,
                size=artifact.size)
            yield entry

@shared_task(base=UserFacingTask)
def publish(publisher_pk, repository_pk):
    """
    Use provided publisher to create a Publication based on a RepositoryVersion.
    Args:
        publisher_pk (str): Use the publish settings provided by this publisher.
        repository_pk (str): Create a Publication from the latest version of this Repository.
    """
    publisher = FilePublisher.objects.get(pk=publisher_pk)
    repository = Repository.objects.get(pk=repository_pk)
    repository_version = RepositoryVersion.latest(repository)

    log.info(
        _('Publishing: repository=%(repository)s, version=%(version)d, publisher=%(publisher)s'),
        {
            'repository': repository.name,
            'version': repository_version.number,
            'publisher': publisher.name,
        })

    with WorkingDirectory():
        with Publication.create(repository_version, publisher) as publication:
            manifest = Manifest('PULP_MANIFEST')
            manifest.write(_publish(publication))
            metadata = PublishedMetadata(
                relative_path=os.path.basename(manifest.path),
                publication=publication,
                file=File(open(manifest.path, 'rb')))
            metadata.save()

    log.info(
        _('Publication: %(publication)s created'),
        {
            'publication': publication.pk
        })


@shared_task(base=UserFacingTask)
def sync(importer_pk):
    """
    Validate the importer, create and finalize RepositoryVersion.
    Args:
        importer_pk (str): The importer PK.
    Raises:
        ValueError: When feed_url is empty.
    """
    importer = FileImporter.objects.get(pk=importer_pk)

    if not importer.feed_url:
        raise ValueError(_("An importer must have a 'feed_url' attribute to sync."))

    base_version = RepositoryVersion.latest(importer.repository)

    with RepositoryVersion.create(importer.repository) as new_version:

        synchronizer = Synchronizer(importer, new_version, base_version)
        with WorkingDirectory():
            log.info(
                _('Starting sync: repository=%(repository)s importer=%(importer)s'),
                {
                    'repository': importer.repository.name,
                    'importer': importer.name
                })
            synchronizer.run()
