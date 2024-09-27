#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport


echo "--- Installing webserver"
sudo mkdir -p /var/lib/html
sudo chmod -R a+rw /var/lib/html
sudo rm /var/lib/html/index.html
echo "Hello World" > /var/lib/html/index.html


echo "--- Adding Start Script"
cat << 'EOF' > /var/devcontainer.com/python.org.start.sh
#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport

python -m http.server -d /var/www/html
EOF



echo "--- Adding Service"
echo "python: /var/devcontainer.com/python.org.start.sh" >> /var/devcontainer.com/services.proc

