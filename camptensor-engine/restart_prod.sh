celerybeat_schedule=/root/camptensor-engine/app/celerybeat-schedule
if [ -f "$celerybeat_schedule" ]; then
    echo "$celerybeat_schedule exists."
    rm -rf $celerybeat_schedule
fi
celerybeat_pid=/root/camptensor-engine/app/celerybeat.pid
if [ -f "$celerybeat_pid" ]; then
    echo "$celerybeat_pid exists."
    rm -rf $celerybeat_pid
fi
docker stop $(docker ps -a | awk '{ print $1}' | tail -n +2)
docker rm $(docker ps -a | awk '{ print $1}' | tail -n +2)
docker-compose -f docker-compose.prod.yml up --build -d