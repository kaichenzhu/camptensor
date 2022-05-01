npm run build
rm -rf /var/lib/docker/volumes/camptensor-engine_static_volume/_data/index.html
cp dist/index.html /var/lib/docker/volumes/camptensor-engine_static_volume/_data/index.html
rm -rf /var/lib/docker/volumes/camptensor-engine_static_volume/_data/static
cp -r dist/static /var/lib/docker/volumes/camptensor-engine_static_volume/_data
