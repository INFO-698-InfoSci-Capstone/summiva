## 📘 Summiva Makefile Command Guide

This document explains how to use the `Makefile` in the Summiva project to manage Docker-based microservices.

---

### ⚙️ 1. Build the Docker Image

```bash
make build
```

* **What it does:** Builds the Docker image named `summiva-service`.
* **Custom usage:**

  ```bash
  make build USER_ID=1001
  ```

---

### 🚀 2. Run a Service in Production Mode

```bash
make run-prod SERVICE_NAME=summarization
```

* **What it does:** Runs the service on port `8000` in production mode.
* **Defaults:** If `SERVICE_NAME` is not specified, it defaults to `summarization`.

---

### 🚰 3. Run a Service in Development Mode with Hot Reload

```bash
make run-dev SERVICE_NAME=summarization
```

* **What it does:** Mounts local `src/` directory and runs the service with live reload.
* **Use case:** Ideal for real-time development and debugging.

---

### 🧹 4. Run All Services Simultaneously

```bash
make run-all
```

* **What it does:**

  * Builds the Docker image if needed.
  * Runs all services (`summarization`, `tagging`, `grouping`, `search`, `clustering`) in separate containers.
  * Dynamically assigns ports (e.g., 8001, 8012).
  * Containers are named as `summiva-<service>`.

---

### 🚩 5. Stop All Running Services

```bash
make stop-all
```

* **What it does:** Stops all containers started by `run-all`.

---

### 🧹 6. Clean Up Docker Resources

```bash
make clean
```

* **What it does:** Removes unused Docker containers, images, and networks.

---

### 🙺 7. Install Python Dependencies for a Service

```bash
make fix-deps SERVICE_NAME=summarization
```

* **What it does:** Installs Python dependencies from `requirements.txt` inside the service container.

---

### 🌀 8. Show Help Message

```bash
make help
```

* **What it does:** Displays available Makefile targets and descriptions.

---

## 📝 Notes

* Rebuild and restart all services:

  ```bash
  make clean build run-all
  ```

* Each service must have a valid `main.py` file at:

  ```
  /app/src/<service>/main.py
  ```