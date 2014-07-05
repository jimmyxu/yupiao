#!/bin/bash -
#
# needs to run daily

cat <<EOF
# vim: set fileencoding=utf-8:

EOF

wget -O- --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js | \
sed -e 's/^var //' -e 's/},{/},\n{/g' | \
sed -e 's/{"station_train_code":"\([^(]\+\)([^-]\+-[^)]\+)","train_no":"\([^"]\+\)"}/"\1": "\2"/g' | \
sed -e 's/".":\[//g' -e 's/\]//g'
