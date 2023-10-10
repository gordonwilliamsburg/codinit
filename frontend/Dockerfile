# Start from the official Node.js LTS base image
FROM node:18.16.0

# Set the working directory
WORKDIR /codinit

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install
RUN npm install react-console-emulator

# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# You can learn more about what data is collected and how it's used at https://nextjs.org/telemetry.
# Telemetry collection is enabled by default and can be opted-out of by users at any time through our docs https://nextjs.org/docs/advanced-features/telemetry
# Uncomment the following line in case you want to disable telemetry.
# RUN npx next telemetry disable

# Open the mapped port
EXPOSE 3000

# Start the app
CMD [ "npm", "run", "dev" ]
