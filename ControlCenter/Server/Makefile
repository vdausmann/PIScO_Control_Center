
add-task:
	@curl -X 'POST' \
	  'http://localhost:8000/add-task' \
	  -H 'accept: application/json' \
	  -H 'Content-Type: application/json' \
	  -d '{ "name": "test", "is_running": true }'


get-task:
	@curl -X 'GET' \
	  'http://localhost:8000/get-task?task_id=${ID}' \
	  -H 'accept: application/json'
