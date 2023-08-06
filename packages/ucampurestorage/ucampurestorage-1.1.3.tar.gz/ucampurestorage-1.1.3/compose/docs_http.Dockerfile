FROM httpd
COPY ./docs/_build/html/ /usr/local/apache2/htdocs/
EXPOSE 80
