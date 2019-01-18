FROM python
MAINTAINER NOSPAM <nospam@nnn.nnn>

RUN apt-get update && apt-get install -y python-pip git openssh-client gocryptfs
RUN pip install awscli
RUN apt-get purge -y apt-transport-https && apt-get autoclean

COPY cloudstomp.py /cloudstomp.py
RUN chmod +x /cloudstomp.py
RUN sed -i 's/^plugindir/cshome = "\/data"\nplugindir/' cloudstomp.py

ENV PYTHONUNBUFFERED=0

CMD ["sh", "-c", "PYTHONUNBUFFERED=0 eval /cloudstomp.py $OPTIONS"]
