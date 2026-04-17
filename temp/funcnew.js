function changeVs2(t) {
    Config.oldOrNew = t;
    Config.writeCookie();
    showVs2();
}

function showVs2() {
    $_Our("chec_vsOld").checked = (Config.oldOrNew == 0 ? true : false);
    $_Our("chec_vsNew").checked = (Config.oldOrNew == 1 ? true : false);
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
        init_halfAllSection("h", "h_l");
        init_halfAllSection("a", "a_l");
        init_halfAllSection("h2", "h2_l");
        init_halfAllSection("a2", "a2_l");
    }
    else {
        init("hn");
        init("an");
        init_league('hn');
        init_league('an');
    }
}
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (elt /*, from*/) {
        var len = this.length >>> 0;
        var from = Number(arguments[1]) || 0;
        from = (from < 0) ? Math.ceil(from) : Math.floor(from);
        if (from < 0)
            from += len;
        for (; from < len; from++) {
            if (from in this &&
                this[from] === elt)
                return from;
        }
        return -1;
    };
}
function changePK(showLetGoal) {
    $_Our("chec_pkLetGoal").checked = showLetGoal;
    $_Our("chec_pkTotalScore").checked = !showLetGoal;
    if (showLetGoal) {
        $_Our("TeamPk_letGoal_h").style.display = "";
        $_Our("TeamPk_letGoal_g").style.display = "";
        $_Our("TeamPk_totalScore_h").style.display = "none";
        $_Our("TeamPk_totalScore_g").style.display = "none";
    }
    else {
        $_Our("TeamPk_totalScore_h").style.display = "";
        $_Our("TeamPk_totalScore_g").style.display = "";
        $_Our("TeamPk_letGoal_h").style.display = "none";
        $_Our("TeamPk_letGoal_g").style.display = "none";
    }
}
String.prototype.splice = function (start, newStr) {
    return this.slice(0, start) + newStr + this.slice(start);
};
/*2014-03-03创立，新分析页面需要用到的JS*/
/****/
var adList = ",4,7,9,12,16,,23,";
var oHttp = zXmlHttp.createRequest();
//改变指数显示或隐藏后是否第一次加载文件
var oddsLoad1 = true;
var oddsLoad2 = true;
var AnalysisObj = {
    cookieName: "analysis_setNew",
    sortCookieName:"analysis_sort",
    list: new Array(), //页面上显示的块，有顺序的
    selectedList: null,//用户设置的方案
    companyIDList: new Array(), //即时赔率比较显示的赔率公司，有顺序的
    cmpList: new Array(),
    isLogin: false,
    idchange: 0, //当更新数据就+1
    rightSetItems: lang == 1 ? new Array("指數", "球隊", "歷史", "概率", "情報") : new Array("指数", "球队", "历史", "概率", "情报"),
    //setItemNames: lang == 1 ? [["即時指數", "指數比較", "Crow*指數"], ["積分排名", "數據對比", "陣容情況", "球員評分", "賽前積分"], ["對賽往績", "近期戰績", "盤路走勢", "相同讓球", "賽前情報"], ["入球分布", "半/全場", "进球数/單雙", "進球時間", "數據比較"], ["媒體預測", "未來五場"]] : [["即时指数", "指数比较", "Crow*指数"], ["积分排名", "数据对比", "阵容情况", "球员评分", "赛前积分"], ["对赛往绩", "近期战绩", "盘路走势", "相同让球", "赛前情报"], ["入球分布", "半/全场", "进球数/单双", "进球时间", "数据比较"], ["媒体预测", "未来五场"]],
    setItemNames: lang == 1 ? ["即時指數", "指數比較", "Crow*指數", "競足數據", "積分排名", "數據對比", "裁判統計", "陣容情況", "球員評分", "賽前積分", "對賽往績", "近期戰績", "盤路走勢", "相同讓球", "入球分布", "半/全場", "进球数/單雙", "進球時間", "數據比較", "賽前簡報", "未來五場"] : ["即时指数", "指数比较", "Crow*指数", "竞足数据", "积分排名", "数据对比","裁判统计", "阵容情况", "球员评分", "赛前积分", "对赛往绩", "近期战绩", "盘路走势", "相同让球", "入球分布", "半/全场", "进球数/单双", "进球时间", "数据比较", "赛前简报", "未来五场"],
    //setIteamIndexs: [["0", "1", "2"], ["5,6", "11", "21", "28", "29"], ["8", "10", "13", "14", "24"], ["15", "17", "18", "19", "26"], ["25", "20"]],
    setIteamIndexs: ["0", "1", "2", "30","5,6", "11","22", "21", "28", "29","8", "10", "13", "14","15", "17", "18", "19", "26","25", "20"],
    setItemList: new Array(),
    itemSort: "0^1^2^30^5,6^11^22^21^28^29^8^10^13^14^15^17^18^19^26^25^20",
    selectAllSet: function () {
        var inputs = document.getElementById("mySet").getElementsByTagName("li");
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].className = "on";
        }
    },
    selectInvertSet: function () {
        var inputs = document.getElementById("mySet").getElementsByTagName("li");
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].className = inputs[i].className == "on" ? "hided" : "on";
        }
    },
    saveSet: function () {
        this.list = new Array();
        var inputs = document.getElementById("mySet").getElementsByTagName("li");
        this.itemSort = "";
        for (var i = 0; i < inputs.length; i++) {
            var val = inputs[i].getAttribute("v");
            this.itemSort += "^" + val;
            if (inputs[i].className != "on") continue;           
            this.list.push(inputs[i].className == "on" ? val : "");
            if (val == "0" || val == "3")//加上内推
                this.list.push(val == "0" ? "4" : "7");
            if (val == "0") oddsLoad1 = true;
            if (val == "1") oddsLoad2 = true;
        }
        this.itemSort = this.itemSort.substring(1);
        writeCookie(this.sortCookieName, this.itemSort);
        AnalysisObj.update();
        AnalysisObj.init();
        Popup.getInstanceById('openNew-container-set').close();
    },
    checkSet: function (obj,e) {
        obj.parentNode.className = obj.parentNode.className == "hided" ? "on" : "hided";
        e.stopPropagation();
    },
    createSetView: function () {
        if ($_Our("bt_add_div")) {
            if (!$_Our("mySet")) $_Our("bt_add_div").innerHTML = '<div id="mySet">';//popupBox            
            var html = "";
            var setOrder = 0;
            //新版定制                      
            html += '<ul class="yScroll' + (lang==1?" big":"")+'" id="choose_right">';
            var tempSortArr = this.itemSort.split('^');
            this.setItemList.sort((prev, next) => {
                return tempSortArr.indexOf(prev.id) - tempSortArr.indexOf(next.id)
            });
            for (var i = 0; i < this.setItemList.length; i++) {
                var obj = this.setItemList[i];
                html += '<li id="v' + setOrder + '" v="' + obj.id + '" class="' + (this.list.indexOf(obj.id) != -1 ? "on" : "hided") + '">';
                html += '<span class="drag"><img src="/images/font-choice.png" style="float:left;">';
                html += obj.name+"</span>";
                html += '<div class="rightBlock" onclick="AnalysisObj.checkSet(this,event)"></div>'
                html += '</li>';
                setOrder++;
            }
            html += '</ul>';
            //旧版定制
            //for (var i = 0; i < this.rightSetItems.length; i++) {
            //    html += '<ul class="line">';
            //    html += '<font class="T">' + this.rightSetItems[i] + '：</font>';
            //    for (var j = 0; j < this.setItemNames[i].length; j++) {
            //        html += '<li' + (this.list.indexOf(this.setIteamIndexs[i][j]) != -1 ? " class=\"on\"" : "") + '><input' + (this.list.indexOf(this.setIteamIndexs[i][j]) != -1 ? " checked " : "") + ' type="checkbox" onclick="AnalysisObj.checkSet(this)"  id="mySet_' + setOrder + '" value="' + this.setIteamIndexs[i][j] + '">';
            //        html += ' <label style="cursor:pointer" for="mySet_' + setOrder + '"><font>' + this.setItemNames[i][j] + '</font></label>';
            //        html += '</li>';
            //        setOrder++;
            //    }
            //    html += '</ul>';
            //}
            $_Our("mySet").innerHTML = html + '<div class="bts"><input type="button" value="全选" onclick="AnalysisObj.selectAllSet()"><input type="button" value="反选" onclick="AnalysisObj.selectInvertSet()"><input type="button" value="重置" onclick="AnalysisObj.ReSet();"><input type="button" value="确定" onclick="AnalysisObj.saveSet();"></div>';
            //<input type="button" value="取消" onclick="Popup.getInstanceById(\'openNew-container-set\').close();">
        }
        openSetting();
    },
    init: function () {
        this.selectedList = getCookie(this.cookieName);
        if (this.selectedList == null || this.selectedList == "") {
            this.selectedList = "4#7#30#5,6#11#20#21#28#29#8#10#13#14#15#17#18#19#26#25#20";//"0#4#1#2#3#7#5,6#11#21#28#8#10#13#14#15#17#18#19#26#22#24#25#20";
            //默认显示的赔率公司
            this.selectedList += "^3#1#8#12#4";
        }
        else {
            var temp = this.selectedList.split('^');
            if (temp.length == 2) {
                this.selectedList = temp[0].replace("#3#", "#");
                this.selectedList += "^" + temp[1];
            }
            else {
                this.selectedList = this.selectedList.replace("#3#", "#");
            }
        }
        var tempSort = getCookie(this.sortCookieName);
        if (tempSort != null && tempSort != "")
            this.itemSort = tempSort;
        this.setItemList = new Array();
        for (var i = 0; i < this.setItemNames.length; i++) {
            this.setItemList.push({ id: this.setIteamIndexs[i], name: this.setItemNames[i]});
        }
        var tempSortArr = this.itemSort.split('^');
        this.setItemList.sort((prev, next) => {
            return tempSortArr.indexOf(prev.id) - tempSortArr.indexOf(next.id)
        });
        this.initWith(this.selectedList);
        this.porlet();
    },
    initWith: function (str) {
        this.list = new Array();
        this.companyIDList = new Array();
        if (str && str != "") {
            var strList = str.split('^');
            this.list = strList[0].split('#');
            if (strList.length >= 2) {
                this.companyIDList = strList[1].split('#');
            }
        }
    },
    update: function () {
        //var oristr = getCookie(this.cookieName);
        var str = this.list.join("#") + "^" + this.companyIDList.join("#");
        writeCookie(this.cookieName, str);
        if (this.selectedList != str) {
            this.selectedList = str;
            this.idchange += 1;
        }
    },
    porlet: function () {//显示
        var tmpListStr = "," + this.list.join(",") + ",";
        var listTmp = this.list.join(",").split(',');
        var sortTmp = this.itemSort.split('^');
        listTmp = this.sortArrayByAnotherArray(listTmp, sortTmp);
        var right_floatHTML = "<a class='rf on' href='javascript:void(0);' onclick='openSetting();return false;'>定制</a>";//<i class='tag'>VIP</i>
        for (var i = 0; i < listTmp.length; i++) {
            if ($_Our("porlet_" + listTmp[i])) {
                var curNode = $_Our("porlet_" + listTmp[i]);
                $_Our("porletP_Group").removeChild(curNode);
                $_Our("porletP_Group").appendChild(curNode);
                if (listTmp[i] == "0" && oddsLoad1) {
                    var allDate = document.getElementById("allDate");
                    if (allDate != null) {
                        oddsLoad1 = false;
                        var s = document.createElement("script");
                        s.type = "text/javascript";
                        s.charset = "gb2312";
                        s.src = "//live.titan007.com/jsData/" + scheduleID.toString().substr(0, 2) + "/" + scheduleID.toString().substr(2, 2) + "/" + scheduleID + ".js?" + Date.parse(new Date());
                        allDate.removeChild(allDate.firstChild);
                        allDate.appendChild(s, "script");

                    }
                }
                else if (listTmp[i] == "1" && oddsLoad2) {
                    oddsLoad2 = false;
                    window.clearTimeout(oddstimer);
                    oddstimer = window.setTimeout("loadData()", 30000);
                }
                curNode.style.display = "";
                curNode.onmousemove = function () {
                    var obj = this.getElementsByTagName("h2")[0];
                    if (typeof (obj) != "undefined") {
                        var spans = obj.getElementsByTagName("div")[0].getElementsByTagName("span");
                        for (var kk = 0; kk < spans.length; kk++) {
                            spans[kk].style.display = "block";
                        }
                    }
                    //console.log("onmousemove:"+spans.length);
                }
                curNode.onmouseout = function () {
                    var obj = this.getElementsByTagName("h2")[0];
                    if (typeof (obj) != "undefined") {
                        var spans = obj.getElementsByTagName("div")[0].getElementsByTagName("span");
                        for (var kk = 0; kk < spans.length; kk++) {
                            spans[kk].style.display = "none";
                        }
                    }
                }
            }
        }

        for (var i = 0; i < 31; i++) {
            if ($_Our("porlet_" + i) && tmpListStr.indexOf("," + i + ",") == -1)
                $_Our("porlet_" + i).style.display = "none";
        }

        showAndHide();

        setTimeout("AnalysisObj.rightSet()", 100);
    },
    rightSet: function () {
        var rightList = new Array(), rightPosList = new Array();
        //for (var i = 0; i < this.list.length; i++) {
        //    for (var j = 0; j < this.rightSetItems.length; j++) {
        //        if (rightList.indexOf(j) == -1 && this.setIteamIndexs[j].indexOf(this.list[i]) != -1) {
        //            rightList.push(j);
        //            rightPosList.push(this.list[i]);
        //        }
        //    }
        //}
        var right_floatHTML = "<a class='rf on' href='javascript:void(0);' onclick='AnalysisObj.createSetView();return false;'>定制</a>";//<i class='tag'>VIP</i>
        //for (var i = 0; i < rightList.length; i++) {
        //    right_floatHTML += "<a class='rf' href='#' onclick='window.location.hash =\"#porlet_" + rightPosList[i].split(',')[0] + "\";window.location = window.location;resePos();return false;'>" + this.rightSetItems[rightList[i]] + "</a>";
        //}
        $_Our("right_float").innerHTML = right_floatHTML;
    },
    ReSet: function () {
        var html = "";
        var setOrder = 0;
        for (var i = 0; i < this.setItemNames.length; i++) {
            html += '<li id="v' + setOrder + '" v="' + this.setIteamIndexs[i] + '" class="on"' + '">';
            html += '<img src="/images/font-choice.png" style="float:left;">';
            html += this.setItemNames[i];
            html += '<div class="rightBlock" onclick="AnalysisObj.checkSet(this,event)"></div>'
            html += '</li>';
            setOrder++;
        }
        document.getElementById("choose_right").innerHTML = html;
    },
    sortArrayByAnotherArray: function (arr, sortArr) {
        const sortedMap = sortArr.map((value, index) => [value, index])
            .sort((a, b) => a[0] - b[0])
            .reduce((acc, [k, v]) => ({ ...acc, [k]: v }), {});
        arr.sort((a, b) => sortedMap[a] - sortedMap[b]);
        return arr;
    }
};
//AnalysisObj.load();
AnalysisObj.init();

function resePos() {
    setTimeout("changePostion()", 100);
}

/**赔率公司定制**/
function addOddsCmp() {
    if ($_Our("bt_add_div")) {
        if (!$_Our("addOddsCmp_id")) $_Our("bt_add_div").innerHTML = "<div id='addOddsCmp_id'></div>";
        var html = "";
        for (var i = 0; i < AnalysisObj.cmpList.length; i += 2) {
            var isShow = false;
            for (var k = 0; k < AnalysisObj.companyIDList.length; k++) {
                if (AnalysisObj.companyIDList[k] == AnalysisObj.cmpList[i]) {
                    isShow = true;
                    break;
                }
            }
            html += "<span class='" + (isShow ? "odds_checked" : "odds_unchecked") + "' onclick='checkOCompany(this)'><input readonly type='checkbox'" + (isShow ? " checked" : "") + " name='oddscmp' value='" + AnalysisObj.cmpList[i] + "'>" + AnalysisObj.cmpList[i + 1] + "</span>";
        }

        $_Our("addOddsCmp_id").innerHTML = "<div>" + html + "</div><div class=\"bts\"><input type='button' value='确 定' onclick='submitOddsCmp()' ><input type='button' value='取 消' onclick=\"Popup.getInstanceById('openNew-container-company').close();\" ></div>";
    }
    Popup.init({ target: Popup.create('openNew-container-company', '赔率公司定制', 'addOddsCmp_id', 480), drag: true, resize: false, autoOpen: true, createOverlay: true, autoLayout: false });
}

function submitOddsCmp() {
    AnalysisObj.companyIDList = new Array();
    var oddscmpList = document.getElementsByName("oddscmp");
    for (var i = 0; i < oddscmpList.length; i++) {
        if (oddscmpList[i].checked) {
            AnalysisObj.companyIDList.push(oddscmpList[i].value);
        }
    }
    reDisplayCmp();
    AnalysisObj.update();

    Popup.getInstanceById('openNew-container-company').close();
}

function checkOCompany(obj) {
    var isChecked = obj.className == "odds_checked";
    obj.getElementsByTagName("input")[0].checked = !isChecked;
    obj.className = (!isChecked ? "odds_checked" : "odds_unchecked");
}

function hidOddsCmp(cmpID) {
    for (var i = 0; i < AnalysisObj.companyIDList.length; i++) {
        if (AnalysisObj.companyIDList[i] == cmpID) {
            AnalysisObj.companyIDList.splice(i, 1);
            break;
        }
    }
    reDisplayCmp();
}

function reDisplayCmp() {
    for (var i = 0; i < AnalysisObj.cmpList.length; i += 2) {
        var isShow = false;
        for (var k = 0; k < AnalysisObj.companyIDList.length; k++) {
            if (AnalysisObj.companyIDList[k] == AnalysisObj.cmpList[i]) {
                isShow = true;
                break;
            }
        }
        $_Our("tr_o_1_" + AnalysisObj.cmpList[i]).style.display = (isShow ? "" : "none");
        try {
            $_Our("tr_o_2_" + AnalysisObj.cmpList[i]).style.display = (isShow ? "" : "none");
        }
        catch (e) { }
        try {
            $_Our("tr_o_3_" + AnalysisObj.cmpList[i]).style.display = (isShow ? "" : "none");
        }
        catch (e) { }
    }
}

//从odds读取回来的页面数据显示
function oddsComp() {
    var nods = $_Our("iframeA").childNodes;
    for (var c = 0; c < 3; c++) {//nods.length
        var theTag = nods[c];
        if (c == 0) {
            if (!theTag || theTag.getAttribute("id") != "iframeAOdds") continue;

            var allCompOdds = new Array();
            var ll = theTag.value.split("^");
            for (var i = 0; i < ll.length; i++) {
                allCompOdds.push(ll[i].split(';'));
            }
            var oddsCheck = getCookie("oddsCompShow");
            var checkB = true; var checkReal = true; var checkRun = true;
            if (oddsCheck != null && oddsCheck != "undefined" && oddsCheck != "") {
                var arrCheck = oddsCheck.split('_');
                checkB = arrCheck[0] == "1";
                checkReal = arrCheck[1] == "1";
                checkRun = arrCheck[2] == "1";
            }
            var checkHtml = '<input id="compCheck_0" type="checkbox"' + (checkB ? 'checked="checked"' : '') + ' onclick="checkOddsComp();"><label>初</label>';
            checkHtml += '<input id="compCheck_1" type="checkbox"' + (checkReal ? 'checked="checked"' : '') + ' onclick="checkOddsComp();"><label>即时</label>';
            checkHtml += '<input id="compCheck_2" type="checkbox"' + (checkRun ? 'checked="checked"' : '') + ' onclick="checkOddsComp();"><label>滚球</label>';
            var html = '<h2 class=fx_title2>即时走势比较' + checkHtml + '</h2><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd"><tbody><tr height="20" bgcolor="#FDEFD2"><td rowspan="2" width="8%" height="24">公司</td><td rowspan="2" width="32"></td><td colspan="3" bgcolor="#F0F2F4">欧洲指数</td><td colspan="3" bgcolor="#F0F2F4">欧转亚盘</td><td colspan="3" bgcolor="#F0F2F4">实际最新亚盘</td><td colspan="3" bgcolor="#F0F2F4">进球数</td><td rowspan="2" width="30">变化</td><td rowspan="2" width="25" style="cursor:pointer;" onclick="addOddsCmp()"><img src="/images/fx.jpg" title="增加公司"></td></tr>'
                + '<tr bgcolor="#FDEFD2" height="20"><td width="7%">主胜</td><td width="7%">和局</td><td width="7%">客胜</td><td width="6%">主队</td><td width="10%">亚让</td><td width="6%">客队</td><td width="6%">主队</td><td width="10%">亚让</td><td width="6%">客队</td><td width="6%">大球</td><td width="6%">盘口</td><td width="6%">小球</td></tr>';

            //Crown  初	1.60	3.60	4.55	0.90	半/一	0.95	1.85	0.85	半/一	1.01	1.86	0.99	2.5/3	0.85	
            //var allCompOdds = [["3","SB","1.60,3.60,4.55,0.90,半/一,0.95,1.85,0.85,半/一,1.01,1.86,0.99,2.5/3,0.85","1.45,4.10,5.35,0.90,一球,0.95,1.85,0.32,平手,2.00,2.32,3.33,4.5,0.10"],["...","...","...","..."]];
            if (checkB || checkReal || checkRun) {
                AnalysisObj.cmpList = new Array();
                for (var i = 0; i < allCompOdds.length; i++) {
                    var odds = allCompOdds[i];
                    AnalysisObj.cmpList.push(odds[0]);
                    AnalysisObj.cmpList.push(odds[1]);
                    var addCss = "display:none;";
                    var hasRunodds = false;
                    for (var k = 0; k < AnalysisObj.companyIDList.length; k++) {
                        if (AnalysisObj.companyIDList[k] == odds[0]) {
                            addCss = "";
                            break;
                        }
                    }
                    if (odds.length > 2) {
                        var tdNum = 0;
                        var o1 = odds[2].split(',');
                        var o2 = odds[3].split(',');
                        var o3;
                        if (checkB) tdNum++;
                        if (checkReal) tdNum++;
                        if (checkRun) tdNum++;
                        if (odds.length > 4) {
                            o3 = odds[4].split(',');
                            if (typeof (o3[0]) != "undefined" && o3[0] != "" && checkRun) {
                                hasRunodds = true;
                            }
                        }
                        if (tdNum == 1) {
                            var tempOdds = checkB ? o1 : (checkReal ? o2 : o3);
                            var tempType = checkB ? "初" : (checkReal ? "即时" : "滚球");
                            if (checkReal && hasRunodds)
                                tempType = "终";
                            if (checkReal || checkB || (checkRun && hasRunodds))
                                html += '<tr bgcolor="#FFFFFF" style="height:20px;color:#666;' + addCss + '" id="tr_o_1_' + odds[0] + '"><td rowspan="' + tdNum + '" class="companyBg"><b>' + odds[1] + '</b></td><td><font color="#555555">' + tempType + '</font></td><td bgcolor="#E8F2FF">' + tempOdds[0] + '</td><td bgcolor="#E8F2FF">' + tempOdds[1] + '</td><td bgcolor="#E8F2FF">' + tempOdds[2] + '</td><td bgcolor="#FDFCCC">' + tempOdds[3] + '</td><td bgcolor="#FDFCCC">' + tempOdds[4] + '</td><td bgcolor="#FDFCCC">' + tempOdds[5] + '</td><td>' + tempOdds[7] + '</td><td>' + tempOdds[8] + '</td><td>' + tempOdds[9] + '</td><td bgcolor="#E8F2FF">' + tempOdds[11] + '</td><td bgcolor="#E8F2FF">' + tempOdds[12] + '</td><td bgcolor="#E8F2FF">' + tempOdds[13] + '</td><td rowspan="' + tdNum + '"><a href="//vip.titan007.com/changeDetail/handicap.aspx?id=' + scheduleID + '&companyID=' + odds[0] + '" target="_blank">详</a></td><td rowspan="' + tdNum + '" style="cursor:pointer;" onclick="hidOddsCmp(' + odds[0] + ')"><img src="/images/sub.jpg" title="隐藏该公司"></td></tr>';
                        } else {
                            if (tdNum == 2) {
                                var hasSecond = false;
                                var rowSpan = 1;
                                var tempOdds1 = "", tempOdds2 = "", tempType1 = "", tempType2 = "";
                                if (checkB && checkReal) {
                                    tempOdds1 = o1;
                                    tempOdds2 = o2;
                                    tempType1 = "初";
                                    tempType2 = hasRunodds ? "终" : "即时";
                                    hasSecond = true;
                                    rowSpan = 2;
                                }
                                else {
                                    if (checkB && checkRun) {
                                        tempOdds1 = o1;
                                        if (hasRunodds) {
                                            tempOdds2 = o3;
                                            hasSecond = true;
                                            rowSpan = 2;
                                            tempType2 = "滚球";
                                        }
                                        tempType1 = "初";
                                    }
                                    else {
                                        if (checkReal && checkRun) {
                                            tempOdds1 = o2;
                                            if (hasRunodds) {
                                                tempOdds2 = o3;
                                                hasSecond = true;
                                                rowSpan = 2;
                                                tempType2 = "滚球";
                                            }
                                            tempType1 = hasRunodds ? "终" : "即时";
                                        }
                                    }
                                }
                                html += '<tr bgcolor="#FFFFFF" style="height:20px;color:#666;' + addCss + '" id="tr_o_1_' + odds[0] + '"><td rowspan="' + rowSpan + '" class="companyBg"><b>' + odds[1] + '</b></td><td><font color="#555555">' + tempType1 + '</font></td><td bgcolor="#E8F2FF">' + tempOdds1[0] + '</td><td bgcolor="#E8F2FF">' + tempOdds1[1] + '</td><td bgcolor="#E8F2FF">' + tempOdds1[2] + '</td><td bgcolor="#FDFCCC">' + tempOdds1[3] + '</td><td bgcolor="#FDFCCC">' + tempOdds1[4] + '</td><td bgcolor="#FDFCCC">' + tempOdds1[5] + '</td><td>' + tempOdds1[7] + '</td><td>' + tempOdds1[8] + '</td><td>' + tempOdds1[9] + '</td><td bgcolor="#E8F2FF">' + tempOdds1[11] + '</td><td bgcolor="#E8F2FF">' + tempOdds1[12] + '</td><td bgcolor="#E8F2FF">' + tempOdds1[13] + '</td><td rowspan="' + rowSpan + '"><a href="//vip.titan007.com/changeDetail/handicap.aspx?id=' + scheduleID + '&companyID=' + odds[0] + '" target="_blank">详</a></td><td rowspan="' + rowSpan + '" style="cursor:pointer;" onclick="hidOddsCmp(' + odds[0] + ')"><img src="/images/sub.jpg" title="隐藏该公司"></td></tr>';
                                if (hasSecond)
                                    html += '<tr bgcolor="#FFFFF0" style="' + addCss + '" class="odds" id="tr_o_2_' + odds[0] + '"><td><font color="#555555">' + tempType2 + '</font></td><td bgcolor="#E8F2FF">' + tempOdds2[0] + '</td><td bgcolor="#E8F2FF">' + tempOdds2[1] + '</td><td bgcolor="#E8F2FF">' + tempOdds2[2] + '</td><td bgcolor="#FDFCCC">' + tempOdds2[3] + '</td><td bgcolor="#FDFCCC">' + tempOdds2[4] + '</td><td bgcolor="#FDFCCC">' + tempOdds2[5] + '</td><td>' + tempOdds2[7] + '</td><td>' + tempOdds2[8] + '</td><td>' + tempOdds2[9] + '</td><td bgcolor="#E8F2FF">' + tempOdds2[11] + '</td><td bgcolor="#E8F2FF">' + tempOdds2[12] + '</td><td bgcolor="#E8F2FF">' + tempOdds2[13] + '</td></tr>';
                            }
                            else {
                                var rowSpan = (hasRunodds ? 3 : 2);
                                html += '<tr bgcolor="#FFFFFF" style="height:20px;color:#666;' + addCss + '" id="tr_o_1_' + odds[0] + '"><td rowspan="' + rowSpan + '" class="companyBg"><b>' + odds[1] + '</b></td><td><font color="#555555">初</font></td><td bgcolor="#E8F2FF">' + o1[0] + '</td><td bgcolor="#E8F2FF">' + o1[1] + '</td><td bgcolor="#E8F2FF">' + o1[2] + '</td><td bgcolor="#FDFCCC">' + o1[3] + '</td><td bgcolor="#FDFCCC">' + o1[4] + '</td><td bgcolor="#FDFCCC">' + o1[5] + '</td><td>' + o1[7] + '</td><td>' + o1[8] + '</td><td>' + o1[9] + '</td><td bgcolor="#E8F2FF">' + o1[11] + '</td><td bgcolor="#E8F2FF">' + o1[12] + '</td><td bgcolor="#E8F2FF">' + o1[13] + '</td><td rowspan="' + rowSpan + '"><a href="//vip.titan007.com/changeDetail/handicap.aspx?id=' + scheduleID + '&companyID=' + odds[0] + '" target="_blank">详</a></td><td rowspan="' + rowSpan + '" style="cursor:pointer;" onclick="hidOddsCmp(' + odds[0] + ')"><img src="/images/sub.jpg" title="隐藏该公司"></td></tr>';
                                html += '<tr bgcolor="#FFFFF0" style="' + addCss + '" class="odds" id="tr_o_2_' + odds[0] + '"><td><font color="#555555">' + (hasRunodds ? "终" : "即时") + '</font></td><td bgcolor="#E8F2FF">' + o2[0] + '</td><td bgcolor="#E8F2FF">' + o2[1] + '</td><td bgcolor="#E8F2FF">' + o2[2] + '</td><td bgcolor="#FDFCCC">' + o2[3] + '</td><td bgcolor="#FDFCCC">' + o2[4] + '</td><td bgcolor="#FDFCCC">' + o2[5] + '</td><td>' + o2[7] + '</td><td>' + o2[8] + '</td><td>' + o2[9] + '</td><td bgcolor="#E8F2FF">' + o2[11] + '</td><td bgcolor="#E8F2FF">' + o2[12] + '</td><td bgcolor="#E8F2FF">' + o2[13] + '</td></tr>';
                                if (hasRunodds) {
                                    html += '<tr bgcolor="#FFFFF0" style="' + addCss + '" class="odds" id="tr_o_3_' + odds[0] + '"><td style="font-weight:normal;color:red;">滚球</td><td bgcolor="#E8F2FF">' + (o2[1] != o3[1] ? o3[0] : "") + '</td><td bgcolor="#E8F2FF">' + (o2[1] != o3[1] ? o3[1] : "") + '</td><td bgcolor="#E8F2FF">' + (o2[1] != o3[1] ? o3[2] : "") + '</td>  <td bgcolor="#FDFCCC"></td>  <td bgcolor="#FDFCCC"> </td>  <td bgcolor="#FDFCCC"></td> <td>' + o3[7] + '</td><td>' + o3[8] + '</td><td>' + o3[9] + '</td><td bgcolor="#E8F2FF">' + o3[11] + '</td><td bgcolor="#E8F2FF">' + o3[12] + '</td><td bgcolor="#E8F2FF">' + o3[13] + '</td></tr>';
                                }
                            }
                        }

                    }
                }
            }
            html += '</tbody></table>';

            $_Our("porlet_" + (c + 1)).innerHTML = html;
        }
        else //console.log(theTag.innerHTML);
        {
            if (c == 1)
                theTag.innerHTML = theTag.innerHTML.replace("Crown全指数", "Crow*全指数").replace('<tbody><tr class="bui" bgcolor="#ECF4FB"><td width="68" rowspan="2" bgcolor="#EAEDEE"><b>罚球数</b></td><td height="21" colspan="3">标准盘</td><td colspan="3">亚让</td><td colspan="3">进球数</td>', '<tbody><tr class="bui" bgcolor="#ECF4FB"><td width="68" rowspan="2" bgcolor="#EAEDEE"><b>罚牌数</b></td><td height="21" colspan="3">标准盘</td><td colspan="3">亚让</td><td colspan="3">总牌数</td>').replace("罚球数","罚牌数");
            $_Our("porlet_" + (c + 1)).innerHTML = theTag.innerHTML;
            nods[c].style.display = "none";
        }
    }
    //$_Our("iframeA").innerHTML = "";
    //showAndHide();
    AnalysisObj.porlet();
}

/**页面上的板块**/
function openSetting() {
    //Popup.init({ target: Popup.create('openNew-container-setting' + AnalysisObj.idchange, '分析数据定制', '/ASetting.aspx?', 550, 500), drag: true, resize: true, autoOpen: true, createOverlay: true, autoLayout: false });
    Popup.init({ target: Popup.create('openNew-container-set', '分析数据定制', 'mySet', 500), drag: true, resize: false, autoOpen: true, createOverlay: true, autoLayout: false });
    try {
        //$("#choose_right").dragsort({ dragSelectorExclude: "div" });
        $("#choose_right").dragsort();
    }
    catch (e) {
        console.log(e);
    }
}
function openLnk(sid) {
    if (location.href.toLowerCase().indexOf("_big") != -1)
        location.href = "/analysis/" + sid + "_big.htm";
    else
        location.href = "/analysis/" + sid + ".htm";
}

//页面那些板块的显隐藏
function showAndHide() {
    //读取设置，控制显示
    for (var i = 0; i < 31; i++) {
        if (i == 29) continue;
        if ($_Our("porlet_" + i)) {
            //console.log("porlet_"+i);
            var tagH2 = $_Our("porlet_" + i).getElementsByTagName("h2");
            if (tagH2.length > 0) {
                if (tagH2[0].innerHTML.indexOf("porlet_right") <= 0) {
                    var html = "<div class='porlet_right'><span class='porlet_close' title='关闭' onclick='r_close(" + i + ")'></span></div>" + tagH2[0].innerHTML;//<span class='porlet_down' title='下移' onclick='r_down("+i+")'></span><span class='porlet_up' title='上移' onclick='r_up("+i+")'></span>
                    tagH2[0].innerHTML = html;//float:right的标签要放在前面
                }
            }
        }
    }
}
//showAndHide();
function r_up(index) {
    var ii = "" + index;
    for (var i = 0; i < AnalysisObj.list.length; i++) {
        if (AnalysisObj.list[i] == ii || ("," + AnalysisObj.list[i] + ",").indexOf("," + ii + ",") != -1) {
            if (i > 0) {
                var tmp = AnalysisObj.list[i - 1];
                AnalysisObj.list[i - 1] = AnalysisObj.list[i];
                AnalysisObj.list[i] = tmp;
                AnalysisObj.update();
                AnalysisObj.porlet();
                //console.log(AnalysisObj.list.join('\r\n'));
            }
            break;
        }
    }
}
function r_down(index) {
    var ii = "" + index;
    for (var i = 0; i < AnalysisObj.list.length; i++) {
        if (AnalysisObj.list[i] == ii || ("," + AnalysisObj.list[i] + ",").indexOf("," + ii + ",") != -1) {
            if (i < AnalysisObj.list.length - 1) {
                var tmp = AnalysisObj.list[i + 1];
                AnalysisObj.list[i + 1] = AnalysisObj.list[i];
                AnalysisObj.list[i] = tmp;
                AnalysisObj.update();
                AnalysisObj.porlet();
            }
            break;
        }
    }
}
function r_close(index) {
    var ii = "" + index;
    for (var i = 0; i < AnalysisObj.list.length; i++) {
        if (AnalysisObj.list[i] == ii || ("," + AnalysisObj.list[i] + ",").indexOf("," + ii + ",") != -1) {
            AnalysisObj.list.splice(i, 1);
            AnalysisObj.update();
            AnalysisObj.porlet();
            break;
        }
    }
}

/**其他方法**/
function getLeft(e) {
    var offset = e.offsetLeft;
    if (e.offsetParent != null)
        offset += getLeft(e.offsetParent);
    return offset;
}

//cookie操作
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
function writeCookie(name, value) {
    var expire = "";
    var hours = 365;
    expire = new Date((new Date()).getTime() + hours * 3600000);
    expire = ";path=/;expires=" + expire.toGMTString();
    document.cookie = name + "=" + value + expire;
}

/**重写**/
function changePostion() {
    var obj = getWidth();
    var winWidth = obj.w;
    var winHeight = obj.h;
    var analyMap = document.getElementById("analyMap");
    var top = Math.min(180, Math.max(0, obj.h - analyMap.offsetHeight) / 2);
    var widthTemp = 0;
    if (winWidth < 1080)
        widthTemp = 20;
    var doc_scrollTop = document.body.scrollTop;
    if (doc_scrollTop == 0) doc_scrollTop = document.documentElement.scrollTop;
    var isIE = !!window.ActiveXObject;
    var isIE6 = isIE && !window.XMLHttpRequest;
    if (isIE6) {
        analyMap.style.cssText = "position: absolute;top:" + (doc_scrollTop + 60) + "px;right: " + ((winWidth - 910) / 2 - 50 + widthTemp) + "px;";
    }
    else {
        var tempTop = document.getElementById("menu") != null ? 293 : 214;
        analyMap.style.cssText = "position: fixed; top:" + tempTop +"px; right: " + ((winWidth - 910) / 2 - 50 + widthTemp) + "px;";
    }
    if (document.getElementById("integralDiv") != null) {
        var topTemp = document.getElementById("menu") != null ? 313 : 234;
        if (doc_scrollTop > 200)
            topTemp = 30;
        var integralMap = document.getElementById("integralDiv");
        if (isIE6) {
            integralMap.style.cssText = "position: absolute;top:" + (doc_scrollTop + 60) + "px;left: " + ((winWidth - 910) / 2 - 50 + widthTemp) + "px;";
        }
        else {
            integralMap.style.cssText = "position: fixed; top:" + topTemp + "px; left: " + ((winWidth - 1120) / 2 - 50 + widthTemp) + "px;";
        }
    }
}
function showHeaderSocre() {
    var obj = $_Our("headVs");
    if (arrLeague[0] == 0) {
        obj.className = "row vs";
        obj.innerHTML = "VS";
    }
    else {
        var className = "";
        switch (arrLeague[0]) {
            case 1:
            case 3:
                className = "half";
                break;
            case 2:
                className = "HT";
                break;
            default:
                className = "end";
                break;
        }
        var scoreHtml = '<div class="' + className + '">';
        scoreHtml += '<div class="score">' + (arrLeague[0] < -1 ? '&nbsp;' : arrLeague[1]) + '</div>';
        if (arrLeague[0] == -1)
            scoreHtml += '<div><span class="row red b">' + getMatchState(arrLeague[0]) + '</span><span class="row">(' + arrLeague[3] + '-' + arrLeague[4] + ')</span></div>';
        else
            scoreHtml += '<div class="vs">' + getMatchState(arrLeague[0]) + '</div>';
        scoreHtml += '<div class="score gt">' + (arrLeague[0] < -1 ? '&nbsp;' : arrLeague[2]) + '</div>';
        scoreHtml += '</div>';
        obj.innerHTML = scoreHtml;
    }
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
    return arrState.length < 2 ? "" : arrState[(lang < 2 ? lang : 0)];
}
var state_ch = Array(18);
state_ch[0] = "推迟,推遲";
state_ch[1] = "中断,中斷";
state_ch[2] = "腰斩,腰斬";
state_ch[3] = "待定,待定";
state_ch[4] = "取消,取消";
state_ch[13] = "完,完";
state_ch[14] = ",";
state_ch[15] = "上半,上半";
state_ch[16] = "中,中";
state_ch[17] = "下半,下半";
state_ch[18] = "加,加";
state_ch[19] = "点,,";
function showBarUrl(id) {
    var isHideAd = (getCookie("ishidepcad") != "" && getCookie("ishidepcad") == "1");
    if (isHideAd) return;
    if (typeof (Ba_Soccer) != "undefined" && Ba_Soccer.indexOf(id) != -1) {
        var obj = document.getElementById("span_barUrl");
        if (obj != null)
            obj.innerHTML = '<a style="color:#3473C7;text-decoration:underline;font-weight: bold;" href="//ba2.titan007.com/linkmatch/1/' + id + '.html" target="_blank">详情</a>';
    }
    _spreadBaInfo.getData("/xml/position/footballanaly.txt");
}
function showDetail(id) {
    var isFromQb = getUrlParam("sd") != null && getUrlParam("sd").toLocaleLowerCase() == "1";
    var url = "//live.titan007.com/detail/" + id + (lang == 0 ? "cn" : lang == 2 ? "sb" : "") + ".htm" + (isFromQb ? "?sd=1" : "");
    window.location.href = url;
    //window.open(url);
}


function randomSort(arr) {
    try {
        arr.sort(function (a, b) {
            return Math.random() - 0.5;
        });
    } catch (e) { }
    return arr;
}

var _spreadBaInfo = new Object();
_spreadBaInfo.chargeJsonArray = new Array();
_spreadBaInfo.getData = function (filePath) {
    try {
        $.get(filePath + "?r=007" + Date.parse(new Date()), function (result) {
            var jsonArr = (typeof (JSON) != 'undefined' ? JSON.parse(result) : eval('(' + result + ')'));
            _spreadBaInfo.chargeJsonArray = randomSort(jsonArr.chargeInfo);
            $("#porlet_4").html(_spreadBaInfo.chargeInfoHtml(1));
            $("#porlet_7").html(_spreadBaInfo.chargeInfoHtml(2));
            $("#porlet_4").show();
            $("#porlet_7").show();
        });
    }
    catch (e) { }
}
_spreadBaInfo.chargeInfoHtml = function (rowIndex) {
    var returnValue = "";
    var arrayIndex = 3 * (rowIndex - 1);
    if (_spreadBaInfo.chargeJsonArray != null && typeof (_spreadBaInfo.chargeJsonArray[arrayIndex]) != 'undefined') {
        returnValue = '<ul class="chargeInfo">';
        for (var i = 0; i < 3; i++) {
            returnValue += '<li>';
            if (arrayIndex + i < _spreadBaInfo.chargeJsonArray.length) {//推广数组范围内的才显示推广
                returnValue += '<a href="' + _spreadBaInfo.chargeJsonArray[arrayIndex + i][1] + '" target="_blank" style="color:' + (_spreadBaInfo.chargeJsonArray[arrayIndex + i].length > 2 ? '#' + _spreadBaInfo.chargeJsonArray[arrayIndex + i][2] : 'blue') + '"><b>' + _spreadBaInfo.chargeJsonArray[arrayIndex + i][0] + "</b></a>";
            }
            returnValue += '</li>';
        }
        returnValue += '</ul>';
    }
    return returnValue;
}
function init_halfAllSection(id, nodeId) {
    if (document.getElementById("sSelect_" + id) == undefined) {
        var html = '<span><select onchange="changeHalfOrFull(\'' + id + '\',this);" id="sSelect_' + id + '"><option value="0" selected="selected">全' + (Config.isSimple ? '场' : '場') + '</option><option value="1">半' + (Config.isSimple ? '场' : '場') + '</option></span>';
        var $jsp = $(html)
        //插入
        $jsp.insertAfter($("#" + nodeId));
    }
}
function checkOddsComp() {
    var checkCompStr = "";
    checkCompStr = (document.getElementById("compCheck_0").checked ? "1" : "0") + "_" + (document.getElementById("compCheck_1").checked ? "1" : "0") + "_" + (document.getElementById("compCheck_2").checked ? "1" : "0");
    writeCookie("oddsCompShow", checkCompStr);   
    oddsComp();
}
function ReSetQingbao() {
    if (document.getElementById("porlet_24") == null) return;
    var objList = document.getElementById("porlet_24").getElementsByTagName("tr");
    for (var i = 0; i < objList.length; i++) {
        var obj = objList[i];
        if (obj.getAttribute("bgcolor") == "#feefed" || obj.getAttribute("bgcolor") == "#f2f9fd") {
            var str = obj.childNodes[1].innerHTML;
            str = str.replace(/;/g, ";<br>").replace(/；/g, "；<br>").replace("有利】", "有利】<br>").replace("有利]", "有利]<br>").replace("不利】", "不利】<br>").replace("不利]", "不利]<br>");
            obj.childNodes[1].innerHTML = str;
        }
    }
}
ReSetQingbao();
function ShowIntegral(type) {//0为总积分榜，1为主队积分榜，2为客队积分榜
    var html = new Array();
    html.push('<div class="standings-box">');
    html.push('<div class="st-tit">' + (lang == 1 ? "賽前積分榜" : "赛前积分榜") + '</div><div class="st-tit" ><span onclick="ShowIntegral(0)" ' + (type == 0 ? "class='on'" : "") + '>' + (lang == 1 ? "總" : "总") + '</span><span onclick="ShowIntegral(1)" ' + (type == 1 ? "class='on'" : "") + '>主</span><span onclick="ShowIntegral(2)" ' + (type == 2 ? "class='on'" : "") + '>客</span></div>');
    var tempData = new Array();
    switch (type) {
        case 0: tempData = totalScoreStr; break;
        case 1: tempData = homeScoreStr; break;
        case 2: tempData = guestScoreStr; break;
    }
    var index = type == 0 ? 1 : 0;
    html.push('<ul>');
    for (var i = 0; i < tempData.length; i++) {
        var data = tempData[i];
        var bgColor = "";
        if (type == 0 && parseInt(data[0]) > -1)
            bgColor = " style='background-color:" + scoreColor[data[0]].split('|')[0] + ";'";
        var currTeam = "";
        if (data[index+1] == h2h_home || data[index+1] == h2h_away)
            currTeam = " on";
        html.push('<li class="st-list' + currTeam + '">');
        html.push('<i' + bgColor + '>' + data[index] + '</i>');
        html.push('<a href="//zq.titan007.com/cn/team/Summary/' + data[index + 1] + '.html" target="_blank">' + data[index + 2] + '</a>');
        html.push('<span>' + data[index + 3] + '</span>');
        html.push('</li>');
    }
    if (type == 0) {
        for (var i = 0; i < scoreColor.length; i++) {
            html.push('<li class="st-list" style="background-color:' + scoreColor[i].split('|')[0] + ';">' + scoreColor[i].split('|')[1] + '</li>');
        }
    }
    html.push('</ul></div>');
    document.getElementById("integralDiv").innerHTML = html.join("");
}

function loadFile() {
    var detail = document.getElementById("ad1");
    var s2 = document.createElement("script");
    s2.type = "text/javascript";
    s2.charset = "utf-8";
    s2.src = "//data.titan007.com/soccer_scheduleid.js?r=007" + Date.parse(new Date());
    detail.appendChild(s2, "script");  
}
var s3 = document.createElement("script");
s3.type = "text/javascript";
s3.charset = "utf-8";
s3.src = "/dragsort.js";
document.body.appendChild(s3, "script");
function vipBannerCheck() {
    vipSubscribe(1);
}
var userLoginType = checkUser();

/****竞彩指数****/
var jcOddsHttp = zXmlHttp.createRequest();
var jcOldData = "";
function GetJcData() {
    jcOddsHttp.open("get", "/default/getAnalyData?sid=" + scheduleID + "&t=1&r=" + Date.parse(new Date()), true);
    jcOddsHttp.onreadystatechange = MakeJcHtml;
    jcOddsHttp.send(null);
    if (parseInt(arrLeague[0]) == 0 && document.getElementById("porlet_30").style.display != "none") {
        window.setTimeout("GetJcData()", 10000);
    }
}
function MakeJcHtml() {
    try {
        if (jcOddsHttp.readyState != 4 || (jcOddsHttp.status != 200 && jcOddsHttp.status != 0)) return;
        if (jcOldData == jcOddsHttp.responseText) return
        jcOldData = jcOddsHttp.responseText;
        if (jcOldData == "") return;
        var obj = JSON.parse(jcOldData);
        var html = new Array();
        if (obj.jcOdds == null) {
            html.push('<table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#ffffff">');
            html.push('<tr height="45"><td>' + (lang == 1 ? "暫無數據" : "暂无数据") + '</td></tr>');
            html.push('</table>');
            document.getElementById("jcOddsDiv").innerHTML = html.join("");
            return;
        }
        var html = new Array();
        var trColor = " bgcolor='#FFFFFF'";
        var trTitleBg = " bgcolor='#ECF4FB'";
        var trTitleClass = " class='bui'";
        var trOddsClass = " class='odds'";
        var height = " height='22'";
        var specialTdClass1 = " class='spTdLeft'";
        var specialTdClass2 = " class='spTdRight'";
        html.push('<table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd">');
        html.push('<tr class="y_bg"' + height +'><th colspan="2" bgcolor="#FDEFD2">胜平负/亚让</th><th bgcolor="#FDEFD2">进球数</th></tr>');
        html.push('<tr' + trTitleClass + trTitleBg + '>');
        html.push('<td style="color:#333;" rowspan="2" width="80">全场</td><td onclick="GoJcUrl(1)" style="font-weight:normal;color:#4F85FF;"' + trColor + height + specialTdClass1 + '><span>&nbsp;</span><span>' + obj.jcOdds.wlOdds.live.win + '</span><span>' + obj.jcOdds.wlOdds.live.draw + '</span><span>' + obj.jcOdds.wlOdds.live.lose + '</span></td>');
        html.push('<td onclick="GoJcUrl(2)"' + specialTdClass2 +'><span>0球</span><span>1球</span><span>2球</span><span>3球</span><span>4球</span><span>5球</span><span>6球</span><span>7+球</span></td>');
        html.push('</tr>');                
        html.push('<tr' + trOddsClass + trColor + '>');
        html.push('<td onclick="GoJcUrl(0)"' + height + specialTdClass1 + '><span>' + obj.jcOdds.sfOdds.rf + '</span><span>' + obj.jcOdds.sfOdds.live.win + '</span><span>' + obj.jcOdds.sfOdds.live.draw + '</span><span>' + obj.jcOdds.sfOdds.live.lose + '</span></td>');
        html.push('<td onclick="GoJcUrl(2)"' + specialTdClass2 +'><span>' + obj.jcOdds.goalOdds.live.g0 + '</span><span>' + obj.jcOdds.goalOdds.live.g1 + '</span><span>' + obj.jcOdds.goalOdds.live.g2 + '</span><span>' + obj.jcOdds.goalOdds.live.g3 + '</span><span>' + obj.jcOdds.goalOdds.live.g4 + '</span><span>' + obj.jcOdds.goalOdds.live.g5 + '</span><span>' + obj.jcOdds.goalOdds.live.g6 + '</span><span>' + obj.jcOdds.goalOdds.live.g7 + '</span></td>');
        html.push('</tr>');

        html.push('<table onclick="GoJcUrl(4)" width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd" style="cursor:pointer;">');
        html.push('<tr' + trTitleClass + trTitleBg + '><td rowspan="2">胜</td><td' + height +'>1:0</td><td>2:0</td><td>2:1</td><td>3:0</td><td width="90">3:1</td><td>3:2</td><td>4:0</td><td>4:1</td><td>4:2</td><td>5:0</td><td>5:1</td><td>5:2</td><td width="91">胜其它</td></tr>');
        html.push('<tr' + trOddsClass + trColor + '>');
        html.push('<td' + height +'>' + obj.jcOdds.scoreOdds.live.score10 + '</td><td>' + obj.jcOdds.scoreOdds.live.score20 + '</td><td>' + obj.jcOdds.scoreOdds.live.score21 + '</td><td>' + obj.jcOdds.scoreOdds.live.score30 + '</td><td>' + obj.jcOdds.scoreOdds.live.score31 + '</td><td>' + obj.jcOdds.scoreOdds.live.score32 + '</td><td>' + obj.jcOdds.scoreOdds.live.score40 + '</td><td>' + obj.jcOdds.scoreOdds.live.score41 + '</td><td>' + obj.jcOdds.scoreOdds.live.score42 + '</td><td>' + obj.jcOdds.scoreOdds.live.score50 + '</td><td>' + obj.jcOdds.scoreOdds.live.score51 + '</td><td>' + obj.jcOdds.scoreOdds.live.score52 + '</td><td>' + obj.jcOdds.scoreOdds.live.scoreWin + '</td>');
        html.push('</tr>');
        html.push('<tr' + trTitleClass + trTitleBg + '><td rowspan="2">平</td><td' + height +'>0:0</td><td>1:1</td><td>2:2</td><td>3:3</td><td>平其它</td><td colspan="8" rowspan="2" bgcolor="#FFFFFF"></td></tr>');
        html.push('<tr' + trOddsClass + trColor + '>');
        html.push('<td' + height +'>' + obj.jcOdds.scoreOdds.live.score00 + '</td><td>' + obj.jcOdds.scoreOdds.live.score11 + '</td><td>' + obj.jcOdds.scoreOdds.live.score22 + '</td><td>' + obj.jcOdds.scoreOdds.live.score33 + '</td><td>' + obj.jcOdds.scoreOdds.live.scoreDraw + '</td>');
        html.push('</tr>')
        html.push('<tr' + trTitleClass + trTitleBg + '><td rowspan="2">负</td><td' + height +'>0:1</td><td>0:2</td><td>1:2</td><td>0:3</td><td>1:3</td><td>2:3</td><td>0:4</td><td>1:4</td><td>2:4</td><td>0:5</td><td>1:5</td><td>2:5</td><td>负其它</td></tr>');
        html.push('<tr' + trOddsClass + trColor + '>');
        html.push('<td' + height +'>' + obj.jcOdds.scoreOdds.live.score01 + '</td><td>' + obj.jcOdds.scoreOdds.live.score02 + '</td><td>' + obj.jcOdds.scoreOdds.live.score12 + '</td><td>' + obj.jcOdds.scoreOdds.live.score03 + '</td><td>' + obj.jcOdds.scoreOdds.live.score13 + '</td><td>' + obj.jcOdds.scoreOdds.live.score23 + '</td><td>' + obj.jcOdds.scoreOdds.live.score04 + '</td><td>' + obj.jcOdds.scoreOdds.live.score14 + '</td><td>' + obj.jcOdds.scoreOdds.live.score24 + '</td><td>' + obj.jcOdds.scoreOdds.live.score05 + '</td><td>' + obj.jcOdds.scoreOdds.live.score15 + '</td><td>' + obj.jcOdds.scoreOdds.live.score25 + '</td><td>' + obj.jcOdds.scoreOdds.live.scoreLose + '</td>');
        html.push('</tr>');
        html.push('</table>');


        html.push('<table onclick="GoJcUrl(3)" width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd" style="cursor:pointer;">');
        html.push('<tr' + trTitleClass + trTitleBg + '><td rowspan="2" width="80">半全场</td><td' + height +'>胜/胜</td><td>胜/平</td><td>胜/负</td><td>平/胜</td><td>平/平</td><td>平/负</td><td>负/胜</td><td>负/平</td><td>负/负</td></tr>');
        html.push('<tr' + trOddsClass + trColor + '>');
        html.push('<td' + height +'>' + obj.jcOdds.hfOdds.live.hfww + '</td><td>' + obj.jcOdds.hfOdds.live.hfwd + '</td><td>' + obj.jcOdds.hfOdds.live.hfwl + '</td><td>' + obj.jcOdds.hfOdds.live.hfdw + '</td><td>' + obj.jcOdds.hfOdds.live.hfdd + '</td><td>' + obj.jcOdds.hfOdds.live.hfdl + '</td><td>' + obj.jcOdds.hfOdds.live.hflw + '</td><td>' + obj.jcOdds.hfOdds.live.hfld + '</td><td>' + obj.jcOdds.hfOdds.live.hfll + '</td>');
        html.push('</tr>');
        html.push('</table>');
        document.getElementById("jcOddsDiv").innerHTML = html.join("");
        //document.getElementById("porlet_30").style.display = "";
    }
    catch(e) {
        console.log(e)
    }
}
function GoJcUrl(type) {
    var url = "//vip.titan007.com/JcOddsDetail.aspx?scheduleId=" + scheduleID + "&oddsType=" + type;
    //switch (type) {
    //    case 0: url += "t=0"; break;//胜平负
    //    case 1: url += "t=1"; break;//让球胜平负
    //    case 2: url += "t=2"; break;//进球数
    //    case 4: url += "t=3"; break;//比分
    //    case 3: url += "t=4"; break;//半全场
    //}
    window.open(url, "target");
}
