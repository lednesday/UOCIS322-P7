FROM python:3.8
LABEL maintainer="linzanna@cs.uoregon.edu"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN chmod +x run_tests.sh
# TODO: don't I need to actually run the script?
# RUN ./run_tests.sh
# these 2 below lines are not necessary with docker-compose
# ENTRYPOINT ["python"]
# CMD ["flask_brevets.py"]
