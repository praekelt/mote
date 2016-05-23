#!/bin/bash

# Add new sites or upgrade them if they already exist. This script is idempotent.


# Default values
CREDENTIALS=praekeltdeploy:password
USER=ubuntu

# Parse arguments
while getopts "d:r:b:c:u:l:" opt; do
    case $opt in
        d)
            DEPLOY_TYPE=$OPTARG;;
        r)
            OWNER_AND_REPO=$OPTARG;;
        b)
            BRANCH=$OPTARG;;
        c)
            CREDENTIALS=$OPTARG;;
        u)
            USER=$OPTARG;;
    esac
done

if [[ -z "$DEPLOY_TYPE" || -z "$OWNER_AND_REPO" || -z "$BRANCH" || -z "$CREDENTIALS" ]];
then
    echo "Usage: deploy-project.sh -d (deploy_type) -r (repo) -b (branch) -c (credentials) [-u (user)]"
    echo "Example: deploy-project.sh -p praekelt -d qa -r praekelt/jmbo-foo -b develop -c praekeltdeploy:mypassword"
    exit 1
fi

# Split OWNER_AND_REPO
INDEX=`expr index "$OWNER_AND_REPO" /`
REPO_OWNER=${OWNER_AND_REPO:0:(${INDEX}-1)}
REPO=${OWNER_AND_REPO:${INDEX}}

# Extract app name. Convention is repo has form jmbo-foo or jmbo.foo.
INDEX=`expr index "$REPO" [-.]`
APP_NAME=${REPO:${INDEX}}

# Compute deploy and working directory
DEPLOY_DIR=/var/${REPO_OWNER}
WORKING_DIR=/tmp/${REPO_OWNER}

# Ensure working directory is clean
sudo rm -rf $WORKING_DIR
sudo -u $USER mkdir -p $WORKING_DIR

# Checkout / update repo to working directory
cd $WORKING_DIR
if [ -d $APP_NAME ]; then
    cd $APP_NAME
    sudo -u $USER git checkout $BRANCH
    sudo -u $USER git pull
else
    sudo -u $USER git clone -b $BRANCH https://${CREDENTIALS}@github.com/$REPO_OWNER/$REPO.git ${APP_NAME}
fi

# Create database. Safe to run even if database already exists.
IS_NEW_DATABASE=0
DB_NAME=$APP_NAME
RESULT=`sudo -u postgres psql -l | grep ${DB_NAME}`
if [ "$RESULT" == "" ]; then
	echo "CREATE USER $DB_NAME WITH PASSWORD '$DB_NAME'" | sudo -u postgres psql
    echo "CREATE DATABASE ${APP_NAME} WITH ENCODING 'UTF-8'" | sudo -u postgres psql
	IS_NEW_DATABASE=1
fi

# Pip
cd /${WORKING_DIR}/${APP_NAME}
PIP_FILE=requirements.pip
sudo -u $USER ${DEPLOY_DIR}/python/bin/pip install -r ${PIP_FILE}
EXIT_CODE=$?
if [ $EXIT_CODE != 0 ]; then
    echo "Pip failure. Aborting."
    exit 1
fi

# Database setup
DJANGO_MANAGE="${DEPLOY_DIR}/python/bin/python manage.py"
if [ $IS_NEW_DATABASE -eq 1 ]; then
    read -p "Create a superuser if prompted. Do not generate default content. [enter]" y
    sudo -u $USER $DJANGO_MANAGE migrate --settings=project.settings
else
    sudo -u $USER $DJANGO_MANAGE migrate --noinput --settings=project.settings
fi

# Static files. Settings file is quite hardcoded.
sudo -u $USER rm -rf static
sudo -u $USER $DJANGO_MANAGE collectstatic --noinput -v 0 --settings=project.settings

# Generate config files
sudo -u $USER ${DEPLOY_DIR}/python/bin/python scripts/generate-configs.py config.yaml

# Copy / move directories in working directory to deploy directory
for f in `ls $WORKING_DIR`
do
    # Delete target directories that contain source. The others (log, media etc are updated).
    if [[ $f == log ]] || [[ $f == *-media-* ]] || [[ $f == *-media ]]; then
        sudo -u $USER cp -r -u ${WORKING_DIR}/${f} $DEPLOY_DIR/
    else
        # Delete target if it exists
        if [ -d ${DEPLOY_DIR}/${f} ]; then
            sudo -u $USER rm -rf ${DEPLOY_DIR}/${f}
        fi
        sudo -u $USER mv ${WORKING_DIR}/${f} $DEPLOY_DIR/

        # Create nginx symlinks if required
        if [ -e ${DEPLOY_DIR}/${f}/conf/nginx.conf ]; then
            sudo ln -s ${DEPLOY_DIR}/${f}/conf/nginx.conf /etc/nginx/sites-enabled/${APP_NAME}.conf
        fi

        # Create supervisor symlinks if required
        if [ -e ${DEPLOY_DIR}/${f}/conf/supervisor.conf ]; then
            sudo ln -s ${DEPLOY_DIR}/${f}/conf/supervisor.conf /etc/supervisor/conf.d/${APP_NAME}.conf
        fi
    fi
done

# Update supervisor
sudo supervisorctl update

# Restart memcached
sudo /etc/init.d/memcached restart

# Restart affected processes
for process in `sudo supervisorctl status | grep ${APP_NAME}- | awk '{ print length(), $0 | "sort -n -r" }' | awk '{ print $2 }'`
do
    sudo supervisorctl restart $process
    sleep 1
done

# Reload nginx
sudo /etc/init.d/nginx reload
