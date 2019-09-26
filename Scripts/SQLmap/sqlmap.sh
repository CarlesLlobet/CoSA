#!/bin/bash

SEGONS=3 # Seconds to wait between requests to see if the process must be killed
TASKS=2 # Number of SQLmap tasks to execute concurrently

SOURCE="${BASH_SOURCE[0]}"
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
TMP=`dirname $0`
PYTHON=/root/AAPT/AAPT/pythonenv/bin/python
SQLMAP=/root/AAPT/AAPT/SQLmap/sqlmap.py

# Test number of parameters
if [[ $# -le 0 ]]; then

    N=`ls -a1 $TMP| grep running | wc -l`
	#Test if there's a sqlmap task running already 
	if (( $N < $TASKS )); then
		#Do a SELECT of the oldest request
		read -d "\n" id type target verbosity level risk depth charset <<< `curl -k -X GET https://localhost:8080/API/SQLmap/get_next/|sed 's/\"//g'|tr "|" "\n"`

		if [[ $id ]]
		then
			#Log parametres
			echo "id = " $id ", type = " $type ", target = " $target ", verbosity = " $verbosity ", level = " $level ", risk = " $risk ", depth = " $depth ", charset = " $charset

            if [[ $type == "HTML" ]]; then
                rm $TMP/.running"$N"
                exit
            fi

			#Create sqlmap.run with the task info and put task to Running state
			touch $TMP/.running"$N"
			curl -k -X PUT -d state=Running https://localhost:8080/API/SQLmap/set_state/$id/

			#Call SQLmap with the params
			$PYTHON $SQLMAP $type "$target" -v $verbosity --level=$level --risk=$risk --crawl=$depth --charset=$charset -a --batch --eta > "$TMP"/sqlmap.results"$N" 2>&1 &
			PID=$!

            while kill -0 $PID
            do
                STATE=`curl -k -X GET https://localhost:8080/API/SQLmap/get_estat/$id/`
			    if [ $STATE == '"Blocked"' ]; then
                    kill -9 $PID
                    curl -k -X GET https://localhost:8080/API/SQLmap/kill/$id/
                    rm $TMP/.running"$N"
                    exit
                fi
                sleep $SECONDS
            done

            $PYTHON $TMP/sql2html.py $TMP/sqlmap.results"$N" > $TMP/sql2html.log

			#Delete sqlmap.run and treat results
			rm $TMP/.running"$N"
			output=`cat "$TMP"/sqlmap.results"$N"`
			echo -e "$output"
			curl -k -X PUT -H "Content-Type:multipart/form-data" -F "file=@"$TMP"/sqlmap.results"$N".html;type=text/plain" https://localhost:8080/API/SQLmap/add_results/$id/
			curl -k -X PUT -H "Content-Type:multipart/form-data" -F "file=@"$TMP"/sqlmap.results"$N";type=text/plain" https://localhost:8080/API/SQLmap/add_report/$id/

			curl -k -X PUT -d state=Finished https://localhost:8080/API/SQLmap/set_state/$id/

			# COMMENTED TO SAVE THE PSQL COMMAND, BECAUSE THE RESULT GOES BY API: output=$(<sqlmap.results)
			#psql -h ip -d DATABASE -U DBUSER -p PORT -tAc 'UPDATE "SQLmap_sqlmap_results" SET output='$output' WHERE id='$id''
		else
			exit
		fi
	else
	    exit
	fi
fi
		
