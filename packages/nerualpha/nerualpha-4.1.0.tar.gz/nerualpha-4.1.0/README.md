## To build the SDK locally:
Because I've been experiencing some issues with the build process on `Mac M1`, I decided to use docker to install dependencies and build the SDK. I've created a `Dockerfile` that can be used to build the SDK. 

I mount the current directory to the container to have the artifacts after the build process available on the host machine in `/dist` folder.

The `Dockerfile` is located in the `python` directory. To build the SDK, run the following command:

```bash
# Build the docker image
docker build -t neru-sdk-python .
```

```bash
# Build the SDK
make build
```