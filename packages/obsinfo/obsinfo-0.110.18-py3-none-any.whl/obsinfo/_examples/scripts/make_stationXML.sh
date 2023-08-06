#!/bin/bash
OBSINFO_GITLAB_REPOSITORY=www.gitlab.com
OBSINFO_PROJECTPATH=resif/obsinfo
OBSINFO_DATAPATH=$HOME/.local/lib/python3.6/site-packages/obsinfo/_examples/Information_Files:GITLAB/obsinfo/_examples/Information_Files
OBSINFO_VERSION=`obsinfo-print_version`
export OBSINFO_GITLAB_REPOSITORY OBSINFO_PROJECTPATH OBSINFO_DATAPATH OBSINFO_VERSION
obsinfo-makeSTATIONXML $*
