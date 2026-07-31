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

# The public https origin is baked into the frontend bundle at build time as
# the /_event websocket target, so it must be the address the browser actually
# uses -- not the container's own port. Left at compose's localhost default the
# bundle asks for ws://<host>:8502/_event, a port that is only published on
# 127.0.0.1 and never reachable through the tunnel, which kills every event
# handler (camera, settings, upload). Override for a different environment:
#   make deploy-dashboard DASHBOARD_PUBLIC_URL=https://staging.example.com
DASHBOARD_PUBLIC_URL ?= https://artguide.thebluetonguegiraffe.online

deploy-dashboard:
	@echo "🧹 Cleaning old dashboard images..."
	cd dashboard_reflex && docker compose down --rmi all --volumes --remove-orphans || true
	@echo "🔨 Building and starting Dashboard (public URL: $(DASHBOARD_PUBLIC_URL))..."
	cd dashboard_reflex && DASHBOARD_PUBLIC_URL=$(DASHBOARD_PUBLIC_URL) docker compose up -d --build
	@echo "✅ Dashboard is running at $(DASHBOARD_PUBLIC_URL)"
	@echo "📋 View logs with: cd dashboard_reflex && docker compose logs -f"

logs-dashboard:
	cd dashboard_reflex && docker compose logs -f

run-dashboard-dev:
	cd dashboard_reflex && reflex run
	@echo "✅ Dashboard is running at http://localhost:3000"
