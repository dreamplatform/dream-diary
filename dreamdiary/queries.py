
import operator
from itertools import groupby
from django.core import serializers
from dreamdiary.settings import USE_MOCKUP_QUERIES
from dreamsso import userdb

class MockupClient(object):
  def users_in_group(self, group_id):
    users = []
    for i in range(2, 10):
        user = {
            "phone_number": "", 
            "theme_color": "ffffff", 
            "first_name": "first_name " + str(i), 
            "last_name": "last_name " + str(i), 
            "saml_permissions": [
                "1.1.dreamdiary.diary.user"
            ], 
            "roles": [
                {
                    "name": "user", 
                    "title": "user", 
                    "organisation": {
                        "id": 1, 
                        "name": "org", 
                        "title": "org"
                    }, 
                    "official": False, 
                    "id": 1, 
                    "permissions": [
                        {
                            "name": "dreamdiary.diary.user"
                        }
                    ]
                }
            ], 
            "locale": "fi-fi", 
            "picture_url": "", 
            "organisations": [
                {
                    "id": 1, 
                    "name": "org", 
                    "title": "org"
                }
            ], 
            "legacy_roles": [
                "org.user"
            ], 
            "username": "mockuser" + str(i),
            "legacy_organisations": [
                "org"
            ], 
            "groups": [
                {
                    "id": group_id, 
                    "organisation": {
                        "id": 1, 
                        "name": "org", 
                        "title": "org"
                    }, 
                    "official": False, 
                    "name": "group 1", 
                    "title": "group 1"
                }
            ], 
            "id": i,
            "saml_organisations": [
                "1"
            ], 
            "saml_roles": [
                "1.1"
            ], 
            "email": ""
        }
        users.append(user)
    return users

  def users_groups_by_permission(self, user, permission_name):
    groups = []
    for i in range(1, 100):
        group = {
            "id": i,
            "organisation": {
                "id": 1,
                "name": "org", 
                "title": "org"
            }, 
            "official": False, 
            "name": "group " + str(i), 
            "title": "group " + str(i)
        }
        groups.append(group)
    return groups


  def distinct_users_in_groups(self, usergroups):
    users = []
    for usergroup in usergroups:
      users_in_group = self.users_in_group(usergroup.id)
      users += users_in_group

    users.sort(key=operator.itemgetter('id'))
    grouped_list = groupby(users, operator.itemgetter('id'))
    distinct_users = [g[1].next() for g in grouped_list]
    return distinct_users


class UserDbClient(userdb.Client):
  def users_in_group(self, group_id):
    """Return all users in specified group_id
    """
    users = []
    users = self._get(('user', 'group', str(group_id)))
    for user in users:
      if 'dreamdiary.diary.user' in user['saml_permissions']:
        users.append(user)
    return users

  def users_groups_by_permission(self, user, permission_name):
    """Gets all organisations where user is in role which has permission
    'permission_name', and returns all unofficial groups in these organisations
    """
    groups = []
    orgs = []
    for role in user.roles:
      for p in role['permissions']:
        if permission_name in p['name']:
          orgs.append(role['organisation']['id'])
    for org in orgs:
       ogs = self._get(('group', 'organisation', str(org)))
       for og in ogs:
         if og['official'] == False:
           groups.append(og)
    return groups

  def distinct_users_in_groups(self, usergroups):
    """Takes set of UserGroup objects and and return
    distinct users in them
    """
    users = []
    for usergroup in usergroups:
      users_in_group = self.users_in_group(usergroup.id)
      users += users_in_group

    users.sort(key=operator.itemgetter('id'))
    grouped_list = groupby(users, operator.itemgetter('id'))
    distinct_users = [g[1].next() for g in grouped_list]
    return distinct_users


class LocalUserDbClient(object):
  def _qs_to_dict(self, qs):
    """Application code expects python datastructures campatible with dataformat
    in userdb api
    """
    l = serializers.serialize('python', qs)
    for d in l:
        fields = d.pop('fields')
        d.update(fields)
        d['id'] = d['pk']
    return l

  def users_in_group(self, group_id):
    users = dreamuserdb.models.User.objects.filter(user_groups__id=group_id).\
            filter(roles__permissions__name='dreamdiary.diary.user')
    users = self._qs_to_dict(users)
    return users

  def users_groups_by_permission(self, user, permission_name):
    org_ids = user.roles.filter(permissions__name=permission_name).values_list('organisation', flat=True)
    groups = dreamuserdb.models.Group.objects.filter(official=False, organisation__in=org_ids)
    groups = self._qs_to_dict(groups)
    return groups

  def distinct_users_in_groups(self, usergroups):
    users = dreamuserdb.models.User.objects.filter(user_groups__id__in=usergroups).\
            filter(roles__permissions__name='dreamdiary.diary.user').distinct()

    #from django.contrib.auth.models import User
    #ids = [u.pk for u in users]
    #l = list(users) + list(User.objects.filter(pk__in=ids))
    #users = self._qs_to_dict(l)
    #for a in users:
    #    if a['model'] == 'dreamuserdb.user':
    #        for b in users:
    #            if b['model'] == 'auth.user' and b['pk'] == a['pk']:
    #                a.update(b)
    #                users.remove(b)
    #users = self._qs_to_dict(users)
    return users


# Use queries.client to access functions in this module
client = None
if USE_MOCKUP_QUERIES:
  client = MockupClient()
else:
  # if userdb app is installed use direct access to database
  try:
    import dreamuserdb.models
    client = LocalUserDbClient()
  # userdb app not installed use http api
  except ImportError:
    client = UserDbClient()

