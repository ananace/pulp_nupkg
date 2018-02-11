"""
Check `Plugin Writer's Guide`_ and `pulp_example`_ plugin
implementation for more details.

.. _Plugin Writer's Guide:
    http://docs.pulpproject.org/en/3.0/nightly/plugins/plugin-writer/index.html

.. _pulp_example:
    https://github.com/pulp/pulp_example/
"""

from rest_framework import serializers
from pulpcore.plugin import serializers as platform

from . import models


class NupkgContentSerializer(platform.ContentSerializer):
    """
    A Serializer for NupkgContent.

    Add serializers for the new fields defined in NupkgContent and
    add those fields to the Meta class keeping fields from the parent class as well.

    For example::

    field1 = serializers.TextField()
    field2 = serializers.IntegerField()
    field3 = serializers.CharField()

    class Meta:
        fields = platform.ContentSerializer.Meta.fields + ('field1', 'field2', 'field3')
        model = models.NupkgContent
    """

    class Meta:
        fields = platform.ContentSerializer.Meta.fields
        model = models.NupkgContent


class NupkgImporterSerializer(platform.ImporterSerializer):
    """
    A Serializer for NupkgImporter.

    Add any new fields if defined on NupkgImporter.
    Similar to the example above, in NupkgContentSerializer.
    Additional validators can be added to the parent validators list

    For example::

    class Meta:
        validators = platform.ImporterSerializer.Meta.validators + [myValidator1, myValidator2]
    """

    class Meta:
        fields = platform.ImporterSerializer.Meta.fields
        model = models.NupkgImporter
        validators = platform.ImporterSerializer.Meta.validators


class NupkgPublisherSerializer(platform.PublisherSerializer):
    """
    A Serializer for NupkgPublisher.

    Add any new fields if defined on NupkgPublisher.
    Similar to the example above, in NupkgContentSerializer.
    Additional validators can be added to the parent validators list

    For example::

    class Meta:
        validators = platform.PublisherSerializer.Meta.validators + [myValidator1, myValidator2]
    """

    class Meta:
        fields = platform.PublisherSerializer.Meta.fields
        model = models.NupkgPublisher
        validators = platform.PublisherSerializer.Meta.validators
