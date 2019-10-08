#!/bin/bash

TMP=`dirname $0`
USER=`cat $TMP/../../AAPT/aapt.settings | grep openvas_username | cut -f4 -d\"`
PASSWD=`cat $TMP/../../AAPT/aapt.settings | grep openvas_password | cut -f4 -d\"`
BINDIR=/usr/bin

DELETED=`curl -k -X GET http://localhost:8080/API/OpenVAS/get_deleted/`
echo "Django raw tasks: "$DELETED

DELETED=($DELETED)
echo "Django Tasks: ""${DELETED[@]}"

#Get all tasks from OMP
TASKS=`$BINDIR/omp -u "$USER" -w "$PASSWD" -G |tr -s " "|cut -f1,3 -d" "`
echo "OpenVAS Tasks: $TASKS"

for d in "${DELETED[@]}"
do
    #Buscar el ID TASK que te "element" com a nom a dins de "TASKS"
    echo "Searching for deleted task "$d
    ID_TASK=`echo "$TASKS"|grep " $d"|cut -f1 -d" "`
    echo "Found ID_TASK :"$ID_TASK

    if [[ $ID_TASK ]]; then
        echo "Deleting task and calling a kill for the task"
        REMOVE_TASK=`$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml=" <delete_task task_id=\"$ID_TASK\"/>"`
        if [[ $REMOVE_TASK ]]; then
            curl -k -X GET http://localhost:8080/API/OpenVAS/kill/$d/
        else
            echo "Unable to delete task from OpenVAS"
        fi
    else
        echo "Task to delete does not exist in OpenVAS"
    fi
done
