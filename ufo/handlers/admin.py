"""Admin module which provides handlers to access and edit admins."""

import json

import flask

import ufo
from ufo.database import models
from ufo.handlers import auth
from ufo.services import custom_exceptions



@ufo.app.route('/admin/')
@ufo.setup_required
@auth.login_required
def admin_list():
  """Retrieves a list of the admins currently in the db.

  Returns:
    A json object with 'items' set to the list of admins in the db.
  """
  items_dict = {'items': models.AdminUser.get_items_as_list_of_dict()}
  return flask.Response(json.dumps((items_dict)), mimetype='application/json')

@ufo.app.route('/admin/add', methods=['POST'])
@ufo.setup_required
@auth.login_required
def add_admin():
  """Stores new admin in the database on post.

  Returns:
    A redirect to the admin_list handler after inserting the specified admin.
  """
  admin_username = flask.request.form.get('admin_username', None)
  admin_password = flask.request.form.get('admin_password', None)

  if admin_username is not None or admin_password is not None:
    admin_user = models.AdminUser(username=json.loads(admin_username))
    admin_user.set_password(json.loads(admin_password))
    try:
      admin_user.save()
    except custom_exceptions.UnableToSaveToDB as e:
      flask.abort(e.code, e.message)

  return flask.redirect(flask.url_for('admin_list'))

@ufo.app.route('/admin/delete', methods=['POST'])
@ufo.setup_required
@auth.login_required
def delete_admin():
  """Deletes the admin corresponding to the passed in id from the db.

  If we had access to a delete method then we would not use get here.
  If the user is not found, this produces a 404 error which redirects to the
  error handler.

  Returns:
    A redirect to the admin_list page after deleting the given admin.
  """
  admin_id = json.loads(flask.request.form.get('admin_id'))
  admin_user = models.AdminUser.query.get_or_404(admin_id)
  admin_user.delete()

  return flask.redirect(flask.url_for('admin_list'))
