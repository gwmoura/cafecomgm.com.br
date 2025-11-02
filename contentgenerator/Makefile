write:
	python3 writer.py

rewrite:
	python3 rewriter.py

revise:
	python3 proofreader.py

consultant:
	python3 consultant.py

start-ollama:
	docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

run-llama3:
# 	docker exec -it ollama ollama run llama3
	docker exec -it ollama ollama run phi3:mini