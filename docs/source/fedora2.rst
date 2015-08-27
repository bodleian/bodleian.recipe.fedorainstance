Fedora 2 configuration
------------------------

.. testcode::
   :hide:

    >>> # test set up
    >>> import mock
    >>> import shutil
    >>> import os
    >>> file_path = os.getcwd()
    >>> os.makedirs('/tmp/tomcat/webapps')
    >>> os.makedirs(os.path.join(file_path, 'parts', 'fedora3instance', 'install'))
    >>> shutil.copy(os.path.join(file_path, 'tests', 'sample.zip'), os.path.join(file_path, 'parts', 'fedora3instance', 'install', 'fedora.war'))
    >>> shutil.copy(os.path.join(file_path, 'tests', 'sample.zip'), '/tmp/test.zip')
    >>> shutil.copy(os.path.join(file_path, 'tests', 'sample.zip'), '/tmp/tomcat/webapps/fedora.war')
    >>> patcher = mock.patch('hexagonit.recipe.download.Download') 
    >>> fake = patcher.start()
    >>> def fake_call(url, md5sum=None, path=None):
    ...     print "Downloading %s" % url
    ...     return '/tmp/test.zip', True
    >>> fake.return_value = fake_call
    >>> patcher2 = mock.patch('bodleian.recipe.fedorainstance.DEFAULT_JAVA_COMMAND', "echo /usr/bin/java")
    >>> x = patcher2.start()

Here is a sample configuration file::

    >>> buildcfg = """
    ... [buildout]
    ... parts = fedora2instance
    ... 
    ... [fedora2instance]
    ... recipe = bodleian.recipe.fedorainstance
    ... version = 2
    ... tomcat-home = /tmp/tomcat
    ... unpack-war-file = true
    ... install-properties = 
    ...     keystore.file=included
    ...     ri.enabled=true
    ...     messaging.enabled=false
    ...     apia.auth.required=false
    ...     database.jdbcDriverClass=com.mysql.jdbc.Driver
    ...     upstream.auth.enabled=false
    ...     tomcat.ssl.port=8443
    ...     ssl.available=true
    ...     database.jdbcURL=jdbc\:mysql\://localhost/fedora22?useUnicode\=true&amp;characterEncoding\=UTF-8&amp;autoReconnect\=true
    ...     database.password=fedoraAdmin
    ...     database.mysql.driver=included
    ...     database.username=fedoraAdmin
    ...     fesl.authz.enabled=false
    ...     tomcat.shutdown.port=8005
    ...     deploy.local.services=false
    ...     xacml.enabled=true
    ...     database.mysql.jdbcDriverClass=com.mysql.jdbc.Driver
    ...     tomcat.http.port=8080
    ...     fedora.serverHost=localhost
    ...     database=mysql
    ...     database.driver=included
    ...     fedora.serverContext=fedora2
    ...     llstore.type=legacy-fs
    ...     tomcat.home=/home/ora/sites/ora/parts/tomcat6
    ...     fedora.home=/home/ora/sites/ora/parts/fedora2
    ...     database.mysql.jdbcURL=jdbc\:mysql\://localhost/fedora22?useUnicode\=true&amp;characterEncoding\=UTF-8&amp;autoReconnect\=true
    ...     install.type=custom
    ...     servlet.engine=existingTomcat
    ...     apim.ssl.required=false
    ...     fedora.admin.pass=fedoraAdmin
    ...     apia.ssl.required=false
    ... 
    ... [example]
    ... servername = localhost
    ... fedora = localhost
    ... mysql = localhost
    ... tomcat6 = 8080
    ... fedora = 8080
    ... mysql = 8080
    ... fedoraAdmin = admin
    ... """
    >>> with open('buildout.cfg', 'w') as f:
    ...     f.write(buildcfg)

Here is what you see::

    >>> # you could have done it using commad line : buildout -c buildout.cfg
    >>> from zc.buildout.buildout import main
    >>> args = ['-c', 'buildout.cfg']
    >>> main(args)
    Installing fedora2instance.
    Downloading http://downloads.sourceforge.net/project/fedora-commons/fedora/2.2.4/fedora-2.2.4-installer.jar?ts=1440584405&use_mirror=waia
    fedora2instance: Unpack war file /tmp/tomcat/webapps/fedora.war to /tmp/tomcat/webapps/fedora
    fedora2instance: removing /tmp/tomcat/webapps/fedora.war


.. testcode::
   :hide:

    >>> # test verification
    >>> import glob
    >>> print glob.glob("/tmp/tomcat/webapps/fedora/*")
    ['/tmp/tomcat/webapps/fedora/you_have_tested_it']
    >>> shutil.rmtree("/tmp/tomcat")
    >>> shutil.rmtree("./parts")
    >>> os.unlink("buildout.cfg")
    >>> os.unlink(".installed.cfg")
    >>> patcher2.stop()
    >>> patcher.stop()

