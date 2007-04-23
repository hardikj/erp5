#!/usr/bin/env python

import os
import re
import signal
from time import sleep
import urllib2
from subprocess import Popen, PIPE
from sendMail import sendMail
import pysvn

host = 'localhost'
port = 8080
portal_name = 'erp5_portal'
instance_home = '/var/lib/zope/unit_test'
profile_dir = '%s/profile' % instance_home

def main():
  setPreference()
  unsubscribeFromTimerService()
  status = getStatus()
  xvfb_pid = None
  firefox_pid = None
  try:
    xvfb_pid = runXvfb()
    firefox_pid = runFirefox()
    while True:
      sleep(10)
      cur_status = getStatus()
      if status != cur_status:
        break
    print cur_status
  finally:
      if xvfb_pid:
        os.kill(xvfb_pid, signal.SIGTERM)
      if firefox_pid:
        os.kill(firefox_pid, signal.SIGTERM)

def startZope():
  os.environ['erp5_force_data_fs'] = "1"
  os.system('%s/bin/zopectl start' % instance_home)
  sleep(2) # ad hoc

def stopZope():
  os.system('%s/bin/zopectl stop' % instance_home)

def runXvfb():
  pid = os.spawnlp(os.P_NOWAIT, 'Xvfb', 'Xvfb', ':123')
  display = os.environ['DISPLAY']
  if display:
    (displayname, protocolname, hexkey) = Popen(['xauth', 'list', display], stdout=PIPE).communicate()[0].split()
    Popen(['xauth', 'add', 'localhost/unix:123', protocolname, hexkey])
  print 'Xvfb : %d' % pid
  return pid

def prepareFirefox():
  os.system("rm -rf %s" % profile_dir)
  os.mkdir(profile_dir)
  pref = file(os.path.join(os.path.dirname(__file__), 'prefs.js')).read()
  pref_file = open(os.path.join(profile_dir, 'prefs.js'), 'w')
  pref_file.write(pref)
  pref_file.close()

def runFirefox():
  os.environ['MOZ_NO_REMOTE'] = '1'
  os.environ['DISPLAY'] = ':123'
  os.environ['HOME'] = profile_dir
  prepareFirefox()
  pid = os.spawnlp(os.P_NOWAIT, "firefox", "firefox", "-profile", profile_dir, "http://%s:%d/%s/portal_tests?auto=true&__ac_name=ERP5TypeTestCase&__ac_password=" % (host, port, portal_name))
  os.environ['MOZ_NO_REMOTE'] = '0'
  print 'firefox : %d' % pid
  return pid

def getStatus():
  try:
    status = urllib2.urlopen('http://%s:%d/%s/TestTool_getResults' % (host, port, portal_name)).read()
  except urllib2.HTTPError, e:
    if e.msg == "No Content" :
      status = ""
    else:
      raise
  return status

def setPreference():
  urllib2.urlopen('http://%s:%d/%s/BTZuite_setPreference?__ac_name=ERP5TypeTestCase&__ac_password=' % (host, port, portal_name))

def unsubscribeFromTimerService():
  urllib2.urlopen('http://%s:%d/%s/portal_activities/?unsubscribe:method=&__ac_name=ERP5TypeTestCase&__ac_password=' % (host, port, portal_name))

def sendResult():
  result_uri = urllib2.urlopen('http://%s:%d/%s/TestTool_getResults' % (host, port, portal_name)).readline()
  file_content = urllib2.urlopen(result_uri).read()
  passes_re = re.compile('<th[^>]*>Tests passed</th>\n\s*<td[^>]*>([^<]*)')
  failures_re = re.compile('<th[^>]*>Tests failed</th>\n\s*<td[^>]*>([^<]*)')
  check_re = re.compile('<img[^>]*?/check.gif"\s*[^>]*?>')
  error_re = re.compile('<img[^>]*?/error.gif"\s*[^>]*?>')
  error_title_re = re.compile('error.gif.*?>([^>]*?)</td></tr>', re.S) 
  pass_test_re = re.compile('<div style="padding-top: 10px;">\s*<p>\s*<img[^>]*?/check.gif".*?</div>\s.*?</div>\s*', re.S)
  footer_re = re.compile('<h2> Remote Client Data </h2>.*</table>', re.S)

  passes = passes_re.search(file_content).group(1)
  failures = failures_re.search(file_content).group(1)
  error_titles = [re.compile('\s+').sub(' ', x).strip() for x in error_title_re.findall(file_content)]
  os.chdir('%s/Products/ERP5' % instance_home)
  revision = pysvn.Client().info('.').revision.number

  subject = "ERP5 r%s: Functional Tests, %s Passes, %s Failures" % (revision, passes, failures)
  summary = """
Test Summary

Tests passed: %4s
Tests failed: %4s

Following tests failed:

%s""" % (passes, failures, "\n".join(error_titles))
  file_content = pass_test_re.sub('', file_content)
  file_content = footer_re.sub('', file_content)
  file_content = check_re.sub('<span style="color: green">PASS</span>', file_content)
  file_content = error_re.sub('<span style="color: red">FAIL</span>', file_content)
  status = (not failures)
  sendMail(subject = subject, body = summary, status = status,
           attachments = [file_content])

if __name__ == "__main__":
  startZope()
  main()
  sendResult()
  stopZope()
