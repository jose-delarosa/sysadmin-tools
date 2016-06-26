# Docker tools

## Scripts to list Docker images and containers

Custom scripts to better display list of Docker images and containers.

## Run example

```bash
$ docker-image-list.py 
+--------------------------------+---------+--------------+----------+--------------+
| image                          | tag     | id           | size     | created      |
+--------------------------------+---------+--------------+----------+--------------+
| docker.io/ubuntu               | latest  | a5a467fddcb8 | 187.9 MB | 10 days ago  |
| docker.io/debian               | wheezy  | 3b5671666ac3 | 84.87 MB | 10 days ago  |
| docker.io/centos               | centos6 | 3bbbf0aca359 | 190.6 MB | 2 weeks ago  |
| docker.io/nginx                | latest  | ceab60537ad2 | 132.8 MB | 5 weeks ago  |
| docker.io/jdelaros1/openmanage | latest  | 14c9ffaa58cd | 923.8 MB | 6 weeks ago  |
| docker.io/jdelaros1/ism        | latest  | 842e8d2701a6 | 442.5 MB | 6 weeks ago  |
| docker.io/haproxy              | latest  | b225626aa252 | 97.81 MB | 7 weeks ago  |
| docker.io/ubuntu               | 14.04   | 91e54dfb1179 | 188.3 MB | 10 weeks ago |
+--------------------------------+---------+--------------+----------+--------------+

```

```bash
$ docker-container-list.py
+-------------+----------+------------+------------------+
| name        | state    | ip         | port             |
+-------------+----------+------------+------------------+
| registry    | running  | 172.17.0.3 | 5000/tcp -> 5000 |
| samba       | shut off | n/a        | n/a ->           |
| webhome     | running  | 172.17.0.1 | 80 -> 80         |
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

These tools are provided as-is. Let me know if you have any problems. Enhancements are welcome!
