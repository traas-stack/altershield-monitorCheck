# BaseImage
FROM python:3.10-slim
MAINTAINER fujinfei.fjf <fujinfei.fjf@antgroup.com>

# Set work dir
WORKDIR /home/admin
COPY .. /home/admin

# Copy project file to container
COPY ./requirements.txt .
COPY ./main.py .

RUN apt-get update && apt-get install -y curl
# install
RUN python3.10 -m pip install -i http://artifacts.alipay.com/artifact/repositories/simple --trusted-host artifacts.alipay.com -r requirements.txt


ENV PORT 8083
EXPOSE $PORT

# start app
CMD ["python", "main.py"]
