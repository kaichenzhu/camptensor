docker run --rm -it -v ~/volume-backup:/backup -v /var/lib/docker:/docker busybox tar cfz /backup/volume.tgz /docker/volumes/
