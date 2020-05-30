FROM node:12-alpine as build

WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
RUN npm install --silent --producton
RUN npm install react-scripts@3.0.1 -g --silent
COPY . ./
EXPOSE 3000

CMD ["npm", "start"]