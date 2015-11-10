bodleian.recipe.fedorainstance
==========================================================

.. image:: https://travis-ci.org/bodleian/bodleian.recipe.fedorainstance.svg?branch=master
    :target: https://travis-ci.org/bodleian/bodleian.recipe.fedorainstance
.. image:: https://coveralls.io/repos/bodleian/bodleian.recipe.fedorainstance/badge.svg
    :target: https://coveralls.io/r/bodleian/bodleian.recipe.fedorainstance
.. image:: http://img.shields.io/badge/license-MIT-brightgreen.svg
    :target: https://github.com/bodleian/bodleian.recipe.fedorainstance/blob/master/LICENSE

bodleian.recipe.fedorainstance is a `Buildout <http://buildout.org/>`_ recipe 
to install an unpacked fedora webapp to your existing Tomcat container.

Usage
-----------
You must mention the recipe in your build out section::

    [your-build-target]
    recipe = bodleian.recipe.fedorainstance

Supported options
++++++++++++++++++++++++++

the recipe supports the following options:

``version``
    fedora version. Valid values are: 4, 3, 3.8, 3.7, 2.2.4 And version 3.7 is 
    a default for ``version`` = 3.  Default configurations can be found in 
    *bodleian/recipe/fedorainstance/recipe_config.ini*

``tomcat-home`` 
    tomcat installation directory.

``fedora-url-suffix``
    the url suffix that should lead to your fedora instance under tomcat. It 
    should be only a single word. This is not applicable when ``version`` is set
    to 2.

Optional options
*********************

``url``
    the url to your fedora package. You may want to override the default 
    download url in *bodleian/recipe/fedorainstance/recipe_config.ini*.

``unpack-war-file``
    set 'false' will prevent the recipe from unpacking the fedora war file to 
    tomcat webapps. In other words, it instructs this recipe to copy the war
    to tomcat webapps directory only.

``java-bin``
    override '/usr/bin/java' if your java is found somewhere else

Fedora 2 and 3 specific options
******************************

``overwrite-existing``
   a signal to the reciepe to clear the destination directory with the
   new content. The previous content is backed up in /tmp. Please
   check your build log when you have put the stone on your toe, for
   example, your fedora buldout got important data that you regretted
   to use overwrite-existing==true.

``install-properties``
    a key-value dictionary that you will need to supply to call 
    **java -jar fcrepo-installer-3.x.jar** from command line. 

An example is::

    [your-build-target]
    recipe = bodleian.recipe.fedorainstance
    version = 3
    tomcat-home = /tmp/tomcat
    fedora-url-suffix = fedora
    unpack-war-file = true
    install-properties = 
        keystore.file=included
        ri.enabled=true
        messaging.enabled=false
        apia.auth.required=false
        ...
        fedora.serverContext=${your-build-target:fedora-url-suffix}

.. note::

   For feodra 3, please set
    **fedora.serverContext=${your-build-target:fedora-url-suffix}** in install-properties.
   Otherwise, this recipe cannot find the fedora war file for deploying it to tomcat

Development
-------------------

Please fork it to your repo and then submit merge requests. 
Here is how you do tests::

    $ python setup.py install
    $ pip install -r tests/requirements.txt
    $ make
