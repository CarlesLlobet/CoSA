from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from operator import itemgetter

from OpenVAS.models import openvas_requests
from OpenVAS.models import openvas_results

@login_required(login_url="/login")
def index(request):
    context = crearContextBase(request)
    context.update({'finished': "no"})
    context.update({'index': "active"})
    return render(request, 'index.html', context)

@login_required(login_url="/login")
def task_nonexistent(request):
    context = crearContextBase(request)
    return render(request, 'task_nonexistent.html', context)

@login_required(login_url="/login")
def task_unauthorized(request):
    context = crearContextBase(request)
    return render(request, 'task_unauthorized.html', context)

@login_required(login_url="/login")
def finished(request):
    context = crearContextBase(request)
    context.update({'finished': "si"})
    return render(request, 'index.html', context)


@login_required(login_url="/login")
def crearContextBase(request):
    notificacions = []
    user = request.user
    # notificacions
    for t in openvas_results.objects.all().order_by("finish_date"):
        aux = t.id
        request = openvas_requests.objects.get(id=aux)
        if request.state == "Finished" and (request.user.id == user.id or user.is_superuser):
            notificacio = {}
            notificacio['tool'] = 'OpenVAS'
            notificacio['id'] = t.id
            notificacio['output'] = t.output
            notificacio['finish_date'] = t.finish_date
            notificacio['name'] = request.name
            notificacions.append(notificacio)
    '''for t in sqlmap_results.objects.all().order_by("finish_date"):
        aux = t.id
        request = sqlmap_requests.objects.get(id=aux)
        if request.state == "Finished" and (request.user.id == user.id or user.is_superuser):
            notificacio = {}
            notificacio['tool'] = 'SQLmap'
            notificacio['id'] = t.id
            notificacio['output'] = t.output
            notificacio['finish_date'] = t.finish_date
            notificacio['name'] = request.name
            notificacions.append(notificacio)
    '''
    '''
    for t in w3af_results.objects.all().order_by("finish_date"):
        aux = t.id
        request = w3af_requests.objects.get(id=aux)
        if request.state == "Finished" and (request.user.id == user.id or user.is_superuser):
            notificacio = {}
            notificacio['tool'] = 'w3af'
            notificacio['id'] = t.id
            notificacio['output'] = t.output
            notificacio['finish_date'] = t.finish_date
            notificacio['name'] = request.name
            notificacions.append(notificacio)
    '''
    notificacions_sorted = sorted(notificacions, key=itemgetter('finish_date'), reverse=True)

    # tasques
    tasks = []
    if user.is_superuser:
        openvas_tasks = openvas_requests.objects.all()
        #sqlmap_tasks = sqlmap_requests.objects.all()
        #w3af_tasks = w3af_requests.objects.all()
    else:
        openvas_tasks = openvas_requests.objects.all().filter(user_id=user.id)
        #sqlmap_tasks = sqlmap_requests.objects.all().filter(user_id=user.id)
        #w3af_tasks = w3af_requests.objects.all().filter(user_id=user.id)
    for t in openvas_tasks:
        aux = {}
        aux['tool'] = 'OpenVAS'
        aux['username'] = t.user.username
        aux['id'] = t.id
        aux['name'] = t.name
        aux['state'] = t.state
        aux['target'] = t.target
        aux['insert_date'] = t.insert_date
        aux['percentage'] = t.percentage
        aux['pos'] = 0
        aux['mail'] = t.mail
        aux['config'] = t.config
        tasks.append(aux)
    '''for t in sqlmap_tasks:
        aux = {}
        aux['tool'] = 'SQLmap'
        aux['username'] = t.user.username
        aux['id'] = t.id
        aux['name'] = t.name
        aux['state'] = t.state
        aux['target'] = t.target
        aux['insert_date'] = t.insert_date
        aux['verbosity'] = t.verbosity
        aux['level'] = t.level
        aux['risk'] = t.risk
        aux['depth'] = t.depth
        aux['charset'] = t.charset
        aux['pos'] = 0
        aux['mail'] = t.mail
        tasks.append(aux)
    '''
    '''
    for t in w3af_tasks:
        aux = {}
        aux['tool'] = 'w3af'
        aux['username'] = t.user.username
        aux['id'] = t.id
        aux['name'] = t.name
        aux['state'] = t.state
        aux['target'] = t.target
        aux['target_os'] = t.target_os
        aux['target_framework'] = t.target_framework
        aux['profile'] = t.profile
        aux['login_url'] = t.login_url
        aux['login_username'] = t.login_username
        aux['login_password'] = t.login_password
        aux['login_usernamefield'] = t.login_userfield
        aux['login_passwordfield'] = t.login_passwordfield
        aux['login_method'] = t.login_method
        aux['insert_date'] = t.insert_date
        aux['pos'] = 0
        aux['mail'] = t.mail
        tasks.append(aux)
    '''
    for i in tasks:
        if i['state'] == "On Hold":
            if i['tool'] == 'OpenVAS':
                i['pos'] = len(openvas_requests.objects.filter(state="On Hold", insert_date__lte=i['insert_date']))
            '''
            elif i['tool'] == 'SQLmap':
                i['pos'] = len(sqlmap_requests.objects.filter(state="On Hold", insert_date__lte=i['insert_date']))
            elif i['tool'] == 'w3af':
                i['pos'] = len(w3af_requests.objects.filter(state="On Hold", insert_date__lte=i['insert_date']))
            '''
    tasks_sorted = sorted(tasks, key=itemgetter('insert_date'), reverse=True)
    return {'notificacions': notificacions_sorted, 'user': user, 'tasks': tasks_sorted}