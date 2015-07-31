For fedora 3
--------------------

.. testcode::
   :hide:

    >>> # test set up
    >>> import mock
    >>> import shutil
    >>> import os
    >>> file_path = os.getcwd()
    >>> os.makedirs('/tmp/tomcat')
    >>> os.makedirs(os.path.join(file_path, 'parts', 'fedora3instance', 'install'))
    >>> shutil.copy(os.path.join(file_path, 'tests', 'sample.zip'), os.path.join(file_path, 'parts', 'fedora3instance', 'install', 'fedora.war'))
    >>> shutil.copy(os.path.join(file_path, 'tests', 'sample.zip'), '/tmp/test.zip')
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
    Installing fedora3instance.
    Downloading http://downloads.sourceforge.net/project/fedora-commons/fedora/3.7.0/fcrepo-installer-3.7.0.jar?r=&ts=1424278682&use_mirror=waia
    fedora3instance: Generated file '/tmp/install.properties'.
    fedora3instance: Unpack war file /home/ora/bodleian-recipie-fedorainstance/parts/fedora3instance/install/fedora.war to /tmp/tomcat/webapps/fedora


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

