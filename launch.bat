python setup.py install
python setup.py nosetests
sphinx-apidoc wuhan_data -o doc -f -e
python setup.py build_sphinx
scrapyd-deploy