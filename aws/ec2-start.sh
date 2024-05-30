#!/bin/bash
# This script is intended to be used as user data for an AWS EC2 instance.

# Update and install necessary packages
sudo yum update -y
sudo yum install -y tzdata
sudo yum install -y git
sudo yum install -y python3
sudo yum install -y python3-pip

# Set Timezone
timedatectl set-timezone Asia/Hong_Kong

# Clone the repository from GitHub
git clone https://github.com/wkchiuea/NewsAggregatorHK-python.git /home/ec2-user/myrepo

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

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Create MongoDB collections
mongo <<EOF
use raw_news;
db.createCollection("news_data");
db.createCollection("job_log");
exit;
EOF

# Set up API token
# export APIFY_API_TOKEN="haha"

# Set up a cron job to run the scrape.py script every hour
# Add the cron job to the crontab
(crontab -l 2>/dev/null; echo "0 * * * * /usr/bin/python3 /home/ec2-user/myrepo/web-scraping/web_scraping_v2.py") | crontab -

# Print a message indicating that the setup is complete
echo "Setup complete. The web_scraping_v2.py script will run every hour."
