# vSenti
Time series sentiment visualizer for VMware products

## Goals
* ~~Inspired by [usa live tweets](https://usa2016livetweets.herokuapp.com/), offer live sentiment analysis of VMware related tweets~~
* With [libscore](http://libscore.com) style of UI, offer time series sentiment analysis of 3 VMware core products: vSphere, vSAN and NSX, from various data sources
* Train classifier that gives sentiment confident level above 60%

## Requirement
* Docker engine >= 1.12
* Docker compose >= 1.8

## Development
**Common**  
```
docker-compose build
docker-compose up
```

**Database**  
MySQL is fired up from docker compose, so simply access with:
```
mysql -h 127.0.0.1 -P 3306 -u vsenti -p
```
and input password with `123456`

Generate dummy data
```
sh init_scripts/populate_vsenti_db_with_dummy_data.sh
```

**API Node.js app**
The API for vsenti is exposed as a REST API which is hosted on an Express Node app
This app is a linked as a submodule. To begin development, for the first time do
```
git submodule init
git submodule update --recrusive
```
This pulls the external repository as a local copy. To fetch the updated submodule, you can rerun the `update` command.

## Deployment
I would suggest run `virtualenv` and `pip install` all dependencies inside `vsenti-analyser` and `vsenti-scrapper`. 

**DB init**  
After running a fresh `vsenti-database` through docker compose:
```
cd vsenti-database
sh populate_vsenti_db.sh
```

**Collect data**  
```
cd vsenti-scrapper
scrapy crawl vmtnforum
```

**Analyze data**  
```
cd vsenti-analyzer
python vsenti.py run --model=vsenti_svm_model.bin --max-articles=3000
```
Ideally the analyzer and crawler will run as cron/scheduler job, so the `max-articles` parameter can be as small as 20.

## Architecture
Below is the workflow and platform architecture of vSenti:

![vSenti Architecture 0.2](./vsenti-architecture-v0.2.png)
