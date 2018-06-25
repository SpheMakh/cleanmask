FROM stimela/base:1.0.0
RUN pip install --upgrade pip setuptools
ADD . /tmp/cleanmask
RUN pip install /tmp/cleanmask
RUN cleanmask --help
