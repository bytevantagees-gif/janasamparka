# Docker Build Optimization Guide

This guide explains how to avoid repeated downloads of large packages during Docker builds.

## Problem
Previously, every backend rebuild would download 900+ MB of packages (PyTorch, Sentence Transformers, etc.), which could take 5-10 minutes even on fast connections.

## Solutions Implemented

### 1. Docker BuildKit Cache Mount (✅ Implemented)

The Dockerfile now uses BuildKit cache mounts to persist pip downloads across builds:

```dockerfile
# Install Python dependencies with caching enabled
# Using buildkit cache mount to speed up rebuilds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt
```

**Benefits:**
- ✅ Pip packages are cached in `/root/.cache/pip` across builds
- ✅ Only changed dependencies are downloaded
- ✅ Dramatically faster rebuilds (seconds instead of minutes)
- ✅ No manual cleanup needed - cache managed automatically

### 2. Docker Layer Caching Strategy

The Dockerfile is structured to maximize layer reuse:

```dockerfile
# 1. System dependencies (rarely change)
RUN apt-get update && apt-get install -y gcc postgresql-client...

# 2. Python requirements (change occasionally)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# 3. Application code (changes frequently)
COPY . .
```

**Benefits:**
- ✅ Unchanged layers are reused from cache
- ✅ Only layers after the changed layer are rebuilt
- ✅ Most code changes don't trigger dependency reinstall

### 3. Fast Rebuild Script

Use the provided script for faster rebuilds:

```bash
./rebuild-backend-fast.sh
```

This script:
- ✅ Enables BuildKit automatically (`DOCKER_BUILDKIT=1`)
- ✅ Shows helpful status messages
- ✅ Displays logs to verify successful startup
- ✅ Provides troubleshooting tips

## Usage

### For Code Changes Only (No Dependency Changes)
```bash
# Just restart the container (instant)
docker compose restart backend

# Or rebuild only changed layers (fast - usually <30 seconds)
./rebuild-backend-fast.sh
```

### For Dependency Changes (requirements.txt modified)
```bash
# BuildKit cache makes this fast too (downloads only new packages)
./rebuild-backend-fast.sh
```

### For Clean Rebuild (Troubleshooting)
```bash
# Forces complete rebuild but still uses pip cache
docker compose build --no-cache backend
docker compose up -d backend
```

## Expected Build Times

With BuildKit cache enabled:

| Scenario | Time | Downloads |
|----------|------|-----------|
| Code changes only | 5-15s | None |
| Minor dependency updates | 30-60s | Only new packages |
| Major dependency changes | 1-3 min | Only changed packages |
| Clean build (first time) | 5-10 min | All packages (one time) |
| Clean build (subsequent) | 1-3 min | Reuses cache |

## How to Verify Cache is Working

```bash
# First build (slow - establishes cache)
docker compose build backend

# Second build (fast - uses cache)
docker compose build backend

# Check for cache usage in build output:
# You should see: "CACHED" for unchanged layers
# Example:
#  => CACHED [2/7] WORKDIR /app
#  => CACHED [3/7] RUN apt-get update...
```

## Troubleshooting

### Cache Not Working?

1. **Ensure BuildKit is enabled:**
   ```bash
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1
   ```

2. **Check Docker version:**
   ```bash
   docker --version  # Should be 19.03 or higher
   ```

3. **Verify cache mount in build output:**
   Look for: `RUN --mount=type=cache` in the build logs

### Need to Clear Cache?

```bash
# Clear build cache (rarely needed)
docker builder prune -a

# Clear pip cache specifically
docker system prune --volumes
```

## Best Practices

1. ✅ **Always use `./rebuild-backend-fast.sh` for rebuilds**
2. ✅ **Group dependency changes** - Update multiple packages at once instead of one-by-one
3. ✅ **Keep requirements.txt organized** - Helps track what changed
4. ✅ **Don't disable BuildKit** - It's much faster
5. ✅ **Use `docker compose restart`** for code-only changes

## Technical Details

### BuildKit Cache Mount
- Cache persists in Docker's build cache storage
- Shared across all builds on the same machine
- Automatically pruned by Docker when disk space is low
- No manual management required

### Why This Works
1. `--mount=type=cache,target=/root/.cache/pip` tells Docker to preserve `/root/.cache/pip` across builds
2. Pip stores downloaded wheels in this directory
3. Next build reuses these wheels instead of re-downloading
4. Works even with `--no-cache` flag (cache mount is separate from layer cache)

## Related Files

- `/backend/Dockerfile` - Contains the optimized build configuration
- `/rebuild-backend-fast.sh` - Fast rebuild helper script
- `/backend/requirements.txt` - Python dependencies

## Monitoring Package Sizes

To see which packages are largest:

```bash
docker exec janasamparka_backend pip list --format=freeze | \
  while read pkg; do 
    size=$(docker exec janasamparka_backend pip show $(echo $pkg | cut -d= -f1) | grep Location | head -1)
    echo "$pkg - $size"
  done | sort -k3 -hr | head -20
```

Large packages in our stack:
- `torch` (~900 MB) - PyTorch for ML
- `sentence-transformers` (~400 MB) - Text embeddings
- `transformers` (~300 MB) - Hugging Face models
- `firebase-admin` (~50 MB) - Firebase SDK

Total: ~2.5 GB of Python packages (one-time download with cache enabled)
