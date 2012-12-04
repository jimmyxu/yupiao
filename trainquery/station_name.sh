#!/bin/bash -

cat <<EOF
# vim: set fileencoding=utf-8:

station_name = {
EOF

wget --no-check-certificate -O- https://www.12306.cn/otsweb/js/common/station_name.js | \
sed -e "s/^.\+'@\(.\+\)'.\+$/\1\n/;s/@/\n/g" | \
sed -e "s/^[^|]\+|\([^|]\+\)|\([^|]\+\)|.\+$/'\1': '\2',/"

echo }
