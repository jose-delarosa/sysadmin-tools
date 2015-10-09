# Docker tools

## Scripts to list Docker images and containers

Custom scripts to better display list of Docker images and containers.

## Run example

```bash
$ docker-image-list.py 
+------------------------------------+---------+--------------+
| image                              | tag     | id           |
+------------------------------------+---------+--------------+
| docker.io/nginx                    | latest  | ceab60537ad2 |
| docker.io/jdelaros1/openmanage     | latest  | 14c9ffaa58cd |
| docker.io/jdelaros1/ism            | latest  | 842e8d2701a6 |
| docker.io/registry                 | latest  | 1694982b51a1 |
| docker.io/haproxy                  | latest  | b225626aa252 |
| docker.io/python                   | 2.7     | 7a7d87336a33 |
| docker.io/debian                   | wheezy  | 19de96c112fc |
| docker.io/centos                   | centos6 | 72703a0520b7 |
| docker.io/centos                   | centos7 | 0f73ae75014f |
| docker.io/ubuntu                   | 14.04   | 91e54dfb1179 |
| docker.io/ubuntu                   | 12.04   | 57bca5139a13 |
| docker.io/registry                 | 2.0     | 08f78f46653a |
| docker.io/atcol/docker-registry-ui | latest  | d838355ad903 |
+------------------------------------+---------+--------------+
```

```bash
$ docker-container-list.py
+-------------+----------+------------+------------------+
| name        | state    | ip         | port             |
+-------------+----------+------------+------------------+
| registry-ui | shut off | n/a        | n/a ->           |
| registry    | running  | 172.17.0.3 | 5000/tcp -> 5000 |
| regdata     | shut off | n/a        | n/a ->           |
| ism         | running  | 172.17.0.1 | n/a ->           |
| omsa81      | running  | 172.17.0.2 | 1311/tcp -> 1311 |
+-------------+----------+------------+------------------+
```

## Support

These tools are provided as-is and not supported by Dell in any shape or form.
