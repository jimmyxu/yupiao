<?php
date_default_timezone_set('Asia/Shanghai');
header('Last-Modified: ' . gmdate('D, d M Y H:i:s', mktime(0, 0, 0)) . ' GMT');;
header('Expires: ' . gmdate('D, d M Y H:i:s', mktime(0, 0, 0) + 24 * 60 * 60 - 1). ' GMT');
$dates = '';
$options = '';
setlocale(LC_TIME, 'zh_CN.UTF-8');
for ($i = 0; $i <= 62; $i++) {
    $offset = time() + $i * 24 * 60 * 60;
    $dates .= date('Y-m-d', $offset) . ',';
    if ($i <= 59) {
        if (($i == @$_GET['D']) || (strftime('%m-%d', $offset) === @$_GET['T'])) {
            $selected = ' selected';
        }
        else {
            $selected = '';
        }
        $options .= "<option value=$i$selected>" . strftime('%m月%d日 %A', $offset) . ' ' . ($i == 0 ? '今天' : "+$i") . '</option>';
    }
}
$dates = rtrim($dates, ',');
?><!doctype html><meta charset=utf-8 /><title>余票查询</title><meta name=viewport content='initial-scale=1.0' /><link rel='shortcut icon' href=favicon.ico /><link rel=stylesheet href=css/style.css /><script src=js/jquery-2.1.4.min.js></script><script src=js/common.js></script><script src=js/yp.js></script><script src=js/jquery.csv2table-0.02-b-4.7.js></script><script>var dates='<?php echo $dates; ?>'.split(',');</script><div><form action=.>发到站<input name=A id=FZ size=8 value='<?php echo htmlspecialchars(@$_GET['A']); ?>' /><input type=button onclick='switchFZDZ();' value='&#x21cc;' tabindex=-1 /><input name=B id=DZ size=8 value='<?php echo htmlspecialchars(@$_GET['B']); ?>' />车次<input name=C id=TC size=8 value='<?php echo htmlspecialchars(@$_GET['C']); ?>' />日期<select name=D id=DATE><?php echo $options; ?></select>多日<input name=S id=DAYS size=8 value='<?php echo @$_GET['S'] ? htmlspecialchars(@$_GET['S']) : '0'; ?>' /><input type=button value=查询余票 id=ypquery_submit /></form></div><div><div id=result_title></div><div id=query_canvas></div><div id=result_canvas></div></div><hr /><small>ご本家様：<a href=http://yupiao.info>YuPiao.info</a> <a href=http://www.miitbeian.gov.cn/ rel=nofollow style=color:grey;>陕ICP备15006889号</a></small>
