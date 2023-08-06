import os, sys, datetime, time
import urllib.request

from dotenv import load_dotenv
import docker

from psutil import process_iter
from signal import SIGTERM # or SIGKILL

load_dotenv()  # take environment variables from .env.

user_profile = os.environ['USERPROFILE']
SEP = os.path.sep

def main():
    """
    The main function to run the server and publish the news articles to the RabbitMQ queue
    """
    print('Server is being initialized...')
    
    # check first if docker is installed
    # if it has docker then run the following code
    if os.system('docker --version') == 0:
        
        print('Docker is installed!')
        
        client = docker.from_env()

        # print all containers
        containers = client.containers.list()

        for container in containers:
            print(
                container.name,
                container.id,
                container.status
            )

        # TODO: add this feature by accepting a command line argument such as --force
        # search any application running on port 5672 and close the process by its ID using sys package
        
        if sys.argv[1] == '--force':
        
            if len(containers) > 0:
                # search if any container is running on port 5672 and close the process
                for container in containers:
                    if container.name == 'aij-messaging-server':
                        container.kill()
                        
                    if 5672 in container.ports:
                        container.kill()
                        
            for proc in process_iter():
                for conns in proc.connections(kind='inet'):
                    if conns.laddr.port == 5672:
                        proc.send_signal(SIGTERM) # or SIGKILL

        client.containers.run(
            image="rabbitmq:3-management", 
            name='aij-messaging-server', 
            ports={
                '5672': 5672,
                '15672': 15672
            },
            remove = True,
            detach=True, 
        )
        
        print('Server is now running using Docker...')
        
    # if docker is not installed then run the following code
    else:
        print('Docker is not installed!')
        os.system('rabbitmq-server -detached')
        print('Server is now running using local RabbitMQ server...')

    print('Server is now running...')


if __name__ == '__main__':
    main()