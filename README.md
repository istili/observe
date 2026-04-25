# Batch Pipeline Monitoring System

## One Command Setup

### Step 1: Configure Environment (Optional)

For production or development with custom credentials:

```bash
cp .env.example .env
# Edit .env with your own credentials
```

If you skip this, defaults will be used (airflow/airflow for all services).

### Step 2: Start Services

```bash
make up
```

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