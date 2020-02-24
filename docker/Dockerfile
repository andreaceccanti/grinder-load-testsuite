FROM  italiangrid/storm-testsuite:nightly

USER root

COPY setup.sh .
RUN chmod +x setup.sh
RUN ./setup.sh

WORKDIR /home/tester

USER tester