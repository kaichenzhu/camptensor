# pull official base image
FROM python:3.8.7-slim-buster

ADD sources.list /etc/apt/

## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean

# set work directory
WORKDIR /home/app/web/

## add user
RUN addgroup --system user && adduser --system --no-create-home --group user
RUN chown -R user:user /home/app/web/ && chmod -R 755 /home/app/web/

# install dependencies
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir

# install nltk
RUN pip install nltk -i https://pypi.tuna.tsinghua.edu.cn/simple
# RUN python3 -c "import nltk; nltk.download(['averaged_perceptron_tagger', 'wordnet'])"

COPY ./requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

RUN apt-get install -y net-tools

# copy entrypoint.sh
# COPY ./entrypoint.sh .

# copy project
# COPY ./manage.py $APP_HOME
# COPY ./api $APP_HOME/api
# COPY ./jwtauth $APP_HOME/jwtauth
# COPY ./server $APP_HOME/server
# COPY ./appfront/dist $APP_HOME/appfront/dist

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
