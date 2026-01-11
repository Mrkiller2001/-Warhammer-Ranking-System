FROM ubuntu:24.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    git \
    curl \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create a non-root user with sudo access (or use existing user if UID 1000 exists)
RUN if id -u 1000 >/dev/null 2>&1; then \
        USERNAME=$(id -un 1000); \
        usermod -l devuser $USERNAME 2>/dev/null || true; \
        groupmod -n devuser $(id -gn 1000) 2>/dev/null || true; \
        usermod -d /home/devuser -m devuser 2>/dev/null || true; \
    else \
        useradd -m -s /bin/bash -u 1000 devuser; \
    fi \
    && echo "devuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /workspace

# Change ownership of workspace
RUN chown -R devuser:devuser /workspace

USER devuser
