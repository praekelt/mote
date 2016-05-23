#! /bin/bash

DEPLOY_DIR=/var/praekelt

echo "Prepare a clean Ubuntu 14.04+ server to serve Jmbo sites"

# Default values
INSTALL_SENTRY=0

# Parse arguments
while getopts "p:s:" opt; do
    case $opt in
        s)
            INSTALL_SENTRY=$OPTARG;;
    esac
done

echo "Installing required Ubuntu packages..."
sudo apt-get install python-virtualenv python-dev \
postgresql libjpeg-dev zlib1g-dev build-essential git-core \
memcached supervisor nginx postgresql-server-dev-all libxslt1-dev \
libproj0 libproj-dev libgeos-dev libgdal1-dev libgeoip1 \
libgeoip-dev postgis unzip \
redis-server postgresql-9.4-postgis-2.1 --no-upgrade
# todo: that postgresql-9.4-postgis-2.1 exact version is a problem. Needs
# softcoding or meta-package.

echo "Configuring PostgreSQL..."
# xxx: Regexes would be better. A loop would also be better.
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     trust/" /etc/postgresql/9.1/main/pg_hba.conf
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     trust/" /etc/postgresql/9.2/main/pg_hba.conf
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     trust/" /etc/postgresql/9.3/main/pg_hba.conf
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     trust/" /etc/postgresql/9.4/main/pg_hba.conf
sudo /etc/init.d/postgresql restart

echo "Configuring nginx..."
sudo sed -i "11i proxy_temp_path /tmp/nginx-cache-tmp;" /etc/nginx/nginx.conf
sudo sed -i "12i log_format rt_cache '\$remote_addr - \$upstream_cache_status [\$time_local] \$request_time \$upstream_response_time \$pipe \"\$request\" \$status \$body_bytes_sent \"\$http_referer\" \"\$http_user_agent\"';"  /etc/nginx/nginx.conf
sudo sed -i "13i proxy_cache_path /var/cache/nginx/thecache levels=1:2 keys_zone=thecache:1000m max_size=1000m inactive=600m;" /etc/nginx/nginx.conf
sudo mkdir -p /var/cache/nginx/thecache
# todo. Set max bucket size.
DIRNAME=`dirname $0`
sudo mkdir -p /usr/share/nginx/www/
sudo cp ${DIRNAME}/resources/50x.html /usr/share/nginx/www/
sudo cp ${DIRNAME}/resources/50x.png /usr/share/nginx/www/

echo "Setting up the www-data user..."
sudo mkdir /var/www
sudo mkdir /var/www/.pip_cache
sudo mkdir /var/www/.pip_download_cache
sudo chown -R www-data:www-data /var/www
sudo usermod www-data -s /bin/bash

echo "Setting up the Django directory..."
sudo mkdir ${DEPLOY_DIR}
sudo virtualenv ${DEPLOY_DIR}/python
sudo mkdir ${DEPLOY_DIR}/log
sudo chown -R www-data:www-data ${DEPLOY_DIR}

# Install genshi and gunicorn library for virtualenv Python
#sudo -u www-data ${DEPLOY_DIR}/python/bin/easy_install genshi
#sudo -u www-data ${DEPLOY_DIR}/python/bin/easy_install gunicorn

# Sentry server
if [ $INSTALL_SENTRY != 0 ]; then
    # Own virtualenv because Sentry installs eggs in it
    sudo virtualenv ${DEPLOY_DIR}/python-sentry
    sudo chown -R www-data:www-data ${DEPLOY_DIR}/python-sentry
    SENTRY_CONFIG=${DEPLOY_DIR}/sentry/sentry.conf.py
    sudo -u www-data ${DEPLOY_DIR}/python-sentry/bin/easy_install sentry
    sudo -u www-data ${DEPLOY_DIR}/python-sentry/bin/sentry init $SENTRY_CONFIG
    # Use our own conf file
    sudo -u www-data cp ${DIRNAME}/resources/sentry.conf.py $SENTRY_CONFIG
    # Replace secret key
    SECRET_KEY=`date +%s | sha256sum | head -c 56`
    sudo -u www-data sed -i "s/SECRET_KEY_PLACEHOLDER/${SECRET_KEY}/" $SENTRY_CONFIG
    sudo -u www-data ${DEPLOY_DIR}/python-sentry/bin/sentry --config=$SENTRY_CONFIG upgrade
    sudo cp ${DIRNAME}/resources/supervisor.sentry.conf /etc/supervisor/conf.d/sentry.conf
    sudo supervisorctl update
fi

# device-proxy
# Own virtualenv because device-proxy installs eggs in it
#sudo virtualenv ${DEPLOY_DIR}/python-deviceproxy --no-site-packages
#sudo chown -R www-data:www-data ${DEPLOY_DIR}/python-deviceproxy
#sudo -u www-data ${DEPLOY_DIR}/python/bin/pip install device-proxy>=0.4.1

echo ""
echo "All done! You probably want to run the deploy-project.sh script now."
if [ "$WEBDAV_PASSWORD" != "" ]; then
    echo "You can open a Webdav connection to $SERVERNAME on port 81 for the /praekelt folder. Username is webdav, password is $WEBDAV_PASSWORD."
fi
