FROM python:3.11-slim

# Install git (needed for installing from GitHub)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# ---- build-time args (can be overridden) ----
ARG IARENA_URL="https://github.com/jparisu/IArena.git"
ARG IARENA_REF="main"   # branch/tag/commit

# Install the IArena library directly from GitHub
# (replace the URL with the real one if different)
RUN pip install "git+${IARENA_URL}@${IARENA_REF}"

# Copy your script into the container
COPY ./multiautograder_script.py /app/multiautograder_script.py

# Default command: run your script
ENTRYPOINT ["python", "/app/multiautograder_script.py"]
