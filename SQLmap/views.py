from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.response import Response

from Core.views import crearContextBase
from SQLmap import models, forms

from SQLmap.models import sqlmap_requests, sqlmap_results


def task_exists(function=None):
    # test per saber si la tasca demanada existeix
    def _dec(view_func):

        def _view(request, *args, **kwargs):
            id = kwargs['id']
            if sqlmap_requests.objects.filter(id=id).exists():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/task_nonexistent/')

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


def user_can_view_task(function=None):
    # test per saber si el Usuari pertany a la unitat i si te permisos per veure-la i per tant entrar a la vista
    def _dec(view_func):

        def _view(request, *args, **kwargs):
            id = kwargs['id']
            if sqlmap_requests.objects.filter(id=id, user=request.user).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/task_unauthorized/')

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


@login_required(login_url="/login")
def sqlmap_howto(request):
    context = crearContextBase(request)
    context.update({'sqlmap_howto': "active"})
    return render(request, 'sqlmap_howto.html', context)


@login_required(login_url="/login")
@task_exists
@user_can_view_task
def sqlmap_task(request, id):
    context = crearContextBase(request)
    task = sqlmap_requests.objects.get(id=id)
    aux = task
    results = sqlmap_results.objects.get(id=task.id)
    context.update({'task': aux, 'results': results})
    return render(request, 'sqlmap_task.html', context)


@login_required(login_url="/login")
def sqlmap_delete(request, id):
    user = request.user
    task = sqlmap_requests.objects.get(id=id)
    if task.user == user or user.is_staff:
        if task.state == "Running":
            task.kill = True
            task.state = "Blocked"
            task.save()
            return HttpResponseRedirect('/SQLmap/task/' + id + '/')
        elif task.state != "Blocked":
            sqlmap_requests.objects.filter(id=id).delete()
            sqlmap_results.objects.filter(id=id).delete()
            return HttpResponseRedirect('/SQLmap/tasks/')
    return Response(status=401)


@login_required(login_url="/login")
def sqlmap_relaunch(request, id):
    task = sqlmap_requests.objects.get(id=id)
    res = sqlmap_results.objects.get(id=id)
    if task.state == "Finished":
        res.output = None
        res.report = None
        res.finish_date = None
        res.save()
        task.state = "On Hold"
        task.insert_date = datetime.now()
        task.save()
    return HttpResponseRedirect('/SQLmap/tasks/')


@login_required(login_url="/login")
def sqlmap_modify(request, id):
    context = crearContextBase(request)
    u = request.user
    task = sqlmap_requests.objects.get(id=id)
    context.update({"task": task, "notModify": False})
    if task.state != "Running" and task.state != "Blocked":
        if request.method == 'POST':
            form = forms.SQLmapForm(request.POST, user=u)
            if form.is_valid():
                # url
                target_url = form.cleaned_data['url']
                # direct connection
                target_dbms = form.cleaned_data['dbms']
                target_user = form.cleaned_data['user']
                target_password = form.cleaned_data['password']
                target_ip = form.cleaned_data['ip']
                target_port = form.cleaned_data['port']
                target_db_name = form.cleaned_data['db_name']
                # parameters
                c = form.cleaned_data['charset']
                v = form.cleaned_data['verbosity']
                l = form.cleaned_data['level']
                r = form.cleaned_data['risk']
                d = form.cleaned_data['depth']
                n = form.cleaned_data['name']
                m = form.cleaned_data['mail']
                mf = form.cleaned_data['mail_field']
                if 'save' in request.POST:
                    e = "Saved"
                elif 'cue' in request.POST:
                    e = "On Hold"

                if target_url == "":
                    t = "-d " + target_dbms + "://" + target_user + ":" + target_password + "@" + target_ip + ":" + \
                        str(target_port) + "/" + target_db_name
                else:
                    t = "-u " + target_url
                if task.state != "Running" and task.state != "Blocked":
                    task.name = n
                    task.target = t
                    task.level = l
                    task.verbosity = v
                    task.risk = r
                    task.depth = d
                    task.charset = c
                    task.user = u
                    task.state = e
                    task.modify_date = datetime.now()
                    if m:
                        task.mail = mf
                    else:
                        task.mail = None
                    task.save()
                else:
                    context.update({"notModify": True})
                    return render(request, 'sqlmap_new.html', context)
                return HttpResponseRedirect('/SQLmap/tasks/')
            else:
                print(form.errors)
        else:
            form = forms.SQLmapForm(user=u)
            form.fields["name"].initial = task.name
            if task.target[0:3] == "-u ":
                form.fields["url"].initial = task.target[3:]
            elif task.target[0:3] == "-d ":
                text = task.target[3:].partition("://")
                form.fields["dbms"].initial = text[0]
                text = text[2].partition(":")
                form.fields["user"].initial = text[0]
                text = text[2].partition("@")
                # La password no la aprofitem
                text = text[2].partition(":")
                form.fields["ip"].initial = text[0]
                text = text[2].partition(":")
                form.fields["port"].initial = text[0]
                form.fields["db_name"].initial = text[2]
            context.update({"initial": 1, "verbosity": task.verbosity, "level": task.level, "risk": task.risk,
                            "depth": task.depth})
            form.fields["charset"].initial = task.charset
            if task.mail:
                form.fields["mail_field"].initial = task.mail
                form.fields["mail"].initial = True
            context.update({"form": form})
            return render(request, 'sqlmap_new.html', context)
    else:
        context.update({"notModify": True})
        return render(request, 'sqlmap_new.html', context)


@login_required(login_url="/login")
def sqlmap_tasks(request):
    context = crearContextBase(request)
    return render(request, 'sqlmap_tasks.html', context)


@login_required(login_url="/login")
def sqlmap_download(request, id):
    task = sqlmap_requests.objects.get(id=id)
    if task.state == "Finished":
        result = sqlmap_results.objects.get(id=task.id)
        print(result.report)
        # Retornant fitxer
        nomArxiu = "Report_" + task.name.replace(" ","-") + "_" + datetime.strftime(result.finish_date, "%Y%m%d%H%M") + ".html"
        response = HttpResponse(result.report, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=' + nomArxiu
        return response
    else:
        context = crearContextBase(request)
        results = "fail"
        context.update({'task': task, 'results': results})
        return render(request, 'sqlmap_task.html', context)


@login_required(login_url="/login")
def sqlmap_new(request):
    context = crearContextBase(request)
    u = request.user
    userid = u.id
    if request.method == 'POST':
        form = forms.SQLmapForm(request.POST, user=u)
        if form.is_valid():
            # url
            target_url = form.cleaned_data['url']
            # direct connection
            target_dbms = form.cleaned_data['dbms']
            target_user = form.cleaned_data['user']
            target_password = form.cleaned_data['password']
            target_ip = form.cleaned_data['ip']
            target_port = form.cleaned_data['port']
            target_db_name = form.cleaned_data['db_name']
            # parameters
            c = form.cleaned_data['charset']
            v = form.cleaned_data['verbosity']
            l = form.cleaned_data['level']
            r = form.cleaned_data['risk']
            d = form.cleaned_data['depth']
            n = form.cleaned_data['name']
            m = form.cleaned_data['mail']
            mf = form.cleaned_data['mail_field']
            if 'save' in request.POST:
                e = "Saved"
            elif 'cue' in request.POST:
                e = "On Hold"

            if target_url == "":
                t = "-d " + target_dbms + "://" + target_user + ":" + target_password + "@" + target_ip + ":" + \
                    str(target_port) + "/" + target_db_name
            else:
                t = "-u " + target_url

            if m:
                p = models.sqlmap_requests.objects.create(name=n, target=t, level=l, verbosity=v, risk=r,
                                                          depth=d,
                                                          charset=c, user=request.user, state=e,
                                                          mail=mf)  # crear la request
            else:
                p = models.sqlmap_requests.objects.create(name=n, target=t, level=l, verbosity=v, risk=r,
                                                          depth=d,
                                                          charset=c, user=request.user,
                                                          state=e)  # crear la request
            r = models.sqlmap_results.objects.create(id=p.id)
            return HttpResponseRedirect('/SQLmap/tasks/')
        else:
            print(form.errors)
    else:
        form = forms.SQLmapForm(user=u)
    context.update({"initial": 0})
    context.update({"form": form})
    return render(request, 'sqlmap_new.html', context)
