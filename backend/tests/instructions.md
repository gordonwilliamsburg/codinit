# Running Docker from Python SDK

In order to allow the python script to connect to Docker Daemon, go to Docker Desktop Settings -> Advanced ->
Allow the default Docker socket to be used (requires password)

Creates /var/run/docker.sock which some third-party clients may use to communicate with Docker Desktop. Learn more

Enabling the "Allow the default Docker socket to be used" option in Docker Desktop settings is a common solution to enable third-party clients, such as the Python Docker client, to communicate with Docker Desktop on macOS. This option creates the Unix socket at `/var/run/docker.sock` which is the standard way for clients to interact with Docker on Unix-based systems, including macOS.

the Unix socket path can be used in the Python Docker client:

```python
client = docker.DockerClient(base_url='unix://var/run/docker.sock')
```

This setup should work for local development and testing on a local machine. If you plan to deploy your application to different environments (like a production server or a cloud environment), make sure to adjust the Docker client configuration accordingly to match the environment's Docker setup.
