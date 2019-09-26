# -*- coding: utf-8 -*-
import base64

import logging
from django.contrib.auth.models import User
from django.utils import timezone
from idna import unicode
from rest_framework import views
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.response import Response
from datetime import datetime
from openvas_lib import VulnscanManager, VulnscanException
from xml.etree import ElementTree
from mailer import Mailer, Message
from dateutil.relativedelta import relativedelta

from AAPT.settings import openvas_username, openvas_password
from OpenVAS.models import openvas_results, openvas_requests
#from SQLmap.models import sqlmap_results, sqlmap_requests
#from w3af.models import w3af_results, w3af_requests

logger = logging.getLogger(__name__)


class OpenVAS_addResult(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        result = openvas_results.objects.get(id=id)
        print(result.id)
        f = request.data['file']
        result.output = f.read().replace("\n", "<br>")
        result.save()
        return Response(status=204)

class OpenVAS_setState(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        task = openvas_requests.objects.get(id=id)
        print(task.id)
        e = request.data['state']
        task.state = e
        task.save()
        if e == "Finished":
            result = openvas_results.objects.get(id=id)
            # Parsejar XML per treure High Medium i Low
            scanner = VulnscanManager("localhost", openvas_username, openvas_password)
            auxReport = scanner.get_report_xml(str(result.report))
            auxReportString = ElementTree.tostring(auxReport.find("report").find("report").find("results"),
                                                   encoding='utf-8', method='xml')
            auxReportXML = ElementTree.fromstring(auxReportString)
            print(auxReportString)
            high = 0
            medium = 0
            low = 0
            log = 0
            for v in auxReportXML:
                print(str(v.find("threat").text))
                if v.find("threat").text == "High":
                    high += 1
                elif v.find("threat").text == "Medium":
                    medium += 1
                elif v.find("threat").text == "Low":
                    low += 1
                elif v.find("threat").text == "Log":
                    log += 1
            parsed = "High: " + str(high) + " / Medium: " + str(medium) + " / Low: " + str(low) + " / Log: " + str(log)
            print(parsed)
            # Inserting finish date and results
            result.finish_date = timezone.now()
            result.output = parsed
            result.save()
            if task.mail:
                report = scanner.get_report_pdf(str(result.report))
                fileName = "Report_" + task.name + "_" + datetime.strftime(result.finish_date, "%Y%m%d%H%M") + ".pdf"
                reportXML = ElementTree.tostring(report.find("report"), encoding='utf-8', method='xml')
                fullReport = ElementTree.fromstring(reportXML)
                pdf = base64.b64decode(fullReport.find("in_use").tail)
                username = User.objects.get(id=task.user.id).username
                print("Username: " + username)
                body = u'Task ' + unicode(
                    task.name) + u' has finished. The scan found the following vulnerabilities:\n' + unicode(
                    parsed) + u'\nAttached you will find the complete report.\n For more information: https://localhost:8000/OpenVAS/task/' + unicode(
                    task.id) + u'/'
                message = Message(From="2apt@applus.com",
                                  To=[task.mail],
                                  Subject=u'[AAPT] OpenVAS Report')
                message.Body = body.encode('utf-8')
                sender = Mailer('localhost')
                message.attach(filename=fileName, content=pdf, mimetype="application/pdf")
                sender.send(message)
        return Response(status=204)

@api_view(['GET'])
def OpenVAS_getState(request, id, format=None):
    if request.method == 'GET':
        task = openvas_requests.objects.all().get(id=id)
        return Response(str(task.state), status=200)


@api_view(['GET'])
def OpenVAS_kill(request, id, format=None):
    if request.method == 'GET':
        task = openvas_requests.objects.all().get(id=id)
        if task.state == "Blocked" or task.state == "Deleted":
            openvas_requests.objects.filter(id=id).delete()
            openvas_results.objects.filter(id=id).delete()
            return Response(status=204)
        return Response(status=400)


@api_view(['GET'])
def OpenVAS_getDeleted(request, format=None):
    if request.method == 'GET':
        query = openvas_requests.objects.all().filter(state="Deleted")
        if query:
            eliminades = query[0].id
            for t in query[1:]:
                eliminades += " " + t.id
            return Response(eliminades, status=200)
        else:
            return Response(status=404)


@api_view(['GET'])
def OpenVAS_getNext(request, format=None):
    if request.method == 'GET':
        ordered = openvas_requests.objects.all().filter(state="On Hold").order_by('insert_date')
        if ordered:
            next = ordered[0]
            print(next)
            task = str(next.id) + "|" + next.target + "|" + next.config
            return Response(task, status=200)
        else:
            return Response(status=404)


class OpenVAS_setReport(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        res = openvas_results.objects.get(id=id)
        print(res.id)
        r = request.data['report']
        res.report = r
        res.save()
        return Response(status=204)


class OpenVAS_setPercentage(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        task = openvas_requests.objects.get(id=id)
        print(task.id)
        p = request.data['percentage']
        task.percentage = p
        task.save()
        return Response(status=204)

'''
class SQLmap_addResult(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        resultat = sqlmap_results.objects.get(id=id)
        print(resultat.id)
        f = request.data['file']
        resultat.sortida = f.read()
        resultat.save()
        return Response(status=204)
    
class SQLmap_setReport(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        resultat = sqlmap_results.objects.get(id=id)
        print(resultat.id)
        f = request.data['file']
        resultat.report = f.read().replace("\n", "<br>")
        resultat.save()
        return Response(status=204)
    
class SQLmap_setState(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        task = sqlmap_requests.objects.get(id=id)
        print(task.id)
        e = request.data['state']
        task.state = e
        task.save()
        if e == "Finished":
            res = sqlmap_results.objects.get(id=id)
            res.finish_date = datetime.now()
            res.save()
            if task.mail:
                username = User.objects.get(id=task.user.id).username
                print("Username: " + username)
                message = Message(From="2apt@applus.com",
                                  To=[task.mail],
                                  Subject=u'[AAPT] SQLmap Report')
                message.Body = u'Task ' + unicode(
                    task.name) + u' already finished. To see the results:\n https://localhost:8080/SQLmap/task/' + unicode(
                    task.id) + u'/'
                sender = Mailer('localhost')
                sender.send(message)
        return Response(status=204)


@api_view(['GET'])
def SQLmap_getState(request, id, format=None):
    if request.method == 'GET':
        task = sqlmap_requests.objects.all().get(id=id)
        return Response(str(task.state), status=200)


@api_view(['GET'])
def SQLmap_kill(request, id, format=None):
    if request.method == 'GET':
        task = sqlmap_requests.objects.all().get(id=id)
        if task.state == "Blocked":
            sqlmap_requests.objects.filter(id=id).delete()
            sqlmap_results.objects.filter(id=id).delete()
            return Response(status=204)
        return Response(status=404)
    
@api_view(['GET'])
def SQLmap_getNext(request, format=None):
    if request.method == 'GET':
        ordered = sqlmap_requests.objects.all().filter(state="On Hold").order_by('insert_date')
        if ordered:
            next = ordered[0]
            print(next)
            task = str(next.id) + "|" + next.target + "|" + str(next.verbosity) + "|" + str(next.level) + "|" + str(
                next.risk) + "|" + str(next.depth) + "|" + next.charset
            return Response(task, status=200)
        else:
            return Response(status=404)

class w3af_addResult(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        result = w3af_results.objects.get(id=id)
        print(result.id)
        f = request.data['file']
        result.output = f.read()
        result.save()
        return Response(status=204)

class w3af_setReport(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        result = w3af_results.objects.get(id=id)
        print(result.id)
        f = request.data['file']
        result.report = f.read().replace("\n", "<br>")
        result.save()
        return Response(status=204)


class w3af_setState(views.APIView):
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request, id, format=None):
        task = w3af_requests.objects.get(id=id)
        print(task.id)
        e = request.data['state']
        task.state = e
        task.save()
        if e == "Finished":
            res = w3af_results.objects.get(id=id)
            res.finish_date = datetime.now()
            res.save()
            if task.mail:
                username = User.objects.get(id=task.user.id).username
                print("Username: " + username)
                message = Message(From="2apt@applus.com",
                                  To=[task.mail],
                                  Subject=u'[AAPT] w3af Report')
                message.Body = u'Task ' + unicode(
                    task.name) + u' has finished. To see the results:\n https://localhost:8080/w3af/task/' + unicode(
                    task.id) + u'/'
                sender = Mailer('localhost')
                sender.send(message)
        return Response(status=204)

@api_view(['GET'])
def w3af_getState(request, id, format=None):
    if request.method == 'GET':
        task = w3af_requests.objects.all().get(id=id)
        return Response(str(task.state), status=200)

@api_view(['GET'])
def w3af_kill(request, id, format=None):
    if request.method == 'GET':
        task = w3af_requests.objects.all().get(id=id)
        if task.state == "Blocked":
            w3af_requests.objects.filter(id=id).delete()
            w3af_results.objects.filter(id=id).delete()
            return Response(status=204)
        return Response(status=404)


@api_view(['GET'])
def w3af_getNext(request, format=None):
    if request.method == 'GET':
        ordered = w3af_requests.objects.all().filter(state="On Hold").order_by('insert_date')
        if ordered:
            next = ordered[0]
            print(next)
            if not next.login_url:
                next.login_url = "empty"
            if not next.login_username:
                next.login_username = "empty"
            if not next.login_userfield:
                next.login_userfield = "empty"
            if not next.login_password:
                next.login_password = "empty"
            if not next.login_passwordfield:
                next.login_passwordfield = "empty"
            if not next.http_domain:
                next.http_domain = "empty"
            if not next.http_user:
                next.http_user = "empty"
            if not next.http_password:
                next.http_password = "empty"
            task = str(
                next.id) + "|" + next.target + "|" + next.target_os + "|" + next.target_framework + "|" + next.profile + "|" + next.login_url + "|" + next.login_username + "|" + next.login_password + "|" + next.login_userfield + "|" + next.login_passwordfield + "|" + next.login_method + "|" + next.http_domain + "|" + next.http_user + "|" + next.http_password
            return Response(task, status=200)
        else:
            return Response(status=404) 
'''