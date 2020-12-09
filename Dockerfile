# Set the base image
FROM debian:latest

# File Author / Maintainer
LABEL maintainer="Jonathan Vlk <jonathan.vlk10@icloud.com>"

EXPOSE 80 443

# Install software dependencies
RUN apt-get update \
 && apt-get install -y python3 \
 && apt-get install -y python3-dev \
 && apt-get install -y python3-distutils \
 && apt-get install -y python3-venv \
 && apt-get install -y python3-pip \
 && apt-get install -y vim \
 && apt-get install -y apache2 \
 && apt-get install -y apache2-dev \
 && apt-get install -y libapache2-mod-wsgi-py3 \
 && apt-get install -y build-essential \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y \
 && apt-get install freetds-dev -y \
 && apt-get install freetds-bin -y \
 && apt-get install tdsodbc -y \
 && apt-get install --reinstall build-essential -y \
 && apt-get clean \
 && apt-get autoremove \
 && rm -rf /var/lib/apt/lists/*

# Populate "ocbcinst.ini" as this is where ODBC driver config sits
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

# Copy over and install the requirements
COPY ./app/requirements.txt /var/www/myplaid-api/app/requirements.txt
RUN pip3 install -r /var/www/myplaid-api/app/requirements.txt

# Copy over the apache configuration file and enable the site with SSL
COPY apache2/myplaid-api.conf /etc/apache2/sites-available/myplaid-api.conf
COPY apache2/options-ssl-apache.conf /etc/letsencrypt/
RUN a2ensite myplaid-api
RUN a2enmod headers
RUN a2enmod ssl
RUN a2enmod wsgi

# Copy over the app and wsgi file
COPY ./myplaid_api.wsgi /var/www/myplaid-api/
COPY ./run.py /var/www/myplaid-api/run.py
COPY ./app /var/www/myplaid-api/app/

RUN a2dissite 000-default.conf
RUN a2ensite myplaid-api.conf

# LINK apache config to docker logs.
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

ENV PLAID_CLIENT_ID=5e68621e21bd680012508840
ENV PLAID_sSECRET=663baf40e4e8b938ff0eac6153a4ca
# ENV PLAID_dSECRET=36bf8dc0d15ba78b274f1247723b66
ENV PLAID_PUBLIC_KEY=615ca4d86144ea9ab81020b1778252
ENV CONN_STR_MYPLAID="DRIVER={/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so};SERVER=host.docker.internal,49854;DATABASE=myplaid;UID=svcmyplaid;PWD=svcmyplaidPwd_23809023"

CMD /usr/sbin/apache2ctl -D FOREGROUND

