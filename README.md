

# SCIMLbot Project 🚀

This project includes two services:
- **Frontend (UI)** – Angular app
- **Backend (BE)** – FastAPI app

Both are containerized using Docker and orchestrated via Docker Compose.

---

## Getting Started

1. Clone the repositories and **checkout correct branches**:

```bash
git clone -b <ui-branch> https://github.com/cs-surya/SCIML.git SCIMLbot-ui
git clone -b <be-branch> https://github.com/your-org/SCIbot-UI.git SCIMLbot-be



2. Build and run everything:

```bash
docker-compose up --build
```

- Frontend: [http://localhost:8080](http://localhost:8080)
- Backend: [http://localhost:8000](http://localhost:8000)

---

## Common Issues

**CORS Errors:**  
Add CORS middleware in FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Nginx Default Page Issue:**  
Make sure Dockerfile copies the correct Angular build output:

```dockerfile
COPY --from=build /app/dist/<your-angular-app-name>/ /usr/share/nginx/html
```
Replace `<your-angular-app-name>` with the actual folder name under `dist/`.

---

## Quick Reset Commands

```bash
docker-compose down --rmi local -v
docker-compose up --build
```

---

