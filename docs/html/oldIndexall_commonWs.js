var isHomeIndex = window.location.href.toLocaleLowerCase().indexOf("index2in1") == -1 && window.location.href.toLocaleLowerCase().indexOf("oldindexall") == -1;
var isCompanyPage = window.location.href.toLocaleLowerCase().indexOf("index2in1") != -1;
var useIsChoose = 0;
function isLocalStorageAvailable() {
    var test = 'test';
    try {
        localStorage.setItem(test, test);
        localStorage.removeItem(test);
        return true;
    } catch (e) {
        return false;
    }
}
function getLocalStorage(key) {
    var val = null;
    if (localStorageEnable) {
        var itemStr = localStorage.getItem(key);
        if (itemStr != null) {
            var item = JSON.parse(itemStr);
            var now = new Date();
            if (now.getTime() > item.expiry) {
                localStorage.removeItem(key);
            }
            else
                val = item.value;
        }        
    }
    else {
        val = getCookie(key);
    }
    return val;
}
function writeLocalStorage(key, value, expiryTime) {
    if (localStorageEnable) {
        if (expiryTime == undefined)
            expiryTime = 365 * 3600000;
        var now = new Date();
        var item = {
            value: value,
            expiry: now.getTime() + expiryTime,
        };
        localStorage.setItem(key, JSON.stringify(item));
    }
    else {
        writeCookie(key, value);
    }
}
function delLocalStorage(key) {
    if (localStorageEnable)
        localStorage.removeItem(key);
    else
        delCookie(key);
}
function existsCookie(key) {
    if (localStorageEnable) {
        var itemStr = localStorage.getItem(key);
        if (itemStr != null)
            return true;
    }
    else if (document.cookie.indexOf(key) != -1)
        return true;
    else return false;
}
var localStorageEnable = isLocalStorageAvailable();
var isChooseMatch = existsCookie("Bet007live_hiddenID");
var companyScheduleIdList = "";
var cupImportantList = ",", cupImportantSIDList = "", cupHidenSIDList = "";
var staticUrl = "//livestatic.titan007.com/";
var isFirstLoad = true;

//var staticUrl = "";
function IsTest() {   
    var re = /(\d+)\.(\d+)\.(\d+)\.(\d+)/;//正则表达式
    if (re.test(window.location.href)) {
        staticUrl = "";
        return true;
    }
    else
        return false;
    
}
var isShowConsole = IsTest();
function IEVersion() {
    var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串  
    var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1; //判断是否IE<11浏览器  
    var isEdge = userAgent.indexOf("Edg") > -1 && !isIE; //判断是否IE的Edge浏览器  
    var isIE11 = userAgent.indexOf('Trident') > -1 && userAgent.indexOf("rv:11.0") > -1;
    if (isIE) {
        var reIE = new RegExp("MSIE (\\d+\\.\\d+);");
        reIE.test(userAgent);
        var fIEVersion = parseFloat(RegExp["$1"]);
        if (fIEVersion >= 7)
            return fIEVersion;
        else
            return 6;//IE版本<=7
    }
    else if (isEdge)
        return 12;//edge
    else if (isIE11)
        return 11; //IE11  
    else
        return -1;//不是ie浏览器   
}
function isSupportOgg() {
    var tmp = document.createElement('audio');
    return tmp.canPlayType && "" != tmp.canPlayType('audio/ogg;codecs="vorbis"');
}
var ieNum = 0;
try {
    if (document.all && typeof (document.documentMode) != "undefined")
        ieNum = document.documentMode;
}
catch (e) {
    ieNum = 0;
}
//定义Config
var Config = new Object();
Config.language = 2;
Config.rank = 0;
Config.explain = 1;
Config.redcard = 1;
Config.showYellowCard = 1;
Config.detail = 1;
Config.vs = 1;
Config.sound = 0;
Config.guestSound = 0;
Config.winLocation = 0;
Config.style = 0;
Config.oddsSound = 0;
Config.showSbOddsDetail = 1;
//Config.orderBy = 1; //1:按时间排;2:搂联赛排
Config.oldOrNew = 1; //1:旧版;2:新版;
//Config.showLeagueScore = 0;
Config.haveLetGoal = 1;
Config.haveTotal = 1;
Config.haveEurope = 0;
Config.isSimple = 1;
Config.cornerPopup = 1;
Config.onlyTopShowWin = 0;
Config.bfOddsShowLetGoal = true;
//Config.oddsColumnIndexAdd = window.location.href.toLocaleLowerCase().indexOf("index2in1") != -1 ? 0 : 1;
Config.oddsColumnIndexAdd = 1;
Config.userAgent = navigator.userAgent.toLowerCase();
Config.isBgsound = Config.userAgent.indexOf("compatible") > -1 && Config.userAgent.indexOf("msie") > -1 && ieNum < 9;
Config.isOgg = !Config.isBgsound && isSupportOgg();
Config.touchEventName = /i(phone|p(o|a)d)/.test(Config.userAgent) ? "touchstart" : "touchend";
Config.soundId_IE8 = "bgsound_bf";
Config.extendUrl_ba = "";
Config.extendUrl_ba2 = "";
Config.extendUrl_ba3 = "";
Config.extendUrl_ba3 = "";
Config.IEVer = IEVersion();
Config.IsIE = Config.IEVer > -1 && Config.IEVer < 12;
Config.OddsScheduleIDList = "";
Config.oddsLastIndex = "";
Config.sclassType = 0;//0为所有比赛，1为足彩，2为竞足，3是北单
Config.secondSclassType = 0;
Config.hiddenAllMatch = false;
Config.concernCount = 0;//置顶赛事数量
Config.isFirstLoadAliasFile = true;
Config.isFirstLoadPanluFile = true;
Config.isFristLoadSbCornerFile = true;
Config.isFirstLoadDetailFile = true;
Config.isFirstLoadSbDetailFile = true;
Config.oddsChangeFile = "";
Config.isHideAd = false;
Config.selectConditonType = 1;//1为联赛筛选，2为国家筛选，3为盘口筛选，4为条件筛选
Config.getCookie = function (type) {
    var Cookie = getCookie("win007BfCookie");
    if (Cookie == null) Cookie = "";
    var Cookie = Cookie.split("^");
    if (Cookie.length != 20) {
        writeCookie("win007BfCookie", null);
        useIsChoose = 0;
    }
    else {
        useIsChoose = 1;
        this.language = parseInt(Cookie[0]);
        this.rank = parseInt(Cookie[1]);
        this.explain = parseInt(Cookie[2]);
        this.redcard = parseInt(Cookie[3]);
        this.showYellowCard = parseInt(Cookie[4]);
        this.detail = parseInt(Cookie[5]);
        this.vs = parseInt(Cookie[6]);
        this.sound = parseInt(Cookie[7]);
        this.winLocation = parseInt(Cookie[8]);
        this.style = parseInt(Cookie[9]);
        //3的配色已取消，默认是0
        this.style = this.style == 3 ? 0 : this.style;
        this.oddsSound = parseInt(Cookie[10]);
        this.guestSound = parseInt(Cookie[11]);
        this.showSbOddsDetail = parseInt(Cookie[12]);
        //this.orderBy = parseInt(Cookie[13]);
        this.oldOrNew = parseInt(Cookie[13]);
        this.haveLetGoal = parseInt(Cookie[14]);
        this.haveTotal = parseInt(Cookie[15]);
        this.haveEurope = parseInt(Cookie[16]);
        this.isSimple = parseInt(Cookie[17]);
        this.cornerPopup = parseInt(Cookie[18]);
        this.onlyTopShowWin = parseInt(Cookie[19]);
    }
    Config.isHideAd = (getCookie("ishidepcad") != "" && getCookie("ishidepcad") == "1");
    getConditonList(1);
    Config.extendUrl_ba = (typeof (ba_pubid) != 'undefined' ? "<a href='http://ba2.titan007.com/" + ba_pubid + "/" + ba_themeid + ".html' target=_blank style='color:blue'><b>" + (Config.language == 1 ? "專家精選每日賽事分析" : "专家精选每日赛事分析") + "</b></a>" : "");
    Config.extendUrl_ba2 = "";// (typeof (fans_pubid) != 'undefined' ? "<a href='http://ba2.titan007.com/" + fans_pubid + "/" + fans_themeid + ".html' target=_blank style='color:blue'><b>" + (Config.language == 1 ? "中場不休推薦投稿有獎 馬上參與(點擊進入活動專帖)" : "中场不休推荐投稿有奖 马上参与(点击进入活动专帖)") + "</b></a>" : "");
    Config.extendUrl_ba3 = "<a href='http://v.titan007.com/' target=_blank style='color:red'><b>" + (Config.language == 1 ? 'V顧問帶您分析英超新賽季' : 'V顾问带您分析英超新赛季') + "</b></a>";
    Config.extendUrl_ba4 = "<a href='http://users.titan007.com/users/register.aspx?from=http://ba2.titan007.com/133/11796085.html' target=_blank style='color:red'><b>" + (Config.language == 1 ? '新用戶尊享' : '新用户尊享') + "</b></a>";
}
Config.setStates = function (type) {
    try {
        //document.getElementById("Language" + Config.language).className = "lgg";
        if (this.rank == 1) document.getElementById("rank").checked = true;
        if (this.explain == 0) document.getElementById("explain").checked = false;
        if (this.redcard == 0) document.getElementById("redcard").checked = false;
        if (this.showYellowCard == 0) document.getElementById("showYellowCard").checked = false;
        //if (this.detail == 0) document.getElementById("detail").checked = false;
        if (this.vs == 0) document.getElementById("vs").checked = false;
        //if (this.sound == -1) document.getElementById("soundCheck").checked = false;
        // if (this.sound > 0)
        document.getElementById("sound").value = this.sound;
        //if (this.guestSound > 0)
        document.getElementById("guestSound").value = this.guestSound;
        if (this.winLocation == -1) document.getElementById("windowCheck").checked = false;
        if (this.winLocation > 0) document.getElementById("winLocation").value = this.winLocation;
        if (this.style > 0) document.getElementById("style").value = this.style;
        if (type != "oldindex") {
            //if (this.oddsSound == 1) document.getElementById("oddsSound").checked = true;
            document.getElementById("checkLet").checked = (Config.haveLetGoal == 1);
            document.getElementById("checkEu").checked = (Config.haveEurope == 1);
            document.getElementById("checkTotal").checked = (Config.haveTotal == 1);
        }
        if (this.showSbOddsDetail == 0) document.getElementById("showSbOddsDetail").checked = false;//type == "index" && 
        if (this.isSimple == 1) {
            document.getElementById("button6").className = "btn33";
            document.getElementById("button7").className = "btn33_on";
        }
        else if (this.isSimple == 0) {
            document.getElementById("button6").className = "btn33_on";
            document.getElementById("button7").className = "btn33";
        }
        else {
            document.getElementById("button6").className = "btn33";
            document.getElementById("button7").className = "btn33";
        }
        if (this.cornerPopup == 0) document.getElementById("cornerPopup").checked = false;
        if (this.onlyTopShowWin == 1) document.getElementById("onlyTopShowWin").checked = true;
        Config.setLangName();
        //if (type == "index" && this.showLeagueScore == 0) document.getElementById("showLeagueScore").checked = false;
        //        if (type == "index") {
        //            if (this.orderBy == 1)
        //                document.getElementById("orderbyChange").value = (this.language == 1 ? "按聯賽選擇" : "按联赛选择");
        //            else
        //                document.getElementById("orderbyChange").value = (this.language == 1 ? "按時間選擇" : "按时间选择");
        //        }
    }
    catch (e) { }
}
Config.writeCookie = function () {
    var value = this.language + "^" + this.rank + "^" + this.explain + "^" + this.redcard + "^" + this.showYellowCard + "^" + this.detail + "^" + this.vs + "^" + this.sound + "^" + this.winLocation + "^" + this.style + "^" + this.oddsSound + "^" + this.guestSound + "^" + this.showSbOddsDetail + "^" + this.oldOrNew + "^" + this.haveLetGoal + "^" + this.haveTotal + "^" + this.haveEurope + "^" + this.isSimple + "^" + this.cornerPopup + "^" + this.onlyTopShowWin;
    writeCookie("win007BfCookie", value);
    useIsChoose = 1;
}
Config.langName = "简体<i>&nbsp;</i>,繁體<i>&nbsp;</i>,Crow*<i>&nbsp;</i>".split(',');
Config.setLangName = function () {
    document.getElementById("langName").innerHTML = this.langName[this.language];
}
function writeConditionCookie(kind, oddsType, idList,sclassType) {
    writeCookie2("FS007Filter", kind + "^" + oddsType + "^" + idList + "^" + sclassType, false, GetCookieTime());
    useIsChoose = 1;
}

function getConditonList(kind) {//获取筛选COOKIE。用户没选择时默认赛事精简    
    var arr = new Array(4);
    var Fs007Filter = getCookie("FS007Filter");
    Fs007Filter = Fs007Filter == null ? '' : Fs007Filter;
    if (Fs007Filter != "") {
        var arrFilter = Fs007Filter.split("^");
        Config.selectConditonType = arrFilter[0];
        if (arrFilter.length < 4)
            arrFilter[3] = 0;
        if (parseInt(arrFilter[0]) == kind) {
            arr = arrFilter;
            if (kind == 1 && parseInt(arr[1]) >= 5)
                arr[1] = 0;
            if (kind == 1 && arr[2] == '_')
                Config.hiddenAllMatch = true;
        }
        else {
            arr[0] = 0;
            arr[1] = kind == 3 ? '0' : '';
            arr[2] = '';
        }
        arr[3] = arrFilter[3];
        Config.sclassType = arr[3];
        Config.secondSclassType = arr[1];
    }
    else {//默认赛事精简
        arr[0] = 1;
        arr[1] = '';
        arr[2] = '';
        arr[3] = 0;
        Config.sclassType = 0;
        Config.secondSclassType = 0;
    }
    return arr;
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
function getMatchState(state) {
    if (state.toString() == "") return "";
    var arrState;
    try {
        arrState = state_ch[parseInt(state) + 14].split(",");
    }
    catch (ex) {
        return "";
    }
    return arrState.length < 2 ? "" : arrState[lang];
}
function setOldOrNew(l) {
    //    if (Config.oldOrNew == l) return;
    Config.oldOrNew = l;
    Config.writeCookie();
    changeOldOrNew(l);
    //SetTrBgColor();
}
function changeOldOrNew(l) {
    var name = location.href.substring(location.href.lastIndexOf("/") + 1);
    //if (name.indexOf('.') != -1 && name.indexOf("all") == -1) return;
    if (name.indexOf("old") != -1 && l == 1) return;
    if ((name.indexOf('.') == -1 || name.indexOf("old") == -1) && name.indexOf("2in1") == -1 && l == 2) return;
    if (l == 1)//旧版
    {
        if (Config.language == 1)
            name = "/oldIndexall_big.aspx";
        else
            name = "/oldIndexall.aspx";

    }
    else//新版
    {
        if (Config.language == 1)
            name = "/indexall_big.aspx";
        else
            name = "/indexall.aspx";
    }
    location.href = name;
}
var hsOddsCompany = new Hashtable();
function initOddsCompanyName() {
    var oddsCompanyIds = new Array(1, 3, 8, 12, 14, 17, 22, 23, 24, 31, 35, 42, 4);
    var oddsCompanyNames = Config.language == 1 ? new Array('澳*', 'Crow*', '36*', '易*', '偉*', '明*', '10*', '金宝*', '12*', '利*', '盈*', '18*', '立*') : new Array('澳*', 'Crow*', '36*', '易*', '伟*', '明*', '10*', '金宝*', '12*', '利*', '盈*', '18*', '立*');
    for (var i = 0; i < oddsCompanyIds.length; i++) {
        hsOddsCompany.add(oddsCompanyIds[i], oddsCompanyNames[i]);
    }
}
var lang = 0; //方便取数据
//var resultName = "角球,黄牌,红牌,射门,射正,射门不中,射门被挡,任意球,控球率,传球,传球成功率,犯规,越位,头球,头球成功,救球,铲球,换人数,过人,界外球,中柱,角球数（加时）,越位（加时）,乌龙球数,黄牌数（加时）,守门员出击,丟球,成功抢断,阻截,成功传中,助攻,换人数（加时）,长传,短传,先开球,第一张黄牌,最后一张黄牌,第一个换人,最后一个换人,第一个角球,最后一个角球,第一个越位,最后越位".split(',');
//var resultName_big = "角球,黃牌,紅牌,射門,射正,射門不中,射門被擋,任意球,控球率,傳球,傳球成功率,犯規,越位,頭球,頭球成功,救球,鏟球,換人數,過人,界外球,中柱,角球數（加時）,越位（加時）,烏龍球數,黃牌數（加時）,守門員出擊,丟球,成功搶斷,阻截,成功傳中,助攻,換人數（加時）,長傳,短傳,先開球,第壹張黃牌,最後壹張黃牌,第壹個換人,最後一个換人,第壹個角球,最後壹個角球,第壹個越位,最後越位".split(',');
var resultName = "先开球,第一个角球,第一张黄牌,射门,射正,犯规,角球,角球(加时),任意球,越位,乌龙球数,黄牌,黄牌数(加时),红牌,控球时间,头球,救球,守门员出击,丟球,成功抢断,阻截,长传,短传,助攻,成功传中,第一个换人,最后换人,第一个越位,最后越位,换人数,最后角球,最后黄牌,换人数(加时), 越位(加时),射门不中,中柱,头球成功,射门被挡,铲球,过人,界外球,传球,传球成功率".split(',');
var resultName_big = "先開球,第壹個角球,第壹張黃牌,射門,射正,犯規,角球,角球(加時),任意球,越位,烏龍球數,黃牌,黃牌(加時),紅牌,控球時間,頭球,救球,守門員出擊,丟球,成功搶斷,阻截,長傳,短傳,助攻,成功傳中,第壹個換人,最後換人,第壹個越位,最後越位,換人數,最後角球,最後黃牌,換人數(加時), 越位(加時),射門不中,中柱,頭球成功,射門被擋,鏟球,過人,界外球,傳球,傳球成功率".split(',');
var flash_sound = Array(5);
flash_sound[0] = "bf_img/sound";
flash_sound[1] = "bf_img/notice";
flash_sound[2] = "bf_img/base";
flash_sound[3] = "bf_img/deep";
flash_sound[4] = "bf_img/oddssound";

function ShowFlash(id, n, type) {
    voicePlay(id, n, type, false);
    window.setTimeout("timecolors(" + id + ")", 120000);
}
function voicePlay(id, n, type, isSelect) {//isSelect:用于用户切换提示声音时播放
    try {
        var sound = (type == 1 ? Config.sound : Config.guestSound);
        if (sound >= 0 && (parseInt(A[n][13]) >= -1 || isSelect)) {
            if ((id > 0 && document.getElementById("tr1_" + id).style.display != "none") || isSelect) {
                if (Config.isBgsound) {
                    var dom = document.getElementById(Config.soundId_IE8);
                    if (dom != null)
                        dom.src = flash_sound[sound] + ".mp3";//设置一个背景音乐文件;
                }
                else {
                    var audioName = type == 1 ? "audio_home" : "audio_guest";
                    document.getElementById(audioName).play();
                }
            }
        }
    } catch (e) { };
}
function soundInit() {
    if (Config.isBgsound) {
        var dom = document.getElementById(Config.soundId_IE8);
        if (dom == null) {
            dom = document.createElement("bgsound");//创建背景音乐
            dom.id = Config.soundId_IE8;
            document.body.appendChild(dom);
        }
    }
    else {
        if (Config.sound >= 0) {
            setSoundHtml(true);
            document.getElementById("audio_home").load();
        }
        if (Config.guestSound >= 0) {
            setSoundHtml(false);
            document.getElementById("audio_guest").load();
        }
        window.removeEventListener(Config.touchEventName, soundHandle, true);
        if (Config.sound >= 0 || Config.guestSound >= 0)
            window.addEventListener(Config.touchEventName, soundHandle, true);
    }
}
function setSoundHtml(isHome) {
    var sound = isHome ? Config.sound : Config.guestSound;
    var soundStr = '<audio id="' + (isHome ? "audio_home" : "audio_guest") + '" style="display: none">';
    soundStr += '<source src="' + flash_sound[sound] + (Config.isOgg ? ".ogg" : ".mp3") + '" type="' + (Config.isOgg ? "audio/ogg" : "audio/mpeg") + '"/>';
    soundStr += '</audio>';
    document.getElementById((isHome ? "soundsHome" : "soundsGuest")).innerHTML = soundStr;
}
function soundHandle() {
    if (Config.sound >= 0)
        document.getElementById("audio_home").load();
    if (Config.guestSound >= 0)
        document.getElementById("audio_guest").load();
    if (Config.sound >= 0 || Config.guestSound >= 0)
        window.removeEventListener(Config.touchEventName, soundHandle);
}
function ShowOddsSound() {
    //var ieVersion = "-1";
    //var ua = navigator.userAgent.toLowerCase();
    //if (window.ActiveXObject)
    //    ieVersion = ua.match(/msie ([\d.]+)/)[1];
    //if (parseFloat(ieVersion) > 0 && parseFloat(ieVersion) < 6)
    //    document.getElementById("flashsound").innerHTML = "<object classid='clsid:D27CDB6E-AE6D-11cf-96B8-444553540000' codebase='http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,0,0' width='1' height='1'><param name='movie' value='" + flash_sound[Config.oddsSound] + "'><param name='quality' value='high'><param name='wmode' value='transparent'><embed src='" + flash_sound[Config.oddsSound] + "' quality='high' pluginspage='http://www.macromedia.com/go/getflashplayer' type='application/x-shockwave-flash' width='1' height='1'></embed></object>";
    //else
    //    document.getElementById("flashsound").innerHTML = "<embed src='" + flash_sound[Config.oddsSound] + "' quality='high' pluginspage='http://www.macromedia.com/go/getflashplayer' type='application/x-shockwave-flash' width='1' height='1'></embed>";
}
var lastUpdateTime, oldUpdateTime = "";
var lastUpdateFileTime = 0;
var hiddenID = "_";
var concernId = "_";
var bg1 = "#FFFDF3";
var bg2 = "#F0F0F0";
var pk = Array(60);
var macName = new Array()
var loadDetailFileTime = new Date();
var loaded = 0, LoadTime = 0, notifyTimer, matchType = -1, runtimeTimer;
var oXmlHttp = zXmlHttp.createRequest();
var oddsHttp = zXmlHttp.createRequest();
var conditionHttp = zXmlHttp.createRequest();
var oldOddsXML = '', getoddsxmlTimer;
var sData = new Object();
var sCornerData = new Object();
var oldXML = "", oldCornerXml = "";
var showCont = 0;
var showCornerCont = 0;
var flashTimer, bfOddsTimer;
var tempA = new Array();

//var T = new Object();//别名表对象

function SortData() {
    var index = Config.sclassType == 1 ? 58 : (Config.sclassType == 2 ? 57 : 59);
    
    if (concernId != null && concernId!="_") {
        temp = new Array();
        Config.concernCount = 0;
        var j = 1;
        /*archived[0] = ",";*/
        var tempCount = matchcount;
        if (Config.sclassType == 0) {//初始化数组
            A.splice(0, A.length);
            A = A.concat(tempA);
        }
        for (var i = 1; i <= tempCount; i++) {
            if (concernId.indexOf("_" + A[i][0] + "_") != -1) {//对置顶临时数组赋值
                temp[j] = A[i];
                A.splice(i, 1);
                tempCount--;
                i--;
                j++;
                Config.concernCount++;
            }
        }
        if (temp.length > 1) {//合并临时置顶数组和普通数据数组
            //document.getElementById("concernCount").innerHTML = archived.length - 1;
            if (Config.sclassType != 0) {//按竞彩足彩单场排序
                temp.sort(sclassSort(index));
                var d = temp.pop();
                temp.unshift(d);
                A.sort(sclassSort(index));
                A.pop();
                var finishTemp = new Array();
                var tempCount2 = A.length;
                var k = 0;
                for (var i = 0; i < tempCount2; i++) {
                    if (parseInt(A[i][13]) < 0) {
                        finishTemp[k] = A[i];
                        A.splice(i, 1);
                        tempCount2--;
                        i--;
                        k++;
                    }
                }
                if (finishTemp.length > 0) {
                    A = A.concat(finishTemp);
                }
                A = temp.concat(A);
            } else {
                A.splice(0, 1);
                A = temp.concat(A);
            }
        } else {
            if (Config.sclassType != 0) {
                A.sort(sclassSort(index));
                var finishTemp = new Array();
                var tempCount2 = A.length;
                var k = 0;
                var d = A.pop();
                A.unshift(d);
                for (var i = 1; i < tempCount2; i++) {
                    if (parseInt(A[i][13]) < 0) {
                        finishTemp[k] = A[i];
                        A.splice(i, 1);
                        tempCount2--;
                        i--;
                        k++;
                    }
                }
                if (finishTemp.length > 0) {
                    A = A.concat(finishTemp);
                }
            }
        }
    } else {
        if (Config.sclassType != 0) {
            A.sort(sclassSort(index));
            var finishTemp = new Array();
            var tempCount2 = A.length;
            var k = 0;
            var d = A.pop();
            A.unshift(d);
            for (var i = 1; i < tempCount2; i++) {
                if (parseInt(A[i][13]) < 0) {
                    finishTemp[k] = A[i];
                    A.splice(i, 1);
                    tempCount2--;
                    i--;
                    k++;
                }
            }
            if (finishTemp.length > 0) {
                A = A.concat(finishTemp);
            }
        }
        else {
            A.splice(0, A.length);
            A = A.concat(tempA);
        }
    }
}
function sclassSort(i) {
    if (i == 57) {
        return function (a, b) {
            return a[i].localeCompare(b[i]);
        }
    }
    else {
        return function (a, b) {
            var v1 = a[i];
            var v2 = b[i];
            return v1 - v2;
        }
    }
}
function getAllMacName() {
    for (var i = 1; i <= matchcount; i++) {
        macName[i] = new Array()
        macName[i][0] = "";
        macName[i][1] = "";
        macName[i][2] = "";
        macName[i][3] = "";
    }
    if (Config.language == 2) {
        try {
            for (i = 0; i < T.length; i++) {
                if (T[i][0] == 3) {
                    for (var j = 1; j <= matchcount; j++) {
                        if (A[j][6] == T[i][1]) {
                            macName[j][2] = T[i][2];
                            break;
                        }
                        if (A[j][6] == T[i][1] + "<font color=#880000>(中)</font>") {
                            macName[j][2] = T[i][2] + "<font color=#880000>(中)</font>";
                            break;
                        }
                        else if (A[j][9] == T[i][1]) {
                            macName[j][3] = T[i][2];
                            break;
                        }
                    }
                }
            }
        }
        catch (e) { }
    }
    for (i = 1; i <= matchcount; i++) {
        if (macName[i][0] == "")
            macName[i][0] = A[i][6].split("<")[0];
        if (macName[i][1] == "")
            macName[i][1] = A[i][9].split("<")[0];
        if (macName[i][2] == "")
            macName[i][2] = A[i][5];
        if (macName[i][3] == "")
            macName[i][3] = A[i][8];
    }
}
function getTeamName(i, t, cId, t2) {//t2 1:新版,旧版;2:2合1
    if (cId == 1 || cId == 3) {
        var key1 = A[i][37] + "_" + cId, key2 = A[i][38] + "_" + cId;
        if (Config.language < 2) {
            if (t2 == 1 || Config.language == 1) {
                if (t == 1)
                    return A[i][5 + Config.language]; //主队
                else
                    return A[i][8 + Config.language]; //客队
            }
            else {
                if (t == 1) {
                    if (A[i][5 + lang].indexOf("(中)") != -1)
                        return typeof (T[key1]) != "undefined" ? T[key1][0] + "<font color=#880000>(中)</font>" : A[i][5 + lang];
                    else
                        return typeof (T[key1]) != "undefined" ? T[key1][0] : A[i][5 + lang];
                }
                else
                    return typeof (T[key2]) != "undefined" ? T[key2][0] : A[i][8 + lang];
            }
        }
        else if (Config.language == 2) {
            if (t == 1) {
                if (A[i][5 + lang].indexOf("(中)") != -1)
                    return typeof (T[key1]) != "undefined" ? T[key1][0] + "<font color=#880000>(中)</font>" : A[i][5 + lang];
                else
                    return typeof (T[key1]) != "undefined" ? T[key1][0] : A[i][5 + lang];
            }
            else
                return typeof (T[key2]) != "undefined" ? T[key2][0] : A[i][8 + lang];
        }
    }
    else {
        if (t == 1)
            return A[i][5 + lang]; //主队
        else
            return A[i][8 + lang]; //客队
    }
}
function timecolors(matchid) {
    try {
        var tr = document.getElementById("tr1_" + matchid);
        tr.cells[4].style.backgroundColor = "";
        tr.cells[6].style.backgroundColor = "";
    }
    catch (e) { }
}

function clearNotify(str) {
    var result;
    try {
        var re = new RegExp(str.replace("(", "\(").replace(")", "\)").replace("[", "\[").replace("]", "])"), "ig");
        var notify = document.getElementById("notify").innerHTML;
        var result = notify.replace(re, "");
        if (notify == result) result = "";
        if (result == "") result = _spreadBaInfo.freeInfo;
    }
    catch (e) { result = _spreadBaInfo.freeInfo; }
    document.getElementById("notify").innerHTML = result;   
}

function CheckSound() {
    var homeNum = parseInt(document.getElementById("sound").value);
    var guestNum = parseInt(document.getElementById("guestSound").value);
    var type = (homeNum == Config.sound ? 1 : 2);
    Config.sound = homeNum < 4 ? homeNum : -1;
    Config.guestSound = guestNum < 4 ? guestNum : -1;
    Config.writeCookie();
    soundInit();
    //voicePlay(0, 1, type, true);
}
function CheckWindow() {
    if (document.getElementById("windowCheck").checked) Config.winLocation = parseInt(document.getElementById("winLocation").value)
    else Config.winLocation = -1;
    Config.writeCookie();
}

function CheckCountry(obj) {
    //if (obj.checked)
    //    obj.parentElement.style.backgroundColor = "#ffeeee";
    //else
    //    obj.parentElement.style.backgroundColor = "white";
    countOneFilter(obj.id.split('_')[1], obj.checked, 2);
    // SelectCountryOK();
}
function SelectCountryAll(value) {
    var i, inputs, choiseNum = 0;
    inputs = document.getElementById("countryList").getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type != "checkbox") continue;
        if (value)
            inputs[i].checked = value;
        else
            inputs[i].checked = !inputs[i].checked;
        if (inputs[i].checked) {
            //inputs[i].parentElement.style.backgroundColor = "#ffeeee";
            var j = inputs[i].id.split('_')[1];
            choiseNum += C[j][2];
        }
        //else {
        //    inputs[i].parentElement.style.backgroundColor = "white";
        //}
    }
    setFilterNum("countryNum", choiseNum);
    //SelectCountryOK();
}

function SelectCountryOK() {
    var i, j, inputs, cIDList = "_";
    var hh = 0;
    inputs = document.getElementById("countryList").getElementsByTagName("input");
    hiddenID = "_";
    for (var i = 0; i < inputs.length; i++) {
        try {
            if (inputs[i].checked) {
                cIDList += inputs[i].getAttribute("cid") + "_";
                var k = parseInt(inputs[i].value);
                for (var j = 1; j <= matchcount; j++) {
                    if (A[j][0] > 0 && A[j][40] == C[k][0]) {
                        document.getElementById("tr1_" + A[j][0]).style.display = "";
                        if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "";// || A[j][26] != ""
                        if ((isHomeIndex || isCompanyPage) && parseInt(flashScheduleIDs) == A[j][0])
                            document.getElementById("tr3_" + A[j][0]).style.display = "";
                        if (A[j][53] == 1 && parseInt(A[j][13]) >= 0)
                            document.getElementById("tr4_" + A[j][0]).style.display = "";
                        hiddenID += A[j][0] + "_";
                    }
                }
            }
            else {
                var k = parseInt(inputs[i].value);
                for (var j = 1; j <= matchcount; j++) {
                    if (A[j][0] > 0 && A[j][40] == C[k][0]) {
                        document.getElementById("tr1_" + A[j][0]).style.display = "none";
                        if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "none";// || A[j][26] != ""
                        if (isHomeIndex || isCompanyPage)
                            document.getElementById("tr3_" + A[j][0]).style.display = "none";
                        document.getElementById("tr4_" + A[j][0]).style.display = "none";
                        hh = hh + 1;
                    }
                }
            }
        } catch (e) { }
    }
    if (hh == 0) hiddenID = "_";
    var tempHiddenIds = hiddenID;
    if (tempHiddenIds != "_")
        tempHiddenIds = enCookieSchedule(tempHiddenIds);
    writeLocalStorage("Bet007live_hiddenID", tempHiddenIds);
    isChooseMatch = true;
    document.getElementById("hiddencount").innerHTML = hh;
    changeLeagueState(2);
    if (isHomeIndex) {
        changeGoalState();
        //changeConditionState();
    }
    Config.isSimple = -1;
    Config.writeCookie();
    //保存赛事筛选项
    writeConditionCookie(2, '', cIDList, Config.sclassType);
    document.getElementById("button6").className = "btn33";
    document.getElementById("button7").className = "btn33";
    SetTrBgColor();
    //if (location.href.toLowerCase().indexOf("index2in1") == -1 && location.href.toLowerCase().indexOf("oldIndexall") == -1)
    //    changeGoalState();
    goPosistionTop(1);
}

function CloseLeague(i) {
    document.getElementById("myleague_" + i).checked = false;
    SelectOK(1);
}

function HiddenLeague(i) {
    var obj = document.getElementById("collapse" + i);
    var b = true;
    if (obj.innerHTML.indexOf("cllse") != -1) {
        b = false;
        obj.innerHTML = "<img src='image/expand2.gif'>";
    }
    else {
        b = true;
        obj.innerHTML = "<img src='image/cllse.gif'>";
    }
    document.getElementById("myleague_" + i).checked = b;
    SelectOK(2);
}
function ShowAllMatch(t) {
    document.getElementById("button6").className = "btn33_on";
    document.getElementById("button7").className = "btn33";
    Config.isSimple = 0;
    Config.writeCookie();
    //oldLetBig = 0;
    SelectAll(true, 1);
    SelectOK(t);
    SetTrBgColor();
    //MakeTable();
    //if (location.href.toLowerCase().indexOf("index2in1") == -1 && location.href.toLowerCase().indexOf("oldIndexall") == -1) 
    //    checkAllGoal();
    //checkAllCountry();
}
function checkAllGoal() {
    var obj = document.getElementById("goalTable");
    var inputs = obj.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type != "checkbox") continue;
        inputs[i].checked = true; //全选
    }
}
function checkAllCountry() {
    var inputs = document.getElementById("countryList").getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        inputs[i].checked = true;
        inputs[i].parentElement.style.backgroundColor = "#ffeeee";
    }
}
var mycountryHeight = 0;
function makeCountry() {
    var countryhtml = new Array();
    var groupHtml = new Array();
    var arrFilter = getConditonList(2);
    var choiseNum = 0;
    var countryGroupData = new Array();
    var countryTemp = new Array();
    for (var i = 0; i < C.length; i++) {
        var temp = C[i];
        temp[C[i].length] = i;
        countryTemp.push(temp);
    }
    countryGroupData = pySegSort(countryTemp,1);
    //countryhtml.push("<ul>");
    groupHtml.push("<ul id='groupTab' class='Fright_nav'>");
    var countryName = "";
    for (var i = 0; i < countryGroupData.length; i++) {
        var groupName = countryGroupData[i].letter[0].toLocaleUpperCase();
        var hasData = false;
        for (var j = 0; j < countryGroupData[i].data.length; j++) {
            var countryData = countryGroupData[i].data[j];
            if (countryData[2] == 0) continue;
            if (Config.language == 0)
                countryName = countryData[1];
            else
                countryName = countryData[3];
            if (!hasData) {
                groupHtml.push("<li id='s" + groupName + "' onclick=\"goPosistion('" + groupName + "',1)\">" + groupName + "</li>");
                countryhtml.push("<div class='catetitle' id='group" + groupName + "'>" + groupName + "</div>");
                countryhtml.push("<div class='group' id='class" + groupName + "'>");
                hasData = true;
            }
            if (countryData[2] > 0 && arrFilter[2].indexOf("_" + countryData[0] + "_") != -1 && parseInt(arrFilter[0]) > 0) {
               // countryhtml.push("<li style='background-color:#fff0f0'><input onclick='CheckCountry(this)' checked type=checkbox id='mycountry_" + i + "' value=" + i + " cid='" + C[i][0] + "'><label style='cursor:pointer' for='mycountry_" + i + "'>");
                countryhtml.push("<label style='display: block;'><input onclick='CheckCountry(this)' checked type=checkbox id='mycountry_" + countryData[countryData.length - 1] + "' value=" + countryData[countryData.length - 1] + " cid='" + countryData[0] + "'>");
                choiseNum += countryData[2];
            }
            else
                //countryhtml.push("<li style='background-color:#ffffff'><input onclick='CheckCountry(this)' type=checkbox id='mycountry_" + i + "' value=" + i + " cid='" + C[i][0] + "'><label style='cursor:pointer' for='mycountry_" + i + "'>");
                countryhtml.push("<label style='display: block;'><input onclick='CheckCountry(this)' type=checkbox id='mycountry_" + countryData[countryData.length - 1] + "' value=" + countryData[countryData.length - 1] + " cid='" + countryData[0] + "'>");
            countryhtml.push("<span><i></i>" + countryName + "</span></label>");
            //countryhtml.push(countryName + "</label></li>");
        }
        if (hasData)
            countryhtml.push("</div>");
    }
    groupHtml.push("</ul>");
    document.getElementById("countryList").innerHTML = countryhtml.join("") + groupHtml.join("");
    document.getElementById("countryNum").innerHTML = "[" + choiseNum + "]";
    var titleList = $("#countryList .catetitle");
    var titleHeight, groupHeight = 0;
    titleHeight = titleList.length * 24;
    var groupList = $("#countryList .group");
    for (var i = 0; i < groupList.length; i++) {
        groupHeight += groupList[i].clientHeight;
    }
    mycountryHeight = titleHeight + groupHeight - 440;
}
var myleagueHeight = 0;
function makeLeague(selectType) {
    document.getElementById("myleague").innerHTML = "";
    var sclassGroupData = new Array();
    var sclassTemp = new Array();
    var hotSclassList = new Array();
    for (var i = 1; i <= sclasscount; i++) {
        var temp = B[i];
        temp[B[i].length] = i;
        sclassTemp.push(temp);
        if (temp[10] != 0)
            hotSclassList.push(temp);
    }
    sclassGroupData = pySegSort(sclassTemp, 0);
    var isDefaultSelelct = false;//当选中的不是cookie记录的类型时，默认选中全部足彩竞足和北单
    var arrFilter = getConditonList(1);
    if (arrFilter[3] != selectType || (arrFilter[0] == 1 && arrFilter[2]==""))
        isDefaultSelelct = true;
    for (var i = 0; i < 4; i++) {
        document.getElementById("rbs" + i).className = "";
    }
    document.getElementById("rbs" + selectType).className = "on";
    var choiseNum = 0;
    var sclassName = "";
    var noSclassData = "<div id='noSclassData' style='display:none;'>" + (Config.language == 1 ? "暫無賽事" : "暂无赛事") + "</div>";
    if (selectType == 0) {
        var hotHtml = new Array();
        var normalHtml = new Array();
        var groupHtml = new Array();
        var hotOnclickHtml = " onclick='CheckLeague(this)' ";
        hotHtml.push("<div id='groupHot' class='catetitle'>热门</div><div class='group' id='classHot'>");
        groupHtml.push("<ul id='groupTab' class='Fright_nav'><li id='sHot' onclick=\"goPosistion('Hot',0)\">热</li>");        
        for (var i = 0; i < hotSclassList.length; i++) {
            var sclassData = hotSclassList[i];
            if (sclassData[6] == 0) continue;
            var scheduleHotCount = sclassData[10] == 2 || isDefaultSelelct ? sclassData[11] : sclassData[6];//等于2时为部分精简，11热门赛程数，6所有赛程数
            if (Config.language < 2)
                sclassName = sclassData[Config.language];
            else
                sclassName = sclassData[0];
            //if (isDefaultSelelct || parseInt(arrFilter[0]) != 1 || arrFilter[2].indexOf("_" + (sclassData[4] + sclassData[9]) + "_") != -1) {
            //    var className = sclassData[10] == 2 ? "lev1 half" : "lev1";
            //    hotHtml.push("<label style='display: block;' class='" + className +"'><input onclick='CheckLeague(this)' checked type=checkbox id='myleague_" + sclassData[sclassData.length - 1] + "' value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'>");
            //    choiseNum += scheduleHotCount;
            //}
            //else {
            //    hotHtml.push("<label style='display: block;' class='lev1'><input onclick='CheckLeague(this)' type=checkbox id='myleague_" + sclassData[sclassData.length - 1] + "' value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'>");
            //}
            var isSelect = false;
            var isSpecial = sclassData[10] == 2;//是否部分精简
            if (isSpecial && parseInt(sclassData[11]) == parseInt(sclassData[6])) {
                for (var j = 1; j < sclasscount; j++) {
                    if (B[j][4] == sclassData[4]) {
                        B[j][10] = 1;//设置为全部精简
                        sclassData[10] = 1;
                        isSpecial = false;//不再是部分精简
                        break;
                    }
                }
            }
            var secondSelectHtml = "";
            hotOnclickHtml = " onclick='CheckLeague(this)' ";
            var className = "sclassName lev1";
            if (isDefaultSelelct || parseInt(arrFilter[0]) != 1 || arrFilter[2].indexOf("_" + (sclassData[4] + sclassData[9]) + "_") != -1) {
                isSelect = true;               
                //hotHtml.push("<label style='display: block;' class='" + className + "'><input onclick='CheckLeague(this)' checked type=checkbox id='myleague_" + sclassData[sclassData.length - 1] + "' value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'>");
                choiseNum += scheduleHotCount;
            }
            var tempDesc = sclassData[6];
            if (isSpecial && parseInt(sclassData[11]) != parseInt(sclassData[6])) {
                tempDesc = sclassData[11] + "+" + (parseInt(sclassData[6]) - parseInt(sclassData[11]));
                secondSelectHtml = "<ul class='sclassPopUl'><li" + (sclassData[12] == 1 || isDefaultSelelct ? " class='on'" : "") + " onclick='selectSecondSclass(this,1)'>热门[" + sclassData[11] + "]</li><li  " + (sclassData[12] == 3 && !isDefaultSelelct ? " class='on'" : "") + " onclick='selectSecondSclass(this,3)'>全部[" + sclassData[6] + "]</li><li" + (sclassData[12] == 0 && !isDefaultSelelct ? " class='on'" : "") +" onclick='selectSecondSclass(this,0)'>不选</li></ul>";
                hotOnclickHtml = "";
                className = sclassData[12] == 1 || isDefaultSelelct ? "sclassName specialSclass lev1 half" : "sclassName specialSclass lev1";
            }
            var highTvHtml = "";
            if (sclassData[13] == 1)
                highTvHtml = '<i class="TVicon">LIVE</i>';
            hotHtml.push("<div style='display: block;' class='" + className + "'>" + highTvHtml +"<span id='myleague_" + sclassData[sclassData.length - 1] + "'" + hotOnclickHtml + " value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'" + (isSelect ? " class='on'" : "") + "><i></i>" + sclassName + "[" + tempDesc + "]</span>" + secondSelectHtml + "</div>");
        }
        hotOnclickHtml = " onclick='CheckLeague(this)' ";
        for (var i = 0; i < sclassGroupData.length; i++) {
            var groupName = sclassGroupData[i].letter[0].toLocaleUpperCase();
            var hasData = false;
            for (var j = 0; j < sclassGroupData[i].data.length; j++) {
                var sclassData = sclassGroupData[i].data[j];
                if (sclassData[6] == 0) continue;
                if (Config.language < 2)
                    sclassName = sclassData[Config.language];
                else
                    sclassName = sclassData[0];
                //该联赛有比赛并且（1：用户没有筛选，默认赛事精简；2：用户筛选的赛事列表）满足以上条件中的一个为选中
                if (sclassData[10] !=0) {
                    continue;
                } else {
                    if (!hasData) {
                        groupHtml.push("<li id='s" + groupName + "' onclick=\"goPosistion('" + groupName + "',0)\">" + groupName + "</li>");
                        normalHtml.push("<div class='catetitle' id='group" + groupName + "'>" + groupName + "</div>");
                        normalHtml.push("<div class='group' id='class" + groupName + "'>");
                        hasData = true;
                    }
                    var isSelect = false;
                    if (!isDefaultSelelct && arrFilter[2].indexOf("_" + (sclassData[4] + sclassData[9]) + "_") != -1) {
                        isSelect = true;
                        //normalHtml.push("<label style='display: block;'><input onclick='CheckLeague(this)' checked type=checkbox id='myleague_" + sclassData[sclassData.length - 1] + "' value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'>");
                        choiseNum += sclassData[6];
                    }
                    //normalHtml.push("<span><i></i>" + sclassName + "[" + sclassData[6] + "]</span></label>");
                    var highTvHtml = "";
                    if (sclassData[13] == 1)
                        highTvHtml = '<i class="TVicon">LIVE</i>';
                    normalHtml.push("<div style='display: block;' class='sclassName'>" + highTvHtml +"<span id='myleague_" + sclassData[sclassData.length - 1] + "'" + hotOnclickHtml + " value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'" + (isSelect ? " class='on'" : "") + "><i></i>" + sclassName + "[" + sclassData[6] + "]</span></div>");
                }
            }
            if (hasData)
                normalHtml.push("</div>");
        }
        groupHtml.push("</ul>");
        hotHtml.push("</div>");
        document.getElementById("myleague").innerHTML = hotHtml.join("") + normalHtml.join("") + groupHtml.join("") + noSclassData;
        document.getElementById("leagueNum").innerHTML = "[" + choiseNum + "]";
        var titleList = $("#myleague .catetitle");
        var titleHeight, groupHeight = 0;
        titleHeight = titleList.length * 24;
        var groupList = $("#myleague .group");
        for (var i = 0; i < groupList.length; i++) {
            groupHeight += groupList[i].clientHeight;
        }
        myleagueHeight = titleHeight + groupHeight - (Config.IsIE ? 440 : 220);
    }
    else {
        var normalHtml = new Array();
        var hotOnclickHtml = " onclick='CheckLeague(this)' ";
        normalHtml.push("<div id='classData' class='group'>");
        for (var i = 0; i < hotSclassList.length; i++) {
            var sclassData = hotSclassList[i];
            if (sclassData[6] == 0) continue;
            if (Config.language < 2)
                sclassName = sclassData[Config.language];
            else
                sclassName = sclassData[0];
            var isSelect = false;
            var isSpecial = sclassData[10] == 2; //是否部分精简
            var secondSelectHtml = "";
            hotOnclickHtml = " onclick='CheckLeague(this)' ";
            var className = "sclassName lev1";
            if (isDefaultSelelct || parseInt(arrFilter[0]) != 1 || arrFilter[2].indexOf("_" + (sclassData[4] + sclassData[9]) + "_") != -1) {
                isSelect = true;
                //normalHtml.push("<label style='display: block;' class='lev1'><input onclick='CheckLeague(this)' checked type=checkbox id='myleague_" + sclassData[sclassData.length - 1] + "' value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'>");
                choiseNum += sclassData[6];
            }
            //else {
            //    normalHtml.push("<label style='display: block;' class='lev1'><input onclick='CheckLeague(this)' type=checkbox id='myleague_" + sclassData[sclassData.length - 1] + "' value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'>");
            //}
            //normalHtml.push("<span><i></i>" + sclassName + "[" + sclassData[6] + "]</span></label>");
            var tempDesc = sclassData[6];
            if (isSpecial) {
                tempDesc = sclassData[11] + "+" + (parseInt(sclassData[6]) - parseInt(sclassData[11]));
                secondSelectHtml = "<ul class='sclassPopUl'><li" + (sclassData[12] == 1 ? " class='on'" : "") + " onclick='selectSecondSclass(this,1)'>热门[" + sclassData[11] + "]</li><li  " + (sclassData[12] == 3 ? " class='on'" : "") + " onclick='selectSecondSclass(this,3)'>全部[" + sclassData[6] + "]</li><li" + (sclassData[12] == 0 ? " class='on'" : "") + " onclick='selectSecondSclass(this,0)'>不选</li></ul>";
                hotOnclickHtml = "";
                className = sclassData[12] == 1 ? "sclassName specialSclass lev1 half" : "sclassName specialSclass lev1";
            }
            var highTvHtml = "";
            if (sclassData[13] == 1)
                highTvHtml = '<i class="TVicon">LIVE</i>';
            normalHtml.push("<div style='display: block;' class='" + className + "'>" + highTvHtml + "<span id='myleague_" + sclassData[sclassData.length - 1] + "'" + hotOnclickHtml + " value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'" + (isSelect ? " class='on'" : "") + "><i></i>" + sclassName + "[" + tempDesc + "]</span>" + secondSelectHtml + "</div>");
        }
        hotOnclickHtml = " onclick='CheckLeague(this)' ";
        for (var i = 0; i < sclassGroupData.length; i++) {
            var groupName = sclassGroupData[i].letter[0].toLocaleUpperCase();
            var hasData = false;
            for (var j = 0; j < sclassGroupData[i].data.length; j++) {
                var sclassData = sclassGroupData[i].data[j];
                if (sclassData[6] == 0) continue;
                if (Config.language < 2)
                    sclassName = sclassData[Config.language];
                else
                    sclassName = sclassData[0];
                var isSelect = false;
                //该联赛有比赛并且（1：用户没有筛选，默认赛事精简；2：用户筛选的赛事列表）满足以上条件中的一个为选中
                if (sclassData[10] != 0) {
                    continue;
                } else {
                    if (isDefaultSelelct || arrFilter[2].indexOf("_" + (sclassData[4] + sclassData[9]) + "_") != -1) {
                        isSelect = true;
                        //normalHtml.push("<label style='display: block;'><input onclick='CheckLeague(this)' checked type=checkbox id='myleague_" + sclassData[sclassData.length - 1] + "' value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'>");
                        choiseNum += sclassData[6];
                    } 
                    if (sclassData[13] == 1)
                        highTvHtml = '<i class="TVicon">LIVE</i>';
                    normalHtml.push("<div style='display: block;' class='sclassName'>" + highTvHtml + "<span id='myleague_" + sclassData[sclassData.length - 1] + "'" + hotOnclickHtml + " value=" + sclassData[sclassData.length - 1] + " cid='" + sclassData[4] + sclassData[9] + "'" + (isSelect ? " class='on'" : "") + "><i></i>" + sclassName + "[" + sclassData[6] + "]</span></div>");
                }
            }
        }
        normalHtml.push("</div>");
        document.getElementById("myleague").innerHTML = normalHtml.join("") + noSclassData;
    }

    ShowMatchByMatchState(arrFilter[1], selectType);
}
String.prototype.Trim = function () {
    return this.replace(/(^\s*)|(\s*$)/g, "");
}
function countOneFilter(j, checked, kind,lastSelect) {
    var name = kind == 2 ? "countryNum" : "leagueNum";
    var obj = document.getElementById(name);
    var num = parseInt(obj.innerHTML.replace("[", "").replace("]", "").Trim());
    var count = kind == 2 ? C[j][2] : 0;
    if (kind == 1) {
        if (B[j][10] == 2 && lastSelect != undefined && lastSelect!=0) {//部分热门需要特殊处理，先把之前选择的赛程数减掉,选择全不选并之前选择了热门的时候，需要把非热门的加上
            
            
            if (checked) {
                var tempCount = lastSelect == 1 ? parseInt(B[j][11]) : parseInt(B[j][6]);//11热门6全部赛程
                num = num - tempCount;
            }
            else {
                if (lastSelect == 1) {
                    var tempCount = parseInt(B[j][6]) - parseInt(B[j][11]);//11热门6全部赛程
                    num = num + tempCount;
                }
            }
        }
        var n = 0;
        for (; n < 5; n++) {
            if (document.getElementById("rb" + n).className == "on") break;
        }
        for (var i = 1; i <= matchcount; i++) {
            if (A[i][0] > 0 && (Config.sclassType == 0 || (Config.sclassType == 1 && A[i][58] != "") || (Config.sclassType == 2 && A[i][57] != "") || (Config.sclassType == 3 && A[i][59] != "")) && (n == 0 || (n == 1 && parseInt(A[i][13]) > 0) || (n == 2 && A[i][13] == "-1") || (n == 3 && A[i][13] == "0") || (n == 4 && A[i][28] == "True"))) {
                
                if (A[i][2] == B[j][0]) {
                    if (B[j][10] == 2 && A[i][62] == 0 && B[j][12] == 1)//部分精简时，选择了热门赛程但该赛程不是热门时需要过滤掉
                        continue;
                    count++;
                }                    
            }
        }
    }
    setFilterNum(name, checked ? num + count : num - count);
}
function setFilterNum(id, num) {
    var obj = document.getElementById(id);
    obj.innerHTML = "[" + num + "]";
    obj.className = obj.className == "flash" ? "flash2" : "flash";
}
function getImportantCup() {
    if (Config.isSimple == 1) {
        cupImportantList = ",";
        for (var i = 1; i <= sclasscount; i++) {
            if (B[i][10] != "0" && B[i][3] == "2")
                cupImportantList += B[i][4] + ",";
        }
    }
}
function selectSecondSclass(obj, type) {
    //type:0:不选,1:热门,3:全部
    var spanObj = obj.parentElement.previousElementSibling;//获取同级第一个元素
    var j = spanObj.id.replace("myleague_", "");
    if (B[j][12] == type) return;
    var lastSelect = B[j][12];
    B[j][12] = type;
    var list = obj.parentElement.getElementsByTagName("li");
    for (var i = 0; i < list.length; i++) {
        list[i].className = "";
    }
    obj.className = "on";
    spanObj.className = type == 0 ? "" : "on";
    obj.parentElement.parentElement.className = type == 1 ? "sclassName specialSclass lev1 half" : "sclassName specialSclass lev1";
    countOneFilter(j, type != 0, 1, lastSelect);
}
function CheckLeague(obj) {
    //if (obj.checked)
    //    obj.parentElement.style.backgroundColor = "#ffeeee";
    //else
    //    obj.parentElement.style.backgroundColor = "white";
    var j = obj.id.replace("myleague_", "");
    var className = obj.className == "on" ? "" : "on";
    obj.className = className;
    var isSelect = className == "on";
    countOneFilter(j, isSelect, 1);
}
function SelectAll(value, t) {
    var choiseNum = 0;
    if (t == 1) {
        for (var i = 0; i < 5; i++) {
            document.getElementById("rb" + i).className = "";
        }
        document.getElementById("rb0").className = "on";
        for (var i = 0; i < 4; i++) {
            document.getElementById("rbs" + i).className = "";
        }
        document.getElementById("rbs0").className = "on";
        //Config.sclassType = 0;
    }
    //var inputs = document.getElementById("myleague").getElementsByTagName("input");
    //for (var i = 0; i < inputs.length; i++) {
    //    if (inputs[i].type != "checkbox") continue;
    //    if (t == 0 && inputs[i].parentElement.style.display != "block") continue;
    //    if (t == 1) inputs[i].parentElement.style.display = "block";//在页面导航点“精简”、“完整”、“显”时，赛事选择要自动跳回“所有赛事”
    //    inputs[i].checked = value ? value : !inputs[i].checked;
    //    if (inputs[i].checked) {
    //        var k = inputs[i].id.split('_')[1];
            
    //        if (n == 0)
    //            choiseNum += B[k][6];
    //        else {//滚球、未开场、已完场、进行中 这些选项只计算符合条件的数据
    //            for (var j = 1; j <= matchcount; j++) {
    //                if (A[j][0] > 0 && (n == 0 || (n == 1 && parseInt(A[j][13]) > 0) || (n == 2 && A[j][13] == "-1") || (n == 3 && A[j][13] == "0") || (n == 4 && A[j][28] == "True"))) {
    //                    if (A[j][2] == B[k][0])
    //                        choiseNum++;
    //                }
    //            }
    //        }
    //    }
    //}

    var n = 0;
    for (; n < 5; n++) {
        if (document.getElementById("rb" + n).className == "on") break;
    }
    var list = document.getElementById("myleague").getElementsByClassName("group");
    for (var i = 0; i < list.length; i++) {
        var sclassList = list[i].getElementsByTagName("span");
        for (var j = 0; j < sclassList.length; j++) {
            var sclassData = sclassList[j];
            if (t == 0 && sclassData.parentElement.style.display != "block") continue;
            if (t == 1) sclassData.parentElement.style.display = "block";//在页面导航点“精简”、“完整”、“显”时，赛事选择要自动跳回“所有赛事”
            sclassData.className = value ? "on" : (sclassData.className == "on" ? "" : "on");
            var k = sclassData.id.split('_')[1];
            if (B[k][10] == 2) {//部分精简赛事需要额外处理样式
                sclassData.parentElement.className = "sclassName specialSclass lev1";
                if (sclassData.className == "on") {
                    B[k][12] = 3;
                } else {
                    B[k][12] = 0;
                }
                var liList = sclassData.parentElement.getElementsByTagName("li");
                for (var m = 0; m < liList.length; m++) {
                    liList[m].className = "";
                }
                if (sclassData.className == "on")
                    liList[1].className = "on";//全选
                else
                    liList[2].className = "on";//全不选
            }
            if (sclassData.className == "on") {                
                if (n == 0)
                    choiseNum += B[k][6];
                else {//滚球、未开场、已完场、进行中 这些选项只计算符合条件的数据
                    for (var j = 1; j <= matchcount; j++) {
                        if (A[j][0] > 0 && (n == 0 || (n == 1 && parseInt(A[j][13]) > 0) || (n == 2 && A[j][13] == "-1") || (n == 3 && A[j][13] == "0") || (n == 4 && A[j][28] == "True"))) {
                            if (A[j][2] == B[k][0])
                                choiseNum++;
                        }
                    }
                }
            }
        }
    }
    //Config.writeCookie();
    setFilterNum("leagueNum", choiseNum);
}
function setOrderby() {
    Config.orderBy = (Config.orderBy == 1 ? 2 : 1);
    if (Config.orderBy == 1)
        document.getElementById("orderbyChange").value = (Config.language == 1 ? "按聯賽選擇" : "按联赛选择");
    else
        document.getElementById("orderbyChange").value = (Config.language == 1 ? "按時間選擇" : "按时间选择");
    Config.writeCookie();
    document.getElementById("hiddencount").innerHTML = 0;
    LoadLiveFile();
}
function SelectImportant(t) {
    var sIDList = "_";
    var choiseNum = 0;
    if (t == 1) {
        var n = 0;
        for (var i = 0; i < 5; i++) {
            if (document.getElementById("rb" + i).className == "on") {
                n = i;
                break;
            }
        }
        for (var j = 1; j <= sclasscount; j++) {
            try {
                if (B[j][6] == 0) continue;
                var obj = document.getElementById("myleague_" + j);
                if (obj.parentElement.style.display != "block") continue;
                if (B[j][10] != "0") {
                    var sName = B[j][0];
                    obj.className = "on";
                    if (B[j][10] == 2) {
                        obj.parentElement.className = "sclassName specialSclass lev1 half";
                        B[j][12] = 1;//只选择热门赛事
                        var liList = obj.parentElement.getElementsByTagName("li");
                        for (var m = 0; m < liList.length; m++) {
                            liList[m].className = m == 0 ? "on" : "";
                        }
                    }
                    sIDList += B[j][4] + "_";
                    for (var i = 1; i <= matchcount; i++) {//A[i][62]精简赛程标识
                        if (sName == A[i][2] && A[i][0] > 0&&A[i][62]==1 && (n == 0 || (n == 1 && parseInt(A[i][13]) > 0) || (n == 2 && A[i][13] == "-1") || (n == 3 && A[i][13] == "0") || (n == 4 && A[i][28] == "True"))) {
                            choiseNum++;
                        }
                    }
                }
                else {
                    obj.className = "";
                }
            }
            catch (e) {
                console.log("error:"+j);
            }
        }
        
        setFilterNum("leagueNum", choiseNum);
    }
    else {
        //Config.sclassType = 0;
        A.splice(0, A.length);
        A = A.concat(tempA);
        SortData();
        ShowMatchByMatchState(0);
        for (var i = 1; i <= sclasscount; i++) {
            if (B[i][6] == 0) continue;
            var obj = document.getElementById("myleague_" + i);
            if (t != 6 && obj.parentElement.style.display != "block") continue;
            if (t == 6)
                obj.parentElement.style.display = "block";//在页面导航点“精简”、“完整”、“显”时，赛事选择要自动跳回“所有赛事”
            if (B[i][10] != 0) {
                obj.className = "on";
                if (B[i][10] == 2) {
                    var liObj = obj.nextElementSibling.firstElementChild;//获取下一个兄弟元素的第一个子元素
                    selectSecondSclass(liObj, 1);
                    //obj.parentElement.className = "sclassName specialSclass lev1 half";
                    B[i][12] = 1; //只选择热门赛事
                }
                sIDList += B[i][4] + "_";
                choiseNum += B[i][11];//热门赛程场次数
            }
            else {
                obj.className = "";
            }
        }
        for (var i = 0; i < 5; i++) {
            document.getElementById("rb" + i).className = "";
        }
        document.getElementById("rb0").className = "on";
        for (var i = 0; i < 4; i++) {
            document.getElementById("rbs" + i).className = "";
        }
        document.getElementById("rbs0").className = "on";
        setFilterNum("leagueNum", choiseNum);
        SelectOK(t);
    }
}
function SelectOK(t) {
    var i, j, inputs, sIDList = "_";
    var hh = 0;
    var sclassType = 0;
    inputs = document.getElementById("myleague").getElementsByTagName("input");
    for (var i = 0; i < 4; i++) {
        if (document.getElementById("rbs" + i).className == "on") {
            sclassType = i;
            break;
        }
    }
    hiddenID = "_";
    var n = 0;
    for (; n < 5; n++) {
        if (document.getElementById("rb" + n).className=="on") break;
    }
    if (n >= 5) n = 0;
    Config.secondSclassType = n;

    //for (var i = 0; i < inputs.length; i++) {
    //    try {
    //        if (inputs[i].checked && inputs[i].parentElement.style.display == "block") {
    //            sIDList += inputs[i].getAttribute("cid") + "_";//选中的联赛
    //            var k = parseInt(inputs[i].value);
    //            for (var j = 1; j <= matchcount; j++) {
    //                if (A[j][0] > 0 && A[j][2] == B[k][0]) {
    //                    if ((sclassType == 0 || (sclassType == 1 && A[j][58] != "") || (sclassType == 2 && A[j][57] != "") || (sclassType == 3 && A[j][59] != "")) && (n == 0 || (n == 1 && parseInt(A[j][13]) > 0) || (n == 2 && A[j][13] == "-1") || (n == 3 && A[j][13] == "0") || (n == 4 && A[j][28] == "True"))) {
    //                        document.getElementById("tr1_" + A[j][0]).style.display = "";
    //                        if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "";// || A[j][26] != ""
    //                        if ((isHomeIndex || isCompanyPage) && parseInt(flashScheduleIDs) == A[j][0])
    //                            document.getElementById("tr3_" + A[j][0]).style.display = "";
    //                        if (A[j][53] == 1 && parseInt(A[j][13]) >= 0)
    //                            document.getElementById("tr4_" + A[j][0]).style.display = "";
    //                        hiddenID += A[j][0] + "_";
    //                    }
    //                    else {
    //                        if (A[j][0] == flashScheduleIDs) {
    //                            flashScheduleIDs = "";//对阵隐藏时，相关动态图显示也取消
    //                            _glflash.clearTimer();
    //                        }
    //                        document.getElementById("tr1_" + A[j][0]).style.display = "none";
    //                        if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "none";// || A[j][26] != ""
    //                        if (isHomeIndex || isCompanyPage)
    //                            document.getElementById("tr3_" + A[j][0]).style.display = "none";
    //                        document.getElementById("tr4_" + A[j][0]).style.display = "none";
    //                        hh = hh + 1;
    //                    }
    //                }
    //            }
    //        }
    //        else {
    //            var k = parseInt(inputs[i].value);
    //            for (var j = 1; j <= matchcount; j++) {
    //                if (A[j][0] > 0 && A[j][2] == B[k][0]) {
    //                    if (A[j][0] == flashScheduleIDs) {
    //                        flashScheduleIDs = "";//对阵隐藏时，相关动态图显示也取消
    //                        _glflash.clearTimer();
    //                    }
    //                    document.getElementById("tr1_" + A[j][0]).style.display = "none";
    //                    if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "none";// || A[j][26] != ""
    //                    if (isHomeIndex || isCompanyPage)
    //                        document.getElementById("tr3_" + A[j][0]).style.display = "none";
    //                    document.getElementById("tr4_" + A[j][0]).style.display = "none";
    //                    hh = hh + 1;
    //                }
    //            }
    //        }
    //    } catch (e) { }
    //}
    var list = document.getElementById("myleague").getElementsByClassName("group");
    for (var i = 0; i < list.length; i++) {
        var sclassList = list[i].getElementsByTagName("span");
        for (var m = 0; m < sclassList.length; m++) {
            var sclassData = sclassList[m];
            if (sclassData.className == "on" && sclassData.parentElement.style.display == "block") {
                sIDList += sclassData.getAttribute("cid") + "_";//选中的联赛
                var k = parseInt(sclassData.getAttribute("value"));
                for (var j = 1; j <= matchcount; j++) {
                    if (A[j][0] > 0 && A[j][2] == B[k][0]) {
                        if ((sclassType == 0 || (sclassType == 1 && A[j][58] != "") || (sclassType == 2 && A[j][57] != "") || (sclassType == 3 && A[j][59] != "")) && (n == 0 || (n == 1 && parseInt(A[j][13]) > 0) || (n == 2 && A[j][13] == "-1") || (n == 3 && A[j][13] == "0") || (n == 4 && A[j][28] == "True"))) {
                            if (A[j][62] == 0 && B[k][12] == 1) {
                                if (A[j][0] == flashScheduleIDs) {
                                    flashScheduleIDs = "";//对阵隐藏时，相关动态图显示也取消
                                    _glflash.clearTimer();
                                }
                                document.getElementById("tr1_" + A[j][0]).style.display = "none";
                                if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "none";// || A[j][26] != ""
                                if (isHomeIndex || isCompanyPage)
                                    document.getElementById("tr3_" + A[j][0]).style.display = "none";
                                document.getElementById("tr4_" + A[j][0]).style.display = "none";
                                hh = hh + 1;
                            } else {
                                document.getElementById("tr1_" + A[j][0]).style.display = "";
                                if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "";// || A[j][26] != ""
                                if ((isHomeIndex || isCompanyPage) && parseInt(flashScheduleIDs) == A[j][0])
                                    document.getElementById("tr3_" + A[j][0]).style.display = "";
                                if (A[j][53] == 1 && parseInt(A[j][13]) >= 0)
                                    document.getElementById("tr4_" + A[j][0]).style.display = "";
                                hiddenID += A[j][0] + "_";
                            }
                        }
                        else {
                            if (A[j][0] == flashScheduleIDs) {
                                flashScheduleIDs = "";//对阵隐藏时，相关动态图显示也取消
                                _glflash.clearTimer();
                            }
                            document.getElementById("tr1_" + A[j][0]).style.display = "none";
                            if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "none";// || A[j][26] != ""
                            if (isHomeIndex || isCompanyPage)
                                document.getElementById("tr3_" + A[j][0]).style.display = "none";
                            document.getElementById("tr4_" + A[j][0]).style.display = "none";
                            hh = hh + 1;
                        }
                    }
                }
            }
            else {
                var k = parseInt(sclassData.getAttribute("value"));
                for (var j = 1; j <= matchcount; j++) {
                    if (A[j][0] > 0 && A[j][2] == B[k][0]) {
                        if (A[j][0] == flashScheduleIDs) {
                            flashScheduleIDs = "";//对阵隐藏时，相关动态图显示也取消
                            _glflash.clearTimer();
                        }
                        document.getElementById("tr1_" + A[j][0]).style.display = "none";
                        if (Config.explain == 1 && (A[j][42] + A[j][30] + A[j][54] != "")) document.getElementById("tr2_" + A[j][0]).style.display = "none";// || A[j][26] != ""
                        if (isHomeIndex || isCompanyPage)
                            document.getElementById("tr3_" + A[j][0]).style.display = "none";
                        document.getElementById("tr4_" + A[j][0]).style.display = "none";
                        hh = hh + 1;
                    }
                }
            }
        }
    }

    if (hh == 0) hiddenID = "_";
    var tempHiddenIds = hiddenID;
    if (tempHiddenIds != "_")
        tempHiddenIds = enCookieSchedule(tempHiddenIds);
    writeLocalStorage("Bet007live_hiddenID", tempHiddenIds);
    document.getElementById("hiddencount").innerHTML = hh;
    if (t < 6) {
        Config.isSimple = -1;
        document.getElementById("button6").className = "btn33";
        document.getElementById("button7").className = "btn33";
        isChooseMatch = true;
    }
    else if (t == 6) {
        Config.isSimple = 1;
        document.getElementById("button6").className = "btn33";
        document.getElementById("button7").className = "btn33_on";
    }
    else {
        Config.isSimple = 0;
        document.getElementById("button6").className = "btn33_on";
        document.getElementById("button7").className = "btn33";
    }
    Config.writeCookie();
    Config.hiddenAllMatch = sIDList == "_";
    if (Config.sclassType != sclassType) {
        Config.sclassType = sclassType;
        //保存赛事筛选项  
        writeConditionCookie(1, n, sIDList, Config.sclassType);
        SortData();
        MakeTable(false);
    }
    else
        //保存赛事筛选项  
        writeConditionCookie(1, n, sIDList, Config.sclassType);
    changeCountryState();
    if (isHomeIndex) {
        changeGoalState();
    }
    if (location.href.toLowerCase().indexOf("index2in1") == -1 && location.href.toLowerCase().indexOf("oldindexall") == -1)
        changeGoalState();
    SetTrBgColor();
    if (t == 1)
        goPosistionTop(0);
    //if(t>=6)
    //    changeLeagueState(1);
}
//'按比赛状态显示
function ShowMatchByMatchState(n, selectType) {
    var i, j;
    //if (n != "" && n == Config.secondSclassType) return;
    if (n == "") n = 0;
    for (var i = 0; i < 5; i++) {
        document.getElementById("rb" + i).className = "";
    }
    document.getElementById("rb" + n).className = "on";
    if (selectType == undefined) {
        selectType = 0;
        for (var i = 0; i < 4; i++) {
            if (document.getElementById("rbs" + i).className == "on") {
                selectType = i;
                break;
            }
        }
    }
    var hasScdule = 0, choiseNum = 0; var hasData = false;
    for (var j = 1; j <= sclasscount; j++) {
        if (B[j][6] == 0) continue;
        var obj = document.getElementById("myleague_" + j);
        try {
            var objSclass = obj.parentNode;
            objSclass.style.display = "none";
        }
        catch (e) {
            console.log("error:" + j);
        }
        var isSet = false;
        for (var i = 1; i <= matchcount; i++) {
            if (A[i][0] > 0 && (n == 0 || (n == 1 && parseInt(A[i][13]) > 0) || (n == 2 && A[i][13] == "-1") || (n == 3 && A[i][13] == "0") || (n == 4 && A[i][28] == "True"))) {
                if (A[i][2] == B[j][0] && (selectType == 0 || (selectType == 1 && A[i][58] != "") || (selectType == 2 && A[i][57] != "") || (selectType == 3 && A[i][59] != ""))) {
                    if (selectType == 0 && A[i][62] == 0 && B[j][12] == 1) continue;
                    if (!isSet) {
                        objSclass.style.display = "block";
                        isSet = true;
                        hasData = true;
                    }
                    if (objSclass.style.display == "block" && obj.className=="on") {
                        choiseNum++;
                        hasData = true;
                    }
                }
            }
        }
    }
    if (hasData)
        document.getElementById("noSclassData").style.display = "none";
    else
        document.getElementById("noSclassData").style.display = "";
    setFilterNum("leagueNum", choiseNum);
    if (selectType == 0)
        ShowGruopName();
}
function CheckExplain() {
    if (document.getElementById("explain").checked) Config.explain = 1;
    else Config.explain = 0;
    Config.writeCookie();
    ShowExplain();
}
function ShowExplain() {
    var value = "none";
    if (Config.explain == 1) value = "";
    for (var i = 1; i <= matchcount; i++) {
        if (A[i][0] > 0 && A[i][42] + A[i][30] + A[i][54] != "" && (hiddenID.indexOf("_" + A[i][0] + "_") != -1 || hiddenID == "_")) {
            document.getElementById("tr2_" + A[i][0]).style.display = value;
        }
    }
}
function ChangeBgColor(n) {
    SetBgColor(n);
    Config.style = n;
    Config.writeCookie();
}
function SetBgColor(n) {
    bg2 = ["F0F0F0", "E0E9F6", "F2F2F2", "F0F7FF", "EDFBFF", "F8F9FC", "EEEEEE"][parseInt(n)];
    var bg;
    bg1 = "#FFFFFF";
    if (bg2 == "F0F0F0") bg1 = "FFFDF3";
    var trs = document.getElementById("table_live").getElementsByTagName("tr");
    var count = 0;
    for (var i = 1; i < trs.length; i++) {
        if (trs[i].getAttribute("index") != null && trs[i].style.display == "") {
            if (count % 2 == 0) bg = bg1; else bg = bg2;
            trs[i].bgColor = bg;//.style.backgroundColor
            count++;
        }
    }
    document.body.style.backgroundImage = n > 0 ? "url(image/bg" + bg2 + ".gif)" : "";
    document.body.style.backgroundRepeat = n > 0 ? "repeat-y" : "";
}
function CheckTeamRank() {
    if (document.getElementById("rank").checked) Config.rank = 1;
    else Config.rank = 0;
    Config.writeCookie();
    ShowTeamOrder();
}
function ShowTeamOrder() {
    if (Config.rank == 1) {
        for (var i = 1; i <= matchcount; i++) {
            if (A[i][0] == 0) continue;
            if (A[i][22] != "") document.getElementById("horder_" + A[i][0]).innerHTML = "<font color=#444444><sup>[" + A[i][22] + "]</sup></font>";
            if (A[i][23] != "") document.getElementById("gorder_" + A[i][0]).innerHTML = "<font color=#444444><sup>[" + A[i][23] + "]</sup></font>";
        }
    }
    else {
        for (var i = 1; i <= matchcount; i++) {
            if (A[i][0] == 0) continue;
            document.getElementById("horder_" + A[i][0]).innerHTML = "";
            document.getElementById("gorder_" + A[i][0]).innerHTML = "";
        }
    }
}
function CheckFunction(obj) {
    if (document.getElementById(obj).checked) eval("Config." + obj + "=1");
    else eval("Config." + obj + "=0");
    Config.writeCookie();
    if (obj == "showYellowCard") {
        MakeTable(false);
        if (location.href.toLowerCase().indexOf("2in1") != -1)
            showodds();
    }
}
function HiddenSelected(value) {
    var hh = parseInt(document.getElementById("hiddencount").innerHTML);
    var obj;
    var isChoose = false;
    var oldHiddenID = hiddenID;
    var haveCheck = false;
    var showNum = 0;
    for (var i = 1; i <= matchcount; i++) {
        obj = document.getElementById("tr1_" + A[i][0]);
        if (A[i][0] > 0 && obj.style.display == "") {
            if (!haveCheck && document.getElementById("chk_" + A[i][0]).checked) haveCheck = true;
        }
    }
    if (!haveCheck)//没有选中比赛时，返回不做任何操作
    {
        hiddenID = oldHiddenID;
        return;
    }
    for (var i = 1; i <= matchcount; i++) {
        obj = document.getElementById("tr1_" + A[i][0]);
        if (A[i][0] > 0 && obj.style.display == "") {
            if (document.getElementById("chk_" + A[i][0]).checked == value) {
                hh = hh + 1;
                hiddenID = hiddenID.replace("_" + A[i][0] + "_", "_");
                document.getElementById("tr1_" + A[i][0]).style.display = "none";
                if (Config.explain == 1 && A[i][42] + A[i][30] + A[i][54] != "") document.getElementById("tr2_" + A[i][0]).style.display = "none";
                if (isHomeIndex)
                    document.getElementById("tr3_" + A[i][0]).style.display = "none";
                if (A[i][53] == 1)
                    document.getElementById("tr4_" + A[i][0]).style.display = "none";
            }
            else {
                if (showNum == 0) hiddenID = "_";
                if (hiddenID.indexOf("_" + A[i][0] + "_") == -1) hiddenID += A[i][0] + "_";
                isChoose = true;
                showNum++;
                document.getElementById("tr1_" + A[i][0]).style.display = "";
                if (Config.explain == 1 && A[i][42] + A[i][30] + A[i][54] != "") document.getElementById("tr2_" + A[i][0]).style.display = "";
                if (isHomeIndex && parseInt(flashScheduleIDs) == A[i][0])
                    document.getElementById("tr3_" + A[i][0]).style.display = "";
                if (A[i][53] == 1 && parseInt(A[i][13]) >= 0)
                    document.getElementById("tr4_" + A[i][0]).style.display = "";
            }
        }
    }
    if (Config.isSimple != -1) {
        Config.isSimple = -1;
        document.getElementById("button6").className = "btn33";
        document.getElementById("button7").className = "btn33";
        Config.writeCookie();
    }
    if (!value && !isChoose) hh = 0;
    document.getElementById("hiddencount").innerHTML = hh;
    if (hiddenID.indexOf("_" + flashScheduleIDs + "_") == -1 && flashScheduleIDs != "") {
        flashScheduleIDs = "";
        _glflash.clearTimer();
    }
    isChooseMatch = true;
    //MakeTable();
    //changeLeagueState(1);
    //changeCountryState();
    //if (location.href.toLowerCase().indexOf("index2in1") == -1 && location.href.toLowerCase().indexOf("oldindexall") == -1) 
    //    changeGoalState();
    var tempHiddenIds = hiddenID;
    if (tempHiddenIds != "_")
        tempHiddenIds = enCookieSchedule(tempHiddenIds);
    writeLocalStorage("Bet007live_hiddenID", tempHiddenIds);
    SetTrBgColor();
}
function changeLeagueState(t) {//t=1:页面功能筛选时联运赛事选择；t=2:用户选择其它筛选时，联赛默认精简
    for (var j = 1; j <= sclasscount; j++) B[j][7] = 0;
    for (var i = 1; i <= matchcount; i++) {
        if (hiddenID != "_" && hiddenID.indexOf("_" + A[i][0] + "_") == -1) continue;
        for (j = 1; j <= sclasscount; j++) {
            if (A[i][2] == B[j][0]) {
                B[j][7]++;
                break;
            }
        }
    }
    var choiseNum = 0;
    for (var j = 1; j <= sclasscount; j++) {
        if (B[j][6] == 0) continue;
        if ((B[j][7] > 0 && t == 1) || (t == 2 && B[j][10] != 0)) {
            if (B[j][10] == 2) {
                document.getElementById("myleague_" + j).parentElement.className = "sclassName specialSclass lev1 half";
                var obj = document.getElementById("myleague_" + j).nextElementSibling.firstElementChild;  
                selectSecondSclass(obj, 1);

                B[j][12] = 1; //只选择热门赛事
            }
            document.getElementById("myleague_" + j).className = "on";
            //document.getElementById("myleague_" + j).checked = true;
            //document.getElementById("myleague_" + j).parentElement.style.backgroundColor = "#ffeeee";
            choiseNum += (B[j][10] == 2 ? B[j][11] : B[j][6]);
        }
        else {
            document.getElementById("myleague_" + j).className = "";
            //document.getElementById("myleague_" + j).checked = false;
            //document.getElementById("myleague_" + j).parentElement.style.backgroundColor = "#ffffff";
        }
    }
    document.getElementById("leagueNum").innerHTML = "[" + choiseNum + "]";
}
function changeCountryState() {
    //for (var j = 0; j < C.length; j++) C[j][4] = 0;
    //for (var i = 1; i <= matchcount; i++) {
    //    if (hiddenID != "_" && hiddenID.indexOf("_" + A[i][0] + "_") == -1) continue;
    //    for (j = 0; j < C.length; j++) {
    //        if (A[i][40] == C[j][0]) {
    //            C[j][4]++;
    //            break;
    //        }
    //    }
    //}
    for (var j = 0; j < C.length; j++) {
        if (C[j][2] == 0) continue;
        //if (C[j][4] > 0) {
        //    document.getElementById("mycountry_" + j).checked = true;
        //    document.getElementById("mycountry_" + j).parentElement.style.backgroundColor = "#ffeeee";
        //}
        //else {
        document.getElementById("mycountry_" + j).checked = false;
        //document.getElementById("mycountry_" + j).parentElement.style.backgroundColor = "#ffffff";
        // }
    }
    document.getElementById("countryNum").innerHTML = "[0]";
}
function movepanlu(event) {
    var scrollTop = Math.max(document.body.scrollTop, document.documentElement.scrollTop);
    document.getElementById('winScore').style.top = Math.max(0, scrollTop + event.clientY - document.getElementById('winScore').offsetHeight - 15) + "px";
}

function hiddendetail() {
    document.getElementById("winScore").style.display = "none";
    document.getElementById("winScore").innerHTML = "";

}
function MoveToBottom(m) {
    try {
        document.getElementById("tr1_" + m).parentElement.insertAdjacentElement("BeforeEnd", document.getElementById("tr1_" + m));
        document.getElementById("tr2_" + m).parentElement.insertAdjacentElement("BeforeEnd", document.getElementById("tr2_" + m));
        if (isHomeIndex || isCompanyPage)
            document.getElementById("tr3_" + m).parentElement.insertAdjacentElement("BeforeEnd", document.getElementById("tr3_" + m));

        document.getElementById("tr4_" + m).style.display = "none";//隐藏高清直播行
    } catch (e) { }
}

function MovePlace(newPos, oldPos) {
    try {
        if (newPos == 0) {
            document.getElementById("tr_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr1_" + oldPos));
            if (isHomeIndex || isCompanyPage)
                document.getElementById("tr_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr3_" + oldPos));
            document.getElementById("tr_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr2_" + oldPos));
            document.getElementById("tr_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr4_" + oldPos));
        }
        else {
            document.getElementById("tr1_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr1_" + oldPos));
            if (isHomeIndex || isCompanyPage)
                document.getElementById("tr1_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr3_" + oldPos));
            document.getElementById("tr1_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr2_" + oldPos));
            document.getElementById("tr1_" + newPos).insertAdjacentElement("BeforeBegin", document.getElementById("tr4_" + oldPos));
        }
    }
    catch (e) {
    }
}
function MovePlace2(newPos, oldPos) {
    try {
        if (newPos == 0) {
            document.getElementById("tr_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr1_" + oldPos));
            if (isHomeIndex || isCompanyPage)
                document.getElementById("tr_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr3_" + oldPos));
            document.getElementById("tr_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr2_" + oldPos));
            document.getElementById("tr_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr4_" + oldPos));
        }
        else {
            document.getElementById("tr1_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr1_" + oldPos));
            if (isHomeIndex || isCompanyPage)
                document.getElementById("tr1_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr3_" + oldPos));
            document.getElementById("tr1_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr2_" + oldPos));
            document.getElementById("tr1_" + newPos).insertAdjacentElement("AfterEnd", document.getElementById("tr4_" + oldPos));
        }
    }
    catch (e) {
    }
}

function SetLevel(m) {
    matchType = m;
    LoadLiveFile();
    document.getElementById("liZC").style.color = "blue";
}
function LoadLiveFile() {
    var allDate = document.getElementById("allDate");
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.charset = "utf-8";
    s.src = staticUrl + "vbsxml/bfdata_ut.js?r=007" + Date.parse(new Date());
    //s.src = staticUrl + "/txt.js?r=007" + Date.parse(new Date());
    allDate.removeChild(allDate.firstChild);
    allDate.appendChild(s, "script");
    window.setTimeout("LoadLiveFile()", 1800 * 1000);
}
function LoadDetailFile() {
    var detail = document.getElementById("span_detail");
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.charset = "utf-8";
    s.src = staticUrl + "vbsxml/detail_ut.js?r=007" + Date.parse(new Date());
    detail.removeChild(detail.firstChild);
    detail.appendChild(s, "script");
    loadDetailFileTime = new Date();
}
function LoadPanluFile() {
    var detail = document.getElementById("span_panlu");
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.charset = "utf-8";
    s.src = staticUrl + "vbsxml/panlu_ut.js?r=007" + Date.parse(new Date());
    detail.removeChild(detail.firstChild);
    detail.appendChild(s, "script");
}

function writeCookie(name, value, isMulti) {
    delCookie(name);
    delCookie(name, true);
    var expire = "";
    var hours = 365;
    expire = new Date((new Date()).getTime() + hours * 3600000);
    expire = ";path=/;expires=" + expire.toGMTString() + ";domain=" + getDoMain(isMulti);
    document.cookie = name + "=" + value + expire; //escape(
}
function writeCookie2(name, value, isMulti, expireTime) {
    delCookie(name);
    delCookie(name, true);
    var expire = "";
    expire = new Date((new Date()).getTime() + expireTime)
    expire = ";path=/;expires=" + expire.toGMTString() + ";domain=" + getDoMain(isMulti);
    document.cookie = name + "=" + value + expire; //escape(
}
function getCookie2(name)//取cookies函数        
{
    var arr = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)(;|$)"));
    if (arr != null) return unescape(arr[2]); return null;

}
function delCookie(name, isMulti)//删除cookie 
{
    try {
        var exp = new Date();
        exp.setTime(exp.getTime() - 1000 * 3600);
        var cval = getCookie2(name);
        if (cval != null && cval != "null")
            document.cookie = name + "=" + cval + ";path=/;expires=" + exp.toGMTString() + ";domain=" + (typeof (isMulti) != "undefined" ? getDoMain(isMulti) : getDoMain());
        //document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
    }
    catch (e) { }
}
function getDoMain(isMulti) {
    var arrDoms = location.href.split("/")[2].split(".");
    var isNum = /^\d+$/;
    if (isNum.test(arrDoms[1]))
        return arrDoms[0] + "." + arrDoms[1] + "." + arrDoms[2] + "." + arrDoms[3].split(":")[0];
    else if (typeof (isMulti) != "undefined" && isMulti)
        return arrDoms[1] + "." + arrDoms[2];
    else
        return arrDoms[0] + "." + arrDoms[1] + "." + arrDoms[2];
}
function changeData(odds) {
    if (typeof (odds) == "undefined" || odds == "")
        return "";
    var tmp = odds;
    var arrd = odds.toString().split(".");
    if (arrd.length > 1) {
        if (arrd[1].length == 1)
            tmp = tmp + "0";
    }
    else
        tmp = tmp + ".00";
    return tmp;
}
function getStrDiv(odds1, odds2) {
    if (typeof (odds1) == "undefined" || odds1 + "" == "")
        return "";
    var retVal;
    var tmp = changeData(odds1);
    if (parseFloat(odds1) > parseFloat(odds2))
        retVal = '<div class="up_red">' + tmp + '</div>';
    else if (parseFloat(odds1) < parseFloat(odds2))
        retVal = '<div class="down_green">' + tmp + '</div>';
    else
        retVal = tmp;
    return retVal;
}
function getStrDiv2(goal1, goal2, t) {
    if (typeof (goal1) == "undefined" || goal1 + "" == "")
        return "";
    var tmp = "", retVal;
    if (t == 1) tmp = Goal2GoalCn(goal1);
    else if (t == 2) tmp = Goal2GoalCn2(goal1);
    else tmp = goal1;
    if (parseFloat(goal1) != parseFloat(goal2))
        retVal = '<div class="change_yellow">' + tmp + '</div>';
    else
        retVal = tmp;
    return retVal;
}
function getChangeStrDiv(odds1, odds2) {
    var retVal;
    if (typeof (odds1) == "undefined" || odds1 == "")
        return "";
    if (parseFloat(odds1) > parseFloat(odds2))
        // retVal = '<div class="up_red"><span class=up>' + odds1 + '</span></div>';
        retVal = '<div class="up_red">' + odds1 + '</div>';
    else if (parseFloat(odds1) < parseFloat(odds2))
        retVal = '<div class="down_green"><span class=down>' + odds1 + '</span></div>';
    else
        retVal = odds1;
    return retVal;
}
function gettime() {
    try {
        LoadTime = (LoadTime + 1) % 60;
        if (LoadTime == 0)
            getxml("2");
        else {
            oXmlHttp.open("get", staticUrl + "vbsxml/time.txt?r=007" + Date.parse(new Date()), true);
            // oXmlHttp.setRequestHeader("User-Agent", "");
            oXmlHttp.onreadystatechange = function () {
                if (oXmlHttp.readyState == 4 && oXmlHttp.status == 200) {
                    lastUpdateTime = new Date();
                    if (oXmlHttp.responseText != "" && oXmlHttp.responseText != lastUpdateFileTime) {
                        lastUpdateFileTime = oXmlHttp.responseText;
                        getxml("");//""						
                    }
                }
            };
            oXmlHttp.send(null);
        }
    }
    catch (e) { }
    window.setTimeout("gettime()", 2000);
    //window.setTimeout("gettime()",3000);
}
function getxml(ii) {
    oXmlHttp.open("get", staticUrl + "vbsxml/change" + ii + "_ut.xml?r=007" + Date.parse(new Date()), true);
    //oXmlHttp.setRequestHeader("User-Agent", "");
    oXmlHttp.onreadystatechange = refresh;
    oXmlHttp.send(null);
}
function refresh() {
    try {
        if (oXmlHttp.readyState != 4 || (oXmlHttp.status != 200 && oXmlHttp.status != 0)) return;
        var root = oXmlHttp.responseXML.documentElement;
        if (root.attributes[0].value != "0") {
            window.setTimeout("LoadLiveFile()", Math.floor(20000 * Math.random()));
            return;
        }

        var D = new Array();
        var matchindex, score1change, score2change, scorechange;
        var goTime, hometeam, guestteam, sclassname, score1, score2, tr;
        var matchNum = 0;
        var winStr = "";
        var notify = "";
        var obj = document.getElementById("ifShow"); //判断是否有显示Crow*详情赔率浮动窗口
        for (var i = 0; i < root.childNodes.length; i++) {
            if (document.all && parseInt(ieNum) < 10)
                D = root.childNodes[i].text.split("^"); //0:ID,1:state,2:score1,3:score2,4:half1,5:half2,6:card1,7:card2,8:time1,9:time2,10:explain,11:lineup		
            else
                D = root.childNodes[i].textContent.split("^");

            tr = document.getElementById("tr1_" + D[0]);
            if (tr == null) continue;
            matchindex = getDataIndex(D[0]);
            //matchindex = tr.attributes["index"].value;
            score1change = false;
            if (A[matchindex][14] != D[2]) {
                A[matchindex][14] = D[2];
                score1change = true;
                tr.cells[4].style.backgroundColor = "#bbbb22";
            }
            score2change = false;
            if (A[matchindex][15] != D[3]) {
                A[matchindex][15] = D[3];
                score2change = true;
                tr.cells[6].style.backgroundColor = "#bbbb22";
            }
            scorechange = score1change || score2change;
            if (A[matchindex][48] != D[16]) {
                A[matchindex][48] = D[16];
            }
            if (A[matchindex][49] != D[17]) {
                A[matchindex][49] = D[17];
            }
            A[matchindex][50] = D[18];
            //附加说明改时变了' Var视频说明改变
            if (A[matchindex][30] != D[10] || A[matchindex][42] != D[15] || A[matchindex][54] != D[19]) {
                if (D[10] != "") {
                    D[10] = checkShowAd(D[10]);
                }
                A[matchindex][30] = D[10];
                A[matchindex][42] = D[15];
                A[matchindex][54] = D[19];
                A[matchindex][55] = D[20];
                A[matchindex][68] = D[25];
                var objVarExplain = document.getElementById("varexplain_" + D[0]);
                var objExplain = document.getElementById("explain_" + D[0]);
                if (A[matchindex][54] != "") {
                    var varName = A[i][68] == A[i][37] ? "(" + getTeamName(i, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)) + ")" : (A[i][68] == A[i][38] ? "(" + getTeamName(i, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)) + ")" : "");
                    objVarExplain.className = "var";
                    objVarExplain.innerHTML = "<img src='images/warning.png'>" + A[matchindex][54 + (Config.language == 1 ? 1 : 0)] + varName.replace("(中)","") + "</span>";
                }
                else {
                    objVarExplain.innerHTML = "";
                    objVarExplain.className = "";
                }
                var ex = showExplain(D[15], getTeamName(matchindex, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)), getTeamName(matchindex, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1))) + D[10];
                //document.getElementById("other_" + D[0]).innerHTML = ex;
                if (ex != "") {
                    objExplain.className = "var green";
                    objExplain.innerHTML = ex;
                }
                else {
                    objExplain.innerHTML = "";
                    objExplain.className = "";
                }
                if (D[10] + D[15] + D[19] == "")
                    document.getElementById("tr2_" + D[0]).style.display = "none";
                else if (hiddenID == "_" || hiddenID.indexOf("_" + D[0] + "_") != -1)//显示的赛事才显示说明
                    document.getElementById("tr2_" + D[0]).style.display = "";
            }
            var isShowWin = Config.onlyTopShowWin == 0 || (Config.onlyTopShowWin == 1 && concernId.indexOf("_" + A[matchindex][0] + "_") != -1);// || concernId == "_"
            if (Config.redcard == 1 && (D[6] != A[matchindex][18] || D[7] != A[matchindex][19]) && tr.style.display != "none" && D[1] != "-1") {//完场后红牌不弹窗
                hometeam = getTeamName(matchindex, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)).replace("<font color=#880000>(中)</font>", " 中").substring(0, 7);
                guestteam = getTeamName(matchindex, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)).substring(0, 7);
                sclassname = A[matchindex][2 + lang];
                if (D[6] != A[matchindex][18]) {
                    hometeam = "<font color=red>" + hometeam + "</font>";
                }
                if (D[7] != A[matchindex][19]) {
                    guestteam = "<font color=red>" + guestteam + "</font>";
                }
                if (isShowWin) {
                    winStr += "<tr bgcolor=#ffffff height=34 align=center class=line><td><font color=red>红牌</font></td><td> " + tr.cells[3].innerHTML + "</td><td><b>" + hometeam + "</b> " + (D[6] == "0" ? "" : "<img src=bf_img/redcard" + D[6] + ".gif border='0'>") + "</td><td  colspan=2> vs</td><td><b>" + guestteam + "</b> " + (D[7] == "0" ? "" : "<img src=bf_img/redcard" + D[7] + ".gif border='0'>") + "</td></tr>";
                    matchNum = matchNum + 1;
                }
            } //redcardChange
            //红牌变化了
            if (D[6] != A[matchindex][18]) {
                A[matchindex][18] = D[6];
                if (D[6] == "0")
                    document.getElementById("redcard1_" + D[0]).innerHTML = "";
                else
                    document.getElementById("redcard1_" + D[0]).innerHTML = "<img src=bf_img/redcard" + D[6] + ".gif border='0'>";
                if (Config.redcard) {
                    tr.cells[4].style.backgroundColor = "#ff8888";
                    window.setTimeout("timecolors(" + D[0] + "," + matchindex + ")", 12000);
                }
            }
            if (D[7] != A[matchindex][19]) {
                A[matchindex][19] = D[7];
                if (D[7] == "0")
                    document.getElementById("redcard2_" + D[0]).innerHTML = "";
                else
                    document.getElementById("redcard2_" + D[0]).innerHTML = "<img src=bf_img/redcard" + D[7] + ".gif border='0'>";
                if (Config.redcard) {
                    tr.cells[6].style.backgroundColor = "#ff8888";
                    window.setTimeout("timecolors(" + D[0] + "," + matchindex + ")", 12000);
                }
            }
            //黄牌变化了
            if (D[12] != A[matchindex][20] && Config.showYellowCard == 1) {
                A[matchindex][20] = D[12];
                if (D[12] == "0")
                    document.getElementById("yellow1_" + D[0]).innerHTML = "";
                else
                    document.getElementById("yellow1_" + D[0]).innerHTML = "<img src=bf_img/yellow" + D[12] + ".gif border='0'>";
            }
            if (D[13] != A[matchindex][21] && Config.showYellowCard == 1) {
                A[matchindex][21] = D[13];
                if (D[13] == "0")
                    document.getElementById("yellow2_" + D[0]).innerHTML = "";
                else
                    document.getElementById("yellow2_" + D[0]).innerHTML = "<img src=bf_img/yellow" + D[13] + ".gif border='0'>";
            }
            //开赛
            if (A[matchindex][11] != D[8]) {               
                var oldPos = matchindex;
                var TTime = new Date();
                var timeStr = AmountTimeDiff(D[8], A[matchindex][36], A[matchindex][43], 1);
                var dataStr = timeStr.split(" ");
                tr.cells[2].innerHTML = dataStr[1];
                var nt = D[8].split(":");
                var nd = D[14].split("-");
                var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
                if (concernId.indexOf("_" + A[matchindex][0] + "_") == -1) {
                    for (var i = 1; i <= matchcount; i++) {                       
                        if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
                            var ot = A[i][11].split(":");
                            var od = A[i][36].split("-");
                            var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                            if (D[1] != -1) {
                                var tempTr = document.getElementById("tr1_" + A[i][0]);
                                if (tempTr.style.display == "none")
                                    continue;
                                if (ot2 > nt2) {
                                    MovePlace(A[i][0], D[0]);
                                    break;
                                }
                            }
                        }
                    }
                }
                else {
                    for (var i = 1; i <= matchcount; i++) {
                        if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
                            var ot = A[i][11].split(":");
                            var od = A[i][36].split("-");
                            var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                            if (D[1] != -1) {
                                var tempTr = document.getElementById("tr1_" + A[i][0]);
                                if (tempTr.style.display == "none")
                                    continue;
                                if (ot2 > nt2) {
                                    MovePlace(A[i][0], D[0]);
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            A[matchindex][11] = D[8];
            A[matchindex][12] = D[9];
            //半场比分
            A[matchindex][16] = D[4];
            A[matchindex][17] = D[5];
            //状态
            if (A[matchindex][13] != D[1]) {
                if (A[matchindex][13] == "-11" || A[matchindex][13] == "-14" || A[matchindex][13] == "-13") {
                    if (D[1] == "1") {
                        var oldPos = matchindex;
                        var TTime = new Date();
                        var nt = D[8].split(":");
                        var nd = D[14].split("-");
                        var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
                        if (concernId.indexOf("_" + A[matchindex][0] + "_") == -1) {
                            for (var i = 1; i <= matchcount; i++) {
                                if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
                                    var ot = A[i][11].split(":");
                                    var od = A[i][36].split("-");
                                    var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                                    if (D[1] != -1) {
                                        if (ot2 > nt2) {
                                            MovePlace(A[i][0], D[0]);
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                        else {
                            for (var i = 1; i <= matchcount; i++) {
                                if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
                                    var ot = A[i][11].split(":");
                                    var od = A[i][36].split("-");
                                    var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                                    if (D[1] != -1) {
                                        if (ot2 > nt2) {
                                            MovePlace(A[i][0], D[0]);
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                var isFromEndtoAdd = false;
                if (((parseInt(A[matchindex][13]) == -1 && parseInt(D[1]) == 4) || (parseInt(A[matchindex][13]) == -1 && parseInt(D[1]) == 5)) && concernId.indexOf("_" + D[0] == -1)) isFromEndtoAdd = true;
                A[matchindex][13] = D[1];
                switch (A[matchindex][13]) {
                    case "0":
                        tr.cells[3].innerHTML = "";
                        break;
                    case "1":
                        var t = A[matchindex][12].split(",");
                        var t2 = new Date(t[0], t[1], t[2], t[3], t[4], t[5]);
                        goTime = Math.floor((new Date() - t2 - difftime) / 60000);
                        if (goTime > 45) {
                            var t3 = goTime - 45;
                            goTime = "45+" + (t3 > 15 ? 15 : t3);
                        }
                        if (goTime < 1) goTime = "1";
                        tr.cells[3].innerHTML = goTime + "<img src='bf_img/in.gif'>";
                        break;
                    case "2":
                    case "4":
                    case "5":
                        tr.cells[3].innerHTML = getMatchState(D[1]);
                        if (isFromEndtoAdd) {
                            var TTime = new Date();
                            var nt = D[8].split(":");
                            var nd = D[14].split("-");
                            var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
                            for (var i = 1; i <= matchcount; i++) {
                                if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
                                    var ot = A[i][11].split(":");
                                    var od = A[i][36].split("-");
                                    var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                                    if (ot2 > nt2) {
                                        MovePlace(A[i][0], D[0]);
                                        break;
                                    }
                                }
                            }
                        }
                        break;
                    case "3":
                        var t = A[matchindex][12].split(",");
                        var t2 = new Date(t[0], t[1], t[2], t[3], t[4], t[5]);
                        goTime = Math.floor((new Date() - t2 - difftime) / 60000) + 46;
                        if (goTime > 90) {
                            var t3 = goTime - 90;
                            goTime = "90+" + (t3 > 15 ? 15 : t3);
                        }
                        if (goTime < 46) goTime = "46";
                        tr.cells[3].innerHTML = goTime + "<img src='bf_img/in.gif'>";
                        break;
                    case "-1":
                        tr.cells[3].innerHTML = getMatchState(D[1]);
                        tr.cells[5].style.color = "red";
                        if (concernId.indexOf("_" + D[0] + "_") == -1) {
                            if (topLeagueIds.indexOf("," + A[matchindex][45] + ",") != -1)
                                window.setTimeout("MoveToTopBottom(" + D[0] + ")", 25000);
                            else
                                window.setTimeout("MoveToBottom(" + D[0] + ")", 25000);
                        }
                        //if (concernId.indexOf("_" + D[0] + "_") == -1)
                        //    window.setTimeout("MoveToBottom(" + D[0] + ")", 25000);
                        break;
                    default:
                        tr.cells[3].innerHTML = getMatchState(D[1]);
                        MoveToBottom(D[0]);
                        break;
                }
                if (parseInt(A[matchindex][13]) == 2 || parseInt(A[matchindex][13]) == 4 || parseInt(A[matchindex][13]) == 5 || parseInt(A[matchindex][13]) < 0) {
                    var timeStr = AmountTimeDiff(A[matchindex][11], A[matchindex][36], A[matchindex][43], 1);
                    var dataStr = timeStr.split(" ");
                    document.getElementById("mt_" + D[0]).innerHTML = dataStr[1];
                }
                if (parseInt(A[matchindex][13]) > 0 && window.location.href.toLowerCase().indexOf("oldindex") == -1) {
                    var oddsImgHtml = tr.cells[12].innerHTML;
                    if (oddsImgHtml.indexOf("走地") != -1 && oddsImgHtml.toLowerCase().indexOf("zds.png") == -1) {
                        tr.cells[12].getElementsByTagName('span').item(1).innerHTML = "<img title='有走地' src='image/zds.png'>";
                        tr.cells[12].className = "zd";
                        tr.cells[12].onclick = myAddclick(D[0]);
                        //tr.cells[12].addEventListener("click", myAddclick(D[0]));
                    }
                }
            }
            //判断是否有补时
            if ((parseInt(D[1]) == 1 || parseInt(D[1]) == 3)&& A[matchindex][56] != D[21]) {
                A[matchindex][56] = D[21];
                if (D[21] == "") {
                    var timeStr = AmountTimeDiff(A[matchindex][11], A[matchindex][36], A[matchindex][43], 1);
                    var dataStr = timeStr.split(" ");
                    document.getElementById("mt_" + D[0]).innerHTML = dataStr[1];
                }
                else
                    document.getElementById("mt_" + D[0]).innerHTML = (Config.language == 1 ? "補" : "补") + "<span style='color:red;'>" + D[21] + "'</span>";
            }
            var spans = tr.cells[7].getElementsByTagName("span")
            if (spans.length > 1)
                spans[0].style.display = (A[matchindex][50] == "1" ? "" : "none");
            //score
            switch (A[matchindex][13]) {
                case "0":
                    A[matchindex][27] = D[11];
                    if (D[11] == "1")
                        tr.cells[5].innerHTML = "阵容";
                    else
                        tr.cells[5].innerHTML = "-";
                    break;
                case "1":
                    tr.cells[5].innerHTML = A[matchindex][14] + "-" + A[matchindex][15];
                    if (spans.length > 1) {
                        spans[0].innerHTML = A[matchindex][48] + "-" + A[matchindex][49];
                        spans[0].style.color = "blue";
                    }
                    break;
                case "-11":
                case "-14":
                    tr.cells[5].innerHTML = "-";
                    if (spans.length > 1) {
                        spans[0].innerHTML = "-";//角球
                        spans[1].innerHTML = "-";//半场比分
                    }
                    else
                        tr.cells[7].innerHTML = "-";
                    break;
                default:  //2 3 -1 -12 -13                   
                    tr.cells[5].innerHTML = A[matchindex][14] + "-" + A[matchindex][15];
                    if (spans.length > 1) {
                        spans[0].innerHTML = A[matchindex][48] + "-" + A[matchindex][49];
                        spans[1].innerHTML = A[matchindex][16] + "-" + A[matchindex][17];
                        if (A[matchindex][13] == -1)
                            spans[0].style.color = "black";
                        spans[1].style.color = "red";
                    }
                    else {
                        tr.cells[7].innerHTML = A[matchindex][16] + "-" + A[matchindex][17];
                        tr.cells[7].style.color = "red";
                    }
                    break;
            }
            if (obj != null && obj.value == "1") {
                var objScore = document.getElementById("ffScoreDetail");
                var sid = objScore.attributes["sid"].value;
                if (parseInt(sid) == parseInt(A[matchindex][0])) {
                    if (parseInt(A[matchindex][13]) == -1)
                        objScore.innerHTML = "<b><font style='color:red;'>" + A[matchindex][14] + " - " + A[matchindex][15] + "</font></b>";
                    else
                        objScore.innerHTML = "<b><font style='color:blue;'>" + A[matchindex][14] + " - " + A[matchindex][15] + "</font></b>";
                }
            }
            if (scorechange) {
                //ShowFlash(D[0],matchindex);
                if (tr.style.display != "none") {
                    hometeam = getTeamName(matchindex, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)).replace("<font color=#880000>(中)</font>", "(中)");//.substring(0, 7);
                    guestteam = getTeamName(matchindex, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1));//.substring(0, 7);
                    sclassname = A[matchindex][2 + lang];
                    if (score1change) {
                        hometeam = "<font color=red>" + hometeam + "</font>";
                        score1 = "<font color=red>" + D[2] + "</font>";
                        score2 = "<font color=blue>" + D[3] + "</font>";
                        ShowFlash(D[0], matchindex, 1);
                    }
                    if (score2change) {
                        guestteam = "<font color=red>" + guestteam + "</font>";
                        score1 = "<font color=blue>" + D[2] + "</font>";
                        score2 = "<font color=red>" + D[3] + "</font>";
                        ShowFlash(D[0], matchindex, 2);
                    }
                    notify += sclassname + ":" + hometeam + " <font color=blue>" + score1 + "-" + score2 + "</font> " + guestteam + " &nbsp; ";

                    if (Config.winLocation > -1 && parseInt(D[1]) >= -1 && isShowWin) {
                        if (matchNum % 2 == 0)
                            winStr += "<tr bgcolor=#ffffff height=34 align=center class=line><td><font color=#1705B1>" + sclassname + "</font></td><td> " + tr.cells[3].innerHTML + "</td><td><b>" + hometeam + "</b></td><td width=11% style='font-size: 18px;font-family:Verdana;font-weight:bold;'>" + score1 + "-" + score2 + "</td><td>" + Goal2GoalCn(A[matchindex][29]) + "</td><td><b>" + guestteam + "</b></td></tr>";
                        else
                            winStr += "<tr bgcolor=#FDF1E7 height=34 align=center class=line><td><font color=#1705B1>" + sclassname + "</font></td><td> " + tr.cells[3].innerHTML + "</td><td><b>" + hometeam + "</b></td><td width=11% style='font-size: 18px;font-family:Verdana;font-weight:bold;'>" + score1 + "-" + score2 + "</td><td>" + Goal2GoalCn(A[matchindex][29]) + "</td><td><b>" + guestteam + "</b></td></tr>";
                        matchNum = matchNum + 1
                    }
                }
            } //scorechange
        }
        if (matchNum > 0) ShowCHWindow(winStr, matchNum);
        var objNotify = document.getElementById("notify");
        if (notify != "") {
            if (delHtmlTag(objNotify.innerHTML) == delHtmlTag(_spreadBaInfo.freeInfo))
                objNotify.innerHTML = notify;
            else
                objNotify.innerHTML += notify;
            notifyTimer = window.setTimeout("clearNotify('" + notify + "')", 20000);
        }
        else if (objNotify.innerHTML == "")
            objNotify.innerHTML = _spreadBaInfo.freeInfo;

    } catch (e) { }
}
function zqScoreChange(data) {
    try {
        var dataList = data.split("!");
        var D = new Array();
        var matchindex, score1change, score2change, scorechange;
        var goTime, hometeam, guestteam, sclassname, score1, score2, tr;
        var matchNum = 0;
        var winStr = "";
        var notify = "";
        var obj = document.getElementById("ifShow"); //判断是否有显示Crow*详情赔率浮动窗口
        for (var i = 0; i < dataList.length; i++) {
            D = dataList[i].split("^");
            tr = document.getElementById("tr1_" + D[0]);
            if (tr == null) continue;
            matchindex = getDataIndex(D[0]);
            //matchindex = tr.attributes["index"].value;
            score1change = false;
            if (A[matchindex][14] != D[2]) {
                A[matchindex][14] = D[2];
                score1change = true;
                tr.cells[4].style.backgroundColor = "#bbbb22";
            }
            score2change = false;
            if (A[matchindex][15] != D[3]) {
                A[matchindex][15] = D[3];
                score2change = true;
                tr.cells[6].style.backgroundColor = "#bbbb22";
            }
            scorechange = score1change || score2change;

            if (A[matchindex][48] != D[16]) {
                A[matchindex][48] = D[16];
            }
            if (A[matchindex][49] != D[17]) {
                A[matchindex][49] = D[17];
            }
            A[matchindex][50] = D[18];
            //附加说明改时变了' Var视频说明改变
            if (A[matchindex][30] != D[10] || A[matchindex][42] != D[15] || A[matchindex][54] != D[19]) {
                if (D[10] != "") {
                    D[10] = checkShowAd(D[10]);
                }
                A[matchindex][30] = D[10];
                A[matchindex][42] = D[15];
                A[matchindex][54] = D[19];
                A[matchindex][55] = D[20];
                A[matchindex][68] = D[25];
                var objVarExplain = document.getElementById("varexplain_" + D[0]);
                var objExplain = document.getElementById("explain_" + D[0]);
                if (A[matchindex][54] != "") {
                    var varName = A[matchindex][68] == A[matchindex][37] ? "(" + getTeamName(matchindex, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)) + ")" : (A[matchindex][68] == A[matchindex][38] ? "(" + getTeamName(matchindex, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)) + ")" : "");
                    objVarExplain.className = "var";
                    objVarExplain.innerHTML = "<img src='images/warning.png'>" + A[matchindex][54 + (Config.language == 1 ? 1 : 0)] + varName.replace("(中)", "") + "</span>";
                }
                else {
                    objVarExplain.innerHTML = "";
                    objVarExplain.className = "";
                }
                var ex = showExplain(D[15], getTeamName(matchindex, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)), getTeamName(matchindex, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1))) + D[10];
                //document.getElementById("other_" + D[0]).innerHTML = ex;
                if (ex != "") {
                    objExplain.className = "var green";
                    objExplain.innerHTML = ex;
                }
                else {
                    objExplain.innerHTML = "";
                    objExplain.className = "";
                }
                if (D[10] + D[15] + D[19] == "")
                    document.getElementById("tr2_" + D[0]).style.display = "none";
                else if (hiddenID == "_" || hiddenID.indexOf("_" + D[0] + "_") != -1)//显示的赛事才显示说明
                    document.getElementById("tr2_" + D[0]).style.display = "";
            }
            var isShowWin = Config.onlyTopShowWin == 0 || (Config.onlyTopShowWin == 1 && concernId.indexOf("_" + A[matchindex][0] + "_") != -1);// || concernId == "_"
            if (Config.redcard == 1 && (D[6] != A[matchindex][18] || D[7] != A[matchindex][19]) && tr.style.display != "none" && D[1] != "-1") {//完场后红牌不弹窗
                hometeam = getTeamName(matchindex, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)).replace("<font color=#880000>(中)</font>", " 中").substring(0, 7);
                guestteam = getTeamName(matchindex, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)).substring(0, 7);
                sclassname = A[matchindex][2 + lang];
                if (D[6] != A[matchindex][18]) {
                    hometeam = "<font color=red>" + hometeam + "</font>";
                }
                if (D[7] != A[matchindex][19]) {
                    guestteam = "<font color=red>" + guestteam + "</font>";
                }
                if (isShowWin) {
                    winStr += "<tr bgcolor=#ffffff height=34 align=center class=line><td><font color=red>红牌</font></td><td> " + tr.cells[3].innerHTML + "</td><td><b>" + hometeam + "</b> " + (D[6] == "0" ? "" : "<img src=bf_img/redcard" + D[6] + ".gif border='0'>") + "</td><td  colspan=2> vs</td><td><b>" + guestteam + "</b> " + (D[7] == "0" ? "" : "<img src=bf_img/redcard" + D[7] + ".gif border='0'>") + "</td></tr>";
                    matchNum = matchNum + 1;
                }
            } //redcardChange

            //红牌变化了
            if (D[6] != A[matchindex][18]) {
                A[matchindex][18] = D[6];
                if (D[6] == "0")
                    document.getElementById("redcard1_" + D[0]).innerHTML = "";
                else
                    document.getElementById("redcard1_" + D[0]).innerHTML = "<img src=bf_img/redcard" + D[6] + ".gif border='0'>";
                if (Config.redcard) {
                    tr.cells[4].style.backgroundColor = "#ff8888";
                    window.setTimeout("timecolors(" + D[0] + "," + matchindex + ")", 12000);
                }
            }
            if (D[7] != A[matchindex][19]) {
                A[matchindex][19] = D[7];
                if (D[7] == "0")
                    document.getElementById("redcard2_" + D[0]).innerHTML = "";
                else
                    document.getElementById("redcard2_" + D[0]).innerHTML = "<img src=bf_img/redcard" + D[7] + ".gif border='0'>";
                if (Config.redcard) {
                    tr.cells[6].style.backgroundColor = "#ff8888";
                    window.setTimeout("timecolors(" + D[0] + "," + matchindex + ")", 12000);
                }
            }

            //黄牌变化了
            if (D[12] != A[matchindex][20] && Config.showYellowCard == 1) {
                A[matchindex][20] = D[12];
                if (D[12] == "0")
                    document.getElementById("yellow1_" + D[0]).innerHTML = "";
                else
                    document.getElementById("yellow1_" + D[0]).innerHTML = "<img src=bf_img/yellow" + D[12] + ".gif border='0'>";
            }
            if (D[13] != A[matchindex][21] && Config.showYellowCard == 1) {
                A[matchindex][21] = D[13];
                if (D[13] == "0")
                    document.getElementById("yellow2_" + D[0]).innerHTML = "";
                else
                    document.getElementById("yellow2_" + D[0]).innerHTML = "<img src=bf_img/yellow" + D[13] + ".gif border='0'>";
            }

            //开赛
            if (A[matchindex][11] != D[8]) {
                var oldPos = matchindex;
                var TTime = new Date();
                var timeStr = AmountTimeDiff(D[8], A[matchindex][36], A[matchindex][43], 1);
                var dataStr = timeStr.split(" ");
                tr.cells[2].innerHTML = dataStr[1];
                var nt = D[8].split(":");
                var nd = D[14].split("-");
                var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
                if (concernId.indexOf("_" + A[matchindex][0] + "_") == -1) {
                    for (var i = 1; i <= matchcount; i++) {
                        if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
                            var ot = A[i][11].split(":");
                            var od = A[i][36].split("-");
                            var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                            if (D[1] != -1) {
                                var tempTr = document.getElementById("tr1_" + A[i][0]);
                                if (tempTr.style.display == "none")
                                    continue;
                                if (ot2 > nt2) {
                                    MovePlace(A[i][0], D[0]);
                                    break;
                                }
                            }
                        }
                    }
                }
                else {
                    for (var i = 1; i <= matchcount; i++) {
                        if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
                            var ot = A[i][11].split(":");
                            var od = A[i][36].split("-");
                            var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                            if (D[1] != -1) {
                                var tempTr = document.getElementById("tr1_" + A[i][0]);
                                if (tempTr.style.display == "none")
                                    continue;
                                if (ot2 > nt2) {
                                    MovePlace(A[i][0], D[0]);
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            A[matchindex][11] = D[8];
            A[matchindex][12] = D[9];

            //半场比分
            A[matchindex][16] = D[4];
            A[matchindex][17] = D[5];

            //状态
            if (A[matchindex][13] != D[1]) {
                if (A[matchindex][13] == "-11" || A[matchindex][13] == "-14" || A[matchindex][13] == "-13") {
                    if (D[1] == "1") {
                        var oldPos = matchindex;
                        var TTime = new Date();
                        var nt = D[8].split(":");
                        var nd = D[14].split("-");
                        var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
                        if (concernId.indexOf("_" + A[matchindex][0] + "_") == -1) {
                            for (var i = 1; i <= matchcount; i++) {
                                if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
                                    var ot = A[i][11].split(":");
                                    var od = A[i][36].split("-");
                                    var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                                    if (D[1] != -1) {
                                        if (ot2 > nt2) {
                                            MovePlace(A[i][0], D[0]);
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                        else {
                            for (var i = 1; i <= matchcount; i++) {
                                if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
                                    var ot = A[i][11].split(":");
                                    var od = A[i][36].split("-");
                                    var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                                    if (D[1] != -1) {
                                        if (ot2 > nt2) {
                                            MovePlace(A[i][0], D[0]);
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                var isFromEndtoAdd = false;
                if (((parseInt(A[matchindex][13]) == -1 && parseInt(D[1]) == 4) || (parseInt(A[matchindex][13]) == -1 && parseInt(D[1]) == 5)) && concernId.indexOf("_" + D[0] == -1)) isFromEndtoAdd = true;
                A[matchindex][13] = D[1];
                switch (A[matchindex][13]) {
                    case "0":
                        tr.cells[3].innerHTML = "";
                        break;
                    case "1":
                        var t = A[matchindex][12].split(",");
                        var t2 = new Date(t[0], t[1], t[2], t[3], t[4], t[5]);
                        goTime = Math.floor((new Date() - t2 - difftime) / 60000);
                        if (goTime > 45) {
                            var t3 = goTime - 45;
                            goTime = "45+" + (t3 > 15 ? 15 : t3);
                        }
                        if (goTime < 1) goTime = "1";
                        tr.cells[3].innerHTML = goTime + "<img src='bf_img/in.gif'>";
                        break;
                    case "2":
                    case "4":
                    case "5":
                        tr.cells[3].innerHTML = getMatchState(D[1]);
                        if (isFromEndtoAdd) {
                            var TTime = new Date();
                            var nt = D[8].split(":");
                            var nd = D[14].split("-");
                            var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
                            for (var i = 1; i <= matchcount; i++) {
                                if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
                                    var ot = A[i][11].split(":");
                                    var od = A[i][36].split("-");
                                    var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
                                    if (ot2 > nt2) {
                                        MovePlace(A[i][0], D[0]);
                                        break;
                                    }
                                }
                            }
                        }
                        break;
                    case "3":
                        var t = A[matchindex][12].split(",");
                        var t2 = new Date(t[0], t[1], t[2], t[3], t[4], t[5]);
                        goTime = Math.floor((new Date() - t2 - difftime) / 60000) + 46;
                        if (goTime > 90) {
                            var t3 = goTime - 90;
                            goTime = "90+" + (t3 > 15 ? 15 : t3);
                        }
                        if (goTime < 46) goTime = "46";
                        tr.cells[3].innerHTML = goTime + "<img src='bf_img/in.gif'>";
                        break;
                    case "-1":
                        tr.cells[3].innerHTML = getMatchState(D[1]);
                        tr.cells[5].style.color = "red";
                        if (concernId.indexOf("_" + D[0] + "_") == -1) {
                            if (topLeagueIds.indexOf("," + A[matchindex][45] + ",") != -1)
                                window.setTimeout("MoveToTopBottom(" + D[0] + ")", 25000);
                            else
                                window.setTimeout("MoveToBottom(" + D[0] + ")", 25000);
                        }
                        break;
                    default:
                        tr.cells[3].innerHTML = getMatchState(D[1]);
                        MoveToBottom(D[0]);
                        break;
                }
                if (parseInt(A[matchindex][13]) == 2 || parseInt(A[matchindex][13]) == 4 || parseInt(A[matchindex][13]) < 0) {
                    var timeStr = AmountTimeDiff(A[matchindex][11], A[matchindex][36], A[matchindex][43], 1);
                    var dataStr = timeStr.split(" ");
                    document.getElementById("mt_" + D[0]).innerHTML = dataStr[1];
                }
                if (parseInt(A[matchindex][13]) > 0 && window.location.href.toLowerCase().indexOf("oldindex") == -1) {
                    var oddsImgHtml = tr.cells[12].innerHTML;
                    if (oddsImgHtml.indexOf("走地") != -1 && oddsImgHtml.toLowerCase().indexOf("zds.png") == -1) {
                        tr.cells[12].getElementsByTagName('span').item(1).innerHTML = "<img title='有走地' src='image/zds.png'>";
                        tr.cells[12].className = "zd";
                        tr.cells[12].onclick = myAddclick(D[0]);
                        //tr.cells[12].addEventListener("click", myAddclick(D[0]));
                    }
                }
            }
            //判断是否有补时
            if ((parseInt(D[1]) == 1 || parseInt(D[1]) == 3) && A[matchindex][56] != D[21]) {
                A[matchindex][56] = D[21];
                if (D[21] == "") {
                    var timeStr = AmountTimeDiff(A[matchindex][11], A[matchindex][36], A[matchindex][43], 1);
                    var dataStr = timeStr.split(" ");
                    document.getElementById("mt_" + D[0]).innerHTML = dataStr[1];
                }
                else
                    document.getElementById("mt_" + D[0]).innerHTML = (Config.language == 1 ? "補" : "补") + "<span style='color:red;'>" + D[21] + "'</span>";
            }
            var spans = tr.cells[7].getElementsByTagName("span")
            if (spans.length > 1)
                spans[0].style.display = (A[matchindex][50] == "1" ? "" : "none");
            //score
            switch (A[matchindex][13]) {
                case "0":
                    A[matchindex][27] = D[11];
                    if (D[11] == "1")
                        tr.cells[5].innerHTML = "阵容";
                    else
                        tr.cells[5].innerHTML = "-";
                    break;
                case "1":
                    tr.cells[5].innerHTML = A[matchindex][14] + "-" + A[matchindex][15];
                    if (spans.length > 1) {
                        spans[0].innerHTML = A[matchindex][48] + "-" + A[matchindex][49];
                        spans[0].style.color = "blue";
                    }
                    break;
                case "-11":
                case "-14":
                    tr.cells[5].innerHTML = "-";
                    if (spans.length > 1) {
                        spans[0].innerHTML = "-";//角球
                        spans[1].innerHTML = "-";//半场比分
                    }
                    else
                        tr.cells[7].innerHTML = "-";
                    break;
                default:  //2 3 -1 -12 -13                   
                    tr.cells[5].innerHTML = A[matchindex][14] + "-" + A[matchindex][15];
                    if (spans.length > 1) {
                        spans[0].innerHTML = A[matchindex][48] + "-" + A[matchindex][49];
                        spans[1].innerHTML = A[matchindex][16] + "-" + A[matchindex][17];
                        if (A[matchindex][13] == -1)
                            spans[0].style.color = "black";
                        spans[1].style.color = "red";
                    }
                    else {
                        tr.cells[7].innerHTML = A[matchindex][16] + "-" + A[matchindex][17];
                        tr.cells[7].style.color = "red";
                    }
                    break;
            }
            if (obj != null && obj.value == "1") {
                var objScore = document.getElementById("ffScoreDetail");
                var sid = objScore.attributes["sid"].value;
                if (parseInt(sid) == parseInt(A[matchindex][0])) {
                    if (parseInt(A[matchindex][13]) == -1)
                        objScore.innerHTML = "<b><font style='color:red;'>" + A[matchindex][14] + " - " + A[matchindex][15] + "</font></b>";
                    else
                        objScore.innerHTML = "<b><font style='color:blue;'>" + A[matchindex][14] + " - " + A[matchindex][15] + "</font></b>";
                }
            }
            if (scorechange) {
                if (tr.style.display != "none") {
                    hometeam = getTeamName(matchindex, 1, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1)).replace("<font color=#880000>(中)</font>", "(中)");//.substring(0, 7);
                    guestteam = getTeamName(matchindex, 2, (isCompanyPage ? companyID : 3), (isCompanyPage ? 2 : 1));//.substring(0, 7);
                    sclassname = A[matchindex][2 + lang];
                    if (score1change) {
                        hometeam = "<font color=red>" + hometeam + "</font>";
                        score1 = "<font color=red>" + D[2] + "</font>";
                        score2 = "<font color=blue>" + D[3] + "</font>";
                        ShowFlash(D[0], matchindex, 1);
                    }
                    if (score2change) {
                        guestteam = "<font color=red>" + guestteam + "</font>";
                        score1 = "<font color=blue>" + D[2] + "</font>";
                        score2 = "<font color=red>" + D[3] + "</font>";
                        ShowFlash(D[0], matchindex, 2);
                    }
                    notify += sclassname + ":" + hometeam + " <font color=blue>" + score1 + "-" + score2 + "</font> " + guestteam + " &nbsp; ";

                    if (Config.winLocation > -1 && parseInt(D[1]) >= -1 && isShowWin) {
                        if (matchNum % 2 == 0)
                            winStr += "<tr bgcolor=#ffffff height=34 align=center class=line><td><font color=#1705B1>" + sclassname + "</font></td><td> " + tr.cells[3].innerHTML + "</td><td><b>" + hometeam + "</b></td><td width=11% style='font-size: 18px;font-family:Verdana;font-weight:bold;'>" + score1 + "-" + score2 + "</td><td>" + Goal2GoalCn(A[matchindex][29]) + "</td><td><b>" + guestteam + "</b></td></tr>";
                        else
                            winStr += "<tr bgcolor=#FDF1E7 height=34 align=center class=line><td><font color=#1705B1>" + sclassname + "</font></td><td> " + tr.cells[3].innerHTML + "</td><td><b>" + hometeam + "</b></td><td width=11% style='font-size: 18px;font-family:Verdana;font-weight:bold;'>" + score1 + "-" + score2 + "</td><td>" + Goal2GoalCn(A[matchindex][29]) + "</td><td><b>" + guestteam + "</b></td></tr>";
                        matchNum = matchNum + 1
                    }
                }
            } //scorechange
        }
        if (matchNum > 0) ShowCHWindow(winStr, matchNum);
        var objNotify = document.getElementById("notify");
        if (notify != "") {
            if (delHtmlTag(objNotify.innerHTML) == delHtmlTag(_spreadBaInfo.freeInfo))
                objNotify.innerHTML = notify;
            else
                objNotify.innerHTML += notify;
            notifyTimer = window.setTimeout("clearNotify('" + notify + "')", 20000);
        }
        else if (objNotify.innerHTML == "")
            objNotify.innerHTML = _spreadBaInfo.freeInfo;

    } catch (e) { console.log(e); }
}
//function zqOddsChange(data) {
//    //console.log("odds:" + data);
//    try {
//        var oldTO;
//        var j = 0;
//        //var root = oddsHttp.responseXML.documentElement.childNodes[0];
//        var dataList = data.split("$$");
//        var oddsDataList = dataList[0].split('!');
//        var D = new Array();
//        var odds, old = new Array();
//        var needSound = false;
//        for (var i = 0; i < oddsDataList.length; i++) {
//            odds = oddsDataList[i];
//            D = odds.split(",");
//            tr = document.getElementById("tr1_" + D[0]);
//            if (tr == null) return;
//            var tempIsMaintain = dataList[1] == "1";
//            var matchindex = getDataIndex(D[0]);
//            var overGoalType = 0;
//            if (typeof (matchindex) != 'undefined' && A.length > matchindex) {
//                if (parseInt(A[matchindex][13]) == 4)
//                    overGoalType = 1;
//                else if (parseInt(A[matchindex][13]) == 5)
//                    overGoalType = 2;
//            }
//            old = tr.attributes["odds"].value.split(",");
//            if (old.length >= 17 && old != odds) {//判断新旧赔率数据
//                for (var j = 3; j < 13; j++) {
//                    if (old[j] != "" && D[j] != "") {
//                        if (D[j] > old[j]) D[j] = "<span class=\"up\">" + D[j] + "</span>";
//                        else if (D[j] < old[j]) D[j] = "<span class=\"down\">" + D[j] + "</span>";
//                    }
//                    if (j == 4) j++;
//                    if (j == 8) j = j + 2;
//                }

//                window.setTimeout("restoreOddsColor(" + D[0] + ")", 30000);
//                if (Config.oddsSound == 1) {
//                    if (tr.style.display != "none")
//                        needSound = true;
//                }
//            }
//            if (old.length >= 17 && old != odds && old[2] != "") {//判断让球新旧盘口
//                if (D[2] > old[2]) D[2] = "<span class=\"up\">" + Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>") + "</span>";
//                else if (D[2] < old[2]) D[2] = "<span class=\"down\">" + Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>") + "</span>";
//                else D[2] = Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>");
//            }
//            else D[2] = Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>");
//            if (old.length >= 17 && old != odds && old[10] != "") {//判断大小新旧盘口
//                if (D[10] > old[10]) D[10] = "<span class=\"up\">" + Goal2GoalCn2(D[10]) + "</span>";
//                else if (D[10] < old[10]) D[10] = "<span class=\"down\">" + Goal2GoalCn2(D[10]) + "</span>";
//                else D[10] = Goal2GoalCn2(D[10]);
//            }
//            else D[10] = Goal2GoalCn2(D[10]);
//            var tmp = "";
//            var displayHtml = tempIsMaintain ? " style='display:none;'" : "";  //判断是维护，维护需要隐藏赔率
//            if (Config.haveLetGoal == 1)//主赔率
//                tmp = "<div class=odds" + (D[13] == "2" ? 4 : 1) + displayHtml + ">" + (D[14] == "0" ? D[3] : "&nbsp;") + "</div>";
//            if (Config.haveTotal == 1)
//                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 2) + displayHtml + ">" + (D[16] == "0" ? D[11] : "&nbsp;") + "</div>";
//            if (Config.haveEurope == 1)
//                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 3) + displayHtml + ">" + (D[15] == "0" ? D[6] : "&nbsp;") + "</div>";
//            tr.cells[8 + Config.oddsColumnIndexAdd].innerHTML = tmp;
//            tmp = "";
//            var oddsCount = 0;

//            if (Config.haveLetGoal == 1) {//盘口
//                tmp = "<div class=odds" + (D[13] == "2" ? 4 : 1) + displayHtml + ">" + (D[14] == "0" ? D[2] : "封") + "</div>";
//                oddsCount++;
//            }
//            if (Config.haveTotal == 1) {
//                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 2) + displayHtml + ">" + (D[16] == "0" ? D[10] : "封") + "</div>";
//                oddsCount++;
//            }
//            if (Config.haveEurope == 1) {
//                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 3) + displayHtml + ">" + (D[15] == "0" ? D[7] : "封") + "</div>";
//                oddsCount++;
//            }
//            var height = (oddsCount == 1 ? "31" : (oddsCount == 2 ? "33" : "49"));
//            var maintainHtml = "<div class='maintain' style='line-height:" + height + "px;height:" + height + "px;" + (tempIsMaintain ? "display:block;" : "") + "'>维护</div>";
//            tr.cells[9 + Config.oddsColumnIndexAdd].innerHTML = tmp + maintainHtml;

//            tmp = "";
//            if (Config.haveLetGoal == 1)//客赔率
//                tmp = "<div class=odds" + (D[13] == "2" ? 4 : 1) + displayHtml + ">" + (D[14] == "0" ? D[4] : "&nbsp;") + "</div>";
//            if (Config.haveTotal == 1)
//                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 2) + displayHtml + ">" + (D[16] == "0" ? D[12] : "&nbsp;") + "</div>";
//            if (Config.haveEurope == 1)
//                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 3) + displayHtml + ">" + (D[15] == "0" ? D[8] : "&nbsp;") + "</div>";
//            tr.cells[10 + Config.oddsColumnIndexAdd].innerHTML = tmp;
//            tmp = "";
//            if (D[13] == "1" || D[13] == "2") {
//                if (D[13] == "1") tmp = "<img src='image/zd.gif' height=10 width=10 title='有走地'>";
//                if (D[13] == "2") tmp = "<img src='image/zd2.gif' height=10 width=10 title='正在走地'>";
//                if (typeof (matchindex) != 'undefined' && A.length > matchindex && parseInt(A[matchindex][13]) >= -1 && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zds.png") == -1) {
//                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = "<img title='有走地' src='image/zds.png'>";
//                    tr.cells[11 + Config.oddsColumnIndexAdd].className = "zd";
//                    tr.cells[11 + Config.oddsColumnIndexAdd].onclick = myAddclick(D[0]);
//                }
//            }
//            if ((D[13] == "1" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd.gif") == -1) || (D[13] == "2" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd2.gif") == -1) || tmp == "") {
//                tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(0).innerHTML = tmp;
//                if (isCompanyPage && tmp == "") {
//                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = tmp;
//                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('onclick');
//                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('class');
//                }
//            }
//            tr.attributes["odds"].value = odds;
//        }
//        if (needSound) ShowOddsSound();
        
//        if (tempIsMaintain != isMaintain) {
//            isMaintain = tempIsMaintain;
//            SetMaintain();
//        }
//    } catch (e) { console.log(e); }
//}
function zqOddsChange(data) {
    //console.log("odds:" + data);
    try {
        var oldTO;
        var j = 0;
        var dataList = data.split("$$");
        var oddsDataList = dataList[0].split('!');
        var D = new Array();
        var odds, old = new Array();
        var needSound = false;
        for (var i = 0; i < oddsDataList.length; i++) {
            odds = oddsDataList[i];
            D = odds.split(",");
            tr = document.getElementById("tr1_" + D[0]);
            if (tr == null) return;
            var tempIsMaintain = dataList[1] == "1";
            var matchindex = getDataIndex(D[0]);
            var overGoalType = 0;
            if (typeof (matchindex) != 'undefined' && A.length > matchindex && D.length > 19) {
                if (parseInt(A[matchindex][13]) == 4)
                    overGoalType = 1;
                else if (parseInt(A[matchindex][13]) == 5)
                    overGoalType = 2;
            }
            old = tr.attributes["odds"].value.split(",");
            if (old.length >= 17 && old != odds) {//判断新旧赔率数据
                if (overGoalType == 0) {//常规时间
                    for (var j = 3; j < 13; j++) {
                        if (old[j] != "" && D[j] != "") {
                            if (D[j] > old[j]) D[j] = "<span class=\"up\">" + D[j] + "</span>";
                            else if (D[j] < old[j]) D[j] = "<span class=\"down\">" + D[j] + "</span>";
                        }
                        if (j == 4) j++;
                        if (j == 8) j = j + 2;
                    }
                } else {//加时
                    var indexList = overGoalType == 1 ? [20, 22, 25, 27, 30, 31, 32] : [35, 37, 40, 42, 45, 46, 47];
                    for (var k = 0; j < indexList.length; k++) {
                        var j = indexList[k];
                        if (old[j] != "" && D[j] != "") {
                            if (D[j] > old[j]) D[j] = "<span class=\"up\">" + D[j] + "</span>";
                            else if (D[j] < old[j]) D[j] = "<span class=\"down\">" + D[j] + "</span>";
                        }
                    }                   
                }
                window.setTimeout("restoreOddsColor(" + D[0] + ")", 30000);
                if (Config.oddsSound == 1) {
                    if (tr.style.display != "none")
                        needSound = true;
                }
            }
            var letgoalIndex = 2;
            var totalIndex = 10;
            var homeOddsIndex = 3, guestOddsIndex = 4, bigOddsIndex = 11, smallOddsIndex = 12, winOddsIndex = 6, drawOddsIndex = 7, loseOddsIndex = 8, letgoalFengIndex = 14, totalFengIndex = 16, ouFengIndex = 15;
            if (overGoalType == 1) {
                letgoalIndex = 21;
                totalIndex = 26;
                homeOddsIndex = 20;
                guestOddsIndex = 22;
                bigOddsIndex = 25;
                smallOddsIndex = 27;
                winOddsIndex = 30;
                drawOddsIndex = 31;
                loseOddsIndex = 32;
                letgoalFengIndex = 23;
                totalFengIndex = 28;
                ouFengIndex = 33;
            } else if (overGoalType == 2) {
                letgoalIndex = 36;
                totalIndex = 41;
                homeOddsIndex = 35;
                guestOddsIndex = 37;
                bigOddsIndex = 40;
                smallOddsIndex = 42;
                winOddsIndex = 45;
                drawOddsIndex = 46;
                loseOddsIndex = 47;
                letgoalFengIndex = 38;
                totalFengIndex = 43;
                ouFengIndex = 48;
            }
            if (old.length >= 17 && old != odds && old[letgoalIndex] != "") {//判断让球新旧盘口
                if (D[letgoalIndex] > old[letgoalIndex]) D[letgoalIndex] = "<span class=\"up\">" + Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>") + "</span>";
                else if (D[letgoalIndex] < old[letgoalIndex]) D[letgoalIndex] = "<span class=\"down\">" + Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>") + "</span>";
                else D[letgoalIndex] = Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>");
            }
            else D[letgoalIndex] = Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>");
            
            if (old.length >= 17 && old != odds && old[totalIndex] != "") {//判断大小新旧盘口
                if (D[totalIndex] > old[totalIndex]) D[totalIndex] = "<span class=\"up\">" + Goal2GoalCn2(D[totalIndex]) + "</span>";
                else if (D[totalIndex] < old[totalIndex]) D[totalIndex] = "<span class=\"down\">" + Goal2GoalCn2(D[totalIndex]) + "</span>";
                else D[totalIndex] = Goal2GoalCn2(D[totalIndex]);
            }
            else D[totalIndex] = Goal2GoalCn2(D[totalIndex]);
            var tmp = "";
            var displayHtml = tempIsMaintain ? " style='display:none;'" : "";  //判断是维护，维护需要隐藏赔率
            var letgoalClick = " onclick='AsianOdds(" + D[0] + ")'";
            var totalClick = " onclick='TotalOdds(" + D[0] + ")'";
            var europeClick = " onclick='EuropeOdds(" + D[0] + ")'"; 
            if (Config.haveLetGoal == 1)//主赔率
                tmp = "<div class=odds" + (D[13] == "2" ? 4 : 1) + displayHtml + letgoalClick + ">" + (D[letgoalFengIndex] == "0" ? D[homeOddsIndex] : "&nbsp;") + "</div>";
            if (Config.haveTotal == 1)
                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 2) + displayHtml + totalClick + ">" + (D[totalFengIndex] == "0" ? D[bigOddsIndex] : "&nbsp;") + "</div>";
            if (Config.haveEurope == 1)
                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 3) + displayHtml + europeClick + ">" + (D[ouFengIndex] == "0" ? D[winOddsIndex] : "&nbsp;") + "</div>";
            tr.cells[8 + Config.oddsColumnIndexAdd].innerHTML = tmp;
            tmp = "";
            var oddsCount = 0;

            if (Config.haveLetGoal == 1) {//盘口
                tmp = "<div class=odds" + (D[13] == "2" ? 4 : 1) + displayHtml + letgoalClick + ">" + (D[letgoalFengIndex] == "0" ? D[letgoalIndex] : "封") + "</div>";
                oddsCount++;
            }
            if (Config.haveTotal == 1) {
                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 2) + displayHtml + totalClick + ">" + (D[totalFengIndex] == "0" ? D[totalIndex] : "封") + "</div>";
                oddsCount++;
            }
            if (Config.haveEurope == 1) {
                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 3) + displayHtml + europeClick + ">" + (D[ouFengIndex] == "0" ? D[drawOddsIndex] : "封") + "</div>";
                oddsCount++;
            }
            var height = (oddsCount == 1 ? "31" : (oddsCount == 2 ? "33" : "49"));
            var maintainHtml = "<div class='maintain' style='line-height:" + height + "px;height:" + height + "px;" + (tempIsMaintain ? "display:block;" : "") + "'>维护</div>";
            tr.cells[9 + Config.oddsColumnIndexAdd].innerHTML = tmp + maintainHtml;

            tmp = "";
            if (Config.haveLetGoal == 1)//客赔率
                tmp = "<div class=odds" + (D[13] == "2" ? 4 : 1) + displayHtml + letgoalClick + ">" + (D[letgoalFengIndex] == "0" ? D[guestOddsIndex] : "&nbsp;") + "</div>";
            if (Config.haveTotal == 1)
                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 2) + displayHtml + totalClick + ">" + (D[totalFengIndex] == "0" ? D[smallOddsIndex] : "&nbsp;") + "</div>";
            if (Config.haveEurope == 1)
                tmp += "<div class=odds" + (D[13] == "2" ? 4 : 3) + displayHtml + europeClick + ">" + (D[ouFengIndex] == "0" ? D[loseOddsIndex] : "&nbsp;") + "</div>";
            tr.cells[10 + Config.oddsColumnIndexAdd].innerHTML = tmp;
            tmp = "";
            if (D[13] == "1" || D[13] == "2") {
                if (D[13] == "1") tmp = "<img src='image/zd.gif' height=10 width=10 title='有走地'>";
                if (D[13] == "2") tmp = "<img src='image/zd2.gif' height=10 width=10 title='正在走地'>";
                if (typeof (matchindex) != 'undefined' && A.length > matchindex && parseInt(A[matchindex][13]) >= -1 && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zds.png") == -1) {
                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = "<img title='有走地' src='image/zds.png'>";
                    tr.cells[11 + Config.oddsColumnIndexAdd].className = "zd";
                    tr.cells[11 + Config.oddsColumnIndexAdd].onclick = myAddclick(D[0]);
                }
            }
            if ((D[13] == "1" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd.gif") == -1) || (D[13] == "2" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd2.gif") == -1) || tmp == "") {
                tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(0).innerHTML = tmp;
                if (isCompanyPage && tmp == "") {
                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = tmp;
                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('onclick');
                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('class');
                }
            }
            tr.attributes["odds"].value = odds;
        }
        if (needSound) ShowOddsSound();

        if (tempIsMaintain != isMaintain) {
            isMaintain = tempIsMaintain;
            SetMaintain();
        }
    } catch (e) { console.log(e); }
}
function SetMaintain() {
    var root = oddsHttp.responseXML.documentElement.childNodes[0];
    var D = new Array();
    var odds = new Array();
    for (var i = 0; i < root.childNodes.length; i++) {
        if (document.all && parseInt(ieNum) < 10)
            odds = root.childNodes[i].text; //id,oddsid,goal,home,away,zoudi,isStopLive
        else
            odds = root.childNodes[i].textContent;
        D = odds.split(",");
        tr = document.getElementById("tr1_" + D[0]);
        if (tr == null) continue;
        var upOddsList = tr.cells[8 + Config.oddsColumnIndexAdd];
        for (var j = 0; j < upOddsList.childNodes.length; j++) {
            var obj = upOddsList.childNodes[j];
            obj.style.display = !isMaintain ? "block" : "none";
        }
        var arrList = tr.cells[9 + Config.oddsColumnIndexAdd];
        for (var j = 0; j < arrList.childNodes.length; j++) {
            var obj = arrList.childNodes[j];
            if (j == arrList.childNodes.length - 1) {
                obj.style.display = isMaintain ? "block" : "none";
            }
            else {
                obj.style.display = !isMaintain ? "block" : "none";
                }
        }
        var downOddsList = tr.cells[10 + Config.oddsColumnIndexAdd];
        for (var j = 0; j < downOddsList.childNodes.length; j++) {
            var obj = downOddsList.childNodes[j];
            obj.style.display = !isMaintain ? "block" : "none";
        }
    }
}
function delHtmlTag(str) {
    return str.replace(/<[^>]+>/g, ""); //去掉所有的html标记
}
function getElementPos(elementId) {
    var ua = navigator.userAgent.toLowerCase();
    var isOpera = (ua.indexOf('opera') != -1);
    var isIE = (ua.indexOf('msie') != -1 && !isOpera); // not opera spoof
    var el = document.getElementById(elementId);
    if (el.parentNode === null || el.style.display == 'none') {
        return false;
    }
    var parent = null;
    var pos = [];
    var box;
    if (el.getBoundingClientRect)    //IE
    {
        box = el.getBoundingClientRect();
        var scrollTop = Math.max(document.documentElement.scrollTop, document.body.scrollTop);
        var scrollLeft = Math.max(document.documentElement.scrollLeft, document.body.scrollLeft);
        return { x: box.left + scrollLeft, y: box.top + scrollTop };
    } else if (document.getBoxObjectFor)    // gecko    
    {
        box = document.getBoxObjectFor(el);
        var borderLeft = (el.style.borderLeftWidth) ? parseInt(el.style.borderLeftWidth) : 0;
        var borderTop = (el.style.borderTopWidth) ? parseInt(el.style.borderTopWidth) : 0;
        pos = [box.x - borderLeft, box.y - borderTop];
    } else    // safari & opera    
    {
        pos = [el.offsetLeft, el.offsetTop];
        parent = el.offsetParent;
        if (parent != el) {
            while (parent) {
                pos[0] += parent.offsetLeft;
                pos[1] += parent.offsetTop;
                parent = parent.offsetParent;
            }
        }
        if (ua.indexOf('opera') != -1 || (ua.indexOf('safari') != -1 && el.style.position == 'absolute')) {
            pos[0] -= document.body.offsetLeft;
            pos[1] -= document.body.offsetTop;
        }
    }
    if (el.parentNode) {
        parent = el.parentNode;
    } else {
        parent = null;
    }
    while (parent && parent.tagName != 'BODY' && parent.tagName != 'HTML') { // account for any scrolled ancestors
        pos[0] -= parent.scrollLeft;
        pos[1] -= parent.scrollTop;
        if (parent.parentNode) {
            parent = parent.parentNode;
        } else {
            parent = null;
        }
    }
    return { x: pos[0], y: pos[1] };
}
function GetBrowserVersion() {
    var ua = navigator.userAgent.toLowerCase();
    var num = "";
    window.ActiveXObject ? num = ua.match(/msie ([\d.]+)/)[1] : '';
    return num;
}
function showTeamPanlu(ID) {
    var theURL = "http://bf.titan007.com/panlu/" + ID + (Config.language == 1 ? "" : "cn") + ".htm";
    window.open(theURL, "", "width=640,height=700,top=10,left=100,resizable=yes,scrollbars=yes");
}
//时区--------------------------------------------------------------
function SelectTimeZone(Page) {
    document.getElementById("TimeZoneList").innerHTML = '<iframe src="' + Page + '" frameborder="0" width="660" height="455" scrolling="no"></iframe>';
    with (document.getElementById("TimeZoneList_div").style) {
        left = (window.screen.width - parseInt(width)) / 2 + "px";
        top = (window.screen.height - parseInt(height)) / 2 + "px";
        display = "";
    }
}

function GetCurrentTimeZone() {
    var now = new Date();
    var tz = 0 - now.getTimezoneOffset() / 60;//本地时区小时数
    var mtz = Math.floor(tz);
    var stz = (tz - mtz) * 60;
    var tzstr = "";
    if (tz >= 0)
        tzstr = "+";
    else
        tzstr = "-";
    if (mtz == 0)
        tzstr += "0";
    if ((tz > 0 && mtz < 10) || (tz < 0 && mtz > -10))
        tzstr += "0";
    tzstr += Math.abs(mtz).toString() + Math.abs(stz).toString();
    if (stz == 0)
        tzstr += "0";
    return tzstr;
}

function CloseTimeZoneList() {
    document.getElementById("TimeZoneList_div").style.display = 'none';
}

var difference_Hour = 0;
var difference_Minute = 0;
var timezone_TZ = "";

function GetTimeZone(lg, DefaultTZ)	//获取时区设置
{
    if (typeof (DefaultTZ) == "undefined")
        DefaultTZ = GetCurrentTimeZone();	//默认时区

    var STZ_Hour = 8;
    var DST = false;
    var rlt = "";
    if (document.cookie.indexOf("bet007TZbegin") != -1 && document.cookie.indexOf("bet007TZend") != -1)
        timezone_TZ = document.cookie.substring(document.cookie.indexOf("bet007TZbegin") + 14, document.cookie.indexOf("bet007TZend")).toUpperCase();
    if (document.cookie.indexOf("bet007DSTbegin") != -1 && document.cookie.indexOf("bet007DSTend") != -1)
        DST = (document.cookie.substring(document.cookie.indexOf("bet007DSTbegin") + 15, document.cookie.indexOf("bet007DSTend")) == "1") ? true : false;

    if (timezone_TZ == "")
        timezone_TZ = DefaultTZ;

    if (timezone_TZ != "AUTO") {
        rlt = 'GMT' + timezone_TZ;
        var TZ_Hour = parseFloat(timezone_TZ.substring(0, 3));
        var TZ_Minute = parseFloat(timezone_TZ.substring(3, 5));
        difference_Minute = TZ_Minute;
        if (TZ_Hour < 0) {
            difference_Hour = 0 - (STZ_Hour - TZ_Hour);
            difference_Minute = 0 - difference_Minute;
        }
        else {
            difference_Hour = TZ_Hour - STZ_Hour;
        }
    }
    else if (timezone_TZ == "AUTO") {
        DST = false;          //自动状况去掉夏令时cookie
        if (lg == 0)
            rlt = "自動";
        else if (lg == 1)
            rlt = "自动";
        else if (lg == 2)
            rlt = "Auto";
        else if (lg == 3)
            rlt = "Tự động";
        else if (lg == 4)
            rlt = "อัตโนมัติ";
        else if (lg == 5)
            rlt = "자동";
        var LTimeZone = new Date().getTimezoneOffset() / 60;
        STZ_Hour = 0 - STZ_Hour;
        if (LTimeZone < 0) {
            difference_Hour = STZ_Hour - LTimeZone;
        }
        else {
            difference_Hour = 0 - (LTimeZone - STZ_Hour);
            difference_Minute = 0 - difference_Minute;
        }
    }
    if (DST)	//Daylight Saving Time夏令时
    {
        difference_Hour += 1;
        if (lg == 0)
            rlt += "(夏令時)";
        else if (lg == 1)
            rlt += "(夏令时)";
        else if (lg == 2)
            rlt += "(DST)";
        else if (lg == 3)
            rlt += "(Giờ mùa)";
        else if (lg == 4)
            rlt += "(DST)";
        else if (lg == 5)
            rlt += "(서머타임)";
    }
    return rlt;
}

function TimeZone_formatNumber(s) {
    if (s < 10)
        return "0" + s;
    return s;
}

function AmountTimeDiff(dateStr, dateStr2, yearStr, rtvFormat) {
    var date_sl = dateStr.split(":");
    var date_sl2 = dateStr2.split("-");
    var d1 = new Date(parseFloat(yearStr), parseFloat(date_sl2[0]) - 1, parseFloat(date_sl2[1]), parseFloat(date_sl[0]) + difference_Hour, parseFloat(date_sl[1]) + difference_Minute, 0, 0);
    var year = d1.getFullYear();
    var month = TimeZone_formatNumber(d1.getMonth() + 1);
    var day = TimeZone_formatNumber(d1.getDate());
    var hour = TimeZone_formatNumber(d1.getHours());
    var minute = TimeZone_formatNumber(d1.getMinutes());
    var second = TimeZone_formatNumber(d1.getSeconds());
    switch (rtvFormat) {
        case 0:
            return year + "," + month + "," + day + "," + hour + "," + minute + "," + second;
        case 1:
            return month + "月" + day + "日 " + hour + ":" + minute;
        case 2:
            return month + "-" + day + "-" + year + " " + hour + ":" + minute + ":" + second;
    }
}

function setGoalShow(t, obj) {
    if (t == 1)
        Config.haveLetGoal = (obj.checked ? 1 : 0);
    else if (t == 2)
        Config.haveTotal = (obj.checked ? 1 : 0);
    else
        Config.haveEurope = (obj.checked ? 1 : 0);
    Config.writeCookie();
    MakeTable(false);
    showodds();
}
function getPageHeight() {
    var pageHeight = window.innerHeight;
    if (typeof pageWindth != "number") {
        if (document.compatMode == "CSS1Compat") {
            pageHeight = document.documentElement.clientHeight;
        }
        else {
            pageHeight = document.body.clientHeight;
        }
    }
    return pageHeight;
}
//------广告显示控制相关-----
var showMatchCount = 0, allTextAdCount = 13, compayScheduleCount = 0;
function getMatchCount() {
    //用每天第一场比赛时间做比赛，超过10小时清空用户选择
    var firstMatchTime = getCookie("bfWin007FirstMatchTime");
    if (firstMatchTime != null && firstMatchTime != firstschematchtime) {
        var arrOldTime = firstMatchTime.split(',');
        var arrNewTime = firstschematchtime.split(',');
        var oldMatchTime = new Date(arrOldTime[0], arrOldTime[1], arrOldTime[2], arrOldTime[3], arrOldTime[4], arrOldTime[5]);
        var newMatchTime = new Date(arrNewTime[0], arrNewTime[1], arrNewTime[2], arrNewTime[3], arrNewTime[4], arrNewTime[5]);
        var timeSpan = (newMatchTime.getTime() - oldMatchTime.getTime()) / 1000;
        var day = parseInt(timeSpan / (24 * 60 * 60));//计算整数天数
        var afterDay = timeSpan - day * 24 * 60 * 60;//取得算出天数后剩余的秒数
        var hour = parseInt(afterDay / (60 * 60));//计算整数小时数
        if (day > 0 || hour > 10) {
            writeCookie("bfWin007FirstMatchTime", firstschematchtime)
            hiddenID = "_";
            delLocalStorage("Bet007live_hiddenID");
            delCookie("FS007Filter");
            isChooseMatch = false;
            useIsChoose = false;
            Config.isSimple = 1;
            Config.sclassType = 0;
            Config.writeCookie();
            document.getElementById("button6").className = "btn33";
            document.getElementById("button7").className = "btn33_on";
        }
    }
    else if (firstMatchTime == null)
        writeCookie("bfWin007FirstMatchTime", firstschematchtime);
    var ArrayHiddenID = hiddenID.split("_");
    showMatchCount = 0;
    var importantScheduleIDList = "";
    try {
        for (var i = 1; i <= matchcount; i++) {
            for (j = 1; j <= sclasscount; j++) {
                if (A[i][2] == B[j][0]) {
                    if ((!useIsChoose && !isChooseMatch) || Config.isSimple == 1) {// 没任何操作前默认显示精简 ；从公司页的精简跳到首页和旧比分精简时需要加上没有开盘的公司
                        if (B[j][10] == "1" && hiddenID.indexOf("_" + A[i][0] + "_") == -1 || (B[j][10] == "2" && A[i][62] == 1)) {
                            hiddenID += A[i][0] + "_";
                        }
                    }
                    if (B[j][10] == "1" && importantScheduleIDList.indexOf(A[i][0]) == -1 || (B[j][10] == "2" && A[i][62] == 1))
                        importantScheduleIDList += A[i][0] + ",";
                    break;
                }
            }
        }
    }
    catch(e) {
        console.log("i:" + i + "   j:" + j);
    }
    if (Config.isSimple == 1) {//隐藏取消精简的比赛
        for (var i = 1; i < ArrayHiddenID.length - 1; i++) {
            if (importantScheduleIDList.indexOf(ArrayHiddenID[i]) == -1)
                hiddenID = hiddenID.replace("_" + ArrayHiddenID[i] + "_", "_");
        }
    }
    //if (isCompanyPage) {//公司页面需赔率文件里面的数据来判断条数
    //    oddsHttp.open("get", "vbsxml/goal" + companyID + ".xml?r=007" + Date.parse(new Date()), false);
    //    oddsHttp.send(null);
    //    if (document.all && parseInt(ieNum) < 10)
    //        companyScheduleIdList = oddsHttp.responseXML.documentElement.childNodes[1].text;
    //    else
    //        companyScheduleIdList = oddsHttp.responseXML.documentElement.childNodes[1].textContent;
    //    compayScheduleCount = companyScheduleIdList.split(',').length - 1;
    //}
    for (var i = 1; i <= matchcount; i++) {
        if (matchType >= 0) {
            A[i][25] = parseInt(A[i][25]);
            if (!(matchType == 0 && A[i][25] > 0 || matchType == 1 && (A[i][25] == 1 || A[i][25] === 3) || matchType == 2 && (A[i][25] == 2 || A[i][25] === 3))) {
                A[i][0] = 0;
                continue;
            }
        }
        if (isCompanyPage && (hiddenID == "_" || hiddenID.indexOf("_" + A[i][0] + "_") != -1) && companyScheduleIdList.indexOf(A[i][0]) != -1)
            showMatchCount++;
        else if (!isCompanyPage && (hiddenID == "_" || hiddenID.indexOf("_" + A[i][0] + "_") != -1))
            showMatchCount++;
    }
    for (var j = 1; j <= sclasscount; j++) {
        B[j][6] = 0;
        B[j][7] = 0;
    }
    for (j = 0; j < C.length; j++) {
        C[j][2] = 0;
        C[j][4] = 0;
    }
}
//--------------------------------------------赔率---------------------------------
function getoddsxml() {
    oddsHttp.open("get", staticUrl + (window.location.href.toLowerCase().indexOf("index2in1") != -1 ? "vbsxml/ch_goal" + companyID + ".xml?r=007" : "vbsxml/ch_goalbf3.xml?r=007") + Date.parse(new Date()), true);
    //oddsHttp.open("get", "vbsxml/ch_goalBf3.xml?r=007" + Date.parse(new Date()), true);
    oddsHttp.onreadystatechange = oddsrefresh;
    oddsHttp.send(null);
    getoddsxmlTimer = window.setTimeout("getoddsxml()", 4000);//10000
}
function oddsrefresh() {
    if (oddsHttp.readyState != 4 || (oddsHttp.status != 200 && oddsHttp.status != 0)) return;
    if (oldOddsXML == oddsHttp.responseText)
        return;
    oldOddsXML = oddsHttp.responseText;
    showodds();
}
//function showodds() {
//    try {
//        var oldTO;
//        var j = 0;
//        var root = oddsHttp.responseXML.documentElement.childNodes[0];
//        for (var i = 0; i < oddsHttp.responseXML.documentElement.childNodes.length; i++) {
//            if (oddsHttp.responseXML.documentElement.childNodes[i].nodeName == "isMaintain") {
//                if (document.all && parseInt(ieNum) < 10)
//                    isMaintain = oddsHttp.responseXML.documentElement.childNodes[i].text == "1"; //id,oddsid,goal,home,away,zoudi,isStopLive
//                else
//                    isMaintain = oddsHttp.responseXML.documentElement.childNodes[i].textContent == "1";
//                break;
//            }
//        }
        
//        var D = new Array();
//        var odds, old = new Array();
//        var needSound = false;
//        for (var i = 0; i < root.childNodes.length; i++) {
//            if (document.all && parseInt(ieNum) < 10)
//                odds = root.childNodes[i].text; //id,oddsid,goal,home,away,zoudi,isStopLive
//            else
//                odds = root.childNodes[i].textContent;
//            D = odds.split(",");
//            tr = document.getElementById("tr1_" + D[0]);
//            if (tr == null) continue;
//            var matchindex = getDataIndex(D[0]);
//            //var matchindex = tr.attributes["index"].value;
//            var { letGoalResult, totalResult, europeResult } = GetFinishWinOddsColor(A[matchindex], D);
//            old = tr.attributes["odds"].value.split(",");
//            if (old.length >= 17 && old != odds) {
//                for (var j = 3; j < 13; j++) {
//                    if (old[j] != "" && D[j] != "") {
//                        if (D[j] > old[j]) D[j] = "<span class=\"up\">" + D[j] + "</span>";
//                        else if (D[j] < old[j]) D[j] = "<span class=\"down\">" + D[j] + "</span>";
//                    }
//                    if (j == 4) j++;
//                    if (j == 8) j = j + 2;
//                }

//                window.setTimeout("restoreOddsColor(" + D[0] + ")", 30000);
//                if (Config.oddsSound == 1) {
//                    if (tr.style.display != "none")
//                        needSound = true;
//                }
//            }
//            if (old.length >= 17 && old != odds && old[2] != "") {
//                if (D[2] > old[2]) D[2] = "<span class=\"up\">" + Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>") + "</span>";
//                else if (D[2] < old[2]) D[2] = "<span class=\"down\">" + Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>") + "</span>";
//                else D[2] = Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>");
//            }
//            else D[2] = Goal2GoalCn(D[2]).replace("受", "<font color='red'>*</font>");
//            if (old.length >= 17 && old != odds && old[10] != "") {
//                if (D[10] > old[10]) D[10] = "<span class=\"up\">" + Goal2GoalCn2(D[10]) + "</span>";
//                else if (D[10] < old[10]) D[10] = "<span class=\"down\">" + Goal2GoalCn2(D[10]) + "</span>";
//                else D[10] = Goal2GoalCn2(D[10]);
//            }
//            else D[10] = Goal2GoalCn2(D[10]);
//            var displayHtml = isMaintain ? " style='display:none;'" : "";
//            var tmp = "";
//            if (Config.haveLetGoal == 1)
//                tmp = "<div class='odds" + (D[13] == "2" ? 4 : 1) + (letGoalResult == 0 ? " winColor" : "") + "'" + displayHtml + " > " + (D[14] == "0" ? D[3] : "&nbsp;") + "</div > ";
//            if (Config.haveTotal == 1)
//                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 2) + (totalResult == 0 ? " winColor" : "") + "'" + displayHtml + ">" + (D[16] == "0" ? D[11] : "&nbsp;") + "</div>";
//            if (Config.haveEurope == 1)
//                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 3) + (europeResult == 0 ? " winColor" : "") + "'" + displayHtml + ">" + (D[15] == "0" ? D[6] : "&nbsp;") + "</div>";
//            tr.cells[8 + Config.oddsColumnIndexAdd].innerHTML = tmp;
//            tmp = "";
//            var oddsCount = 0;
            
//            if (Config.haveLetGoal == 1) {
//                tmp = "<div class='odds" + (D[13] == "2" ? 4 : 1) + "'" + displayHtml+ ">" + (D[14] == "0" ? D[2] : "封") + "</div>";
//                oddsCount++;
//            }
//            if (Config.haveTotal == 1) {
//                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 2) + "'" + displayHtml+ ">" + (D[16] == "0" ? D[10] : "封") + "</div>";
//                oddsCount++;
//            }
//            if (Config.haveEurope == 1) {
//                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 3) + (europeResult == 1 ? " winColor" : "") + "'" + displayHtml+ ">" + (D[15] == "0" ? D[7] : "封") + "</div>";
//                oddsCount++;
//            }
//            //background:" + tr.getAttribute("bgcolor")+";
//            var height = (oddsCount == 1 ? "31" : (oddsCount == 2 ? "33" : "49"));
//            var maintainHtml = "<div class='maintain' style='line-height:"+height+"px;height:" + height + "px;" + (isMaintain ? "display:block;" : "") + "'>维护</div>";

//            tr.cells[9 + Config.oddsColumnIndexAdd].innerHTML = tmp + maintainHtml;

//            tmp = "";
//            if (Config.haveLetGoal == 1)
//                tmp = "<div class='odds" + (D[13] == "2" ? 4 : 1) + (letGoalResult == 2 ? " winColor" : "") + "'" + displayHtml + ">" + (D[14] == "0" ? D[4] : "&nbsp;") + "</div>";
//            if (Config.haveTotal == 1)
//                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 2) + (totalResult == 2 ? " winColor" : "") + "'" + displayHtml + ">" + (D[16] == "0" ? D[12] : "&nbsp;") + "</div>";
//            if (Config.haveEurope == 1)
//                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 3) + (europeResult == 2 ? " winColor" : "") + "'"  + displayHtml + ">" + (D[15] == "0" ? D[8] : "&nbsp;") + "</div>";
//            tr.cells[10 + Config.oddsColumnIndexAdd].innerHTML = tmp;
//            tmp = "";
//            if (D[13] == "1" || D[13] == "2") {
//                if (D[13] == "1") tmp = "<img src='image/zd.gif' height=10 width=10 title='有走地'>";
//                if (D[13] == "2") tmp = "<img src='image/zd2.gif' height=10 width=10 title='正在走地'>";
//                if (typeof (matchindex) != 'undefined' && A.length > matchindex && parseInt(A[matchindex][13]) >= -1 && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zds.png") == -1) {
//                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = "<img title='有走地' src='image/zds.png'>";
//                    tr.cells[11 + Config.oddsColumnIndexAdd].className = "zd";
//                    tr.cells[11 + Config.oddsColumnIndexAdd].onclick = myAddclick(D[0]);
//                    // tr.cells[11 + Config.oddsColumnIndexAdd].addEventListener("click", myAddclick(D[0]));
//                }
//                //if (A[matchindex][51] == "1")
//                //    tmp += "<br/> <span id='opeFlashBtn_" + D[0] + "'><a style='cursor:pointer;' href=javascript: onclick='openFlash(" + A[matchindex][0] + ")'><img src='images/ant/show_info.png'></a></span>";
//                //else
//                //    tmp += "<br/><span><img style='height:0px;width:10px'></s";
//            }
//            if ((D[13] == "1" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd.gif") == -1) || (D[13] == "2" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd2.gif") == -1) || tmp == "") {
//                //if (window.location.href.toLowerCase().indexOf("index2in1") != -1)
//                // tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML = tmp;
//                //else
//                tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(0).innerHTML = tmp;
//                if (isCompanyPage && tmp == "") {
//                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = tmp;
//                    //tr.cells[11 + Config.oddsColumnIndexAdd].onclick = null;
//                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('onclick');
//                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('class');
//                }
//            }
//            tr.attributes["odds"].value = odds;
//        }
//        if (needSound) ShowOddsSound();
//    } catch (e) { }
//}
function showodds() {
    try {
        var oldTO;
        var j = 0;
        var root = oddsHttp.responseXML.documentElement.childNodes[0];
        for (var i = 0; i < oddsHttp.responseXML.documentElement.childNodes.length; i++) {
            if (oddsHttp.responseXML.documentElement.childNodes[i].nodeName == "isMaintain") {
                if (document.all && parseInt(ieNum) < 10)
                    isMaintain = oddsHttp.responseXML.documentElement.childNodes[i].text == "1"; //id,oddsid,goal,home,away,zoudi,isStopLive
                else
                    isMaintain = oddsHttp.responseXML.documentElement.childNodes[i].textContent == "1";
                break;
            }
        }
        var D = new Array();
        var odds, old = new Array();
        var needSound = false;
        for (var i = 0; i < root.childNodes.length; i++) {
            if (document.all && parseInt(ieNum) < 10)
                odds = root.childNodes[i].text; //id,oddsid,goal,home,away,zoudi,isStopLive
            else
                odds = root.childNodes[i].textContent;
            D = odds.split(",");
            tr = document.getElementById("tr1_" + D[0]);
            if (tr == null) continue;
            var matchindex = getDataIndex(D[0]);
            var letGoalResult, totalResult, europeResult;
            var oddsResultObj = new Object()
            oddsResultObj = GetFinishWinOddsColor(A[matchindex], D);
            letGoalResult = oddsResultObj.letgoal;
            totalResult = oddsResultObj.total;
            europeResult = oddsResultObj.europe;

            var overGoalType = 0;
            if (typeof (matchindex) != 'undefined' && A.length > matchindex && D.length > 19) {
                if (parseInt(A[matchindex][13]) == 4)
                    overGoalType = 1;
                else if (parseInt(A[matchindex][13]) == 5)
                    overGoalType = 2;
            }
            old = tr.attributes["odds"].value.split(",");
            if (old.length >= 17 && old != odds) {
                if (overGoalType == 0) {
                    for (var j = 3; j < 13; j++) {
                        if (old[j] != "" && D[j] != "") {
                            if (D[j] > old[j]) D[j] = "<span class=\"up\">" + D[j] + "</span>";
                            else if (D[j] < old[j]) D[j] = "<span class=\"down\">" + D[j] + "</span>";
                        }
                        if (j == 4) j++;
                        if (j == 8) j = j + 2;
                    }
                } else {//加时
                    var indexList = overGoalType == 1 ? [20, 22, 25, 27, 30, 31, 32] : [35, 37, 40, 42, 45, 46, 47];
                    for (var k = 0; j < indexList.length; k++) {
                        var j = indexList[k];
                        if (old[j] != "" && D[j] != "") {
                            if (D[j] > old[j]) D[j] = "<span class=\"up\">" + D[j] + "</span>";
                            else if (D[j] < old[j]) D[j] = "<span class=\"down\">" + D[j] + "</span>";
                        }
                    }
                }
                window.setTimeout("restoreOddsColor(" + D[0] + ")", 30000);
                if (Config.oddsSound == 1) {
                    if (tr.style.display != "none")
                        needSound = true;
                }
            }
            var letgoalIndex = 2;
            var totalIndex = 10;
            var homeOddsIndex = 3, guestOddsIndex = 4, bigOddsIndex = 11, smallOddsIndex = 12, winOddsIndex = 6, drawOddsIndex = 7, loseOddsIndex = 8, letgoalFengIndex = 14, totalFengIndex = 16, ouFengIndex = 15;
            if (overGoalType == 1) {
                letgoalIndex = 21;
                totalIndex = 26;
                homeOddsIndex = 20;
                guestOddsIndex = 22;
                bigOddsIndex = 25;
                smallOddsIndex = 27;
                winOddsIndex = 30;
                drawOddsIndex = 31;
                loseOddsIndex = 32;
                letgoalFengIndex = 23;
                totalFengIndex = 28;
                ouFengIndex = 33;
            } else if (overGoalType == 2) {
                letgoalIndex = 36;
                totalIndex = 41;
                homeOddsIndex = 35;
                guestOddsIndex = 37;
                bigOddsIndex = 40;
                smallOddsIndex = 42;
                winOddsIndex = 45;
                drawOddsIndex = 46;
                loseOddsIndex = 47;
                letgoalFengIndex = 38;
                totalFengIndex = 43;
                ouFengIndex = 48;
            }
            if (old.length >= 17 && old != odds && old[2] != "") {
                if (D[letgoalIndex] > old[letgoalIndex]) D[letgoalIndex] = "<span class=\"up\">" + Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>") + "</span>";
                else if (D[letgoalIndex] < old[letgoalIndex]) D[letgoalIndex] = "<span class=\"down\">" + Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>") + "</span>";
                else D[2] = Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>");
            }
            else D[letgoalIndex] = Goal2GoalCn(D[letgoalIndex]).replace("受", "<font color='red'>*</font>");
            if (old.length >= 17 && old != odds && old[10] != "") {
                if (D[totalIndex] > old[totalIndex]) D[totalIndex] = "<span class=\"up\">" + Goal2GoalCn2(D[totalIndex]) + "</span>";
                else if (D[totalIndex] < old[totalIndex]) D[totalIndex] = "<span class=\"down\">" + Goal2GoalCn2(D[totalIndex]) + "</span>";
                else D[totalIndex] = Goal2GoalCn2(D[totalIndex]);
            }
            else D[totalIndex] = Goal2GoalCn2(D[totalIndex]);
            var displayHtml = isMaintain ? " style='display:none;'" : "";
            var letgoalClick = " onclick='AsianOdds(" + D[0] + ")'";
            var totalClick = " onclick='TotalOdds(" + D[0] + ")'";
            var europeClick = " onclick='EuropeOdds(" + D[0] + ")'"; 
            var tmp = "";
            if (Config.haveLetGoal == 1)
                tmp = "<div class='odds" + (D[13] == "2" ? 4 : 1) + (letGoalResult == 0 ? " winColor" : "") + "'" + displayHtml + letgoalClick + " > " + (D[letgoalFengIndex] == "0" ? D[homeOddsIndex] : "&nbsp;") + "</div > ";
            if (Config.haveTotal == 1)
                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 2) + (totalResult == 0 ? " winColor" : "") + "'" + displayHtml + totalClick + ">" + (D[totalFengIndex] == "0" ? D[bigOddsIndex] : "&nbsp;") + "</div>";
            if (Config.haveEurope == 1)
                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 3) + (europeResult == 0 ? " winColor" : "") + "'" + displayHtml + europeClick + ">" + (D[ouFengIndex] == "0" ? D[winOddsIndex] : "&nbsp;") + "</div>";
            tr.cells[8 + Config.oddsColumnIndexAdd].innerHTML = tmp;
            tmp = "";
            var oddsCount = 0;

            if (Config.haveLetGoal == 1) {
                tmp = "<div class='odds" + (D[13] == "2" ? 4 : 1) + "'" + displayHtml + letgoalClick + ">" + (D[letgoalFengIndex] == "0" ? D[letgoalIndex] : "封") + "</div>";
                oddsCount++;
            }
            if (Config.haveTotal == 1) {
                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 2) + "'" + displayHtml + totalClick + ">" + (D[totalFengIndex] == "0" ? D[totalIndex] : "封") + "</div>";
                oddsCount++;
            }
            if (Config.haveEurope == 1) {
                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 3) + (europeResult == 1 ? " winColor" : "") + "'" + displayHtml + europeClick + ">" + (D[ouFengIndex] == "0" ? D[drawOddsIndex] : "封") + "</div>";
                oddsCount++;
            }
            var height = (oddsCount == 1 ? "31" : (oddsCount == 2 ? "33" : "49"));
            var maintainHtml = "<div class='maintain' style='line-height:" + height + "px;height:" + height + "px;" + (isMaintain ? "display:block;" : "") + "'>维护</div>";

            tr.cells[9 + Config.oddsColumnIndexAdd].innerHTML = tmp + maintainHtml;

            tmp = "";
            if (Config.haveLetGoal == 1)
                tmp = "<div class='odds" + (D[13] == "2" ? 4 : 1) + (letGoalResult == 2 ? " winColor" : "") + "'" + displayHtml + letgoalClick + ">" + (D[letgoalFengIndex] == "0" ? D[guestOddsIndex] : "&nbsp;") + "</div>";
            if (Config.haveTotal == 1)
                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 2) + (totalResult == 2 ? " winColor" : "") + "'" + displayHtml + totalClick + ">" + (D[totalFengIndex] == "0" ? D[smallOddsIndex] : "&nbsp;") + "</div>";
            if (Config.haveEurope == 1)
                tmp += "<div class='odds" + (D[13] == "2" ? 4 : 3) + (europeResult == 2 ? " winColor" : "") + "'" + displayHtml + europeClick + ">" + (D[ouFengIndex] == "0" ? D[loseOddsIndex] : "&nbsp;") + "</div>";
            tr.cells[10 + Config.oddsColumnIndexAdd].innerHTML = tmp;
            tmp = "";
            if (D[13] == "1" || D[13] == "2") {
                if (D[13] == "1") tmp = "<img src='image/zd.gif' height=10 width=10 title='有走地'>";
                if (D[13] == "2") tmp = "<img src='image/zd2.gif' height=10 width=10 title='正在走地'>";
                if (typeof (matchindex) != 'undefined' && A.length > matchindex && parseInt(A[matchindex][13]) >= -1 && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zds.png") == -1) {
                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = "<img title='有走地' src='image/zds.png'>";
                    tr.cells[11 + Config.oddsColumnIndexAdd].className = "zd";
                    tr.cells[11 + Config.oddsColumnIndexAdd].onclick = myAddclick(D[0]);
                }
            }
            if ((D[13] == "1" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd.gif") == -1) || (D[13] == "2" && tr.cells[11 + Config.oddsColumnIndexAdd].innerHTML.toLowerCase().indexOf("zd2.gif") == -1) || tmp == "") {
                tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(0).innerHTML = tmp;
                if (isCompanyPage && tmp == "") {
                    tr.cells[11 + Config.oddsColumnIndexAdd].getElementsByTagName('span').item(1).innerHTML = tmp;
                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('onclick');
                    $(tr.cells[11 + Config.oddsColumnIndexAdd]).removeAttr('class');
                }
            }
            tr.attributes["odds"].value = odds;
        }
        if (needSound) ShowOddsSound();
    } catch (e) { }
}
function myAddclick(id) {
    return function () {
        showgoallist(id);
    }
}
function restoreOddsColor(matchid) {
    var tr = document.getElementById("tr1_" + matchid);
    if (tr == null) return;
    tr.cells[8 + Config.oddsColumnIndexAdd].innerHTML = tr.cells[8 + Config.oddsColumnIndexAdd].innerHTML.replace(/<span class=\"up\">/gi, "").replace(/<span class=\"down\">/gi, "").replace(/<\/span>/gi, "");
    tr.cells[9 + Config.oddsColumnIndexAdd].innerHTML = tr.cells[9 + Config.oddsColumnIndexAdd].innerHTML.replace(/<span class=\"up\">/gi, "").replace(/<span class=\"down\">/gi, "").replace(/<\/span>/gi, "");
    tr.cells[10 + Config.oddsColumnIndexAdd].innerHTML = tr.cells[10 + Config.oddsColumnIndexAdd].innerHTML.replace(/<span class=\"up\">/gi, "").replace(/<span class=\"down\">/gi, "").replace(/<\/span>/gi, "");
}
if (!Array.prototype.forEach) {
    Array.prototype.forEach = function forEach(callback, thisArg) {
        var T, k;
        if (this == null) {
            throw new TypeError("this is null or not defined");
        }
        var O = Object(this);
        var len = O.length >>> 0;
        if (typeof callback !== "function") {
            throw new TypeError(callback + " is not a function");
        }
        if (arguments.length > 1) {
            T = thisArg;
        }
        k = 0;
        while (k < len) {
            var kValue;
            if (k in O) {
                kValue = O[k];
                callback.call(T, kValue, k, O);
            }
            k++;
        }
    };
}
//--------------------------------------------现场分析动态图------------------------------------------
//定义namespace
var _glflash = new Object();
//公共变量
_glflash.Domain = "$$";
_glflash.DataType = "!";
_glflash.SplitRecord = "^";
_glflash.SplitColumn = ",";
_glflash.SplitBfOddsRecord = "#";
_glflash.SplitBfOddsType = ";";


//通用列表类
_glflash.List = function () {
    this.items = new Array();
    this.keys = new Object();

    this.Add = function (key, value) {
        if (typeof (key) != "undefined") {
            var vv = typeof (value) == "undefined" ? null : value;
            var idx = this.keys[key];
            if (idx == null) {
                idx = this.items.length;
                this.keys[key] = idx;
            }
            this.items[idx] = vv;
        }
    }
    this.Get = function (key) {
        var idx = this.keys[key];
        if (idx != null)
            return this.items[idx];
        return null;
    }
    this.GetNum = function (key) {
        var i = 0;
        for (var k in this.keys) {
            if (key == k)
                return i;
            i++;
        }
        return null;
    }
    this.Clear = function () {
        for (var k in this.keys) {
            delete this.keys[k];
        }
        delete this.keys;
        this.keys = null;
        this.keys = new Object();

        for (var i = 0; i < this.items.length; i++) {
            delete this.items(i);
        }
        delete this.items;
        this.items = null;
        this.items = new Array();
    }
}
_glflash.schedule = function (infoStr) {
    var arr = infoStr.split(_glflash.SplitRecord);
    this.sId = arr[0];
    this.weather = arr[1];
    this.temperature = arr[2];
    this.filed = arr[3].split(_glflash.SplitColumn);
    this.homeTeamID = arr[4];
    this.guestTeamID = arr[5];
    this.homeScore = arr[6];
    this.guestScore = arr[7];
    this.state = arr[8];
    this.jsqScheduleCount = arr[9];
    this.time = arr[10];
    this.detailTime = arr[11];
    this.homeTechList = new _glflash.techCount(arr[12], this.state);
    this.guestTechList = new _glflash.techCount(arr[13], this.state);
}
_glflash.techCount = function (infoStr, state) {
    infoStr = typeof (infoStr) == 'undefined' ? '' : infoStr;
    var arr = infoStr.split(_glflash.SplitColumn);
    this.attack = "-";
    this.shorts = "-";
    this.controlPre = "-";
    if ((state > 0 || state == -1) && arr.length == 3) {
        this.attack = (arr[0] != "" ? arr[0] : "&nbsp;");
        this.shorts = (arr[1] != "" ? arr[1] : "&nbsp;");
        this.controlPre = (arr[2] != "" && parseInt(arr[2]) > 0 ? arr[2] + "%" : "&nbsp;");
    }
}
//得失球类
_glflash.countDetail = function (infoStr) {
    var arr = infoStr.split(_glflash.SplitColumn);
    this.hjq = arr[0];
    this.hsq = arr[1];
    this.gjq = arr[2];
    this.gsq = arr[3];
}
_glflash.GoalsCount = function (sId, infoStr) {
    this.sId = sId;
    var countArr = infoStr.split(_glflash.SplitRecord);
    this.countList = new _glflash.List();
    var countItem;
    for (var i = 0; i < countArr.length; i++) {
        countItem = new _glflash.countDetail(countArr[i]);
        this.countList.Add(i, countItem);
    }
    // this.count1 = counta[0].split(_glflash.SplitColumn);
}
_glflash.GraphData = function (sId, infoStr) {
    this.sId = sId;
    var infoArr = infoStr.split(_glflash.SplitColumn);
    this.Id = infoArr[0];
    this.teamId = infoArr[1];
    this.eventType = infoArr[2];
    this.location = infoArr[3];
    this.state = infoArr[4];
    this.time = infoArr[5];
    this.injuryTime = infoArr[6];
}
_glflash.barDetail = function (infoStr) {
    var arr = infoStr.split(_glflash.SplitColumn);
    this.Id = arr[0];
    this.dataType = arr[1];
    this.teamID = arr[2];
    this.eventType = arr[3];
    this.time = arr[4];
}
_glflash.statusBar = function (sId, infoStr) {
    infoStr = infoStr.replace("\n", "");
    this.sId = sId;
    var arr = infoStr.split(_glflash.SplitRecord);
    this.barList1 = new _glflash.List();
    this.barList2 = new _glflash.List();
    this.barList3 = new _glflash.List();
    var barItem;
    for (var i = 0; i < arr.length; i++) {
        barItem = new _glflash.barDetail(arr[i]);
        var detailArr = arr[i].split(_glflash.SplitColumn)
        if (detailArr.length > 2) {
            if (detailArr[1] == "1")//危险进攻（20）、射门（28，20）
                this.barList1.Add(detailArr[0], barItem);
            else if (detailArr[1] == "2")//角球
                this.barList2.Add(detailArr[0], barItem);
            else if (detailArr[1] == "3")//进球
                this.barList3.Add(detailArr[0], barItem);
        }
    }
}
_glflash.initBfOdds = function (infoStr) {
    var bfOddsList = new _glflash.List();
    var arr = infoStr.split(_glflash.SplitRecord);
    for (var i = 0; i < arr.length; i++) {
        var arrOdds = arr[i].split(_glflash.SplitBfOddsRecord);
        bfOddsList.Add(parseInt(arrOdds[0]), new _glflash.oneBfOdds(arr[i]));
    }
    return bfOddsList;
}
_glflash.oneBfOdds = function (infoStr) {
    var arr = infoStr.split(_glflash.SplitBfOddsRecord);
    this.sId = arr[0];
    this.oddsList = new _glflash.List();
    var arrOdds = arr[1].split(_glflash.SplitBfOddsType);
    for (var i = 0; i < arrOdds.length; i++) {
        var oneOdds = arrOdds[i].split(_glflash.SplitColumn);
        var key = (oneOdds[0] == "早餐" ? 1 : oneOdds[0] == "未开场" ? 2 : 3) + "_" + oneOdds[1] + "_" + oneOdds[2] + "_" + oneOdds[17];
        this.oddsList.Add(key, new _glflash.bfOdds(key, arrOdds[i]));
    }
}
_glflash.bfOdds = function (id, infoStr) {
    this.ID = id;
    var arr = infoStr.split(_glflash.SplitColumn);
    this.stateInfo = (arr[0] == "早餐" ? '<span class="green">早</span>' : arr[0] == "未开场" ? '<span class="red">未</span>' : arr[0] == "中场" ? '<span class="blue">中</span>' : '<span class="red">' + arr[0] + '</span>');
    this.homeScore = parseInt(arr[1]);
    this.guestScore = parseInt(arr[2]);
    this.showScore = (arr[0] == "早餐" || arr[0] == "未开场" ? "&nbsp;" : this.homeScore + ":" + this.guestScore);
    this.oddsID_h = arr[3];
    this.homeOdds_f = arr[4];
    this.letgoal_f = Goal2GoalCn(arr[5]).replace("受", "<font color='red'>*</font>");
    this.guestOdds_f = arr[6];
    this.homeOdds = arr[7];
    this.letgoal = Goal2GoalCn(arr[8]).replace("受", "<font color='red'>*</font>");
    this.guestOdds = arr[9];

    this.oddsID_t = arr[10];
    this.upOdds_f = arr[11];
    this.totalScore_f = Goal2GoalCn2(arr[12]);
    this.downOdds_f = arr[13];
    this.upOdds = arr[14];
    this.totalScore = Goal2GoalCn2(arr[15]);
    this.downOdds = arr[16];
}
_glflash.clearTimer = function () {
    window.clearTimeout(flashTimer);
    window.clearTimeout(bfOddsTimer);
}
_glflash.getInt = function (number) {
    return typeof (number) != "undefined" && number != "" ? parseInt(number) : -1;//默认值为-1，方便开场或单节开始时更新为0的比分
}
_glflash.getFloat = function (number) {
    return typeof (number) != "undefined" && number != "" ? parseFloat(number) : 0;
}
var flashData = new Object();
flashData.scheduleList = new _glflash.List();
flashData.jsqList_30 = new _glflash.List();
flashData.jsqList_50 = new _glflash.List();
flashData.graphList = new _glflash.List();
flashData.statusList = new _glflash.List();
flashData.bfOddsList = new _glflash.List();
flashData.changeBfOddsList = new _glflash.List();

var flashScheduleIDs = "";
function openFlash(id) {
    autoAnalyID = 0;//将自动展开的动态分析取消
    if (flashScheduleIDs != "")
        closeFlash(flashScheduleIDs);
    flashScheduleIDs = id;
    var tr1 = document.getElementById("tr1_" + flashScheduleIDs);
    //var flashSpan = tr1.cells[8].getElementsByTagName('span').item(0);
    tr1.cells[8].innerHTML = tr1.cells[8].innerHTML.replace("openFlash", "closeFlash").replace("show_info.png", "hide_info.png").replace((Config.language == 1 ? "現場分析" : "现场分析"), "收起");
    var matchindex = getDataIndex(flashScheduleIDs);
    //var matchindex = tr1.attributes["index"].value;
    var tr = document.getElementById("tr3_" + flashScheduleIDs);
    tr.style.display = "";
    loadFlashData();
    loadBfOdds();
    document.getElementById("flashLive_" + flashScheduleIDs).innerHTML = showFlashLive(flashScheduleIDs);
    if (Config.IsIE) {
        runEvent(flashScheduleIDs, null, 0);
        if (parseInt(A[matchindex][13]) >= 0)
            getflashChange();
    }
    if (!isCompanyPage || (isCompanyPage && companyID == 3))
        getBfOddsChange();
}
function closeFlash(id) {
    _glflash.clearTimer();
    flashLine.Clear();
    var obj = document.getElementById("tr3_" + id);
    if (obj != null)
        obj.style.display = "none";
    document.getElementById("flashLive_" + id).innerHTML = "";
    var tr1 = document.getElementById("tr1_" + id);
    if (tr1 != null) {
        //var flashSpan = tr1.cells[8].getElementsByTagName('span').item(0);
        tr1.cells[8].innerHTML = tr1.cells[8].innerHTML.replace("closeFlash", "openFlash").replace("hide_info.png", "show_info.png").replace("收起", (Config.language == 1 ? "現場分析" : "现场分析"));
    }
    flashData = new Object();
    flashData.scheduleList = new _glflash.List();
    flashData.jsqList_30 = new _glflash.List();
    flashData.jsqList_50 = new _glflash.List();
    flashData.graphList = new _glflash.List();
    flashData.statusList = new _glflash.List();
    oldCornerTime_H = 0, oldCornerTime_G = 0;
    flashScheduleIDs = "";
}
function loadFlashData() {
    var oXmlFlashHttp = zXmlHttp.createRequest();
    oXmlFlashHttp.open("get", "/flashdata/get?id=" + flashScheduleIDs + "&t=" + Date.parse(new Date()), false);
    //oXmlFlashHttp.open("get", "1251503.txt?" + Date.parse(new Date()), false);
    oXmlFlashHttp.send(null);
    var data = oXmlFlashHttp.responseText;
    var doMains = data.split(_glflash.Domain);
    for (var i = 0; i < doMains.length; i++) {
        var oneSchedule = doMains[i].split(_glflash.DataType);
        var arrSchedule = oneSchedule[0].split(_glflash.SplitRecord);
        var scheduleDetail = new _glflash.schedule(oneSchedule[0]);
        var oneJsq30 = new _glflash.GoalsCount(arrSchedule[0], oneSchedule[1]);
        var oneJsq50 = new _glflash.GoalsCount(arrSchedule[0], oneSchedule[2]);
        var oneflash = new _glflash.GraphData(arrSchedule[0], oneSchedule[3]);
        var oneStatus = new _glflash.statusBar(arrSchedule[0], oneSchedule[4]);
        flashData.scheduleList.Add(arrSchedule[0], scheduleDetail);
        flashData.jsqList_30.Add(arrSchedule[0], oneJsq30);
        flashData.jsqList_50.Add(arrSchedule[0], oneJsq50);
        flashData.graphList.Add(arrSchedule[0], oneflash);
        flashData.statusList.Add(arrSchedule[0], oneStatus);
    }
}
function reloadFlashTech() {
    var oXmlFlashHttp = zXmlHttp.createRequest();
    oXmlFlashHttp.open("get", "/flashdata/get?id=" + flashScheduleIDs + "&t=" + Date.parse(new Date()), false);
    oXmlFlashHttp.send(null);
    var data = oXmlFlashHttp.responseText;
    var oneSchedule = data.split(_glflash.DataType);
    var arrSchedule = oneSchedule[0].split(_glflash.SplitRecord);
    var scheduleDetail = new _glflash.schedule(oneSchedule[0]);
    var oldSchedulDetail = flashData.scheduleList.Get(scheduleDetail.sId);
    updateObjData(oldSchedulDetail, scheduleDetail);
}
function showFlashLive(sId) {
    var html = new Array();
    html.push('<div class="ant' + (Config.IsIE ? "" : " v2") + '">');
    html.push('<div class="odds" id="bfOddsDiv">');
    html.push(makeBfOdds(sId));
    html.push('</div>');
    html.push('<div class="flash">');
    if (Config.IsIE) {
        html.push('<div class="miniDomain">titan007.com</div>');
        html.push('<div class="liveBox">');
        html.push(makeFlashEvent(sId));
        html.push('</div>');
        html.push(makeStatus(sId));
    }
    else {
        var homeTeam = getTeamHtmlName(sId, 0);
        var guestTeam = getTeamHtmlName(sId, 1);
        html.push('<iframe src="/flashlive/flash.html?id=' + sId + '&h=' + homeTeam + '&g=' + guestTeam + '&t=' + difftime + '" height="357" frameborder="0"></iframe>');
    }
    html.push('</div>');
    html.push('<div class="guessBox">');
    html.push(makeJsq(sId, 1));
    html.push(makeJsq(sId, 2));
    html.push('</div>');
    html.push('</div>');
    return html.join("");
}
function makeJsq(sId, t) {
    var scheduleDetail = flashData.scheduleList.Get(sId);
    var jsqList = t == 1 ? flashData.jsqList_30.Get(sId) : flashData.jsqList_50.Get(sId);
    if (jsqList.countList.length == 0) return;
    if (t == 2 && scheduleDetail.jsqScheduleCount <= 30) return;
    var coumnList = "1-15,16-30,31-45,46-60,61-75,76-90".split(',');
    var html = new Array();
    html.push('<table width="100%" border="0" cellspacing="1" cellpadding="0" id="JSQ_' + sId + (t == 1 ? '_30"' : '_50" style="display:none;"') + '>');
    html.push('<tr>');
    if (scheduleDetail.jsqScheduleCount > 30)
        html.push('<th colspan="5" align="left"><div class="btns"><span onclick="changeJsq(' + sId + ',1)"' + (t == 1 ? ' class="on"' : '') + '>近30' + (Config.language == 1 ? '場' : '场') + '</span><span onclick="changeJsq(' + sId + ',2)"' + (t == 2 ? ' class="on"' : '') + '>近50' + (Config.language == 1 ? '場' : '场') + '</span></div>');
    else
        html.push('<th colspan="5" align="left"><div class="btns"><span class="on">近30' + (Config.language == 1 ? '場' : '场') + '</span></div>');
    html.push((Config.language == 1 ? '主客進失球概率' : '主客进失球概率') + ' </th>');
    html.push('</tr>');
    html.push('<tr>');
    html.push('<td align="center">' + (Config.language == 1 ? '進' : '进') + '球</td>');
    html.push('<td align="center">失球</td>');
    html.push('<td align="center" class="y">' + (Config.language == 1 ? '時' : '时') + '段</td>');
    html.push('<td align="center">' + (Config.language == 1 ? '進' : '进') + '球</td>');
    html.push('<td align="center">失球</td>');
    html.push('</tr>');
    for (var i = 0; i < jsqList.countList.items.length; i++) {
        var arrhjq = jsqList.countList.items[i].hjq.split(';');
        var arrhsq = jsqList.countList.items[i].hsq.split(';');
        var arrgjq = jsqList.countList.items[i].gjq.split(';');
        var arrgsq = jsqList.countList.items[i].gsq.split(';');
        //<span class="red">20%</span>
        html.push('<tr>');
        html.push('<td align="center">' + (arrhjq.length > 1 ? "<span class=\"red\">" + arrhjq[0] + "</span>" : arrhjq[0]) + '</td>');
        html.push('<td align="center">' + (arrhsq.length > 1 ? "<span class=\"red\">" + arrhsq[0] + "</span>" : arrhsq[0]) + '</td>');
        html.push('<td align="center" class="y">' + coumnList[i] + '</td>');
        html.push('<td align="center">' + (arrgjq.length > 1 ? "<span class=\"red\">" + arrgjq[0] + "</span>" : arrgjq[0]) + '</td>');
        html.push('<td align="center">' + (arrgsq.length > 1 ? "<span class=\"red\">" + arrgsq[0] + "</span>" : arrgsq[0]) + '</td>');
        html.push('</tr>');
    }
    html.push('</table>');
    return html.join("");
}
function changeJsq(sId, t) {
    document.getElementById("JSQ_" + sId + (t == 1 ? "_50" : "_30")).style.display = "none";
    document.getElementById("JSQ_" + sId + (t == 1 ? "_30" : "_50")).style.display = "";
}
function makeFlashEvent(sId) {
    var scheduleDetail = flashData.scheduleList.Get(sId);
    var homeTeam = getTeamHtmlName(sId, 0);
    var guestTeam = getTeamHtmlName(sId, 1);
    var html = new Array();
    html.push('<div class="homeEventBox" id="homeEventBox_' + sId + '">');
    html.push('<div class="team"><div class="teamName">' + homeTeam);
    html.push('</div><div class="ball">控球</div>');
    html.push('</div>');
    html.push('<div class="ctrlBG" id="homeCtrlBG_' + sId + '"></div>');
    html.push('<div class="attackBG" id="homeAttackBG_' + sId + '"></div>');
    html.push('<div class="DAttackBG" id="homeDAttackBG_' + sId + '"></div>');
    html.push('</div>');

    html.push('<div class="guestEventBox" id="guestEventBox_' + sId + '">');
    html.push('<div class="team"><div class="teamName">' + guestTeam);
    html.push('</div><div class="ball">控球</div>');
    html.push('</div>');
    html.push('<div class="ctrlBG" id="guestCtrlBG_' + sId + '"></div>');
    html.push('<div class="attackBG" id="guestAttackBG_' + sId + '"></div>');
    html.push('<div class="DAttackBG" id="guestDAttackBG_' + sId + '"></div>');
    html.push('</div>');

    html.push('<div class="foul" id="foul_' + sId + '">');
    html.push('<span class="redCard"></span>');
    html.push('</div>');

    html.push('<div class="pointBall_0" id="pointBall_' + sId + '">');
    html.push('<div class="team">');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">' + (Config.language == 1 ? "點球" : "点球") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div class="ballIn" id="ballIn_' + sId + '"></div>');

    html.push('<div class="autoBall_0" id="autoBall_' + sId + '">');
    html.push('<div class="team">');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">任意球</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div class="DAutoBall_0" id="DAutoBall_' + sId + '">');
    html.push('<div class="team">');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">' + (Config.language == 1 ? "危險任意球" : "危险任意球") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div class="DBall_0" id="DBall_' + sId + '">');
    html.push('<div class="team">');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">' + (Config.language == 1 ? "球門球" : "球门球") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div class="offside_1" id="offside_' + sId + '">');
    html.push('<div class="team">');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">越位</div>');
    html.push('</div>');
    html.push('<i></i>');
    html.push('</div>');

    html.push('<div class="cornerBall_0" id="cornerBall_' + sId + '">');
    html.push('<div class="team">');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">角球</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div class="lineBall_0" id="lineBall_' + sId + '">');
    html.push('<div class="team">');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">界外球</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div class="star" id="star_' + sId + '">');
    html.push('<div class="team"> ');
    html.push('<div class="teamName"></div>');
    html.push('<div class="ball">' + (Config.language == 1 ? "先開球" : "先开球") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div id="msg_' + sId + '" class="msg"></div>');
    html.push('<div id="shotIn_' + sId + '" class="shotIn">');
    html.push('<div class="team"><span class="teamName"></span>');
    html.push('<div class="ball">' + (Config.language == 1 ? "射正球門" : "射正球门") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div id="stopIt_' + sId + '" class="stopIt">');
    html.push('<div class="team"><span class="teamName"></span>');
    html.push('<div class="ball">' + (Config.language == 1 ? "射門被阻擋" : "射门被阻挡") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div id="shotOut_' + sId + '" class="shotOut">');
    html.push('<div class="team"><span class="teamName"></span>');
    html.push('<div class="ball">' + (Config.language == 1 ? "射偏球門" : "射偏球门") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div id="shotLost_' + sId + '" class="shotLost">');
    html.push('<div class="team"><span class="teamName"></span>');
    html.push('<div class="ball">' + (Config.language == 1 ? "射中門框" : "射中门框") + '</div>');
    html.push('</div>');
    html.push('</div>');

    html.push('<div class="default dataPlane" id="default_' + sId + '">');
    html.push('<div class="matchBox">');
    html.push('<div class="homeTeam">' + homeTeam + '</div>');
    html.push('<div class="score"></div>');
    html.push('<div class="vs"></div>');
    html.push('<div class="score"></div>');
    html.push('<div class="guestTeam">' + guestTeam + '</div>');
    html.push('</div>');
    html.push('<ul class="dataBox">');
    html.push('<li><div class="home">-</div><div class="tit">' + (Config.language == 1 ? "進攻" : "进攻") + '</div><div class="guest">-</div></li>');
    html.push('<li><div class="home">-</div><div class="tit">' + (Config.language == 1 ? "射門" : "射门") + '</div><div class="guest">-</div></li>');
    html.push('<li><div class="home">-</div><div class="tit">控球率</div><div class="guest">-</div></li>');
    html.push('</ul > ');
    html.push('<div class="tianqi">');
    if (scheduleDetail.temperature != '' || scheduleDetail.filed[0].length > 3 || scheduleDetail.weather != "") {
        html.push('<div class="data2">');
        if (scheduleDetail.filed[0].length > 3)
            html.push((Config.language == 1 ? "場地" : "场地") + ' : ' + (Config.language == 1 ? scheduleDetail.filed[1] : scheduleDetail.filed[0]));
        if (scheduleDetail.weather != "")
            html.push(' 天' + (Config.language == 1 ? "氣" : "气") + ' : ' + scheduleDetail.weather + ' ');
        if (scheduleDetail.temperature != "")
            html.push((Config.language == 1 ? " 溫" : " 温") + '度 : ' + scheduleDetail.temperature);
        html.push('</div>');
    }
    html.push('</div>');
    html.push(' </div>');

    html.push('<div class="dataPlane" id="dataPlane_' + sId + '">');
    html.push('<div class="matchBox">');
    html.push('<div class="homeTeam">' + homeTeam + '</div>');
    html.push('<div class="score" id="flashHomeScore_' + sId + '">' + scheduleDetail.homeScore + '</div>');
    html.push('<div class="vs" id="flashState_' + sId + '">中场</div>');
    html.push('<div class="score" id="flashGuestScore_' + sId + '">' + scheduleDetail.guestScore + '</div>');
    html.push('<div class="guestTeam">' + guestTeam + '</div>');
    html.push('</div>');
    html.push('<ul class="dataBox" id="flashTech_' + sId + '">');
    html.push('<li><div class="home">' + scheduleDetail.homeTechList.attack + '</div><div class="tit">' + (Config.language == 1 ? "進攻" : "进攻") + '</div><div class="guest">' + scheduleDetail.guestTechList.attack + '</div></li>');
    html.push('<li><div class="home">' + scheduleDetail.homeTechList.shorts + '</div><div class="tit">' + (Config.language == 1 ? "射門" : "射门") + '</div><div class="guest">' + scheduleDetail.guestTechList.shorts + '</div></li>');
    html.push('<li><div class="home">' + scheduleDetail.homeTechList.controlPre + '</div><div class="tit">控球率</div><div class="guest">' + scheduleDetail.guestTechList.controlPre + '</div></li>');
    html.push('</ul>');
    html.push('<div class="tianqi">');
    if (scheduleDetail.temperature != '' || scheduleDetail.filed[0].length > 3 || scheduleDetail.weather != "") {
        html.push('<div class="data2">');
        if (scheduleDetail.filed[0].length > 3)
            html.push((Config.language == 1 ? "場地" : "场地") + ' : ' + (Config.language == 1 ? scheduleDetail.filed[1] : scheduleDetail.filed[0]));
        if (scheduleDetail.weather != "")
            html.push(' 天' + (Config.language == 1 ? "氣" : "气") + ' : ' + scheduleDetail.weather + ' ');
        if (scheduleDetail.temperature != "")
            html.push((Config.language == 1 ? " 溫" : " 温") + '度 : ' + scheduleDetail.temperature);
        html.push('</div>');
    }
    html.push('</div>');
    html.push('</div>');

    return html.join("");
}
var flashMsg = new Array(39);
flashMsg[2] = "中场,中場,中场".split(',');
flashMsg[3] = "下半场开始,下半場開始,下半场开始".split(',');
flashMsg[4] = "完场,完場,完场".split(',');
flashMsg[5] = "受伤,受傷,受伤".split(',');
flashMsg[6] = "加时上半场,加時上半場,加时上半场".split(',');
flashMsg[7] = "加时半场,加時半場,加时半场".split(',');
flashMsg[8] = "加时下半场,加時下半場,加时下半场".split(',');
flashMsg[9] = "加时完场,加時完場,加时完场".split(',');
flashMsg[10] = "点球决胜,點球決勝,点球决胜".split(',');
flashMsg[30] = "替补,替補,替补".split(',');
flashMsg[36] = "射失点球,射失點球,射失点球".split(',');
flashMsg[37] = "犯规,犯規,犯规".split(',');
flashMsg[38] = "进球无效,進球無效,进球无效".split(',');
function runEvent(sId, oneflash, flashNum) {
    if (oneflash != null)
        flashData.graphList.items[flashNum] = oneflash;
    var list = flashData.graphList.Get(sId);
    var scheduleDetail = flashData.scheduleList.Get(sId);
    var teamType = scheduleDetail.homeTeamID == list.teamId ? 0 : 1;
    if (scheduleDetail.state == 0)
        defaultInfo(sId);
    else {
        switch (parseInt(list.eventType)) {
            case 1:
                star(sId, teamType);
                break;
            //case 2:
            case 3:
            //case 4:
            case 5:
            case 6:
            case 7:
            case 8:
            case 9:
            case 10:
            case 30:
            case 37:
            case 38:
                showMsg(sId, flashMsg[list.eventType][Config.language]);
                break;
            case 2:
            case 4:
                reloadFlashTech();//先加载数据文件更新技统列表数据
                dataPlane(sId, scheduleDetail, flashMsg[list.eventType][Config.language]);
                break;
            case 20:
                dangerousAttack(sId, teamType);
                break;
            case 21:
                attack(sId, teamType);
                break;
            case 22:
                ctrl(sId, teamType);
                break;
            case 23:
                ballIn(sId, teamType, scheduleDetail.homeScore, scheduleDetail.guestScore);
                break;
            case 24:
            case 25:
                var cardType = list.eventType == 25 ? 'red' : 'yellow';
                foul(sId, cardType, teamType);
                break;
            case 26:
                DBall(sId, teamType);
                break;
            case 27:
                pointBall(sId, teamType);
                break;
            case 28:
                shotIn(sId, teamType);
                break;
            case 29:
                shotOut(sId, teamType);
                break;
            case 31:
                offside(sId, teamType);
                break;
            case 32:
                autoBall(sId, teamType);
                break;
            case 33:
                //if (parseInt(scheduleDetail.state) >= 3)
                //    teamType = teamType == 0 ? 1 : 0;
                lineBall(sId, list.location, teamType);
                break;
            case 34:
                var direction;
                if (list.location > 0) {//500
                    //if (parseInt(scheduleDetail.state) >= 3) {
                    //    if (teamType == 0)
                    //        direction = list.location == 1 ? 0 : 3;
                    //    else
                    //        direction = list.location == 1 ? 1 : 2;
                    //}
                    //else {
                    if (teamType == 0)
                        direction = list.location == 1 ? 1 : 2;
                    else
                        direction = list.location == 1 ? 0 : 3;
                    // }
                }
                else {//一比分
                    //if (parseInt(scheduleDetail.state) >= 3)
                    //    direction = teamType == 0 ? 3 : 1;
                    //else
                    direction = teamType == 0 ? 1 : 3;
                }
                cornerBall(sId, direction, teamType);
                break;
            case 35:
                pointBallIn(sId, teamType, scheduleDetail.homeScore, scheduleDetail.guestScore);
                break;
            case 36:
                showPointBallMsg(sId, flashMsg[36][Config.language]);
                break;
            case 39:
                DAutoBall(sId, teamType);
                break;
            case 40:
                stopIt(sId, teamType);
                break;
            case 41:
                shotLost(sId, teamType);
                break;
            case 42:
                var msg = (list.injuryTime > 0 ? (Config.language == 1 ? "補時" : "补时") + list.injuryTime + (Config.language == 1 ? "分鐘" : "分钟") : (Config.language == 1 ? "傷停補時" : "伤停补时"));
                showMsg(sId, msg);
                break;
        }
    }
}
function setStatusTimeLine(minutes, state, sId) {
    if (state == "2") minutes = 45;
    if (state == "-1" || parseInt(state) > 3) minutes = 90;
    if (state == "-1" && minutes > 45) minutes = 45;
    if (minutes > 95) minutes = 95;
    try {
        document.getElementById("timeLine_" + sId).style.left = getStatusPosition(0, minutes) + "px";
    }
    catch (e) { }
}
var oldCornerTime_H = 0, oldCornerTime_G = 0;
function makeStatus(sId) {
    var html = new Array();
    var homeHtml = new Array();
    var guestHtml = new Array();
    var oneStatus = flashData.statusList.Get(sId);
    var scheduleDetail = flashData.scheduleList.Get(sId);
    var state = parseInt(scheduleDetail.state);
    var listGraph = oneStatus.barList1;//20 a; 28,29 s;
    var listCorner = oneStatus.barList2;//f
    var listGoal = oneStatus.barList3;//b
    html.push('<div class="timeLine" id="statusLine_' + sId + '">');//' + (Config.language == 1 ? " big" : "") + '
    html.push('<div class="info">');
    if (state >= -1) {
        var minutes = $("#time_" + sId).text();
        if (state == 2) minutes = 45;
        if (state == -1 || state > 3) minutes = 90;
        if (minutes == '90+') minutes = 90;
        if (state == 1 && minutes != '' && minutes == '45+') minutes = 45;
        if (minutes == "中") minutes = 45;
        html.push('<div class="timeLine" id="timeLine_' + sId + '" style="left:' + getStatusPosition(0, minutes) + 'px"></div>');// 
    }
    for (var i = 0; i < listGraph.items.length; i++) {
        var num = getStatusPosition(listGraph.items[i].eventType, listGraph.items[i].time);
        var onei = '<i class="' + (listGraph.items[i].eventType == "20" ? "a" : "s") + '" style="left:' + num + 'px;cursor:pointer;" title="' + listGraph.items[i].time + '\'' + (Config.language == 1 ? " 危險進攻" : " 危险进攻") + '"></i>';
        if (scheduleDetail.homeTeamID == listGraph.items[i].teamID)
            homeHtml.push(onei);
        else
            guestHtml.push(onei);
    }
    for (var i = 0; i < listCorner.items.length; i++) {
        var num = getStatusPosition(listCorner.items[i].eventType, listCorner.items[i].time);
        if (scheduleDetail.homeTeamID == listCorner.items[i].teamID) {
            if (num - oldCornerTime_H <= 3)
                num += 3 - (num - oldCornerTime_H);
            var onei = '<i class="f" style="left:' + num + 'px;cursor:pointer;" title="' + listCorner.items[i].time + '\' 角球"></i>';
            homeHtml.push(onei);
            oldCornerTime_H = num;
        }
        else {
            if (num - oldCornerTime_G <= 3)
                num += 3 - (num - oldCornerTime_G);
            var onei = '<i class="f" style="left:' + num + 'px;cursor:pointer;" title="' + listCorner.items[i].time + '\' 角球"></i>';
            guestHtml.push(onei);
            oldCornerTime_G = num;
        }
    }
    for (var i = 0; i < listGoal.items.length; i++) {
        var num = getStatusPosition(listGoal.items[i].eventType, listGoal.items[i].time);
        var onei = '<i class="' + getBarBallStyle(listGoal.items[i].eventType) + '" style="left:' + num + 'px;cursor:pointer;" title="' + listGoal.items[i].time + "\'" + getBarBallStyleName(listGoal.items[i].eventType) + '"></i>';
        if (scheduleDetail.homeTeamID == listGoal.items[i].teamID)
            homeHtml.push(onei);
        else
            guestHtml.push(onei);
    }
    html.push('<div class="home" id="homeLine_' + sId + '">');
    html.push(homeHtml.join(""));
    html.push('</div>');
    html.push('<div class="guest" id="guestLine_' + sId + '">');
    html.push(guestHtml.join(""));
    html.push('</div>');
    html.push('</div>');
    html.push('</div>');
    return html.join("");
}
function getStatusPosition(t, time) {
    time = (time.toString().indexOf('完') != -1 ? 90 : time);
    var imgWidth = 0;
    switch (parseInt(t)) {
        case 20:
        case 28:
        case 29:
            imgWidth = 1;
            break;
        case 1:
        case 7:
        case 8:
        case 9:
            imgWidth = 14;
            break;
        case 0:
            imgWidth = 7;
            break;
    }
    return parseInt(time / 100 * 430 - imgWidth / 2);//480
}
var xmlFlash = zXmlHttp.createRequest(), txtChangeBfOdds = zXmlHttp.createRequest();
var oldFlash = "", oldChnageBfOddsData = "";
function getflashChange() {
    try {
        xmlFlash.open("get", "/flashdata/get?chid=" + flashScheduleIDs + "&" + Date.parse(new Date()), true);
        xmlFlash.onreadystatechange = flashRefresh;
        xmlFlash.send(null);
    } catch (e) { }
    flashTimer = window.setTimeout("getflashChange()", 2000);
}
function loadBfOdds() {
    var oXmlBfOddsHttp = zXmlHttp.createRequest();
    oXmlBfOddsHttp.open("get", staticUrl + "/vbsxml/scoreOdds_bf.txt?r=007" + Date.parse(new Date()), false);
    oXmlBfOddsHttp.send(null);
    var data = oXmlBfOddsHttp.responseText;
    if (typeof (data) != 'undefined' && data != "")
        flashData.bfOddsList = _glflash.initBfOdds(data);
}
function getBfOddsChange() {
    try {
        txtChangeBfOdds.open("get", staticUrl + "/vbsxml/ch_scoreOdds_bf.txt?r=007" + Date.parse(new Date()), true);
        txtChangeBfOdds.onreadystatechange = bfOddsRefresh;
        txtChangeBfOdds.send(null);
    } catch (e) { }
    bfOddsTimer = window.setTimeout("getBfOddsChange()", 4000);
}
var __sto = setTimeout;
window.setTimeout2 = function (callback, timeout, param) {
    var args = Array.prototype.slice.call(arguments, 2);
    var _cb = function () {
        callback.apply(null, args);
    }
    __sto(_cb, timeout);
}
function flashRefresh() {
    if (xmlFlash.readyState != 4 || (xmlFlash.status != 200 && xmlFlash.status != 0)) return;
    if (oldXML == xmlFlash.responseText) return
    oldXML = xmlFlash.responseText;
    var arr;
    var changeIDList = ",";
    var playFlash = false;
    if (xmlFlash.responseText == null || xmlFlash.responseText.replace("\n", "") == "") return;
    var data = xmlFlash.responseText.replace("\n", "");
    var doMains = data.split(_glflash.Domain);
    for (var i = 0; i < doMains.length; i++) {
        var oneSchedule = doMains[i].split(_glflash.DataType);
        var arrSchedule = oneSchedule[0].split(_glflash.SplitRecord);
        var scheduleDetail = flashData.scheduleList.Get(arrSchedule[0]);
        scheduleDetail.homeScore = parseInt(arrSchedule[1]);
        scheduleDetail.guestScore = parseInt(arrSchedule[2]);
        scheduleDetail.state = parseInt(arrSchedule[3]);
        scheduleDetail.time = arrSchedule[4];
        if (typeof (oneSchedule[1]) != "undefined" && oneSchedule[1] != "") {
            var arrLive = oneSchedule[1].split(_glflash.SplitRecord);
            var flashNum = flashData.graphList.GetNum(arrSchedule[0]);
            var oldFlash = flashData.graphList.items[flashNum];
            var startNum = 0;
            for (var j = 0; j < arrLive.length; j++) {
                var onearr = arrLive[j].split(_glflash.SplitColumn);
                if (onearr.length < 3) continue;
                var oneflash = new _glflash.GraphData(arrSchedule[0], arrLive[j]);
                if (oldFlash.Id == "" || (oldFlash.Id != "" && parseInt(oldFlash.Id) < parseInt(oneflash.Id))) {
                    oldFlash = oneflash;
                    var overTime = 500 * startNum;
                    //window.setTimeout("runEvent(" + oneflash.sId + "," + homeScore + "," + guestScore + ",'" + oneflash + "'," + flashNum + ")", overTime);//避免动画消失太快    
                    if (oneflash.eventType == 23) {
                        var scheduleDetail = flashData.scheduleList.Get(arrSchedule[0]);
                        scheduleDetail.homeScore = parseInt(onearr[7]);
                        scheduleDetail.guestScore = parseInt(onearr[8]);
                    }
                    window.setTimeout2(runEvent, overTime, oneflash.sId, oneflash, flashNum);//避免动画消失太快                     
                    startNum++;
                }
            }
        }
        if (typeof (oneSchedule[2]) != "undefined" && oneSchedule[2] != "") {
            var arrStatus = oneSchedule[2].split(_glflash.SplitRecord);
            var statusNum = flashData.statusList.GetNum(arrSchedule[0]);
            var oldStatus = flashData.statusList.items[statusNum];
            for (var j = 0; j < arrStatus.length; j++) {
                // var oneStatus = new _glflash.statusBar(arrSchedule[0], arrStatus[j]);
                var oneStatus = new _glflash.barDetail(arrStatus[j]);
                var onearr = arrStatus[j].split(_glflash.SplitColumn);
                if (onearr.length < 3) continue;
                var oldStatusItem1 = oldStatus.barList1.items[oldStatus.barList1.items.length - 1];
                if (onearr[1] == "1" && (typeof (oldStatusItem1) == "undefined" || (typeof (oldStatusItem1) != "undefined" && parseInt(oldStatusItem1.Id) < parseInt(oneStatus.Id)))) {
                    flashData.statusList.items[statusNum].barList1.Add(arrSchedule[0], oneStatus);
                    var num = getStatusPosition(oneStatus.eventType, oneStatus.time);
                    var onei = '<i class="' + (oneStatus.eventType == "20" ? "a" : "s") + '" style="left:' + num + 'px;cursor:pointer;" title="' + oneStatus.time + '\'' + (Config.language == 1 ? " 危險進攻" : " 危险进攻") + '"></i>';
                    if (scheduleDetail.homeTeamID == oneStatus.teamID)
                        document.getElementById("homeLine_" + arrSchedule[0]).innerHTML += onei;
                    else
                        document.getElementById("guestLine_" + arrSchedule[0]).innerHTML += onei;
                }
                var oldStatusItem2 = oldStatus.barList2.items[oldStatus.barList2.items.length - 1];
                if (onearr[1] == "2" && (typeof (oldStatusItem2) == "undefined" || (typeof (oldStatusItem2) != "undefined" && parseInt(oldStatusItem2.Id) < parseInt(oneStatus.Id)))) {
                    flashData.statusList.items[statusNum].barList2.Add(arrSchedule[0], oneStatus);
                    var num = getStatusPosition(oneStatus.eventType, oneStatus.time);
                    if (scheduleDetail.homeTeamID == oneStatus.teamID) {
                        if (num - oldCornerTime_H <= 3)
                            num += 3 - (num - oldCornerTime_H);
                        var onei = '<i class="f" style="left:' + num + 'px;cursor:pointer;" title="' + oneStatus.time + '\' 角球"></i>';
                        document.getElementById("homeLine_" + arrSchedule[0]).innerHTML += onei;
                        oldCornerTime_H = num;
                    }
                    else {
                        if (num - oldCornerTime_G <= 3)
                            num += 3 - (num - oldCornerTime_G);
                        var onei = '<i class="f" style="left:' + num + 'px;cursor:pointer;" title="' + oneStatus.time + '\' 角球"></i>';
                        document.getElementById("guestLine_" + arrSchedule[0]).innerHTML += onei;
                        oldCornerTime_G = num;
                    }
                }
                var oldStatusItem3 = oldStatus.barList3.items[oldStatus.barList3.items.length - 1];
                if (onearr[1] == "3" && (typeof (oldStatusItem3) == "undefined" || (typeof (oldStatusItem3) != "undefined" && parseInt(oldStatusItem3.Id) < parseInt(oneStatus.Id)))) {
                    flashData.statusList.items[statusNum].barList3.Add(arrSchedule[0], oneStatus);
                    var num = getStatusPosition(oneStatus.eventType, oneStatus.time);
                    var onei = '<i class="' + getBarBallStyle(oneStatus.eventType) + '" style="left:' + num + 'px;cursor:pointer;" title="' + oneStatus.time + "\'" + getBarBallStyleName(oneStatus.eventType) + '"></i>';
                    if (scheduleDetail.homeTeamID == oneStatus.teamID)
                        document.getElementById("homeLine_" + arrSchedule[0]).innerHTML += onei;
                    else
                        document.getElementById("guestLine_" + arrSchedule[0]).innerHTML += onei;
                }
            }
        }
        if (arrSchedule[5] != scheduleDetail.detailTime) {//入球事件有删除时触发
            refreshStatus(arrSchedule[0]);
        }
    }
}
function changeBfOdds(isLet, sId) {
    Config.bfOddsShowLetGoal = isLet;
    document.getElementById("bfOddsDiv").innerHTML = makeBfOdds(sId);
}
function makeBfOdds(sId) {
    var propeList = Config.bfOddsShowLetGoal ? [["homeOdds_f", "letgoal_f", "guestOdds_f"], ["homeOdds", "letgoal", "guestOdds"]] : [["upOdds_f", "totalScore_f", "downOdds_f"], ["upOdds", "totalScore", "downOdds"]];
    var oddsState = new Array('开', '即');
    var bfOddsItem = (typeof (flashData.bfOddsList) != 'undefined' ? flashData.bfOddsList.Get(sId) : null);
    if (isCompanyPage && companyID != 3)
        bfOddsItem = null;
    var html = new Array();
    html.push('<table width="100%" border="0" cellspacing="1" cellpadding="0">');
    html.push('<tr><th colspan="6" align="left"><div class="btns"><span' + (Config.bfOddsShowLetGoal ? ' class="on"' : '') + ' onclick="changeBfOdds(true,' + sId + ')">亚让</span><span' + (!Config.bfOddsShowLetGoal ? ' class="on"' : '') + ' onclick="changeBfOdds(false,' + sId + ')">进球数</span></div>&nbsp;&nbsp;' + (Config.language == 1 ? "即時指數" : "即时指数") + '</th></tr>');
    if (bfOddsItem != null) {
        html.push('<tr>');
        html.push('<td width="30" align="center">' + (Config.language == 1 ? "時間" : "时间") + '</td>');
        html.push('<td width="45" align="center">比分</td>');
        html.push('<td colspan="4" align="center">' + (Config.language == 1 ? "指數" : "指数") + '</td>');
        html.push('</tr>');
        var scheduleDetail = flashData.scheduleList.Get(sId);
        var noDataStyle = (bfOddsItem.oddsList.items.length >= 3 ? '' : bfOddsItem.oddsList.items.length == 2 ? 'nodata' : 'nodata2');
        var noDataContent = "";
        if (bfOddsItem.oddsList.items.length < 3)
            noDataContent = (parseInt(scheduleDetail.state) > 0 || parseInt(scheduleDetail.state) == -1) ? '&nbsp;' : bfOddsItem.oddsList.items.length == 1 && bfOddsItem.oddsList.stateInfo == "" ? '暂无即时数据' : '暂无滚球数据';
        var startIndex = bfOddsItem.oddsList.items.length < 3 ? 0 : bfOddsItem.oddsList.items.length - 3;//只显示最新三条。虽然数据文件已做处理，但一条新记录产生时，总长度还是会超过三条
        for (var i = startIndex; i < bfOddsItem.oddsList.items.length; i++) {
            var oddsItem = bfOddsItem.oddsList.items[i];
            html.push('<tr align="center"><td rowspan="2">' + oddsItem.stateInfo + '</td><td rowspan="2">' + oddsItem.showScore + '</td>');
            for (var j = 0; j < propeList.length; j++) {
                if (j == 1)
                    html.push('<tr align="center">');
                html.push('<td>' + oddsState[j] + '</td>');
                propeList[j].forEach(function (a) {
                    html.push('<td' + (a.indexOf("goal") != -1 || a.indexOf("totalScore") != -1 ? ' class="y"' : '') + '>' + oddsItem[a] + '</td>');
                });
                html.push('</tr>');
            }
        }
        html.push('</table>');
        if (noDataStyle != "")
            html.push('<div class="' + noDataStyle + '">' + noDataContent + '</div>');
    }
    else {
        html.push('</table>');
        html.push('<div class="nodata3">暂无数据</div>');
    }
    return html.join("");
}
function bfOddsRefresh() {
    if (txtChangeBfOdds.readyState != 4 || (txtChangeBfOdds.status != 200 && txtChangeBfOdds.status != 0)) return;
    if (oldChnageBfOddsData == txtChangeBfOdds.responseText || txtChangeBfOdds.responseText == "" || flashScheduleIDs == "") return;
    oldChnageBfOddsData = txtChangeBfOdds.responseText;
    var propeList = Config.bfOddsShowLetGoal ? [["homeOdds_f", "letgoal_f", "guestOdds_f"], ["homeOdds", "letgoal", "guestOdds"]] : [["upOdds_f", "totalScore_f", "downOdds_f"], ["upOdds", "totalScore", "downOdds"]];
    flashData.changeBfOddsList = _glflash.initBfOdds(txtChangeBfOdds.responseText);
    var changeBfOddsItem = flashData.changeBfOddsList.Get(flashScheduleIDs);
    var oldBfOddsItem = flashData.bfOddsList.Get(flashScheduleIDs);
    if (changeBfOddsItem == null) return;
    var isReload = false;
    if (oldBfOddsItem != null) {
        var obj = document.getElementById("bfOddsDiv").getElementsByTagName("table")[0];//.tBodies[0];
        for (var i = 0; i < changeBfOddsItem.oddsList.items.length; i++) {
            var isChange = false, isColorChange = false;
            var bfOddsItem = changeBfOddsItem.oddsList.items[i];
            var oldOddsItem = oldBfOddsItem.oddsList.Get(bfOddsItem.ID);
            if (oldOddsItem != null) {//状态或比分没变化，不需要新加赔率行时
                for (var j = 0; j < propeList.length; j++) {
                    var trObj = (j == 0 ? obj.rows[obj.rows.length - 2] : obj.rows[obj.rows.length - 1]);
                    var tdIndex = (j == 0 ? 3 : 1);//初指赔率从第3个单无格开始；即时赔率从第一个单元格开始
                    for (var k = 0; k < propeList[j].length; k++) {
                        var key = propeList[j][k];
                        if (bfOddsItem[key] != oldOddsItem[key]) {
                            isChange = true;
                            if (j == 0 || k == 1)//初指和盘口更新不需要变化底色
                                trObj.cells[tdIndex + k].innerHTML = bfOddsItem[key];
                            else {
                                var colorClass = getOddsColor(bfOddsItem[key], oldOddsItem[key]);
                                if (!isColorChange)
                                    isColorChange = (colorClass != "");
                                trObj.cells[tdIndex + k].innerHTML = (colorClass != "" ? '<span class="' + colorClass + '">' + bfOddsItem[key] + '</span>' : bfOddsItem[key]);
                            }
                        }
                    }
                }
                if (isChange) {
                    obj.rows[obj.rows.length - 2].cells[0].innerHTML = bfOddsItem.stateInfo;
                    updateObjData(oldOddsItem, bfOddsItem);
                }
            }
            else {
                isReload = true;//状态或比分变化时重新加载整块赔率
                oldBfOddsItem.oddsList.Add(bfOddsItem.ID, bfOddsItem);
            }
        }
        if (isColorChange)
            window.setTimeout("restoreBfOddsColor(" + changeBfOddsItem.oddsList.items.length + ")", 30000);
    }
    else {
        isReload = true;//新开盘的重新加载整块赔率
        flashData.bfOddsList.Add(flashScheduleIDs, changeBfOddsItem);
    }
    if (isReload)
        document.getElementById("bfOddsDiv").innerHTML = makeBfOdds(flashScheduleIDs);
}
function getOddsColor(changeOdds, odds) {
    if (_glflash.getFloat(changeOdds) > _glflash.getFloat(odds)) return "redBG";
    else if (_glflash.getFloat(changeOdds) < _glflash.getFloat(odds)) return "greenBG";
    else return "";
}
function updateObjData(oldObj, newObj) {
    for (property in oldObj) {
        if (newObj.hasOwnProperty(property) && newObj[property] != null && newObj[property].toString() != "")
            oldObj[property] = newObj[property];
    }
}
function restoreBfOddsColor(num) {
    try {
        var obj = document.getElementById("bfOddsDiv");
        if (obj == null) return;
        obj = obj.getElementsByTagName("table")[0];
        if (obj == null) return;
        var tr1 = obj.rows[obj.rows.length - 2];
        var tr2 = obj.rows[obj.rows.length - 1];
        if (num > 1) {
            var tr3 = obj.rows[obj.rows.length - 4];
            var tr4 = obj.rows[obj.rows.length - 3];
        }
        for (var i = 0; i < tr1.cells.length; i++) {
            tr1.cells[i].innerHTML = tr1.cells[i].innerHTML.toLowerCase().replace(/<span class=redbg>/g, "").replace(/<span class=greedbg>/g, "").replace(/<\/span>/g, "");
        }
        for (var i = 0; i < tr2.cells.length; i++) {
            tr2.cells[i].innerHTML = tr2.cells[i].innerHTML.toLowerCase().replace(/<span class=redbg>/g, "").replace(/<span class=greedbg>/g, "").replace(/<\/span>/g, "");
        }
        if (num > 1) {
            for (var i = 0; i < tr3.cells.length; i++) {
                tr3.cells[i].innerHTML = tr3.cells[i].innerHTML.toLowerCase().replace(/<span class=redbg>/g, "").replace(/<span class=greedbg>/g, "").replace(/<\/span>/g, "");
            }
            for (var i = 0; i < tr4.cells.length; i++) {
                tr4.cells[i].innerHTML = tr4.cells[i].innerHTML.toLowerCase().replace(/<span class=redbg>/g, "").replace(/<span class=greedbg>/g, "").replace(/<\/span>/g, "");
            }
        }
    }
    catch (e) { }
}

function getBarBallStyle(kind) {
    return kind == 1 ? "b" : kind == 7 ? "b2" : "b3";
}
function getBarBallStyleName(kind) {
    var name = "";
    switch (kind) {
        case "7":
            name = Config.language == 1 ? "點球" : "点球";
            break;
        case "8":
            name = Config.language == 1 ? "烏龍球" : "乌龙球";
            break;
        default:
            name = Config.language == 1 ? "進球" : "进球";
            break;
    }
    return " " + name;
}
function refreshStatus(sId) {
    if (!Config.IsIE) return;//旧版才需要执行
    loadFlashData();
    oldCornerTime_H = 0, oldCornerTime_G = 0;
    document.getElementById("statusLine_" + sId).innerHTML = makeStatus(sId);
}
function getPreHtml(pre, kind) {
    pre = parseFloat(pre);
    var preHtml = '<font {0}>{1}%</font>';
    var bgStyle = new Array("class=redBG", "class=greenBG", "color=blue");
    var bgColor = new Array("color=red", "color=green", "color=blue");
    var styleIndex = pre >= 70 ? 0 : pre <= 30 ? 1 : 2;
    var showColor = kind == 1 ? bgStyle : bgColor;
    return preHtml.format(showColor[styleIndex], pre);
}
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
function SetTrBgColor() {
    var trs = document.getElementById("table_live").getElementsByTagName("tr");
    var count = 0;
    for (var i = 0; i < trs.length; i++) {
        if (trs[i].getAttribute("index") != null && trs[i].style.display != "none") {
            trs[i].style.backgroundColor = (count % 2 == 0 ? bg1 : bg2);
            count++;
        }
    }
}
function getHdLiveUrl(scheduleID) {

    var url = "/detail/" + scheduleID + (Config.language == 0 ? "cn" : Config.language == 1 ? "" : "sb") + ".htm?s=1";
    return '<a href="' + url +'" target="_blank" style="color:blue"><b>' + (Config.language == 1 ? "高清直播" : "高清直播") + '</b></a>';
    //return '<span onclick="showgoallist(' + scheduleID + ')">' + (Config.language == 1 ? "高清直播" : "高清直播") + '</span>';
}
//window.onload = function () {
//    document.getElementById("ad").innerHTML = '<div style="width: 940px;background-color: #f6f6f6;margin-left: 0px;"><img src="/image/chai.gif" width="940" height="45" border="0"></div>';
//}
function randomSort(arr) {
    try {
        arr.sort(function (a, b) {
            return Math.random() - 0.5;
        });
    } catch (e) { }
    return arr;
}
//var jsonStr = '{"freeInfo":[["专家精选每日赛事分析", "http://ba2.titan007.com/133/12276314.html" ],["V顾问带您分析英超新赛季", "http://v.titan007.com/"],["新用户尊享", "http://users.titan007.com/users/register.aspx?from=http://ba2.titan007.com/133/11796085.html" ]],"chargeInfo":[["title1", "www.runoob.com" ],["title2", "www.google.com"],["title3", "www.taobao.com" ]]}';
var _spreadBaInfo = new Object();
_spreadBaInfo.freeJsonArray = new Array();
_spreadBaInfo.chargeJsonArray = new Array();
_spreadBaInfo.freeInfo = "";
_spreadBaInfo.getData = function (filePath) {
    ShowMsgBox();
    if (Config.isHideAd)
        LoadLiveFile();
    else {
        $.get(filePath + "?r=007" + Date.parse(new Date()), function (result) {
            var jsonArr = (typeof (JSON) != 'undefined' ? JSON.parse(result) : eval('(' + result + ')'));
            _spreadBaInfo.freeJsonArray = jsonArr.freeInfo;
            _spreadBaInfo.chargeJsonArray = randomSort(jsonArr.chargeInfo);
            _spreadBaInfo.freeInfo = _spreadBaInfo.freeInfoHtml();
            LoadLiveFile();
        });
    }
}
_spreadBaInfo.chargeInfoHtml = function (rowIndex, scheduleShowCount, rowCount) {
    var returnValue = "";
    var arrayIndex = 3 * (rowIndex - 1);
    //页面显示的赛程数据足够时才显示推广
    if ((3 * (rowIndex - 1) + 1 <= scheduleShowCount || scheduleShowCount == 0) && _spreadBaInfo.chargeJsonArray != null && typeof (_spreadBaInfo.chargeJsonArray[arrayIndex]) != 'undefined') {//scheduleShowCount为0表示比分页面赛程不够
        returnValue = '<tr><td colspan="' + rowCount + '" bgcolor="#ffffff" align="center" height="18"><ul class="chargeInfo">';
        for (var i = 0; i < 3; i++) {
            returnValue += '<li>';
            if (arrayIndex + i < _spreadBaInfo.chargeJsonArray.length) {//推广数组范围内的才显示推广
                returnValue += '用户推广：<a href="' + _spreadBaInfo.chargeJsonArray[arrayIndex + i][1] + '" target="_blank" style="color:' + (_spreadBaInfo.chargeJsonArray[arrayIndex + i].length > 2 ? '#' + _spreadBaInfo.chargeJsonArray[arrayIndex + i][2] : 'blue') + '"><b>' + _spreadBaInfo.chargeJsonArray[arrayIndex + i][0] + "</b></a>";
            }
            returnValue += '</li>';
        }
        returnValue += '</ul></td></tr>';
    }
    return returnValue;
}
_spreadBaInfo.freeInfoHtml = function () {
    var returnValue = "";
    if (_spreadBaInfo.freeJsonArray != null && _spreadBaInfo.freeJsonArray.length > 0) {
        returnValue = '<ul class="freeInfo">';
        for (var i = 0; i < 3; i++) {
            returnValue += '<li>' + (_spreadBaInfo.freeJsonArray.length > i ? '<a href="' + _spreadBaInfo.freeJsonArray[i][1] + '" target="_blank" style="color:#' + _spreadBaInfo.freeJsonArray[i][2] + '"><b>' + _spreadBaInfo.freeJsonArray[i][0] + '</b></a>' : '') + '</li > ';
        }
        returnValue += '</ul>';
    }
    return returnValue;
}
function GetQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg); //获取url中"?"符后的字符串并正则匹配
    var context = "";
    if (r != null)
        context = r[2];
    reg = null;
    r = null;
    return context == null || context == "" || context == "undefined" ? "" : context;
}
function setRegKindCookie() {
    if (window.location.href.indexOf("?g=tf") != -1)
        writeCookie("RegKind", "tf", true);
}
var T = new Object();
function initAliasName() {
    var nameArr = new Array();
    try {
        oXmlHttp.open("get", staticUrl + "vbsxml/alias3.txt?r=007" + Date.parse(new Date()), false);
        oXmlHttp.onreadystatechange = function () {
            if (oXmlHttp.readyState == 4 && oXmlHttp.status == 200) {
                if (oXmlHttp.responseText != "") {
                    var t_alias = oXmlHttp.responseText;
                    nameArr = t_alias.split(',');
                    for (var i = 0; i < nameArr.length; i++) {
                        var nameTemp = nameArr[i].split('^');
                        T[nameTemp[0] + "_" + nameTemp[1]] = [nameTemp[2]];
                    }
                }
            }
        };
        oXmlHttp.send(null);
    }
    catch (e) { }
}

var groupNameList = ["Hot", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
function pySegSort(arr,index, empty) {
    if (!String.prototype.localeCompare)
        return null;

    var letters = "*abcdefghijklmnopqrstuvwxyz".split('');
    var zh = "阿八嚓哒妸发旮哈讥咔垃痳拏噢妑七呥扨它穵夕丫帀".split('');

    var segs = [];
    var curr;
    for (var i = 0; i < letters.length; i++) {
        curr = { letter: letters[i], data: [] };        
        try {
            for (var j = 0; j < arr.length; j++) {
                var obj = arr[j];
                var lett = getChineseStrPY(obj[index], 'all')[0].toLowerCase();
                if (obj[index] == "秘鲁")
                    lett = 'b';
                if (lett == letters[i]) {//如果首字母小写和当前一致，则添加
                    curr.data.push(obj);
                }
                //else if (letters[i] == "#") {//如果非字母非汉字，则添加进#中
                //    var lett = getChineseStrPY(obj[index], 'all')[0].toLowerCase();
                //    var charCode = lett.charCodeAt(0);
                //    if (charCode > 40869) {//19968~40869汉字
                //        curr.data.push(obj);
                //    } else if (122 < charCode && charCode < 19968) {//97~122小写字母
                //        curr.data.push(obj);
                //    } else if (90 < charCode && charCode < 97) {//65~90大写字母
                //        curr.data.push(obj);
                //    } else if (charCode < 65) {
                //        curr.data.push(obj);
                //    }
                //}
                //if ((!zh[i - 1] || zh[i - 1].localeCompare(obj[index], "zh") <= 0) && (zh[i] == undefined || obj[index].localeCompare(zh[i], "zh") == -1)) {
                //    curr.data.push(obj);
                //}
            }
        }
        catch (e) {
            console.log(e);
        }
        if (empty || curr.data.length) {
            segs.push(curr);
            //curr.data.sort(function (a, b) {
            //    return a[index].localeCompare(b[index], "zh");
            //});
        }
    }
    return segs;
}

$('#Layer2 .screen').bind("scroll", function () {
    var top = $(this).scrollTop();
    var temptop = top;
    var h = $(this).height();
    top = h < 420 ? "50%" : (top + 220) + "px";    
    if ($(this).scrollTop() > myleagueHeight)
        top = (myleagueHeight + 220) + "px";
    $("#Layer2 .Fright_nav").css("top", top);
    //console.log("firstTop:" + temptop + ",top:" + top + ",h:" + h);
});
$('#DivCountry .screen').bind("scroll", function () {
    var top = $(this).scrollTop();
    var h = $(this).height();
    top = h < 420 ? "50%" : (top + 220) + "px";
    if ($(this).scrollTop() > mycountryHeight)
        top = (mycountryHeight + 220) + "px";
    $("#DivCountry .Fright_nav").css("top", top);
});
function ShowGruopName() {
    for (var i = 0; i < groupNameList.length; i++) {
        var letter = groupNameList[i];
        if (document.getElementById("group" + letter) == null) continue;
        //var arr = $("#class" + letter + " label:visible");
        var count = 0;
        var arr = document.getElementById("class" + letter);
        for (var j = 0; j < arr.childNodes.length; j++) {
            if (arr.childNodes[j].style.display == "block") {
                count++;
                break;
            }
        }
        if (count == 0) {
            document.getElementById("group" + letter).style.display = "none";
            document.getElementById("class" + letter).style.display = "none";
            document.getElementById("s" + letter).style.display = "none";
        } else {
            document.getElementById("group" + letter).style.display = "";
            document.getElementById("class" + letter).style.display = "";
            document.getElementById("s" + letter).style.display = "";
        }
    }
}
function goPosistion(id,type) {
    var mainContainer = type == 0 ? $('#myleague') : $('#countryList');
    var scrollToContainer = mainContainer.find('#group' + id);
    if (!!scrollToContainer && !!scrollToContainer.offset()) {
        mainContainer.scrollTop(
            scrollToContainer.offset().top - mainContainer.offset().top + mainContainer.scrollTop()
        );
    }
}
function goPosistionTop(type) {
    var mainContainer = type == 0 ? $('#myleague') : $('#countryList');
    var scrollToContainer = mainContainer.find("#" + mainContainer[0].firstChild.id);
    //var scrollToContainer = mainContainer.find('#groupHot');
    if (!!scrollToContainer && !!scrollToContainer.offset()) {
        mainContainer.scrollTop(
            scrollToContainer.offset().top - mainContainer.offset().top + mainContainer.scrollTop()
        );
    }
}
function ShowIEMsg(type) {
    if (type == 0)
        document.getElementById("tipsBox").style.display = "none";
}
function ShowMsgBox() {
    if (Config.IEVer > 0 && Config.IEVer < 9) {
        document.getElementById("tipsBox").style.display = "";
    }
    else {
        document.getElementById("scoreLoading").style.display = "";
    }
}
function ShowSclass(t) {
    //if (t == Config.sclassType) return;
    for (var i = 0; i < 4; i++) {
        document.getElementById("rbs" + i).className = "";        
    }
    document.getElementById("rbs" + t).className = "on";
    var index = 0;
    for (var i = 0; i < 5; i++) {
        if (document.getElementById("rb" + i).className == "on") {
            index = i;
            break;
        }
    }
    makeLeague(t)
    //ShowMatchByMatchState(index);
}
//获取距离10点半时间，用于每天重置联赛筛选cookie
function GetCookieTime() {
    var d1 = new Date();
    var d2 = new Date();
    if (d1.getHours() * 100 + d1.getMinutes() > 1030) {
        d2 = new Date(d1.getFullYear(), d1.getMonth(), d1.getDate() + 1, 10, 30, 0);
    }
    else {
        d2 = new Date(d1.getFullYear(), d1.getMonth(), d1.getDate(), 10, 30, 0);
    }
    var d3 = d2 - d1;
    return d3;
}
function getDataIndex(sId) {
    var i = 1;
    for (;i < A.length; i++) {
        if (A[i][0] == sId)
            break;
    }
    return i;
}
var qingbaoList = new Array();
function QingbaoObj(data) {
    var temp = data.split("^");
    this.Id = temp[0];
    this.count = parseInt(temp[1]);
}
if (typeof(QingBao_Soccer) != 'undefined') {
    var tempData = QingBao_Soccer.split("!");
    for (var i = 0; i < tempData.length; i++) {
        var obj = new QingbaoObj(tempData[i]);
        qingbaoList.push(obj);
    }
}

function WsBegin(isReconnect) {
    try {
        //var token = "";
        var url = "wss://live.titan007.com/stream";
        var re = /(\d+)\.(\d+)\.(\d+)\.(\d+)\:(\d+)/;
        if (IsTest())
            url = "ws://" + window.location.href.match(re)[0] +"/stream";
        //var txtTokenHttp = zXmlHttp.createRequest();
        //txtTokenHttp.open("get", "/commoninterface", false);
        //txtTokenHttp.send(null);
        //token = txtTokenHttp.responseText;
        var options;
        if (Config.oddsChangeFile == "")
            options = { channels: ["change_ut_xml"], url: url };
        else
            options = { channels: ["change_ut_xml", Config.oddsChangeFile], url: url };
        return wsHelper.connectWs(options, isReconnect);
    }
    catch (e) {
        return false;
    }
}
function ReceiveMsg(event) {
    //console.log(`${event.type}: `, event.detail.data);
    try {
        var data = event.detail.data;
        var reader = new FileReader();       
        reader.onload = function () {
            var jsonObj = JSON.parse(pako.inflate(new Uint8Array(reader.result), {
                to: "string"
            }));
            /*     console.log(jsonObj);*/
            if (!!jsonObj.change_ut_xml) {
                if (isShowConsole)
                    console.log(jsonObj.change_ut_xml);
                zqScoreChange(jsonObj.change_ut_xml);
            }
            if (Config.oddsChangeFile in jsonObj) {
                zqOddsChange(jsonObj[Config.oddsChangeFile], false);
            }
        }
        reader.readAsArrayBuffer(data);
    }
    catch (e) {
        console.log("ReceiveMsgError:" + e);
    }
}
var scoreChInterval;
var refreshTime = 2000;
function SocketClose(event) {
    //如果重连超过一定次数或者不是正常的，改用轮询
    if (window.wsHelper.options.reConnect >= window.wsHelper.options.maxReconNum || !window.wsHelper.options.normal) {
        reloadChangeData();
    }
}

function WsRun() {
    window.removeEventListener('ws-message', ReceiveMsg);
    window.addEventListener('ws-message', ReceiveMsg);
    window.removeEventListener('ws-close', SocketClose);
    window.addEventListener('ws-close', SocketClose);
}
function getChangeData() {
    if (isFirstLoad) {
        Config.oddsChangeFile = !isHomeIndex && !isCompanyPage ? "" : (isCompanyPage ? "ch_goal" + companyID + "_xml2" : "ch_goalBf3_xml2");
        if (!WsBegin(true)) {
            reloadChangeData();
        }
        else {
            WsRun();
        }
        isFirstLoad = false;
    }
}
function reloadChangeData() {
    gettime();
    if (window.location.href.toLocaleLowerCase().indexOf("oldindexall") == -1) {
        window.clearTimeout(getoddsxmlTimer);
        getoddsxmlTimer = window.setTimeout("getoddsxml()", 4000);
    }
}
function checkShowAd(data) {
    if (Config.isHideAd) {
        var temp = data.replaceAll("&nbsp;", "");
        temp = temp.replaceAll(/\<a.*?\<\/a\>/g, "");
        return temp;
    }
    else
        return data;
}
function showAdv() {
    try {
        var adv = document.getElementById("adv");//反屏蔽模式
        var s = document.createElement("script");
        s.type = "text/javascript";
        s.charset = "utf-8";
        s.src = "//budjs.titan007.com/common/dy_xgn/source/nh/u_h.js";
        adv.appendChild(s, "script");
        //(window.slotbydup = window.slotbydup || []).push({   非反屏蔽模式
        //    id: "u6921932",
        //    container: "_l2nblo0h0bo",
        //    async: true
        //});
    }
    catch (e) {
        console.log(e);
    }
}
function initAdv() {
    if (Config.isHideAd) return;
    var cookieName = "uAdv"
    var str = getCookie(cookieName);
    var time1 = new Date(new Date().getFullYear() + "-" + (new Date().getMonth() + 1) + "-" + new Date().getDate() + " 12:00:00");
    var nowTime = new Date();
    if (str == "" || str == null) {
        writeCookie(cookieName, nowTime.getTime() + "^" + 1 + "^" + (nowTime > time1 ? 1 : 0));//上午为0，下午为1
        showAdv();
    }
    else {
        var arr = str.split('^');
        var lastTimeSpan = parseInt(arr[0]);
        var times = parseInt(arr[1]);
        var timeType = arr.length > 2 ? parseInt(arr[2]) : (nowTime > time1 ? 1 : 0);
        var lastTimeDate = new Date(date("Y-m-d 00:00:00", lastTimeSpan));
        if (lastTimeDate < new Date(new Date().getFullYear() + "-" + (new Date().getMonth() + 1) + "-" + new Date().getDate() + " 00:00:00")) {//通过日期判断是否当天首次打开
            writeCookie(cookieName, new Date().getTime() + "^" + 1 + "^" + (nowTime > time1 ? 1 : 0));
            showAdv();
        }
        else {
            //var lastTime = new Date(date("Y-m-dTH:i:s", lastTimeSpan));
            if (nowTime < time1) {//当天12点前
                if (times < 4 && nowTime.getTime() - lastTimeSpan > 900000) {//12点前显示4次，超过15分钟显示一次
                    if (times == 3)
                        writeCookie(cookieName, time1.getTime() + "^0^1");//12点前超过4次后不显示，设置下次显示时间为12点后
                    else
                        writeCookie(cookieName, new Date().getTime() + "^" + (times + 1) + "^0");
                    showAdv();
                }
            }
            else {
                if (timeType == 0)
                    times = 0;
                if (times < 4 && (nowTime.getTime() - lastTimeSpan > 900000)) {
                    writeCookie(cookieName, new Date().getTime() + "^" + (times + 1) + "^1");
                    showAdv();
                }
            }
        }
    }
}
//时间戳格式化,date("YmdHis",time) 相当于yyyyMMddHHmmss
function date(format, timestamp) {
    var a, jsdate = ((timestamp) ? new Date(timestamp.length == 10 ? (timestamp * 1000) : (timestamp * 1)) : new Date());
    var pad = function (n, c) {
        if ((n = n + "").length < c) {
            return new Array(++c - n.length).join("0") + n;
        } else {
            return n;
        }
    };
    var txt_weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    var txt_ordin = { 1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st" };
    var txt_months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var f = {
        // Day 
        d: function () { return pad(f.j(), 2) },
        D: function () { return f.l().substr(0, 3) },
        j: function () { return jsdate.getDate() },
        l: function () { return txt_weekdays[f.w()] },
        N: function () { return f.w() + 1 },
        S: function () { return txt_ordin[f.j()] ? txt_ordin[f.j()] : 'th' },
        w: function () { return jsdate.getDay() },
        z: function () { return (jsdate - new Date(jsdate.getFullYear() + "/1/1")) / 864e5 >> 0 },

        // Week 
        W: function () {
            var a = f.z(), b = 364 + f.L() - a;
            var nd2, nd = (new Date(jsdate.getFullYear() + "/1/1").getDay() || 7) - 1;
            if (b <= 2 && ((jsdate.getDay() || 7) - 1) <= 2 - b) {
                return 1;
            } else {
                if (a <= 2 && nd >= 4 && a >= (6 - nd)) {
                    nd2 = new Date(jsdate.getFullYear() - 1 + "/12/31");
                    return date("W", Math.round(nd2.getTime() / 1000));
                } else {
                    return (1 + (nd <= 3 ? ((a + nd) / 7) : (a - (7 - nd)) / 7) >> 0);
                }
            }
        },

        // Month 
        F: function () { return txt_months[f.n()] },
        m: function () { return pad(f.n(), 2) },
        M: function () { return f.F().substr(0, 3) },
        n: function () { return jsdate.getMonth() + 1 },
        t: function () {
            var n;
            if ((n = jsdate.getMonth() + 1) == 2) {
                return 28 + f.L();
            } else {
                if (n & 1 && n < 8 || !(n & 1) && n > 7) {
                    return 31;
                } else {
                    return 30;
                }
            }
        },

        // Year 
        L: function () { var y = f.Y(); return (!(y & 3) && (y % 1e2 || !(y % 4e2))) ? 1 : 0 },
        //o not supported yet 
        Y: function () { return jsdate.getFullYear() },
        y: function () { return (jsdate.getFullYear() + "").slice(2) },

        // Time 
        a: function () { return jsdate.getHours() > 11 ? "pm" : "am" },
        A: function () { return f.a().toUpperCase() },
        B: function () {
            // peter paul koch: 
            var off = (jsdate.getTimezoneOffset() + 60) * 60;
            var theSeconds = (jsdate.getHours() * 3600) + (jsdate.getMinutes() * 60) + jsdate.getSeconds() + off;
            var beat = Math.floor(theSeconds / 86.4);
            if (beat > 1000) beat -= 1000;
            if (beat < 0) beat += 1000;
            if ((String(beat)).length == 1) beat = "00" + beat;
            if ((String(beat)).length == 2) beat = "0" + beat;
            return beat;
        },
        g: function () { return jsdate.getHours() % 12 || 12 },
        G: function () { return jsdate.getHours() },
        h: function () { return pad(f.g(), 2) },
        H: function () { return pad(jsdate.getHours(), 2) },
        i: function () { return pad(jsdate.getMinutes(), 2) },
        s: function () { return pad(jsdate.getSeconds(), 2) },
        //u not supported yet 

        // Timezone 
        //e not supported yet 
        //I not supported yet 
        O: function () {
            var t = pad(Math.abs(jsdate.getTimezoneOffset() / 60 * 100), 4);
            if (jsdate.getTimezoneOffset() > 0) t = "-" + t; else t = "+" + t;
            return t;
        },
        P: function () { var O = f.O(); return (O.substr(0, 3) + ":" + O.substr(3, 2)) },
        //T not supported yet 
        //Z not supported yet 

        // Full Date/Time 
        c: function () { return f.Y() + "-" + f.m() + "-" + f.d() + "T" + f.h() + ":" + f.i() + ":" + f.s() + f.P() },
        //r not supported yet 
        U: function () { return Math.round(jsdate.getTime() / 1000) }
    };

    return format.replace(/[\ ]?([a-zA-Z])/g, function (t, s) {
        if (t != s) {
            // escaped 
            ret = s;
        } else if (f[s]) {
            // a date function exists 
            ret = f[s]();
        } else {
            // nothing special 
            ret = t == "T" || t == "t" ? " " : s;
        }
        return ret;
    });
}
function initHtml() {
    GetTopImg();
    CreatTipsToolHtml();
}
function CreatTipsToolHtml() {
    
    var html = new Array();
    html.push('<a id="toplink" style="display:none;" class="top" onclick="goTopOrBottom(0)" title="回到顶部"><i>顶部</i></a>');
    html.push('<a class="appLink QRcode" title="客户端下载" onclick="GoAppDownload(event)">');
    html.push('<i><span class="tit">客户端</span>');
    html.push('<ul class="appLinkpop">');
    html.push('<li class="app" onclick="GoAppDownload(event)"><b>' + (Config.language == 1 ? "新球體育" : "新球体育") + '</b>');
    html.push('<img class="appicon" src="//users.titan007.com/images/nbo007.png"><div class="appLinkbtn">立即下载</div>');
    html.push('</li>');
    //html.push('<li class="app" onclick="window.open(\'//www.dee138.com/app\', \'_blank\')"><b>微球</b>');
    //html.push('<img class="appicon" src="//users.titan007.com/images/weiqiu/weiqiucode.png"><div class="appLinkbtn">立即下载</div>');
    //html.push('</li>');
    html.push('</ul>');
    html.push('</a>');
    //html.push('<a class="feedback" title="反馈" onclick="showFeedback()"><i>反馈</i></a>');//http://192.168.10.42:866//users.titan007.com
    html.push('<a class="feedback" title="反馈" href="//users.titan007.com/fanku.aspx" target="_blank"><i>反馈</i></a>');
    html.push('<a id="bottomlink" class="bottom" title="回到底部" onclick="goTopOrBottom(1)"><i>底部</i></a>');

    var element = document.createElement("div");
    element.id = "returnTop";
    element.className = "tipsTool";
    element.innerHTML = html.join("");
    element.style.position = "fixed";
    element.style.left = ((document.body.clientWidth - 950) / 2 + 950 + 10) + "px";
    element.style.bottom = "193px";
    document.getElementsByTagName('body')[0].appendChild(element);
    
}
function GoAppDownload(e) {
    window.open('//www.titan007.com/app/', '_blank');
    e.stopPropagation();
}
function showAppTips(type) {
    document.getElementById("appTips").style.display = type == 1 ? "block" : "none";
}
//滚动条距离顶部高度
function getScrollTop() {
    var scrollTop = 0;
    if (document.documentElement && document.documentElement.scrollTop) {
        scrollTop = document.documentElement.scrollTop;
    }
    else if (document.body) {
        scrollTop = document.body.scrollTop;
    }
    return Math.ceil(scrollTop);
}

//滚动条本身高度：就是可视窗口高度
function getScrollBarHeight() {
    var scrollBarHeight = document.documentElement.clientHeight;
    return Math.ceil(scrollBarHeight);
}

//整个页面高度
function getPageHeight() {
    return Math.ceil(Math.max(document.body.clientHeight, document.documentElement.scrollHeight));
}


window.onscroll = function () {
    var top = getScrollTop();
    var ch = getScrollBarHeight();
    var sh = getPageHeight();
    if (sh - top - ch > 260) {
        $("#bottomlink").fadeIn(500);
        //document.getElementById("bottomlink").style.display = "block";
    }
    else {
        $("#bottomlink").fadeOut(500);
        //document.getElementById("bottomlink").style.display = "none";
    }
    if (top > 250) {
        $("#toplink").fadeIn(500);
        //document.getElementById("toplink").style.display = "block";
    }
    else {
        $("#toplink").fadeOut(500);
        //document.getElementById("toplink").style.display = "none";
    }
}
window.onresize = function () {
    document.getElementById("returnTop").style.left = ((document.body.clientWidth - 950) / 2 + 950+10) + "px";
}
function goTopOrBottom(type) {
    var top = 0;
    if (type == 1) {
        top = getPageHeight();
    }
    $('html,body').animate({ scrollTop: top + 'px' }, 'normal');

}
function showFeedback() {
    var obj = document.getElementById("feedBackDiv");
    if (obj == null) {
        var node = document.createElement("div");
        node.id = "feedBackDiv";
        //node.className = "feedbackpop";
        node.innerHTML = "<iframe src='//users.titan007.com/fanku.aspx' frameborder='0' width='100%' height='100%' scrolling='no'></iframe>";
        //192.168.10.43:81  users.titan007.com  http://192.168.10.42:866/fanku.aspx
        document.getElementsByTagName('body')[0].appendChild(node);
    }
    else {
        obj.innerHTML = "<iframe src='//users.titan007.com/fanku.aspx' frameborder='0' width='100%' height='100%' scrolling='no'></iframe>";
    }
        
}
//window.addEventListener('message', function (e) {
//    var type = e.data.type == undefined ? 0 : parseInt(e.data.type);
//    if (type > 0)
//        this.document.getElementById("feedBackDiv").style.display = "none";
//});
function MoveToTop(obj) {
    var oldPos = matchindex;
    var TTime = new Date();
    var timeStr = AmountTimeDiff(D[8], A[matchindex][36], A[matchindex][43], 1);
    var dataStr = timeStr.split(" ");
    tr.cells[2].innerHTML = dataStr[1];
    var nt = D[8].split(":");
    var nd = D[14].split("-");
    var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
    for (var i = 1; i <= matchcount; i++) {
        if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
            var ot = A[i][11].split(":");
            var od = A[i][36].split("-");
            var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
            if (D[1] != -1) {
                var tempTr = document.getElementById("tr1_" + A[i][0]);
                if (tempTr.style.display == "none")
                    continue;
                if (ot2 > nt2) {
                    MovePlace(A[i][0], D[0]);
                    break;
                }
            }
        }
    }
}
function InitScheduleData() {
    tempA = new Array();
    tempA = tempA.concat(A);
}
function MoveToTopBottom(newPos) {
    var currentIndex = 0;
    var newIndex = 0;

    for (var i = 1; i <= matchcount; i++) {//找到最后一个置顶联赛赛事对象的下标
        var obj = A[i];
        if (topLeagueIds.indexOf("," + obj[45] + ",") == -1)
            break;
        newIndex++;
    }
    for (var i = 1; i <= matchcount; i++) {//找到当前对象的下标
        var obj = A[i];
        if (newPos == obj[0]) {
            currentIndex = i;
            break;
        }
    }
    if (currentIndex != newIndex) {
        var oldPos = A[newIndex][0];
        A.splice(newIndex, 0, A.splice(currentIndex, 1)[0]);//赛事数组对象位置调整，，放在最后一个置顶联赛赛事的后面
        MovePlace2(oldPos, newPos);//页面元素位置调整，放在最后一个置顶联赛赛事的后面
    }
}
//获取完场赛事赢赔率的着色
function GetFinishWinOddsColor(scheduleObj,oddsObj) {
    var letGoalResult = 1;//0主胜，1平手，2客胜
    var totalResult = 1;//0大球，1平手，2小球
    var europeResult = 3;//0胜，1平，2负，3不处理
    if (scheduleObj[13] == "-1") {
        var homeSocre = parseInt(scheduleObj[14]);
        var guestScore = parseInt(scheduleObj[15]);
        var letGoal = parseFloat(oddsObj[2]);
        var totalGoal = parseFloat(oddsObj[10]);
        //让球
        if (homeSocre - letGoal > guestScore)
            letGoalResult = 0;
        else if (homeSocre - letGoal < guestScore)
            letGoalResult = 2;
        //大小
        if (homeSocre + guestScore > totalGoal)
            totalResult = 0;
        else if (homeSocre + guestScore < totalGoal)
            totalResult = 2;
        //1x2
        if (homeSocre > guestScore)
            europeResult = 0;
        else if (homeSocre == guestScore)
            europeResult = 1;
        else
            europeResult = 2;
    }
    var obj = new Object();
    obj.letgoal = letGoalResult;
    obj.total = totalResult;
    obj.europe = europeResult;
    return obj;
}
var lastLockTime = Date.now();
document.addEventListener('visibilitychange', function () {
    try {
        if (document.hidden) {
            lastLockTime = Date.now();
        } else {
            // 页面被激活，执行相应操作
            var currTime = Date.now();
            //console.log('页面被激活！当前时间：' + new Date() + "   时间差：" + (currTime - lastLockTime) / 1000 + "秒");
            if (currTime - lastLockTime > 600000)//超过10分钟
            {
                window.location.reload();
                //console.log('页面被激活！当前时间：' + currTime + "   时间差：" + (currTime - lastLockTime) / 60000) + "分钟";
            }
        }
    }
    catch (e) {
        console.log(e);
    }
});
function enCookieSchedule(ids) {
    var tempIds = "_";
    var arrIds = ids.split('_');
    for (var i = 0; i < arrIds.length; i++) {
        var id = arrIds[i];
        if (id == "") continue;
        if (localStorageEnable)
            tempIds += parseInt(id).toString(36) + "_";           
        else
            tempIds += parseInt(id.substring(1)).toString(36) + "_";
    }
    return tempIds;
}
function deCookieSchedule(ids) {
    var tempIds = "_";
    var arrIds = ids.split('_');
    for (var i = 0; i < arrIds.length; i++) {
        var id = arrIds[i];
        if (id == "") continue;
        if (!isNaN(id)) {
            tempIds = ids;
            break;
        }
        if (localStorageEnable)
            tempIds += parseInt(id, 36).toString() + "_";
        else
            tempIds += "2" + parseInt(id, 36).toString() + "_";
    }
    return tempIds;
}
function GetTopImg() {
    var topImgHttp = zXmlHttp.createRequest();
    topImgHttp.open("get", "/CommonInterface.ashx?type=5", false);
    topImgHttp.send(null);
    var str = topImgHttp.responseText;
    if (str != "") {
        var arr = str.split('^');
        document.getElementById("topImg").innerHTML = '<a href="' + arr[1] + '" target="_blank" class="topAdv"><img src="' + arr[0] + '" alt=""  /></a>';
        document.getElementById("topImg").style.display = "";
    }
}

