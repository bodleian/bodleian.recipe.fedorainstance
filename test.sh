if [ -f '.installed.cfg' ]
then
    rm .installed.cfg
fi
nosetests --rednose --with-cov --cov bodleian --cov tests --with-doctest --doctest-extension=.rst
