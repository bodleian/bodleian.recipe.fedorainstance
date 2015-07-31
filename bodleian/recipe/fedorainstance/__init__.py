import logging
import os
import zipfile
import re
import stat
import urllib2
import zc.buildout
import shutil
from genshi.template import Context
from genshi.template import NewTextTemplate
from genshi.template.base import TemplateSyntaxError
from genshi.template.eval import UndefinedError


from hexagonit.recipe.download import Recipe as downloadRecipe


PACKAGES = {
    "4": "https://github.com/fcrepo4/fcrepo4/releases/download/fcrepo-4.2.0/fcrepo-webapp-4.2.0.war",
    "3": "http://10.0.2.15:8000/fcrepo-installer-3.7.0.jar"
    #http://downloads.sourceforge.net/project/fedora-commons/fedora/3.7.0/fcrepo-installer-3.7.0.jar?r=&ts=1424278682&use_mirror=waia"
}

class Fedora4Worker:
    """
    Install Fedora 4
    """
    def __init__(self, buildout, name, options, logger):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logger

        options.setdefault('destination',
                           os.path.join(options['tomcat-home'],
                                        "webapps",
                                        options['tomcat-url-suffix']))

        self.options['url'] = PACKAGES[options['version']]
        self.download = downloadRecipe(buildout, name, options)

    def work(self):
        output = self.download.install()
        return [output]

class Fedora3Worker:
    """
    Install Fedora 3
    """
    def __init__(self, buildout, name, options, logger):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logger

        destination = os.path.join(
            buildout['buildout']['parts-directory'], 
            self.name)
        if not os.path.isdir(destination):
            os.makedirs(destination)
        options.setdefault('destination', destination) 

        self.options['url'] = PACKAGES[options['version']]
        self.options['download-only'] = 'true'
        self.download = downloadRecipe(buildout, name, options)

    def _generate_from_template(self, **kwargs):
        destination = kwargs['destination']
        source = kwargs['source']
        name = kwargs['name']
        output_file = os.path.join(destination, name)
        with open(source, 'r') as template:
            template = NewTextTemplate(template)

        context = Context(name=name,
                          buildout=self.buildout['buildout'],
                          options=self.buildout[self.name],
                          additional=kwargs)
        try:
            output = template.generate(context).render()
        except (TemplateSyntaxError, UndefinedError) as e:
            raise zc.buildout.UserError(
                'Error in template {0:s}:\n{1:s}'.format(name, e.msg))

        with open(output_file, 'wb') as outfile:
            outfile.write(output.encode('utf8'))

        self.logger.info('Generated file %r.', name)

    def work(self):
        output = self.download.install()
        self._generate_from_template(
            destination='/tmp',
            source=self.template_dir,
            name='install.properties'
        )
        command = '/usr/bin/java -jar %s /tmp/install.properties' % output[0]
        print command
        os.system(command)

    @property
    def template_dir(self):
        return os.path.join(os.path.dirname(__file__), 'install.properties')

WORKER = {
    "4": Fedora4Worker,
    "3": Fedora3Worker
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

        if "tomcat-home" not in options:
            self.logger.error("No tomcat app directory specified")
            raise zc.buildout.UserError("No tomcat app directory specified")

        if options["version"] not in PACKAGES:
            self.logger.error("Specified version %s is not supported" % options['version'])
            raise zc.buildout.UserError("Specified version %s is not supported" % options['version'])

        worker_class = WORKER[options['version']]
        self.worker = worker_class(buildout, name, options, self.logger)

    def install(self):
        self.worker.work()
        return self.options.created()

    def update(self):
        return self.options.created()
