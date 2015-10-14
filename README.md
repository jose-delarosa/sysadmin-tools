# Docker tools

## Scripts to list Docker images and containers

Custom scripts to better display list of Docker images and containers.

## Run example

```bash
$ docker-image-list.py 
+---------------------------------------+---------+--------------+----------+
| image                                 | tag     | id           | size     |
+---------------------------------------+---------+--------------+----------+
| docker.io/nginx                       | latest  | ceab60537ad2 | 132.8 MB |
| docker.io/jdelaros1/openmanage        | latest  | 14c9ffaa58cd | 923.8 MB |
| docker.io/jdelaros1/ism               | latest  | 842e8d2701a6 | 442.5 MB |
| docker.io/registry                    | latest  | 1694982b51a1 | 423.2 MB |
| docker.io/redis                       | latest  | 2f2578ff984f | 109.2 MB |
| docker.io/haproxy                     | latest  | b225626aa252 | 97.81 MB |
| docker.io/python                      | 2.7     | 7a7d87336a33 | 675.3 MB |
| docker.io/debian                      | wheezy  | 19de96c112fc | 84.9 MB  |
| docker.io/centos                      | centos6 | 72703a0520b7 | 190.6 MB |
| docker.io/centos                      | centos7 | 0f73ae75014f | 172.3 MB |
| docker.io/ubuntu                      | 14.04   | 91e54dfb1179 | 188.3 MB |
| docker.io/ubuntu                      | 12.04   | 57bca5139a13 | 134.8 MB |
| docker.io/registry                    | 2.0     | 08f78f46653a | 548.6 MB |
+---------------------------------------+---------+--------------+----------+

```

```bash
$ docker-container-list.py
+-------------+----------+------------+------------------+
| name        | state    | ip         | port             |
+-------------+----------+------------+------------------+
| registry    | running  | 172.17.0.3 | 5000/tcp -> 5000 |
| regdata     | shut off | n/a        | n/a ->           |
| ism         | running  | 172.17.0.1 | n/a ->           |
| omsa81      | running  | 172.17.0.2 | 1311/tcp -> 1311 |
+-------------+----------+------------+------------------+

$ docker-container-list.py -h
Usage: docker-container-list [options]
   Display container information in a nice readable format.

Options:
  -h, --help  show this help message and exit
  -i          image
  -I          ip
  -P          ports
  -v          volumes
  -n          node
  -c          command
  -p          pid

```

## Support

These tools are provided as-is. Let me know if you have any problems. Enhancements welcomed!
