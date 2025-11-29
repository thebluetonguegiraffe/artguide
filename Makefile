run_api:
	uvicorn api.api:app --host localhost --port 8000

run_dashboard:
	streamlit run dashboard/main.py --server.port 8501

