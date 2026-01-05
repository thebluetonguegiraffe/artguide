deploy-api:
	@echo "🧹 Cleaning old images..."
	cd api && docker compose down --rmi all --volumes --remove-orphans || true
	@echo "🔨 Building and starting API..."
	cd api && docker compose up -d --build
	@echo "✅ API is running at http://localhost:7005"
	@echo "📚 API docs at http://localhost:7005/docs"
	@echo "📋 View logs with: make logs"

logs-api:
	cd api && docker compose logs -f

deploy-dashboard:
	@echo "🧹 Cleaning old dashboard images..."
	cd dashboard && docker compose down --rmi all --volumes --remove-orphans || true
	@echo "🔨 Building and starting Dashboard..."
	cd dashboard && docker compose up -d --build
	@echo "✅ Dashboard is running at http://localhost:8502"
	@echo "📋 View logs with: cd dashboard && docker compose logs -f"

logs-dashboard:
	cd dashboard && docker compose logs -f

run-dashboard-dev:
	@ export PYTHONPATH=.
	streamlit run dashboard/main.py --server.port 8501
	@echo "✅ Dashboard is running at http://localhost:8501"