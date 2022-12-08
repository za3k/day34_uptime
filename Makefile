run-debug:
	flask --debug run
run-demo:
	gunicorn3 -e SCRIPT_NAME=/hackaday/uptime --bind 0.0.0.0:8034 app:app
