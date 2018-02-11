from pulpcore.plugin import PulpPluginAppConfig


class PulpNupkgPluginAppConfig(PulpPluginAppConfig):
    name = 'pulp_nupkg.app'
    label = 'pulp_nupkg'
