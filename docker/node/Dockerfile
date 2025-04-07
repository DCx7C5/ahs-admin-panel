FROM node
ARG user=user
ENV user=$user

RUN npm install -g npm@latest

ENV TERM=xterm-256color

WORKDIR /project/frontend/

COPY --chmod=740 --chown=1000:1000 docker/node/entrypoint.sh /entrypoint.sh

USER 1000:1000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["npm", "run", "dev"]
