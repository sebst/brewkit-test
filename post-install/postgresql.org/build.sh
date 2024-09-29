#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport



POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_DB="database"

postgresql_user_name="postgres"
postgresql_user_id="510"
postgresql_group_name="postgres"
postgresql_group_id="510"

POSTGRESQL_HOME="/var/run/postgresql"
POSTGRESQL_RUNTIME_DIR="/var/run/postgresql"
POSTGRESQL_CONFIG_DIR="/var/run/postgresql/config"

PGDATA="/var/run/postgresql/data"
POSTGRESQL__data_directory="/var/run/postgresql/data"
POSTGRESQL__external_pid_file="/var/run/postgresql/postgresql.pid"
POSTGRESQL__config_file="/var/run/postgresql/config/postgresql.conf"
POSTGRESQL__hba_file="/var/run/postgresql/config/pg_hba.conf"
POSTGRESQL__ident_file="/var/run/postgresql/config/pg_ident.conf"

POSTGRESQL__unix_socket_directories="/var/run/postgresql"
POSTGRESQL__log_directory="/var/run/postgresql/logs"



echo '[postgresql-init] Create postgresql daemon group (if not exists) ...'
&>/dev/null getent group "${postgresql_group_name}" || groupadd \
  --gid "${postgresql_group_id}" \
    "${postgresql_group_name}"


echo '[postgresql-init] Create postgresql daemon user (if not exists) ...'
&>/dev/null id -u "${postgresql_user_name}" || useradd \
  --uid "${postgresql_user_id}" \
  --gid "${postgresql_group_id}" \
  --system \
  --no-create-home \
  --home-dir "${POSTGRESQL_HOME}" \
  --shell '/usr/sbin/nologin' \
  "${postgresql_user_name}"


printf '[postgresql-init] Remove existing POSTGRESQL_RUNTIME_DIR="%s"\n' \
  "${POSTGRESQL_RUNTIME_DIR}"
rm -rf "${POSTGRESQL_RUNTIME_DIR}"

printf '[postgresql-init] Create postgresql directories (HOME, [..]) ...\n'
printf '[postgresql-init] - %s="%s"\n' \
  'POSTGRESQL_HOME' "${POSTGRESQL_HOME}" \
  'POSTGRESQL_RUNTIME_DIR' "${POSTGRESQL_RUNTIME_DIR}" \
  'POSTGRESQL_CONFIG_DIR' "${POSTGRESQL_CONFIG_DIR}"
install \
  -d \
  --mode=2770 \
  --owner=root \
  --group="${postgresql_group_name}" \
    "${POSTGRESQL_HOME}" \
    "${POSTGRESQL_RUNTIME_DIR}" \
    "${POSTGRESQL_RUNTIME_DIR}/filebeat" \
    "${POSTGRESQL_RUNTIME_DIR}/filebeat/data" \
    "${POSTGRESQL_RUNTIME_DIR}/filebeat/logs" \
    "${POSTGRESQL_RUNTIME_DIR}/filebeat/module" \
    "${POSTGRESQL_CONFIG_DIR}" \
    "${POSTGRESQL_CONFIG_DIR}/postgresql.conf.d" \
    "${POSTGRESQL_CONFIG_DIR}/pg_ident.conf.d" \
    "${POSTGRESQL_CONFIG_DIR}/pg_hba.conf.d" \
    "${POSTGRESQL__log_directory}"

# TODO: if "locale -a" does not contain
locale-gen "en_US.UTF-8"

# see also: "cat /var/run/postgres/data/PG_VERSION" => "16"
readonly postgres_version="$(postgres -V | grep -oE '[.0-9]+' | head -1)"
readonly postgres_major_version="${postgres_version%.*}"

printf '[postgresql-init] environment variables\n'
env | grep -iE '^postgres'



echo "--- Adding Start Script"
cat << 'EOF' > /var/devcontainer.com/postgresql.org.start.sh
#!/usr/bin/env -S bash --noprofile --norc -o errexit -o pipefail -o noclobber -o nounset -o allexport

sudo -u postgres postgres -D "${POSTGRESQL_CONFIG_DIR}" 
EOF
chmod +x /var/devcontainer.com/postgresql.org.start.sh



echo "--- Adding Service"
echo "..."
echo "postgresql: /var/devcontainer.com/postgresql.org.start.sh" >> /var/devcontainer.com/services.proc

