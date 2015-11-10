Fedora 4 configuration 
------------------------

.. testcode::
   :hide:

    >>> # test set up
    >>> import mock
    >>> import shutil
    >>> import os
    >>> file_path = os.getcwd()
    >>> shutil.copy(os.path.join(file_path, 'tests', 'sample.zip'), '/tmp/test.zip')
    >>> patcher = mock.patch('hexagonit.recipe.download.Download') 
    >>> fake = patcher.start()
    >>> def fake_call(url, md5sum=None, path=None):
    ...     print "Downloading %s" % url
    ...     return '/tmp/test.zip', True
    >>> fake.return_value = fake_call

Here is an example configuration::

    >>> buildcfg = """
    ... [buildout]
    ... parts = fedorainstance
    ... 
    ... [fedorainstance]
    ... recipe = bodleian.recipe.fedorainstance
    ... version = 4
    ... tomcat-home = /tmp/tomcat
    ... fedora-url-suffix = fedora
    ... """
    >>> with open('buildout.cfg', 'w') as f:
    ...     f.write(buildcfg)


Here is what you see::

    >>> # you could have done it using commad line : buildout -c buildout.cfg
    >>> from zc.buildout.buildout import main
    >>> args = ['-c', 'buildout.cfg']
    >>> main(args) # doctest: +ELLIPSIS
    Creating directory .../parts'.
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
    >>> os.unlink("buildout.cfg")
    >>> os.unlink(".installed.cfg")
    >>> patcher.stop()

