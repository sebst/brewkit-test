# FROM mcr.microsoft.com/vscode/devcontainers/base:debian-11

# # Install Homebrew
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# RUN     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# RUN     export PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"

# Install [pkgx](https://pkgx.dev)
# RUN     /home/linuxbrew/.linuxbrew/bin/brew install pkgxdev/made/pkgx

# # Install [Brewkit](https://github.com/pkgxdev/brewkit)
# RUN     pkgx +brewkit

# # Check the version of Brewkit
# RUN     pkgx bk --version




# Use the base image
FROM mcr.microsoft.com/vscode/devcontainers/base:debian-11




# Install dependencies for Homebrew
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    file \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*


# Add user vscode
# RUN     useradd -m vscode
# Add user vscode to the sudoers
# RUN     echo "vscode ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER    vscode

# Install Homebrew
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
RUN     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
RUN     export PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"
# # Install [pkgx](https://pkgx.dev)
RUN     /home/linuxbrew/.linuxbrew/bin/brew install pkgxdev/made/pkgx
# # Install [Brewkit](https://github.com/pkgxdev/brewkit)
RUN     /home/linuxbrew/.linuxbrew/bin/pkgx +brewkit
# # Check the version of Brewkit
RUN     /home/linuxbrew/.linuxbrew/bin/pkgx bk --version


# # Install Homebrew
# RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
#     && echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /root/.profile \
#     && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" \
#     && brew --version

# # Set up Homebrew in the environment
# ENV PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:${PATH}"
# RUN echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /etc/bash.bashrc

# # Verify Homebrew installation
# RUN brew --version

# Set the default shell to bash
SHELL ["/bin/bash", "-c"]