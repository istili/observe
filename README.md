# Batch Pipeline Monitoring System

## Getting Started

### Step 1: Configure Environment (Optional)

For production or development with custom credentials:

```bash
cp .env.example .env
# Edit .env with your own credentials
```

If you skip this, defaults will be used (airflow/airflow for all services).

### Step 2: First-Time Setup

After cloning the repo for the first time, run the bootstrap command. This will
pull all Docker images, run Airflow DB migrations, create the admin user, and
start all services. The first run may take several minutes while images are
downloaded.

```bash
make bootstrap
```

### Step 3: Subsequent Starts

Once images are pulled and the database is initialized, use the normal start
command for all subsequent runs:

```bash
make up
```

## Available Commands

| Command | Description |
|---|---|
| `make bootstrap` | **First-time setup**: pull images, initialize Airflow DB, start all services |
| `make up` | Start all services (fast, for subsequent runs) |
| `make down` | Stop all services |
| `make pull` | Pull all Docker images |
| `make init` | Run Airflow DB migrations and create the admin user |
| `make status` | Show running container status |
| `make logs` | Stream logs from all services |
| `make trigger` | Manually trigger the batch pipeline DAG |
| `make clean` | Stop all services and remove volumes (full reset) |

## After Setup

1. Open Grafana

	http://localhost:3000 (admin/admin)

2. Import the dashboard

	- Click **Dashboards** → **New** → **Import**
	- Upload `dashboard-export.json` from this folder
	- Click **Load** → **Import**

3. Run the pipeline

	```bash
	make trigger
	```

4. See the data

	- In Grafana, open **Batch Pipeline Monitoring - Ikram Stili**
	- Set the time range to **Last 6 hours**
	- The metrics should appear on the dashboard
	- Check **Latest Data Timestamp by Market (Age Seconds)**:
	  - **Green** means the market feed was refreshed within the last 3 minutes
	  - **Red** means the market feed is stale and needs attention