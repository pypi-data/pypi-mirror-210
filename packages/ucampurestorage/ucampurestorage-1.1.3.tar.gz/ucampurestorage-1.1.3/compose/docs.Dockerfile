FROM python
RUN mkdir /myapp
COPY ./ /myapp
COPY ./README.md /myapp/docs/README.md
RUN if [ -e /myapp/docs/README.rst ]; then rm /myapp/docs/README.rst; fi
RUN if [ -e /myapp/docs/readme.rst ]; then rm /myapp/docs/readme.rst; fi
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --no-cache-dir -r /myapp/requirements-dev.txt
WORKDIR /myapp
EXPOSE 8000
RUN /py/bin/m2r /myapp/docs/README.md
RUN rm /myapp/docs/README.md
WORKDIR /myapp/docs
RUN /py/bin/sphinx-build -M html . _build
WORKDIR /myapp
ENV PATH="/py/bin":$PATH
