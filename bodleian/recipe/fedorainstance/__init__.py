import logging
import os
import zipfile
import zc.buildout
from genshi.template import Context
from genshi.template import NewTextTemplate
from genshi.template.base import TemplateSyntaxError
from genshi.template.eval import UndefinedError


from hexagonit.recipe.download import Recipe as downloadRecipe

# buildout options
BUILDOUT = 'buildout'
FIELD_TOMCAT_HOME = 'tomcat-home'
FIELD_FEDORA_URL_SUFFIX = 'fedora-url-suffix'
FIELD_FEDORA_VERSION = 'version'
FIELD_UNPACK_WAR_FILE = 'unpack-war-file'
FIELD_DESTINATION = 'destination'
FIELD_URL = 'url'

# internal constants
DEFAULT_JAVA_COMMAND = '/usr/bin/java'
DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME = 'webapps'
DEFAULT_FEDORA3_INSTALL_PROPERTIES = 'install.properties'
DEFAULT_FEDORA3_WAR_FILE_FOLDER = 'install'
DEFAULT_TMP_DIR = '/tmp'
DEFAULT_FEDORA_WAR_FILE_NAME = 'fedora.war'
FEDORA3 = '3'
FEDORA4 = '4'

# messages
MESSAGE_MISSING_VERSION = "No version specified"
MESSAGE_MISSING_TOMCAT_HOME = "No tomcat app directory specified"
MESSAGE_NOT_SUPPORTED_VERSION = "Specified version %s is not supported"

PACKAGES = {
    FEDORA4: "https://github.com/fcrepo4/fcrepo4/releases/download/fcrepo-4.2.0/fcrepo-webapp-4.2.0.war",
    #"4": "http://localhost:8000/fcrepo-webapp-4.2.0.war",
    FEDORA3: "http://10.0.2.15:8000/fcrepo-installer-3.7.0.jar"
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

        options.setdefault(FIELD_DESTINATION,
                           os.path.join(options[FIELD_TOMCAT_HOME],
                                        DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME,
                                        options[FIELD_FEDORA_URL_SUFFIX]))

        self.options[FIELD_URL] = PACKAGES[options[FIELD_FEDORA_VERSION]]
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
            buildout[BUILDOUT]['parts-directory'], 
            self.name)
        import pdb; pdb.set_trace()
        if not os.path.isdir(destination):
            os.makedirs(destination)
        options.setdefault(FIELD_DESTINATION, destination) 

        download_options = {
            FIELD_URL: PACKAGES[options[FIELD_FEDORA_VERSION]],
            'download-only': 'true',
            FIELD_DESTINATION: DEFAULT_TMP_DIR
        }
        self.download = downloadRecipe(buildout, name, download_options)

    def _generate_from_template(self, **kwargs):
        output_file = kwargs['output_file']
        source = kwargs['source']
        with open(source, 'r') as template:
            template = NewTextTemplate(template)

        context = Context(buildout=self.buildout[BUILDOUT],
                          options=self.buildout[self.name],
                          additional=kwargs)
        try:
            output = template.generate(context).render()
        except (TemplateSyntaxError, UndefinedError) as e:
            raise zc.buildout.UserError(
                'Error in template {0:s}:\n{1:s}'.format(output_file, e.msg))

        with open(output_file, 'wb') as outfile:
            outfile.write(output.encode('utf8'))

        self.logger.info('Generated file %r.', output_file)

    def work(self):
        output = self.download.install()
        self._generate_from_template(
            output_file=self.tmp_install_properties,
            source=self.install_properties,
        )
        command = '%s -jar %s %s' % (DEFAULT_JAVA_COMMAND,
                                     output[0],
                                     self.tmp_install_properties)
        os.system(command)
        if self.options.get(FIELD_UNPACK_WAR_FILE, '') == 'true':
            fedora_war = os.path.join(self.options[FIELD_DESTINATION],
                                      DEFAULT_FEDORA3_WAR_FILE_FOLDER,
                                      DEFAULT_FEDORA_WAR_FILE_NAME)
            tomcat_webapp = os.path.join(
                self.options[FIELD_TOMCAT_HOME],
                DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME,
                self.options[FIELD_FEDORA_URL_SUFFIX])
            self.logger.info('Unpack war file %s to %s', fedora_war, tomcat_webapp)
            with zipfile.ZipFile(fedora_war) as zip_file:
                zip_file.extractall(tomcat_webapp)

    @property
    def install_properties(self):
        return os.path.join(os.path.dirname(__file__),
                            DEFAULT_FEDORA3_INSTALL_PROPERTIES)
    @property
    def tmp_install_properties(self):
        return os.path.join(DEFAULT_TMP_DIR,
                            DEFAULT_FEDORA3_INSTALL_PROPERTIES)

WORKER = {
    FEDORA4: Fedora4Worker,
    FEDORA3: Fedora3Worker
}

class FedoraRecipe:
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        # validate options
        if FIELD_FEDORA_VERSION not in options:
            self.logger.error(MESSAGE_MISSING_VERSION)
            raise zc.buildout.UserError(MESSAGE_MISSING_VERSION)

        if FIELD_TOMCAT_HOME not in options:
            self.logger.error(MESSAGE_MISSING_TOMCAT_HOME)
            raise zc.buildout.UserError(MESSAGE_MISSING_TOMCAT_HOME)

        if options[FIELD_FEDORA_VERSION] not in PACKAGES:
            message = MESSAGE_NOT_SUPPORTED_VERSION % options[FIELD_FEDORA_VERSION]
            self.logger.error(message)
            raise zc.buildout.UserError(message)

        # choose worker class
        worker_class = WORKER[options[FIELD_FEDORA_VERSION]]
        self.worker = worker_class(buildout, name, options, self.logger)

    def install(self):
        self.worker.work()
        return self.options.created()

    def update(self):
        return self.options.created()
