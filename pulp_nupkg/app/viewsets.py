"""
Check `Plugin Writer's Guide`_ and `pulp_example`_ plugin
implementation for more details.

.. _Plugin Writer's Guide:
    http://docs.pulpproject.org/en/3.0/nightly/plugins/plugin-writer/index.html

.. _pulp_example:
    https://github.com/pulp/pulp_example/
"""

from django_filters.rest_framework import filterset
from pulpcore.plugin import models as pulpcore_models
from rest_framework import decorators, serializers as drf_serializers
from rest_framework.exceptions import ValidationError
from pulpcore.plugin import viewsets as platform

from . import models, serializers


class NupkgContentViewSet(platform.ContentViewSet):
    """
    A ViewSet for NupkgContent.

    Define endpoint name which will appear in the API endpoint for this content type.
    For example::
        http://pulp.example.com/api/v3/content/nupkg/

    Also specify queryset and serializer for NupkgContent.
    """

    endpoint_name = 'nupkg'
    queryset = models.NupkgContent.objects.all()
    serializer_class = serializers.NupkgContentSerializer


class NupkgImporterViewSet(platform.ImporterViewSet):
    """
    A ViewSet for NupkgImporter.

    Similar to the NupkgContentViewSet above, define endpoint_name,
    queryset and serializer, at a minimum.
    """

    endpoint_name = 'nupkg'
    queryset = models.NupkgImporter.objects.all()
    serializer_class = serializers.NupkgImporterSerializer

    @decorators.detail_route(methods=('post',))
    def sync(self, request, pk):
        importer = self.get_object()
        if not importer.feed_url:
            # TODO(asmacdo) make sure this raises a 400
            raise ValueError(_("An importer must have a 'feed_url' attribute to sync."))

        async_result = tasks.sync.apply_async_with_reservation(
            viewsets.tags.RESOURCE_REPOSITORY_TYPE, str(importer.repository.pk),
            kwargs={'importer_pk': importer.pk}
        )
        return viewsets.OperationPostponedResponse([async_result], request)


class NupkgPublisherViewSet(platform.PublisherViewSet):
    """
    A ViewSet for NupkgPublisher.

    Similar to the NupkgContentViewSet above, define endpoint_name,
    queryset and serializer, at a minimum.
    """

    endpoint_name = 'nupkg'
    queryset = models.NupkgPublisher.objects.all()
    serializer_class = serializers.NupkgPublisherSerializer

    @decorators.detail_route(methods=('post',))
    def publish(self, request, pk):
        publisher = self.get_object()
        repository_pk = str(publisher.repository.pk)
        async_result = tasks.publish.apply_async_with_reservation(
            viewsets.tags.RESOURCE_REPOSITORY_TYPE, repository_pk,
            kwargs={'publisher_pk': str(publisher.pk),
                    'repository_pk': repository_pk}
        )
        return viewsets.OperationPostponedResponse([async_result], request)
