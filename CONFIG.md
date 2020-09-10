# config.js Explained

*JavaScript for Data Scientists*

## What config.js Does

The config.js file allows the Lambda School Labs 26 Citrics Team A Data Scientist to choose whether to build the team Docker image and deploy to the team AWS application or build his personal Docker image and deploy to his own application.

## Installing node.js

### What is node.js, and why do I need to install it?

node.js is a local JavaScript runtime which allows developers to build and test apps locally before hosting them online. Unlike Python, which is built into the MacOS operating system, since JavaScript is native to the web, without installing a runtime such as node.js, developers are incapable of running JavaScript files locally in command line or terminal. Therefore, you will need to download node.js in order to run config.js in command line or terminal.

Here is the link to the [download page](https://nodejs.org/en/download/) for node.js, and here are [instructions for setup in Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04).

## Using config.js

The simplest part of this README;
in command line or terminal, simply type:

```
node config.js
```

You should see a message in command line or terminal prompting you to enter your Docker ID:

```
Docker ID:
----------
```

Simply input your Docker ID if building and pushing to your personal AWS app. If building and pushing to the team app, use *Aaron Watkins'* Docker ID **ekselan**.  In the former case, you'll be greeted with the following in command line or terminal:

```
YOUR_DOCKER_ID
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "YOUR_DOCKER_ID/labs26-citrics-ds-teama_web:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ],
  "Command": "uvicorn app.main:app --workers 1 --host 0.0.0.0 --port 8000"
}
writing to ./Dockerrun.aws.json
```

Double check that the Dockerrun.aws.json file is up to date, and you can proceed with pushing to docker and deploying to AWS.