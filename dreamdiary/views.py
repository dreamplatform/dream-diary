
# -*- coding: utf-8 -*-

import logging
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponseForbidden, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson as json
from django.db import IntegrityError
from dreamdiary.decorators import supervisor_or_user_required, supervisor_required, user_required
from dreamdiary.models import Network, Task, Work, Connection, TaskAttachment, Color, UserGroup, Answer, WorkAttachment
from dreamdiary.queries import client

LOG = logging.getLogger(__name__)


###############################################################
#Common views
#Common entrypoints to site, delegates rendering to appropriate
#sub routines. This is to enable uniform urls between supervisor
#and user
###############################################################

@login_required
@supervisor_or_user_required
def index(request):
    if request.user.has_perm('dreamdiary.supervisor'):
        return _supervisor_index(request)
    elif request.user.has_perm('dreamdiary.user'):
        return _user_index(request)


@login_required
@supervisor_or_user_required
def network(request, network_id, user_id=None):
    if request.user.has_perm('dreamdiary.supervisor'):
        return _supervisor_network(request, network_id, user_id=user_id)
    elif request.user.has_perm('dreamdiary.user'):
        return _user_network(request, network_id)


@login_required
@supervisor_or_user_required
def archive(request):
    if request.user.has_perm('dreamdiary.supervisor'):
        return _supervisor_archive(request)
    elif request.user.has_perm('dreamdiary.user'):
        return _user_archive(request)


@login_required
@supervisor_or_user_required
def ajax_paginated_snippet(request):
    """Ajaxview that returns paginated snippets. supports also filtering.
    This is used to build up item lists in ui.

    GET parameters:
        t       : type. lowercase class name of desired objects
        c       : count. items per page. must be >= 3
        p       : page. requested page
        q       : optional search string, if provided dataset is filtered with it before pagination
        rt      : optional related itemtype, for example getting users requires network as parameter
        ri      : optional related item id
        a       : optional integer 0=show only not archived, 1=show archived, 2=show both
    """
    objtype = request.GET.get('t', None)
    count = int(request.GET.get('c', 15))
    page = int(request.GET.get('p', 1))
    search_string = request.GET.get('q', None)
    related_object_type = request.GET.get('rt', None)
    related_object_id = request.GET.get('ri', None)
    archived_flag = int(request.GET.get('a', 0))

    #general validations
    if not objtype:
        LOG.error('t parameter missing in GET data')
        return HttpResponseBadRequest(content='t parameter is required')
    if count < 3:
        LOG.error('c must be >= 3')
        return HttpResponseBadRequest(content='c must be >= 3')
    if page < 1:
        LOG.error('p must be >= 1')
        return HttpResponseBadRequest(content='p must be >= 1')
    if archived_flag not in (0, 1, 2):
        LOG.error(' must be 0, 1 or 2')
        return HttpResponseBadRequest(content='a must be 0, 1 or 2')

    try:
        data = _get_paginated_data(request, objtype, count, page, search_string=search_string,\
                related_object_type=related_object_type, related_object_id=related_object_id,\
                archived_flag=archived_flag)
    except (NotImplementedError, AttributeError) as e:
        return HttpResponseBadRequest(e)

    return render(request, data['template'], data)


def _get_paginated_data(request, objtype, count, page, search_string=None,\
        related_object_type=None, related_object_id=None, archived_flag=0):

    ALLOWED_TYPES = ('network', 'task', 'work', 'user', 'group')
    if not objtype in ALLOWED_TYPES:
        LOG.error('t with value of %s is not allowed' % objtype)
        raise AttributeError('t with value of %s is not allowed' % objtype)

    qs = None
    top_item = None
    bottom_item = None
    related_object = None
    is_user_supervisor = request.user.has_perm(u'dreamdiary.supervisor')
    is_user_user = request.user.has_perm(u'dreamdiary.user')
    template = ''

    #force item count in one page in reasonable limits
    if count > 20:
        count = 20

    #get objects and check permissions, choose correct template
    #this is where non-common handling is mostly done
    if objtype == 'network':
        if is_user_supervisor:
            qs = Network.objects.filter(user=request.user).distinct()
            if archived_flag == 0:
                qs = qs.filter(is_archived=False)
            elif archived_flag == 1:
                qs = qs.filter(is_archived=True)
            if archived_flag == 1:
                template = 'dreamdiary/supervisor/snippets/archive_network_list.html'
            else:
                template = 'dreamdiary/supervisor/snippets/network_list.html'
        elif is_user_user:
            users_groups = [g['id'] for g in request.user.usergroups]
            qs = Network.objects.filter(usergroups__pk__in=users_groups).order_by('-created').distinct()
            template = 'dreamdiary/user/snippets/network_list.html'
    elif objtype == 'task':
        if is_user_supervisor:
            qs = Task.objects.filter(user=request.user).distinct()
            if archived_flag == 0:
                qs = qs.filter(is_archived=False)
            elif archived_flag == 1:
                qs = qs.filter(is_archived=True)
            if archived_flag == 1:
                template = 'dreamdiary/supervisor/snippets/archive_task_list.html'
            else:
                template = 'dreamdiary/supervisor/snippets/task_list.html'
        elif is_user_user:
            #user has no ability to list tasks
            raise NotImplementedError('Requested functionality is not available')
    elif objtype == 'work':
        if is_user_supervisor:
            #supervisor has no ability to list works
            raise NotImplementedError('Requested functionality is not available')
        elif is_user_user:
            qs = Work.objects.filter(user=request.user).distinct()
            if archived_flag == 0:
                qs = qs.filter(is_archived=False)
            elif archived_flag == 1:
                qs = qs.filter(is_archived=True)
            if archived_flag == 1:
                template = 'dreamdiary/user/snippets/archive_work_list.html'
            else:
                template = 'dreamdiary/user/snippets/work_list.html'
    elif objtype == 'user':
        if is_user_supervisor:
            if not related_object_type or not related_object_id:
                raise AttributeError('Related object data is needed')
            if not related_object_type == 'network':
                raise AttributeError('Related object type must be "network"')
            network = Network.objects.get(pk=related_object_id)
            usergroups = network.usergroups.all()
            # NOTE: This breaks http api configuration!!!!
            #get users from userdb and save local db if not exists
            #users = client.distinct_users_in_groups(usergroups)
            #id_list = []
            #for user_data in users:
            #    user, created = User.objects.get_or_create(id=user_data['id'])
            #    user.username = user_data['username']
            #    user.first_name = user_data['first_name']
            #    user.last_name = user_data['last_name']
            #    user.save()
            #    id_list.append(user.id)
            #qs = User.objects.filter(id__in=id_list)
            qs = client.distinct_users_in_groups(usergroups)
            related_object = network
            template = 'dreamdiary/supervisor/snippets/user_list.html'
        elif is_user_user:
            raise NotImplementedError('Requested functionality is not available')
    elif objtype == 'group':
        if is_user_supervisor:
            #get all groups from those organisation where user has some role in which
            #diary supervisor permission is present... *sigh*..
            groups = client.users_groups_by_permission(request.user, 'dreamdiary.diary.supervisor')
            #store to db if not exist
            id_list = []
            for group_data in groups:
                usergroup, created = UserGroup.objects.get_or_create(id=group_data['id'])
                if usergroup.title != group_data['title']:
                    usergroup.title = group_data['title']
                    usergroup.save()
                id_list.append(usergroup.id)
            qs = UserGroup.objects.filter(id__in=id_list).distinct()
            template = 'dreamdiary/supervisor/snippets/group_list.html'
        else:
            raise NotImplementedError('Requested functionality is not available')

    #NOTE after this point qs must contain only objects which are visible to user

    #apply filtering if q is provided
    #this also contains some non-common handling
    if search_string:
        if objtype == 'user':
            qs = qs.filter(Q(first_name__contains=search_string)|Q(last_name__contains=search_string))
        elif objtype == 'group':
            qs = qs.filter(title__contains=search_string)
        else:
            qs = qs.filter(Q(title__contains=search_string)|Q(color__title__contains=search_string))
    paginator = Paginator(qs, count)

    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    #add top and bottom items if filtering is not enabled
    if search_string == None:
        if page.has_next():
            next_page = paginator.page(page.next_page_number())
            bottom_item = next_page[0]
        if page.has_previous():
            prev_page = paginator.page(page.previous_page_number())
            top_item = prev_page[len(prev_page)-1]

    data = {
        'items' : page,
        'template' : template,
        'top_item' : top_item,
        'bottom_item' : bottom_item,
        'qs' : qs,
    }
    if related_object:
        data[related_object_type] = related_object

    return data

@login_required
@supervisor_or_user_required
def ajax_color(request):
    """Ajax view for attaching color to object. Accepts only POST requests

    POST parameters (all required):
        i:      object id
        t:      object type
        title:  color title
        rgb:    color value, rgb hexstring
    """
    ALLOWED_TYPES = ('network', 'task', 'work')
    if request.method != 'POST':
        LOG.error('Request is not POST')
        return HttpResponseBadRequest()

    try:
        obj_id = request.POST['i']
        objtype = request.POST['t']
        title = request.POST['title']
        rgb = request.POST['rgb']
    except KeyError as e:
        LOG.exception(e)
        return HttpResponseBadRequest()

    if not objtype in ALLOWED_TYPES:
        LOG.error('invalid objtype %s' % objtype)
        return HttpResponseBadRequest()

    #get the object and check that the user has permission to modify it
    try:
        if objtype == 'network':
            obj = Network.objects.get(id=obj_id, user=request.user)
        elif objtype == 'task':
            obj = Task.objects.get(id=obj_id, user=request.user)
        elif objtype == 'work':
            obj = Work.objects.get(id=obj_id, user=request.user)
    except ObjectDoesNotExist:
        LOG.exception('%s object with id %d does not exist or does not belong to user %d' %\
                (objtype, obj_id, request.user.id))
        raise Http404

    #get or create the color and attach to object
    color, created = Color.objects.get_or_create(color=rgb, user=request.user)
    color.title = title
    color.save()
    obj.color = color
    obj.save()
    return HttpResponse()


@login_required
@supervisor_or_user_required
def ajax_order(request):
    """Ajaxview for ordering model instances. Accepts only POST request.
    View receives arbitrary lenght list of object ids. Indexes in list
    determines their orders relative to each other. Objects are ordered again
    using the SAME order values as they already have, meaning that order values
    are SWAPPED between objects. This should guarantee that orders don't conflict
    with user's (or some other user's) objects.

    POST parameters (all required):
        t:  object type
        l:  list of object id's
    """
    #NOTE: Connections also have order, however it is not used currently
    ALLOWED_TYPES = ('network', 'task', 'work')

    if not request.method == 'POST':
        LOG.error('Request method was not POST')
        return HttpResponseBadRequest()

    try:
        objtype = request.POST['t']
        objid_list = request.POST.getlist('l[]')
    except KeyError as e:
        LOG.exception(e)
        return HttpResponseBadRequest()

    if not objtype in ALLOWED_TYPES:
        LOG.error('invalid objtype %s' % objtype)
        return HttpResponseBadRequest()

    if objtype == 'network':
        objects = Network.objects.filter(id__in=objid_list).distinct()
    elif objtype == 'task':
        objects = Task.objects.filter(id__in=objid_list).distinct()
    elif objtype == 'work':
        objects = Work.objects.filter(id__in=objid_list).distinct()

    #check that user has permission for these objects
    objects = objects.filter(user=request.user)

    #check that all objects still has same number of items than list
    #POSTed in by ui. If not, some objects was not found or user has no permission
    #to them
    if not objects.count() == len(objid_list):
        LOG.error('Some objects specified in l paramater was not found or user has no permission to them')
        #either way, user needs to know only 404
        raise Http404

    objects_in_new_order = []
    i = 0
    for obj_id in objid_list:
        #objects are in ascending order
        order_obj = objects[i]
        item = {
            'obj' : objects.get(id=obj_id),
            'new_order' : order_obj.order,
        }
        objects_in_new_order.append(item)
        i += 1

    #nullify orderfield to avoid integrity errors when saving
    objects.update(order=None)

    #finally save the objects with swapped orders
    for item in objects_in_new_order:
        obj = item['obj']
        obj.order = item['new_order']
        obj.save()

    return HttpResponse()


#################
#supervisor views
#################

@login_required
@supervisor_required
def _supervisor_index(request):
    """
    Notes:
        Actual pagination is handled via ajax call
    """
    network_data = _get_paginated_data(request, 'network', 15, 1)
    task_data = _get_paginated_data(request, 'task', 15, 1)

    context = {
        'networks': network_data['items'],
        'tasks': task_data['items'],
        'network_bottom_item' : network_data['bottom_item'],
        'task_bottom_item' : task_data['bottom_item'],
    }
    return render(request, 'dreamdiary/supervisor/index.html', context)


@login_required
@supervisor_required
def _supervisor_network(request, network_id, user_id=None):
    """Allows supervisor to view network in the context of user.
    user is always selected and only his/her answers are shown in tasks
    Requests to this view goes trough commonview
    """
    #get network and check it belongs to requesting supervisor
    try:
        network = Network.objects.get(pk=network_id)
    except Network.DoesNotExist:
        LOG.exception('Requested network with id  %s does not exists' % network_id)
        raise Http404
    if not network.user == request.user:
        LOG.error('Requested network %d does not belong to user %d' %
                (network_id, request.user.id))
        return HttpResponseForbidden()

    data = _get_paginated_data(request,\
            'user', 15, 1, related_object_type='network', related_object_id=network.id)
    #get selected user
    #could do redirect here with user_id, but
    #_get_paginated_data to users is extremely expensive
    #so we don't want to do it twice (if execution ends up defaulting to
    #first user this would happen)
    selected_user = None
    if user_id:
        try:
            selected_user = data['qs'].get(pk=user_id)
        except User.DoesNotExist:
            LOG.exception('View network for user %s: user is not in any group shared to this network (%d)' %\
                    (user_id, network.id))
            raise Http404
    #if user id is not provided, default to first one in qs
    else:
        if data['qs'].count():
            selected_user = data['qs'][0]

    context = {
        'users' : data['items'],
        'network' : network,
        'selected_user' : selected_user,
    }
    return render(request, 'dreamdiary/supervisor/view_network.html', context)


@login_required
@supervisor_required
def supervisor_edit_network(request, network_id=None):
    """View for editing/creating network. If network_id is provided editing mode
    is active

    Expected POST data:
        networkTitle
        networkdata (required)
    """
    network = None
    if network_id:
        try:
            network = Network.objects.get(pk=network_id, user=request.user)
        except Network.DoesNotExist:
            LOG.exception('user with id %d requested network with id %d\
                    ,which is either missing or does not belong to user' \
                    % (request.user.id, network_id))
            #Could actually be permission issue due the user parameter filtering
            #but really no need to reveal this to user
            raise Http404
    task_data = _get_paginated_data(request, 'task', 15, 1)

    #POST specific handling
    if request.method == 'POST':
        if 'save' in request.POST:
            #check that required data is present
            if not 'networkdata' in request.POST:
                LOG.error('networkdata missing in POST data')
                return HttpResponseBadRequest()
            #check the validity of these parameters
            hierarchy_data = request.POST['networkdata']
            if not hierarchy_data:
                LOG.error('No networkdata provided in POST request')
                return HttpResponseBadRequest()
            try:
                hierarchy_data = json.loads(hierarchy_data)
            except:
                LOG.exception('Data was not json')
                return HttpResponseBadRequest()

            is_new_network_created = False
            #setup network instance
            title = request.POST.get('networkTitle', None)
            if network and title:
                network.title = title
            else:
                attrs = {'user' : request.user}
                if title:
                    attrs['title'] = title
                network = Network(**attrs)
                #set this flag so we can determine if redirect should be done
                #at the end
                is_new_network_created = True
            network.save()
            connected_tasks = []

            #iterate data to create tasks and connections specified in it
            for item in hierarchy_data:
                if item['type'] == 'item':
                    task_id = item['id']
                    try:
                        task = Task.objects.get(pk=task_id, user=request.user)
                    except Task.DoesNotExist:
                        LOG.exception('Network data contains task item which is not in db or does not belong to user')
                        raise Http404
                    #check that connection
                    #order is automatically set to max+1
                    connection, created = Connection.objects.get_or_create(network=network, task=task)
                    connected_tasks.append(task.id)
            #if we made it her, data is parsed tasks and connections are created
            #so save json data to network and tear down any connections that may been
            #removed its done
            network.hierarchy = json.dumps(hierarchy_data)
            network.save()
            existing_connections = network.connections
            #leave out any connection that has task which is included in POSTed networkdata
            #the remainin set is to be deleted as the task-network relation is terminated
            #the filtering with user is there just in case to make sure we are touching only connections
            #of user making this request
            purged_connections = existing_connections.exclude(task__id__in=connected_tasks).\
                    filter(task__user=request.user)
            purged_connections.delete()

            #if new network is created redirect user to the url wich points to
            #newly created network
            if is_new_network_created:
                return redirect('supervisor_edit_network', network.id)

        elif 'archive' in request.POST:
            network.is_archived = True
            network.save()

        elif 'unarchive' in request.POST:
            network.is_archived = False
            network.save()

        elif 'delete' in request.POST:
            network.delete()
            return redirect('diary_index')

    context = {
        'tasks' : task_data['items'],
        'task_bottom_item' : task_data['bottom_item'],
        'network' : network,
    }
    return render(request, 'dreamdiary/supervisor/edit_network.html', context)


@login_required
@supervisor_required
def supervisor_share_network(request, network_id):
    """View for sharing network to groups

    POST params:
        l[]:  list of group ids (required)
    """
    try:
        network = Network.objects.get(id=network_id, user=request.user)
    except network.DoesNotExist:
        LOG.exception('Network object with id %s does not exist or does not belong to requesting user' %\
                network_id)
        raise Http404

    groups_data =  _get_paginated_data(request, 'group', 15, 1)
    active_groups = network.usergroups

    #POST specific handling
    if request.method == 'POST':
        #check the group list params is present
        if'l[]' in request.POST:
            group_id_list = request.POST.getlist('l[]')
            #these are needed for checking validity of posted ids
            users_groups_by_permission = client.users_groups_by_permission(request.user,\
                    'dreamdiary.diary.supervisor')
            users_groups_by_permission = [str(g['id']) for g in users_groups_by_permission]

            #purge all existing relation between Network and UserGroup
            #as the posted list is always complete
            network.usergroups.clear()

            #iterate posted id list and create corresponding UserGroup objects
            for group_id in group_id_list:
                #check the id is in list of valid group ids
                if group_id in users_groups_by_permission:
                    try:
                        usergroup = UserGroup.objects.get(id=group_id)
                        network.usergroups.add(usergroup)
                        #network.save()
                    except UserGroup.DoesNotExist:
                        #NOTE: TODO
                        #UserGroup object should be in local db in default flow
                        #where groups are fetched trough _get_paginated_data
                        #theoreticaly it should not be required, and group should be
                        #fetched from userdb (and permission checks made), but we don't
                        #support this righ now
                        pass
                else:
                    #we skip this but continue excecution, though is means somebody has
                    #tampered the POST data manualy
                    LOG.warning('User %d tried to share network %d to group %s, which he has no permission' \
                            % (request.user.id, network.id, str(group_id)))

    context = {
        'groups' : groups_data['items'],
        'network' : network,
        'active_groups' : active_groups.all(),
    }

    return render(request, 'dreamdiary/supervisor/share_network.html', context)

@login_required
@supervisor_required
def supervisor_edit_task(request, task_id=None):
    """View for editing/creating task. If task_id is provided editing mode
    is active

    Expected POST data:
        taskTitle (required)
        taskDesc
        attachment[]
    """
    task = None
    if task_id:
        try:
            task = Task.objects.get(pk=task_id, user=request.user)
        except Task.DoesNotExist:
            LOG.exception('user with id %d requested task with id %d\
                    ,which is either missing or does not belong to user' \
                    % (request.user.id, task_id))
            #Could actually be permission issue due the user parameter filtering
            #but really no need to reveal this to user
            raise Http404
    task_data = _get_paginated_data(request, 'task', 15, 1)

    #POST specific handling
    if request.method == 'POST':
        if 'save' in request.POST:
            is_new_task_created = False
            #setup task instance
            title = request.POST.get('taskTitle', None)
            if task and title:
                task.title = title
            else:
                attrs = {'user' : request.user}
                if title:
                    attrs['title'] = title
                task = Task(**attrs)
                #set this flag so we can determine if redirect should be done
                #at the end
                is_new_task_created = True
            #posted attachment list is always the full lists
            #so we purge all existing attachments
            task.attachments.all().delete()
            task.description = request.POST.get('taskDesc', '')
            task.save()
            post_attachments = request.POST.getlist('attachment[]', [])
            #NOTE no format validation is done to urls posted, all string will pass
            for a in post_attachments:
                #TODO somekind of validation might be good idea
                #for example, if string "asd" is posted as url, it will show up
                #as <current_url>/asd to the user in ui
                #maybe just skipping invalid urls?
                attachment = TaskAttachment(task=task, url=a)
                attachment.save()

            if is_new_task_created:
                return redirect('supervisor_edit_task', task.id)

        elif 'archive' in request.POST:
            task.is_archived = True
            task.save()

        elif 'unarchive' in request.POST:
            task.is_archived = False
            task.save()

        elif 'delete' in request.POST:
            task.delete()
            return redirect('diary_index')


    context = {
        'tasks' : task_data['items'],
        'task_bottom_item' : task_data['bottom_item'],
        'task' : task,
    }
    return render(request, 'dreamdiary/supervisor/edit_task.html', context)


@login_required
@supervisor_required
def _supervisor_archive(request):
    network_page = 1
    task_page = 1

    if request.method == 'POST':
        if 'id' in request.POST and 'type' in request.POST:
            _id = request.POST['id']
            _type = request.POST['type']
            try:
                if _type == 'network':
                    obj = Network.objects.get(pk=_id, user=request.user)
                elif _type == 'task':
                    obj = Task.objects.get(pk=_id, user=request.user)
            except (Network.DoesNotExist, Task.DoesNotExist):
                LOG.exception('user with id %d requested object type %s with id %d\
                        ,which is either missing or does not belong to user' \
                        % (request.user.id, _type, _id))
                raise Http404
            if 'unarchive' in request.POST:
                obj.is_archived = False
                obj.save()
            elif 'delete' in request.POST:
                obj.delete()
            if 'p' in request.GET:
                if _type == 'network':
                    network_page = int(request.GET['p'])
                elif _type == 'task':
                    task_page = int(request.GET['p'])
        else:
            LOG.error('Method was POST, but required paramaters were missing')
            return HttpResponseBadRequest()

    network_data = _get_paginated_data(request, 'network', 15, network_page, archived_flag=1)
    task_data = _get_paginated_data(request, 'task', 15, task_page, archived_flag=1)

    context = {
        'networks': network_data['items'],
        'tasks': task_data['items'],
        'network_bottom_item' : network_data['bottom_item'],
        'network_top_item' : network_data['top_item'],
        'task_bottom_item' : task_data['bottom_item'],
        'task_top_item' : task_data['top_item'],
    }
    return render(request, 'dreamdiary/supervisor/archive.html', context)


###########
#user views
###########

@login_required
@user_required
def _user_index(request):
    """Index page view for user
    """
    work_data = _get_paginated_data(request, 'work', 15, 1)
    network_data = _get_paginated_data(request, 'network', 15, 1)

    context = {
        'works' : work_data['items'],
        'networks' : network_data['items'],
        'work_bottom_item' : work_data['bottom_item'],
        'network_bottom_item' : network_data['bottom_item'],
    }
    return render(request, 'dreamdiary/user/index.html', context)

@login_required
@user_required
def _user_network(request, network_id=None):
    """Allows user to view network and answers to tasks with works.
    Requests to this view goes trough commonview
    """
    try:
        network = Network.objects.get(id=network_id, usergroups__in=request.user.usergroups.all)
    except Network.DoesNotExist:
        LOG.exception('Network with id %s does not exist or it is not shared to any group requesting user is in'\
                % network_id)
        raise Http404

    work_data = _get_paginated_data(request, 'work', 15, 1)

    context = {
        'network' : network,
        'works' : work_data['items'],
        'work_bottom_item' : work_data['bottom_item'],
    }
    return render(request, 'dreamdiary/user/network.html', context)


@login_required
@user_required
def user_ajax_answer(request):
    """Submitting work to task (making Answer of it) is handled here.
    Accepts only POST requests.

    POST (ajax) params (all required):
        wi:     work id
        ti:     task id
        ni:     network id
        a:      action, (add or remove)
    """
    if request.method != 'POST':
        LOG.error('Request is not POST')
        return HttpResponseBadRequest()

    #get parameters, all are required
    try:
        work_id = request.POST['wi']
        task_id = request.POST['ti']
        network_id = request.POST['ni']
        action = request.POST['a']
    except KeyError as e:
        LOG.exception(e)
        return HttpResponseBadRequest()

    #check whether action is invalid
    if not action in ('add', 'remove'):
        LOG.excetion('Invalid action "%s"' % action)
        return HttpResponseBadRequest()

    #get objects and check permissions
    try:
        work = Work.objects.get(id=work_id, user=request.user)
    except Work.DoesNotExist:
        LOG.exception('Work with id %s does not exist' % str(work_id))
        raise Http404
    try:
        network = Network.objects.get(id=network_id, usergroups__in=request.user.usergroups.all)
    except Network.DoesNotExist:
        LOG.exception('Network with id %s does not exist or it is not shared to any group requesting user is in'\
                % network_id)
        raise Http404
    try:
        connection = Connection.objects.get(network=network, task=task_id)
    except Connection.DoesNotExist:
        LOG.exception('Connection between network %s and task %sdoes not exist'\
                % (str(network.id), str(task_id)))
        raise Http404

    if action == 'add':
        try:
            answer = Answer(connection=connection, work=work)
            answer.save()
        except IntegrityError as e:
            #integrity error is raised is there is answer with these connection and work instances
            #lets just log it and ignore otherwise as no violation has occured
            #UI should not make these posts
            LOG.exception(e)
    elif action == 'remove':
        try:
            answer = Answer.objects.get(connection=connection, work=work)
            answer.delete()
        except Answer.DoesNotExist:
            #lets just ignore this also, no harm done
            LOG.exception('Trying to remove answer which does not exist')

    return HttpResponse()


@login_required
@user_required
def user_edit_work(request, work_id=None):
    """Allows user to create and edit works. If work_id is not provided
    edit mode is active.

    Expected POST data:
        workTitle (required)
        workDesc
        attachment[]
    """
    work = None
    if work_id:
        try:
            work = Work.objects.get(pk=work_id, user=request.user)
        except Task.DoesNotExist:
            LOG.exception('user with id %d requested work with id %s\
                    ,which is either missing or does not belong to user' \
                    % (request.user.id, str(work_id)))
            #Could actually be permission issue due the user parameter filtering
            #but really no need to reveal this to user
            raise Http404
    work_data = _get_paginated_data(request, 'work', 15, 1)

    #POST specific handling
    if request.method == 'POST':
        if 'save' in request.POST:
            is_new_work_created = False
            #setup work instance
            title = request.POST.get('workTitle', None)
            if work and title:
                work.title = title
            else:
                attrs = {'user' : request.user}
                if title:
                    attrs['title'] = title
                work = Work(**attrs)
                #set this flag so we can determine if redirect should be done
                #at the end
                is_new_work_created = True
            #posted attachment list is always the full lists
            #so we purge all existing attachments
            work.attachments.all().delete()
            work.description = request.POST.get('workDesc', '')
            work.save()
            post_attachments = request.POST.getlist('attachment[]', [])
            #NOTE no format validation is done to urls posted, all string will pass
            for a in post_attachments:
                #TODO somekind of validation might be good idea
                #for example, if string "asd" is posted as url, it will show up
                #as <current_url>/asd to the user in ui
                #maybe just skipping invalid urls?
                attachment = WorkAttachment(work=work, url=a)
                attachment.save()

            if is_new_work_created:
                return redirect('user_edit_work', work.id)

        elif 'archive' in request.POST:
            work.is_archived = True
            work.save()

        elif 'unarchive' in request.POST:
            work.is_archived = False
            work.save()

        elif 'delete' in request.POST:
            work.delete()
            return redirect('diary_index')

    context = {
        'works' : work_data['items'],
        'work_bottom_item' : work_data['bottom_item'],
        'work' : work,
    }
    return render(request, 'dreamdiary/user/edit_work.html', context)


@login_required
@user_required
def _user_archive(request):
    page = 1
    if request.method == 'POST':
        if 'id' in request.POST and 'type' in request.POST:
            _id = request.POST['id']
            _type = request.POST['type']
            try:
                if _type == 'work':
                    obj = Work.objects.get(pk=_id, user=request.user)
            except Work.DoesNotExist:
                LOG.exception('user with id %d requested object type %s with id %d\
                        ,which is either missing or does not belong to user' \
                        % (request.user.id, _type, _id))
                raise Http404
            if 'unarchive' in request.POST:
                obj.is_archived = False
                obj.save()
            elif 'delete' in request.POST:
                obj.delete()
            if 'p' in request.GET:
                page = int(request.GET['p'])
        else:
            LOG.error('Method was POST, but required paramaters were missing')
            return HttpResponseBadRequest()

    work_data = _get_paginated_data(request, 'work', 15, page, archived_flag=1)

    context = {
        'work_top_item': work_data['top_item'],
        'works' : work_data['items'],
        'work_bottom_item' : work_data['bottom_item'],
    }
    return render(request, 'dreamdiary/user/archive.html', context)


