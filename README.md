# Docker tools

## Scripts to list Docker images and containers

Custom scripts to better display list of Docker images and containers.

## Run example

```bash
$ d-im-list
+----------------------+----------+--------------+----------+--------------+
| image                | tag      | id           | size     | created      |
+----------------------+----------+--------------+----------+--------------+
| jdelaros1/dsu        | 15.05.00 | d6e5eee45da8 | 392.7 MB | 11 hours ago |
| sshd                 | latest   | 9e5fbfb9eb43 | 286.7 MB | 16 hours ago |
| jdelaros1/openmanage | latest   | 53c24faac39e | 963.4 MB | 16 hours ago |
| redis                | latest   | 4b7672067154 | 111 MB   | 2 weeks ago  |
| python               | 2.7      | d833e0b23482 | 747.9 MB | 5 weeks ago  |
| centos               | centos6  | b9aeeaeb5e17 | 202.6 MB | 7 weeks ago  |
| centos               | centos7  | fd44297e2ddb | 215.7 MB | 7 weeks ago  |
+----------------------+----------+--------------+----------+--------------+
```

```bash
$ d-list
+-------+--------------+----------+-------+------------+----------------+
| name  | id           | state    | image | ip         | port           |
+-------+--------------+----------+-------+------------+----------------+
| httpd | 068bea02ff17 | shut off | httpd | n/a        | n/a ->         |
| sshd  | 211390df9a33 | running  | sshd  | 172.17.0.1 | 22/tcp -> 2022 |
+-------+--------------+----------+-------+------------+----------------+
```

## Support

These tools are provided as-is and not supported by Dell in any shape or form.
