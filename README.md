# shipp. Smart Home Integrated Privacy Protection

This project was developed as part of a bachelor thesis at the University of Zurich in Spring 2023. 

[![Docker Version][docker-image]][dockerhub-url]


*shipp* is an extensible open-source privacy enhancing technology designed for smart home environments. 
By integrating existing tools into a unified framework, it aims to monitor and control smart home devices' communication behavior through user-defined policies.
The goal is to increase transparency and limit data collection.

![](shipp_logo.png)

## Installation

On Raspberry Pi OS:

1. Install Docker.
    ```bash
    sudo apt-get update
    sudo apt-get install docker
    ```
2. Set up your project directory and set up the configuration for the reverse proxy (Nginx).
   Copy the [nginx folder](https://github.com/elduwa/shipp/tree/master/nginx) from the repository to your project directory.
   ```bash
    mkdir shipp
    cd shipp
    # Copy the nginx folder from the repository to your shipp directory.
    ```
    Replace the `${LOCAL_NETWORK_IP_RANGE}` placeholder in the `default.conf.template` file with your local network IP range in CIDR notation (e.g. 193.xxx.1.0/24)
   

3. Create a resolv.conf file in the project directory:
    ```bash
    touch resolv.conf
    ```
    Add the following lines to the file:
    ```
    nameserver 127.0.0.1
    options ndots:0
    ```

4. Set up your docker-compose.yml for this project. Use the [template](https://github.com/elduwa/shipp/blob/master/docker-compose.yml) provided in the repository.
   Consult the respective documentation for [Pi-hole](https://github.com/pi-hole/docker-pi-hole), [InfluxDB](https://github.com/docker-library/docs/blob/master/influxdb/README.md) and [Home Assistant](https://www.home-assistant.io/installation/raspberrypi#install-home-assistant-container) for further information on the setup of these services.
   Listed below is a table containing the environment variables that require configuration to install the *shipp* service.

   | ENV Variable        | Example              | Description                                                 |
   |---------------------|----------------------|-------------------------------------------------------------|
   | `SECRET_KEY`          | 32-bit hex key       | Used by the flask application for authentication.           |
   | `API_SECRET_KEY`      | Fernet generated key | Used to encrypt API keys on the Database.                   |
   | `INFLUXDB_AUTH_TOKEN` | 32-bit hex key       | Needs to be the same as `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`. |
   | `PIHOLE_DOMAIN`       | pi.hole              | Used to address Pi-hole in the local network.               |
   | `PIHOLE_AUTH_TOKEN`   |                      | Can be looked up in the Pi-hole web interface.              |
   | `MAIL_SERVER`         | mail.gmx.net         | The SMTP server used to deliver user notifications.         |
   | `MAIL_PORT`           | 587                  | The corresponding port for the SMTP server.                 |
   | `MAIL_USERNAME`       | shipp.info@gmx.ch    | Sender address (login) for email notifications.             |
   | `MAIL_PASSWORD`       |                      | Corresponding password for `MAIL_USERNAME` account            |
   | `TZ`                  | Europe/Zurich        | Your local timezone.                                        |

   To generate a secret key for the `SECRET_KEY` and `INFLUXDB_AUTH_TOKEN` (=`DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`) variable, you can use the following command:
   ```bash
   openssl rand -hex 32
   ```
   To generate the `API_SECRET_KEY`, it is recommended to use [cryptography.fernet](https://cryptography.io/en/latest/fernet/):
   ```python
   from cryptography.fernet import Fernet
   Fernet.generate_key()
   ```

5. Start the docker containers.
    ```bash
    docker compose up -d
    ```

6. Configure devices to use Pi-hole as their DNS server: [Instructions](https://discourse.pi-hole.net/t/how-do-i-configure-my-devices-to-use-pi-hole-as-their-dns-server/245)


## Usage examples

### Using the dashboard
https://github.com/elduwa/shipp/assets/33815072/e52f1358-204a-47b2-8e5d-10d513506c99

### Adding a new device
https://github.com/elduwa/shipp/assets/33815072/0d7b9c6e-1d19-465f-bef3-5cf94be6b64e

### Modifying device policies
https://github.com/elduwa/shipp/assets/33815072/66cee392-0d71-40bf-a610-3e1597c072a2


## Development setup

### Prerequisites
- Python >= 3.11
- Node.js >= 18.16.0
- Ideally a running Pi-hole instance that is configured as the primary DNS server for your network.

1. Clone the *shipp* repository.
    ```bash
    git clone https://github.com/elduwa/shipp.git
    cd shipp
    ```
2. Add a .env file to the root directory of the project with the following contents:
   ```bash
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   SECRET_KEY=<your-secret-key>
   API_SECRET_KEY=<your-api-secret-key>
   SQLITE_URL=sqlite:///data/sqlite.db
   PIHOLE_DB_URL=sqlite:///data/gravity.db
   INFLUXDB_ACTIVE=false
   INFLUXDB_URL=http://localhost:8086/
   INFLUXDB_AUTH_TOKEN=<your-influxdb-auth-token>
   INFLUXDB_ORG=home
   INFLUXDB_BUCKET=communications
   PIHOLE_DOMAIN=pi.hole
   PIHOLE_AUTH_TOKEN=<your-pihole-auth-token>
   MAIL_SERVER=<notification-smtp-server>
   MAIL_PORT=<notification-smtp-server-port>
   MAIL_USERNAME=<sender-email-address/username>
   MAIL_PASSWORD=<your-password>
   SCHEDULER_TIMEINTERVAL=3600
   TZ=Europe/Zurich
   ```

3. Create a python virtual environment and install the dependencies for the project.
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
4. Install the Node.js dependencies and build the frontend sources.
    ```bash
    npm install
    npm run build
    ```
5. Start the Flask development server.
    ```bash
    flask run --debug
    ```

## Meta

Elliott Wallace – elliott.wallace@uzh.ch

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/elduwa/](https://github.com/elduwa/)

## Contributing

1. Fork it (<https://github.com/elduwa/shipp/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Disclaimer

This project is not affiliated with or officially endorsed by Pi-hole, InfluxDB or Home Assistant.

<!-- Markdown link & img dfn's -->
[docker-image]: https://img.shields.io/docker/v/elliottwallace/shipp?logo=docker&logoColor=%232496ED
[dockerhub-url]: https://hub.docker.com/r/elliottwallace/shipp

