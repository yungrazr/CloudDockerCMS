# CloudDockerCMS

2nd Cloud Computing Assignment
Daniel Vegera - C15469578

## Setting up

Clone this repository and then proceed to build the docker image using the included dockerfile in the repository.
Create a swarm and add the worker nodes.
Then create service using the following command.
```
docker service create --replicas 3 -p 8080:8080 --mount type=bind,source=/var/run/docker.sock,destination=/var/run/docker.sock --constraint 'node.role==manager' --name dockercms cms
```
Creates 3 replicas (--replicas), opens up docker socket as a service (--mount) and makes sure service can only run on a manager node (--constraint)

## Part 1

Use this command to create a manager
```
docker swarm init
```
And then use the given command to create workers
```
docker swarm join [OPTIONS] HOST:PORT
```
![Image 1](/1.png?raw=true "Screenshot")

## Part 2


## Part 3

```
docker service create --detach=true --replicas 3 -p 80:80 --name weba nginx
```
Using nginx image to make a web server service using webport 80 to redirect & receive traffic.

![Image 2](/2.png?raw=true "Screenshot")