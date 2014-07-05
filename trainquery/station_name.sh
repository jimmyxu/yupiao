#!/bin/bash -

cat <<EOF
# vim: set fileencoding=utf-8:

station_name = {
EOF

wget -O- --no-check-certificate https://kyfw.12306.cn/otn/resources/js/framework/station_name.js | \
sed -e "s/^.\+'@\(.\+\)'.\+$/\1\n/;s/@/\n/g" | \
sed -e "s/^[^|]\+|\([^|]\+\)|\([^|]\+\)|\([^|]\+\)|.\+$/'\1': '\2',/"

echo }
