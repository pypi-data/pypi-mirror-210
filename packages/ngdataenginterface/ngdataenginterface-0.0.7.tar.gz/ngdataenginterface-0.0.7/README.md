# ngdataenginterface

## Installation

To install the `ngdataenginterface` package from PyPI, you can use `pip`:

```shell
pip install ngdataenginterface
```

## installing a Specific Version

If you need to install a specific version of the package, you can specify it using the == operator:

```shell 
pip install ngdataenginterface==1.0.0
```

Replace 1.0.0 with the desired version number.

# Development Guide for ngdataenginterface

This guide provides step-by-step instructions for setting up a development environment using Docker for the ngdataenginterface project on macOS, Linux, and Windows machines.

## Prerequisites

- Docker installed on your machine:
  - [Docker Desktop for macOS](https://www.docker.com/products/docker-desktop)
  - [Docker Engine for Linux](https://docs.docker.com/engine/install/)
  - [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

## Development Setup

1. Clone the ngdataenginterface repository with ssh:

```shell
git clone git@gitlab.com:ng-cash/data/ngdataenginterface.git
```

2. Change into the project directory:

```shell
cd ngdataenginterface
```

3. Build the docker image

```shell
docker build -t my-pyspark-app .
```

## Running the Development Environment

### macOS / Linux
1. Start a Docker container and mount the project directory for iterative development:
   ```shell
   docker run -it --rm -v "$(pwd)":/app my-pyspark-app
   ```
This command starts the Docker container interactively (__-it__ flag), removes it after it exits (__--rm__ flag), and mounts the current directory (__$(pwd)__) to the /app directory inside the container. You will have an interactive bash shell within the container. 

2. Inside the container, you can run tests, execute scripts, and make changes to the code using your preferred editor or IDE on your host machine. The changes will be immediately available inside the container.
### Windows
1. Start a Docker container and mount the project directory for iterative development:
   ```shell
   docker run -it --rm -v "%cd%:/app" my-pyspark-app bash
   ```
This command starts the Docker container interactively z(__-it__ flag), removes it after it exits (__--rm__ flag), and mounts the current directory (__%cd%__) to the /app directory inside the container. You will have an interactive bash shell within the container. Run `python` command to access python shell.

2. Inside the container, you can run tests, execute scripts, and make changes to the code using your preferred editor or IDE on your host machine. The changes will be immediately available inside the container.


Run the tests to verify if the configurations are correct:

```shell
ENV=dev AWS_ACCESS_KEY_ID=<aws-access-key-id> AWS_SECRET_ACCESS_KEY=<aws-secret-access-key> pytest -vv
```

Don't forget to change __aws-access-key-id__ and __aws-secret-access-key__.

After that, run `python` command to access python shell, and tou are ready to go!
