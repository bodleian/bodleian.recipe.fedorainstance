bodleian.recipe.fedorainstance
==========================================================

bodleian.recipe.fedorainstance is a `Buildout <http://buildout.org/>`_ recipe to install a fedora webapp to your existing Tomcat container.

Usage
-----------
You must mention the recipe in your build out section::

    [your-build-target]
    recipe = bodleian.recipe.fedorainstance

Supported options
++++++++++++++++++++++++++

the recipe supports the following options:

``version``
    fedora version. Only 3 and 4 are valid inputs

``tomcat-home`` 
    tomcat installation directory.

``fedora-url-suffix``
    the url suffix that should lead to your fedora instance under tomcat. It should be only a single word.

Optional options
*********************

``url``
    the url to your fedora package. You may want to override the default download url.

``unpack-war-file``
    set 'false' will prevent the recipe to unpack war file to tomcat

``java-bin``
    override '/usr/bin/java' if your java is found somewhere else

Fedora 3 specific options
******************************

``install-properties``
    a key-value dictionary that you will need to supply to call **java -jar fcrepo-installer-3.x.jar** from command line.

