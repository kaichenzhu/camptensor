docker run --rm -it -v /var/lib/docker:/docker -v ~/volume-backup/docker/volumes:/volume-backup busybox cp -r /volume-backup/ /docker/volumes
