# CloudDockerCMS

2nd Cloud Computing Assignment
Daniel Vegera - C15469578

##Part 1

```
docker swarm init
```
And then use the given command to create workers

```
docker swarm join [OPTIONS] HOST:PORT
```
![Alt text](/1.jpg?raw=true "Screenshot")

##Part 2


##Part 3

```
docker service create --detach=true --replicas 3 -p 80:80 --name weba nginx
```
Using nginx image to make a web server service using webport 80 to redirect & receive traffic.

![Alt text](/2.jpg?raw=true "Screenshot")