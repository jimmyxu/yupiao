var DAYS_FORWARD = 20;
function init() {
	if(parseInt(!!($('#FZ')[0].value) + !!($('#DZ')[0].value) + !!$('#TC')[0].value) >= 2) {// 会不会导致兼容性问题？
		YP.doYpQuery();
	}
    try{
        if($('#FZ')[0].value == "" && $('#DZ')[0].value == "") {
            var c = getCookie('lastYP');
            if(c) {
                c = c.split('|');
                if(c.length == 5) {
                    $('#FZ')[0].value = c[0];
                    $('#DZ')[0].value = c[1];
                    $('#TC')[0].value = c[2];
                    var date = new Date(c[3]);
                    var date_forward = new Date();
                    date_forward.setDate(date_forward.getDate() + DAYS_FORWARD);
                    if (date >= new Date() && date <= date_forward) {
                        $('#DATE')[0].value = Math.ceil((date - new Date()) / (1000 * 3600 * 24));
                    }
                    $('#DAYS')[0].value = c[4];
                }
            }
        }
    }
    catch(err){};
	if($('#FZ')[0].value == "" && $('#DZ')[0].value == "") {
		$('#FZ')[0].value = 'BJP';
		$('#DZ')[0].value = 'SHH';
	}
	$('#ypquery_submit').bind('click', YP.doYpQuery);
    // 回车键
    $('#FZ,#DZ,#TC,#DAYS').keypress(function (e) {
        var keyCode = e.keyCode ? e.keyCode : e.which ? e.which : e.charCode; 
        if (keyCode == 13) {
            YP.doYpQuery();
        }
    });
    /*
    window.onhashchange = function(e){
        if (!jsChangingHash){
            console.info(e);
            hashProcess();
        }
    };*/
}

var YP = window.YP = YP || {};
(function() {
	var tableCanvas = null;
	//var csvTitle = "日期,#,车次,发站,到站,出发,到达,历时,商务,特等,动1,动2,高软,软卧,硬卧,软座,硬座,无座,等级";
	var csvTitle = "日期,#,车次,发站,到站,出发,到达,历时,软卧,硬卧,软座,硬座,其他,无座,等级";
	var queryKeys = null;
	var queryDatas = null;
	var queryStatus = null;
	var queryMode = "";
	var FZ, DZ, TC, DT, DAYS;
	YP.doYpQuery = function() {
		csvs = {};
		queryKeys = [];
		queryDatas = {};
		queryStatus = {};
		FZ = $('#FZ')[0].value;
		DZ = $('#DZ')[0].value;
		TC = $('#TC')[0].value;
		DT = parseInt($('#DATE')[0].value);
		DAYS = parseInt($('#DAYS')[0].value);
		if(DAYS + DT > DAYS_FORWARD)
			DAYS = DAYS_FORWARD - DT;
		tableCanvas = $('<div></div>').attr('id', 'table_canvas');
		$('#query_canvas').html("");
		$('#result_canvas').html("").append(tableCanvas);
		if(parseInt(!!FZ + !!DZ + !!TC) < 2) {// 会不会导致兼容性问题？
			alert('查询条件过少，不能查询');
			return;
		}
		setCookie('lastYP', [FZ, DZ, TC, dates[DT], DAYS].join('|'), 30);

		if(FZ && DZ) {
			queryMode = "normal";
			runNormalQuery();
		} else if(!FZ || !DZ) {
			queryMode = "enum";
			DAYS = 0;
			enumStationQuery();
		}
		updateResultTitle(FZ, DZ, TC, DT, DAYS);
		return false;
	}
	function runNormalQuery() {
		for(var i = 0; i <= DAYS; i++) {
			var pos = $('<div></div>').attr('id', 'result' + i).appendTo($('#query_canvas'));
			singleQuery(FZ, DZ, TC, dates[DT + i], i, pos);
		}
	}

	function csvAddLink(csvline) {
		if(!csvline || csvline == '')
			return '';
		var cell = csvline.split(',');
		cell[2] = "<a target=\"_blank\" href=\"http://yupiao.info/train/" + cell[2].split('(')[0] + "/" + cell[0] + "\">" + cell[2] + "</a>";
		function linkStation(station) {
			return "<a target=\"_blank\" href=\"http://yupiao.info/station/" + encodeURI(station) + "/" + cell[0] + "\">" + station + "</a>";
		}

		cell[3] = linkStation(cell[3]);
		cell[4] = linkStation(cell[4]);
		cell[0] = cell[0].substr(5);
		return cell.join(',');
	}

	function enumStationQuery() {
		$.ajax({
            url : "/~jimmy/yp/api/train/" + TC + "/" + dates[DT],
			dataType : "json",
			success : function(train) {
				cur_train = train;
				//console.debug(train);
				if(!train.stop[FZ || DZ]) {
					var msg = TC + "次列车不经过“" + (FZ || DZ) + "”站<br/>";
					msg += "请选择以下沿途车站：" + train.stops.join(',');
					$('#query_canvas').html(msg);
					return;
				}
				if(!DZ) {
					var begini = train.stop[FZ] ? train.stop[FZ].sequence : 0;
					for(var i = begini; i < train.stops.length; i++) {
						var pos = $('<div></div>').attr('id', 'result' + i).appendTo($('#query_canvas'));
						//singleQuery(FZ, train.stops[i], train.stop[train.stops[i]].station_traincode, dates[DT], i, pos); // bugfix@20121218
						singleQuery(FZ, train.stops[i], TC, dates[DT], i, pos);
					}
				} else if(!FZ) {
					var endi = train.stop[DZ] ? train.stop[DZ].sequence - 1 : train.stops.length - 1;
					for(var i = 0; i < endi; i++) {
						var pos = $('<div></div>').attr('id', 'result' + i).appendTo($('#query_canvas'));
						singleQuery(train.stops[i], DZ, train.stop[train.stops[i]].station_traincode, dates[DT], i, pos);
					}
				}
			}
		});
	}

	var MAX_SECONDS = 11;
	function singleQuery(FZ, DZ, TC, dt, delta, pos, requery) {
		var KEY = FZ + "-" + DZ + "-" + TC + "/" + dt;
        try{
            if (TC && cur_train!=null && FZ){
                if (dt ==dates[0]){
                    var now = (Date.now()/1000 /60 + 480) % 1440;
                    var dep_time = cur_train.stop[FZ].dep_time % 1440;
                    if (dep_time < now)
                    {
                        //console.debug(now +','  + dep_time);
                        pos.html([dt,'由',FZ,'开出的',TC,'次列车，开车时间为',parseInt(dep_time / 60), ':', parseInt(dep_time % 60), '，列车已开出，跳过查询'].join(''));
                        return;
                    }
                } 
            }
        }
        catch(err){
        }
		if(!requery) {
			requery = 0;
			queryKeys.push(KEY);
		}
		url = "/~jimmy/yp/api/yp/" + encodeURI(KEY) + "?jsoncallback=?";
		//var url = "http://localhost:4007/api/yp/" + KEY + "?jsoncallback=?";
		var seconds = MAX_SECONDS;
		var countdown = $('<span></span>');
		pos.html("正在查询：" + KEY + "").append(countdown);
		var doCountdown = function() {//retry
			if(queryStatus[KEY]) {
				//console.debug('stopInternal ' + KEY + "-" + requery + "-" + 'seconds:' + seconds);
				return;
			}
			seconds--;
			if(seconds == -1) {
				// init a new query
				singleQuery(FZ, DZ, TC, dt, delta, pos, requery + 1);
			} else if(seconds >= 0) {
				countdown.html(( requery ? ", 正在重新查询(" + requery +  ")" : "") + ", 请等待" + seconds + "秒...");
				setTimeout(doCountdown, 1150)
			}
		};
		setTimeout(doCountdown, 200);
		$.getJSON(url, {}, function(data) {
			if(queryStatus[KEY]) {
				//console.debug('abandonQuery ' + KEY + "-" + requery + "-" + 'seconds:' + seconds);
				return;
			}
		
			if (false && data.data == ""){
				queryStatus[KEY] = true;
				seconds = -100;
				countdown.html("没查询到数据，请检查您的输入。");
				return;
			} 

			queryStatus[KEY] = true;
			seconds = -100;
			pos.html("<!-- -->");

			var csvlines = [];
			var lines = data.data.split(';');
			$.each(lines, function(i, line) {
                if(line == '') return;
				if(queryMode == 'enum') {
					var data = line.split(',');
					data[1] = delta;
					line = data.join(',');
				}
				//line = dt + "," + line;
				line = csvAddLink(line);
				csvlines.push(line);
			});
			var csv = csvlines.join('\n');
			updateResultTable(KEY, csv);
		})
	}

	function updateResultTitle(A, B, TC, DT, DAYS){
		try {
			var date0 = dates[DT];
			var datetitle = date0 + " ";
			if(DAYS) {
				var date1 = dates[DT + DAYS];
				datetitle = date0 + "至" + date1 + " ";
			}
			var tctitle = "";

			if(TC) {
				tctitle = " " + TC + "次列车";
			}
			var A = FZ ? FZ : "沿途各站";
			var B = DZ ? DZ : "沿途各站";
			var fromtotitle = A + " 至 " + B;
			var title = datetitle + tctitle + " " + fromtotitle + " 的剩余火车票额<hr />" ;
			$('#result_title').html(title);
		} catch(e) {
			$('#result_title').html(e);
		}
	}

	function updateResultTable(key, csv) {
		queryDatas[key] = csv;

		var newcsvs = [csvTitle]
		for(var i = 0; i < queryKeys.length; i++) {
			if(queryDatas[queryKeys[i]])
				newcsvs.push(queryDatas[queryKeys[i]]);
		}
		tableCanvas.csv2table(newcsvs.join('\n'));
	}

})();
function switchFZDZ() {
	var A = $('#FZ')[0].value;
	var B = $('#DZ')[0].value;
	$('#FZ')[0].value = B;
	$('#DZ')[0].value = A;
}
