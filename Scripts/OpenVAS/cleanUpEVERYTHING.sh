#!/bin/bash

USER=`cat ../../AAPT/2apt.settings | grep openvas_username | cut -f4 -d\"`
PASSWD=`cat ../../AAPT/2apt.settings | grep openvas_password | cut -f4 -d\"`
BINDIR=/usr/bin

#Pillar totes les tasks de OMP
TASKS=`$BINDIR/omp -u "$USER" -w "$PASSWD" -G |tr -s " "|cut -f1 -d" "`
echo "OpenVAS Tasks: "$TASKS

for t in $TASKS
do

    ID_TASK=`echo "$t"`
    echo "Found ID_TASK :"$ID_TASK

    if [[ $ID_TASK ]]; then
        echo "Deleting task"
        REMOVE_TASK=`$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml=" <delete_task task_id=\"$ID_TASK\"/>"`
        if [[ $REMOVE_TASK ]]; then
            echo "Deleted successfully task "$ID_TASK
        else
            echo "Unable to delete the task "$ID_TASK
        fi
    else
        echo "No tasks to delete in OpenVAS"
    fi
done

#Get all targets from OMP
TARGETS=`$BINDIR/omp -u "$USER" -w "$PASSWD" -T |tr -s " "|cut -f1 -d" "`
echo "OpenVAS Targets: "$TARGETS

for t in $TARGETS
do
    ID_TARGET=`echo "$t"`
    echo "Found ID_TARGET :"$ID_TARGET

    if [[ $ID_TARGET ]]; then
        echo "Deleting target"
        REMOVE_TARGET=`$BINDIR/omp --pretty-print -u "$USER" -w "$PASSWD" --xml=" <delete_target target_id=\"$ID_TARGET\"/>"`
        if [[ $REMOVE_TARGET ]]; then
            echo "Deleted successfully target: "$ID_TARGET
        else
            echo "Unable to delete the target: "$ID_TASK
        fi
    else
        echo "No target to delete in OpenVAS"
    fi
done
