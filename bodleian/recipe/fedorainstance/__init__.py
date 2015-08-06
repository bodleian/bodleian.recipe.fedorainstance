import os
import re
import logging
import zipfile
import tempfile
import zc.buildout
import ConfigParser
from hexagonit.recipe.download import Recipe as downloadRecipe

# buildout options
BUILDOUT = 'buildout'
FIELD_FEDORA_VERSION = 'version'
FIELD_TOMCAT_HOME = 'tomcat-home'
FIELD_FEDORA_URL_SUFFIX = 'fedora-url-suffix'
FIELD_UNPACK_WAR_FILE = 'unpack-war-file'
FIELD_INSTALL_PROPERTIES = 'install-properties'
FIELD_URL = 'url'
FIELD_JAVA_BIN = 'java-bin'

# internal download recipe options
FIELD_DESTINATION = 'destination'
FIELD_DOWNLOAD_ONLY = 'download-only'

# internal constants
DEFAULT_JAVA_COMMAND = '/usr/bin/java'
DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME = 'webapps'
DEFAULT_FEDORA3_INSTALL_PROPERTIES = 'install.properties'
DEFAULT_FEDORA3_WAR_FILE_FOLDER = 'install'
DEFAULT_FEDORA_NAME = 'fedora'
FEDORA3 = '3'
FEDORA4 = '4'

# configurations
DEFAULT_CONFIG_INI_FILE = 'recipe_config.ini'
SECTION_PACKAGES = 'packages'

# messages
MESSAGE_MISSING_VERSION = "No version specified"
MESSAGE_MISSING_TOMCAT_HOME = "No tomcat app directory specified"
MESSAGE_NOT_SUPPORTED_VERSION = "Specified version %s is not supported"
MESSAGE_SINGLE_WORD = "A single word is expected"


# utility function
def is_single_word(word):
    """
    test if a string contains single word or not
    """
    return re.match(r'\A[\w-]+\Z', word)


class FedoraWorker:
    """
    A genuine fedora worker
    """
    def __init__(self, buildout, name, options, logger, config):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logger
        self.config = config

        # it should download something
        self.download = downloadRecipe(buildout, name,
                                       self.get_download_options())

    def get_download_options(self):
        return {}

    def work(self):
        """
        it should install fedora
        """
        pass


class Fedora4Worker(FedoraWorker):
    """
    Install Fedora 4
    """
    def get_download_options(self):
        """
        Instruct download recipe to deploy war file to
        tomcat webapps directory
        """
        download_options = {
            FIELD_DESTINATION: os.path.join(
                self.options[FIELD_TOMCAT_HOME],
                DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME,
                self.options[FIELD_FEDORA_URL_SUFFIX])
        }
        if self.options.get(FIELD_URL, None) is None:
            download_options[FIELD_URL] = self.config.get(
                SECTION_PACKAGES,
                self.options[FIELD_FEDORA_VERSION]
            )
        else:
            download_options[FIELD_URL] = self.options.get(FIELD_URL)

        if self.options.get(FIELD_UNPACK_WAR_FILE, None) != 'true':
            download_options['download-only'] = 'true'

        return download_options

    def work(self):
        """
        Go! download it
        """
        output = self.download.install()
        return [output]


class Fedora3Worker(FedoraWorker):
    """
    Install Fedora 3
    """
    def __init__(self, buildout, name, options, logger, config):
        FedoraWorker.__init__(self,
                              buildout, name, options,
                              logger, config)
        if options.get(FIELD_JAVA_BIN, None) is None:
            options[FIELD_JAVA_BIN] = DEFAULT_JAVA_COMMAND

    def get_download_options(self):
        """
        Instruct download recipe to get the fedora installer
        """
        destination = os.path.join(
            self.buildout[BUILDOUT]['parts-directory'],
            self.name)
        if not os.path.isdir(destination):
            os.makedirs(destination)
        self.options.setdefault(FIELD_DESTINATION, destination)

        download_options = {
            'download-only': 'true',
            FIELD_DESTINATION: tempfile.gettempdir()
        }
        if self.options.get(FIELD_URL, None) is None:
            download_options[FIELD_URL] = self.config.get(
                SECTION_PACKAGES,
                self.options[FIELD_FEDORA_VERSION]
            )
        return download_options

    def work(self):
        """
        Install fedora to parts and deploy the war file
        """
        output = self.download.install()
        with open(self.tmp_install_properties, 'w') as f:
            f.write(self.options[FIELD_INSTALL_PROPERTIES])
        command = '%s -jar %s %s' % (
            self.options[FIELD_JAVA_BIN],
            output[0],
            self.tmp_install_properties)
        os.system(command)
        if self.options.get(FIELD_UNPACK_WAR_FILE, '') == 'true':
            default_fedora_war_file_name = (
                "%s.war" % self.options[FIELD_FEDORA_URL_SUFFIX])
            fedora_war = os.path.join(
                self.options[FIELD_DESTINATION],
                DEFAULT_FEDORA3_WAR_FILE_FOLDER,
                default_fedora_war_file_name)
            tomcat_webapp = os.path.join(
                self.options[FIELD_TOMCAT_HOME],
                DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME,
                self.options[FIELD_FEDORA_URL_SUFFIX])
            self.logger.info('Unpack war file %s to %s',
                             fedora_war,
                             tomcat_webapp)
            with zipfile.ZipFile(fedora_war) as zip_file:
                zip_file.extractall(tomcat_webapp)

    @property
    def tmp_install_properties(self):
        return os.path.join(tempfile.gettempdir(),
                            DEFAULT_FEDORA3_INSTALL_PROPERTIES)


# update this worker dictionary to get new ones
WORKER = {
    FEDORA4: Fedora4Worker,
    FEDORA3: Fedora3Worker
}


class FedoraWorkerFactory:
    """
    Worker factory to get a fedora worker per major version
    """
    @staticmethod
    def get_worker(version):
        if version is None:
            return None
        prime_version = version[0]
        return WORKER.get(prime_version, None)


class FedoraRecipe:
    """
    The entry class for buildout
    """
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        self.config = ConfigParser.RawConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__),
                                      DEFAULT_CONFIG_INI_FILE))

        # validate options
        if FIELD_FEDORA_VERSION not in options:
            self._raise_user_error_exception(MESSAGE_MISSING_VERSION)

        if FIELD_TOMCAT_HOME not in options:
            self._raise_user_error_exception(MESSAGE_MISSING_TOMCAT_HOME)

        if FIELD_FEDORA_URL_SUFFIX not in options:
            self.options[FIELD_FEDORA_URL_SUFFIX] = DEFAULT_FEDORA_NAME
        else:
            if not is_single_word(self.options[FIELD_FEDORA_URL_SUFFIX]):
                self._raise_user_error_exception(MESSAGE_SINGLE_WORD)

        if not self.config.has_option(SECTION_PACKAGES,
                                      options[FIELD_FEDORA_VERSION]):
            self._raise_not_supported_version_exception()
        if options.get(FIELD_UNPACK_WAR_FILE, None) is None:
            options[FIELD_UNPACK_WAR_FILE] = 'true'

        # choose worker class
        worker_class = FedoraWorkerFactory.get_worker(
            options[FIELD_FEDORA_VERSION]
        )
        if worker_class is None:
            self._raise_not_supported_version_exception()
        self.worker = worker_class(buildout, name, options,
                                   self.logger, self.config)

    def _raise_user_error_exception(self, message):
        self.logger.error(message)
        raise zc.buildout.UserError(message)

    def _raise_not_supported_version_exception(self):
        message = (
            MESSAGE_NOT_SUPPORTED_VERSION % self.options[FIELD_FEDORA_VERSION])
        self.logger.error(message)
        raise zc.buildout.UserError(message)

    def install(self):
        self.worker.work()
        return self.options.created()

    def update(self):
        return self.options.created()
