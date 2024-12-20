FROM node:14 

#set working directory inside container
WORKDIR /frontend

#copy files to leverage docker cache
COPY package*.json ./

#install dependencies
RUN npm install

#copy the entire frontend directory to the container
COPY . .

#build the frontend
RUN npm run build

#expose the port
EXPOSE 3000

#start the frontend
CMD ["npm", "start"]
