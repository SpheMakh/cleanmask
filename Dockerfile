FROM kernsuite/base:3
RUN docker-apt-install python-pip
RUN pip install --upgrade pip setuptools
ADD . /tmp/cleanmask
RUN pip install /tmp/cleanmask
RUN cleanmask --help
