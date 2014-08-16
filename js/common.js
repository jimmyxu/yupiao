
$(document).ready(initialize);

function initialize() {
	$('.nav span').mouseover(function(e) {
		e.currentTarget.style['background-color'] = '#4C4C4C';
	});
	$('.nav span').mouseout(function(e) {
		e.currentTarget.style['background-color'] = '#2d2d2d';
	});
    try{
	init();
    }
    catch(err){}
}

function setCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+encodeURIComponent(value)+expires+"; path=.";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return decodeURIComponent(c.substring(nameEQ.length,c.length));
    }
    return null;
}

function deleteCookie(name) {
    setCookie(name,"",-1);
}
