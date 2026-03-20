var zXml = {
    useActiveX: (typeof ActiveXObject != "undefined"),
    useXmlHttp: (typeof XMLHttpRequest != "undefined")
};

zXml.ARR_XMLHTTP_VERS = ["MSXML2.XmlHttp.6.0", "MSXML2.XmlHttp.3.0"];

function zXmlHttp() { }

zXmlHttp.createRequest = function () {
    if (zXml.useXmlHttp) return new XMLHttpRequest();

    if (zXml.useActiveX)  //IE < 7.0 = use ActiveX
    {
        if (!zXml.XMLHTTP_VER) {
            for (var i = 0; i < zXml.ARR_XMLHTTP_VERS.length; i++) {
                try {
                    new ActiveXObject(zXml.ARR_XMLHTTP_VERS[i]);
                    zXml.XMLHTTP_VER = zXml.ARR_XMLHTTP_VERS[i];
                    break;
                } catch (oError) { }
            }
        }
        if (zXml.XMLHTTP_VER) return new ActiveXObject(zXml.XMLHTTP_VER);
    }
    alert("对不起，您的电脑不支持 XML 插件，请安装好或升级浏览器。");
};
var panlu, overUnder, result;
if (location.href.toLowerCase().indexOf("cn") != -1) {
    panlu = ["", "<font color=green>输</font>", "<font color=blue>走</font>", "<font color=red>赢</font>"];
    overUnder = ["<font color=green>小</font>", "<font color=blue>走</font>", "<font color=red>大</font>"];
    result = ["<font color=green>负</font>", "<font color=blue>平</font>", "<font color=red>胜</font>"];
}
else {
    panlu = ["", "<font color=green>輸</font>", "<font color=blue>走</font>", "<font color=red>贏</font>"];
    overUnder = ["<font color=green>小</font>", "<font color=blue>走</font>", "<font color=red>大</font>"];
    result = ["<font color=green>負</font>", "<font color=blue>平</font>", "<font color=red>勝</font>"];
}
function filter(str) {
    var pattern = /[`~!@#$^&*=|{}':;',\\\[\]\.<>\/?~！@#￥……&*（）——|{}【】'；：""'。，、？]/g;
    return str.replace(pattern, "");
}
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) {
        var str = filter(decodeURI(r[2]));
        return str;
    }
    return null;
}
var CompanyName = new Array(13);
CompanyName[3] = "Crow*";
CompanyName[1] = "澳*";
CompanyName[8] = "36*";
CompanyName[12] = "易胜*";
CompanyName[4] = "立*";
function getCookie(name) {
    var cname = name + "=";
    var dc = document.cookie;
    if (dc.length > 0) {
        begin = dc.indexOf(cname);
        if (begin != -1) {
            begin += cname.length;
            end = dc.indexOf(";", begin);
            if (end == -1) end = dc.length;
            return dc.substring(begin, end);
        }
    }
    return null;
}
function delCookie(name)//删除cookie 
{
    var exp = new Date();
    exp.setTime(exp.getTime() - 1000 * 3600);
    var cval = getCookie(name);
    if (cval != null && cval != "null")
        document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
}
function writeCookie(name, value) {
    delCookie(name);
    var expire = "";
    var hours = 365;
    expire = new Date((new Date()).getTime() + hours * 3600000);
    expire = ";path=/;expires=" + expire.toGMTString() + ";domain=" + getDoMain();
    document.cookie = name + "=" + value + expire; //escape(
}
function getDoMain() {
    var arrDoms = location.href.split("/")[2].split(".");
    var isNum = /^\d+$/;
    if (isNum.test(arrDoms[1]))
        return arrDoms[0] + "." + arrDoms[1] + "." + arrDoms[2] + "." + arrDoms[3].split(":")[0];
    else
        return arrDoms[1] + "." + arrDoms[2];
}
lang = location.href.toLowerCase().indexOf("cn") != -1 ? 0 : location.href.toLowerCase().indexOf("sb") != -1 ? 2 : 1;
//定义Config
var Config = new Object();
Config.oldOrNew = 1;
Config.acid_v = 3;
Config.atype_v = 1;
Config.scid_v = 0;
Config.stype_v = 1;
Config.acid_hn = 3;
Config.atype_hn = 1;
Config.scid_hn = 0;
Config.stype_hn = 1;
Config.acid_an = 3;
Config.atype_an = 1;
Config.scid_an = 0;
Config.stype_an = 1;
Config.haveLetGoal = 1;
Config.haveTotal = 1;
Config.haveEurope = 0;
Config.isHalf = 0;
Config.isSimple = (lang == 0 || lang == 2);
Config.teamInfoUrl = '"//zq.titan007.com/' + (lang == 1 ? "big" : "cn") + '/team/Summary/{0}.html"';
Config.scoreDetailUrl = '"//live.titan007.com/detail/{0}' + (lang == 0 ? "cn" : lang == 1 ? "" : "sb") + '.htm"';
Config.vipAsiaUrl = '"//vip.titan007.com/AsianOdds_n.aspx?id={0}&l=' + (lang == 1 ? "1" : "0") + '"';
Config.isHalf_h = 0;
Config.isHalf_a = 0;
Config.isHalf_h2 = 0;
Config.isHalf_a2 = 0;
Config.neutrality_h2 = 1;
Config.neutrality_a2 = 1;

Config.getCookie = function () {
    var Cookie = getCookie("fAnalyCookie");
    if (Cookie == null) Cookie = "";
    var Cookie = Cookie.split("^");
    if (Cookie.length != 16) writeCookie("fAnalyCookie", null);
    else {
        this.oldOrNew = parseInt(Cookie[0]);
        this.acid_v = parseInt(Cookie[1]);
        this.atype_v = parseInt(Cookie[2]);
        this.scid_v = parseInt(Cookie[3]);
        this.stype_v = parseInt(Cookie[4]);
        this.acid_hn = parseInt(Cookie[5]);
        this.atype_hn = parseInt(Cookie[6]);
        this.scid_hn = parseInt(Cookie[7]);
        this.stype_hn = parseInt(Cookie[8]);
        this.acid_an = parseInt(Cookie[9]);
        this.atype_an = parseInt(Cookie[10]);
        this.scid_an = parseInt(Cookie[11]);
        this.stype_an = parseInt(Cookie[12]);
        this.haveLetGoal = parseInt(Cookie[13]);
        this.haveTotal = parseInt(Cookie[14]);
        this.haveEurope = parseInt(Cookie[15]);       
    }
}
Config.setStates = function () {
    try {
        $_Our("hSelect_v").value = this.acid_v;
        $_Our("hType_v").value = this.atype_v;
        $_Our("sSelect_v").value = this.scid_v;
        $_Our("sType_v").value = this.stype_v;

        $_Our("hSelect_hn").value = this.acid_hn;
        $_Our("hType_hn").value = this.atype_hn;
        $_Our("sSelect_hn").value = this.scid_hn;
        $_Our("sType_hn").value = this.stype_hn;

        $_Our("hSelect_an").value = this.acid_an;
        $_Our("hType_an").value = this.atype_an;
        $_Our("sSelect_an").value = this.scid_an;
        $_Our("sType_an").value = this.stype_an;
        $_Our("checkLet").checked = (this.haveLetGoal == 1);
        $_Our("checkEu").checked = (this.haveEurope == 1);
        $_Our("checkTotal").checked = (this.haveTotal == 1);

        $_Our("sSelect_h").value = this.isHalf_h;
        $_Our("sSelect_a").value = this.isHalf_a;
        $_Our("sSelect_h2").value = this.isHalf_h2;
        $_Our("sSelect_a2").value = this.isHalf_a2;
    }
    catch (e) { }
}
Config.writeCookie = function () {
    var value = this.oldOrNew + "^" + this.acid_v + "^" + this.atype_v + "^" + this.scid_v + "^" + this.stype_v + "^" + this.acid_hn + "^" + this.atype_hn + "^" + this.scid_hn + "^" + this.stype_hn + "^" + this.acid_an + "^" + this.atype_an + "^" + this.scid_an + "^" + this.stype_an + "^" + this.haveLetGoal + "^" + this.haveTotal + "^" + this.haveEurope;
    writeCookie("fAnalyCookie", value);
}
var GoalCn = ["平手", "平手/半球", "半球", "半球/一球", "一球", "一球/球半", "球半", "球半/两球", "两球", "两球/两球半", "两球半", "两球半/三球", "三球", "三球/三球半", "三球半", "三球半/四球", "四球", "四球/四球半", "四球半", "四球半/五球", "五球", "五球/五球半", "五球半", "五球半/六球", "六球", "六球/六球半", "六球半", "六球半/七球", "七球", "七球/七球半", "七球半", "七球半/八球", "八球", "八球/八球半", "八球半", "八球半/九球", "九球", "九球/九球半", "九球半", "九球半/十球", "十球", "十球/十球半", "十球半", "十球半/十一球", "十一球", "十一球/十一球半", "十一球半", "十一球半/十二球", "十二球", "十二球/十二球半", "十二球半", "十二球半/十三球", "十三球", "十三球/十三球半", "十三球半", "十三球半/十四球", "十四球"];
var GoalOU = ["0", "0/0.5", "0.5", "0.5/1", "1", "1/1.5", "1.5", "1.5/2", "2", "2/2.5", "2.5", "2.5/3", "3", "3/3.5", "3.5", "3.5/4", "4", "4/4.5", "4.5", "4.5/5", "5", "5/5.5", "5.5", "5.5/6", "6", "6/6.5", "6.5", "6.5/7", "7", "7/7.5", "7.5", "7.5/8", "8", "8/8.5", "8.5", "8.5/9", "9", "9/9.5", "9.5", "9.5/10", "10", "10/10.5", "10.5", "10.5/11", "11", "11/11.5", "11.5", "11.5/12", "12", "12/12.5", "12.5", "12.5/13", "13", "13/13.5", "13.5", "13.5/14", "14"];
var GoalOU2 = ["0", "0/-0.5", "-0.5", "-0.5/-1", "-1", "-1/-1.5", "-1.5", "-1.5/-2", "-2", "-2/-2.5", "-2.5", "-2.5/-3", "-3", "-3/-3.5", "-3.5", "-3.5/-4", "-4", "-4/-4.5", "-4.5", "-4.5/-5", "-5", "-5/-5.5", "-5.5", "-5.5/-6", "-6", "-6/-6.5", "-6.5", "-6.5/-7", "-7", "-7/-7.5", "-7.5", "-7.5/-8", "-8", "-8/-8.5", "-8.5", "-8.5/-9", "-9", "-9/-9.5", "-9.5", "-9.5/-10", "-10"];
function Goal2GoalCn(goal) { //handicap conversion
    if (goal.toString() == "")
        return "";
    else {
        if (goal >= 0) return GoalCn[parseInt(goal * 4)];
        else return "受让" + GoalCn[Math.abs(parseInt(goal * 4))];
    }
}

function Goal2GoalOU(goal) {
    if (typeof (goal) == "undefined")
        return "";
    if (goal.toString() == "")
        return "";
    if (goal >= 0) return GoalOU[parseInt(goal * 4)];
    else return GoalOU2[Math.abs(parseInt(goal * 4))];
}
function $_Our(s) { return document.getElementById(s); }
function $$_Our(n) { return document.getElementsByName(n); }
String.prototype.format = function () {
    var val = this.toString();
    for (var a = 0, i = 0; a < arguments.length; a++) {
        if (arguments[a] instanceof Array) {
            for (var j = 0; j < arguments[a].length; j++) {
                val = val.replace(new RegExp("\\{" + i++ + "\\}", "g"), arguments[a][j]);
            }
        } else {
            val = val.replace(new RegExp("\\{" + i++ + "\\}", "g"), arguments[a]);
        }
    }
    return val;
}
var oXmlHttp = zXmlHttp.createRequest();
var oldOddsData = "";
var oddstimer;
function loadData() {
    try {
        oXmlHttp.open("get", "/analysis/odds/" + scheduleID + ".htm?" + Date.parse(new Date()), false);
        oXmlHttp.onreadystatechange = function () {
            if (oXmlHttp.readyState == 4 && oXmlHttp.status == 200) {
                if (oXmlHttp.responseText != "") {
                    $_Our("iframeA").innerHTML = oXmlHttp.responseText;
                    oldOddsData = oXmlHttp.responseText
                    try { oddsComp(); } catch (e) { }
                }
            }
        };
        oXmlHttp.send(null);
    }
    catch (e) { }
    if (getSpanHour(matchTime) <= 3 && document.getElementById("porlet_1").style.display != "none") //3小时后算完场
    {
        window.clearTimeout(oddstimer);
        oddstimer = window.setTimeout("loadData()", 30000);
    }
}
function init_league(id) {
    var html = [];
    var t = "<input type=\"checkbox\" name=\"" + id + "_l\" id=\"{0}_" + id + "\" checked=\"checked\" onclick=\"t_onclick(this.parentElement.id);\" /><label for=\"{0}_" + id + "\">{1}</label>";
    var data = [];
    switch (id) {
        case 'v': data = v_data;
            break;
        case 'hn':
        case 'h': data = h_data;
            break;
        case 'an':
        case 'a': data = a_data;
            break;
        case 'h2': data = h2_data;
            break;
        case 'a2': data = a2_data;
            break;
    }
    if (id == "h2" || id == "a2") {
        var hasNeutrality = false;
        for (var k in data) {
            if (data[k][5].toString().indexOf("(中)") != -1) hasNeutrality = true;
            if (html.join("").indexOf(">" + data[k][2] + "<") < 0) html.push(t.format(data[k][1], data[k][2]));
        }
        if (hasNeutrality)
            html.push(t.format("999", "中立场"));
    }
    else {
        for (var k in data) {
            if (html.join("").indexOf(">" + data[k][2] + "<") < 0) html.push(t.format(data[k][1], data[k][2]));
        }
    }
    $_Our(id + "_l").innerHTML = html.join("");
}

function init(id, count) {
    var data = [];
    var chks = $$_Our(id + "_l");
    switch (id) {
        case 'v': data = v_data;
            break;
        case 'hn':
        case 'h': data = h_data;
            break;
        case 'an':
        case 'a': data = a_data;
            break;
        case 'h2': data = h2_data;
            break;
        case 'a2': data = a2_data;
            break;
    }
    newdata = [];
    var tempCount = 1;
    for (var i = 0; i < data.length; i++) {
        //if (id == 'v' && $_Our(id + '_t').checked && (data[i][6] == h2h_home || data[i][5].toString().indexOf("(中)") != -1)) continue;
        //if (id == 'hn' && $_Our(id + '_t').checked && (data[i][4] != h2h_home || data[i][5].toString().indexOf("(中)") != -1)) continue;
        //if (id == 'an' && $_Our(id + '_t').checked && (data[i][6] != h2h_away || data[i][5].toString().indexOf("(中)") != -1)) continue;
        if (id == 'v' && $_Our(id + '_t').checked && data[i][6] == h2h_home) continue;
        if (id == 'hn' && $_Our(id + '_t').checked && data[i][4] != h2h_home) continue;
        if (id == 'an' && $_Our(id + '_t').checked && data[i][6] != h2h_away) continue;
        if (id == 'h2' && Config.neutrality_h2 == 0 && data[i][5].toString().indexOf("(中)") != -1) continue;
        if (id == 'a2' && Config.neutrality_a2 == 0 && data[i][5].toString().indexOf("(中)") != -1) continue;
        if (tempCount > 30) break;
        var f1 = 0;
        for (var j = 0; j < chks.length; j++)
            if (data[i][1] == chks[j].id.substr(0, chks[j].id.indexOf('_')) && chks[j].checked == false) { f1 = 1; break };
        if (f1 == 1) continue;
        newdata.push(data[i]);
        tempCount++;
    }
    var c = count ? count : newdata.length > 10 ? 10 : newdata.length;
    if (id == 'v' || id.indexOf('n') != -1)
        init_vs(id, c);
    else
        init_vs2(id, c);

    if (!count)
        init_select(id, c);
}
function s_onchange(id, count) {
    init(id.substr(0, id.indexOf('_')), count)
}
function t_onclick(id) {
    if (id == "h2_l" && $_Our('999_h2') != null)
        Config.neutrality_h2 = ($_Our('999_h2').checked == true ? 1 : 0);
    if (id == "a2_l" && $_Our('999_a2') != null)
        Config.neutrality_a2 = ($_Our('999_a2').checked == true ? 1 : 0);
    init(id.substr(0, id.indexOf('_')));
}
function getDataArray(id, scheID) {
    var retVal = [];
    var data = [];
    switch (id) {
        case 'v': data = v_data;
            break;
        case 'hn':
        case 'h': data = h_data;
            break;
        case 'an':
        case 'a': data = a_data;
            break;
        case 'h2': data = h2_data;
            break;
        case 'a2': data = a2_data;
            break;
    }
    for (var i = 0; i < data.length; i++) {
        if (parseInt(data[i][15]) == scheID) {
            retVal = data[i];
            break;
        }
    }
    return retVal;
}
function changeHalfOrFull(id, obj) {
    
    if (Config.oldOrNew == 1) {
        Config.isHalf = obj.value;
        showOdds_h(id, 1);
    }
    else {
        switch (id) {
            case "h": Config.isHalf_h = obj.value; break;
            case "a": Config.isHalf_a = obj.value; break;
            case "h2": Config.isHalf_h2 = obj.value; break;
            case "a2": Config.isHalf_a2 = obj.value; break;
        }
        showOldDataOdds(id);
    }
        
}
function showOdds_h(id, t) {
    //var url = "<a href=\"//vip.titan007.com/AsianOdds_n.aspx?id={0}\" target=\"_blank\">{1}</a>";
    var trlist = $_Our("table_" + id).getElementsByTagName("tr");
    //    var num = $_Our(id + "_s").value;
    var num = 0, numBig = 0;
    var awin = 0, big = 0, win = 0, draw = 0, loss = 0, singleNum = 0;
    var count = (newdata.length > 0 && newdata[0].length <= 16) || newdata.length == 0 ? 0 : 1;
    for (var i = 0; i < trlist.length; i++) {
        if (trlist[i].getAttribute("index") != null) {
            trlist[i].cells[5 + count].innerHTML = "";
            trlist[i].cells[6 + count].innerHTML = "";
            trlist[i].cells[7 + count].innerHTML = "";
            trlist[i].cells[12 + count].innerHTML = "";
            trlist[i].cells[13 + count].innerHTML = "";
        }
    }
    if (t == 1) {
        switch (id) {
            case "v":
                Config.acid_v = parseInt($_Our("hSelect_" + id).value);
                Config.atype_v = parseInt($_Our("hType_" + id).value);
                break;
            case "hn":
                Config.acid_hn = parseInt($_Our("hSelect_" + id).value);
                Config.atype_hn = parseInt($_Our("hType_" + id).value);
                break;
            case "an":
                Config.acid_an = parseInt($_Our("hSelect_" + id).value);
                Config.atype_an = parseInt($_Our("hType_" + id).value);
                break;
        }
        Config.writeCookie();
    }
    var varcompayid = id == "v" ? Config.acid_v : id === "hn" ? Config.acid_hn : Config.acid_an;
    var hType = id == "v" ? Config.atype_v : id === "hn" ? Config.atype_hn : Config.atype_an;
    if (t == 0) {
        $_Our("hSelect_" + id).value = varcompayid;
        $_Our("hType_" + id).value = hType;
    }

    for (var i = 0; i < Vs_hOdds.length; i++) {
        var odds = Vs_hOdds[i];
        var tr = $_Our("tr" + id + "_" + odds[0]);
        if (tr == null) continue;
        if (varcompayid != parseInt(odds[1])) continue;
        var strIds = tr.getAttribute("index");
        if (strIds == null || strIds == '') continue;
        //var scheduleArr = getDataArray(id, parseInt(odds[0]));
        var strScore = tr.cells[3].innerHTML.replace(/<.+?>/gim, '');
        var allFullScore = strScore.split('(')[0].split('-');
        var allHalfScore = strScore.split('(')[1].replace(')', '').split('-');
        var arrIds = strIds.split(',');
        var result1 = -2;
        var result2 = -2;
        var oddsLoc = Config.isHalf == "1" ? 8 : 0;
        var arrScore = Config.isHalf == "1" ? allHalfScore : allFullScore;
        //var scoreResult = getScoreResult(parseInt(arrScore[0]), parseInt(arrScore[1]), parseInt(arrIds[0]), id);
        //win += (scoreResult == 1 ? 1 : 0);
        //draw += (scoreResult == 0 ? 1 : 0);
        //loss += (scoreResult == -1 ? 1 : 0);
        //if ((parseInt(arrScore[0]) + parseInt(arrScore[1]) + 2) % 2 > 0) singleNum++;
        if (hType == 1) {
            if (odds[6 + oddsLoc] != "") {
                num++;
                result1 = getResult(parseFloat(odds[6 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]), parseInt(arrIds[0]), id);
                if (result1 == 1)
                    awin++;
                tr.cells[5 + count].innerHTML = odds[5 + oddsLoc];
                tr.cells[6 + count].innerHTML = "<a href=" + (Config.vipAsiaUrl.format(odds[0])) + " target=\"_blank\">" + Goal2GoalCn(parseFloat(odds[6 + oddsLoc])) + "</a>";// url.format(odds[0], Goal2GoalCn(parseFloat(odds[6 + oddsLoc])));
                tr.cells[7 + count].innerHTML = odds[7 + oddsLoc];
            }
            if (odds[9 + oddsLoc] != "") {
                numBig++;
                result2 = getTotalResult(parseFloat(odds[9 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]));
                if (result2 == 1)
                    big++;
            }
        } else {
            if (odds[3 + oddsLoc] != "") {
                num++;
                result1 = getResult(parseFloat(odds[3 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]), parseInt(arrIds[0]), id);
                if (result1 == 1)
                    awin++;
                tr.cells[5 + count].innerHTML = odds[2 + oddsLoc];
                tr.cells[6 + count].innerHTML = "<a href=" + (Config.vipAsiaUrl.format(odds[0])) + " target=\"_blank\">" + Goal2GoalCn(parseFloat(odds[3 + oddsLoc])) + "</a>";//url.format(odds[0], Goal2GoalCn(parseFloat(odds[3 + oddsLoc])));
                tr.cells[7 + count].innerHTML = odds[4 + oddsLoc];
            }
            if (odds[8 + oddsLoc] != "") {
                numBig++;
                result2 = getTotalResult(parseFloat(odds[8 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]));
                if (result2 == 1)
                    big++;
            }
        }
        //tr.cells[11 + count].innerHTML = Config.isHalf == "1" ? result[scheduleArr[19] + 1] : result[scheduleArr[12] + 1];
        tr.cells[12 + count].innerHTML = panlu[result1 + 2];
        tr.cells[13 + count].innerHTML = (result2 > -2 ? overUnder[result2 + 1] : "");
    }
    var data = [];
    switch (id) {
        case 'v': data = v_data;
            break;
        case 'hn':
        case 'h': data = h_data;
            break;
        case 'an':
        case 'a': data = a_data;
            break;
        case 'h2': data = h2_data;
            break;
        case 'a2': data = a2_data;
            break;
    }
    for (var i = 0; i < data.length; i++) {
        var odds = data[i];
        var tr = $_Our("tr" + id + "_" + odds[15]);
        if (tr == null) continue;
        var strIds = tr.getAttribute("index");
        if (strIds == null || strIds == '') continue;
        //if (tr.style.display != "") continue;
        var strScore = tr.cells[3].innerHTML.replace(/<.+?>/gim, '');
        var allFullScore = strScore.split('(')[0].split('-');
        var allHalfScore = strScore.split('(')[1].replace(')', '').split('-');
        var arrIds = strIds.split(',');
        var oddsLoc = Config.isHalf == "1" ? 8 : 0;
        var arrScore = Config.isHalf == "1" ? allHalfScore : allFullScore;
        var scoreResult = getScoreResult(parseInt(arrScore[0]), parseInt(arrScore[1]), parseInt(arrIds[0]), id);
        win += (scoreResult == 1 ? 1 : 0);
        draw += (scoreResult == 0 ? 1 : 0);
        loss += (scoreResult == -1 ? 1 : 0);
        if ((parseInt(arrScore[0]) + parseInt(arrScore[1]) + 2) % 2 > 0) singleNum++;
        tr.cells[11 + count].innerHTML = result[scoreResult + 1];
    }
    try {
        $_Our("awin_" + id).innerHTML = getPreHtml((num > 0 ? Math.floor(awin / num * 1000) / 10 : 0), 1);// (num > 0 ? Math.floor(awin / num * 1000) / 10 : 0) + "%";
        $_Our("big_" + id).innerHTML = getPreHtml((numBig > 0 ? Math.floor(big / numBig * 1000) / 10 : 0), 1);//(numBig > 0 ? Math.floor(big / numBig * 1000) / 10 : 0) + "%";
        $_Our("win_" + id).innerHTML = win;
        $_Our("draw_" + id).innerHTML = draw;
        $_Our("loss_" + id).innerHTML = loss;
        $_Our("winPre_" + id).innerHTML = getPreHtml((Math.floor(win / (win + draw + loss) * 1000) / 10), 1);//(Math.floor(win / (win + draw + loss) * 1000) / 10) + "%";
        $_Our("single_" + id).innerHTML = getPreHtml((Math.floor(singleNum / (win + draw + loss) * 1000) / 10), 2);//(Math.floor(singleNum / (win + draw + loss) * 1000) / 10) + "%";
    }
    catch (ex) {

    }
}

function showOldDataOdds(id) {
    var isHalf = 0;
    var hType = 1;//是否终盘
    var varcompayid = 3;
    var num = 0, numBig = 0;
    var awin = 0, big = 0, win = 0, draw = 0, loss = 0, singleNum = 0;
    switch (id) {
        case "h": isHalf = Config.isHalf_h; break;
        case "a": isHalf = Config.isHalf_a; break;
        case "h2": isHalf = Config.isHalf_h2; break;
        case "a2": isHalf = Config.isHalf_a2; break;
    }
    var trlist = $_Our("table_" + id).getElementsByTagName("tr");
    for (var i = 0; i < trlist.length; i++) {
        if (trlist[i].getAttribute("index") != null) {
            trlist[i].cells[7].innerHTML = "";
            trlist[i].cells[8].innerHTML = "";
            trlist[i].cells[9].innerHTML = "";
        }
    }
    for (var i = 0; i < Vs_hOdds.length; i++) {
        var odds = Vs_hOdds[i];
        var tr = $_Our("tr" + id + "_" + odds[0]);
        if (tr == null) continue;
        if (varcompayid != parseInt(odds[1])) continue;
        var strIds = tr.getAttribute("index");
        if (strIds == null || strIds == '') continue;        
        var strScore = tr.cells[5].innerHTML.replace(/<.+?>/gim, '');
        var allFullScore = strScore.split('(')[0].split('-');
        var allHalfScore = strScore.split('(')[1].replace(')', '').split('-');
        var arrIds = strIds.split(',');
        var result1 = -2;
        var result2 = -2;
        var oddsLoc = isHalf == "1" ? 8 : 0;
        var arrScore = isHalf == "1" ? allHalfScore : allFullScore;

        if (hType == 1) {
            if (odds[6 + oddsLoc] != "") {
                num++;
                result1 = getResult(parseFloat(odds[6 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]), parseInt(arrIds[0]), id);
                if (result1 == 1)
                    awin++;
                tr.cells[3].innerHTML = "<a href=" + (Config.vipAsiaUrl.format(odds[0])) + " target=\"_blank\">" + Goal2GoalCn(parseFloat(odds[6 + oddsLoc])) + "</a>";
            }
            if (odds[9 + oddsLoc] != "") {
                numBig++;
                result2 = getTotalResult(parseFloat(odds[9 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]));
                if (result2 == 1)
                    big++;
            }
        } else {
            if (odds[3 + oddsLoc] != "") {
                num++;
                result1 = getResult(parseFloat(odds[3 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]), parseInt(arrIds[0]), id);
                if (result1 == 1)
                    awin++;
                tr.cells[3].innerHTML = "<a href=" + (Config.vipAsiaUrl.format(odds[0])) + " target=\"_blank\">" + Goal2GoalCn(parseFloat(odds[3 + oddsLoc])) + "</a>";
            }
            if (odds[8 + oddsLoc] != "") {
                numBig++;
                result2 = getTotalResult(parseFloat(odds[8 + oddsLoc]), parseInt(arrScore[0]), parseInt(arrScore[1]));
                if (result2 == 1)
                    big++;
            }
        }

        tr.cells[8].innerHTML = panlu[result1 + 2];
        tr.cells[9].innerHTML = (result2 > -2 ? overUnder[result2 + 1] : "");
    }
    var data = [];
    switch (id) {
        case 'v': data = v_data;
            break;
        case 'hn':
        case 'h': data = h_data;
            break;
        case 'an':
        case 'a': data = a_data;
            break;
        case 'h2': data = h2_data;
            break;
        case 'a2': data = a2_data;
            break;
    }
    for (var i = 0; i < data.length; i++) {
        var odds = data[i];
        var tr = $_Our("tr" + id + "_" + odds[15]);
        if (tr == null) continue;
        var strIds = tr.getAttribute("index");
        if (strIds == null || strIds == '') continue;
        //if (tr.style.display != "") continue;
        var strScore = tr.cells[5].innerHTML.replace(/<.+?>/gim, '');
        var allFullScore = strScore.split('(')[0].split('-');
        var allHalfScore = strScore.split('(')[1].replace(')', '').split('-');
        var arrIds = strIds.split(',');
        var oddsLoc = isHalf == "1" ? 8 : 0;
        var arrScore = isHalf == "1" ? allHalfScore : allFullScore;
        var scoreResult = getScoreResult(parseInt(arrScore[0]), parseInt(arrScore[1]), parseInt(arrIds[0]), id);
        win += (scoreResult == 1 ? 1 : 0);
        draw += (scoreResult == 0 ? 1 : 0);
        loss += (scoreResult == -1 ? 1 : 0);
        if ((parseInt(arrScore[0]) + parseInt(arrScore[1]) + 2) % 2 > 0) singleNum++;
        tr.cells[7].innerHTML = result[scoreResult + 1];
    }
    try {
        $_Our("awin_" + id).innerHTML = getPreHtml((num > 0 ? Math.floor(awin / num * 1000) / 10 : 0), 1);// (num > 0 ? Math.floor(awin / num * 1000) / 10 : 0) + "%";
        $_Our("big_" + id).innerHTML = getPreHtml((numBig > 0 ? Math.floor(big / numBig * 1000) / 10 : 0), 1);//(numBig > 0 ? Math.floor(big / numBig * 1000) / 10 : 0) + "%";
        $_Our("win_" + id).innerHTML = win;
        $_Our("draw_" + id).innerHTML = draw;
        $_Our("loss_" + id).innerHTML = loss;
        $_Our("winPre_" + id).innerHTML = getPreHtml((Math.floor(win / (win + draw + loss) * 1000) / 10), 1);//(Math.floor(win / (win + draw + loss) * 1000) / 10) + "%";
        $_Our("single_" + id).innerHTML = getPreHtml((Math.floor(singleNum / (win + draw + loss) * 1000) / 10), 2);//(Math.floor(singleNum / (win + draw + loss) * 1000) / 10) + "%";
    }
    catch (ex) {

    }
}
function getScoreResult(hScore, gScore, hId, id) {
    var result = 0;
    if (hScore > gScore)
        result = 1;
    else if (hScore == gScore)
        result = 0;
    else
        result = -1;
    if ((id.indexOf('h') != -1 || id.indexOf('v') != -1) && hId != h2h_home)
        result = result == 1 ? -1 : result == -1 ? 1 : result;
    if (id.indexOf('a') != -1 && hId != h2h_away)
        result = result == 1 ? -1 : result == -1 ? 1 : result;
    return result;
}
function getResult(goal, hScore, gScore, hId, id) {
    var result = -2;
    if (goal >= 0) {
        if (hScore - goal > gScore)
            result = 1;
        else if (hScore - goal == gScore)
            result = 0;
        else
            result = -1;
    }
    else {//主队的结果,所以调转
        if (gScore - Math.abs(goal) > hScore)
            result = -1;
        else if (gScore - Math.abs(goal) == hScore)
            result = 0;
        else
            result = 1;
    }
    if ((id.indexOf('h') != -1 || id.indexOf('v') != -1) && hId != h2h_home)
        result = result == 1 ? -1 : result == -1 ? 1 : result;
    if (id.indexOf('a') != -1 && hId != h2h_away)
        result = result == 1 ? -1 : result == -1 ? 1 : result;
    return result;
}
function getTotalResult(goal, hScore, gScore) {
    if (hScore + gScore > goal)
        return 1;
    else if (hScore + gScore == goal)
        return 0;
    else
        return -1;
}
function showOdds_s(id, t) {
    var url = "<a href=\"//op1.titan007.com/oddslist/{0}" + (lang == 1 ? "_2" : "") + ".htm\" target=\"_blank\">{1}</a>";
    //var url2 = "<a href=\"//op1.titan007.com/OddsHistory.aspx?id={0}&Company={1}&r1={2}&r2={3}\" target=\"_blank\">{4}</a>";
    var url2 = "<a href=\"//op1.titan007.com/OddsHistory.aspx?id={0}&cid={1}&sid={2}&l={3}\" target=\"_blank\">{4}</a>";
    var trlist = $_Our("table_" + id).getElementsByTagName("tr");
    var count = (newdata.length > 0 && newdata[0].length <= 16) || newdata.length == 0 ? 0 : 1;
    for (var i = 0; i < trlist.length; i++) {
        if (trlist[i].getAttribute("index") != null) {
            trlist[i].cells[8 + count].innerHTML = "";
            trlist[i].cells[9 + count].innerHTML = "";
            trlist[i].cells[10 + count].innerHTML = "";
        }
    }
    if (t == 1) {
        if (id == "v") {
            Config.scid_v = parseInt($_Our("sSelect_" + id).value);
            Config.stype_v = parseInt($_Our("sType_" + id).value);
        }
        else if (id == "hn") {
            Config.scid_hn = parseInt($_Our("sSelect_" + id).value);
            Config.stype_hn = parseInt($_Our("sType_" + id).value);
        }
        else {
            Config.scid_an = parseInt($_Our("sSelect_" + id).value);
            Config.stype_an = parseInt($_Our("sType_" + id).value);
        }
        Config.writeCookie();
    }
    var varcompayid = id == "v" ? Config.scid_v : id === "hn" ? Config.scid_hn : Config.scid_an;
    var hType = id == "v" ? Config.stype_v : id === "hn" ? Config.stype_hn : Config.stype_an;
    var cName = varcompayid == 80 ? "澳*" : varcompayid == 18 ? "12*" : varcompayid == 115 ? "威廉希*" : varcompayid == 281 ? "36*" : "Crow*";
    if (t == 0) {
        $_Our("sSelect_" + id).value = varcompayid;
        $_Our("sType_" + id).value = hType;
    }
    for (var i = 0; i < Vs_eOdds.length; i++) {
        var odds = Vs_eOdds[i];
        var tr = $_Our("tr" + id + "_" + odds[0]);
        if (tr == null) continue;
        if (varcompayid != parseInt(odds[1])) continue;
        var hName = tr.cells[2].innerHTML.replace(/<.+?>/gim, '');
        var gName = tr.cells[4 + count].innerHTML.replace(/<.+?>/gim, '');
        if (hType == 1) {
            tr.cells[8 + count].innerHTML = odds[5];
            if (varcompayid == 0)
                tr.cells[9 + count].innerHTML = url.format(odds[0], odds[6]);
            else {
                var homeresult = encodeURI(hName);
                var guestresult = encodeURI(gName);
                tr.cells[9 + count].innerHTML = url2.format(odds[8], varcompayid, scheduleID, lang != 0 ? 1 : 0, odds[6]);
                //tr.cells[9 + count].innerHTML = url2.format(odds[8], cName, hName, gName, odds[6]);
            }

            tr.cells[10 + count].innerHTML = odds[7];
        } else {
            tr.cells[8 + count].innerHTML = odds[2];
            if (varcompayid == 0)
                tr.cells[9 + count].innerHTML = url.format(odds[0], odds[3]);
            else {
                var homeresult = encodeURI(hName);
                var guestresult = encodeURI(gName);
                tr.cells[9 + count].innerHTML = url2.format(odds[8], varcompayid, scheduleID, lang != 0 ? 1 : 0, odds[3]);
                // tr.cells[9 + count].innerHTML = url2.format(odds[8], cName, hName, gName, odds[3]);
            }
            tr.cells[10 + count].innerHTML = odds[4];
        }
    }
}
function init_vs(id, count) {
    var sb = [];
    var win1, standoff = 0, win = 0, lost = 0, victoryNum = 0, drawNum = 0, lossNum = 0, bigNum = 0, singleNum = 0;
    sb.push('<table width="100%" border="0"  cellPadding=1 cellSpacing=1  bgcolor="#bbbbbb" id="table_' + id + '">');
    if ((newdata.length > 0 && newdata[0].length <= 16) || newdata.length == 0)
        sb.push('<tr align="center" class="blue_t2"><td height="20" rowspan="2">' + (Config.isSimple ? '类' : '類') + '型</td><td rowspan="2">日期</td><td rowspan="2">主' + (Config.isSimple ? '场' : '場') + '</td><td rowspan="2">比分(半' + (Config.isSimple ? '场' : '場') + ')</td><td rowspan="2">客' + (Config.isSimple ? '场' : '場') + '</td><td colspan="3"><select onchange="showOdds_h(\'' + id + '\',1);" id="hSelect_' + id + '"><option value="3" selected="selected">Crow*</option><option value="1">澳*</option><option value="8">36*</option><option value="12">易' + (Config.isSimple ? '胜' : '勝') + '*</option><option value="24">12*</option></select>&nbsp;&nbsp;<select id="hType_' + id + '" onchange="showOdds_h(\'' + id + '\',1);"><option value="0">初</option><option value="1" selected="selected">' + (Config.isSimple ? '终' : '終') + '</option></select></td><td colspan="3"><select onchange="showOdds_s(\'' + id + '\',1);" id="sSelect_' + id + '"><option value="0" selected="selected">胜平负均值</option><option value="115">威廉希*</option><option value="80">澳*</option><option value="281">36*</option> <option value="545">Crow*</option><option value="18">12*</option></select>&nbsp;&nbsp;<select id="sType_' + id + '" onchange="showOdds_s(\'' + id + '\',1);"><option value="0">初</option><option value="1" selected="selected">' + (Config.isSimple ? '终' : '終') + '</option></select></td><td rowspan="2">' + (Config.isSimple ? '胜' : '勝') + '负</td><td rowspan="2">' + (Config.isSimple ? '盘' : '盤') + '路</td><td rowspan="2">进球数</td></tr><tr align="center" class="blue_t2"><td>主</td><td>' + (Config.isSimple ? '盘' : '盤') + '口</td><td>客</td><td>主</td><td>和</td><td>客</td></tr>');
    else if (newdata[0].length <= 19)
        sb.push('<tr align="center" class="blue_t2"><td height="20" rowspan="2">' + (Config.isSimple ? '类' : '類') + '型</td><td rowspan="2">日期</td><td rowspan="2">主' + (Config.isSimple ? '场' : '場') + '</td><td rowspan="2">比分(半' + (Config.isSimple ? '场' : '場') + ')</td><td rowspan="2">角球</td><td rowspan="2">客' + (Config.isSimple ? '场' : '場') + '</td><td colspan="3"><select onchange="showOdds_h(\'' + id + '\',1);" id="hSelect_' + id + '"><option value="3" selected="selected">Crow*</option><option value="1">澳*</option><option value="8">36*</option><option value="12">易' + (Config.isSimple ? '胜' : '勝') + '*</option><option value="24">12*</option></select>&nbsp;&nbsp;<select id="hType_' + id + '" onchange="showOdds_h(\'' + id + '\',1);"><option value="0">初</option><option value="1" selected="selected">' + (Config.isSimple ? '终' : '終') + '</option></select></td><td colspan="3"><select onchange="showOdds_s(\'' + id + '\',1);" id="sSelect_' + id + '"><option value="0" selected="selected">胜平负均值</option><option value="115">威廉希*</option><option value="80">澳*</option><option value="281">36*</option> <option value="545">Crow*</option><option value="18">12*</option></select>&nbsp;&nbsp;<select id="sType_' + id + '" onchange="showOdds_s(\'' + id + '\',1);"><option value="0">初' + (Config.isSimple ? '盘' : '盤') + '</option><option value="1" selected="selected">' + (Config.isSimple ? '终' : '終') + '</option></select></td><td rowspan="2">' + (Config.isSimple ? '胜' : '勝') + '负</td><td rowspan="2">' + (Config.isSimple ? '盘' : '盤') + '路</td><td rowspan="2">进球数</td></tr><tr align="center" class="blue_t2"><td>主</td><td>' + (Config.isSimple ? '盘' : '盤') + '口</td><td>客</td><td>主</td><td>和</td><td>客</td></tr>');
    else
        sb.push('<tr align="center" class="blue_t2"><td height="20" rowspan="2">' + (Config.isSimple ? '类' : '類') + '型</td><td rowspan="2">日期</td><td rowspan="2">主' + (Config.isSimple ? '场' : '場') + '</td><td rowspan="2">比分(半' + (Config.isSimple ? '场' : '場') + ')</td><td rowspan="2">角球</td><td rowspan="2">客' + (Config.isSimple ? '场' : '場') + '</td><td colspan="3"><select onchange="showOdds_h(\'' + id + '\',1);" id="hSelect_' + id + '"><option value="3" selected="selected">Crow*</option><option value="1">澳*</option><option value="8">36*</option><option value="12">易' + (Config.isSimple ? '胜' : '勝') + '*</option><option value="24">12*</option></select>&nbsp;&nbsp;<select id="hType_' + id + '" onchange="showOdds_h(\'' + id + '\',1);"><option value="0">初</option><option value="1" selected="selected">' + (Config.isSimple ? '终' : '終') + '</option></select></td><td colspan="3"><select onchange="showOdds_s(\'' + id + '\',1);" id="sSelect_' + id + '"><option value="0" selected="selected">胜平负均值</option><option value="115">威廉希*</option><option value="80">澳*</option><option value="281">36*</option> <option value="545">Crow*</option><option value="18">12*</option></select>&nbsp;&nbsp;<select id="sType_' + id + '" onchange="showOdds_s(\'' + id + '\',1);"><option value="0">初</option></option><option value="1" selected="selected">' + (Config.isSimple ? '终' : '終') + '</option></select></td><td colspan="3"><select onchange="changeHalfOrFull(\'' + id + '\',this);" id="sSelect_' + id + '"><option value="0"' + (Config.isHalf==1 ?"": " selected='selected'") + ' >全' + (Config.isSimple ? '场' : '場') + '</option><option value="1" ' + (Config.isHalf==1 ? " selected='selected'" : "") +'>半' + (Config.isSimple ? '场' : '場') + '</option></td></tr><tr align="center" class="blue_t2"><td>主</td><td>' + (Config.isSimple ? '盘' : '盤') + '口</td><td>客</td><td>主</td><td>和</td><td>客</td><td>' + (Config.isSimple ? '胜' : '勝') + '负</td><td>' + (Config.isSimple ? '让' : '讓') + '球</td><td>进球数</td></tr>');

    var hColor = "", gColor = "";
    for (var a = 0; a < count; a++) {
        if (id == "v") {
            hColor = h2h_home == newdata[a][4] ? 'green' : 'black';
            gColor = h2h_away == newdata[a][4] ? 'green' : 'black';
        }
        else {
            hColor = id.substring(0, 1) == 'h' && h2h_home == newdata[a][4] || id.substring(0, 1) == 'a' && h2h_away == newdata[a][4] ? 'green' : 'black';
            gColor = id.substring(0, 1) == 'h' && h2h_home == newdata[a][6] || id.substring(0, 1) == 'a' && h2h_away == newdata[a][6] ? 'green' : 'black';
        }
        if (newdata[a].length <= 16)
            sb.push('<tr bgcolor={15} align=center  index="{20},{21}" id="{19}"><td height=25 bgcolor={3}><font color=white>{2}</font></td><td>{0}</td><td><a href={4} target=_blank><font color={16}>{5}</font></a></td><td><a href={18} target=_blank><font color=red>{8}-{9}</font></a>({10})</td><td><a href={6} target=_blank><font color={17}>{7}</font></a></td><td bgcolor="#FeFaF8"></td><td bgcolor="#FeFaF8"></td><td bgcolor="#FeFaF8"></td><td bgcolor="#F2F9FD"></td><td bgcolor="#F2F9FD"></td><td bgcolor="#F2F9FD"></td><td><font color=red>{12}</font></td><td><font color=red>{13}</font></td><td>{14}</td></tr>'.format(
                newdata[a][0], newdata[a][1], newdata[a][2], newdata[a][3], Config.teamInfoUrl.format(newdata[a][4]), newdata[a][5], Config.teamInfoUrl.format(newdata[a][6]), newdata[a][7], newdata[a][8], newdata[a][9], newdata[a][10], newdata[a][11], result[newdata[a][12] + 1], panlu[newdata[a][13] + 2], overUnder[newdata[a][14] + 1], a % 2 == 0 ? '#ffffff' : '#f0f0f0', hColor, gColor, Config.scoreDetailUrl.format(newdata[a][15]), ("tr" + id + "_" + newdata[a][15]), newdata[a][4], newdata[a][6]));
        else if (newdata[a].length <= 19)
            sb.push('<tr bgcolor={15} align=center  index="{21},{22}" id="{19}"><td height=25 bgcolor={3}><font color=white>{2}</font></td><td>{0}</td><td><a href={4} target=_blank><font color={16}>{5}</font></a></td><td><a href={18} target=_blank><font color=red>{8}-{9}</font></a>({10})</td><td>{20}</td><td><a href={6} target=_blank><font color={17}>{7}</font></a></td><td bgcolor="#FeFaF8"></td><td bgcolor="#FeFaF8"></td><td bgcolor="#FeFaF8"></td><td bgcolor="#F2F9FD"></td><td bgcolor="#F2F9FD"></td><td bgcolor="#F2F9FD"></td><td><font color=red>{12}</font></td><td><font color=red>{13}</font></td><td>{14}</td></tr>'.format(
                newdata[a][0], newdata[a][1], newdata[a].length > 18 && newdata[a][18] ? "<a href=" + newdata[a][18] + " target=_blank><font color=white>" + newdata[a][2] + "</font></a>" : newdata[a][2], newdata[a][3], Config.teamInfoUrl.format(newdata[a][4]), newdata[a][5], Config.teamInfoUrl.format(newdata[a][6]), newdata[a][7], newdata[a][8], newdata[a][9], newdata[a][10], newdata[a][11], result[newdata[a][12] + 1], panlu[newdata[a][13] + 2], overUnder[newdata[a][14] + 1], a % 2 == 0 ? '#ffffff' : '#f0f0f0', hColor, gColor, Config.scoreDetailUrl.format(newdata[a][15]), ("tr" + id + "_" + newdata[a][15]), newdata[a][16] != "" ? newdata[a][16] + "-" + newdata[a][17] : "", newdata[a][4], newdata[a][6]));
        else
            sb.push('<tr bgcolor={15} align=center  index="{21},{22}" id="{19}"><td height=25 bgcolor={3}><font color=white>{2}</font></td><td>{0}</td><td><a href={4} target=_blank><font color={16}>{5}</font></a></td><td><a href={18} target=_blank><font color=red>{8}-{9}</font></a>({10})</td><td>{20}</td><td><a href={6} target=_blank><font color={17}>{7}</font></a></td><td bgcolor="#FeFaF8"></td><td bgcolor="#FeFaF8"></td><td bgcolor="#FeFaF8"></td><td bgcolor="#F2F9FD"></td><td bgcolor="#F2F9FD"></td><td bgcolor="#F2F9FD"></td><td><font color=red>{12}</font></td><td><font color=red>{13}</font></td><td>{14}</td></tr>'.format(
                newdata[a][0], newdata[a][1], newdata[a].length > 18 && newdata[a][18] ? "<a href=" + newdata[a][18] + " target=_blank><font color=white>" + newdata[a][2] + "</font></a>" : newdata[a][2], newdata[a][3], Config.teamInfoUrl.format(newdata[a][4]), newdata[a][5], Config.teamInfoUrl.format(newdata[a][6]), newdata[a][7], newdata[a][8], newdata[a][9], newdata[a][10], newdata[a][11], result[newdata[a][12] + 1], panlu[newdata[a][13] + 2], overUnder[newdata[a][14] + 1], a % 2 == 0 ? '#ffffff' : '#f0f0f0', hColor, gColor, Config.scoreDetailUrl.format(newdata[a][15]), ("tr" + id + "_" + newdata[a][15]), newdata[a][16] != "" ? newdata[a][16] + "-" + newdata[a][17] : "", newdata[a][4], newdata[a][6]));
        if (newdata[a][13] == 1) win++;
        if (newdata[a][13] == 0) standoff++;
        if (newdata[a][13] == -1) lost++;
        if (newdata[a][14] == 1) bigNum++;
        if ((newdata[a][8] + newdata[a][9] + 2) % 2 > 0) singleNum++;
        if (newdata[a][12] == 1) victoryNum++;
        if (newdata[a][12] == 0) drawNum++;
        if (newdata[a][12] == -1) lossNum++;
    }
    if (count - standoff > 0)
        win1 = Math.floor(win / (win + standoff + lost) * 1000) / 10;
    else
        win1 = "0";
    if (count > 0) {
        var victoryPre = Math.floor(victoryNum / count * 1000) / 10;
        var bigPre = Math.floor(bigNum / count * 1000) / 10;
        var singlePre = Math.floor(singleNum / count * 1000) / 10;
        if (id == 'v')
            sb.push('<tr align=center><TD height=25 align=center colSpan=15 bgcolor=#ffffff>近 <font color=red>' + count + '</font> ' + (Config.isSimple ? '场' : '場') + ',	' + (Config.isSimple ? '胜' : '勝') + '出 <font color=red><span id="win_' + id + '">' + victoryNum + '</span></font> ' + (Config.isSimple ? '场' : '場') + ',平局 <font color=red><span id="draw_' + id + '">' + drawNum + '</span></font> ' + (Config.isSimple ? '场' : '場') + ',输 <font color=red><span id="loss_' + id + '">' + lossNum + '</span></font> ' + (Config.isSimple ? '场' : '場') + ', ' + (Config.isSimple ? '胜' : '勝') + '率：' + getPreHtml(victoryPre, 1, "winPre", id) + ' ' + (Config.isSimple ? '赢' : '贏') + '率：' + getPreHtml(win1, 1, "awin", id) + ' 大率：' + getPreHtml(bigPre, 1, "big", id) + ' ' + (Config.isSimple ? '单' : '單') + '率：' + getPreHtml(singlePre, 2, "single", id) + '</td></tr>');
        else
            sb.push('<tr align=center><TD height=25 align=center colSpan=15 bgcolor=#ffffff>近<font color=red>' + count + '</font>' + (Config.isSimple ? '场' : '場') + ',' + (Config.isSimple ? '胜' : '勝') + '<span id="win_' + id + '">' + victoryNum + '</span>平<span id="draw_' + id + '">' + drawNum + '</span>负<span id="loss_' + id + '">' + lossNum + '</span>, ' + (Config.isSimple ? '胜' : '勝') + '率:' + getPreHtml(victoryPre, 1, "winPre", id) + ' ' + (Config.isSimple ? '赢' : '贏') + '率:' + getPreHtml(win1, 1, "awin", id) + ' 大:' + getPreHtml(bigPre, 1, "big", id) + ' ' + (Config.isSimple ? '单' : '單') + '率:' + getPreHtml(singlePre, 2, "single", id) + '</td></tr>');
    }
    sb.push('</table>');
    $_Our(id).innerHTML = sb.join('');
    showOdds_h(id, 0);
    showOdds_s(id, 0);
}
//kind 1:输出颜色块 2：改变字体颜色
function getPreHtml(pre, kind, name, id) {
    pre = parseFloat(pre);
    if (isNaN(pre)) pre = 0;
    var preHtml = '<span id="{1}"><font {0}>{2}%</font></span>';
    var preHtml2 = '<font {0}>{1}%</font>';
    var bgStyle = new Array("class=redBG", "class=greenBG", "color=blue");
    var bgColor = new Array("color=red", "color=green", "color=blue");
    var styleIndex = pre >= 70 ? 0 : pre <= 30 ? 1 : 2;
    if (kind == 1) {
        if (typeof (name) != 'undefined' && name != '')
            return preHtml.format(bgStyle[styleIndex], name + '_' + id, pre);
        else
            return preHtml2.format(bgStyle[styleIndex], pre);
    }
    else
        return preHtml2.format(bgColor[styleIndex], pre);
}
function init_vs2(id, count) {
    var sb = [];
    var win1, standoff = 0, win = 0, lost = 0, victoryNum = 0, drawNum = 0, lossNum = 0, bigNum = 0, singleNum = 0;
    sb.push('<table id="table_' + id + '" width="100%" border="0"  cellPadding=1 cellSpacing=1  bgcolor="#bbbbbb">');
    if ((newdata.length > 0 && newdata[0].length <= 16) || newdata.length == 0)
        sb.push('<TR align=center class=blue_t2><td height=20>' + (Config.isSimple ? '类' : '類') + '型</td><td>日期</td><td>主' + (Config.isSimple ? '场' : '場') + '</td><td>' + (Config.isSimple ? '盘' : '盤') + '口</td><td>客' + (Config.isSimple ? '场' : '場') + '</td><td>比分</td><td>半' + (Config.isSimple ? '场' : '場') + '</td><td>' + (Config.isSimple ? '胜' : '勝') + '负</td><td>'  + (Config.isSimple ? '让' : '讓') + '球</td><td>进球数</td></tr>');
    else
        sb.push('<TR align=center class=blue_t2><td height=20>' + (Config.isSimple ? '类' : '類') + '型</td><td>日期</td><td>主' + (Config.isSimple ? '场' : '場') + '</td><td>' + (Config.isSimple ? '盘' : '盤') + '口</td><td>客' + (Config.isSimple ? '场' : '場') + '</td><td>比分</td><td>角球</td><td>' + (Config.isSimple ? '胜' : '勝') + '负</td><td>' + (Config.isSimple ? '让' : '讓') + '球</td><td>进球数</td></tr>');
    
    for (var a = 0; a < count; a++) {

        if (newdata[a].length <= 16)
            sb.push('<tr bgcolor={15} align=center index="{23},{24}" id="tr{20}_{21}"><td height=25 bgcolor={3}><font color=white>{2}</font></td><td>{0}</td><td><a href={4} target=_blank><font color={16}>{5}</font></a></td><td><a href={19} target=_blank>{11}<a></td><td><a href={6} target=_blank><font color={17}>{7}</font></a></td><td><a href={18} target=_blank><font color=red>{8}-{9}</font></a></td><td>{10}</td><td><font color=red>{12}</font></td><td><font color=red>{13}</font></td><td><font color=blue>{14}</td></tr>'.format(
                newdata[a][0], newdata[a][1], newdata[a][2], newdata[a][3], Config.teamInfoUrl.format(newdata[a][4]), newdata[a][5], Config.teamInfoUrl.format(newdata[a][6]), newdata[a][7], newdata[a][8], newdata[a][9], newdata[a][10], newdata[a][11], result[newdata[a][12] + 1], panlu[newdata[a][13] + 2], overUnder[newdata[a][14] + 1], a % 2 == 0 ? '#ffffff' : '#f0f0f0', id.substring(0, 1) == 'h' && h2h_home == newdata[a][4] || id.substring(0, 1) == 'a' && h2h_away == newdata[a][4] ? 'green' : 'black', id.substring(0, 1) == 'h' && h2h_home == newdata[a][6] || id.substring(0, 1) == 'a' && h2h_away == newdata[a][6] ? 'green' : 'black', Config.scoreDetailUrl.format(newdata[a][15]), Config.vipAsiaUrl.format(newdata[a][15]), id, newdata[a][15]));
        else
            sb.push('<tr bgcolor={15} align=center index="{23},{24}" id="tr{21}_{22}"><td height=25 bgcolor={3}><font color=white>{2}</font></td><td>{0}</td><td><a href={4} target=_blank><font color={16}>{5}</font></a></td><td><a href={20} target=_blank>{11}<a></td><td><a href={6} target=_blank><font color={17}>{7}</font></a></td><td><a href={18} target=_blank><font color=red>{8}-{9}</font><br/><span style="font-size: 11px;">({10})</span></a></td><td>{19}</td><td><font color=red>{12}</font></td><td><font color=red>{13}</font></td><td><font color=blue>{14}</td></tr>'.format(
                newdata[a][0], newdata[a][1], newdata[a].length > 18 && newdata[a][18] ? "<a href=" + newdata[a][18] + " target=_blank><font color=white>" + newdata[a][2] + "</font></a>" : newdata[a][2], newdata[a][3], Config.teamInfoUrl.format(newdata[a][4]), newdata[a][5], Config.teamInfoUrl.format(newdata[a][6]), newdata[a][7], newdata[a][8], newdata[a][9], newdata[a][10], newdata[a][11], result[newdata[a][12] + 1], panlu[newdata[a][13] + 2], overUnder[newdata[a][14] + 1], a % 2 == 0 ? '#ffffff' : '#f0f0f0', id.substring(0, 1) == 'h' && h2h_home == newdata[a][4] || id.substring(0, 1) == 'a' && h2h_away == newdata[a][4] ? 'green' : 'black', id.substring(0, 1) == 'h' && h2h_home == newdata[a][6] || id.substring(0, 1) == 'a' && h2h_away == newdata[a][6] ? 'green' : 'black', Config.scoreDetailUrl.format(newdata[a][15]), newdata[a][16] != "" ? newdata[a][16] + "-" + newdata[a][17] : "", Config.vipAsiaUrl.format(newdata[a][15]), id, newdata[a][15], newdata[a][4], newdata[a][6]));
        if (newdata[a][13] == 1) win++;
        if (newdata[a][13] == 0) standoff++;
        if (newdata[a][13] == -1) lost++;
        if (newdata[a][14] == 1) bigNum++;
        if ((newdata[a][8] + newdata[a][9] + 2) % 2 > 0) singleNum++;
        if (newdata[a][12] == 1) victoryNum++;
        if (newdata[a][12] == 0) drawNum++;
        if (newdata[a][12] == -1) lossNum++;
    }
    if (count - standoff > 0)
        win1 = Math.floor(win / (win + standoff + lost) * 1000) / 10;
    else
        win1 = "0";
    var victoryPre = Math.floor(victoryNum / count * 1000) / 10;
    var bigPre = Math.floor(bigNum / count * 1000) / 10;
    var singlePre = Math.floor(singleNum / count * 1000) / 10;
    if (count > 0) sb.push('<tr align=center><TD height=25 align=center colspan=10 bgcolor=#ffffff>近<font color=red>' + count + '</font>' + (Config.isSimple ? '场' : '場') + ',' + (Config.isSimple ? '胜' : '勝') + '<span id="win_' + id + '">' + victoryNum + '</span>平<span id="draw_' + id + '">' + drawNum + '</span>负<span id="loss_' + id + '">' + lossNum + '</span>, 胜率:' + getPreHtml(victoryPre, 1, "winPre", id) + ' ' + (Config.isSimple ? '赢' : '贏') + '率:' + getPreHtml(win1, 1, "awin", id)  + ' 大: ' + getPreHtml(bigPre, 1, "big", id) + ' ' + (Config.isSimple ? '单' : '單') + '率:' + getPreHtml(singlePre, 2, "single", id) + '</td></tr>');
    sb.push('</table>');
    $_Our(id).innerHTML = sb.join('');
    var objTd = $_Our(id + "_vsOldTd");
    var tdName = "h";
    switch (id) {
        case "h":
            tdName = "a";
            break;
        case "a":
            tdName = "h";
            break;
        case "h2":
            tdName = "a2";
            break;
        case "a2":
            tdName = "h2";
            break;
    }
    var objTd2 = $_Our(tdName + "_vsOldTd");
    if (objTd) {
        var height = objTd.offsetHeight > 0 ? objTd.offsetHeight : objTd.clientHeight;
        height = height / 2 + 14;
        objTd.style.background = "url(/images/noData.jpg) no-repeat center " + height + "px";
        objTd2.style.background = "url(/images/noData.jpg) no-repeat center " + height + "px";

    }
    showOldDataOdds(id);
}
function init_select(id, count) {
    var select = $_Our(id + "_s");
    select.options.length = 0;
    for (var i = 0; i < newdata.length; i++)
        select.options[i] = new Option((i + 1) < 10 ? " " + (i + 1) : (i + 1), (i + 1));
    if (select.options.length > 0)
        select.options[newdata.length > count ? count - 1 : i - 1].selected = true;
    else
        select.options[0] = new Option(" " + 0, 0);
}
function miniopen(a) {
    var w = window.screen.width;
    var h = window.screen.height;
    var winWidth = 400;
    var winHeight = 600;
    var winTop = (h - winHeight) / 2;
    var winLeft = (w - winWidth) / 2;
    window.open(a, "_blank", "top=" + winTop + ",left=" + winLeft + ",height=" + winHeight + ",width=" + winWidth + ",status=yes,toolbar=auto,menubar=no,location=no");
    return false;
}
function changeVs(t) {
    Config.oldOrNew = t;
    Config.writeCookie();
    showVs();
}
function showVs() {
    $_Our("chec_vsOld").checked = (Config.oldOrNew == 0 ? true : false);
    $_Our("chec_vsNew").checked = (Config.oldOrNew == 1 ? true : false);
    $_Our("chec_vsOld2").checked = (Config.oldOrNew == 0 ? true : false);
    $_Our("chec_vsNew2").checked = (Config.oldOrNew == 1 ? true : false);
    $_Our("vsOld").style.display = (Config.oldOrNew == 0 ? "" : "none");
    $_Our("vsNew").style.display = (Config.oldOrNew == 0 ? "none" : "");
    if (Config.oldOrNew == 0) {
        init("h");
        init("a");
        init("h2");
        init("a2");
        init_league('h');
        init_league('a');
        init_league('h2');
        init_league('a2');
    }
    else {
        init("hn");
        init("an");
        init_league('hn');
        init_league('an');
    }
}
//function com_init_vs() {
//    var sb = [];
//    sb.push('<table id="table_com" width="100%" border="0"  cellPadding=1 cellSpacing=1  bgcolor="#bbbbbb">');
//    //sb.push('<tr align=middle bgcolor="#FAF1DE" height=20><td >球队</td><td>' + (Config.isSimple ? '总' : '總') + '' + (Config.isSimple ? '进' : '進') + '球</td><td>' + (Config.isSimple ? '总' : '總') + '失球</td><td>' + (Config.isSimple ? '净' : '凈') + (Config.isSimple ? '胜' : '勝') + '球</td><td>' + (Config.isSimple ? '场' : '場') + '均' + (Config.isSimple ? '进' : '進') + '球</td><td>' + (Config.isSimple ? '胜' : '勝') + '率</td><td>平率</td><td>负率</td><td>同主<font color="#1e50a2">客</font>' + (Config.isSimple ? '进' : '進') + '</td><td>同主<font color="#1e50a2">客</font>失</td><td>同主<font color="#1e50a2">客</font>' + (Config.isSimple ? '净' : '凈') + (Config.isSimple ? '胜' : '勝') + '</td><td>同主<font color="#1e50a2">客</font>均' + (Config.isSimple ? '进' : '進') + '</td><td>同主<font color="#1e50a2">客</font>' + (Config.isSimple ? '胜' : '勝') + '</td><td>同主<font color="#1e50a2">客</font>平</td><td>同主<font color="#1e50a2">客</font>负</td></tr>');
//    sb.push('<tr align=middle bgcolor="#FAF1DE" height=20><td >球队</td><td>' + (Config.isSimple ? '总' : '總') + '' + (Config.isSimple ? '进' : '進') + '球</td><td>' + (Config.isSimple ? '总' : '總') + '失球</td><td>' + (Config.isSimple ? '净' : '凈') + (Config.isSimple ? '胜' : '勝') + '球</td><td>' + (Config.isSimple ? '场' : '場') + '均' + (Config.isSimple ? '进' : '進') + '球</td><td>' + (Config.isSimple ? '场' : '場') + '均角球</td><td>' + (Config.isSimple ? '场' : '場') + '均黄牌</td><td>同主<font color="#1e50a2">客</font>' + (Config.isSimple ? '进' : '進') + '</td><td>同主<font color="#1e50a2">客</font>失</td><td>同主<font color="#1e50a2">客</font>' + (Config.isSimple ? '净' : '凈') + (Config.isSimple ? '胜' : '勝') + '</td><td>同主<font color="#1e50a2">客</font>均' + (Config.isSimple ? '进' : '進') + '</td><td>同主<font color="#1e50a2">客</font>' + (Config.isSimple ? '胜' : '勝') + '</td><td>同主<font color="#1e50a2">客</font>平</td><td>同主<font color="#1e50a2">客</font>负</td></tr>');
//    sb.push('<tr id=tr_com_h align=middle bgcolor="#ffffff" height=20><td >' + hometeam + '</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>');
//    sb.push('<tr id=tr_com_a align=middle bgcolor="#f0f0f0" height=20 style="color:#1e50a2;"><td >' + guestteam + '</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>');
//    sb.push('</table>');
//    $_Our("div_com").innerHTML = sb.join('');
//}
function com_init_vs() {
    var sb = [];
    sb.push('<table id="table_com" width="100%" border="0"  cellPadding=1 cellSpacing=1  bgcolor="#bbbbbb">');
    sb.push('<tr align=middle bgcolor="#FAF1DE" height=20><td rowspan="2" width="14%">' + (Config.isSimple ? '球队' : '球隊') + '</td><td colspan="9">全部</td><td colspan="7">同主客</td></tr>');
    sb.push('<tr align=middle bgcolor="#FAF1DE" height=20><td width="5%">胜</td><td width="5%">平</td><td width="5%">负</td><td width="5%">' + (Config.isSimple ? '进' : '進') + '球</td><td width="5%">失球</td><td width="6%">' + (Config.isSimple ? '净' : '凈') + (Config.isSimple ? '胜' : '勝') + '球</td><td width="6%">' + (Config.isSimple ? '场' : '場') + '均' + (Config.isSimple ? '进' : '進') + '球</td><td width="6%">' + (Config.isSimple ? '场' : '場') + '均角球</td><td width="6%">' + (Config.isSimple ? '场' : '場') + '均黄牌</td><td width="5%">' + (Config.isSimple ? '进' : '進') + '球</td><td width="5%">失球</td><td width="6%">' + (Config.isSimple ? '净' : '凈') + (Config.isSimple ? '胜' : '勝') + '球</td><td width="6%">' + (Config.isSimple ? '场' : '場') + '均' + (Config.isSimple ? '进' : '進') + '球</td><td width="5%">' + (Config.isSimple ? '胜' : '勝') + '</td><td width="5%">平</td><td width="5%">负</td></tr>');
    sb.push('<tr id=tr_com_h align=middle bgcolor="#ffffff" height=20><td >' + hometeam + '</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>');
    sb.push('<tr id=tr_com_a align=middle bgcolor="#f0f0f0" height=20 style="color:#1e50a2;"><td >' + guestteam + '</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>');
    sb.push('</table>');
    $_Our("div_com").innerHTML = sb.join('');
}
function com_init_data(count) {
    var c = count ? (count > a_data.length ? a_data.length : count) : (a_data.length > 10 ? 10 : a_data.length);
    com_init_vs_data("a", c);
    c = count ? (count > h_data.length ? h_data.length : count) : (h_data.length > 10 ? 10 : h_data.length);
    com_init_vs_data("h", c);
    if (!count)
        init_select_com("com", c);
}
function init_select_com(id, count) {
    var select = $_Our(id + "_s");
    select.options.length = 0;
    var tempCount = h_data.length > a_data.length ? a_data.length : h_data.length;
    for (var i = 0; i < tempCount; i++)
        select.options[i] = new Option((i + 1) < 10 ? " " + (i + 1) : (i + 1), (i + 1));
    if (select.options.length > 0)
        select.options[tempCount > count ? count - 1 : i - 1].selected = true;
    else
        select.options[0] = new Option(" " + 0, 0);
}
function com_init_vs_data(id, count) {
    var data = [];
    if (id == "h")
        data = h_data;
    else
        data = a_data;

    var allGoal = 0, allLossGoal = 0, winNum = 0, drawNum = 0, lossNum = 0, hgCount = 0, hgGoal = 0, hgLossGoal = 0, hgWin = 0, hgDraw = 0, hgLoss = 0, cornerNum = 0, yellowCard = 0;
    for (var a = 0; a < count; a++) {
        if ((id == "h" && h2h_home == data[a][4]) || (id == "a" && h2h_away == data[a][4])) {
            allGoal += parseInt(data[a][8]);
            allLossGoal += parseInt(data[a][9]);
            if (parseInt(data[a][8]) > parseInt(data[a][9])) {
                winNum += 1;
                if (id == "h")
                    hgWin += 1;
            }
            else if (parseInt(data[a][8]) == parseInt(data[a][9])) {
                drawNum += 1;
                if (id == "h")
                    hgDraw += 1;
            }
            else {
                lossNum += 1;
                if (id == "h")
                    hgLoss += 1;
            }
            if (id == "h") {
                hgCount += 1;
                hgGoal += parseInt(data[a][8]);
                hgLossGoal += parseInt(data[a][9]);                
            }
            if (data[a][16] != "")
                cornerNum += parseInt(data[a][16]);
            if (data[a].length > 20)
                yellowCard += parseInt(data[a][20]);
        }
        else if ((id == "h" && h2h_home == data[a][6]) || (id == "a" && h2h_away == data[a][6])) {
            allGoal += parseInt(data[a][9]);
            allLossGoal += parseInt(data[a][8]);
            if (parseInt(data[a][9]) > parseInt(data[a][8])) {
                winNum += 1;
                if (id == "a")
                    hgWin += 1;
            }
            else if (parseInt(data[a][8]) == parseInt(data[a][9])) {
                drawNum += 1;
                if (id == "a")
                    hgDraw += 1;
            }
            else {
                lossNum += 1;
                if (id == "a")
                    hgLoss += 1;
            }
            if (id == "a") {
                hgCount += 1;
                hgGoal += parseInt(data[a][9]);
                hgLossGoal += parseInt(data[a][8]);                
            }
            if (data[a][17] != "")
                cornerNum += parseInt(data[a][17]);
            if (data[a].length > 20)
                yellowCard += parseInt(data[a][21]);
        }
    }
    var tr = document.getElementById("tr_com_" + id);
    tr.cells[1].innerHTML = count > 0 ? Math.floor(winNum / count * 1000) / 10 + "%" : "";
    tr.cells[2].innerHTML = count > 0 ? Math.floor(drawNum / count * 1000) / 10 + "%" : "";
    tr.cells[3].innerHTML = count > 0 ? Math.floor(lossNum / count * 1000) / 10 + "%" : "";
    tr.cells[4].innerHTML = allGoal;
    tr.cells[5].innerHTML = allLossGoal;
    tr.cells[6].innerHTML = allGoal - allLossGoal;
    tr.cells[7].innerHTML = count > 0 ? Math.floor(allGoal / count * 100) / 100 : 0;
    tr.cells[8].innerHTML = count > 0 ? Math.floor(cornerNum / count * 100) / 100 : 0;
    tr.cells[9].innerHTML = count > 0 && data[0].length > 20 ? (count > 0 ? Math.floor(yellowCard / count * 100) / 100 : 0) : "-";
    //tr.cells[7].innerHTML = count > 0 ? Math.floor(lossNum / count * 1000) / 10 + "%" : "";
    tr.cells[10].innerHTML = hgGoal;
    tr.cells[11].innerHTML = hgLossGoal;
    tr.cells[12].innerHTML = hgGoal - hgLossGoal;
    tr.cells[13].innerHTML = hgCount > 0 ? Math.floor(hgGoal / hgCount * 100) / 100 : "0";
    tr.cells[14].innerHTML = hgCount > 0 ? Math.floor(hgWin / hgCount * 1000) / 10 + "%" : "";
    tr.cells[15].innerHTML = hgCount > 0 ? Math.floor(hgDraw / hgCount * 1000) / 10 + "%" : "";
    tr.cells[16].innerHTML = hgCount > 0 ? Math.floor(hgLoss / hgCount * 1000) / 10 + "%" : "";
}
function LoadDetailFile(sid) {
    var detail = document.getElementById("span_odds");
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.charset = "utf-8";
    s.src = "jsData/" + sid + ".js?" + Date.parse(new Date());
    detail.removeChild(detail.firstChild);
    detail.appendChild(s, "script");
    loadDetailFileTime = new Date();
    try {
        showOdds(sid);
    }
    catch (e) { }
    window.setTimeout("LoadDetailFile(" + sid + ")", 120000);
}
function showOdds(sid) {
    var html = new Array();
    html.push("<table width=100% border=0 cellpadding=2 cellspacing=1 bgcolor=#C5DCED class=liveodd_box style='text-align:center;'>");
    html.push("<tr bgColor=#fdefd2 class=tyr_f>");
    html.push("<TD width=86 height=24 bgcolor=#DAE9FA>公司</TD>");
    html.push("<TD width=42 bgcolor=#DAE9FA></TD>");
    html.push("<TD width=66 bgcolor=#DAE9FA>主队</TD>");
    html.push("<TD width=65 bgcolor=#DAE9FA>亚让</TD>");
    html.push("<TD width=63 bgcolor=#DAE9FA>客队</TD>");
    html.push("<TD width=70 bgcolor=#DAE9FA>主胜</TD>");
    html.push("<TD width=70 bgcolor=#DAE9FA>和局</TD>");
    html.push("<TD width=70 bgcolor=#DAE9FA>客胜</TD>");
    html.push("<TD width=75 bgcolor=#DAE9FA>大球</TD>");
    html.push("<TD width=69 bgcolor=#DAE9FA>盘口</TD>");
    html.push("<TD width=67 bgcolor=#DAE9FA>小球</TD>");
    html.push("<TD width=48 bgcolor=#DAE9FA>变化</TD>");
    html.push("</tr>");
    for (var k in arrOdds) {
        html.push("<tr bgcolor=#FFFFFF style=height:20px;>");
        html.push("<td rowspan=" + ((st > 0 || st == -1) && arrOdds[k][0] == 3 ? "3" : "2") + " class=yui><strong>" + CompanyName[arrOdds[k][0]] + "</strong></td>");
        html.push("<td>初</td>");
        if (typeof (arrOdds[k][1][1]) != "undefined" && arrOdds[k][1][1] != "") {
            html.push("<td>" + arrOdds[k][1][1] + "</td>");
            html.push("<td>" + Goal2GoalCn(arrOdds[k][1][2]) + "</td>");
            html.push("<td>" + arrOdds[k][1][3] + "</td>");
        }
        else {
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
        }
        if (typeof (arrOdds[k][1][4]) != "undefined" && arrOdds[k][1][4] != "") {
            html.push("<td bgColor=#FEFFEE>" + arrOdds[k][1][4] + "</td>");
            html.push("<td bgColor=#FEFFEE>" + arrOdds[k][1][5] + "</td>");
            html.push("<td bgColor=#FEFFEE>" + arrOdds[k][1][6] + "</td>");
        }
        else {
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
        }
        if (typeof (arrOdds[k][1][7]) != "undefined" && arrOdds[k][1][7] != "") {
            html.push("<td>" + arrOdds[k][1][7] + "</td>");
            html.push("<td>" + Goal2GoalOU(arrOdds[k][1][8]) + "</td>");
            html.push("<td>" + arrOdds[k][1][9] + "</td>");
        }
        else {
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
        }
        html.push("<td rowspan=" + ((st > 0 || st == -1) && arrOdds[k][0] == 3 ? "3" : "2") + ">" + "<a href=//vip.titan007.com/changeDetail/handicap.aspx?id=" + sid + "&companyID=" + arrOdds[k][0] + "  target=_blank><img src=../Images/t2.gif width=11 height=12  border=0/></a></td>");
        html.push("</tr>");
        if ((st > 0 || st == -1) && arrOdds[k][0] == 3 && arrOdds[k].length == 4) {
            html.push("<tr bgcolor=#FFFFFF style=height:20px;>");
            html.push("<td bgcolor=#F2F9FD>终</td>");
            if (typeof (arrOdds[k][3][1]) != "undefined" && arrOdds[k][3][1] != "") {
                html.push("<td>" + arrOdds[k][3][1] + "</td>");
                html.push("<td>" + Goal2GoalCn(arrOdds[k][3][2]) + "</td>");
                html.push("<td>" + arrOdds[k][3][3] + "</td>");
            }
            else {
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
            }
            if (typeof (arrOdds[k][3][4]) != "undefined" && arrOdds[k][3][4] != "") {
                html.push("<td bgColor=#FEFFEE>" + arrOdds[k][3][4] + "</td>");
                html.push("<td bgColor=#FEFFEE>" + arrOdds[k][3][5] + "</td>");
                html.push("<td bgColor=#FEFFEE>" + arrOdds[k][3][6] + "</td>");
            }
            else {
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
            }
            if (typeof (arrOdds[k][3][7]) != "undefined" && arrOdds[k][3][7] != "") {
                html.push("<td>" + arrOdds[k][3][7] + "</td>");
                html.push("<td>" + Goal2GoalOU(arrOdds[k][3][8]) + "</td>");
                html.push("<td>" + arrOdds[k][3][9] + "</td>");
            }
            else {
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
            }
            html.push("</tr>");
        }
        html.push("<tr bgcolor=#fffff0 style=height:20px;>");
        if (typeof (arrOdds[k][2][1]) != "undefined" && arrOdds[k][2][1] != "") {
            if ((st > 0 || st == -1) && arrOdds[k][0] == 3)
                html.push("<td bgcolor=#F2F9FD><span style=color:#F60>滚球</span></td>");
            else if (st > 0)
                html.push("<td bgcolor=#F2F9FD>终</td>");
            else
                html.push("<td bgcolor=#F2F9FD><span style=color:#F60>即时</span></td>");
            html.push("<td bgcolor=#F2F9FD><strong>" + arrOdds[k][2][1] + "</strong></td>");
            html.push("<td bgcolor=#F2F9FD><strong>" + Goal2GoalCn(arrOdds[k][2][2]) + "</strong></td>");
            html.push("<td bgcolor=#F2F9FD><strong>" + arrOdds[k][2][3] + "</strong></td>");
        }
        else {
            html.push("<td bgcolor=#F2F9FD>" + "</td>");
            html.push("<td bgcolor=#F2F9FD>" + "</td>");
            html.push("<td bgcolor=#F2F9FD>" + "</td>");
        }
        if ((typeof (arrOdds[k][2][4]) != "undefined" && arrOdds[k][2][4] != "" && arrOdds[k][0] != 3) || (typeof (arrOdds[k][2][4]) != "undefined" && arrOdds[k][2][4] != "" && st == 0)) {
            html.push("<td bgcolor=#FEFFEE><strong>" + arrOdds[k][2][4] + "</strong></td>");
            html.push("<td bgcolor=#FEFFEE><strong>" + arrOdds[k][2][5] + "</strong></td>");
            html.push("<td bgcolor=#FEFFEE><strong>" + arrOdds[k][2][6] + "</strong></td>");
        }
        else {
            html.push("<td bgcolor=#FEFFEE>" + "</td>");
            html.push("<td bgcolor=#FEFFEE>" + "</td>");
            html.push("<td bgcolor=#FEFFEE>" + "</td>");
        }
        if (typeof (arrOdds[k][2][7]) != "undefined" && arrOdds[k][2][7] != "") {
            html.push("<td bgcolor=#F2F9FD><strong>" + arrOdds[k][2][7] + "</strong></td>");
            html.push("<td bgcolor=#F2F9FD><strong>" + Goal2GoalOU(arrOdds[k][2][8]) + "</strong></td>");
            html.push("<td bgcolor=#F2F9FD><strong>" + arrOdds[k][2][9] + "</strong></td>");
        }
        else {
            html.push("<td bgcolor=#F2F9FD>" + "</td>");
            html.push("<td bgcolor=#F2F9FD>" + "</td>");
            html.push("<td bgcolor=#F2F9FD>" + "</td>");
        }
        html.push("</tr>");
    }
    html.push("</table>");
    $_Our("iframeA").innerHTML = html.join("");
}
function LoadDetailFileNew(sid) {
    var detail = document.getElementById("span_odds");
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.charset = "utf-8";
    s.src = "jsData/" + sid + ".js?" + Date.parse(new Date());
    detail.removeChild(detail.firstChild);
    detail.appendChild(s, "script");
    loadDetailFileTime = new Date();
    try {
        showOddsNew(sid);
    }
    catch (e) { }
    window.setTimeout("LoadDetailFileNew(" + sid + ")", 120000);
}
function showOddsNew(sid) {
    var html = new Array();
    html.push("<table width=100% border=0 cellpadding=2 cellspacing=1 bgcolor=#C5DCED class=liveodd_box style='text-align:center;'>");
    html.push("<tr bgColor=#fdefd2 class=tyr_f>");
    html.push("<TD rowspan='2' colspan='2' height=24 bgcolor=#DAE9FA>公司</TD>");
    html.push("<TD colspan='3' bgcolor=#DAE9FA>欧指</TD>");
    html.push("<TD colspan='4' bgcolor=#DAE9FA>欧转亚盘</TD>");
    html.push("<TD colspan='4' bgcolor=#DAE9FA>实际亚盘</TD>");
    html.push("<TD colspan='3' bgcolor=#DAE9FA>进球数</TD>");
    html.push("<TD width=30 rowspan='2' bgcolor=#DAE9FA>变化</TD>");
    html.push("</tr>");
    html.push("<tr bgColor=#fdefd2 class=tyr_f>");
    html.push("<TD width=45 bgcolor=#DAE9FA>主胜</TD>");
    html.push("<TD width=45 bgcolor=#DAE9FA>和局</TD>");
    html.push("<TD width=45 bgcolor=#DAE9FA>客胜</TD>");
    html.push("<TD width=45 bgcolor=#DAE9FA>主队</TD>");
    html.push("<TD width=55 bgcolor=#DAE9FA>亚让</TD>");
    html.push("<TD width=45 bgcolor=#DAE9FA>客队</TD>");
    html.push("<TD width=50 bgcolor=#DAE9FA>总水位</TD>");
    html.push("<TD width=50 bgcolor=#DAE9FA>主队</TD>");
    html.push("<TD width=55 bgcolor=#DAE9FA>亚让</TD>");
    html.push("<TD width=50 bgcolor=#DAE9FA>客队</TD>");
    html.push("<TD width=50 bgcolor=#DAE9FA>总水位</TD>");
    html.push("<TD width=50 bgcolor=#DAE9FA>大球</TD>");
    html.push("<TD width=50 bgcolor=#DAE9FA>盘口</TD>");
    html.push("<TD width=50 bgcolor=#DAE9FA>小球</TD>");
    html.push("</tr>");
    for (var k in arrOdds) {
        html.push("<tr bgcolor=#FFFFFF style=height:20px;>");
        html.push("<td rowspan=" + ((st > 0 || st == -1) && arrOdds[k][0] == 3 ? "3" : "2") + " class=yui><strong>" + CompanyName[arrOdds[k][0]] + "</strong></td>");
        html.push("<td width='42' style='text-align:center;'>初</td>");
        if (typeof (arrOdds[k][1][4]) != "undefined" && arrOdds[k][1][4] != "") {
            html.push("<td>" + arrOdds[k][1][4] + "</td>");
            html.push("<td>" + arrOdds[k][1][5] + "</td>");
            html.push("<td>" + arrOdds[k][1][6] + "</td>");
        }
        else {
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
        }
        if (typeof (arrOdds[k][1][10]) != "undefined" && arrOdds[k][1][10] != "") {
            html.push("<td bgColor=#FEFFEE>" + arrOdds[k][1][10] + "</td>");
            html.push("<td bgColor=#FEFFEE>" + Goal2GoalOU(arrOdds[k][1][11]) + "</td>");
            html.push("<td bgColor=#FEFFEE>" + arrOdds[k][1][12] + "</td>");
            html.push("<td bgColor=#FEFFEE>1.85</td>");
        }
        else {
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
        }
        if (typeof (arrOdds[k][1][1]) != "undefined" && arrOdds[k][1][1] != "") {
            html.push("<td>" + arrOdds[k][1][1] + "</td>");
            html.push("<td>" + Goal2GoalOU(arrOdds[k][1][2]) + "</td>");
            html.push("<td>" + arrOdds[k][1][3] + "</td>");
            html.push("<td>" + (parseFloat(arrOdds[k][1][1]) + parseFloat(arrOdds[k][1][3])).toFixed(2) + "</td>");
        }
        else {
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
            html.push("<td></td>");
        }
        if (typeof (arrOdds[k][1][7]) != "undefined" && arrOdds[k][1][7] != "") {
            html.push("<td bgColor=#FEFFEE>" + arrOdds[k][1][7] + "</td>");
            html.push("<td bgColor=#FEFFEE>" + Goal2GoalOU(arrOdds[k][1][8]) + "</td>");
            html.push("<td bgColor=#FEFFEE>" + arrOdds[k][1][9] + "</td>");
        }
        else {
            html.push("<td bgColor=#FEFFEE></td>");
            html.push("<td bgColor=#FEFFEE></td>");
            html.push("<td bgColor=#FEFFEE></td>");
        }
        html.push("<td rowspan=" + ((st > 0 || st == -1) && arrOdds[k][0] == 3 ? "3" : "2") + ">" + "<a href=//vip.titan007.com/changeDetail/handicap.aspx?id=" + sid + "&companyID=" + arrOdds[k][0] + "  target=_blank><img src=../Images/t2.gif width=11 height=12  border=0/></a></td>");
        html.push("</tr>");
        if ((st > 0 || st == -1) && arrOdds[k][0] == 3 && arrOdds[k].length == 4) {
            html.push("<tr bgcolor=#FFFFFF style=height:20px;>");
            html.push("<td bgcolor=#F2F9FD style='text-align:center;'>终</td>");
            if (typeof (arrOdds[k][3][4]) != "undefined" && arrOdds[k][3][4] != "") {
                html.push("<td>" + arrOdds[k][3][4] + "</td>");
                html.push("<td>" + arrOdds[k][3][5] + "</td>");
                html.push("<td>" + arrOdds[k][3][6] + "</td>");
            }
            else {
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
            }
            if (typeof (arrOdds[k][3][10]) != "undefined" && arrOdds[k][3][10] != "") {
                html.push("<td bgColor=#FEFFEE>" + arrOdds[k][3][10] + "</td>");
                html.push("<td bgColor=#FEFFEE>" + Goal2GoalOU(arrOdds[k][3][11]) + "</td>");
                html.push("<td bgColor=#FEFFEE>" + arrOdds[k][3][12] + "</td>");
                html.push("<td bgColor=#FEFFEE>1.85</td>");
            }
            else {
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
            }
            if (typeof (arrOdds[k][3][1]) != "undefined" && arrOdds[k][3][1] != "") {
                html.push("<td>" + arrOdds[k][3][1] + "</td>");
                html.push("<td>" + Goal2GoalOU(arrOdds[k][3][2]) + "</td>");
                html.push("<td>" + arrOdds[k][3][3] + "</td>");
                html.push("<td>" + (parseFloat(arrOdds[k][3][1]) + parseFloat(arrOdds[k][3][3])).toFixed(2) + "</td>");
            }
            else {
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
                html.push("<td></td>");
            }
            if (typeof (arrOdds[k][3][7]) != "undefined" && arrOdds[k][3][7] != "") {
                html.push("<td bgColor=#FEFFEE>" + arrOdds[k][3][7] + "</td>");
                html.push("<td bgColor=#FEFFEE>" + Goal2GoalOU(arrOdds[k][3][8]) + "</td>");
                html.push("<td bgColor=#FEFFEE>" + arrOdds[k][3][9] + "</td>");
            }
            else {
                html.push("<td bgColor=#FEFFEE></td>");
                html.push("<td bgColor=#FEFFEE></td>");
                html.push("<td bgColor=#FEFFEE></td>");
            }
            html.push("</tr>");
        }
        html.push("<tr style=height:20px;>");
        if ((st > 0 || st == -1) && arrOdds[k][0] == 3)
            html.push("<td bgcolor=#F2F9FD style='text-align:center;'><span style=color:#F60>滚球</span></td>");
        else if (st > 0 || st == -1)
            html.push("<td bgcolor=#F2F9FD style='text-align:center;'>终</td>");
        else
            html.push("<td bgcolor=#F2F9FD style='text-align:center;'><span style=color:#F60>即时</span></td>");
        if (typeof (arrOdds[k][2][4]) != "undefined" && arrOdds[k][2][4] != "") {
            html.push("<td bgcolor=#ffffff><strong>" + arrOdds[k][2][4] + "</strong></td>");
            html.push("<td bgcolor=#ffffff><strong>" + arrOdds[k][2][5] + "</strong></td>");
            html.push("<td bgcolor=#ffffff><strong>" + arrOdds[k][2][6] + "</strong></td>");
        }
        else {
            html.push("<td bgcolor=#ffffff>" + "</td>");
            html.push("<td bgcolor=#ffffff>" + "</td>");
            html.push("<td bgcolor=#ffffff>" + "</td>");
        }
        if (typeof (arrOdds[k][2][10]) != "undefined" && arrOdds[k][2][10] != "") {
            html.push("<td bgcolor=#FEFFEE><strong>" + arrOdds[k][2][10] + "</strong></td>");
            html.push("<td bgcolor=#FEFFEE><strong>" + Goal2GoalOU(arrOdds[k][2][11]) + "</strong></td>");
            html.push("<td bgcolor=#FEFFEE><strong>" + arrOdds[k][2][12] + "</strong></td>");
            html.push("<td bgcolor=#FEFFEE><strong>1.85</strong></td>");
        }
        else {
            html.push("<td bgcolor=#FEFFEE></td>");
            html.push("<td bgcolor=#FEFFEE></td>");
            html.push("<td bgcolor=#FEFFEE></td>");
            html.push("<td bgcolor=#FEFFEE></td>");
        }
        if (typeof (arrOdds[k][2][1]) != "undefined" && arrOdds[k][2][1] != "") {
            html.push("<td bgcolor=#ffffff><strong>" + arrOdds[k][2][1] + "</strong></td>");
            html.push("<td bgcolor=#ffffff><strong>" + Goal2GoalOU(arrOdds[k][2][2]) + "</strong></td>");
            html.push("<td bgcolor=#ffffff><strong>" + arrOdds[k][2][3] + "</strong></td>");
            html.push("<td bgcolor=#ffffff><strong>" + (parseFloat(arrOdds[k][2][1]) + parseFloat(arrOdds[k][2][3])).toFixed(2) + "</strong></td>");
        }
        else {
            html.push("<td bgcolor=#ffffff>" + "</td>");
            html.push("<td bgcolor=#ffffff>" + "</td>");
            html.push("<td bgcolor=#ffffff>" + "</td>");
            html.push("<td bgcolor=#ffffff>" + "</td>");
        }
        if (typeof (arrOdds[k][2][7]) != "undefined" && arrOdds[k][2][7] != "") {
            html.push("<td bgColor=#FEFFEE><strong>" + arrOdds[k][2][7] + "</strong></td>");
            html.push("<td bgColor=#FEFFEE><strong>" + Goal2GoalOU(arrOdds[k][2][8]) + "</strong></td>");
            html.push("<td bgColor=#FEFFEE><strong>" + arrOdds[k][2][9] + "</strong></td>");
        }
        else {
            html.push("<td bgColor=#FEFFEE>" + "</td>");
            html.push("<td bgColor=#FEFFEE>" + "</td>");
            html.push("<td bgColor=#FEFFEE>" + "</td>");
        }
        html.push("</tr>");
    }
    html.push("</table>");
    $_Our("iframeA").innerHTML = html.join("");
}

function showTotalScore(lang) {
    if (typeof (totalScore) == "undefined") return;
    var mainDiv = document.getElementById("cupScore");
    var arrData = new Array();
    arrData.push("<TABLE width='100%' border=0 align=center cellPadding=3 cellSpacing=1 borderColorLight=#ffffff borderColorDark=#666666 bgcolor=#CCCCCC><tr class=blue_t2 align='center'><td width='9%' height=25>排名</td><td  width='15%'>球队名称</td><td width='8%'>赛</td><td width='8%'>胜</td><td width='8%'>平</td><td width='8%'>负</td><td width='8%'>得</td><td width='8%'>失</td><td width='8%'>净</td><td width='8%'>附加积分</td><td width='10%'>总积分</td></tr>");
    var arrColorRefer = new Array();
    for (var i = 0; i < totalScore.length; i++) {
        var oneRecord = totalScore[i];
        var teamAndCard = showScoreTeam(oneRecord[3], oneRecord[2], lang);
        if (teamAndCard == '') continue;
        arrData.push("<tr align='center' bgcolor=#FFFFFF" + (oneRecord[2] == h2h_home || oneRecord[2] == h2h_away ? " class='onteam'" : "") + "><td bgcolor=#F4FBE9>" + oneRecord[1] + "</td><td align='left' bgcolor=#FCEEDE><a href='//zq.titan007.com/" + (lang == 1 ? "big" : "cn") + "/team/Summary/" + oneRecord[2] + ".html' target='_blank'>" + teamAndCard + "</a></td><td bgcolor=#F2F9FD>" + oneRecord[4] + "</td><td bgcolor=#F2F9FD>" + oneRecord[5] + "</td><td bgcolor=#F2F9FD>" + oneRecord[6] + "</td><td bgcolor=#F2F9FD>" + oneRecord[7] + "</td><td bgcolor=#F2F9FD>" + oneRecord[8] + "</td><td bgcolor=#F2F9FD>" + oneRecord[9] + "</td><td bgcolor=#F2F9FD>" + oneRecord[10] + "</td><td bgcolor=#F2F9FD>" + (oneRecord.length > 19 ? oneRecord[19] : "") + "</td><td bgcolor=#F2F9FD>" + (oneRecord[16] - oneRecord[17]) + "</td></tr>");
        //扣分说明
        if (oneRecord[18] != "") {
            arrData.push("<tr bgcolor='#F0F0F0'><td colspan='16'>注:" + oneRecord[18] + "</td></tr>");
        }
    }
    arrData.push("</table>");
    mainDiv.innerHTML = arrData.join('');
}
//积分榜显示球队
function showScoreTeam(redCardNum, teamID, lang) {
    var html = "";
    for (var i = 0; i < arrTeam.length; i++) {
        if (parseInt(arrTeam[i][0]) == teamID)
            html = arrTeam[i][1 + lang];
    }
    if (redCardNum != 0)
        html += "&nbsp;<span style=\"padding-bottom:0px; padding-top:0px; padding-left:2px; padding-right:2px; background-color:#F00;color:#fff;\">" + redCardNum + "</span>";
    return html;
}


var objPostion = function (width, height) {
    this.w = width;
    this.h = height;
}
function getWidth() {
    var winWidth = 0;
    var winHeight = 0;
    if (window.innerWidth)
        winWidth = window.innerWidth;
    else if ((document.body) && (document.body.clientWidth))
        winWidth = document.body.clientWidth;
    if (window.innerHeight)
        winHeight = window.innerHeight;
    else if ((document.body) && (document.body.clientHeight))
        winHeight = document.body.clientHeight;
    //        if (document.documentElement && document.documentElement.clientWidth) {
    //            winWidth = document.documentElement.clientWidth;
    //            winHeight = document.documentElement.clientHeight;
    //        }
    var obj = new objPostion(winWidth, winHeight);
    return obj;
}
function debounce(callback, delay, context) {
    if (typeof (callback) !== "function") {
        return;
    }
    delay = delay || 150;
    context = context || null;
    var timeout;
    var runIt = function () {
        callback.apply(context);
    };
    return (function () {
        window.clearTimeout(timeout);
        timeout = window.setTimeout(runIt, delay);
    });
}
function changeState() {
    var obj = getWidth();
    var winWidth = obj.w;
    var objDiv = document.getElementById("analyMap");
    objDiv.style.display = "";
    changePostion();
    //if (winWidth < 1080)
    //    objDiv.style.display = "none";
    //else {
    //    objDiv.style.display = "";
    //    changePostion();
    //}
}
function changePostion() {
    var top = 200;
    var obj = getWidth();
    var winWidth = obj.w;
    var winHeight = obj.h;
    var doc_scrollTop = document.body.scrollTop;
    if (doc_scrollTop == 0) doc_scrollTop = document.documentElement.scrollTop;
    var obj = document.getElementById("analyMap");
    if (navigator.userAgent.indexOf("MSIE") > 0 && navigator.userAgent.indexOf("MSIE 6.0") > 0) {
        obj.style.cssText = "position: absolute;top:" + (doc_scrollTop + top) + "px;right: " + ((winWidth - 865) / 2 - 50) + "px;";
    }
    else {
        obj.style.cssText = "position: fixed; top:" + top + "px; right: " + ((winWidth - 865) / 2 - 50) + "px;";
    }
}
function showAnalysNews() {
    var html = '<table  cellspacing="1" bordercolordark="#666666" cellpadding="3" width="100%" bgcolor="#cccccc" bordercolorlight="#ffffff" border="0">';
    for (var i = 0; i < an_zqList.length; i += 2) {
        var new1 = an_zqList[i];
        var new2 = an_zqList[i + 1]
        html += '<tr bgcolor="#ffcccc"><td  bgcolor="#fefaf8" height="25"><span style="padding-left:20px;"><a href="' + new1[1] + '" target="_blank">' + new1[0] + '</a></span></td><td bgcolor="#f2f9fd"><span style="padding-left:20px;"><a href="' + new2[1] + '" target="_blank">' + new2[0] + '</a></span></td></tr>';
    }
    $_Our("analyNewsTable").innerHTML = html + "</table>";
}
function odds_op_set(obj) {
    var theValue = obj.options[obj.selectedIndex].value;
    var opOddsList = obj.getAttribute("allodds").split(";");
    var hasOdds = false;
    for (var i = 0; i < opOddsList.length; i++) {
        var subList = opOddsList[i].split(",");
        if (subList[0] == theValue) {
            hasOdds = true;
            for (var k = 1; k < subList.length; k++) {
                if (subList[k] == "0") subList[k] = "";
                if (k <= 3) $_Our("oo_" + k).innerHTML = subList[k];
                else if (k > 3 && k <= 6) {
                    if (subList[k] != "") $_Our("gl_" + (k - 3)).innerHTML = subList[k] + "%";
                    else $_Our("gl_" + (k - 3)).innerHTML = "";
                }
                else {
                    if (subList[k] != "") $_Our("o_fh").innerHTML = subList[k] + "%";
                    else $_Our("o_fh").innerHTML = "";
                }
            }
        }
    }
    if (!hasOdds) {
        for (var k = 1; k < 8; k++) {
            if (k <= 3) $_Our("oo_" + k).innerHTML = "";
            else if (k > 3 && k <= 6)
                $_Our("gl_" + (k - 3)).innerHTML = "";
            else
                $_Our("o_fh").innerHTML = "";
        }
    }
}
function setIsShow(ID, sID) {
    try {
        $_Our(ID).style.display = soccer_scheduleid.indexOf(sID) == -1 ? "none" : "";
        $_Our("li_detailCount").style.display = ((arrLeague[0] > 0 || arrLeague[0] == -1) ? "" : "none");
    }
    catch (e) { }
}
function setAnalyMenu(sID) {
    var isFromQb = getUrlParam("sd") != null && getUrlParam("sd").toLocaleLowerCase() == "1";
    var html = (typeof (Ba_Soccer) == 'undefined' || Ba_Soccer.indexOf(sID) == -1 ? '' : '<li><a href="//ba2.titan007.com/linkmatch/1/' + sID + '.html' + (isFromQb ? "?sd=1" : "") + '" target="_blank" class="hotIcon">' + (lang == 1 ? "方案" : "方案") + '</a></li>');
    html += (typeof (jincaituijian) == 'undefined' || jincaituijian.indexOf(sID) == -1 ? '' : '<li><a href="//ai.titan007.com/JingCai/index.aspx?id=' + sID + (isFromQb ? "&sd=1" : "") + '" target="_blank">' + (lang == 1 ? "串關" : "串关") + '</a></li>');
    html += (typeof (soccer_scheduleid) == 'undefined' || soccer_scheduleid.indexOf(sID) == -1 ? '' : '<li><a href="//guess2.titan007.com/tuijian/' + sID + '.html' + (isFromQb ? "?sd=1" : "") + '">' + (lang == 1 ? "推薦" : "推荐") + '</a></li>');
    html += '<li class="ontab"><a href="' + sID + 'cn.htm" class="nobg">分析</a></li>';
    html += '<li><a href="//vip.titan007.com/AsianOdds_n.aspx?id=' + sID + '&l=0' + (isFromQb ? "&sd=1" : "") + '">' + (lang == 1 ? "亚讓" : "亚让") + '</a></li>';
    html += '<li><a href="//vip.titan007.com/OverDown_n.aspx?id=' + sID + '&l=0' + (isFromQb ? "&sd=1" : "") + '">' + (lang == 1 ? "進球數" : "进球数") + '</a></li>';
    html += '<li><a href="//vip.titan007.com/Corner.aspx?id=' + sID + '&l=0' + (isFromQb ? "&sd=1" : "") + '">角球</a></li>';
    html += '<li><a href="//1x2.titan007.com/oddslist/' + sID + '.htm' + (isFromQb ? "?sd=1" : "") + '">' + (lang == 1 ? "勝平負" : "胜平负") + '</a></li>';
    //html += '<li><a href="//vip.titan007.com/betfa/single.aspx?id=' + sID + '&l=0">' + (lang == 1 ? "必發" : "必发") + '</a></li>';
    html += ((typeof (arrLeague) != 'undefined' && (arrLeague[7] == 1) || isFromQb=="1") ? '<li><a href="javascript:void(0);" onclick="showDetail(' + sID + ');" style="color:#2a9bff;">' + (lang == 1 ? "現場分析" : "现场分析") + '</a></li>' : '');
    html += '<li><a href="//users.titan007.com/member/MatchVIP.aspx?id=' + sID + '&kind=1' + (isFromQb ? "&sd=1" : "") + '">' + (lang == 1 ? "會員" : "会员") + '</a></li>';
    $_Our("odds_menu").innerHTML = html;
    if (typeof (vipTitle) != 'undefined' && document.getElementById("vipBannerDesc") != null)
        document.getElementById("vipBannerDesc").innerHTML = vipTitle;
}
function changeLangStatus() {
    try {
        var url = location.href;
        var lang = url.toLowerCase().indexOf("cn") != -1 ? 0 : url.toLowerCase().indexOf("sb") != -1 ? 2 : 1;
        document.getElementById("Language" + lang).className = "item on";
    }
    catch (e) { }
}
function isUserLoginCheck(cookiename) {
    if (document.cookie.indexOf("Auth=") != -1 || document.cookie.indexOf(";Auth=") != -1 || document.cookie.indexOf("; Auth=") != -1) {
        if (getCookie(cookiename).replace(/\s+/g, "") != "") {
            return true;
        } else
            return false;
    } else {
        var d = new Date();
        d.setTime(d.getTime() + (1000));
        var expires = 'expires=' + d.toUTCString();
        document.cookie = cookiename + '=new_value;path=/;domain=.titan007.com;' + expires;
        if (document.cookie.indexOf((cookiename + '=')) === -1) {
            return true;
        } else
            return false;
    }
}
//0未登录，1是会员，2不是会员
function checkUser() {
    if (window.location.href.indexOf("61.143.225") > 0)
        return 1;
    if (!isUserLoginCheck("Auth")) {
        return 0;
    }
    else {
        var loginObj = getCookie("loginsameinfo");
        if (loginObj != null && loginObj != "") {
            var longtime = Math.floor(new Date().getTime() / 1000);
            var decode = AES_Decrypt(atob(decodeURIComponent(loginObj)), "NTNhMDJjMTY1ZjU0OGM2OQ==", "NDhlM2Q3MmFhNmZjNmEzZA==")
            var entity = JSON.parse(decode);
            if (entity.isvip && entity.endtime > longtime) {
                return 1;
            }
            else {
                return 2;
            }
        }
        else {
            return 2;
        }
    }
}

function AddMemberHtml() {
    var html = new Array();     
    //html.push('<div class="vip-pop-up" id="flahsBg" style="display: none;">');
    html.push('<div id="newpopup">');
    html.push('<div class="text">开通会员解锁权益</div>');
    html.push('<div class="info"><a class="offbtn" href="javascript:void(0);" onclick="vipSubscribe(0)">取消</a><a class="onbtn" href="javascript:void(0);" onclick="vipSubscribe(1)">前往开通</a></div>');
    html.push('</div>');
    html.push('<div id="backgound"></div>');
    //html.push('</div>');
    var s3 = document.createElement("div");
    s3.className = "vip-pop-up";
    s3.id = "flahsBg";
    s3.style.display = "none";
    s3.innerHTML = html.join('');
    document.body.appendChild(s3, "div");
}
function vipSubscribe(type) {
    if (type == 1) {
        window.open("//users.titan007.com/member/VipRole.aspx");
        /*if (userLoginType == 0) {
            window.location.href = "//guess2.titan007.com/users/login.aspx?ReturnUrl=" + window.location.href;
        } else {
            window.location.href = "//users.titan007.com/user/VipRole.aspx";
        }*/
    }
    else {
        document.getElementById("flahsBg").style.display = "none";
    }
}
AddMemberHtml();
function referee_init_data(count) {
    showRefereeData(count);
}
var isBig = location.href.toLowerCase().indexOf("cn") == -1 && location.href.toLowerCase().indexOf("sb") == -1;
function showRefereeData(count) {
    var html = new Array();
    if (typeof (referData) == "undefined") return "";
    if (referData.length == 0) {
        document.getElementById("div_referee").innerHTML = '<table width="100%" border="0" cellpadding="1" cellspacing="1" bgcolor="#bbbbbb"><tr align="middle" bgcolor="#FFFFFF"><td height="45">暂无数据</td></tr></table>';
        return;
    }
    var c = count ? count : 10;
    var couchName = referData[0];
    var homeTeamId = h2h_home;
    var guestTeamId = h2h_away;
    var homeShowCount = c;
    var guestShowCount = c;
    var homeTotalCount = referData[1].length;
    var guestTotalCount = referData[2].length;
    homeShowCount = homeTotalCount < homeShowCount ? homeTotalCount : homeShowCount;
    guestShowCount = guestTotalCount < guestShowCount ? guestTotalCount : guestShowCount;
    var homeData = GetOneRefereeData(referData[1], homeTeamId, homeShowCount);
    var guestData = GetOneRefereeData(referData[2], guestTeamId, guestShowCount);

    html.push('<table id="table_referee" width="100%" border="0" cellpadding="1" cellspacing="1" bgcolor="#bbbbbb">');
    html.push('<tr align="middle" bgcolor="#FAF1DE" height="20"><td rowspan="3">' + couchName + '</td><td>' + (isBig ? "球隊" : "球队") + '</td><td>' + (isBig ? "場次" : "场次") + '</td><td>' + (isBig ? "勝" : "胜") + '</td><td>平</td><td>' + (isBig ? "負" : "负") + '</td><td>' + (isBig ? "上盤率" : "上盘率") + '</td><td>' + (isBig ? "場均黃牌" : "场均黄牌") + '</td></tr>');
    html.push('<tr align="middle" bgcolor="#ffffff"><td>' + hometeam + '</td><td>近' + homeShowCount + (isBig ? "場" : "场") + '</td><td>' + homeData[0] + '</td><td>' + homeData[1] + '</td><td>' + homeData[2] + '</td><td>' + homeData[3] + '</td><td>' + homeData[4] + '</td></tr>');
    html.push('<tr align="middle" bgcolor="#f0f0f0" ><td>' + guestteam + '</td><td>近' + guestShowCount + (isBig ? "場" : "场") + '</td><td>' + guestData[0] + '</td><td>' + guestData[1] + '</td><td>' + guestData[2] + '</td><td>' + guestData[3] + '</td><td>' + guestData[4] + '</td></tr>');
    html.push('</table>')
    document.getElementById("div_referee").innerHTML = html.join('');
    init_select_Referee("referee", c);
}
function GetOneRefereeData(data,teamId,count) {
    var yellowCount = 0, win = 0, draw = 0, lose = 0, letgoalWinCount = 0;
    for (var i = 0; i < count; i++) {
        var obj = data[i];
        if (teamId == obj[1]) {
            switch (parseInt(obj[3])) {
                case 1: win++; break;
                case 2: draw++; break;
                case 3: lose++; break;
            }
            yellowCount += parseInt(obj[4]);
            if (parseInt(obj[6]) == 1)
                letgoalWinCount++;
        }
        else {
            switch (parseInt(obj[3])) {
                case 3: win++; break;
                case 2: draw++; break;
                case 1: lose++; break;
            }
            yellowCount += parseInt(obj[5]);
            if (parseInt(obj[6]) == 3)
                letgoalWinCount++;
        }
    }
    var yellowAvg = count > 0 ? (yellowCount / count).toFixed(1) : 0;
    var letgoalWinRate = (count > 0 ? (letgoalWinCount / count * 100).toFixed(0) : 0) + "%";
    return [win, draw, lose, letgoalWinRate, yellowAvg];
}
function init_select_Referee(id, count) {
    var select = $_Our(id + "_s");
    select.options.length = 0;
    var homeTotalCount = referData[1].length;
    var guestTotalCount = referData[2].length;
    var totalCount = homeTotalCount > guestTotalCount ? homeTotalCount : guestTotalCount;
    for (var i = 0; i < totalCount; i++)
        select.options[i] = new Option((i + 1) < 10 ? " " + (i + 1) : (i + 1), (i + 1));
    if (select.options.length > 0)
        select.options[totalCount > count ? count - 1 : i - 1].selected = true;
    else
        select.options[0] = new Option(" " + 0, 0);
}