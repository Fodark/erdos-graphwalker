# FROM gcr.io/distroless/nodejs
# WORKDIR /app

# ENV PATH /app/node_modules/.bin:$PATH

# COPY package.json /app/package.json
# RUN npm install --silent
# RUN npm install react-scripts@3.0.1 -g --silent

# CMD ["npm", "start"]

FROM node:12-alpine as build

WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json /app/package.json
RUN npm install
RUN npm install react-scripts@3.0.1 --silent
EXPOSE 3000

CMD ["npm", "start"]

#FROM node:12-alpine

#COPY --from=build /app /