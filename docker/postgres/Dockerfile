FROM postgres:latest
ARG user=user
ENV user=$user

ENV TERM xterm-256color

RUN groupadd $user && usermod -aG $user postgres

COPY --chmod=740 --chown=1000:1000 ./docker/postgres/entrypoint.sh /entrypoint.sh

USER 1000:1000
