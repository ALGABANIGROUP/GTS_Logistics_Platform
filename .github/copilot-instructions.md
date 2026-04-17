# Copilot Instructions for GTS Logistics Platform

## Big Picture Architecture
- **Modular SaaS platform** for freight management, brokerage, and logistics automation.
- **Backend:** FastAPI (Python) for core business logic, API orchestration, and real-time sync.
- **Frontend:** Vite + React for dashboards, bot panels, and client interfaces.
- **Core AI Bots:** Each bot (General Manager, Freight Broker, Finance, Documents Manager, Service Bot) is a distinct module with clear boundaries.
- **Search & SEO System:** Separate submodule using Elasticsearch, Scrapy, and NLP for search, crawling, and content analysis.
- **Data Flows:** Real-time sync between shippers, carriers, brokers; bots orchestrate workflows and automate tasks.

## Critical Developer Workflows
- **Backend Start:**
  - `python -m uvicorn backend.main:app --reload` (or use VS Code task: Start Backend)
- **Frontend Start:**
  - `cd frontend && npm run dev` (or use VS Code task: Start Frontend)
- **Bot Panel Quick Start:**
  - Access at `http://localhost:5173/ai-bots/customer-service`
  - Import main panel: `import { CustomerServicePanel } from '../panels/customer-service';`
- **Testing:**
  - Python scripts for checks (e.g., `check_users.py`, `check_auth_me.py`)
  - No unified test runner; use script per module.

## Project-Specific Conventions
- **AI Bots:** Each bot is a self-contained module with its own panel/component and backend logic.
- **File Naming:**
  - Migration scripts: `add_*_column.sql`, `add_*_to_users.py`
  - Check scripts: `check_*_table.py`, `check_*_roles.py`
- **Docs:**
  - Platform reports and invoices are organized by company in `docs/platform_reports/*`.
  - Each bot/component has a README in its directory.
- **Frontend:**
  - React components grouped by bot and panel.
  - Use HMR via Vite; ESLint rules enforced.

## Integration Points & External Dependencies
- **Carrier APIs:** Planned integration (TruckerPath, 123Loadboard, DAT).
- **Search/SEO:** Elasticsearch, Scrapy, NLP libraries.
- **VoIP/Comms:** Call center modules integrate with external VoIP APIs.
- **Finance/Docs:** Automated invoice and document generation, stored in `docs/platform_reports`.

## Cross-Component Communication
- **Bots communicate via backend API endpoints.**
- **Frontend panels orchestrate bot actions and display real-time stats.**
- **Data synchronization is real-time between backend and frontend.**

## Examples
- To add a new bot: create a backend module, frontend panel, and README.
- To run customer service bot locally: start backend, frontend, and access `/ai-bots/customer-service`.
- To check user table: run `python check_users.py`.

## Key Files/Directories
- `backend/main.py`: FastAPI entry point
- `frontend/src/components/bots/panels/*`: Bot panels
- `docs/platform_reports/*`: Reports and invoices
- `search-seo-system/`: Search/SEO submodule

## Support & Contact
- **Technical Support**: support@gabanilogistics.com
- **Operations Team**: operations@gabanilogistics.com
- **Platform Issues**: Check logs in `backend/logs/` or contact support

---

**For unclear or incomplete sections, please provide feedback or request examples.**
