import logging
import os
import zipfile
import zc.buildout
import re


from hexagonit.recipe.download import Recipe as downloadRecipe

# buildout options
BUILDOUT = 'buildout'
FIELD_TOMCAT_HOME = 'tomcat-home'
FIELD_FEDORA_URL_SUFFIX = 'fedora-url-suffix'
FIELD_FEDORA_VERSION = 'version'
FIELD_UNPACK_WAR_FILE = 'unpack-war-file'
FIELD_DESTINATION = 'destination'
FIELD_URL = 'url'
FIELD_DOWNLOAD_ONLY = 'download-only'

# internal constants
DEFAULT_JAVA_COMMAND = '/usr/bin/java'
DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME = 'webapps'
DEFAULT_FEDORA3_INSTALL_PROPERTIES = 'install.properties'
DEFAULT_FEDORA3_WAR_FILE_FOLDER = 'install'
DEFAULT_TMP_DIR = '/tmp'
FEDORA3 = '3'
FEDORA4 = '4'

# messages
MESSAGE_MISSING_VERSION = "No version specified"
MESSAGE_MISSING_TOMCAT_HOME = "No tomcat app directory specified"
MESSAGE_NOT_SUPPORTED_VERSION = "Specified version %s is not supported"
MESSAGE_SINGLE_WORD = "A single word is expected"

PACKAGES = {
    FEDORA4: "https://github.com/fcrepo4/fcrepo4/releases/download/fcrepo-4.2.0/fcrepo-webapp-4.2.0.war",
    FEDORA3: "http://downloads.sourceforge.net/project/fedora-commons/fedora/3.7.0/fcrepo-installer-3.7.0.jar?r=&ts=1424278682&use_mirror=waia"
}


def is_single_word(word):
    """
    test if a string contains single word or not
    """
    return re.match(r'\A[\w-]+\Z', word)


class Fedora4Worker:
    """
    Install Fedora 4
    """
    def __init__(self, buildout, name, options, logger):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logger

        download_options = {
            FIELD_DESTINATION: os.path.join(
                options[FIELD_TOMCAT_HOME],
                DEFAULT_TOMCAT_WEBAPPS_FOLDER_NAME,
                options[FIELD_FEDORA_URL_SUFFIX])
        }
        if self.options.get(FIELD_URL, None) is None:
            download_options[FIELD_URL] = PACKAGES[
                options[FIELD_FEDORA_VERSION]
            ]
        else:
            download_options[FIELD_URL] = self.options.get(FIELD_URL)

        if self.options.get(FIELD_UNPACK_WAR_FILE, None) != 'true':
            download_options['download-only'] = 'true'

        self.download = downloadRecipe(buildout, name, download_options)

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
        if not os.path.isdir(destination):
            os.makedirs(destination)
        options.setdefault(FIELD_DESTINATION, destination)

        download_options = {
            'download-only': 'true',
            FIELD_DESTINATION: DEFAULT_TMP_DIR
        }
        if self.options.get(FIELD_URL, None) is None:
            download_options[FIELD_URL] = PACKAGES[
                options[FIELD_FEDORA_VERSION]
            ]

        self.download = downloadRecipe(buildout, name, download_options)

    def work(self):
        output = self.download.install()
        with open(self.tmp_install_properties, 'w') as f:
            f.write(self.options['install-properties'])
        command = '%s -jar %s %s' % (DEFAULT_JAVA_COMMAND,
                                     output[0],
                                     self.tmp_install_properties)
        os.system(command)
        if self.options.get(FIELD_UNPACK_WAR_FILE, '') == 'true':
            default_fedora_war_file_name = ("%s.war"
                % self.options[FIELD_FEDORA_URL_SUFFIX])
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
        return os.path.join(DEFAULT_TMP_DIR,
                            DEFAULT_FEDORA3_INSTALL_PROPERTIES)

WORKER = {
    FEDORA4: Fedora4Worker,
    FEDORA3: Fedora3Worker
}


class FedoraRecipe:
    """
    The entry class for buildout
    """
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

        if FIELD_FEDORA_URL_SUFFIX not in options:
            self.options[FIELD_FEDORA_URL_SUFFIX] = 'fedora'
        else:
            if not is_single_word(self.options[FIELD_FEDORA_URL_SUFFIX]):
                self.logger.error(MESSAGE_SINGLE_WORD)
                raise zc.buildout.UserError(MESSAGE_SINGLE_WORD)

        if options[FIELD_FEDORA_VERSION] not in PACKAGES:
            message = (MESSAGE_NOT_SUPPORTED_VERSION 
                        % options[FIELD_FEDORA_VERSION])
            self.logger.error(message)
            raise zc.buildout.UserError(message)
        if options.get(FIELD_UNPACK_WAR_FILE, None) is None:
            options[FIELD_UNPACK_WAR_FILE] = 'true'

        # choose worker class
        worker_class = WORKER[options[FIELD_FEDORA_VERSION]]
        self.worker = worker_class(buildout, name, options, self.logger)

    def install(self):
        self.worker.work()
        return self.options.created()

    def update(self):
        return self.options.created()
