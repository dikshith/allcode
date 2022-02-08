#!/bin/bash

#About the program - This program reads the HAR file exported from Chrome-Dev Tools. It parses the HAR file and
# writes the following information into a CSV and HTML file.
# URLPath, url_hostname, req_content_type, Class, Method, Inner Methods, request_type, response_status, response_size, response_time, response_Blocked, response_wait, response_receive, response_blocked_queueing
#Pre-Requisite :
# curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# sudo python3 get-pip.py
# pip3 install pathlib
# pip3 install dateparser

#How to Run : bash ./run_har_parser.sh -i <<HAR file or derectory path>> -o <<Output Directory name>>


#===================================================================================================================

help_text="bash ./run_har_parser.sh -i <input har file/directory> -o <output result directory>"
if [ $# -eq 0 ];
then
     echo ${help_text}
    exit 0
else
while getopts :i:o:h flag
do
    case "${flag}" in
        i) input_file="${OPTARG}";;
        o) result_folder=${OPTARG}
            if ! mkdir ${result_folder}; then
            exit 2 ;
            fi;;
        h) echo ${help_text};
            exit 2;;
        ?) echo ${help_text} >&2;
          exit 2;;
    esac
done
fi

# if ! mkdir ${result_folder}; then
#     exit 2 ;
# fi
csv_file=${result_folder}/result.csv
html_file=${result_folder}/result.html


args=( -i "${input_file}" -o ${csv_file})
python3 - "${args[@]}" << END
import re
import csv
import json
import sys
import getopt
from urllib.parse import urlparse
from urllib.parse import parse_qs
from operator import itemgetter
import dateparser
import glob
import os
def parser(filename,outputfile):
        harfile = open(filename)
        harfile_json = json.loads(harfile.read())
        # print(harfile_json)
        harfile.close()         
        HAR_File = filename
        index=1
        output_list=[]
        output_list.append(['Input file : '+ HAR_File])
#        output_list.append(['S.No','Start time','URLPath','URL Hostname','Req Content Format','Class','Method','Inner Calls','Request Type','Response Status','Response Size','Total Time','Wait Time(TTFB)','Blocked Time','Receive Time','Blocked Queueing Time','Server Timing'])
        output_list.append(['S.No','Start time','URLPath','URL Hostname','Req Content Format','Class','Method','Inner Calls','Request Type','Response Status','Response Size','Total Time','Wait Time(TTFB)','Blocked Time','Receive Time','Blocked Queueing Time'])
        for entry in harfile_json['log']['entries']:
            urlparts = urlparse(entry['request']['url'])
            url_path = urlparts.path
            url_hostname = urlparts.hostname          
            regex_auracalls = re.compile(".*ApexAction.execute.*")
            apexcall = re.search(regex_auracalls,urlparts.query)
            request_type = entry['request']['method']
            # print(request_type)     
            response_status = entry['response']['status']
            response_time = "{:.2f}".format(entry['time'])
            response_size = entry['response']['_transferSize'] if '_transferSize' in entry['response'] else int(entry['response']['bodySize'])+int(entry['response']['headersSize'])
            response_Blocked = "{:.2f}".format(entry['timings']['blocked'])
            response_wait = "{:.2f}".format(entry['timings']['wait'])
            response_receive = "{:.2f}".format(entry['timings']['receive'])
            response_blocked_queueing = "{:.2f}".format(entry['timings']['_blocked_queueing']) if '_blocked_queueing' in entry['timings'] else ''
            serial_number= str(index)
            start_time = str(dateparser.parse(entry['startedDateTime']))[10:-9]
            request_class = ''
            request_method = ''
            inner_methods = ''
            req_content_type = ''   
            actions = ''
            inner_methods = ''
            regex_filter = re.compile(r"(?i).*\.(bmp|css|js|gif|ico|jpe?g|png|swf|woff|woff2|svg)")
            regex_filter2 = re.compile(r"(resource|analytics|javascript|ImageServer)(.*)")
            match_filter = re.search(regex_filter,url_path)
            match_filter2 = re.search(regex_filter2,url_path) 
            # server_timing = 'Not available'             
            if not (match_filter or match_filter2):
                if request_type=='POST':
                    text = entry['request']['postData']['text']
                    req_content_type = entry['request']['postData']['mimeType']
                    if url_path == "/apexremote":
                        actions = json.loads(text)
                        if isinstance(actions, dict):
                            request_class = actions['action']
                            request_method = actions['method']                        
                            if actions['method']=='doGenericInvoke':
                                request_class = actions['action']
                                request_method = actions['method']
                                inner_main_class= actions['data'][0]
                                inner_main_method= actions['data'][1]
                                inner_methods=inner_main_class+'-'+inner_main_method                                                                  
                                if isinstance(json.loads(actions['data'][2]).get('items'), dict):                                  
                                    # print(json.loads(actions['data'][2]).get('items'))
                                    inner_methods = inner_methods+',=>'
                                    for key in json.loads(actions['data'][2]).get('items').get('records')[0]:
                                        if (isinstance(json.loads(actions['data'][2]).get('items').get('records')[0].get(key), dict)):
                                            if json.loads(actions['data'][2]).get('items').get('records')[0].get(key).get('actions') != None:
                                                for key2 in json.loads(actions['data'][2]).get('items').get('records')[0].get(key).get('actions'):
                                                    if(key2 in ['remote']):
                                                        inner_methods = inner_methods+','+key2+' : '+json.loads(actions['data'][2]).get('items').get('records')[0].get(key).get('actions').get('remote').get('params').get('methodName')
                                                    elif(key2 in ['rest','client']):
                                                        continue
                                                    else:
                                                        inner_methods = inner_methods+','+key2+' : '+json.loads(actions['data'][2]).get('items').get('records')[0].get(key).get('actions').get(key2).get('remote').get('params').get('methodName')
                                elif isinstance(json.loads(actions['data'][2]).get('items'), list):
                                    # print(json.loads(actions['data'][2]).get('items'))
                                    if json.loads(actions['data'][2]).get('items')[0].get('parentRecord')!= None:
                                        inner_methods = inner_methods+',=>'
                                        for key in json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0]:
                                            if isinstance(json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key), dict):
                                                if json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key).get('actions') != None:
                                                    for key2 in json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key).get('actions'):
                                                        if json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key).get('actions').get(key2).get('remote') != None:
                                                            inner_methods = inner_methods+','+key2+' : '+json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key).get('actions').get(key2).get('remote').get('params').get('methodName')
                                            # if isinstance(json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key), dict):
                                        #     if json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key).get('actions') != None:
                                        #         if json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key).get('actions').get('remote') != None:
                                        #             print(key,json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get(key).get('actions').get('remote').get('params'))
                                        # inner_methods = inner_methods+' ******* '+str(json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].get('')get(key))
                                # for k in json.loads(actions['data'][2]).get('items')[0].get('parentRecord').get('records')[0].keys():
                                #     inner_methods = inner_methods+k
                                # inner_methods = 'DICT***'+''.join(json.dumps(inner_methods1))+'-'+''.join(json.dumps(inner_methods2)) if request_method not in ('saveDocxNewContractSections','getDocxSectionHtmlContent') else ''
                            elif actions['method']=='GenericInvoke2':
                              inner_main_class= actions['data'][0]
                              inner_main_method= actions['data'][1]                            
                              inner_methods=inner_main_class+'-'+inner_main_method
                            elif actions['method']=='invokeMethod':
                              inner_methods = actions['data'][0]
                        elif isinstance(actions, list):
                          for sub in actions:
                            request_class = request_class+','+sub['action']
                            request_method = request_method+','+sub['method']
                            # for method in [sub['method'] for sub in actions]:
                          for method in request_method.split(','):
                            if method=='invokeMethod':
                              inner_methods = ','.join([(method+' - '+str(sub['data'][0]) if sub['data'] != None else '') for sub in actions ])
                    elif url_path.__contains__('aura'):
                        # if response_status==200 and ("text" in entry['response']['content']):
                            # server_timing = str([(json.loads(entry['response']['content']['text'])).get('perfSummary').get('actions') if 'perfSummary' in (json.loads(entry['response']['content']['text'])).keys() else '', '<b>'+str(dict(map(itemgetter('name','value'), entry['response']['headers'])).get('Server-Timing')).replace('Total;dur','Total duration')+'</b>' if 'Server-Timing' in dict(map(itemgetter('name','value'), entry['response']['headers'])) else ''])\
                            # .replace('[','<div class="divTable" ><div class="divTableBody"><div class="divTableRow">')\
                            # .replace(']','</div></div></div></div></div>')\
                            # .replace(': {','</div><div class="divTableCell">')\
                            # .replace('{','<div class="divTableCell">')\
                            # .replace('}},','</div></div></div></div><div class="divTable" ><div class="divTableBody"><div class="divTableRow"> <div class="divTableCell" style="clear:both;">')\
                            # .replace('},','</div></div><div class="divTableRow"><div class="divTableCell">')
                        # else:
                            # server_timing = 'Not available'
                        # if apexcall:
                        #     regex_className = re.compile(r"className\":\"(.+?)\",\"")
                        #     regex_methodName = re.compile(r"methodName\":\"(.+?)\",\"")                    
                        #     inner_methodName=re.findall(regex_methodName,str(json.loads(parse_qs(text)['message'][0])))
                        #     inner_className=re.findall(regex_className,str(json.loads(parse_qs(text)['message'][0])))
                        #     # request_method = ','.join([sub['id']+' : '+urlparse(sub['descriptor']).path.split('$')[1]+'-'+str(sub["params"].get('classname'))+'-'+str(sub["params"].get('method')) for sub in json.loads(parse_qs(text)['message'][0])['actions']])
                        if apexcall:
                            # regex_className = re.compile(r"sClassName\': \'(.+?)\',")
                            # regex_methodName = re.compile(r"sMethodName\': \'(.+?)\',")                    
                            # inner_methodName=re.findall(regex_methodName,str(json.loads(parse_qs(text)['message'][0])))
                            # inner_className=re.findall(regex_className,str(json.loads(parse_qs(text)['message'][0])))
                            # print(str(json.loads(parse_qs(text)['message'][0])))
                            # request_method = ','.join([sub['id']+' : '+urlparse(sub['descriptor']).path.split('$')[1]+'-'+str(sub["params"].get('classname'))+'-'+str(sub["params"].get('method')) for sub in json.loads(parse_qs(text)['message'][0])['actions']])
                            for sub in json.loads(parse_qs(text)['message'][0])['actions']:
                                method_name=str(sub["params"].get('method'))
                                # print(str(sub["params"].get('method')))
                                if method_name=='GenericInvoke2':
                                    regex_className = re.compile(r"sClassName\': \'(.+?)\',")
                                    regex_methodName = re.compile(r"sMethodName\': \'(.+?)\',")                    
                                    inner_methodName=re.findall(regex_methodName,str(json.loads(parse_qs(text)['message'][0])))
                                    inner_className=re.findall(regex_className,str(json.loads(parse_qs(text)['message'][0])))
                                    inner_methods=(method_name+ ' : '+','.join(inner_className)+ ' - '+','.join(inner_methodName))
                                elif method_name=='handleData':
                                    call_type = json.loads(sub["params"].get('params').get('dataSourceMap')).get('type')
                                    call_value=json.loads(sub["params"].get('params').get('dataSourceMap')).get('value')
                                    if call_type=='apexremote':
                                        # call_value=json.loads(sub["params"].get('params').get('dataSourceMap')).get('value')
                                        inner_className=call_value.get('className')
                                        inner_methodName=call_value.get('methodName')
                                        inner_methods=(call_type+ ' : '+ inner_className+' - '+inner_methodName)
                                    elif call_type=='dataraptor':
                                        # inner_className=call_value.get('className')
                                        inner_methodName=call_value.get('bundleName')
                                        inner_methods=(call_type+ ' : '+ inner_methodName)   
                                    elif call_type=='integrationprocedure':
                                        inner_methodName=call_value.get('ipMethod')
                                        inner_methods=(call_type+ ' : '+inner_methodName)
                                elif method_name =='GenericInvoke2NoCont':
                                  inner_className=sub["params"].get('params').get('sClassName')
                                  inner_methodName=sub["params"].get('params').get('sMethodName')
                                  Bundle_name=''
                                  if inner_methodName=='invokeOutboundDR':
                                    Bundle_name=json.loads(sub["params"].get('params').get('input')).get('Bundle')
                                  elif inner_methodName=='invokeInboundDR':
                                    Bundle_name=json.loads(sub["params"].get('params').get('input')).get('bundleName')
                                  inner_methods=inner_className+' : '+inner_methodName+','+Bundle_name                         
                            request_method = ','.join([urlparse(sub['descriptor']).path.split('$')[1]+'-'+str(sub["params"].get('classname'))+'-'+str(sub["params"].get('method')) for sub in json.loads(parse_qs(text)['message'][0])['actions']])
                            # inner_methods = ','.join(inner_className)+'-'+','.join(inner_methodName)
                            request_class = ','.join([sub['descriptor'].split('/')[-2].split('.')[-1] for sub in json.loads(parse_qs(text)['message'][0])['actions']])
                            url_path=url_path+urlparts.query
                            # print(request_method)
                        else:
                            # request_method = ','.join([sub['id']+' : '+urlparse(sub['descriptor']).path.split('$')[1] for sub in json.loads(parse_qs(text)['message'][0])['actions']])
                            request_class = ','.join([sub['descriptor'].split('/')[-2].split('.')[-1] for sub in json.loads(parse_qs(text)['message'][0])['actions']])
                            request_method = ','.join([urlparse(sub['descriptor']).path.split('$')[1] for sub in json.loads(parse_qs(text)['message'][0])['actions']])
                            # inner_methods = ','.join(json.loads(sub["params"].get('successAction')).get('id')+' : '+urlparse(json.loads(sub["params"].get('successAction')).get('descriptor')).path.split('$')[1] if 'successAction' in sub["params"].keys() else '' for sub in json.loads(parse_qs(text)['message'][0])['actions'])
                            inner_methods = ','.join(urlparse(json.loads(sub["params"].get('successAction')).get('descriptor')).path.split('$')[1] if 'successAction' in sub["params"].keys() else '' for sub in json.loads(parse_qs(text)['message'][0])['actions'])
                index=index+1
                # output_list.append([serial_number,start_time,url_path,url_hostname,req_content_type,request_class,request_method,inner_methods,request_type,response_status,response_size,response_time,response_wait,response_Blocked,response_receive,response_blocked_queueing,server_timing])
                output_list.append([serial_number,start_time,url_path,url_hostname,req_content_type,request_class,request_method,inner_methods,request_type,response_status,response_size,response_time,response_wait,response_Blocked,response_receive,response_blocked_queueing])

        return output_list

def main(argv):
    filename = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('parser_v3.py  -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('parser_v3.py  -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            filename = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
            
    for f in filename.split(','):
      if not os.path.exists(f):
        print(f+ " : doesn't exists.")
        continue;
      else:
        if os.path.isdir(f):
            for harfile in glob.iglob(f + '/**/**.har', recursive=True):
              if os.path.isfile(harfile):
                output_list = parser(harfile,outputfile)
                with open(outputfile, "a") as f:
                    writer = csv.writer(f,delimiter='|')
                    writer.writerows(output_list)
        elif os.path.isfile(f):
            harfile=f
            output_list = parser(harfile,outputfile)
            with open(outputfile, "a") as f:
                writer = csv.writer(f,delimiter='|')
                writer.writerows(output_list)

if __name__=="__main__":
    main(sys.argv[1:])
END

function createHTML() {
     sed -i '' "s/-\[\]//g; s/\"en-us\"//g; s/\"en-gb\"//g; s/\"-\"//g;  s/\"//g" $1
 echo "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
 echo "<html>"
 echo "<head>
        <style>	
                body {font-family: \"Lucida Sans Unicode\", \"Lucida Grande\", sans-serif;}	
                /* Style the tab */	
                .tab {	
                  overflow: hidden;	
                  border: 1px solid #ccc;
/*                  background-color: #cce9fc; */
                }	
                /* Style the buttons inside the tab */	
                .tab button {	
                  background-color:  #7bc0ed;	
                  float: center;	
                  outline: none;	
                  cursor: pointer;	
                  padding: 5px 5px;	
                  transition: 0.6s;	
                  font-size: 12px;	
                  border: 1px solid #d9f2ff;
                  border-radius: 4px;
                  box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);
                }	
                /* Change background color of buttons on hover */	
                .tab button:hover {	
                  background-color: #ddd;
                  transition: 0.6s;	
                }	
                /* Create an active/current tablink class */	
                .tab button.active {	
                  background-color: #11476b;
                  color: #ffffff;
	
                }	
                /* Style the tab content */	
                .tabcontent {	
                  display: none;	
                  padding: 6px 12px;	
                  border: 1px solid #ccc;	
                  border-top: none;	
                }	
                </style>
 
 <style type=\"text/css\">
 .table-sortable th {
  cursor: pointer;
}

.table-sortable .th-sort-asc::after {
  content: "\25b4";
}

.table-sortable .th-sort-desc::after {
  content: "\25be";
}

.table-sortable .th-sort-asc::after,
.table-sortable .th-sort-desc::after {
  margin-left: 5px;
}

.table-sortable .th-sort-asc,
.table-sortable .th-sort-desc {
  background: rgba(51, 98, 187, 0.397);
}

nulltable a:link {
        color: #666;
        font-weight: bold;
        text-decoration:none;
}
table a:visited {
        color: #999999;
        font-weight:bold;
        text-decoration:none;
}
table a:active,
table a:hover {
        text-decoration:underline;
}
table {
        color:#666;
        font-size:12px;
        background:#fafafa;
        border:#ccc 1px solid;
        border-radius:3px;
        border-collapse:collapse;
        border-spacing: 0;
        box-shadow: 0 1px 2px #d1d1d1;
}
table th {
        color: white;
        text-align: center;
        vertical-align: bottom;
        height:15px;
        padding-bottom: 3px;
        padding-left: 5px;
        padding-right: 5px;
        background-color:#006BB2;
}
.verticalText {
        text-align: center;
        vertical-align: middle;
        width: 15px;
        margin: 0px;
        padding:1px 1px 0;
        background-color:#006BB2;
        white-space: nowrap;
        -ms-transform: rotate(-90deg);          /* IE9+ */
        -webkit-transform: rotate(-90deg);      /* Safari 3.1+, Chrome */
        -moz-transform: rotate(-90deg);         /* FF3.5+ */
        -o-transform: rotate(-90.0deg);         /* Opera 10.5 */
}
table th:first-child {
        text-align: left;
}
table tr:first-child th:first-child {
        border-top-left-radius:3px;}

table tr:first-child th:last-child {
        border-top-right-radius:3px;
}
table tr {
        text-align: center;
}
table td:first-child {
        text-align: left;
        border-left: 0;
}
table td {
        padding:5px 5px 5px;
        border-right:1px solid #e0e0e0;
        border-bottom:1px solid #e0e0e0;
        border-left: 1px solid #e0e0e0;
        }
table tr:last-child td {
        border-bottom:0;
}
table tr:last-child td:first-child {
        border-bottom-left-radius:3px;
}
table tr:last-child td:last-child {
        border-bottom-right-radius:3px;
}
.divHead{
color : #999999; font-size: 12px; padding: 5px 5px; border-right:1px solid #ccc;border-left:1px solid #ccc;
}
.divTable{
	display: table;
	width: 100%;
}
.divTableRow {
	display: table-row;
}
.divTableHeading {
	background-color: #EEE;
	display: table-header-group;
}
.divTableCell, .divTableHead {
	border: 1px solid #999999;
	display: table-cell;
	padding: 3px 10px;
}
.divTableHeading {
	background-color: #EEE;
	display: table-header-group;
	font-weight: bold;
}
.divTableFoot {
	background-color: #EEE;
	display: table-footer-group;
	font-weight: bold;
}
.divTableBody {
	display: table-row-group;
}
</style>
</head>
<body class=\"body\" style=\"margin: 1px; padding: 1px 1px 1px;\">"
echo "<h3 style=\"text-align:left\"><a id=\"top\"> HAR Parser V2 </a></h3>"

echo "<table align=\"left\" border=1>"
echo "</table>"
echo "</p>"
echo "<hr>"
isheader="true";
echo "<h4 style=\"text-align:left\"><a id=\"top\"> <u>HAR Data details:</u></a></h4>"

fileName=$1
echo "<div class=\"tab\">"
while read INPUT;
do
if [[ $INPUT == Input* ]]; then
tabName=`echo -n $INPUT|awk  -F '/'  '{ sub("\r", "", $NF); print $NF}'`
echo "<button class=\"tablinks\" onclick=\"harFiles(event, '${tabName}')\" id=\"defaultOpen\">${tabName}</button>"
fi
done < $fileName
echo "</div><div class=\"divHead\" style=\"font-style: italic;\">*** Size in bytes and Time in millisec</div><div><table>"


while read DIVINPUT ; do
if [[ $DIVINPUT == Input* ]]; then
tabName=`echo -n $DIVINPUT|awk  -F '/'  '{ sub("\r", "", $NF); print $NF}'`
echo "</table></div><div id=\"${tabName}\" class=\"tabcontent divHead\" >$DIVINPUT"
echo "<table  border=1  class=\"table-sortable\">"
    elif [[ $DIVINPUT == S.No* ]]; then
      echo "<thead><tr><th>${DIVINPUT//|/</th><th>}</th></tr></thead>" ;
    else
      VALUE=${DIVINPUT//|/</td><td align=center>}
      VALUE=${VALUE//,/<br/>}
      
      echo "<tr><td>${VALUE}</td></tr>" ;
    fi
done < $fileName;
echo "</table><script>
        function harFiles(evt, fileName) {
          var i, tabcontent, tablinks;
          tabcontent = document.getElementsByClassName(\"tabcontent\");
          for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = \"none\";
          }
          tablinks = document.getElementsByClassName(\"tablinks\");
          for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(\" active\", \"\");
          }
          document.getElementById(fileName).style.display = \"block\";
          evt.currentTarget.className += \" active\";
        }
        
        // Get the element with id=\"defaultOpen\" and click on it
        document.getElementById(\"defaultOpen\").click();
        </script>
        <script>
          /**
      * Sorts a HTML table.
      * 
      * @param {HTMLTableElement} table The table to sort
      * @param {number} column The index of the column to sort
      * @param {boolean} asc Determines if the sorting will be in ascending
      */
      function sortTableByColumn(table, column, asc = true) {
        const dirModifier = asc ? 1 : -1;
        const tBody = table.tBodies[0];
        const rows = Array.from(tBody.querySelectorAll(\"tr\"));
      
        // Sort each row
        const sortedRows = rows.sort((a, b) => {
            const aColText = parseFloat(a.querySelector(\`td:nth-child(\${ column + 1 })\`).textContent.trim(), 10);
            const bColText = parseFloat(b.querySelector(\`td:nth-child(\${ column + 1 })\`).textContent.trim(), 10);
      
            return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
        });
      
        // Remove all existing TRs from the table
          while (tBody.firstChild) {
            tBody.removeChild(tBody.firstChild);
        }
      
        // Re-add the newly sorted rows
        tBody.append(...sortedRows);
      
        // Remember how the column is currently sorted
        table.querySelectorAll(\"th\").forEach(th => th.classList.remove(\"th-sort-asc\", \"th-sort-desc\"));
        table.querySelector(\`th:nth-child(\${ column + 1})\`).classList.toggle(\"th-sort-asc\", asc);
        table.querySelector(\`th:nth-child(\${ column + 1})\`).classList.toggle(\"th-sort-desc\", !asc);
      }
      
      document.querySelectorAll(\".table-sortable th\").forEach(headerCell => {
        headerCell.addEventListener(\"click\", () => {
            const tableElement = headerCell.parentElement.parentElement.parentElement;
            const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
            const currentIsAscending = headerCell.classList.contains(\"th-sort-asc\");
      
            sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
        });
      });
    
      </script>"



 echo "<br></br>"
 echo "</body> </HTML>"
}      

createHTML ${csv_file}>${html_file}
