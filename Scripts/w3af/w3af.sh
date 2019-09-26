#!/bin/bash

SECONDS=3 # Seconds to wait between requests to see if the process must be killed
TASKS=2 # Number of w3af tasks to execute concurrently

SOURCE="${BASH_SOURCE[0]}"
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
TMP=`dirname $0`
PYTHON=/root/AAPT/AAPT/pythonenv/bin/python
W3AF=/root/AAPT/AAPT/w3af/w3af_console

# Test number of parameters
if [[ $# -le 0 ]]; then
    N=`ls -a1 $TMP| grep running | wc -l`
    #Test if there's a w3af task running already
    if (( $N < $TASKS )); then
            #Select the oldest request
            # id|target|target_os|target_framework|profile|login_url|login_username|login_password|login_userfield|login_passwordfield|login_method
            read id target target_os target_framework profile login_url login_username login_password login_userfield login_passwordfield login_method http_domain http_user http_password<<< `curl -k -X GET https://localhost:8080/API/w3af/get_next/|sed 's/\"//g'|tr "|" "\n"`
            if [[ $id ]];then
                #Log parametres
                echo "id = " $id ", target = " $target ", target_os = " $target_os ", target_framework = " $target_framework ", profile = " $profile ", login_url = " $login_url ", login_username = " $login_username ", login_password = " $login_password ", login_userfield = " $login_userfield ", login_passwordfield = " $login_passwordfield ", login_method = " $login_method
                
		#Crear w3af.run amb la info de la task i posar a Running la task
                touch $TMP/.running"$N"
                curl -k -X PUT -d state=Running https://localhost:8080/API/w3af/set_state/$id/

                # Escriure un nou "$TMP"/execute"$N".w3af per executarlo
                echo "# -----------------------------------------------------------------------------------------------------------" > "$TMP"/execute"$N".w3af
                echo "#                               W3AF AUDIT SCRIPT FOR WEB APPLICATION                                         " >> "$TMP"/execute"$N".w3af
                echo "# -----------------------------------------------------------------------------------------------------------" >> "$TMP"/execute"$N".w3af
                echo "# Configure HTTP settings" >> "$TMP"/execute"$N".w3af
                echo "      http-settings" >> "$TMP"/execute"$N".w3af
                echo "      set timeout 30" >> "$TMP"/execute"$N".w3af
                if [[ $http_domain != "buit" && $http_user != "buit" && $http_password != "buit" ]]; then
                    echo "      set basic_auth_user $http_user" >> "$TMP"/execute"$N".w3af
                    echo "      set basic_auth_passwd $http_password" >> "$TMP"/execute"$N".w3af
                    echo "      set basic_auth_domain $http_domain" >> "$TMP"/execute"$N".w3af
                fi
                echo "      back" >> "$TMP"/execute"$N".w3af
                echo "# Configure scanner global behaviors" >> "$TMP"/execute"$N".w3af
                echo "      misc-settings" >> "$TMP"/execute"$N".w3af
                echo "      set max_discovery_time 20" >> "$TMP"/execute"$N".w3af
                echo "      set fuzz_cookies True" >> "$TMP"/execute"$N".w3af
                echo "      set fuzz_form_files True" >> "$TMP"/execute"$N".w3af
                echo "      set fuzz_url_parts True" >> "$TMP"/execute"$N".w3af
                echo "      set fuzz_url_filenames True" >> "$TMP"/execute"$N".w3af
                echo "      back" >> "$TMP"/execute"$N".w3af
                echo "#Define profile to use" >> "$TMP"/execute"$N".w3af
                echo "  profiles" >> "$TMP"/execute"$N".w3af
                echo "  use $profile" >> "$TMP"/execute"$N".w3af
                echo "  back" >> "$TMP"/execute"$N".w3af
                if [[ $login_username != "buit" && $login_password != "buit" ]]; then
                    echo "#Configure target authentication" >> "$TMP"/execute"$N".w3af
                    echo "      auth detailed" >> "$TMP"/execute"$N".w3af
                    echo "      auth config detailed" >> "$TMP"/execute"$N".w3af
                    echo "      set username $login_username" >> "$TMP"/execute"$N".w3af
                    echo "      set password $login_password" >> "$TMP"/execute"$N".w3af
                    if [[ $login_method  != "buit" ]]; then
                        echo "      set method $login_method" >> "$TMP"/execute"$N".w3af
                    fi
                    if [[ $login_url  != "buit" ]]; then
                        echo "      set auth_url $login_url" >> "$TMP"/execute"$N".w3af
                    fi
                    if [[ $login_userfield != "buit" && $login_passwordfield != "buit" ]]; then
                        echo "      set username_field $login_userfield" >> "$TMP"/execute"$N".w3af
                        echo "      set password_field $login_passwordfield" >> "$TMP"/execute"$N".w3af
                    fi
                    echo "      back" >> "$TMP"/execute"$N".w3af
                fi
                echo "#Configure reporting in order to generate an HTML report" >> "$TMP"/execute"$N".w3af
                echo "      plugins" >> "$TMP"/execute"$N".w3af
                echo "      output console, html_file" >> "$TMP"/execute"$N".w3af
                echo "      output config html_file" >> "$TMP"/execute"$N".w3af
                echo "      set output_file $TMP/w3af"$N".results.html" >> "$TMP"/execute"$N".w3af
                echo "      set verbose False" >> "$TMP"/execute"$N".w3af
                echo "      back" >> "$TMP"/execute"$N".w3af
                echo "      output config console" >> "$TMP"/execute"$N".w3af
                echo "      set verbose False" >> "$TMP"/execute"$N".w3af
                echo "      back" >> "$TMP"/execute"$N".w3af
                echo "      back" >> "$TMP"/execute"$N".w3af
                echo "#Set target informations, do a cleanup and run the scan" >> "$TMP"/execute"$N".w3af
                echo "      target" >> "$TMP"/execute"$N".w3af
                echo "      set target $target" >> "$TMP"/execute"$N".w3af
                echo "      set target_os $target_os" >> "$TMP"/execute"$N".w3af
                echo "      set target_framework $target_framework" >> "$TMP"/execute"$N".w3af
                echo "      back" >> "$TMP"/execute"$N".w3af
                echo "      cleanup" >> "$TMP"/execute"$N".w3af
                echo "      start" >> "$TMP"/execute"$N".w3af
                echo "      exit" >> "$TMP"/execute"$N".w3af

                if [[ $target == "HTML" ]]; then
                    rm $TMP/.running"$N"
                    exit
                fi

                #Call w3af with the script
                $PYTHON $W3AF -s "$TMP"/execute"$N".w3af > "$TMP"/w3af"$N".results &
                PID=$!

                while kill -0 $PID
                do
                    STATE=`curl -k -X GET https://localhost:8080/API/w3af/get_state/$id/`
                    if [ $STATE == '"Blocked"' ]; then
                        kill -9 $PID
                        curl -k  -X GET https://localhost:8080/API/w3af/kill/$id/
                        rm $TMP/.running"$N"
			rm "$TMP"/execute"$N".w3af
                        exit
                    fi
                    sleep $SECONDS
                done
                

                #Deleting all the <br> from the html output
                output=`cat "$TMP"/w3af"$N".results.html`
                sed -i 's/<br>//g' "$TMP"/w3af"$N".results.html

		#Copy the full HTML to save it later
		cp $TMP/w3af"$N".results.html $TMP/w3af"$N".results.full

                #Deleting all stylings (bootstrap and others)
                sed -i '/<style>/,/<\/style>/d' "$TMP"/w3af"$N".results.html

		#Deleting also all HTTP responses to see better
		sed -i '/<pre>/,/<\/pre>/d' "$TMP"/w3af"$N".results.html
                echo -e "$output"
                curl  -k -X PUT -H "Content-Type:multipart/form-data" -F "file=@"$TMP"/w3af"$N".results.html;type=text/plain" https://localhost:8080/API/w3af/add_results/$id/
                curl  -k -X PUT -H "Content-Type:multipart/form-data" -F "file=@"$TMP"/w3af"$N".results.full;type=text/plain" https://localhost:8080/API/w3af/add_report/$id/

                curl  -k -X PUT -d state=Finalitzada https://localhost:8080/API/w3af/set_state/$id/
		
		rm "$TMP"/execute"$N".w3af
		rm $TMP/w3af"$N".results.html
		rm $TMP/w3af"$N".results.full
		rm $TMP/w3af"$N".results
                rm $TMP/.running"$N"
            else
                exit
            fi
    else
        exit
    fi
fi
