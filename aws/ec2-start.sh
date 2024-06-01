#!/bin/bash
# This script is intended to be used as user data for an AWS EC2 instance.

# Update the package list and install necessary packages
sudo yum update -y
sudo yum install -y tzdata
sudo yum install -y git
sudo yum install -y logrotate

sudo yum install -y \
    alsa-lib \
    atk \
    cups-libs \
    dbus-glib \
    GConf2 \
    gtk3 \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-fonts-Type1 \
    xorg-x11-fonts-misc

sudo amazon-linux-extras install epel -y
sudo yum install -y chromium

# Enable and install Python 3.8 and pip
sudo amazon-linux-extras enable python3.8
sudo yum install -y python3.8
sudo yum install -y python3-pip

# Update the default python3 symlink to point to python3.8
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
sudo alternatives --set python3 /usr/bin/python3.8

# Verify the Python version
python3 --version

# Set Timezone
sudo timedatectl set-timezone Asia/Hong_Kong

# Clone the repository from GitHub
git clone -b release/aws-deploy https://github.com/wkchiuea/NewsAggregatorHK-python.git /home/ec2-user/myrepo

# Navigate to the repository directory
cd /home/ec2-user/myrepo

# Install the required Python packages
pip3 install -r requirements.txt

# Install MongoDB
sudo tee /etc/yum.repos.d/mongodb-org-4.4.repo <<EOF
[mongodb-org-4.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/4.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc
EOF

sudo yum install -y mongodb-org
sudo yum install -y mongodb-mongosh

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Create MongoDB collections
sudo mongosh <<EOF
use raw_news;
db.createCollection("news_data");
db.createCollection("comments");
db.createCollection("job_log");
exit;
EOF

# Set up API token
##### export APIFY_API_TOKEN="haha"
##### export FLASK_SECRET="haha"

# Set up a cron job to run the scrape.py script every hour
# Add the cron job to the crontab
echo "0 * * * * /usr/bin/python3 /home/ec2-user/myrepo/web-scraping/web_scraping_v2.py >> /home/ec2-user/myrepo/web-scraping/web_scraping_v2.log 2>&1" | sudo crontab -
echo "30 * * * * /usr/bin/python3 /home/ec2-user/myrepo/web-scraping/fb_comment.py 25 --comments_limit 50 >> /home/ec2-user/myrepo/web-scraping/fb_comment.log 2>&1" | sudo crontab -

# web_scraping_v2.py
# Create the logrotate configuration for the log file
cat <<EOF > /etc/logrotate.d/web_scraping_v2
/home/ec2-user/myrepo/web-scraping/web_scraping_v2.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 root root
    postrotate
        /usr/bin/systemctl reload crond > /dev/null 2>&1 || true
    endscript
}
EOF

# Ensure correct permissions for the logrotate configuration
chown root:root /etc/logrotate.d/web_scraping_v2
chmod 644 /etc/logrotate.d/web_scraping_v2

# fb_comment.py
# Create the logrotate configuration for the log file
cat <<EOF > /etc/logrotate.d/fb_comment
/home/ec2-user/myrepo/web-scraping/fb_comment.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 root root
    postrotate
        /usr/bin/systemctl reload crond > /dev/null 2>&1 || true
    endscript
}
EOF

# Ensure correct permissions for the logrotate configuration
chown root:root /etc/logrotate.d/fb_comment
chmod 644 /etc/logrotate.d/fb_comment

# flask/app.py
# Create the logrotate configuration for the log file
cat <<EOF > /etc/logrotate.d/flask_app
/home/ec2-user/myrepo/flask/flask_app.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 root root
    postrotate
        /usr/bin/systemctl reload crond > /dev/null 2>&1 || true
    endscript
}
EOF

# Ensure correct permissions for the logrotate configuration
chown root:root /etc/logrotate.d/flask_app
chmod 644 /etc/logrotate.d/flask_app

# Print a message indicating that the setup is complete
echo "Setup complete. The web_scraping_v2.py script will run every hour."

# Start Server
cd /home/ec2-user/myrepo/flask
sudo touch /home/ec2-user/myrepo/flask/flask_app.log
sudo chown root:root /home/ec2-user/myrepo/flask/flask_app.log
# Create systemd service file
sudo bash -c 'cat <<EOF > /etc/systemd/system/flask-app.service
[Unit]
Description=Flask App using Waitress
After=network.target

[Service]
ExecStart=/usr/local/bin/waitress-serve --listen=0.0.0.0:5000 app:app
WorkingDirectory=/home/ec2-user/myrepo/flask
StandardOutput=append:/home/ec2-user/myrepo/flask/flask_app.log
StandardError=append:/home/ec2-user/myrepo/flask/flask_app.log
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF'
# Enable and start the service
sudo systemctl enable flask-app.service
sudo systemctl start flask-app.service

echo "*** Server started successfully"

echo "***** All setup complete"