FROM redis:bookworm
ARG user=user
ENV user=$user

RUN apt update && \
    apt -y install \
      libssl-dev \
      build-essential && \
    apt autoremove && \
    apt autoclean

ENV TERM xterm-256color

RUN groupadd $user && usermod -a -G $user redis

WORKDIR /project

COPY --chown=999:1000 ./docker/redis/redis.conf /etc/redis.conf
COPY --chmod=740 --chown=999:1000 ./docker/redis/entrypoint.sh /entrypoint.sh

RUN mkdir -p /tmp/redis && chown -R 999:1000 /tmp/redis
RUN mkdir -p /var/lib/redis && chown -R 999:999 /var/lib/redis

USER 999:1000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["redis-server", "/etc/redis.conf"]