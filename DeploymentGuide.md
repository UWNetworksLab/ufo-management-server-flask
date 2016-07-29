# ufo-management-server

Management Server component of uProxy for Orgs (UfO)

## Deployment

### Create an Instance

The Management Server can be deployed locally or to the cloud. We have setup a one-click to deploy instance on Heroku to facilitate easy updating. That is the preferred method for creating a new instance as it is what customers will use. There is also a means to do this via command line. Both approaches are described here.

#### Create an Instance via Click-to-Deploy

The click to deploy method creates a new app based on a template from github. Heroku will read the configurations already created there and generate a new app for you, with almost no interaction required. Simply follow these steps:

1. Visit the Click-to-Deploy [link](https://dashboard.heroku.com/new?template=https://github.com/uProxy/ufo-management-server-flask/tree/master).
  * TODO(eholder): Switch this to production version after beta testing. We want testers to use master in the meantime for quick fixes.
  * TODO(eholder): Create the Heroku button on the website.
1. Login if necessary.
1. Fill in the app name if desired.
1. Click the “Deploy” button.
1. Wait for Heroku to create the app...
1. Once Heroku has finished, click the “Manage App” button to navigate to Heroku’s management dashboard.
1. On the management dashboard, under the Resources tab, select “Upgrade to Hobby” to bring up the upgrade prompt.
1. From here, select one of the levels higher than Free and click Save.
  * This is required in order to scale your dynos up to use worker and clock processes.
  * The hobby level is the least expensive level that allows for more than 2 dynos (only 2 are available under the free level) and is what we recommend.
  * If you have not previously setup billing on Heroku, it will prompt you to do so, as running the 3 dynos (web, worker, and clock) will each cost $7/month or $21/month total.
1. Once upgraded to a higher level, click the pencil icon next to each dyno to edit it.
1. Enable each dyno and confirm the change.
  * TODO(eholder): It would be nice to automatically start Heroku at the Hobby level at least with the dynos already running, thus eliminating steps 6-10.
1. Once complete, you can then navigate directly to the app via clicking the menu button in the top and selecting “Open app” or by visiting the following address:
  * `http://<your_instance_name>.herokuapp.com/setup/`

#### Create an Instance via Command Line

Before deploying a test instance to Heroku, first follow their [steps to install](https://devcenter.heroku.com/articles/getting-started-with-python#introduction) the toolbelt and setup the local environment.
On ubuntu, heroku is installed under `/usr/local/heroku/bin` directory.

To deploy a test instance to Heroku, run the commands listed below. These can be chained on the commandline. Note: `--app` is only required if you have more than one heroku app. If you have multiple apps, then you will have multiple heroku remotes. Use `git remote -v`to view them, but if you use one, the name is like `heroku`.

1. `git checkout <your_dev_branch>`
1. `heroku login (only necessary if you aren’t already logged in)`
1. `heroku create <your_instance_name>`
1. `heroku buildpacks:add heroku/nodejs --app <your_instance_name>`
1. `heroku buildpacks:add heroku/python --app <your_instance_name>`
1. `heroku buildpacks:add https://github.com/uProxy/nginx-buildpack --app <your_instance_name>`
1. `git push <your_heroku_remote_name> <your_dev_branch>:master (optional -f)`
1. `heroku addons:create heroku-postgresql --app <your_instance_name>`
1. `heroku addons:create redistogo --app <your_instance_name>`
1. `heroku run python setup_database.py --app <your_instance_name>`
1. `heroku ps:scale web=1 worker=1 clock=1 --app <your_instance_name>`
1. `heroku ps --app <your_instance_name> (optional)`
1. `heroku logs --tail --app <your_instance_name> (optional)`

Now, you can visit your test instance on heroku.
* `http://<your_instance_name>.herokuapp.com/setup/`

### Update an Instance

Similarly to creating an instance, updating an instance can be done via the Heroku UI or via command line. The Heroku UI approach is what customers will use, so refer to that documentation which will be expanded in time. The command line approach is useful for debugging test environments. Each is described below.

#### Update an Instance in Heroku

To update a running instance in Heroku, the instance will need to be connected to the github repository once and then the update process can be easily run afterwards.

##### Connect a Heroku Instance to Github

1. Navigate to the Heroku dashboard for the instance desired, such as the link below:
  * https://dashboard.heroku.com/apps/<your_instance_name>/resources
1. Click the “Deploy” tab at the top.
1. In the “Deployment Method” section, click Github.
1. In the “Connect to Github” section, find your repository for the management server.
  * For the production instance, this will be under the uProxy Organization and named ufo-management-server-flask.
1. Select “Connect” next to your repository.

##### Deploy an Update After Connecting to Github

1. Navigate to the Heroku dashboard for the instance desired, such as the link below:
  * https://dashboard.heroku.com/apps/<your_instance_name>/resources
1. Click the “Deploy” tab at the top.
1. In the “Manual Deploy” section, select a branch to deploy.
  * For the production instance, the branch will be named production.
1. Click “Deploy Branch”.

Optionally, you can also enable automatic deployment from a branch of your choosing in the “Automatic Deploys” section. This is NOT recommended for any branch other than production if using the ufo-management-server-flask repository.

Note: The nightly release uses the master branch with automatic deployment setup. This is for development purposes only and should NOT be used by customers.

#### Update an Instance on Command Line

After the initial creation of a test instance, you can run an abbreviated set of commands to update the test instance with your code change.

1. `git push heroku <your_dev_branch>:master (optional -f)`
1. `heroku ps:scale web=1 worker=1 clock=1 --app <your_instance_name>`
1. `heroku ps --app <your_instance_name> (optional)`
1. `heroku logs --tail --app <your_instance_name> (optional)`

The same steps as updating a test instance apply for updating the production instance. The production instance is named ufo-prod and is accessed at https://ufo-prod.herokuapp.com/ . Before updating the production instance, consult the steps listed under Release.

### Remove an Instance

To tear down the test instance:
* `heroku destroy <your_instance_name>`
The production instance should NEVER BE REMOVED!

### Debug an Instance

To show the status of a running instance:
* `heroku ps --app <your_instance_name> (optional)`
To view the configuration of a running instance:
* `heroku config --app <your_instance_name> (optional)`
To run a local instance:
* `heroku local`
To view the logs of an instance:
* `heroku logs --app <your_instance_name> (optional)`

### Setup SSH Keys to Access Proxy Server

1. Know which user the ssh-client will be using to access the proxy server.  Currently, this is hard-coded to root.
1. Either have an existing key-pair or generate it.
1. Copy the public key to the user who the ssh-client will be accessing the proxy server.
  * `sudo ssh-copy-id -i <full_path_to_public_key> <root_or_other_user>@<proxy_server_ip_address>`
  * [More details here](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-14-04) especially if you want to setup other non-root user.
1. Save the corresponding private key to the management server for this proxy server.

### Securing the Server with TLS

When deployed on Heroku, the Management Server utilizes an [nginx buildpack](https://github.com/uProxy/nginx-buildpack) with [our own configuration](https://github.com/uProxy/nginx-buildpack/blob/master/config/nginx.conf.erb#L43) to provide a secure layer for HTTPS/HTTP + TLS. We redirect all traffic to the HTTPS version via a 301 Moved Permanently redirect and also provide the [HTTP Strict Transport Security (HSTS)](https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security) header to prevent clients that have visited via HTTPS to get downgraded to HTTP without the browser recognizing the potential attack. This is automatically configured out of the box during deployment and works by using Heroku’s SSL cert. When using a custom domain name, an SSL cert for that domain must be provided, but from our perspective it will function identically.

Outside of Heroku however, the nginx setup is entirely avoided since we do not anticipate users to deploy with gunicorn or a Procfile (as required by Heroku). We encourage anyone running the management server off of Heroku to use a similar system to nginx to provide their own HTTPS/HTTP + TLS security where available.

### Configuring Recaptcha for Login Protection

The Management Server utilizes [Recaptcha](https://www.google.com/recaptcha/intro/index.html) to prevent brute force login attacks. You can configure a recaptcha project by visiting the [admin setup site](https://www.google.com/recaptcha/admin#list) and registering a new site. You'll want to add your deployed app's domain, such as my-app-name.herokuapp.com. This will generate site and secret keys for your app.

Next, you need to add those keys as environment variables in your app on Heroku. Here are the steps to do that:

1. Visit the [heroku dashboard](https://dashboard.heroku.com/apps).
1. Navigate to your app, such as my-app-name.
1. Go to the Settings tab.
1. Click 'Reveal Config Vars'
1. Scroll to the bottom.
1. Type in RECAPTCHA_SITE_KEY for the key and copy and paste in the value for the site key you received on the [admin setup site](https://www.google.com/recaptcha/admin#list) for your app.
1. Click Add.
1. Type in RECAPTCHA_SECRET_KEY for the key and copy and paste in the value for the secret key you received on the [admin setup site](https://www.google.com/recaptcha/admin#list) for your app.
1. Click Add.

That's it! Your app should now pick up the site and secret keys to use recaptcha after several failed logins attempts. If you run into an issue with these not being picked up, we suggest that you redeploy the server by pushing a blank update. For information on that, check the sections above for Update an Instance.

## Troubleshooting

### SQLAlchemy Unable to Open Database/app.instance_path Not Pointing to App Directory

This error is caused by your virtual environment not being setup or not currently running. You can enable your virtual environment with the following command:

`. venv/bin/activate`

Furthermore, if you need to reset your entire environment, you can with the following steps:

1. Make sure venv is turned on: `. venv/bin/activate`
1. Pickup the latest dependencies: `pip install -r requirements.txt and bower install`
1. Create the vulcanized html: `./vulcanize.sh`
1. Reset the database: `rm -fr instance/app.db` and `python setup_database.py`
1. Start the server (if it isn't already): `python run.py`
1. Go through the setup flow. `http://your-app-instance/setup`

### Debugging Enqueued Jobs

The free nano instance of redis is prone to run out of memory upon repeated exceptions. Here are some general tips on debugging / flushing enqueued job on redis.

* Heroku has an integrated dashboard of redis info. You can also find the redis host, port, and access parameters here.
* You can login via CLI to get more info.
  * `redis-cli -h catfish.redistogo.com -p 10290 -a fa537e8f6dfa5c327ff2825759d71b91 info`
* You can also wipe redis clean and start over.
  * `redis-cli -h catfish.redistogo.com -p 10290 -a fa537e8f6dfa5c327ff2825759d71b91 flushall'
