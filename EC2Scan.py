
import requests
import xml.etree.ElementTree as ET
import time


def login(s):
    print("Login Step")
    #
    # ---Session Login---
    #
    # Logs into a Qualys session given a requests.Session object 's'. A Session.post()
    # always returns a response, here assigned 'r'.
    #
    payload = {
               'action':'login',
               'username':'',
               'password':''
               }
    r = s.post('https://qualysguard.qualys.eu/api/2.0/fo/session/', data=payload)

    # Now that all the hard work was done, lets parse the response.
    xmlreturn = ET.fromstring(r.text)
    for elem in xmlreturn.findall('.//TEXT'):
        print elem.text #Prints the "Logged in" message. Not really needed, but reassuring.



def logout(s):
    print("Logout Step")
    #
    # ---Logout---
    #
    # Really, you need a description for what this does?
    #
    payload = {
               'action':'logout'
               }
    r = s.post('https://qualysguard.qualys.eu/api/2.0/fo/session/', data=payload)

    # Now that all the hard work was done, lets parse the response.
    xmlreturn = ET.fromstring(r.text)
    for elem in xmlreturn.findall('.//TEXT'):
        print elem.text   #Prints the "Logged out" message. Not really needed, but reassuring.


#scanRef = launchScan(s, ec2Endpoint, connector, scannerName, ec2Instance)
def launchScan(s, endpoint, connector, scanner, ec2instance):
    print("Launch Scan Step")
    #
    #---Launch Scan---
    #
    # Launches a scan given a target IP and returns the reference string to be
    # used when checking the scan status and starting a report.
    # Note: The field 'iscanner_name' is the same as the the dropdown list of
    # scanner appliances when launching a scan from the web interface.
    # I just have a thing for using the last appliance in the list.
    # The 'option_id' is found on the info page of the scanner options profile
    # you want to use.
    #
    # US Scanner
    payload = {
               'action':'launch',
               'scan_title':'EC2',
               'connector_name':connector,
               'ec2_endpoint':endpoint,
               'iscanner_name':scanner,
               #'target_from':'tags',
               #'use_ip_nt_range_tags':'0',
               #'tag_include_selector':'any',
               #'tag_set_by':'id',
               #'tag_set_include':'20782645',
               'option_id':'90514245',
               'ec2_instance_ids':ec2instance,
               }

    r = s.post('https://qualysguard.qualys.eu/api/2.0/fo/scan/', data=payload)
   
    # Now that all the hard work was done, lets parse the response.
    #print r.text   #prints the full xml response from Qualys just for fun.
    xmlreturn = ET.fromstring(r.text)
    for elem in xmlreturn.findall('.//ITEM'):
        print elem.text   #Prints the "Scan Launched" message. Not really needed, but reassuring.
        if (elem[0].text == 'REFERENCE'): scanRef = elem[1].text
    return scanRef
 
 
 
 
def checkScan(s, scanRef):
    #
    #---Check Scans---
    #
    # Checks the status of our scan.
    #
    payload = {
               'action':'list',
               'scan_ref':scanRef,
               }
    r = s.post('https://qualysguard.qualys.eu/api/2.0/fo/scan/', data=payload)
 
    # Now that all the hard work was done, lets parse the response.
    #print r.text   #prints the full xml response from Qualys just for fun.
    xmlreturn = ET.fromstring(r.text)
    for elem in xmlreturn.findall('.//STATUS'):
        status = elem[0].text
        print elem[0].text   #Prints the status message. Not really needed, but reassuring.
    return status
 
 
# s, ec2Endpoint, connector, scannerName, ec2Instance)
def launchReport(s, scanRef, reportType, ec2Instance):
    print("Launch Report Step")
    #
    #---Launch Report---
    #
    # Launches a Report given a scanRef and type of report and returns the reference string
    # to be used when checking the status of the report and downloading it.
    # Note: I got template_id from the web interface, reports > templates and then select 'info'
    # from the drop-down on the particular template you want to use.
    # Make sure the report template you use is of the "Manual" type
    #
    payload = {
               'action':'launch',
               'report_type':'Scan',
               #'template_id':'92074087',
               #'template_id':'92062891', Linux report non-dmz
               'template_id':'92141729',
               'output_format':reportType,
               'ips':targetIP,
               'report_refs':scanRef,
               'report_title':ec2Instance,
               }
    r = s.post('https://qualysguard.qualys.eu/api/2.0/fo/report/', data=payload)
 
    # Now that all the hard work was done, lets parse the response.
    #print r.text   #prints the full xml response from Qualys just for fun.
    xmlreturn = ET.fromstring(r.text)
    for elem in xmlreturn.findall('.//ITEM'):
        if (elem[0].text == 'ID'): reportID = elem[1].text
    return reportID
 
 
 
def checkReport(s, reportID):
    #
    #---Check Reports---
    #
    # Checks the status of our Report.
    #
    payload = {
               'action':'list',
               'id':reportID,
               }
    r = s.post('https://qualysguard.qualys.eu/api/2.0/fo/report/', data=payload)
 
    # Now that all the hard work was done, lets parse the response.
    #print r.text   #prints the full xml response from Qualys just for fun.
    xmlreturn = ET.fromstring(r.text)
    for elem in xmlreturn.findall('.//STATUS'):
        status = elem[0].text
        print elem[0].text  #Prints the status message. Not really needed, but reassuring.
    return status
 
 
 
def downloadReport(s, reportID, targetIP):
    print("Download Report Step")
    #
    #---Download Report---
    #
    # Lets get the report.
    #
    payload = {
               'action':'fetch',
               'id':reportID,
               }
    r = s.post('https://qualysguard.qualys.eu/api/2.0/fo/report/', data=payload)
 
    # Now that all the hard work was done, lets get that report.
    # No chunking needed due to small size of a single IP scan report.
    with open("/Users/mikev1963/Python/qualys/OUTPUT/Scan_Report_"+targetIP+".pdf", "wb") as report:
        report.write(r.content)
 
 
def main():
    s = requests.Session()
    s.headers.update({'X-Requested-With':'Facklers PyQual python primer'})
    login(s)
 
    ec2Endpoint = 'eu-west-2'
    connector = 'AWSLZ-NET-JAS'
    scannerName = 'awslz-lon-az1-qly-001'
    ec2InstanceList = ['i-03027da5059122483']
 
    for ec2Instance in ec2InstanceList:
        print ec2Instance
        scanRef = launchScan(s, ec2Endpoint, connector, scannerName, ec2Instance)
 
        # These API calls are valuable commodities, lets wait at least 10 minutes before we check.
        time.sleep(600)
 
        # Ok, now lets check on the scan.
        while checkScan(s, scanRef) != "Finished":
            time.sleep(600)

        reportType = 'pdf'
        reportID = launchReport(s, scanRef, reportType, ec2Instance)

        # Apparently asking about a report too soon after initiating it causes bad
        # responses which breaks checkReport()
        time.sleep(120)

        # OK, now lets check on the report, reports go faster so we can shorten the interval.
        while checkReport(s, reportID) != "Finished":
            time.sleep(120)

        downloadReport(s, reportID, targetIP)

    logout(s)
    s.close()

if __name__ == "__main__": main()
