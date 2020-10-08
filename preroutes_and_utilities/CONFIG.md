# config.py Explained

## What config.py Does

The config.py file allows the Lambda School Labs 26 Citrics Team A Data Scientist to choose whether to build the team Docker image and deploy to the team AWS application or build his personal Docker image and deploy to his own application.

## Using config.py

The simplest part of this README;
in command line or terminal, simply type:

```
python preroutes_and_utilities/config.py
```

You should see a message in command line or terminal prompting you to enter your Docker ID:

```
Docker ID:
```

Simply input your Docker ID if building and pushing to your personal AWS app. If building and pushing to the team app, use *Aaron Watkins'* Docker ID **ekselan**.  In the former case, you'll be greeted with the following in command line or terminal:

```
Docker ID: YOUR_DOCKER_ID
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

### Resetting config.py

Two reset options are built into the config.py script, reset and reset team.

The former resets the DOCKER_ID parameter to the default, like so:

```
Docker ID: reset
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "DOCKER_ID/labs26-citrics-ds-teama_web:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ],
  "Command": "uvicorn app.main:app --workers 1 --host 0.0.0.0 --port 8000"
}
```

The latter resets the DOCKER_ID parameter to the team Docker ID, *ekselan*:

```
Docker ID: reset team
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "ekselan/labs26-citrics-ds-teama_web:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ],
  "Command": "uvicorn app.main:app --workers 1 --host 0.0.0.0 --port 8000"
}
```

### Exiting the program:

When prompted for the Docker ID, the following inputs will close the program without altering the .json file.

```
Docker ID: exit
```

or

```
Docker ID: quit
```

or 

```
Docker ID: q
```
```