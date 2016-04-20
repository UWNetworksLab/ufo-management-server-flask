# ufo-management-server

Management Server component of uProxy for Orgs (UfO)

## Status

[![Travis Status](https://travis-ci.org/uProxy/ufo-management-server-flask.svg)](https://travis-ci.org/uProxy/ufo-management-server-flask)
[![Code Health](https://landscape.io/github/uProxy/ufo-management-server-flask/master/landscape.svg?style=flat)](https://landscape.io/github/uProxy/ufo-management-server-flask/master)

## Tools

UfO is built using the following tools:
 - [Python](https://www.python.org/) as the primary language we code in.
 - [Flask](http://flask.pocoo.org/) for basic server functionality and interfaces.
 - [Polymer](http://www.polymer-project.org/) for UI.
 - [Travis](https://travis-ci.org/) for continuous integration.
 - [Landscape](https://landscape.io/dashboard) for code health monitoring.

To manage dependencies we use:
 - [Pip](http://pip.readthedocs.org/en/stable/) to install various python packages and libraries (specified in `requirements.txt`).
 - [NPM](https://www.npmjs.org/) to install node modules that we use for our build process (specified in `package.json`).
 - [Bower](http://bower.io) to install libraries that we use in the UI (specified in `bower.json`) including Polymer.


## Development

Development of UfO centers around one core git repository for the Management Server. Its purpose is to facilitate adding and removing users to and from the various proxy servers that a customer sets up. The Management Server is based on the Flask framework and so makes heavy use of Flask’s built in tools and utilities. A previous version was built on AppEngine, but is no longer supported (see [here](https://github.com/uProxy/ufo-management-server) for more info on that repository). The following sections provide best practice information for setting up, developing, testing, and maintaining the Management Server (as well as future components, such as the Deployment Server).

For a high level technical overview of UfO, see the [UfO Design Doc](https://docs.google.com/document/d/1M6gL67V2m5xk1pr42-CLh7jJteg74OpHof-14GgLa3U/edit).

### Setup

#### Prerequisites

- [Python 2.7](https://www.python.org/)
- [Pip](http://pip.readthedocs.org/en/stable/)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Node JS](https://nodejs.org/en/download/package-manager/)

#### Steps

To setup development of the Management Server locally, please perform the following steps:

1. Ensure you already have the prerequisites above installed and reachable via command line/terminal.
1. In a terminal, navigate to the directory where you would like to download UfO.
  * E.g., `cd ~/UfO`
1. Clone the UfO repository:
  * `git clone https://github.com/uProxy/ufo-management-server-flask.git` or
  * `git clone git@github.com:uProxy/ufo-management-server-flask.git` if you have your ssh access to GitHub set up (useful if you use 2-step auth for GitHub, which you should do).
1. Install virtualenv for running a virtual environment during development:
1. Setup a virtual environment:
  * `virtualenv venv`
  * `. venv/bin/activate`
1. Install the database library: `sudo apt-get install libpq-dev`
1. Install the necessary pip dependencies: `pip install -r requirements.txt`
1. Setup a local database: `python setup_database.py`
1. Install the necessary npm dependencies: `npm install`
1. Download the latest bower dependencies: `bower install`
1. Create the vulcanized html file: `./vulcanize.sh`

We hope to automate this in the future with some sort of setup script containing these steps.

#### Dependency Changes

In the event that our dependencies change, it is recommended to perform the following steps to refresh your local environment.

1. Pull down the latest source code:
  `git checkout your-branch-name-here`
  `git pull`
1. Update your dependencies:
  `pip install -r requirements.txt`
  `npm install`
  `bower install`
  `./vulcanize.sh`
1. Repeat steps 1-2 for every local branch including master.

### Implement

The [Landscape.io](https://landscape.io/github/uProxy/ufo-management-server-flask) health check service is configured to run automatically to test our code for style violations and other potentially unhealthy code habits. It has not been run lately due to backend issues with the service (see the [issue tracker](https://github.com/landscapeio/landscape-issues/issues) for that project for more info). In the future we may consider running our own checks as part of [Travis CI](https://travis-ci.org/) or some other service.

#### Source Control

We use git for our source control management. All changes should meet the following requirements:
1. Limited in scope and yet self-contained, as it attempts to address only one feature, issue, bug, or problem at a time.
1. In the form of a pull request from a development branch to master including all necessary commits.
1. Based off of the most recent version of master.
1. Contains all necessary unit and function tests (more on those below).
1. If addressing some planned feature, issue, bug, etc. then it should have a tracking entry.

All pull requests should be approved (given a “thumbs up” or “lgtm”) by at least one other member of the team as well as pass all unit tests on [Travis CI](https://travis-ci.org/). If the pull request is substantially large, more reviewers may be necessary. Nothing is to be committed directly to master (must be in a separate branch and merged into master), and no one is permitted to merge into master without passing review and passing Travis CI. Additionally, no one is permitted to merge directly into production without passing review and passing Travis CI. For more information on the production branch, see the Release section below.

### Test

#### Unit Testing

Any substantially complex piece of code should be unit tested rigorously to uncover any flaws in logic or syntax before submitting a pull request. Unit tests should utilize the format already established to inherit from base_test.py (which itself inherits from flask.ext.testing.TestCase to provide extra testing tools) where possible. Each test file should be named just as the file it exercises with _test appended, such as user_test.py would exercise the behaviors of user.py. Each test file should only exercise the behaviors present in one file of the application in order to be limited in scope.

In writing our current unit tests, we have made every effort to limit the use of mocks when real data and function calls can be used. If a piece of code cannot be sufficiently exercised in tests without excessive use of mocks, then it is a likely sign that the piece of code needs to be refactored.

To run the unit tests locally, execute the following command:
`python -m unittest discover -p "*_test.py"`

[Travis CI](https://travis-ci.org/) is configured to execute our unit tests on every commit, push, and pull request.

#### Functional Testing

Our functional tests are primarily intended to automate the Quality Assurance (QA) process by checking that page loading and navigation works as intended, data entered into forms is processed, and calls to the live database proceed. We built them utilizing the Selenium/WebDriver framework. These tests should run against a live server (deployed either locally or in the cloud) and go through the same flows a typical user would. Please see the existing tests in the tests/ui/ directory for an example.

There is a web_driver.sh file included in source control that will install and setup WebDriver testing in your local environment. To use this, simply execute the following command:

`./web_driver.sh install`

Similarly, this file can be used to execute the WebDriver tests as well. To do so, simply execute the following command:

`./web_driver.sh test server_url_goes_here login_username_goes_here login_password_goes_here`

Here’s an example with realistic values substituted:

`./web_driver.sh test http://0.0.0.0:5000 ethanAdmin test1111`

You can also run the WebDriver tests directly with the following commands:

`cd tests/ui/`

`python ui_test_suite.py --server_url=”server_url_goes_here” --username=”login_username_goes_here” --password=”login_password_goes_here”`

## Release

TODO: Figure out and build a versioning system that might notify th eadmin in the management server that things might need updated.

There are two main channels for releasing the management server: nightly and production. The nightly channel will release automatically on every push to the master branch in github as long as the unit tests pass. The production channel can only be released manually from the production branch. For the remainder of this document, the assumed channel of release is production since it is the only one that requires any interaction.

Heroku Links:

[Nightly](https://dashboard.heroku.com/apps/ufo-nightly/resources)

[Production](https://dashboard.heroku.com/apps/ufo-prod/resources)

### Requirements for Release

To release a new version of the management server, it must meet several requirements, listed below.

1. All unit tests must pass. These should be executed against the code level which is about to released with no additional code patched. See Unit Testing for how to execute them.
1. All functional tests must pass. These should be executed against a test instance which is deployed with the code level which is about to release with no additional code patched. See Functional Testing for how to execute them.
1. All database schema changes must come with a migration to update the most recently released schema (prior to the new release) to the new schema. See Schema Migration for how to create a migration tool.
1. Each release must be accompanied by a matching release note which details the changes from the most recent release (prior to the new release). See Release Note for how to create and distribute the release note.
1. TODO(eholder): Versioning step should go here.

### Create a Release

The process for creating a release is to create a Pull Request (PR) from the master branch (or other intended branch if performing a cherry pick) to the production branch. This release PR must pass all the normal PR requirements (reviewed and approved) as well as those listed above. Once this is complete and the review note has been sent out, the release PR can be merged into the production branch. From this point, the new release can be pushed to the production instance [here](https://ufo-prod.herokuapp.com/). See Update an Instance under Deployment for how to do that.

### Schema Migration

See the [UfO Notes for Migrations](https://docs.google.com/document/d/1r2sFTTS1-9crtkl3dAYc4sSEQ9hlKMxS2z1v5UHDCpk/edit#heading=h.3smlf2qe82pa) document on how to do this.

### Release Note

Each release must be accompanied by a matching release note which details the changes from the most recent release (prior to the new release). A release note serves to inform fellow developers and interested users what functionality is present in a given release and any other pertinent information that may have changed.

#### Requirements for a Release Note

1. Must be sent to all of the following addresses:
  * uProxy Team Address:
  * Management Server Team Address:
  * UfO Subscribed Customer Address:
  * TODO(eholder): Create these email address handlers and potentially combine them for simplicity.
1. Must include at least the following information:
  * New version number in production.
  * A list of PR’s included in the build with link references.
  * A list of issues the PR’s address.
  * A brief overall summary.
  * Any failing steps/tests from the Requirements for Release (if there were any). If there were any introduced, you must include an explanation of why the step/test is failing and why this release went through without passing. This is HIGHLY DISCOURAGED and should not be utilized without prior approval from the team.

#### Example Release Note

Hey All,

I just pushed a new release out to production for UfO. This updates the version to 1.0.0.2. Here are the PR's included since the last build:

PR’s:

https://github.com/uProxy/ufo-management-server-flask/pull/86

This release was to address the lack of web driver tests by expanding them.

(Further bug explanation here if needed.)

Issues/Features Addressed:

https://github.com/uProxy/ufo-management-server-flask/issues/126

Thanks!

## Deployment

### Create an Instance

The Management Server can be deployed locally or to the cloud. We have setup a one-click to deploy instance on Heroku to facilitate easy updating. That is the preferred method for creating a new instance as it is what customers will use. There is also a means to do this via command line. Both approaches are described here.

#### Create an Instance via Click-to-Deploy

The click to deploy method creates a new app based on a template from github. Heroku will read the configurations already created there and generate a new app for you, with almost no interaction required. Simply follow these steps:

1. Visit the Click-to-Deploy [link](https://dashboard.heroku.com/new?template=https://github.com/uProxy/ufo-management-server-flask/tree/production).
  * TODO(eholder): Create the button on the website.
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
