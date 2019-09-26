from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from openvas_lib import VulnscanManager
from django.shortcuts import render
from django.http import HttpResponseRedirect
from xml.etree import ElementTree
import base64
from datetime import datetime

from Core.views import crearContextBase
from rest_framework.response import Response
from OpenVAS import models, forms
from OpenVAS.forms import full_domain_validator
from OpenVAS.models import openvas_requests, openvas_results

from AAPT.settings import openvas_username, openvas_password

def task_exists(function=None):
    # test per saber si la tasca demanada existeix
    def _dec(view_func):

        def _view(request, *args, **kwargs):
            id = kwargs['id']
            if openvas_requests.objects.filter(id=id):
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
            if openvas_requests.objects.filter(id=id, user=request.user).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/task_unauthorized/')

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)

@login_required(login_url="/login")
def openvas_delete(request, id):
    user = request.user
    task = openvas_requests.objects.get(id=id)
    if task.user == user or user.is_staff:
        if task.state == "Running":
            task.state = "Blocked"
            task.save()
            return HttpResponseRedirect('/OpenVAS/task/' + id + '/')
        elif task.state != "Blocked":
            # openvas_requests.objects.filter(id=id).delete()
            # openvas_results.objects.filter(id=id).delete()
            task.state = "Deleted"
            task.save()
            return HttpResponseRedirect('/OpenVAS/tasks/')
    return Response(status=401)


@login_required(login_url="/login")
def openvas_download(request, id):
    scanner = VulnscanManager("localhost", openvas_username, openvas_password)
    task = openvas_requests.objects.get(id=id)
    if task.state == "Finished":
        result = openvas_results.objects.get(id=task.id)
        print(result.report)
        # Retornant pdf
        report = scanner.get_report_pdf(str(result.report))
        nomArxiu = "Report_" + task.name + "_" + datetime.strftime(result.finish_date, "%Y%m%d%H%M") + ".pdf"
        reportXML = ElementTree.tostring(report.find("report"), encoding='utf-8', method='xml')
        fullReport = ElementTree.fromstring(reportXML)
	    #response = HttpResponse(base64.b64decode(fullReport.find("in_use").tail), content_type='application/pdf')
        response = HttpResponse(base64.b64decode(reportXML.split(">")[-2]), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=' + nomArxiu
        return response
    else:
        context = crearContextBase(request)
        context.update({'openvas_tasks': "active"})
        results = "fail"
        context.update({'task': task, 'results': results})
        return render(request, 'openvas_task.html', context)


@login_required(login_url="/login")
def openvas_relaunch(request, id):
    task = openvas_requests.objects.get(id=id)
    res = openvas_results.objects.get(id=id)
    if task.state == "Finished" or task.state == "Saved":
        res.output = None
        res.report = None
        res.finish_date = None
        res.save()
        task.state = "On Hold"
        task.percentage = 0
        task.insert_date = datetime.now()
        task.save()
    return HttpResponseRedirect('/OpenVAS/tasks/')


@login_required(login_url="/login")
def openvas_modify(request, id):
    context = crearContextBase(request)
    context.update({'openvas_tasks': "active"})
    u = request.user
    task = openvas_requests.objects.get(id=id)
    context.update({"task": task, "notModify": False})
    if task.state != "Running" and task.state != "Blocked":
        if request.method == 'POST':
            form = forms.OpenVASForm(request.POST, user=u)
            if form.is_valid():
                ips = form.cleaned_data['ips']
                urls = form.cleaned_data['urls']
                m = form.cleaned_data['mail']
                mf = form.cleaned_data['mail_field']
                c = form.cleaned_data['config']
                pc = form.cleaned_data['periodicity_checkbox']
                ed = form.cleaned_data['execute_date']
                pd = form.cleaned_data['periodicity']
                if 'save' in request.POST:
                    e = "Saved"
                elif 'cue' in request.POST:
                    e = "On Hold"

                # Treiem els espais entre hostnames
                urls = urls.replace(" ", "")
                ips = ips.replace(" ", "")

                if ips != "" and urls != "":
                    t = ips + "," + urls
                elif ips != "":
                    t = ips
                else:
                    t = urls

                n = form.cleaned_data['name']
                if task.state != "Running" and task.state != "Blocked":
                    task.name = n
                    task.target = t
                    task.user = u
                    task.state = e
                    task.percentage = 0
                    task.config = c
                    task.modify_date = datetime.now()
                    if m:
                        task.mail = mf
                    else:
                        task.mail = None
                    if pc:
                        task.periodicity = pd
                        task.execute_date = ed
                    else:
                        task.periodicity = None
                        task.execute_date = None
                    task.save()
                else:
                    context.update({"notModify": True})
                    return render(request, 'openvas_new.html', context)
                return HttpResponseRedirect('/OpenVAS/tasks/')
            else:
                print(form.errors)
        else:
            form = forms.OpenVASForm(user=u)
            form.fields["name"].initial = task.name
            tasks = task.target.split(",")
            urls = ""
            ips = ""
            if full_domain_validator(tasks[0]) == 1:
                ips += tasks[0]
            else:
                urls += tasks[0]
            for t in tasks[1:]:
                if full_domain_validator(t) == 1:
                    urls += "," + t
                else:
                    ips += "," + t
            form.fields["urls"].initial = urls
            form.fields["ips"].initial = ips
            if task.mail:
                form.fields["mail_field"].initial = task.mail
                form.fields["mail"].initial = True
            form.fields["config"].initial = task.config
            context.update({"form": form})
            return render(request, 'openvas_new.html', context)
    else:
        context.update({"notModify": True})
        return render(request, 'openvas_new.html', context)

@login_required(login_url="/login")
def openvas_howto(request):
    context = crearContextBase(request)
    context.update({'openvas_howto': "active"})
    return render(request, 'openvas_howto.html', context)

@login_required(login_url="/login")
@task_exists
@user_can_view_task
def openvas_task(request, id):
    context = crearContextBase(request)
    context.update({'openvas_tasks': "active"})
    task = openvas_requests.objects.get(id=id)
    results = openvas_results.objects.get(id=task.id)
    context.update({'task': task, 'results': results})
    return render(request, 'openvas_task.html', context)



@login_required(login_url="/login")
def openvas_tasks(request):
    context = crearContextBase(request)
    context.update({'openvas_tasks': "active"})
    return render(request, 'openvas_tasks.html', context)


@login_required(login_url="/login")
def openvas_new(request):
    context = crearContextBase(request)
    context.update({'openvas_new': "active"})
    u = request.user
    if request.method == 'POST':
        form = forms.OpenVASForm(request.POST, user=u)
        if form.is_valid():
            ips = form.cleaned_data['ips']
            urls = form.cleaned_data['urls']
            m = form.cleaned_data['mail']
            mf = form.cleaned_data['mail_field']
            c = form.cleaned_data['config']
            if 'save' in request.POST:
                e = "Saved"
            elif 'cue' in request.POST:
                e = "On Hold"

            # Treiem els espais entre hostnames
            urls = urls.replace(" ", "")
            ips = ips.replace(" ", "")

            if ips != "" and urls != "":
                t = ips + "," + urls
            elif ips != "":
                t = ips
            else:
                t = urls

            n = form.cleaned_data['name']
            if m:
                p = models.openvas_requests.objects.create(name=n, target=t, user=request.user,
                                                           state=e,
                                                           percentage=0, mail=mf, config=c)  # crear la request
            else:
                p = models.openvas_requests.objects.create(name=n, target=t, user=request.user,
                                                           state=e,
                                                           percentage=0, config=c)  # crear la request
            r = models.openvas_results.objects.create(id=p.id)
            return HttpResponseRedirect('/OpenVAS/tasks/')
        else:
            print(form.errors)
    else:
        form = forms.OpenVASForm(user=u)
    context.update({"form": form})
    return render(request, 'openvas_new.html', context)
