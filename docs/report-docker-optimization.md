# Dockerfile Optimization Analysis and Recommendations

## Current Dockerfile Issues

### 1. **No Multi-Stage Build**
- Current: Single-stage build includes build tools in final image
- Impact: Larger image size (~2-3GB extra) with unnecessary build dependencies

### 2. **Poor Layer Caching**
- Issue: `COPY src/ ./src/` happens before `pip install`, then `COPY . .` copies everything again
- Impact: Any source code change invalidates all subsequent layers, forcing full dependency reinstall

### 3. **Security Concerns**
- Running as root user
- No image signature verification
- Build tools (gcc, cmake) remain in final image
- No vulnerability scanning

### 4. **Build Speed Issues**
- Dependencies reinstalled on every source code change
- No use of Docker BuildKit mount cache
- pip cache explicitly disabled but not leveraged properly

### 5. **Image Size Issues**
- apt cache not cleaned in same layer (partially fixed with rm -rf)
- Build dependencies included in final image
- Duplicate COPY operations

## Optimization Recommendations

### 1. Multi-Stage Builds (HIGH PRIORITY)
**Implementation:**
- Stage 1 (builder): Install all dependencies, compile packages
- Stage 2 (runtime): Copy only installed packages and application code
- Remove build-essential, cmake from runtime stage

**Expected Impact:**
- Image size reduction: 500MB - 1.5GB
- Security: Reduced attack surface
- Build time: Slightly longer first build, faster subsequent builds

### 2. Layer Caching Optimization (HIGH PRIORITY)
**Current problematic order:**
```dockerfile
COPY pyproject.toml README.md ./
COPY src/ ./src/              # ❌ Invalidates cache on any src change
RUN pip install --no-cache-dir .
COPY . .                       # ❌ Duplicate copy
```

**Optimized order:**
```dockerfile
COPY pyproject.toml README.md ./
RUN mkdir -p ./src && touch ./src/__init__.py  # Minimal structure
COPY src/snsw ./src/snsw      # Only package source
RUN pip install --no-cache-dir .
COPY . .                       # Application code last
```

**Expected Impact:**
- 90% faster rebuilds when only app code changes
- Dependencies cached unless pyproject.toml changes

### 3. Security Improvements (MEDIUM PRIORITY)

**Recommended changes:**
a) Use non-root user (with CUDA considerations):
```dockerfile
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser
```

b) Use specific base image digests:
```dockerfile
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime@sha256:...
```

c) Add security scanning to CI/CD:
```bash
docker scan snsw:latest
trivy image snsw:latest
```

d) Remove build tools from runtime image (via multi-stage)

**Expected Impact:**
- Reduced privilege escalation risk
- Smaller attack surface
- Compliance with security best practices

### 4. Build Speed Improvements (MEDIUM PRIORITY)

**Use BuildKit cache mounts:**
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir .
```

**Parallel dependency installation:**
```dockerfile
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir . && \
    pip install --no-cache-dir TTS peft transformers==4.35.2 \
    datasets safetensors scipy librosa faster-whisper yt-dlp
```

**Expected Impact:**
- 20-40% faster pip installations with cache mounts
- Better CI/CD pipeline performance

### 5. Additional Best Practices

**a) Add .dockerignore file:**
- Exclude: tests/, docs/, .git/, *.md, __pycache__/, OUTPUTS/, ARCHIVE/
- Impact: Faster context transfer, smaller context size

**b) Combine RUN commands:**
```dockerfile
# Before: 2 layers
RUN apt-get update && apt-get install -y ...
RUN rm -rf /var/lib/apt/lists/*

# After: 1 layer
RUN apt-get update && apt-get install -y ... \
    && rm -rf /var/lib/apt/lists/*
```

**c) Use --no-install-recommends:**
```dockerfile
RUN apt-get install -y --no-install-recommends package-name
```

**d) Pin Python package versions:**
- Consider pinning critical dependencies beyond just transformers
- Ensures reproducible builds

**e) Add health check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import torch; exit(0 if torch.cuda.is_available() else 1)"
```

## Implementation Priority

### Phase 1: Critical (Immediate Implementation)
1. ✅ Add .dockerignore file
2. ✅ Implement multi-stage build
3. ✅ Fix layer caching order
4. ✅ Remove build tools from runtime

**Expected benefits:** 40-60% smaller image, 5-10x faster rebuilds

### Phase 2: Important (Next Sprint)
1. Add BuildKit cache mounts
2. Implement non-root user (test CUDA compatibility)
3. Pin all dependency versions
4. Add health check

**Expected benefits:** Better security, 20-30% faster builds

### Phase 3: Nice-to-Have (Future)
1. Use image digests for base images
2. Implement vulnerability scanning
3. Add multi-platform builds (amd64/arm64)
4. Consider distroless/minimal base images

## Optimized Dockerfile Summary

The optimized Dockerfile (`Dockerfile.optimized`) includes:

✅ Multi-stage build (builder + runtime)  
✅ Optimized layer caching order  
✅ Removed build dependencies from final image  
✅ Combined RUN commands for fewer layers  
✅ --no-install-recommends flag  
✅ Proper cleanup in same layer  
✅ Environment variables consolidated  
✅ Comments for optional security improvements  

## Testing Recommendations

1. **Build comparison:**
```bash
# Original
docker build -t snsw:original -f Dockerfile .

# Optimized
docker build -t snsw:optimized -f Dockerfile.optimized .

# Compare sizes
docker images | grep snsw
```

2. **Functionality test:**
```bash
docker run --rm --gpus all snsw:optimized python -c "import torch; print(torch.cuda.is_available())"
```

3. **Rebuild speed test:**
```bash
# Modify a source file
touch src/kaggle/run_inference.py

# Time rebuild
time docker build -t snsw:optimized -f Dockerfile.optimized .
```

## Expected Results

| Metric | Original | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Image Size | ~8-10GB | ~6-7GB | 20-30% reduction |
| First Build | ~15-20min | ~15-20min | Similar |
| Rebuild (code change) | ~15-20min | ~1-2min | 90% faster |
| Security Issues | High | Medium | Reduced attack surface |
| Layers | ~15 | ~10 | Simplified |

## Notes

- CUDA support requires root or proper device permissions; test non-root user thoroughly
- Model files should be mounted at runtime, not baked into image
- Consider using docker-compose for development with volume mounts
- BuildKit features require Docker 18.09+ and DOCKER_BUILDKIT=1 environment variable
