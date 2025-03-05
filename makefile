ui:
	@echo "Running UI"
	uv run streamlit run start_page.py

app:
	@echo "Running App"
	uv run uvicorn app:app --reload

install:
	uv sync
	uv venv
	
update:
	uv lock --upgrade
	uv sync
	
serve_telemetry:
	@echo "Running Telemetry"
	uv run python -m phoenix.server.main serve

run_experiment:
	@echo "Running Experiment"
	uv run python -m src.agent_experiments.gui_agent.main