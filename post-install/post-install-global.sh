#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport

echo "--- Running post-installation-global.sh"


echo "--- Adding Start Script for dc-ccli"
cat << 'EOF' > /var/devcontainer.com/dc-ccli.start.sh
#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport

dc-ccli server
EOF
chmod +x /var/devcontainer.com/dc-ccli.start.sh


echo "--- Adding Service for dc-ccli"
echo "dcccli: /var/devcontainer.com/dc-ccli.start.sh" >> /var/devcontainer.com/services.proc
