Usage
=======

For fedora 4
--------------------

.. testcode::
   :hide:

    >>> # test set up
    >>> import mock
    >>> import shutil
    >>> import os

For fedora 3
--------------------

.. testcode::
   :hide:

    >>> # test set up
    >>> file_path = os.getcwd()
    >>> os.makedirs(os.path.join(file_path, 'parts', 'fedora3instance'))
    >>> shutil.copy(os.path.join(file_path, 'tests', 'sample.zip'), os.path.join(file_path, 'parts', 'fedora3instance', 'fedora.war'))
    >>> patcher = mock.patch('hexagonit.recipe.download.Download') 
    >>> fake = patcher.start()
    >>> def fake_call(url, md5sum=None, path=None):
    ...     print "Downloading %s" % url
    ...     return '/tmp/test.zip', True
    >>> fake.return_value = fake_call
    >>> patcher2 = mock.patch('bodleian.recipe.fedorainstance.DEFAULT_JAVA_COMMAND', first="echo /usr/bin/java")
    >>> patcher2.start()

Here is a sample configuration file::

    >>> buildcfg = """
    ... [buildout]
    ... parts = fedora3instance
    ... 
    ... [fedora3instance]
    ... recipe = bodleian.recipe.fedorainstance
    ... version = 3
    ... tomcat-home = /tmp/tomcat
    ... fedora-url-suffix = fedora
    ... unpack-war-file = true
    ... """
    >>> with open('buildout.cfg', 'w') as f:
    ...     f.write(buildcfg)

Here is what you see::

    >>> # you could have done it using commad line : buildout -c buildout.cfg
    >>> from zc.buildout.buildout import main
    >>> args = ['-c', 'buildout.cfg']
    >>> main(args)
    Installing fedorainstance.
    Downloading https://github.com/fcrepo4/fcrepo4/releases/download/fcrepo-4.2.0/fcrepo-webapp-4.2.0.war
    fedorainstance: Extracting package to /tmp/tomcat/webapps/fedora


.. testcode::
   :hide:

    >>> # test verification
    >>> import glob
    >>> print glob.glob("/tmp/tomcat/webapps/fedora/*")
    ['/tmp/tomcat/webapps/fedora/you_have_tested_it']
    >>> shutil.rmtree("/tmp/tomcat")
    >>> shutil.rmtree("./parts")
    >>> os.unlink("buildout.cfg")
    >>> patcher.stop()

