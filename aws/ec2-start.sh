#!/bin/bash
# This script is intended to be used as user data for an AWS EC2 instance.

# Update the package list and install necessary packages
sudo yum update -y
sudo yum install -y tzdata
sudo yum install -y git

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
git clone -b test/aws-web-scraping https://github.com/wkchiuea/NewsAggregatorHK-python.git /home/ec2-user/myrepo

# Navigate to the repository directory
cd /home/ec2-user/myrepo/web-scraping

# Install the required Python packages using pip within the virtual environment
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
mongosh <<EOF
use raw_news;
db.createCollection("news_data");
db.createCollection("comments");
db.createCollection("job_log");
exit;
EOF

# Set up a cron job to run the scripts every hour
# Add the cron job to the crontab
(crontab -l 2>/dev/null; echo "0 * * * * /usr/bin/python3 /home/ec2-user/myrepo/web-scraping/web_scraping_v2.py") | crontab -
#(crontab -l 2>/dev/null; echo "30 * * * * /home/ec2-user/myrepo/venv/bin/python /home/ec2-user/myrepo/web-scraping/fb_comment.py 25 --comments_limit 50") | crontab -

# Print a message indicating that the setup is complete
echo "Setup complete. The web_scraping_v2.py script will run every hour."
