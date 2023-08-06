FROM python
RUN mkdir /myapp
COPY ./ /myapp
RUN pip install --upgrade pip && pip install --no-cache-dir -r /myapp/requirements-docs.txt
