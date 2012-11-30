<?php
$url = 'http://yupiao.info/api/train/' . explode('/train/', $_SERVER['REQUEST_URI'], 2)[1];

$ch = curl_init($url);
$curl_opt = array();
$curl_opt[CURLOPT_TIMEOUT] = 16;
$curl_opt[CURLOPT_RETURNTRANSFER] = TRUE;
$curl_opt[CURLOPT_HTTP_VERSION] = CURL_HTTP_VERSION_1_1;
$curl_opt[CURLOPT_HEADERFUNCTION] = create_function('$ch, $str',
        'if(strpos($str, "Content-Length:") === FALSE && strpos($str, "Transfer-Encoding:") === FALSE) {
             header($str);
         }
         return strlen($str);');
curl_setopt_array($ch, $curl_opt);
$ret = curl_exec($ch);
curl_close($ch);

header('Content-Length: ' . strlen($ret));
echo $ret;
