from bodleian.recipe.fedorainstance import FedoraRecipe
from bodleian.recipe.fedorainstance import (
    FIELD_FEDORA_VERSION,
    FIELD_TOMCAT_HOME,
    FIELD_FEDORA_URL_SUFFIX,
    FIELD_URL,
    FIELD_UNPACK_WAR_FILE
)
from nose.tools import raises
from zc.buildout import UserError


@raises(UserError)
def test_version_key():
    FedoraRecipe(None, None, {})


@raises(UserError)
def test_tomcat_home_key():
    FedoraRecipe(None, None, {FIELD_FEDORA_VERSION: "3"})


@raises(UserError)
def test_fedora_suffix_key():
    FedoraRecipe(None, None, {
        FIELD_FEDORA_VERSION: "3",
        FIELD_TOMCAT_HOME: "test",
        FIELD_FEDORA_URL_SUFFIX: "too many words"
    })


@raises(UserError)
def test_fedora_version_key():
    FedoraRecipe(None, None, {
        FIELD_FEDORA_VERSION: "100",
        FIELD_TOMCAT_HOME: "test",
        FIELD_FEDORA_URL_SUFFIX: "fedora"
    })

def test_fedora_4_key():
    FedoraRecipe({"buildout": {"parts-directory": "/tmp"}}, "test", {
        FIELD_FEDORA_VERSION: "4",
        FIELD_TOMCAT_HOME: "test",
        FIELD_URL: "http",
        FIELD_UNPACK_WAR_FILE: "false"
    })


