#!/bin/bash -
#
# needs to run daily

cat <<EOF
# vim: set fileencoding=utf-8:

EOF

curl -kvo- -H 'Accept-Encoding: gzip' https://kyfw.12306.cn/otn/resources/js/query/train_list.js | \
    gunzip | \
    $(dirname $0)/train_list.pl
