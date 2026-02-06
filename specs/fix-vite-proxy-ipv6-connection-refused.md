# Bug: Vite Proxy IPv6 Connection Refused

## Bug Description
When running `scripts/start.sh`, both the backend and frontend servers start successfully, but API requests from the frontend fail with `ECONNREFUSED ::1:8000`. The frontend Vite dev server proxy is attempting to connect to the backend using IPv6 (`::1`) instead of IPv4 (`127.0.0.1`), causing connection failures.

**Symptoms:**
- Backend reports `Uvicorn running on http://0.0.0.0:8000` and `Application startup complete`
- Frontend reports `VITE v6.3.5 ready`
- API calls fail with `Error: connect ECONNREFUSED ::1:8000`

**Expected behavior:** API proxy requests should successfully reach the backend server.

**Actual behavior:** Proxy requests fail because Vite resolves `localhost` to IPv6 `::1`, but the backend only accepts IPv4 connections.

## Problem Statement
The Vite proxy configuration uses `http://localhost:8000` as the target, which may resolve to IPv6 address `::1` on some systems. The uvicorn backend server binds to `0.0.0.0:8000`, which on most configurations only listens on IPv4, causing the IPv6 connection to be refused.

## Solution Statement
Change the Vite proxy target from `http://localhost:8000` to `http://127.0.0.1:8000` to explicitly use IPv4, ensuring consistent connectivity regardless of how the system resolves `localhost`.

## Steps to Reproduce
1. Run `bash scripts/start.sh`
2. Wait for both services to start
3. Open `http://localhost:5173` in a browser
4. Observe the Vite proxy errors in the terminal:
   ```
   [vite] http proxy error: /api/schema
   Error: connect ECONNREFUSED ::1:8000
   ```

## Root Cause Analysis
The root cause is a hostname resolution mismatch between IPv4 and IPv6:

1. **Vite proxy configuration** uses `http://localhost:8000` as the target
2. **Node.js DNS resolution** on some systems resolves `localhost` to IPv6 `::1` first (per RFC 6761)
3. **Uvicorn backend** binds to `0.0.0.0:8000`, which typically only listens on IPv4
4. When Vite's proxy attempts to connect to `::1:8000`, the connection is refused because nothing is listening on that IPv6 address

This is a common issue when mixing `localhost` (which can resolve to either IPv4 or IPv6) with services that only bind to IPv4.

## Relevant Files
Use these files to fix the bug:

- **`app/client/vite.config.ts`** - Contains the Vite proxy configuration with the `localhost` target that needs to be changed to `127.0.0.1`

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update Vite Proxy Configuration
- Open `app/client/vite.config.ts`
- Change the proxy target from `http://localhost:8000` to `http://127.0.0.1:8000`
- This forces IPv4 and ensures consistent behavior across all systems

### Step 2: Run Validation Commands
- Execute the validation commands to confirm the fix works

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate no regressions
- `bash scripts/start.sh` - Start services and verify no proxy errors appear when making API requests
- `curl http://127.0.0.1:8000/api/health` - Verify backend is accessible via IPv4

## Notes
- This is a one-line fix in `vite.config.ts`
- The change from `localhost` to `127.0.0.1` is a common best practice to avoid IPv4/IPv6 resolution issues
- No new dependencies required
