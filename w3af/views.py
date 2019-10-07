from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.response import Response

from Core.views import crearContextBase

from w3af import models, forms
from w3af.models import w3af_requests, w3af_results


def task_exists(function=None):
    # test per saber si la tasca demanada existeix
    def _dec(view_func):

        def _view(request, *args, **kwargs):
            id = kwargs['id']
            if w3af_requests.objects.filter(id=id).exists():
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
            if w3af_requests.objects.filter(id=id, user=request.user).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/task_unauthorized/')

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


@login_required(login_url="/login")
def w3af_howto(request):
    context = crearContextBase(request)
    return render(request, 'w3af_howto.html', context)


@login_required(login_url="/login")
@task_exists
@user_can_view_task
def w3af_task(request, id):
    context = crearContextBase(request)
    task = w3af_requests.objects.get(id=id)
    aux = task
    results = w3af_results.objects.get(id=task.id)
    context.update({'task': aux, 'results': results})
    return render(request, 'w3af_task.html', context)


@login_required(login_url="/login")
def w3af_delete(request, id):
    user = request.user
    task = w3af_requests.objects.get(id=id)
    if task.user == user or user.is_staff:
        if task.state == "Running":
            task.kill = True
            task.state = "Blocked"
            task.save()
            return HttpResponseRedirect('/w3af/task/' + id + '/')
        elif task.state != "Blocked":
            w3af_requests.objects.filter(id=id).delete()
            w3af_results.objects.filter(id=id).delete()
            return HttpResponseRedirect('/w3af/tasks/')
    return Response(status=401)


@login_required(login_url="/login")
def w3af_relaunch(request, id):
    task = w3af_requests.objects.get(id=id)
    res = w3af_results.objects.get(id=id)
    if task.state == "Finished":
        res.output = None
        res.finish_date = None
        res.save()
        task.state = "On Hold"
        task.insert_date = datetime.now()
        task.save()
    return HttpResponseRedirect('/w3af/tasks/')


@login_required(login_url="/login")
def w3af_modify(request, id):
    context = crearContextBase(request)
    u = request.user
    task = w3af_requests.objects.get(id=id)
    context.update({"task": task, "notModify": False})
    if task.state != "Running" and task.state != "Blocked":
        if request.method == 'POST':
            form = forms.w3afForm(request.POST, user=u)
            if form.is_valid():
                n = form.cleaned_data['name']
                # target
                t = form.cleaned_data['target']
                to = form.cleaned_data['target_os']
                tf = form.cleaned_data['target_framework']
                # auth
                lu = form.cleaned_data['login_url']
                lun = form.cleaned_data['login_username']
                lp = form.cleaned_data['login_password']
                luf = form.cleaned_data['login_userfield']
                lpf = form.cleaned_data['login_passwordfield']
                lm = form.cleaned_data['login_method']
                # basic auth
                hd = form.cleaned_data['http_domain']
                hu = form.cleaned_data['http_user']
                hp = form.cleaned_data['http_password']
                # parameters
                p = form.cleaned_data['profile']
                m = form.cleaned_data['mail']
                mf = form.cleaned_data['mail_field']
                if 'save' in request.POST:
                    e = "Saved"
                elif 'cue' in request.POST:
                    e = "On Hold"

                if p == "Fast Scan":
                    pb = "fast_scan"
                elif p == "Full Audit":
                    pb = "full_scan"
                elif p == "OWASP Scan":
                    pb = "OWASP_TOP10"

                if task.state != "Running" and task.state != "Blocked":
                    task.name = n
                    task.target = t
                    task.target_os = to
                    task.target_framework = tf
                    task.login_url = lu
                    task.login_username = lun
                    task.login_password = lp
                    task.login_userfield = luf
                    task.login_passwordfield = lpf
                    task.login_method = lm
                    task.profile = pb
                    task.user = u
                    task.state = e
                    task.http_domain = hd
                    task.http_user = hu
                    task.http_password = hp
                    task.modify_date = datetime.now()
                    if m:
                        task.mail = mf
                    else:
                        task.mail = None
                    task.save()
                else:
                    context.update({"notModify": True})
                    return render(request, 'w3af_new.html', context)
                return HttpResponseRedirect('/w3af/tasks/')
            else:
                print(form.errors)
        else:
            form = forms.w3afForm(user=u)
            form.fields["name"].initial = task.name
            form.fields["target"].initial = task.target
            form.fields["target_os"].initial = task.target_os
            form.fields["target_framework"].initial = task.target_framework
            form.fields["target_login_url"].initial = task.login_url
            form.fields["login_username"].initial = task.login_username
            form.fields["login_password"].initial = task.login_password
            form.fields["login_userfield"].initial = task.login_userfield
            form.fields["login_passwordfield"].initial = task.login_passwordfield
            form.fields["login_method"].initial = task.login_method
            form.fields["profile"].initial = task.profile
            form.fields["http_domain"].initial = task.http_domain
            form.fields["http_user"].initial = task.http_user
            form.fields["http_password"].initial = task.http_password
            context.update({"initial": 1})
            if task.mail:
                form.fields["mail_field"].initial = task.mail
                form.fields["mail"].initial = True
            context.update({"form": form})
            return render(request, 'w3af_new.html', context)
    else:
        context.update({"notModify": True})
        return render(request, 'w3af_new.html', context)


@login_required(login_url="/login")
def w3af_tasks(request):
    context = crearContextBase(request)
    return render(request, 'w3af_tasks.html', context)


@login_required(login_url="/login")
def w3af_download(request, id):
    task = w3af_requests.objects.get(id=id)
    if task.state == "Finished":
        result = w3af_results.objects.get(id=task.id)
        #print(result.report)
        # Retornant fitxer
        nomArxiu = "Report_" + task.name + "_" + datetime.strftime(result.finish_date, "%Y%m%d%H%M") + ".html"
        response = HttpResponse(result.report, content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename=' + nomArxiu
        return response
    else:
        context = crearContextBase(request)
        results = "fail"
        context.update({'task': task, 'results': results})
        return render(request, 'w3af_task.html', context)


@login_required(login_url="/login")
def w3af_new(request):
    context = crearContextBase(request)
    u = request.user
    userid = u.id
    if request.method == 'POST':
        form = forms.w3afForm(request.POST, user=u)
        if form.is_valid():
            n = form.cleaned_data['name']
            # target
            t = form.cleaned_data['target']
            to = form.cleaned_data['target_os']
            tf = form.cleaned_data['target_framework']
            # auth
            lu = form.cleaned_data['login_url']
            lun = form.cleaned_data['login_username']
            lp = form.cleaned_data['login_password']
            luf = form.cleaned_data['login_userfield']
            lpf = form.cleaned_data['login_passwordfield']
            lm = form.cleaned_data['login_method']
            # basic auth
            hd = form.cleaned_data['http_domain']
            hu = form.cleaned_data['http_user']
            hp = form.cleaned_data['http_password']
            # parameters
            p = form.cleaned_data['profile']
            m = form.cleaned_data['mail']
            mf = form.cleaned_data['mail_field']
            pc = form.cleaned_data['periodicity_checkbox']
            ed = form.cleaned_data['execute_date']
            pd = form.cleaned_data['periodicity']
            if 'save' in request.POST:
                e = "Saved"
            elif 'cue' in request.POST:
                e = "On Hold"

            if p == "Fast Scan":
                pb = "fast_scan"
            elif p == "Full Audit":
                pb = "full_audit"
            elif p == "OWASP Top 10":
                pb = "OWASP_TOP10"

            if m:
                p = models.w3af_requests.objects.create(name=n, target=t, target_os = to, target_framework = tf, login_url = lu, login_username = lun, login_password = lp,
                                                        login_userfield = luf, login_passwordfield = lpf, login_method = lm, user=request.user, state=e, profile=pb,
                                                          mail=mf, http_user= hu, http_password=hp, http_domain=hd)  # crear la request
            else:
                p = models.w3af_requests.objects.create(name=n, target=t, target_os = to, target_framework = tf, login_url = lu, login_username = lun, login_password = lp,
                                                        login_userfield = luf, login_passwordfield = lpf, login_method = lm, user=request.user, profile=pb,
                                                          state=e, http_user= hu, http_password=hp, http_domain=hd)  # crear la request
            r = models.w3af_results.objects.create(id=p.id)
            return HttpResponseRedirect('/w3af/tasks/')
        else:
            print(form.errors)
    else:
        form = forms.w3afForm(user=u)
    context.update({"initial": 0})
    context.update({"form": form})
    return render(request, 'w3af_new.html', context)
