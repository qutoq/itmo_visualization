from datetime import timedelta


# Настройки очередей
#task_routes = {
#    "tasks.add": {"queue": "default"},
#    "tasks.long_running_task": {"queue": "long"},
#}

# Настройки повтора задач
#beat_schedule = {
#    "run_every_10_seconds": {
#        "task": "tasks.some_task",
#        "schedule": timedelta(seconds=10),
#    },
#}

broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/1"
task_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
