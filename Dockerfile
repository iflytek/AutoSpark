FROM python:3.9
WORKDIR /app
COPY requirements.txt .

#RUN apt-get update && apt-get install --no-install-recommends -y git wget libpq-dev gcc python3-dev && pip install psycopg2
RUN  pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple/ 
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install llama-index==0.6.35 -i https://pypi.python.org/simple 
RUN pip config set global.index-url https://repo.model.xfyun.cn/api/packages/administrator/pypi/simple  &&  pip config set global.extra-index-url https://pypi.mirrors.ustc.edu.cn/simple/
RUN pip install spark-ai-python  websocket-client autospark-kit  -i https://repo.model.xfyun.cn/api/packages/administrator/pypi/simple

COPY . .
COPY config.yaml ./config.yaml
COPY entrypoint.sh ./entrypoint.sh
COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./entrypoint.sh ./wait-for-it.sh

CMD ["./wait-for-it.sh", "as__postgres:5432","-t","60","--","./entrypoint.sh"]
