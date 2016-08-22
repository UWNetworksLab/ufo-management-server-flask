# ufo-management-server

Management Server component of uProxy for Orgs (UfO)


## Development

Development of UfO centers around one core git repository for the Management Server. Its purpose is to facilitate adding and removing users to and from the various proxy servers that a customer sets up. The Management Server is based on the Flask framework and so makes heavy use of Flask’s built in tools and utilities. A previous version was built on AppEngine, but is no longer supported (see [here](https://github.com/uProxy/ufo-management-server) for more info on that repository). The following sections provide best practice information for setting up, developing, testing, and maintaining the Management Server (as well as future components, such as the Deployment Server).

For a high level technical overview of UfO, see the [UfO Design Doc](https://docs.google.com/document/d/1M6gL67V2m5xk1pr42-CLh7jJteg74OpHof-14GgLa3U/edit).

### Tools

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
  * `git checkout your-branch-name-here`
  * `git pull`
1. Update your dependencies:
  * `pip install -r requirements.txt`
  * `npm install`
  * `bower install`
  * `./vulcanize.sh`
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

TODO: Figure out and build a versioning system that might notify the admin in the management server that things might need updated.

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

The process for creating a release is to create a Pull Request (PR) from the master branch (or other intended branch if performing a cherry pick) to the production branch. This release PR must pass all the normal PR requirements (reviewed and approved) as well as those listed above. Once this is complete and the review note has been sent out, the release PR can be merged into the production branch. From this point, the new release can be pushed to the production instance [here](https://ufo-prod.herokuapp.com/). See Update an Instance on the [Deployment Guide](DeploymentGuide.md) for how to do that.

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

### Automating a Pull Request to Production

One of the goals of our release process is to have an automated nightly build and test that will push to production on success. In order to do that, we set up a [Sauce Labs account](https://saucelabs.com/beta/tunnels) (based on the github project to allow free automated tests) and configured it to perform functional tests for us through Travis CI on pull requests to the production branch. Travis CI handles this by triggering our web_driver.sh script on each test which then determines what branch the test is being executed against ($TRAVIS_BRANCH environment variable). If the branch is production or if the override ($TRAVIS_WEB_DRIVER_OVERRIDE environment variable) is set to true, then the webdriver tests will proceed. Since these tests take a while, we don’t want to run them on every single PR, so this is a means to keep our typical tests as quick as possible.

Now that those tests are in place, the last piece is actually triggering them automatically via a pull request to the production branch from the master branch. We’ve implemented this as a cron job. The configuration of the job can be seen below:

`00 02 * * * curl -X POST -k -d '{"title": "Automated Nightly Release to Production", "head": "master", "base": "production"}' https://api.github.com/repos/uProxy/ufo-management-server-flask/pulls?access_token=YOUR_GITHUB_ACCESS_TOKEN_GOES_HERE`

The `00 02 * * *` part is the syntax for cron which denotes that the job will run at 2am every day. The actual request trigger is afterwards, via a curl command that specifies the title of the PR (`Automated Nightly Release to Production`), the head branch to pull from (`master`), the base branch to pull onto (`production`), the repo to perform this within (`https://api.github.com/repos/uProxy/ufo-management-server-flask`), and finally an access token (`YOUR_GITHUB_ACCESS_TOKEN_GOES_HERE`) that authenticates the request. Users on github.com can generate these access tokens by going [here](https://github.com/settings/tokens). Since they authenticate a user for various access scopes, they should be treated as secret, which is why ours is omitted here.

This is already configured to run on a test machine. No developer should need to do this, but it is documented here for informational purposes and in case of errors for debugging.

Once the pull request has been created and the tests have executed, all that remains is a final approval on the PR and the actual merge. Travis CI will maintain the results of the tests in case there is a failure, in which case a developer should reject the PR, and create a fix for whatever is broken. If all tests pass and there are no further concerns, a thumbs up can be given and the merge performed.

## Assorted Notes

### Retry for i18n After 1 Second

In the Polymer UI code, we currently use quaintous-i18n along with a messages.json file to produce internationalized text strings. The quaintous-i18n element works by loading your messages.json file that you specify (according to the user's current language) and then sets up a behavior which other elements can then use. In the other elements, they add this behavior as part of their definition and are able to call I18N like so:

`I18N.__(messageKeyGoesHere)`

to get the i18n-ed message for the corresponding key. However, there is a race condition between when these elements call quaintous-i18n and when quaintous-i18n actually loads the messages.json file (via an AJAX request). If quaintous-i18n does not have the messages file yet, it simply returns the key given to it instead of a translated string. While this doesn't happen often and can be easily fixed most times by reloading the page, it's overall a poor user experience.

Thus, to mitigate this issue, we have created a retry around setting these messages. Essentially, everywhere that a message is set in the attached handler of an element (which gets fired when the element is rendered fully in the DOM), we set a timeout to fire 1 second later. In the timeout if the last message to be set was set to its key rather than an i18n-ed value, we retry setting all the messages in that element (assuming them all to have failed). Currently, the timeout is set to 1 second arbitrarily. If this comes to be an issue, we will adjust as necessary. There is no subsequent retry after the first, and thus no possibility of infinitely retrying if the message keeps failing (could be a programmer error or the message just may not have a translation yet).
