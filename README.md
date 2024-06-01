# NewsAggregatorHK-python
Capstone Project utilizing web scraping, NLP, Tableau, Python Flask  
  
## Execute Scripts
News Scraping (Single Thread)  
- `sudo python3 web_scraping_v2.py`  
  
FB Comments : results_limit and comments_limit  
- `sudo python3 fb_comment.py 25 --comments_limit 50`  
  
Flask Service
- `sudo python3 app.py`
- Run in background : `sudo nohup python3 app.py &`
  
## AWS Deployment
1. Navigate to EC2 Page
2. Choose AMI as Amazon Linux 2
3. Setup SG and Key Pairs
4. Choose Volume
5. Paste "ec2-start.sh" to User Data
6. Setup correct secrets  
  
## Post Deployment
1. Check Cloud init log  
`sudo cat /var/log/cloud-init-output.log`  
2. Check Crontab  
`sudo crontab -l`  

## Maintenance
MongoDB
- `mongosh "mongodb://localhost:27017"`
- `use raw_news`
- `db.[COLLECTION_NAME].find()`
- `db.job_log.find()`
  
MongoDB Export Import Data
- Export
  - `mongodump --db raw_news --out /home/ec2-user/mongodump/`
  - `scp -i XXXX.pem -r ec2-user@AAAAAAAA:/home/ec2-user/mongodump/ ~/Downloads/mongodump/`
- Import
  - `scp -i XXXX.pem -r ~/Downloads/mongodump/ ec2-user@AAAAAAAA:/home/ec2-user/mongodump/`
  - `mongorestore --db raw_news /home/ec2-user/mongodump/raw_news`
  
Logs
- `tail ~/myrepo/web-scraping/web_scraping_v2.log`
- `tail ~/myrepo/web-scraping/fb_comment.log`
- `tail ~/myrepo/flask/flask_app.log`
  
Test Service
- `curl -G "http://127.0.0.1:5000/news`
- ` 
curl -G "http://127.0.0.1:5000/news"
     --data-urlencode "after_datetime=2024-05-31 14:00"  
     --data-urlencode "platform=now"
`
  
Cron Job
- Edit crontab : `sudo crontab -e`
- Show crontab : `sudo crontab -l`
  
**  ALL Data Collections are for academic purpose
