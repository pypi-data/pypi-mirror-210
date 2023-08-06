import os
import urllib.request

from dotenv import load_dotenv
import docker


load_dotenv()  # take environment variables from .env.

user_profile = os.environ['USERPROFILE']
SEP = os.path.sep

def main():
    """
    The main function to run the script
    """
    client = docker.from_env()
    # docker run -d --hostname my-rabbit --name some-rabbit rabbitmq:3
    client.containers.run("rabbitmq:3", detach=True)
    
    # print all containers
    containers = client.containers.list()
    
    for container in containers:
        print(
            container.name,
            container.id,
            container.status
        )


if __name__ == '__main__':
    main()
