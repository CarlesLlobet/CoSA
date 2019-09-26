#!/bin/bash

TASKS=2 # Number of OpenVAS tasks to execute concurrently

TMP=`dirname $0`
USER=`cat $TMP/../../AAPT/2apt.settings | grep openvas_username | cut -f4 -d\"`
PASSWD=`cat $TMP/../../AAPT/2apt.settings | grep openvas_password | cut -f4 -d\"`
BINDIR=/usr/bin

#Verfifica si ha acabado la tarea anterior
N=`ls -a1 $TMP| grep running | wc -l`
if (( $N > 0 ))
then
	echo "Already running "$N" tasks from the buffer"
	(( COUNTER = $N-1 ))
	echo "Counter value is: "$COUNTER
	while (( $COUNTER >= 0 )); do
        #Reading which task is running
        echo "Testing the: "$COUNTER
        IFS=";" read -r -d "\n" id target ID_TARGET ID_CONFIG ID_TASK ID_TASK_STARTED < $TMP/.running"$COUNTER"
        echo $id", "$target", "$ID_TARGET", "$ID_CONFIG", "$ID_TASK", "$ID_TASK_STARTED
        #Updating how is task
        read state <<< `$BINDIR/omp -u "$USER" -w "$PASSWD" -G "$ID_TASK" | head -1 | awk -F ' ' '{print $2}'`
        echo $state
        if [ "$state" == "Running" ]
        then
            read percentage <<< `$BINDIR/omp -u "$USER" -w "$PASSWD" -G "$ID_TASK" | head -1 | awk -F ' ' '{print $3}'| cut -f1 -d%`
            echo $percentage
	        curl -k -X PUT -d percentage=$percentage https://localhost:8080/API/OpenVAS/set_percentage/$id/
	        STATE=`curl -k -X GET https://localhost:8080/API/OpenVAS/get_estat/$id/`
		    if [ $STATE == '"Blocked"' ]; then
		        STOP_TASK = `$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml=" <stop_task task_id=\"$ID_TASK\"/>"`
		        REMOVE_TASK = `$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml=" <delete_task task_id=\"$ID_TASK\"/>"`
		        rm $TMP/.running"$COUNTER"
		        curl -k -X GET https://localhost:8080/API/OpenVAS/kill/$id/
		        let N-=1
		    fi
        elif [ "$STATE" == "Done" ]
        then
            STATE=`curl -k -X GET https://localhost:8080/API/OpenVAS/get_estat/$id/`
		    if [ $STATE == '"Blocked"' ]; then
		        REMOVE_TASK = `$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml=" <delete_task task_id=\"$ID_TASK\"/>"`
		        curl -k -X GET https://localhost:8080/API/OpenVAS/kill/$id/
		    else
                curl -k -X PUT -d state=Finalitzada https://localhost:8080/API/OpenVAS/set_state/$id/
		    fi
		    rm $TMP/.running"$COUNTER"
		    let N-=1
        else
            echo $state" is not Done nor Running"
        fi
        let COUNTER-=1
    done
else
    echo "No running tasks"
fi
if (( $N < $TASKS ))
then
    echo "Searching new task"
    #Obtaining next target from the buffer

    read next <<< `curl -k -X GET https://localhost:8080/API/OpenVAS/get_next/|sed 's/\"//g'`
    id=`echo $next|cut -f1 -d "|"|tr -d '[[:space:]]'`
    target=`echo $next|cut -f2 -d "|"|tr -d '[[:space:]]'`
    config=`echo $next|cut -f3 -d "|"`
	if [[ $id ]]; then
	    echo "Task found: " $id", "$target", "$config

        #Search for target and if it exists take the id, otherwise create it
        read -d "\n" ID_TARGET aux <<< `$BINDIR/omp -u "$USER" -w "$PASSWD" -T | grep $target|tr " " "\n"`
        if [[ $ID_TARGET ]]; then
            echo "Target already existed"
        else
            #Create the target
            CREATE_TARGET=`$BINDIR/omp -u "$USER" -w "$PASSWD" --xml="<create_target><name>$target</name><hosts>$target</hosts><alive_tests>Consider Alive</alive_tests></create_target>"`
            ID_TARGET=`echo $CREATE_TARGET | awk '{print $2}' FS=" " | awk '{print $2}' FS="="|sed -e 's/"//g'`
        fi
        if [[ $ID_TARGET ]]; then
            echo "Target created:" $ID_TARGET
        fi

        #Select the configuration for the scan
        PARSER_CONFIG=`echo -E $config | sed "s/[ ][ ]*/\\\\\ /g"`
        ID_CONFIG=`$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" -g| sed -n -e'/\s\s'"$PARSER_CONFIG"'$/p' | awk '{print $1}' FS=" "`

        #Search the task and if it exists take the id, otherwise create it
        read -d "\n" name <<< `$BINDIR/omp -u "$USER" -w "$PASSWD" -G |tr -s " "|cut -f3 -d" "| grep $id`
        if [[ $name ]]; then
            echo "Task already exists"
            read -d "\n" ID_TASK aux <<< `$BINDIR/omp -u "$USER" -w "$PASSWD" -G | grep $nom|tr " " "\n"`
        else
            #Create the scan
            CREATE_TASK=`$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml="<create_task><name>$id</name><comment>$target</comment><config id=\"$ID_CONFIG\"/><target id=\"$ID_TARGET\"/></create_task>"`
            ID_TASK=`echo $CREATE_TASK | awk '{print $2}' FS=" " | awk '{print $2}' FS="="|sed -e 's/"//g'`
        fi

        echo "Task created"
        if [[ $ID_TASK ]]; then
            echo "Task created:" $ID_TASK
        fi

        #Execute
        START_TASK=`$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml=" <start_task task_id=\"$ID_TASK\"/>"`
        ID_TASK_STARTED=`echo $START_TASK | awk '{print $6}' FS=" " | sed -n -e 's/.*<report_id>\(.*\)<\/report_id>.*/\1/p'`

        echo "Task executed"
        if [[ $ID_TASK_STARTED ]]; then
            echo "Task executed:" $ID_TASK_STARTED
        fi

        curl -k -X PUT -d state=Running https://localhost:8080/API/OpenVAS/set_state/$id/
        curl -k -X PUT -d report=$ID_TASK_STARTED https://localhost:8080/API/OpenVAS/set_report/$id/

        echo $id";"$target";"$ID_TARGET";"$ID_CONFIG";"$ID_TASK";"$ID_TASK_STARTED > $TMP/.running"$N"
    else
        echo "No task to execute"
    fi
else
    echo "Task limit reached"
fi
exit

