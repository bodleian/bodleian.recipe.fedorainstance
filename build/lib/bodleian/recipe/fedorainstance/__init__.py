import logging
import os
import zipfile
import re
import stat
import urllib2
import zc.buildout

from hexagonit.recipe.download import Recipe as downloadRecipe


PACKAGES = {
 "4": "https://github.com/fcrepo4/fcrepo4/releases/download/fcrepo-4.2.0/fcrepo-webapp-4.2.0.war"
}


class FedoraRecipe:
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        options.setdefault('destination', os.path.join(
            buildout['buildout']['parts-directory'],
            self.name))

        if "version" not in options:
            self.logger.error("No version specified")
            raise zc.buildout.UserError("No version specified")

        if options["version"] not in PACKAGES:
            self.logger.error("Specified version %s is not supported" % options['version'])
            raise zc.buildout.UserError("Specified version %s is not supported" % options['version'])
        self.options['url'] = PACKAGES[options['version']]
        self.options['download-only'] = 'true'
        self.download = downloadRecipe(buildout, name, options)

    def _execute(self):
        print self.options['version']

    def install(self):
        import pdb; pdb.set_trace()
        output = self.download.install()
        target_dir = self.options['target']
        # Unzip the produced archive
        with zipfile.ZipFile(output[0]) as zip_file:
            # Extract
            zip_file.extractall(target_dir)
        return self.options.created()

    def update(self):
        return self.options.created()