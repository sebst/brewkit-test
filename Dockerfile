# FROM mcr.microsoft.com/vscode/devcontainers/base:debian-11
FROM pkgxdev/pkgx

# # Install dependencies for Homebrew
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    file \
    git \
    procps \
    sudo \
    && rm -rf /var/lib/apt/lists/*


# Add user vscode
RUN     useradd -m vscode
# Add user vscode to the sudoers
RUN     echo "vscode ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER    vscode

RUN     pkgx +bk

COPY    --chown=vscode ./build.sh /home/vscode/


# Set the default shell to bash
SHELL ["/bin/bash", "-c"]
