#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport



echo "--- Adding Start Script"
cat << 'EOF' > /var/devcontainer.com/postgresql.org.start.sh
#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport

postgres 
EOF
chmod +x /var/devcontainer.com/postgresql.org.start.sh



echo "--- Adding Service"
echo "..."
echo "postgresql: /var/devcontainer.com/postgresql.org.start.sh" >> /var/devcontainer.com/services.proc

