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

## Architecture
Below is the workflow and platform architecture of vSenti:

![vSenti Architecture 0.2](./vsenti-architecture-v0.2.png)
