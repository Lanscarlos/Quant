var GoalCn = "平手,平/半,半球,半/一,一球,一/球半,球半,球半/两,两球,两/两球半,两球半,两球半/三,三球,三/三球半,三球半,三球半/四球,四球,四/四球半,四球半,四球半/五,五球,五/五球半,五球半,五球半/六,六球,六/六球半,六球半,六球半/七,七球,七/七球半,七球半,七球半/八,八球,八/八球半,八球半,八球半/九,九球,九/九球半,九球半,九球半/十,十球".split(",");
var GoalCn2 = ["0", "0/0.5", "0.5", "0.5/1", "1", "1/1.5", "1.5", "1.5/2", "2", "2/2.5", "2.5", "2.5/3", "3", "3/3.5", "3.5", "3.5/4", "4", "4/4.5", "4.5", "4.5/5", "5", "5/5.5", "5.5", "5.5/6", "6", "6/6.5", "6.5", "6.5/7", "7", "7/7.5", "7.5", "7.5/8", "8", "8/8.5", "8.5", "8.5/9", "9", "9/9.5", "9.5", "9.5/10", "10", "10/10.5", "10.5", "10.5/11", "11", "11/11.5", "11.5", "11.5/12", "12", "12/12.5", "12.5", "12.5/13", "13", "13/13.5", "13.5", "13.5/14", "14"];
function Goal2GoalCn(goal) { //数字盘口转汉汉字	
    if (goal == null || goal + "" == "")
        return "";
    else {
        if (goal > 10 || goal < -10) return goal + "球";
        if (goal >= 0) return GoalCn[parseInt(goal * 4)];
        else return "<font color='red'>*</font>" + GoalCn[Math.abs(parseInt(goal * 4))];
    }
}
function Goal2GoalCn2(goal) {
    if (goal == "")
        return "";
    else {
        if (goal > 14) return goal + "球";
        return GoalCn2[parseInt(goal * 4)];
    }
}
function Hashtable() {
    this._hash = new Object();
    this.add = function (key, value) {
        if (typeof (key) != "undefined") {
            this._hash[key] = typeof (value) == "undefined" ? null : value;
            return true;
        }
        else
            return false;
    }
    this.remove = function (key) { delete this._hash[key]; }
    this.keys = function () {
        var keys = new Array();
        for (var key in this._hash) {
            keys.push(key);
        }
        return keys;
    }
    this.count = function () { var i = 0; for (var k in this._hash) { i++; } return i; }
    this.items = function (key) { return this._hash[key]; }
    this.contains = function (key) {
        return typeof (this._hash[key]) != "undefined";
    }
    this.clear = function () { for (var k in this._hash) { delete this._hash[k]; } }
}
function setType(t) {
    var objLet = document.getElementById("checkLet");
    var objEu = document.getElementById("checkEu");
    var objTotal = document.getElementById("checkTotal");
    if (objLet.checked && objEu.checked && objTotal.checked) {
        if (t == 1)
            objLet.checked = false;
        else if (t == 2)
            objTotal.checked = false;
        else if (t == 3)
            objEu.checked = false;
        alert("同时只能选择两种类型！");
    }
    if (!objLet.checked && !objEu.checked && !objTotal.checked) {
        if (t == 1)
            objLet.checked = true;
        else if (t == 2)
            objTotal.checked = true;
        else if (t == 3)
            objEu.checked = true;
    }
    var num = 0;
    if (objLet.checked) num++;
    if (objEu.checked) num++;
    if (objTotal.checked) num++;
    if (num == 1) return;
    else {
        Config.haveLetGoal = objLet.checked ? 1 : 0;
        Config.haveEurope = objEu.checked ? 1 : 0;
        Config.haveTotal = objTotal.checked ? 1 : 0;
        Config.writeCookie();
        maketable();
        //Config.setStates();
    }
}
var scoreOddsHttp = zXmlHttp.createRequest();
var oldXml = "";
var ieNum = 0;
try {
    if (document.all && typeof (document.documentMode) != "undefined")
        ieNum = document.documentMode;
}
catch (e) {
    ieNum = 0;
}
function LoadLiveFile() {
    var allDate = document.getElementById("allDate");
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.charset = "gb2312";
    s.src = "//live.titan007.com/jsData/" + getFilePath() + scheduleID + ".js?" + Date.parse(new Date());
    allDate.removeChild(allDate.firstChild);
    allDate.appendChild(s, "script");
}
function getxml() {
    //var temp = "," + AnalysisObj.list.join(',');
    //if (temp.indexOf(',0,') == -1) return;
    if (matchState == -1) return;
    if (typeof (sOdds) == "undefined") return;
    if (typeof (sOdds[0][0]) == "undefined") return;
    if (getSpanHour(matchTime) <= 3) {//3小时后算完场
        if (document.getElementById("porlet_0").style.display != "none") {
            scoreOddsHttp.open("get", "/xml/" + getFilePath() + "ch_" + scheduleID + ".xml?" + Date.parse(new Date()), true);
            scoreOddsHttp.onreadystatechange = refresh;
            scoreOddsHttp.send(null);
        }
        window.setTimeout("getxml()", 6000);
    }
}
function getFilePath() {
    return scheduleID.toString().substr(0, 2) + "/" + scheduleID.toString().substr(2, 2) + "/";
}
function refresh() {
    try {
        if (scoreOddsHttp.readyState != 4 || (scoreOddsHttp.status != 200 && scoreOddsHttp.status != 0)) return;
        if (oldXml == scoreOddsHttp.responseText) return
        oldXml = scoreOddsHttp.responseText;
        if (scoreOddsHttp.responseXML == null) return;
        var root = scoreOddsHttp.responseXML.documentElement;
        var D = new Array();
        var odds;
        //var obj = document.getElementById("oddsTbody"); //oddsTable
        var obj = document.getElementById("oddsTable").tBodies[0]
        //var tr2 = obj.rows[obj.rows.length - 1];
        //var tr1 = null;
        //if (obj.rows.length > 4)
        //    tr1 = obj.rows[obj.rows.length - 2];
        var oddsLocHalf = "6,8,18,20,30,32".split(',');
        var oddsLocFull = "12,14,24,26,36,38".split(',');
        for (var i = 0; i < root.childNodes.length; i++) {
            if (root.childNodes[i].nodeName != "c3"||root.childNodes[i].textContent=="") continue;
            if (document.all && parseInt(ieNum) < 10)
                D = root.childNodes[i].text.split(";");
            else
                D = root.childNodes[i].textContent.split(";");
			if(D="")
            for (var j = 0; j < D.length; j++) {
                var data = D[j].split(',');
                var odds2 = D[j].split(',');
                var isOneRow = (parseInt(data[39]) > 1 || parseInt(data[39]) == -1); //中场后没有半场赔率
                var tr1, tr2;
                var key = (data[0] == "早餐" ? 1 : data[0] == "未开场" ? 2 : 3) + "_" + data[1] + "_" + data[2] + "_" + data[39];
                if (scoreStateHt.contains(key)) {
                    var arrHt = scoreStateHt.items(key).split(',');
                    var trLoc = parseInt(arrHt[0]);// + parseInt(arrh[1]);
                    tr2 = obj.rows[trLoc];
                    var odds = sOdds[parseInt(arrHt[2])];
                    if (!isOneRow)
                        tr2 = obj.rows[trLoc + 1];
                    tr1 = obj.rows[trLoc];

                    for (var k = 0; k < oddsLocHalf.length; k++) {
                        if (typeof (odds[oddsLocHalf[k]]) != "undefined" && typeof (data[oddsLocHalf[k]]) != "undefined") {
                            if (parseFloat(odds[oddsLocHalf[k]]) > parseFloat(data[oddsLocHalf[k]])) data[oddsLocHalf[k]] = "<span class=greedBg>" + data[oddsLocHalf[k]] + "</span>";
                            else if (parseFloat(odds[oddsLocHalf[k]]) < parseFloat(data[oddsLocHalf[k]])) data[oddsLocHalf[k]] = "<span class=redBg>" + data[oddsLocHalf[k]] + "</span>";
                        }
                    }
                    for (var k = 0; k < oddsLocFull.length; k++) {
                        if (typeof (odds[oddsLocFull[k]]) != "undefined" && typeof (data[oddsLocFull[k]]) != "undefined") {
                            if (parseFloat(odds[oddsLocFull[k]]) > parseFloat(data[oddsLocFull[k]])) data[oddsLocFull[k]] = "<span class=greedBg>" + data[oddsLocFull[k]] + "</span>";
                            else if (parseFloat(odds[oddsLocFull[k]]) < parseFloat(data[oddsLocFull[k]])) data[oddsLocFull[k]] = "<span class=redBg>" + data[oddsLocFull[k]] + "</span>";
                        }
                    }
                    var h1 = 3, f1 = 9, h2 = 15, f2 = 21; //让球、进球数
                    if (Config.haveLetGoal == 0) {//进球数、欧赔
                        h1 = 15;
                        f1 = 21;
                        h2 = 27;
                        f2 = 33;
                    }
                    else {
                        if (Config.haveEurope == 1) {//让球、欧赔
                            h2 = 27;
                            f2 = 33;
                        }
                    }
                    window.setTimeout("restoreOddsColor(" + D.length + ")", 30000);
                    if (!isOneRow && data[0] != '') {
                        tr1.cells[0].innerHTML = (data[39] == 1 && parseInt(data[0].toString()) > 45 ? "45" : data[0]);
                        for (var k = 0; k < 6; k++) {
                            var num = h1 + k;
                            if (data[num] == '') continue;
                            if (k == 1 || k == 4) {
                                var goal = (h1 == 3 ? Goal2GoalCn(data[num]) : Goal2GoalOU(data[num])); //3 让 15 进球数
                                tr1.cells[k + 3].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;";
                            }
                            else
                                tr1.cells[k + 3].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? data[num] : "&nbsp;";
                        }
                        for (var k = 0; k < 6; k++) {
                            var num = h2 + k;
                            if (data[num] == '') continue;
                            if (k == 1 || k == 4) {
                                var goal = (h2 == 15 ? Goal2GoalOU(data[num]) : data[num]); //15 进球数 27 欧
                                tr1.cells[k + 9].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;";
                            }
                            else
                                tr1.cells[k + 9].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? data[num] : "&nbsp;";
                        }
                    }
                    if (isOneRow && data[0] != '')
                        tr2.cells[0].innerHTML = data[0];
                    for (var k = 0; k < 6; k++) {
                        var count = isOneRow ? 3 : 1;
                        var num = f1 + k;
                        if (data[num] == '') continue;
                        if (k == 1 || k == 4) {
                            var goal = (h1 == 3 ? Goal2GoalCn(data[num]) : Goal2GoalOU(data[num])); //3 让 15 进球数
                            tr2.cells[k + count].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;";
                        }
                        else
                            tr2.cells[k + count].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? data[num] : "&nbsp;";
                    }
                    for (var k = 0; k < 6; k++) {
                        var count = isOneRow ? 9 : 7;
                        var num = f2 + k;
                        if (data[num] == '') continue;
                        if (k == 1 || k == 4) {
                            var goal = (h2 == 15 ? Goal2GoalOU(data[num]) : data[num]); //15 进球数 27 欧
                            tr2.cells[k + count].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;";
                        }
                        else
                            tr2.cells[k + count].innerHTML = typeof (data[num]) != "undefined" && String(data[num]) != '' ? data[num] : "&nbsp;";
                    }
                }

                else {
                    //if (tr2.cells.length == 15) {
                    //    for (var k = 0; k < 6; k++) {
                    //        var num = (k >= 3 ? 9 : 6);
                    //        tr2.cells[num + k].bgColor = "#ECFBFB";
                    //    }
                    //}
                    //else {
                    //    for (var k = 0; k < 6; k++) {
                    //        var num = (k >= 3 ? 7 : 4);
                    //        tr2.cells[num + k].bgColor = "#ECFBFB";
                    //        num = (k >= 3 ? 9 : 6);
                    //        tr1.cells[num + k].bgColor = "#ECFBFB";
                    //    }
                    //}
                    var fra = document.createDocumentFragment();
                    var newTr0 = document.createElement("tr");
                    newTr0.setAttribute("odds", D[j]);
                    newTr0.setAttribute("bgcolor", "#FFFFFF");
                    //newTr0.innerHTML = oneRow(D[j], false, 1);
                    newTr0 = oneRowTd(data, 1, newTr0);
                    fra.appendChild(newTr0);
                    var key = (data[0] == "早餐" ? 1 : data[0] == "未开场" ? 2 : 3) + "_" + data[1] + "_" + data[2] + "_" + data[39];
                    var keys = scoreStateHt.keys();
                    var arrHt = scoreStateHt.items(keys[keys.length - 1]).split(',');
                    scoreStateHt.add(key, (parseInt(arrHt[0]) + parseInt(arrHt[1])) + "," + ((data[39] > 1 || data[39] == -1) ? 1 : 2) + "," + (parseInt(arrHt[2]) + 1));
                    if (!isOneRow) {
                        var newTr1 = document.createElement("tr");
                        newTr1.setAttribute("bgcolor", "#FFFFFF");
                        //newTr1.innerHTML = oneRow(D[j], false, 2);
                        newTr1 = oneRowTd(data, 2, newTr1);
                        fra.appendChild(newTr1);
                    }
                    obj.appendChild(fra);
                    //取消前一条数据的封盘
                    var odds = sOdds[parseInt(arrHt[2])];//取前一条数据
                    sOdds[sOdds.length] = data;//保存新数据
                    var oldTrStart = parseInt(arrHt[0]);
                    var oldTrRows = parseInt(arrHt[1]);
                    isOneRow = oldTrRows == 1;
                    tr2 = obj.rows[oldTrStart];
                    if (!isOneRow)
                        tr2 = obj.rows[oldTrStart + 1];
                    tr1 = obj.rows[oldTrStart];
                    if (!isOneRow && odds[0] != '') {
                        for (var k = 3; k < 6; k++) {
                            var num = Config.h1 + k;
                            if (odds[num] != '') {
                                tr1.cells[k + 3].setAttribute("class", "");
                                tr1.cells[k + 3].innerHTML = getShowOdds(odds, num, k, 1, false);
                            }
                            num = Config.h2 + k;
                            if (odds[num] != '') {
                                tr1.cells[k + 9].setAttribute("class", "");
                                tr1.cells[k + 9].innerHTML = getShowOdds(odds, num, k, 2, false);
                            }
                        }
                    }
                    for (var k = 3; k < 6; k++) {
                        var count = isOneRow ? 3 : 1;
                        var num = Config.f1 + k;
                        if (odds[num] != '') {
                            tr2.cells[k + count].setAttribute("class", "");
                            tr2.cells[k + count].innerHTML = getShowOdds(odds, num, k, 1, false);
                        }
                        count = isOneRow ? 9 : 7;
                        num = Config.f2 + k;
                        if (odds[num] != '') {
                            tr2.cells[k + count].setAttribute("class", "");
                            tr2.cells[k + count].innerHTML = getShowOdds(odds, num, k, 2, false);
                        }
                    }
                }
            }
        }
    } catch (e) { }
}
function getSpanHour(date) {
    var now = new Date();
    var span = now.getTime() - date.getTime()
    var days = span / (24 * 3600 * 1000)
    return days * 24;
}
function restoreOddsColor(num) {
    var obj = document.getElementById("oddsTable");
    if (obj == null) return;
    var tr1 = obj.rows[obj.rows.length - 2];
    var tr2 = obj.rows[obj.rows.length - 1];
    if (num > 1) {
        var tr3 = obj.rows[obj.rows.length - 4];
        var tr4 = obj.rows[obj.rows.length - 3];
    }
    for (var i = 0; i < tr1.cells.length; i++) {
        tr1.cells[i].innerHTML = tr1.cells[i].innerHTML.toLowerCase().replace(/<span class=redBg>/g, "").replace(/<span class=greedBg>/g, "").replace(/<span class=\"redbg\">/g, "").replace(/<span class=\"greenbg\">/g, "").replace(/<\/span>/g, "");
    }
    for (var i = 0; i < tr2.cells.length; i++) {
        tr2.cells[i].innerHTML = tr2.cells[i].innerHTML.toLowerCase().replace(/<span class=redBg>/g, "").replace(/<span class=greedBg>/g, "").replace(/<span class=\"redbg\">/g, "").replace(/<span class=\"greenbg\">/g, "").replace(/<\/span>/g, "");
    }
    if (num > 1) {
        for (var i = 0; i < tr3.cells.length; i++) {
            tr3.cells[i].innerHTML = tr3.cells[i].innerHTML.toLowerCase().replace(/<span class=redBg>/g, "").replace(/<span class=greedBg>/g, "").replace(/<span class=\"redbg\">/g, "").replace(/<span class=\"greenbg\">/g, "").replace(/<\/span>/g, "");
        }
        for (var i = 0; i < tr4.cells.length; i++) {
            tr4.cells[i].innerHTML = tr4.cells[i].innerHTML.toLowerCase().replace(/<span class=redBg>/g, "").replace(/<span class=greedBg>/g, "").replace(/<span class=\"redbg\">/g, "").replace(/<span class=\"greenbg\">/g, "").replace(/<\/span>/g, "");
        }
    }
}

function isInsert(oldOdds, newOdds) {
    var reg = new RegExp("^\d+$");
    var oldScores = parseInt(oldOdds[1]) + parseInt(oldOdds[2]);
    var newScores = parseInt(newOdds[1]) + parseInt(newOdds[2]);
    if ((oldOdds[0] == "早餐" && newOdds[0] == "未开场") || (oldOdds[0] == "未开场" && reg.test(newOdds[0])) || (reg.test(oldOdds[0])) && newOdds[0] == "中场" || (oldOdds[0] == "中场" && reg.test(newOdds[0])) || oldScores != newScores)
        return true;
    else
        return false;
}
var scoreStateHt = new Hashtable();
function maketable() {
    var html = new Array();
    if (typeof (sOdds) == "undefined") return;
    if (sOdds.length == 0 || typeof (sOdds[0][0]) == "undefined") return;
    html.push('<div class="content">');
    html.push('<table class="zsTable" width="100%" align="center" cellpadding="0" cellspacing="0" id="oddsTable">');
    html.push('<tbody id="oddsTbody">');
    html.push('<tr bgcolor="#FFFFFF">');
    html.push('<td rowspan="2" align="center" bgcolor="#F0F0FF">时间</td>');
    html.push('<td rowspan="2" align="center" bgcolor="#F0F0FF">比分</td>');
    html.push('<td rowspan="2" align="center" bgcolor="#F0F0FF" class="rightline">半全场</td>');
    html.push('<td height="20" colspan="6" align="center" bgcolor="#FCEAAB"><strong>' + (Config.haveLetGoal == 1 ? '亚让' : '进球数') + '</strong></td>');
    html.push('<td colspan="6" align="center" bgcolor="#FCEAAB" class="leftline"><strong>' + (Config.haveEurope == 1 ? '欧指' : '进球数') + '</strong></td>');
    html.push('</tr>');
    html.push('<tr bgcolor="#FFFFFF">');
    html.push('<td height="20" colspan="3" align="center">开盘</td>');
    html.push('<td colspan="3" align="center" bgcolor="#FFFFD0">即时</td>');
    html.push('<td colspan="3" align="center" class="leftline">开盘</td>');
    html.push('<td colspan="3" align="center" bgcolor="#FFFFD0">即时</td>');
    html.push('</tr>');
    var trStart = 2;
    for (var i = 0; i < sOdds.length; i++) {
        html.push(oneRow(sOdds[i], i == sOdds.length - 1, 0));
        var arrs = sOdds[i];
        var key = (arrs[0] == "早餐" ? 1 : arrs[0] == "未开场" ? 2 : 3) + "_" + arrs[1] + "_" + arrs[2] + "_" + arrs[39];
        scoreStateHt.add(key, trStart + "," + ((arrs[39] > 1 || arrs[39] == -1) ? 1 : 2) + "," + i);
        trStart += ((arrs[39] > 1 || arrs[39] == -1) ? 1 : 2);
    }
    html.push('</tbody></table>');
    //html.push('<div class="discription"><div>说明：</div>');
    //html.push('背景 <span style="background-color:#ECFBFB">&nbsp;&nbsp;&nbsp;&nbsp;</span> 表示历史数据, &nbsp;&nbsp;');
    //html.push('背景 <span style="background-color:#FFFFD0">&nbsp;&nbsp;&nbsp;&nbsp;</span> 表示最新数据</div>');
    //html.push('</div>');
    html.push('</div>');
    document.getElementById("socreOdds").innerHTML = html.join("");
    Config.getCookie();
}
function oneRow(data, isEnd, t) {
    var arrs = data;
    if (t > 0)
        arrs = data.split(',');
    var html = new Array();
    var score = (arrs[0] == "早餐" || arrs[0] == "未开场" ? "&nbsp;" : arrs[1] + ":" + arrs[2]);
    var bgColor = (arrs[0] == "早餐" ? "#349F00" : arrs[0] == "未开场" ? "#FF3333" : "#0066FF");
    var h1 = 3, f1 = 9, h2 = 15, f2 = 21; //让球、进球数
    if (Config.haveLetGoal == 0) {//进球数、欧赔
        h1 = 15;
        f1 = 21;
        h2 = 27;
        f2 = 33;
    }
    else {
        if (Config.haveEurope == 1) {//让球、欧赔
            h2 = 27;
            f2 = 33;
        }
    }
    var isOneRow = (arrs[39] > 1 || arrs[39] == -1);
    if (t == 0)
        html.push('<tr bgcolor="#FFFFFF"' + (isEnd ? " odds='" + data + "'" : "") + '>');
    if (t == 0 || t == 1) {
        html.push('<td width="50"' + (isOneRow ? '' : ' rowspan="2"') + ' align="center" bgcolor="' + bgColor + '" class="write">' + (arrs[39] == 1 && arrs[0] != '' && parseInt(arrs[0].toString()) > 45 ? "45" : arrs[0]) + '</td>');
        html.push('<td width="50"' + (isOneRow ? '' : ' rowspan="2"') + ' align="center" bgcolor="#FFFFFF" class="red_number">' + score + '</td>');
        html.push('<td width="50" height="24" align="center" bgcolor="#FFFFFF" class="rightline">' + (isOneRow ? '全场' : '半场') + '</td>');
        for (var i = 0; i < 6; i++) {
            var num = h1 + i;
            if (isOneRow)
                num = f1 + i;
            var color = (i < 3 ? "#FFFFFF" : isEnd ? "#ECFBFB" : "#ECFBFB");
            var goal = arrs[num];
            if (i == 1 || i == 4)
                var goal = (h1 == 3 ? Goal2GoalCn(arrs[num]) : Goal2GoalOU(arrs[num])); //3 让 15 进球数
            html.push('<td width="' + (i == 1 || i == 4 ? "70" : "40") + '" align="center" bgcolor="' + color + '">' + (typeof (arrs[num]) != "undefined" && String(arrs[num]) != '' ? goal : "&nbsp;") + '</td>');
        }
        for (var i = 0; i < 6; i++) {
            var num = h2 + i;
            if (isOneRow)
                num = f2 + i;
            var color = (i < 3 ? "#FFFFFF" : isEnd ? "#ECFBFB" : "#ECFBFB");
            var goal = arrs[num];
            if (i == 1 || i == 4)
                goal = (h2 == 15 ? Goal2GoalOU(arrs[num]) : arrs[num]); //15 进球数 27 欧
            html.push('<td width="' + (i == 1 || i == 4 ? "70" : i == 5 ? 42 : "40") + '" align="center"' + (i == 0 ? ' class="leftline"' : '') + (color != "" ? ' bgcolor="' + color + '"' : '') + '>' + (isEnd && i >= 3 ? "<span class=\"isnew\">" : "") + (typeof (arrs[num]) != "undefined" && String(arrs[num]) != '' ? goal : "&nbsp;") + (isEnd && i > 3 ? "</span>" : "") + '</td>');
        }
    }
    if (t == 0) {
        html.push('</tr>');
        if (!isOneRow)
            html.push('<tr bgcolor="#FFFFFF">');
    }
    if (!isOneRow) {
        if (t == 0 || t == 2) {
            html.push('<td height="24" align="center" class="rightline">全场</td>');
            for (var i = 0; i < 6; i++) {
                var num = f1 + i;
                var color = (i < 3 ? "#FFFFFF" : isEnd ? "#ECFBFB" : "#ECFBFB");
                var goal = arrs[num];
                if (i == 1 || i == 4)
                    goal = (h1 == 3 ? Goal2GoalCn(arrs[num]) : Goal2GoalOU(arrs[num])); //3 让 15 进球数
                html.push('<td align="center"' + (color != "" ? ' bgcolor="' + color + '"' : '') + '>' + (typeof (arrs[num]) != "undefined" && String(arrs[num]) != '' ? goal : "&nbsp;") + '</td>');
            }
            for (var i = 0; i < 6; i++) {
                var num = f2 + i;
                var color = (i < 3 ? "#FFFFFF" : isEnd ? "#ECFBFB" : "#ECFBFB");
                var goal = arrs[num];
                if (i == 1 || i == 4)
                    goal = (h2 == 15 ? Goal2GoalOU(arrs[num]) : arrs[num]); //15 进球数 27 欧
                html.push('<td align="center"' + (i == 0 ? ' class="leftline"' : '') + (color != "" ? ' bgcolor="' + color + '"' : '') + '>' + (isEnd && i >= 3 ? "<span class=\"isnew\">" : "") + (typeof (arrs[num]) != "undefined" && String(arrs[num]) != '' ? goal : "&nbsp;") + (isEnd && i > 3 ? "</span>" : "") + '</td>');
            }
        }
    }
    if (t == 0 && !isOneRow)
        html.push('</tr>');
    return html.join("");
}
function oneRowTd(data, t, tr) {
    var score = (data[0] == "早餐" || data[0] == "未开场" ? "&nbsp;" : data[1] + ":" + data[2]);
    var bgColor = (data[0] == "早餐" ? "#349F00" : data[0] == "未开场" ? "#FF3333" : "#0066FF");
    var h1 = 3, f1 = 9, h2 = 15, f2 = 21; //让球、进球数
    if (Config.haveLetGoal == 0) {//进球数、欧赔
        h1 = 15;
        f1 = 21;
        h2 = 27;
        f2 = 33;
    }
    else {
        if (Config.haveEurope == 1) {//让球、欧赔
            h2 = 27;
            f2 = 33;
        }
    }
    var isOneRow = (data[39] > 1 || data[39] == -1);
    var attrNameList = "";
    var attrValList = "";
    if (t == 1) {
        attrNameList = "width," + (isOneRow ? '' : 'rowspan,') + "align,bgcolor,class";
        attrValList = "50," + (isOneRow ? '' : '2,') + "center," + bgColor + ",write";
        tr.appendChild(createTd(attrNameList, attrValList, data[0]));
        attrNameList = "width," + (isOneRow ? '' : 'rowspan,') + "align,bgcolor,class";
        attrValList = "50," + (isOneRow ? '' : '2,') + "center,#FFFFFF,red_number";
        tr.appendChild(createTd(attrNameList, attrValList, score));
        attrNameList = "width,height,align,bgcolor,class";
        attrValList = "50,24,center,#FFFFFF,rightline";
        tr.appendChild(createTd(attrNameList, attrValList, isOneRow ? '全场' : '半场'));
        for (var i = 0; i < 6; i++) {
            var num = h1 + i;
            if (isOneRow)
                num = f1 + i;
            var color = (i < 3 ? "#FFFFFF" : "#ECFBFB");
            var goal = data[num];
            if (i == 1 || i == 4)
                var goal = (h1 == 3 ? Goal2GoalCn(data[num]) : Goal2GoalOU(data[num])); //3 让 15 进球数
            attrNameList = "width,align,bgcolor,class";
            attrValList = (i == 1 || i == 4 ? "70" : "40") + ",center," + color + ",rightline";
            tr.appendChild(createTd(attrNameList, attrValList, (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;")));
            //html.push('<td width="' + (i == 1 || i == 4 ? "70" : "40") + '" align="center" bgcolor="' + color + '">' + (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;") + '</td>');
        }
        for (var i = 0; i < 6; i++) {
            var num = h2 + i;
            if (isOneRow)
                num = f2 + i;
            var color = (i < 3 ? "#FFFFFF" : "#ECFBFB");
            var goal = data[num];
            if (i == 1 || i == 4)
                goal = (h2 == 15 ? Goal2GoalOU(data[num]) : data[num]); //15 进球数 27 欧
            attrNameList = "width,align," + (i == 0 ? "class," : "") + (color != "" ? "bgcolor" : "");
            attrValList = (i == 1 || i == 4 ? "70" : i == 5 ? 42 : "40") + ",center," + (i == 0 ? "leftline," : "") + (color != "" ? color : "");
            tr.appendChild(createTd(attrNameList, attrValList, (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;")));
            //html.push('<td width="' + (i == 1 || i == 4 ? "70" : i == 5 ? 42 : "40") + '" align="center"' + (i == 0 ? ' class="leftline"' : '') + (color != "" ? ' bgcolor="' + color + '"' : '') + '>' + (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;") + '</td>');
        }
    }
    else if (t == 2) {
        attrNameList = "height,align,class";
        attrValList = "24,center,rightline";
        tr.appendChild(createTd(attrNameList, attrValList, '全场'));
        for (var i = 0; i < 6; i++) {
            var num = f1 + i;
            var color = (i < 3 ? "#FFFFFF" : "#ECFBFB");
            var goal = data[num];
            if (i == 1 || i == 4)
                goal = (h1 == 3 ? Goal2GoalCn(data[num]) : Goal2GoalOU(data[num])); //3 让 15 进球数
            attrNameList = "align," + (color != "" ? "bgcolor" : "");
            attrValList = "center," + (color != "" ? color : "");
            tr.appendChild(createTd(attrNameList, attrValList, (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;")));
            //html.push('<td align="center"' + (color != "" ? ' bgcolor="' + color + '"' : '') + '>' + (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;") + '</td>');
        }
        for (var i = 0; i < 6; i++) {
            var num = f2 + i;
            var color = (i < 3 ? "#FFFFFF" : "#ECFBFB");
            var goal = data[num];
            if (i == 1 || i == 4)
                goal = (h2 == 15 ? Goal2GoalOU(data[num]) : data[num]); //15 进球数 27 欧
            attrNameList = "align," + (i == 0 ? "class," : "") + (color != "" ? "bgcolor" : "");
            attrValList = "center," + (i == 0 ? "leftline," : "") + (color != "" ? color : "");
            tr.appendChild(createTd(attrNameList, attrValList, (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;")));
            // html.push('<td align="center"' + (i == 0 ? ' class="leftline"' : '') + (color != "" ? ' bgcolor="' + color + '"' : '') + '>' + (typeof (data[num]) != "undefined" && String(data[num]) != '' ? goal : "&nbsp;") + '</td>');
        }
    }
    return tr;
}
function createTd(attrNameList, attrValList, txt) {
    var arrName = attrNameList.split(',');
    var arrVal = attrValList.split(',');
    var attributeList = "";
    try {
        for (var i = 0; i < arrName.length; i++) {
            attributeList += " " + arrName[i] + "='" + arrVal[i] + "'";
        }
        var td = document.createElement("<td" + attributeList + "></td>");
        td.innerHTML = txt;
        return td;
    } catch (e) {
        var td = document.createElement("td");
        for (var i = 0; i < arrName.length; i++) {
            td.setAttribute(arrName[i], arrVal[i]);
        }
        td.innerHTML = txt;
        return td;
    }
}