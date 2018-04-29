# HTTP Proxy with Content Filtering and Site Blocking

This HTTP proxy, when run on a local machine, implements content filtering and site blocking based on the user's chosen keywords and blocked sites. It includes its own caching mechanism.

## Setup

config - Both the sections of this file can be updated by the user to customize the proxy. The [ Keywords ] section has words that the proxy will notify the user about if found, and the [ Blocked ] section includes a list of urls to avoid. 

The network settings need to be updated so that HTTP traffic is routed through the proxy. Under the network settings for your machine, add an HTTP proxy routed through localhost. Choose whatever port number you will pass in when running the proxy.

## Run

python3 proxy.py < portno >
