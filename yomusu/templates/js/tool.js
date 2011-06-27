/****************
 * WebサービスにPOSTする
 */
function postxml(url, param, func) {
	var xmlHttp = new XMLHttpRequest();
	if (!xmlHttp) {
		alert("あなたのブラウザ、対応してません");
		return false;
	}
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState==4 && xmlHttp.status == 200) {
			func(xmlHttp);
		}
	}
	xmlHttp.open("POST", url, true);
	xmlHttp.send(param);
}

/******************
 * WebサービスからGETする
 */
function readxml(url, param, func) {
	var xmlHttp = new XMLHttpRequest();
	if (!xmlHttp) {
		alert("あなたのブラウザ、対応してません");
		return false;
	}
	xmlHttp.onreadystatechange = function() {
		// readyState = 4(complete)
		// status = httpresponseのこと
		if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
			func(xmlHttp);
		}
	}
	xmlHttp.open("GET", url + "?" + param, true);
	xmlHttp.send("");
}

function html_escape( s ) {
	var  e = document.createElement("div");

	if( typeof e.textContent != "undefined" ) {
		// DOM3(Chrome,Firefox)
		e.textContent = s;
	} else {
		// IE
		e.innerText = s;
	}
	return e.innerHTML
}


function attachOnLoadEvent( func ) {

	if (window.addEventListener) { //for W3C DOM
		window.addEventListener("load", func, false);
	} else if (window.attachEvent) { //for IE
		window.attachEvent("onload", func);
	} else  {
		window.onload = func;
	}
}
