# GoEye

Store camera analytics. GoEye reads the store's CCTV cameras and shows them live on a web dashboard. Person detection and behaviour analytics are being built next.

Everything runs in Docker: one command starts the whole app.

## What you need

- **Docker Desktop**, installed and running
- This PC on the **same network as the camera recorder (NVR)**
- A **`.env`** file in this folder (ask the project owner, or create it from `.env.example`). It holds the camera addresses, the camera login and the database passwords. Never commit it.
- A **`web/.env`** file containing `NEXT_PUBLIC_API_URL=http://localhost:8001`

## Start GoEye

Open a terminal in this folder and run:

```
docker compose up -d
```

The first start builds the app and takes several minutes. Later starts take seconds. In Docker Desktop the app shows up as **goeye**, a group of 6 containers.

## Create your login (first time only)

```
docker compose exec backend python -m backend.modules.auth.create_admin you@example.com
```

Type a password (at least 8 characters) when asked, then type it again. Nothing appears on screen while you type; that's normal.

## Log in and view the cameras

1. Open **http://localhost:5173** in your browser.
2. Sign in with the email and password you just created.
3. The **Dashboard** shows each camera as a live tile, with an **Online** / **Offline** badge. The top right shows how many cameras are online.

Expect the picture to look grey and smeared for a few seconds after a camera connects. It clears once the camera sends its first full frame.

Click **Sign out** at the top right when you're done.

## Stop GoEye

```
docker compose down
```

Your data (users, events) is kept and comes back on the next start. You can also use the start/stop button on the **goeye** group in Docker Desktop.

## Add or change a camera

Cameras are listed in `.env`:

```
CAMERAS={"cam1501":"rtsp://10.0.0.93:554/streaming/channels/1501","cam1601":"rtsp://10.0.0.93:554/streaming/channels/1601"}
```

Add an entry with a short id and the camera's RTSP address. Leave the username and password out of the address; they come from `RTSP_USER` and `RTSP_PASSWORD`. Then restart:

```
docker compose up -d
```

## Addresses

| What | Address |
|---|---|
| Dashboard | http://localhost:5173 |
| Backend API | http://localhost:8001 (port 8000 is used by camera_tool) |

## Something isn't working

| Problem | What to check |
|---|---|
| Dashboard page doesn't open | Is Docker Desktop running? Run `docker compose ps`: all 6 services should be "Up". |
| "Invalid email or password" | Create a login first (see above), or check the email spelling. |
| A camera shows **Offline** | Is this PC on the store network? Check `RTSP_USER` / `RTSP_PASSWORD` in `.env`. See the camera log: `docker compose logs vision` |
| "port is already allocated" when starting | Another program is using that port. Stop it, or ask before changing GoEye's ports. |
| Anything else | `docker compose logs -f` shows what every part is doing. |

## Project layout

```
backend/   API (FastAPI): core/ + modules/<feature>/
vision/    camera reading and, next, detection and analytics
shared/    settings and messages shared by vision and backend
web/       dashboard (Next.js), see web/README.md
RULES.md   coding standards for everyone working on this code
```
