#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport




echo "--- Adding Start Script"
cat << 'EOF' > /var/devcontainer.com/redis.io.start.sh
#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport

redis-server 
EOF
chmod +x /var/devcontainer.com/redis.io.start.sh



echo "--- Adding Service"
echo "redis: /var/devcontainer.com/redis.io.start.sh" >> /var/devcontainer.com/services.proc

