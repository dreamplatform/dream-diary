
#coding=utf-8

import logging
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.utils import simplejson as json
from dreamdiary.fields import HtmlColorCodeField, OrderField

LOG = logging.getLogger(__name__)

class Archivable(models.Model):
    is_archived = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def can_be_deleted(self):
        raise NotImplementedError()

    def delete(self, *args, **kwargs):
        if self.can_be_deleted():
            return super(Archivable, self).delete(*args, **kwargs)
        else:
            raise Exception("This %s can not be deleted!" % self.__class__.__name__)

    def save(self, *args, **kwargs):
        if self.is_archived and hasattr(self, 'order'):
            self.order = None
        return super(Archivable, self).save(*args, **kwargs)


class Diary(models.Model):
    """This table exists only for compatibility with
    dream platform permission system.
    """
    class Meta:
        permissions = (
            (u'supervisor', u'supervisor'),
            (u'user', u'user'),
        )


class UserGroup(models.Model):
    """UserGroup always has the same ID tham corresponding group
    in Userdb. It's used to bind (send) gNetwork to groups, thus 
    allowing only members of groups to access that Networm. If user leaves
    group, he has no longer permission to see the Network
    """
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % self.title


class Network(Archivable):
    """Network groups tasks into single bundle. Many tasks
    can belong to many Networks
    """
    title = models.CharField(_(u'title'), max_length=255)
    description = models.TextField(_(u'description'), default='', blank=True)
    #user should be always supervisor
    user = models.ForeignKey(User, related_name='networks')
    created = models.DateTimeField(_(u'created'), auto_now_add=True)
    last_modified = models.DateTimeField(_(u'last modified'), blank=True, null=True, auto_now=True)
    deadline = models.DateTimeField(_(u'deadline'), blank=True, null=True)
    color = models.ForeignKey('Color', null=True, blank=True, default=None)
    #task hierarchy for visual editor in ui
    hierarchy = models.TextField(_(u'network data as JSON'), blank=True, null=True, default=None)
    #Network order compared to other Networks user has
    order = OrderField(_(u'order'), null=True, blank=True, instance_is_archivable=True)
    #This is used to check who has permission to see and send answers tothis Network
    usergroups = models.ManyToManyField(UserGroup, null=True, blank=True)

    class Meta:
        ordering = ['-order']
        unique_together = ('order', 'user')

    @property
    def hierarchy_data(self):
        data = None
        try:
            data = json.loads(self.hierarchy)
        except:
            LOG.exception('hierarchy data is not JSON')
        return data

    @property
    def hierarchy_connectors(self):
        """Return all connectors in hierarchy_data
        """
        connectors = []
        hierarchy_data = self.hierarchy_data
        if hierarchy_data:
            for d in hierarchy_data:
                if 'type' in d and d['type'].startswith('connector'):
                    connectors.append(d)
        return connectors

    @property
    def connections(self):
        """Returns the Connections of this network, that beeing essentially
        the attached tasks.
        """
        return Connection.objects.filter(network=self)

    def __unicode__(self):
        return u'%s' % self.title

    def user_percentage(self, user):
        """Calculates completed percentage for one user.
        """
        #TODO might be reasonable to cache this..
        connections = self.connections
        connections_count = connections.count()
        if connections_count == 0:
            return 0

        answer_count = 0
        for connection in connections:
            if connection.answers.filter(work__user=user, connection=connection):
                answer_count += 1
        if answer_count == 0:
            return 0

        percent = float(answer_count)/float(connections_count) * 100
        if percent > 100:
            percent = 100
        return int(percent)

    def save(self, *args, **kwargs):
        super(Network, self).save(*args, **kwargs)
        if not self.title:
            self.title = 'Network %d' % self.id
            self.save()

    def can_be_deleted(self):
        if self.usergroups.count() > 0:
            return False
        return True


class Task(Archivable):
    """Tasks are attached to Networks and composes the actual content of the
    Network. Users who have access to that Network also have permission to answer
    with Works to tasks it contains.
    """
    title = models.CharField(_(u'title'), max_length=255, default=_('Task'))
    description = models.TextField(_(u'description'), default='', blank=True)
    #user should be always supervisor
    user = models.ForeignKey(User, related_name='tasks')
    created = models.DateTimeField(_(u'created'), auto_now_add=True)
    last_modified = models.DateTimeField(_(u'last modified'), auto_now=True)
    color = models.ForeignKey('Color', null=True, blank=True, default=None)
    order = OrderField(_('order'), null=True, blank=True, instance_is_archivable=True)

    class Meta:
        ordering = ['-order']

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        if not self.title:
            self.title = 'Task %d' % self.id
            self.save()

    def can_be_deleted(self):
        network_ids = self.connection_set.all().values_list('network')
        networks = Network.objects.filter(id__in=network_ids)
        retval = True
        for network in networks:
            if network.can_be_deleted == False:
                retval = False
                break
        return retval


class Work(Archivable):
    """Work is used to compose and return an answer to Task.
    One Work can be returned to many tasks.
    """
    title = models.CharField(_(u'title'), max_length=255)
    description = models.TextField(_(u'description'), default='', blank=True)
    #user should be always user
    user = models.ForeignKey(User, related_name='works')
    created = models.DateTimeField(_(u'created'), auto_now_add=True)
    last_modified = models.DateTimeField(_(u'last modified'), auto_now=True)
    color = models.ForeignKey('Color', null=True, blank=True, default=None)
    order = OrderField(_(u'order'), null=True, blank=True, instance_is_archivable=True)

    class Meta:
        ordering = ['-order']
        unique_together = ('user', 'order')

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        super(Work, self).save(*args, **kwargs)
        if not self.title:
            self.title = 'Work %d' % self.id
            self.save()

    def can_be_deleted(self):
        if self.answer_set.count() > 0:
            return False
        return True


class TaskAttachment(models.Model):
    """Simple table to hold url resources attached to Tasks
    """
    url = models.URLField(_(u'url'), max_length=2048)
    task = models.ForeignKey(Task, related_name='attachments')


class WorkAttachment(models.Model):
    """Simple table to hold url resources attached to Work
    """
    url = models.URLField(_(u'url'), max_length=2048)
    work = models.ForeignKey(Work, related_name='attachments')


class Color(models.Model):
    """Color can be bind Network, Task and Work. This is to help
    user to group visually items which are somehow related.
    For example color red with title 'Math' can be attached to Network.
    Now if red is attached to some other Task/Network it too will have
    this 'Math' tag. When user changes the title of red, it changes to both objects.

    Loginc is that user has only one instance of each different color, but different Users
    can have different instances of that color.
    Color is therefore global in the context of user.
    """
    color = HtmlColorCodeField()
    title = models.CharField(max_length=200, blank=True, default='')
    user = models.ForeignKey(User, related_name='colors')

    class Meta:
        unique_together = ('color', 'user')

    def __unicode__(self):
        return u'%s (%s)' % (self.color, self.user)


class Connection(models.Model):
    """Intermediary table for attaching Tasks to Networks.
    Extra data is order, which is tasks order in scope of Network
    """
    network = models.ForeignKey(Network)
    task = models.ForeignKey(Task)
    #order of task in network
    order = OrderField(_(u'order'), null=True, blank=True)

    def __unicode__(self):
        return u'%s in %s' % (self.task.title, self.network.title)

    @property
    def answers(self):
        """Return submitted answers for this task.
        """
        return Answer.objects.filter(connection=self)

    class Meta:
        ordering = ['-order']
        unique_together = (
            ('network', 'task'),
            ('network', 'task', 'order'),
        )


class Answer(models.Model):
    """Intermediary table for attaching Works to task connected to network.
    Extra data comprises timestamps for submit/edit dates
    """
    connection = models.ForeignKey(Connection)
    work = models.ForeignKey(Work)
    submitted = models.DateTimeField(_(u'Date this answer was submitted'), auto_now_add=True)
    last_modified = models.DateTimeField(_(u'Date this answer was last modified'), auto_now=True)

    def __unicode__(self):
        return u'%s in %s' % (self.work.title, self.connection.task.title)

    class Meta:
        unique_together = ('connection', 'work')
