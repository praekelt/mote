manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

$manage syncdb --noinput --settings=project.settings

#the following two commands require nodejs 5.6.x + to be present on the server.
#to achieve this i ran the following commands on the server:

# sudo apt-get --purge remove node
# sudo apt-get --purge remove nodejs
# curl -sL https://deb.nodesource.com/setup_5.x | sudo -E bash -
# sudo apt-get install -y nodejs

cd /var/praekelt/kevro-styleguide/
npm install
bower install --allow-root
npm run barron-gulp
npm run barron-webpack

echo "start- collect statics:"
# $manage collectstatic --noinput --settings=project.settings
$manage collectstatic --noinput --settings=project.settings
