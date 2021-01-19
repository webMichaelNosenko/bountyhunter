# bountyhunter
A script for monitoring bug bounty programs. 
'Bountyhunter' sends out alerts to its users when it finds new bug bounty programs or detects changes in the old ones.
All data is collected from the Hackerone website. 
Alerts are sent out via telegram bot @BuggyHunter_bot. 
The application can be run via docker-compose, which uses two Dockerfiles - one for the main script, another one for the PostgreSQL database.
It can also be run without docker, which requires PostgreSQL installed and configured.


