# Logs live inside the container, so `docker compose down` destroys them along
# with it. Every deploy archives the outgoing container's output here first --
# otherwise the only record of why a container died dies with the container.
LOG_DIR := logs
STAMP = $(shell date +%Y%m%d-%H%M%S)

deploy-api:
	@mkdir -p $(LOG_DIR)
	-@docker logs artguide-api > $(LOG_DIR)/api-$(STAMP).log 2>&1 \
		&& echo "📦 Previous logs saved to $(LOG_DIR)/api-$(STAMP).log"
	@echo "🔨 Building and starting API..."
	cd api && docker compose up -d --build
	@echo "✅ API is running at http://localhost:7005"
	@echo "📚 API docs at http://localhost:7005/docs"
	@echo "📋 View logs with: make logs-api"

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
	@mkdir -p $(LOG_DIR)
	-@docker logs artguide-dashboard > $(LOG_DIR)/dashboard-$(STAMP).log 2>&1 \
		&& echo "📦 Previous logs saved to $(LOG_DIR)/dashboard-$(STAMP).log"
	@echo "🔨 Building and starting Dashboard (public URL: $(DASHBOARD_PUBLIC_URL))..."
	cd dashboard_reflex && DASHBOARD_PUBLIC_URL=$(DASHBOARD_PUBLIC_URL) docker compose up -d --build
	@echo "✅ Dashboard is running at $(DASHBOARD_PUBLIC_URL)"
	@echo "📋 View logs with: make logs-dashboard"

logs-dashboard:
	cd dashboard_reflex && docker compose logs -f

# Are both services actually up? Answers the "is it me or is it the server?"
# question without a redeploy.
health:
	@printf "api       "; curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 http://127.0.0.1:7005/status || echo "unreachable"
	@printf "dashboard "; curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 http://127.0.0.1:8502/ || echo "unreachable"
	@docker ps --filter name=artguide --format '{{.Names}}\t{{.Status}}'

# Why did the last pipeline run fail? Pulls just the interesting lines out of
# both services, newest last.
errors:
	@docker logs --since 2h artguide-dashboard 2>&1 | grep -E "ERROR|Traceback|Bad Request|Too Many Requests|failed" || echo "(dashboard: nothing)"
	@docker logs --since 2h artguide-api 2>&1 | grep -E "ERROR|Traceback|500 |502 " || echo "(api: nothing)"

# Images are no longer deleted on every deploy (that also deleted the logs, and
# left nothing running when a build failed). Reclaim the old layers on demand.
clean-images:
	docker image prune -f

run-dashboard-dev:
	cd dashboard_reflex && reflex run
	@echo "✅ Dashboard is running at http://localhost:3000"

.PHONY: deploy-api logs-api deploy-dashboard logs-dashboard health errors clean-images run-dashboard-dev
