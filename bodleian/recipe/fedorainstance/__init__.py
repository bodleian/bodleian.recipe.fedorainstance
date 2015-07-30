import logging
import os
import zipfile
import re
import stat
import urllib2
import zc.buildout

from hexagonit.recipe.download import Recipe as downloadRecipe


PACKAGES = {
    "4": "https://github.com/fcrepo4/fcrepo4/releases/download/fcrepo-4.2.0/fcrepo-webapp-4.2.0.war",
    "3": "http://downloads.sourceforge.net/project/fedora-commons/fedora/3.7.0/fcrepo-installer-3.7.0.jar?r=&ts=1424278682&use_mirror=waia"
}


class FedoraRecipe:
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        if "version" not in options:
            self.logger.error("No version specified")
            raise zc.buildout.UserError("No version specified")

        if "tomcat-app-dir" not in options:
            self.logger.error("No tomcat app directory specified")
            raise zc.buildout.UserError("No tomcat app directory specified")

        if options["version"] not in PACKAGES:
            self.logger.error("Specified version %s is not supported" % options['version'])
            raise zc.buildout.UserError("Specified version %s is not supported" % options['version'])
        options.setdefault('destination',
                           os.path.join(options['tomcat-app-dir'],
                                        options['tomcat-url-suffix']))

        self.options['url'] = PACKAGES[options['version']]
        self.download = downloadRecipe(buildout, name, options)

    def _execute(self):
        print self.options['version']

    def install(self):
        output = self.download.install()
        target_dir = self.options['tomcat-app-dir']
        return self.options.created()

    def update(self):
        return self.options.created()