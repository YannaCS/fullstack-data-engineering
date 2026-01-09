### install Dependencies
```bash 
uv pip install celery redis
```

### setup rabbitMQ
```bash
# Just queue
docker run -d -p 5672:5672 rabbitmq

# with management UI
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

open http://localhost:15672/ for management UI
```

### setup Redis
```bash
docker run -d -p 6379:6379 redis
```


### start message queue worker

```bash
# Terminal 1
celery -A message_queue_worker worker --loglevel=info
```

### start message queue server

```bash
fastapi dev message_queue.py
```