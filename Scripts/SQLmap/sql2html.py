import sys
#I/O paths, take SQLMap STDOUT file from script parameter
stdout_file_path = sys.argv[1]
report_file_path = stdout_file_path + ".html"
#Open STDOUT file in read mode
file_handle_read = open(stdout_file_path,"r")
#Open REPORT file in write mode
file_handle_write = open(report_file_path,"w")
#Initialize HTML report stream
file_handle_write.write("<html xmlns=\"http://www.w3.org/1999/xhtml\" lang=\"en\" xml:lang=\"en\">")
#Flag to know is global audit is OK
cannot_find_injectable_parameter = False
cannot_find_usable_links = False
cannot_connect = False
#Read STDOUT file line by line
execution_traces = []
i = 0
for line in file_handle_read:
    if (line.strip().startswith("[")) and (line.find("[*]") == -1):
        #Check for special message indicating audit global status
        if(line.lower().find("all parameters are not injectable") > -1):
            cannot_find_injectable_parameter = True
        if (line.lower().find("no usable links found") > -1):
            cannot_find_usable_links = True
        if (line.lower().find("Can't connect") > -1):
            cannot_find_usable_links = True
        #Report generation
        line_part = line.strip().split(" ")
        if (line_part[2].lower() == "testing"):
            pass
    else:
        # No te tags de data ni etiqueta al principi
        execution_trace = ""
        count = 0
        while(count < len(line_part)):
            execution_trace = execution_trace + " " + line_part[count]
            count += 1
        execution_traces[i] = execution_trace
        i += 1

#Write global audit stauts line
if(cannot_find_injectable_parameter):
    file_handle_write.write("<h2 class=\"fail\">SQLmap no ha trobat cap par&agrave;metre injectable</h2>")
elif(cannot_find_usable_links):
    file_handle_write.write("<h2 class=\"fail\">SQLmap no ha trobat cap par&agrave;metre amb GET per injectar</h2>")
elif(cannot_find_usable_links):
    file_handle_write.write("<h2 class=\"fail\">SQLmap no s'ha pogut connectar</h2>")
else:
    if i > 0:
        file_handle_write.write(
            "<h2 class=\"found\">SQLmap ha trobat par&agrave;metres injectables i informaci&oacute;</h2>")
        file_handle_write.write("<table id=\"myStyle\">")
        file_handle_write.write("<thead><tr><th scope=\"col\">Descripci&oacute;</th></tr></thead>")
        file_handle_write.write("<tbody>")
        for j in range(i):
            file_handle_write.write("<tr><td>" + execution_traces[j] + "</td></tr>")
        file_handle_write.write("</tbody></table>")
    else:
        file_handle_write.write(
            "<h2 class=\"noFound\">SQLmap ha trobat par&agrave;metres injectables per&ograve; no informaci&oacute;</h2>")
#Close I/O stream
file_handle_write.close()
file_handle_read.close()
#Print some informations
print("Report generated to " + report_file_path)