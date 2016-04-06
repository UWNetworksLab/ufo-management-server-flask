import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

import ufo

MIGRATE = Migrate(ufo.app, ufo.db)
MANAGER = Manager(ufo.app)

MANAGER.add_command('db', MigrateCommand)


if __name__ == '__main__':
    MANAGER.run()
