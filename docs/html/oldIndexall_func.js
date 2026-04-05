var state_ch = Array(18);
state_ch[0] = "推迟,推遲,Defer";
state_ch[1] = "中断,中斷,Halt";
state_ch[2] = "腰斩,腰斬,Halt";
state_ch[3] = "<font color=green>待定</font>,<font color=green>待定</font>,<font color=green>Wait</font>";
state_ch[4] = "取消,取消,Cancel";
state_ch[13] = "<b>完</b>,<b>完</b>,<b>Ft</b>";
state_ch[14] = ",,";
state_ch[15] = "上,上,Part1";
state_ch[16] = "<font color=blue>中</font>,<font color=blue>中</font>,<font color=blue>Half</font>";
state_ch[17] = "下,下,Part2";
state_ch[18] = "加,加,Ot";
state_ch[19] = "点,點,";
var GoalCn = "平手,平/半,半球,半/一,一球,一/球半,球半,球半/两,两球,两/两球半,两球半,两球半/三,三球,三/三球半,三球半,三球半/四球,四球,四/四球半,四球半,四球半/五,五球,五/五球半,五球半,五球半/六,六球,六/六球半,六球半,六球半/七,七球,七/七球半,七球半,七球半/八,八球,八/八球半,八球半,八球半/九,九球,九/九球半,九球半,九球半/十,十球".split(",");
var GoalCn2 = ["0", "0/0.5", "0.5", "0.5/1", "1", "1/1.5", "1.5", "1.5/2", "2", "2/2.5", "2.5", "2.5/3", "3", "3/3.5", "3.5", "3.5/4", "4", "4/4.5", "4.5", "4.5/5", "5", "5/5.5", "5.5", "5.5/6", "6", "6/6.5", "6.5", "6.5/7", "7", "7/7.5", "7.5", "7.5/8", "8", "8/8.5", "8.5", "8.5/9", "9", "9/9.5", "9.5", "9.5/10", "10", "10/10.5", "10.5", "10.5/11", "11", "11/11.5", "11.5", "11.5/12", "12", "12/12.5", "12.5", "12.5/13", "13", "13/13.5", "13.5", "13.5/14", "14"];
function Goal2GoalCn(goal) { //数字盘口转汉汉字	
    if (goal == null || goal + "" == "")
        return "";
    else {
        if (goal > 10 || goal < -10) return goal + "球";
        if (goal >= 0) return GoalCn[parseInt(goal * 4)];
        else return "受" + GoalCn[Math.abs(parseInt(goal * 4))];
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
var ShowAd = false;
//更新比赛进行的时间
function setMatchTime() {
    for (var i = 1; i <= matchcount; i++) {
        try {
            if (A[i][0] == 0) continue;
            var realTime = -1;
            if (A[i][13] == "1") {  //上半场			
                var t = A[i][12].split(",");
                var t2 = new Date(t[0], t[1], t[2], t[3], t[4], t[5]);
                goTime = Math.floor((new Date() - t2 - difftime) / 60000);
                if (goTime > 45) {
                    var t3 = goTime - 45;
                    goTime = "45+" + (t3 > 15 ? 15 : t3);
                }
                if (goTime < 1) goTime = "1";
                realTime = goTime;
                document.getElementById("time_" + A[i][0]).innerHTML = goTime + "<img src='bf_img/in.gif' border=0>";
            }
            if (A[i][13] == "3") {  //下半场		
                var t = A[i][12].split(",");
                var t2 = new Date(t[0], t[1], t[2], t[3], t[4], t[5]);
                goTime = Math.floor((new Date() - t2 - difftime) / 60000) + 46;
                if (goTime > 90) {
                    var t3 = goTime - 90;
                    goTime = "90+" + (t3 > 15 ? 15 : t3);
                }
                if (goTime < 46) goTime = "46";
                realTime = goTime;
                document.getElementById("time_" + A[i][0]).innerHTML = goTime + "<img src='bf_img/in.gif' border=0>";
            }
            if (realTime > -1 && flashScheduleIDs == A[i][0])
                setStatusTimeLine(realTime, A[i][13], A[i][0]);
        } catch (e) { }
    }
    runtimeTimer = window.setTimeout("setMatchTime()", 30000);
}
//function addConcern(sId, num) {
//    //var cCount = document.getElementById("concernCount").innerHTML;
//    var matchIndex = getDataIndex(sId);
//    if (concernId.indexOf("_" + A[matchIndex][0] + "_") == -1) concernId += A[matchIndex][0] + "_";
//    else return;
//    writeCookie("Bet007live_concernId_AllDomain", concernId);
//    SortData();
//    matchIndex = getDataIndex(sId);
//    //cCount++;
//    var tr = document.getElementById("tr1_" + A[matchIndex][0]);
//    tr.cells[num].innerHTML = tr.cells[num].innerHTML.replace("addConcern", "deleteConcern").replace("unTop", "top").replace("添加", "取消");
//    var TTime = new Date();
//    var isChange = false;
//    var nt = A[matchIndex][11].split(":");
//    var nd = A[matchIndex][36].split("-");
//    var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);

//    if (Config.sclassType == 0) {
//        for (var i = 1; i <= matchcount; i++) {
//            if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
//                if (A[i][13] >= 0 && A[i][0] != sId) {
//                    var ot = A[i][11].split(":");
//                    var od = A[i][36].split("-");
//                    var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
//                    if (ot2 >= nt2) {
//                        isChange = true;
//                        MovePlace(A[i][0], A[matchIndex][0]);
//                        break;
//                    }
//                }
//            }
//        }
//    }
//    else {
//        var index = Config.sclassType == 1 ? 58 : (Config.sclassType == 2 ? 57 : 59);//57是足彩号，需要比较ASCII码
//        if (index == 57) {
//            for (var i = 1; i <= matchcount; i++) {
//                if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
//                    if (A[i][index].localeCompare(A[matchIndex][57]) > 0) {
//                        isChange = true;
//                        MovePlace(A[i][0], A[matchIndex][0]);
//                        break;
//                    }
//                }
//            }
//        }
//        else {
//            for (var i = 1; i <= matchcount; i++) {
//                if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
//                    if (parseInt(A[i][index]) > parseInt(A[matchIndex][index])) {
//                        isChange = true;
//                        MovePlace(A[i][0], A[matchIndex][0]);
//                        break;
//                    }
//                }
//            }
//        }
//    }
//    if (!isChange) MovePlace(0, A[matchIndex][0]);
//    //document.getElementById("concernCount").innerHTML = cCount;
//}
function addConcern(sId, num) {
    if (concernId.indexOf("_" + sId + "_") == -1) concernId += sId + "_";
    else return;
    writeCommonCookie("Bet007live_concernId_AllDomain", concernId);
    SortData();//赛事排序
    var matchIndex = getDataIndex(sId);//获取排序后该赛事所在位置
    var tr = document.getElementById("tr1_" + sId);
    tr.cells[num].innerHTML = tr.cells[num].innerHTML.replace("addConcern", "deleteConcern").replace("unTop", "top").replace("添加", "取消");
    if (Config.concernCount == 1 || Config.concernCount == matchIndex)//第一场置顶赛事或最后一场置顶赛事
        MovePlace(0, sId);
    else
        MovePlace(A[matchIndex + 1][0], sId);
}
function addMoreConcern(num) {
    //var searchStr = document.getElementById("searchCorcen").value;
    //if (searchStr == "") {
    //    alert("请输入搜索内容!");
    //    return;
    //}
    var sclassList = ",";
    var inputs = document.getElementById("myleague").getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked) {
            var k = parseInt(inputs[i].value);
            sclassList += B[k][0] + ",";
        }
    }
    if (sclassList != "") {
        if (location.href.indexOf("old") == -1 && location.href.indexOf("2in1") == -1)
            num = 13;
        for (var i = 1; i <= matchcount; i++) {
            try {
                if (sclassList.indexOf("," + A[i][2] + ",") != -1)//.indexOf(searchStr) != -1 || A[i][3].indexOf(searchStr) != -1 || A[i][4].indexOf(searchStr) != -1 || A[i][5].indexOf(searchStr) != -1 || A[i][6].indexOf(searchStr) != -1 || A[i][7].indexOf(searchStr) != -1 || A[i][8].indexOf(searchStr) != -1 || A[i][9].indexOf(searchStr) != -1 || A[i][10].indexOf(searchStr) != -1)
                    addConcern(i, num);
            }
            catch (e) { }
        }
    }
}
//function deleteConcern(sId, count) {
//    var matchIndex = getDataIndex(sId);
//    if (concernId.indexOf("_" + A[matchIndex][0] + "_") == -1) return;
//    var tr = document.getElementById("tr1_" + A[matchIndex][0]);
//    tr.cells[count].innerHTML = tr.cells[count].innerHTML.replace("deleteConcern", "addConcern").replace("top", "unTop").replace("取消", "添加");
//    var TTime = new Date();
//    var isChange = false;
//    var nt = A[matchIndex][11].split(":");
//    var nd = A[matchIndex][36].split("-");
//    var nt2 = new Date(TTime.getYear(), nd[0], nd[1], nt[0], nt[1], 0);
//    if (Config.sclassType == 0) {
//        for (var i = 1; i <= matchcount; i++) {
//            if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
//                if (A[matchIndex][13] == -1) {
//                    if (A[i][13] == -1 && A[i][0] > 0) {
//                        var ot = A[i][11].split(":");
//                        var od = A[i][36].split("-");
//                        var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
//                        if (ot2 > nt2) {
//                            isChange = true;
//                            MovePlace(A[i][0], A[matchIndex][0]);
//                            break;
//                        }
//                    }
//                }
//                else {
//                    if (A[i][0] > 0) {
//                        var ot = A[i][11].split(":");
//                        var od = A[i][36].split("-");
//                        var ot2 = new Date(TTime.getYear(), od[0], od[1], ot[0], ot[1], 0);
//                        if (ot2 > nt2) {
//                            isChange = true;
//                            MovePlace(A[i][0], A[matchIndex][0]);
//                            break;
//                        }
//                    }
//                }
//            }
//        }
//    }
//    else {
//        var index = Config.sclassType == 1 ? 58 : (Config.sclassType == 2 ? 57 : 59);//57是足彩号，需要比较ASCII码
//        if (index == 57) {
//            for (var i = 1; i <= matchcount; i++) {
//                if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
//                    if (A[i][index].localeCompare(A[matchIndex][57]) > 0) {
//                        isChange = true;
//                        MovePlace(A[i][0], A[matchIndex][0]);
//                        break;
//                    }
//                }
//            }
//        }
//        else {
//            var tempIndex = 0, minDiff = 1000;
//            for (var i = 1; i <= matchcount; i++) {
//                if (concernId.indexOf("_" + A[i][0] + "_") == -1) {
//                    if (parseInt(A[i][index]) > parseInt(A[matchIndex][index])) {
//                        var archived = parseInt(A[i][index]) - parseInt(A[matchIndex][index]);
//                        if (archived < minDiff) {
//                            minDiff = archived;
//                            tempIndex = i;
//                        }
//                    }
//                }
//            }
//            if (tempIndex > 0) {
//                isChange = true;
//                MovePlace(A[tempIndex][0], A[matchIndex][0]);
//            }
//        }
//    }
//    if (!isChange) {
//        if (location.href.indexOf("2in1") != -1) {
//            var list = new Array();
//            list = oddsLastIndex.split(',');
//            if (matchIndex > 10) {
//                var num = matchIndex;
//                var num2 = 0;
//                for (var i = list.length - 2; i >= 0; i--) {
//                    if (concernId.indexOf("_" + A[list[i]][0] + "_") != -1) {
//                        num2 = i;
//                    }
//                }
//                MovePlace(A[list[num2 - 1]][0], A[matchIndex][0]);
//            }
//            else {
//                var num = list.length - 1;
//                MovePlace(A[list[num - 1]][0], A[matchIndex][0]);
//            }
//        }
//        else {
//            if (matchIndex > 10) {
//                var num2 = 0;
//                for (var i = A.length - 1; i > 1; i--) {
//                    if (concernId.indexOf("_" + A[i][0] + "_") != -1) {
//                        num2 = i;
//                    }
//                }
//                MovePlace(A[num2 - 1][0], A[matchIndex][0]);
//            }
//            else {
//                var num = A.length - 1;
//                MovePlace(A[num - 1][0], A[matchIndex][0]);
//            }
//        }
//    }
//    concernId = concernId.replace("_" + A[matchIndex][0] + "_", "_");
//    writeCookie("Bet007live_concernId_AllDomain", concernId);
//    SortData();
//}
function deleteConcern(sId, count) {   
    if (concernId.indexOf("_" + sId + "_") == -1) return;
    concernId = concernId.replace("_" + sId + "_", "_");
    writeCommonCookie("Bet007live_concernId_AllDomain", concernId);
    SortData();
    var matchIndex = getDataIndex(sId);
    var tr = document.getElementById("tr1_" + sId);
    tr.cells[count].innerHTML = tr.cells[count].innerHTML.replace("deleteConcern", "addConcern").replace("top", "unTop").replace("取消", "添加");
    if (isCompanyPage)//判断是否指定公司的页面，index2in1页面
    {
        if (matchIndex == (A.length - 1))//判断是否最后一个
            MovePlace2(A[matchIndex - 1][0], sId);
        else {
            var hasData = false;
            for (var i = matchIndex + 1; i < A.length - 1; i++) {
                if (A[i][0] != 0) {
                    hasData = true;
                    MovePlace(A[i][0], sId);
                    break;
                }
            }
            if (!hasData)
                MovePlace2(0, sId);
        }
            
    }
    else {
        if (matchIndex == (A.length - 1))//判断是否最后一个
            MovePlace2(A[matchIndex - 1][0], sId);
        else
            MovePlace(A[matchIndex + 1][0], sId);
    }
    
}
function deleteAllConcern() {
    if (concernId == "_" || concernId == "")
        return;
    concernId = "_";
    //document.getElementById("concernCount").innerHTML = 0;
    writeCommonCookie("Bet007live_concernId_AllDomain", concernId);
    var allDate = document.getElementById("allDate");
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.charset = "utf-8";
    s.src = "VbsXml/bfdata_ut.js?r=007" + Date.parse(new Date());
    allDate.removeChild(allDate.firstChild);
    allDate.appendChild(s, "script");
    //ShowBf();
}


function showdetail(obj, event, cId) {
    try {
        if (Config.detail == 0) return;  // || A[n][13]=="0"
        if (Config.isFirstLoadDetailFile) {
            var detail = document.getElementById("span_detail");
            var s = document.createElement("script");
            s.type = "text/javascript";
            s.charset = "utf-8";
            s.src = staticUrl + "vbsxml/detail_ut.js?r=007" + Date.parse(new Date());
            detail.removeChild(detail.firstChild);
            detail.appendChild(s, "script");
            loadDetailFileTime = new Date();
            s.onload = s.onreadystatechange = function () {
                Config.isFirstLoadDetailFile = false;
                createDetail(obj, event, cId);
            }
        }
        else {
            createDetail(obj, event, cId);
        }
    }
    catch (e) {}
}
function createDetail(obj, event, cId) {
    var sid = obj.attributes["aLoc"].value;
    var n = getDataIndex(sid);
    var homeTeam = getTeamName(n, 1, cId, 1);
    var guestTeam = getTeamName(n, 2, cId, 1);
    var detailHeight = 42;
    var detailNum = 0;
    var techNum = 0;
    try {
        if (Math.floor((new Date() - loadDetailFileTime) / 600) > 60) LoadDetailFile();
        var R = new Array();
        var temp = "";
        var hasChange = false;
        for (var i = 0; i < rq.length; i++) {
            R = rq[i].split('^');
            if (R[0] != A[n][0]) continue;
            if (!hasChange && R[2] == '11') hasChange = true;
            var showDetailName = R[2] == '11' && R[6] != '' ? R[6].replace('↑', '<img src="/images/up.gif" align="absmiddle">').replace('↓', '<img src="/images/down.gif" align="absmiddle">') : R[6] != '' ? R[6] : R[4];
            var time = (parseInt(R[10]) > 0 ? R[3] + "+" + R[10] : R[3]);
            if (R[1] == "1")
                temp += "<tr bgcolor=white align=center><td width=12% bgcolor=#EFF4EA>" + time + "'</td><td colspan=2 height=18 style='text-align:left;'><img src='bf_img/" + R[2] + ".gif'>" + showDetailName + "</td></tr>";
            else
                temp += "<tr bgcolor=white align=center><td width=12% bgcolor=#EFF4EA>" + time + "'</td><td colspan=2 height=18 style='text-align:right;'>" + showDetailName + "<img src='bf_img/" + R[2] + ".gif'></td></tr>";
            detailNum++;
        }
        var html = "<div><table width=\"380\" class=\"evt_table\" bgcolor=\"#E1E1E1\" cellpadding=\"0\" cellspacing=\"1\" border=\"0\">";// style='border:solid 1px #666;'
        html += "<tr><td height=20 colspan=3 bgcolor=#666699 align=center><font color=white><b>初指参考：" + Goal2GoalCn(A[n][29]) + "</b></font></td></tr>";
        html += "<tr bgcolor=#D5F2B7 align=center><td width=12% bgcolor=#CCE8B5>时间</td><td height=20 width=44%><font color=#006600><b>" + (A[n][22] != "" ? "[" : "") + A[n][22] + (A[n][22] != "" ? "]" : "") + homeTeam + "</b></font></td><td width=44%><font color=#006600><b>" + (A[n][23] != "" ? "[" : "") + A[n][23] + (A[n][23] != "" ? "]" : "") + guestTeam + "</b></font></td></tr>";
        html += temp;
        html += "</table>";
        var technicCount = ""; //技术统计
        for (var i = 0; i < tc.length; i++) {
            R = tc[i].split('^');
            if (R[0] == A[n][0]) {
                technicCount = R[1];
                break;
            }
        }
        var bgcolor1 = "#FFFFFF";
        var bgcolor2 = "#F0F0FF";
        var regex = new RegExp("\\*", "g");
        var tempTechHtml = "";
        var arrTc = technicCount.replace(regex, "<img src=bf_img/55.gif width=11 height=11>").split(';');
        var useTecList = ",3,4,14,";
        for (var j = 0; j < arrTc.length; j++) {
            if (arrTc[j] == '' || parseInt(arrTc[j].split(',')[0]) > 43) continue;
            if (useTecList.indexOf(',' + arrTc[j].split(',')[0] + ',') == -1) continue;
            tempTechHtml += "<tr class=font12 height=16 bgcolor=" + bgcolor1 + " align=center>";
            tempTechHtml += "<td width='42%'>" + arrTc[j].split(',')[1] + "</td>";
            tempTechHtml += "<td bgcolor=" + bgcolor2 + ">" + resultName[parseInt(arrTc[j].split(',')[0])] + "</td>";
            tempTechHtml += "<td width='42%'>" + arrTc[j].split(',')[2] + "</td></tr>";
            techNum++;
        }
        if (techNum > 0) {
            detailHeight = 63;
            html += "<table width=380 bgcolor=#E1E1E1 cellpadding=0 cellspacing=1 border=0>";
            html += "<tr bgcolor=#D5F2B7 align=center><td height=20 colspan=3 width=44%><font color=#006600><b>技术统计</b></font></td></tr>";
            html += tempTechHtml;
        }
        if (j > 0)
            html += "</table>";
        html += "</div>";
        var obj = document.getElementById('winScore');
        if (location.href.indexOf("old") != -1) {
            var num = 199;
            obj.style.left = (document.body.clientWidth / 2 - num) + "px";
        }
        else {
            var num = 300;
            obj.style.left = (document.body.clientWidth / 2 - num) + "px"; //-175
        }    
        detailHeight += 19 * detailNum + 17 * techNum;
        //旧
        //var postPk = getElementPos("tr1_" + A[n][0]);
        //var papeHeight = getPageHeight();
        //var tdHeight = document.getElementById("tr1_" + A[n][0]).offsetHeight;// location.href.indexOf("old") != -1 ? 18 : 30;
        //if (papeHeight - postPk.y - tdHeight > detailHeight || postPk.y < detailHeight)
        //    obj.style.top = (postPk.y + tdHeight) + "px";
        //else
        //    obj.style.top = (postPk.y - detailHeight - 6) + "px";
        //新
        var postPk = getElementPos("tr1_" + A[n][0]);
        var tdObj = document.getElementById("tr1_" + A[n][0]);
        var bottom = getDistanceToBottom(tdObj);  //获取当前元素到底部的浏览器可视范围底部的距离
        var tdHeight = document.getElementById("tr1_" + A[n][0]).offsetHeight;// location.href.indexOf("old") != -1 ? 18 : 30;
        if (bottom > detailHeight)
            obj.style.top = (postPk.y + tdHeight) + "px";
        else
            obj.style.top = (postPk.y - detailHeight - 6) + "px";

        obj.innerHTML = html;
        obj.style.display = "";
    } catch (e) { }
}
function getDistanceToBottom(element) {
    var rect = element.getBoundingClientRect();
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var clientHeight = window.innerHeight || document.documentElement.clientHeight;
    var elementTop = rect.top + scrollTop;
    var distance = clientHeight - (elementTop - scrollTop) - rect.height;
    return distance;
}
function showpaulu(obj, event, cId) {
    try {

        if (Config.vs == 0) return;
        if (Config.isFirstLoadPanluFile) {
            var detail = document.getElementById("span_panlu");
            var s = document.createElement("script");
            s.type = "text/javascript";
            s.charset = "utf-8";
            s.src = staticUrl + "vbsxml/panlu_ut.js?r=007" + Date.parse(new Date());
            detail.removeChild(detail.firstChild);
            detail.appendChild(s, "script");
            s.onload = s.onreadystatechange = function () {
                Config.isFirstLoadPanluFile = false;
                CreatePanlu(obj, event, cId);                
            }
        }
        else {
            CreatePanlu(obj, event, cId);
        }
        
    } catch (e) { }
}
function CreatePanlu(obj, event, cId) {
    var sid = obj.attributes["aLoc"].value
    var n = getDataIndex(sid);
    var html = [], bg = "";
    var bigNum = 0, victoryNum = 0, singleNum = 0, j = 0, win1;
    var win = 0, standoff = 0;
    var countInfo = "";
    html.push("<div style='background-color:#e4e4e4;'><table width='530' border='0' align='center' cellpadding='0' cellspacing='1' bgcolor='#dddddd'>"); //border:solid 1px #666;
    html.push("<tr align='center' bgcolor='#006699' style='color:white'>");
    html.push("<td width='50' height='18'>赛事</td>");
    html.push("<td width='53'>时间</td>");
    html.push("<td>主场球队</td>");
    html.push("<td width='35'>比分</td>");
    html.push("<td>客场球队</td>");
    html.push("<td width='28'>半场</td>");
    html.push("<td>盘*</td>");
    html.push("<td width='28'>盘路</td>");
    html.push("<td width='28'>胜负</td>");
    html.push("<td width='36'>进球数</td>");
    html.push("<td width='28'>单双</td>");
    html.push("</tr>");
    var contentHeight = 18;
    var homeTeam = getTeamName(n, 1, cId, 1);
    var guestTeam = getTeamName(n, 2, cId, 1);
    var sclassName = A[n][2 + lang];
    for (var i = 0; i < p.length; i++) {
        var b = p[i];
        if (!(b[3] == A[n][37] && b[4] == A[n][38] || b[4] == A[n][37] && b[3] == A[n][38])) continue;
        if (b[7] == null) b[7] = "";
        if (b[8] == null) b[8] = "";

        bg = (bg == "#ffffff") ? "#F4F8FF" : "#ffffff";
        html.push("<tr align=center bgcolor='" + bg + "'>");
        html.push("<td bgcolor=" + b[1] + " height=22><font color=#FFFFFF>" + b[0] + "</font></td>");
        html.push("<td>" + b[2] + "</td>");

        if (b[3] == A[n][37]) //主场
        {
            html.push("<td><font color=#880000>" + homeTeam.replace("(中)", "") + "</td>");
            html.push("<td style='color:red'><B>" + b[5] + "-" + b[6] + "</td>");
            html.push("<td>" + guestTeam + "</a></td>");
            html.push("<td><font color=red>" + b[7] + "-" + b[8] + "</td>");
            html.push("<TD>" + Goal2GoalCn(b[9]) + "</TD>");
            if (b[5] - b[9] > b[6]) { html.push("<TD><font color=red>赢</font></TD>"); win++; }
            if (b[5] - b[9] == b[6]) { html.push("<TD><font color=blue>走</font></TD>"); standoff++ }
            if (b[5] - b[9] < b[6]) html.push("<TD><font color=green>输</font></TD>");
            if (b[5] > b[6]) html.push("<TD><font color=red>胜</font></TD>");
            if (b[5] == b[6]) html.push("<TD><font color=blue>平</font></TD>");
            if (b[5] < b[6]) html.push("<TD><font color=green>负</font></TD>");
            if (b[5] > b[6]) victoryNum++;
        }
        else //客场
        {
            html.push("<td style='color:#000000'>" + guestTeam + "</td>");
            html.push("<td style='color:red'><B>" + b[5] + "-" + b[6] + "</td>");
            html.push("<td style='color=#880000'>" + homeTeam.replace("(中)", "") + "</td>");
            html.push("<td><font color=red>" + b[7] + "-" + b[8] + "</td>");
            html.push("<TD>" + Goal2GoalCn(b[9]) + "</TD>");
            if (b[5] - b[9] < b[6]) { html.push("<TD><font color=red>赢</font></TD>"); win++; }
            if (b[5] - b[9] == b[6]) { html.push("<TD><font color=blue>走</font></TD>"); standoff++ }
            if (b[5] - b[9] > b[6]) html.push("<TD><font color=green>输</font></TD>");
            if (b[5] < b[6]) html.push("<TD><font color=red>胜</font></TD>");
            if (b[5] == b[6]) html.push("<TD><font color=blue>平</font></TD>");
            if (b[5] > b[6]) html.push("<TD><font color=green>负</font></TD>");
            if (b[5] < b[6]) victoryNum++;
        }

        if (b[5] + b[6] > 2.5) {
            html.push("<td><font color=red>大</td>");
            bigNum++;
        }
        else
            html.push("<td><font color=green>小</td>");
        if ((b[5] + b[6]) % 2 == 1) {
            html.push("<td><font color=red>单</td>");
            singleNum++;
        }
        else
            html.push("<td><font color=blue>双</td>");
        html.push("</tr>");
        j++;
    }

    if (j > 0) {
        if (j - standoff > 0)
            win1 = Math.round(win / (j - standoff) * 1000) / 10;
        else
            win1 = "0";
        html.push("<tr><td height=20 align=center colspan=11 bgcolor=white>最近[ <font color=red>" + j + " </font>]场,  &nbsp;  胜率：<font color=red>" + Math.round(victoryNum / j * 1000) / 10 + "%</font> 赢盘率：<font color=red>" + win1 + "% </font> 大球：<font color=red>" + Math.round(bigNum / j * 1000) / 10 + "%</font> 单：<font color=red>" + Math.round(singleNum / j * 1000) / 10 + "%</font></td></tr>");
    }
    html.push("</table></div>");
    var obj = document.getElementById('winScore');
    if (location.href.indexOf("old") != -1)
        obj.style.left = (document.body.clientWidth / 2 - 320) + "px"; //-350
    else
        obj.style.left = (document.body.clientWidth / 2 - 450) + "px"; //-440
    var scrollTop = Math.max(document.body.scrollTop, document.documentElement.scrollTop);
    var pos = getElementPos("sound");
    var postPk = getElementPos("tr1_" + A[n][0]);
    var oddsY = postPk.y - scrollTop;
    contentHeight += (j + 1) * 23;
    if (j == 0) {
        if (location.href.indexOf("old") != -1)
            obj.style.left = (document.body.clientWidth / 2 + 10) + "px"; //-10
        else
            obj.style.left = (document.body.clientWidth / 2 - 90) + "px"; //-10
        html = [];
        html.push("<table style='background-color:#FFFFFF;width:180px;line-height:28px;text-align:center;font-size:14px;'><tr><td><b>没有 " + sclassName + " 对赛往绩</b></td></tr></table>");//border:solid 1px #666; 
        contentHeight = 38;
    }
    //var papeHeight = getPageHeight();
    var tdHeight = 0;
    if (location.href.indexOf("indexall") != -1 || location.href.indexOf("index2in1") != -1 || location.href.indexOf("oldIndexall") != -1 || location.href.indexOf(".aspx") == -1) {
        if (event.clientY - pos.y < contentHeight)
            obj.style.top = postPk.y + "px";
        else
            obj.style.top = (postPk.y - contentHeight) + "px";
    }
    else
        obj.style.top = Math.max(0, scrollTop + event.clientY - (j + 2) * 23 - 15) + "px";
    obj.innerHTML = html.join("");
    obj.style.display = "";
}
function check() {
    if (oldUpdateTime == lastUpdateTime && oldUpdateTime != "") {
        if (confirm("由于程序忙，或其他网络问题，你已经和服务器断开连接超过 5 分钟，是否要重新连接观看比分？")) window.location.reload();
    }
    oldUpdateTime = lastUpdateTime;
    window.setTimeout("check()", 300000);
}


function setScoreMatchHtml() {
    try {
        if (Config.language != 0) {
            document.getElementById("fScore").innerHTML = '<a href="http://bf.titan007.com/Over1.htm" target="_blank">完场比分</a>';
            document.getElementById("nMatch").innerHTML = '<a href="http://bf.titan007.com/Next1.htm" target="_blank">下日赛程</a>';
        }
        else {
            document.getElementById("fScore").innerHTML = '<a href="http://bf.titan007.com/Over1_cn.htm" target="_blank">完场比分</a>';
            document.getElementById("nMatch").innerHTML = '<a href="http://bf.titan007.com/Next1_cn.htm" target="_blank">下日赛程</a>';
        }
    }
    catch (e) { }
}
function showExplain(exlist, hometeam, guestteam) {
    // 广东体育; 1 | 1; 2 | 5; 12 | 90, 1 - 1; 2 - 2; 1, 2 - 2; 5 - 4; 1   
    hometeam = hometeam.replace("\(中\)", "");
    guestteam = guestteam.replace("\(中\)", "");
    var explainList = "";
    if (exlist != "") {
        var arrExplain = exlist.split('|');
        if (arrExplain[0].split(';')[0] != "")
            explainList += arrExplain[0].split(';')[0] + " ";
        if (arrExplain[0].split(';')[1] == "1")
            explainList += "<a href=http://www.310win.com/buy/jingcai.aspx target=_blank><font color=red>[购买竞彩]</font></a> <br>";
        if (arrExplain[1].split(';')[0] != "") {

            explainList += "先开球(";
            if (arrExplain[1].split(';')[0] == "1")
                explainList += hometeam + ")";
            else if (arrExplain[1].split(';')[0] == "2")
                explainList += guestteam + ")";
            if (arrExplain[1].split(';')[1] == "")
                explainList += "<br>";
        }
        if (arrExplain[1].split(';')[1] != "") {
            if (arrExplain[1].split(';')[1] == "1" || arrExplain[1].split(';')[1] == "5")
                explainList += " <a href=http://tvhk.city007.net/ target=_blank><font color=blue>[独家宽频]</font></a><br>";
            else if (arrExplain[1].split(';')[1] == "2" || arrExplain[1].split(';')[1] == "4")
                explainList += " <a href=http://www.310tv.com/ target=_blank><font color=blue>直播</font></a><br>";
        }
        if (arrExplain[2].split(';')[0] != "") {
            explainList += "角球数(" + arrExplain[2].split(';')[0] + ") | ";
            explainList += "角球数(" + arrExplain[2].split(';')[1] + ")<br>";
        }
        var scoresList = arrExplain[3].split(';');
        //if (scoresList[0] != "") {
        if (scoresList[0] != "")
            explainList += scoresList[0].split(',')[0] + "分钟[" + scoresList[0].split(',')[1] + "],";
        if (scoresList.length > 1 && scoresList[1] != "")
            explainList += "两回合[" + scoresList[1] + "],";
        if (scoresList.length > 2 && scoresList[2] != "") {
            if (scoresList[2].split(',')[0] == "1")
                explainList += "120分钟[" + scoresList[2].split(',')[1] + "],";
            else if (scoresList[2].split(',')[0] == "2")
                explainList += "加时[" + scoresList[2].split(',')[1] + "],";
            else
                explainList += "加时中,现在比分[" + scoresList[2].split(',')[1] + "]";
        }
        if (scoresList.length > 3 && scoresList[3] != "") {
            var tempPointExplain = "点球[" + scoresList[3] + "],";
            if (scoresList.length > 4 && scoresList[4] == "")
                tempPointExplain = "点球[" + scoresList[3] + "]";
            explainList += tempPointExplain;
        }
        if (scoresList.length > 4)
            explainList += (scoresList[4] == "1" ? "主胜" : scoresList[4] == "2" ? "客胜" : "");
            //explainList += (scoresList[4] == "1" ? hometeam + "胜出" : scoresList[4] == "2" ? guestteam + "胜出" : "");
        //}
        //else if (explainList.lastIndexOf("<br>") == explainList.length - 4)
        //explainList = explainList.substring(0, explainList.length - 4);
    }
    return explainList;
}
function SetLanguage(l) {
    document.getElementById("Language" + Config.language).className = "";
    document.getElementById("Language" + l).className = "lgg";
    Config.language = l;
    Config.writeCookie();
    if (Config.language == 1) {
        changeUrl(l);
    }
    else
        LoadLiveFile();
    Config.setLangName();
    SetTrBgColor();
}
function changeUrl(l) {
    if (l == 1) {
        var name = location.href.substring(location.href.lastIndexOf("/") + 1);
        var para = "";
        var num = location.href.indexOf("?");
        if (num > 0)
            para = location.href.substring(num);
        if (name.indexOf('.') != -1)
            name = name.split('.')[0] + "_big.aspx" + para;
        else
            name = "indexall_big.aspx" + para;
        location.href = name;
    }
}
function changeUrl2(l) {
    var name = location.href.substring(location.href.lastIndexOf("/") + 1);
    var para = "";
    var num = location.href.indexOf("?");
    if (num > 0)
        para = location.href.substring(num);
    if (l == 1) {
        if (name.indexOf('.') != -1) {
            Config.oldOrNew = 2;
            if (Config.language == 1)
                Config.language = 0;
            return; //name = name.split('.')[0] + "_big.aspx" + para;
        }
        else {
            if (Config.oldOrNew == 2)
                name = "indexall_big.aspx" + para;
            else
                name = "oldIndexall_big.aspx" + para;
        }
    }
    else if (Config.oldOrNew == 1) {
        if (name.indexOf('.') != -1) {
            Config.oldOrNew = 2;
            return;
        }
        else
            name = "oldIndexall.aspx" + para;
    }
    else return;
    location.href = name;
}
var oldOddsI = 0;
function showOddsDetail(obj, event) {
    if (Config.showSbOddsDetail == 0) return;
    if (Config.isFirstLoadSbDetailFile) {
        var detail = document.getElementById("span_sbDetail");
        var s = document.createElement("script");
        s.type = "text/javascript";
        s.charset = "utf-8";
        s.src = staticUrl + ((isCompanyPage && companyID == 8) ? ("vbsxml/runOddsData_8.js?r=007" + Date.parse(new Date())) : ("vbsxml/sbOddsData.js?r=007" + Date.parse(new Date())));
        detail.removeChild(detail.firstChild);
        detail.appendChild(s, "script");
        loadSbDetailTime = new Date();
        s.onload = s.onreadystatechange = function () {
            Config.isFirstLoadSbDetailFile = false;
            createOddsDetail(obj, event);
        }
    }
    else {
        createOddsDetail(obj, event);
    }
}
function createOddsDetail(obj, event) {
    var scheduleId = obj.attributes["aLoc"].value;
    if (showCont > 0) return;
    var width = 515;
    var hasRunning = true;
    var i = getDataIndex(scheduleId);
    var homeTeam = getTeamName(i, 1, 3, 1);
    var guestTeam = getTeamName(i, 2, 3, 1);
    var sclassName = A[i][2];
    var hOrder = A[i][22];
    var gOrder = A[i][23];
    var strScore = "VS";
    var tempCompanyId = (isCompanyPage && companyID == 8) ? 8 : 3;
    var matchState = parseInt(A[i][13]);
    if (matchState > 0 || matchState == -1) {
        if (matchState == -1)
            strScore = "<b><font style='color:red;'>" + A[i][14] + " - " + A[i][15] + "</font></b>";
        else
            strScore = "<b><font style='color:blue;'>" + A[i][14] + " - " + A[i][15] + "</font></b>";
    }
    var html = new Array();
    var strGoals;
    if (Math.floor((new Date() - loadSbDetailTime) / 600) > 60) LoadSbDetailFile();
    if (typeof (sData[scheduleId]) == "undefined")
        return;
    var arrOdds = sData[scheduleId];
    if (typeof (arrOdds[0][6]) == "undefined" || arrOdds[0][6] == "" || matchState == -1) {
        width = 480;//406
        hasRunning = false;
    }
    var obj = document.getElementById('sbOddsDetail');
    var postPk = getElementPos("tr1_" + A[i][0]);
    if (oldOddsI != i) {
        oldOddsI = i;
        //    html.push('<div style="width:' + width + 'px" class="livetab">');
        var leagueNameUrl = A[i][31] != "" ? ' <a href="http://zq.titan007.com' + A[i][31] + '" target="_blank" style="color:#FFF">' + sclassName + '</a>' : '<span style="color:#FFF">' + sclassName + '</span>';
        html.push('<table width="' + width + '" border="0" cellpadding="0" cellspacing="1">');
        html.push('<tr>');
        html.push('<td width="' + (hasRunning ? "11%" : "12%") + '" height="31" bgcolor="#770088">' + leagueNameUrl + '</td>');
        html.push('<td width="' + (hasRunning ? "34" : "36") + '%" bgcolor="#FDFEE0" style="text-align:right">' + (hOrder != "" ? '<sup class="sup_small">[' + hOrder + ']</sup>' : '') + '<b>' + homeTeam + '</b></td>');
        html.push('<td  id="ffScoreDetail" sid=' + scheduleId + ' width="18%" bgcolor="#FDFEE0">' + strScore + '</td>');
        html.push('<td width="37%" bgcolor="#FDFEE0" style="text-align:left"><b>' + guestTeam + '</b>' + (gOrder != "" ? '<sup class="sup_small">[' + gOrder + ']</sup>' : '') + '</td>');
        html.push('</tr>');
        html.push('</table>');
        strGoals = scheduleId + "," + matchState + ",";
        if (matchState > 0 || matchState == -1)//让,标准,大
            strGoals += (typeof (arrOdds[0][7]) == "undefined" ? '' : arrOdds[0][7]) + "," + (typeof (arrOdds[0][6]) == "undefined" ? '' : arrOdds[0][6]) + "," + (typeof (arrOdds[0][8]) == "undefined" ? '' : arrOdds[0][8]) + "," + (typeof (arrOdds[1][7]) == "undefined" ? '' : arrOdds[1][7]) + "," + (typeof (arrOdds[1][6]) == "undefined" ? '' : arrOdds[1][6]) + "," + (typeof (arrOdds[1][8]) == "undefined" ? '' : arrOdds[1][8]) + "," + (typeof (arrOdds[2][7]) == "undefined" ? '' : arrOdds[2][7]) + "," + (typeof (arrOdds[2][6]) == "undefined" ? '' : arrOdds[2][6]) + "," + (typeof (arrOdds[2][8]) == "undefined" ? '' : arrOdds[2][8]);
        else
            strGoals += (typeof (arrOdds[0][4]) == "undefined" ? '' : arrOdds[0][4]) + "," + (typeof (arrOdds[0][3]) == "undefined" ? '' : arrOdds[0][3]) + "," + (typeof (arrOdds[0][5]) == "undefined" ? '' : arrOdds[0][5]) + "," + (typeof (arrOdds[1][4]) == "undefined" ? '' : arrOdds[1][4]) + "," + (typeof (arrOdds[1][3]) == "undefined" ? '' : arrOdds[1][3]) + "," + (typeof (arrOdds[1][5]) == "undefined" ? '' : arrOdds[1][5]) + "," + (typeof (arrOdds[2][4]) == "undefined" ? '' : arrOdds[2][4]) + "," + (typeof (arrOdds[2][3]) == "undefined" ? '' : arrOdds[2][3]) + "," + (typeof (arrOdds[2][5]) == "undefined" ? '' : arrOdds[2][5]);
        html.push('<table id="ffOddsDetail" width="' + width + 'px" border="0" cellpadding="0" cellspacing="1"  style="background-color:#AEBFCA" odds="' + strGoals + '">');
        html.push('<tr>');
        html.push('<td width="' + (hasRunning ? "11%" : "12%") + '" bgcolor="#4864B7">&nbsp;</td>');
        if (hasRunning)
            html.push('<td colspan="3" bgcolor="#ECEDEB">现(全场)</td>');
        html.push('<td colspan="3" bgcolor="#F2F9FD">即(全场)</td>');
        html.push('<td colspan="3" bgcolor="#FEF7ED">初(全场)</td>');
        html.push('</tr>');
        html.push('<tr>');
        html.push('<td bgcolor="#4864B7" class="li_ti">亚 <a href="http://vip.titan007.com/changeDetail/handicap.aspx?id=' + scheduleId + '&companyID=' + tempCompanyId + '" target="_blank"><font color=yellow>走势</font></a></td>');
        if (hasRunning) {
            html.push('<td width="35" bgcolor="#ECEDEB">' + changeData(arrOdds[0][6]) + '</td>');
            html.push('<td width="90" bgcolor="#ECEDEB">' + Goal2GoalCn(arrOdds[0][7]) + '</td>');
            html.push('<td width="35" bgcolor="#ECEDEB">' + changeData(arrOdds[0][8]) + '</td>');
        }
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#F2F9FD">' + getStrDiv(arrOdds[0][3], arrOdds[0][0]) + '</td>');
        html.push('<td width="' + (hasRunning ? "90" : "21%") + '" bgcolor="#F2F9FD">' + getStrDiv2(arrOdds[0][4], arrOdds[0][1], 1) + '</td>');
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#F2F9FD">' + getStrDiv(arrOdds[0][5], arrOdds[0][2]) + '</td>');
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#FEF7ED">' + (typeof (arrOdds[0][0]) == "undefined" ? '&nbsp;' : changeData(arrOdds[0][0])) + '</td>');
        html.push('<td width="' + (hasRunning ? "90" : "21%") + '" bgcolor="#FEF7ED">' + Goal2GoalCn(arrOdds[0][1]) + '</td>');
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#FEF7ED">' + (typeof (arrOdds[0][2]) == "undefined" ? '&nbsp;' : changeData(arrOdds[0][2])) + '</td>');
        html.push('</tr>');
        html.push('<tr>');
        html.push('<td bgcolor="#4864B7" class="li_ti">欧 <a href="http://vip.titan007.com/changeDetail/1x2.aspx?id=' + scheduleId + '&companyID=' + tempCompanyId + '" target="_blank"><font color=yellow>走势</font></a></td>');
        if (hasRunning) {
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[1][6]) == "undefined" ? '&nbsp;' : changeData(arrOdds[1][6])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[1][7]) == "undefined" ? '&nbsp;' : changeData(arrOdds[1][7])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[1][8]) == "undefined" ? '&nbsp;' : changeData(arrOdds[1][8])) + '</td>');
        }
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[1][3], arrOdds[1][0]) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + (typeof (arrOdds[1][4]) == "undefined" ? '&nbsp;' : getStrDiv(arrOdds[1][4], arrOdds[1][1])) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[1][5], arrOdds[1][2]) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[1][0]) == "undefined" ? '&nbsp;' : changeData(arrOdds[1][0])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[1][1]) == "undefined" ? '&nbsp;' : changeData(arrOdds[1][1])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[1][2]) == "undefined" ? '&nbsp;' : changeData(arrOdds[1][2])) + '</td>');
        html.push('</tr>');
        html.push('<tr>');
        html.push('<td bgcolor="#4864B7" class="li_ti">大 <a href="http://vip.titan007.com/changeDetail/overunder.aspx?id=' + scheduleId + '&companyID=' + tempCompanyId + '" target="_blank"><font color=yellow>走势</font></a></td>');
        if (hasRunning) {
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[2][6]) == "undefined" ? '&nbsp;' : changeData(arrOdds[2][6])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[2][7]) == "undefined" ? '&nbsp;' : Goal2GoalCn2(arrOdds[2][7])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[2][8]) == "undefined" ? '&nbsp;' : changeData(arrOdds[2][8])) + '</td>');
        }
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[2][3], arrOdds[2][0]) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + (typeof (arrOdds[2][4]) == "undefined" ? '&nbsp;' : getStrDiv2(arrOdds[2][4], arrOdds[2][1], 2)) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[2][5], arrOdds[2][2]) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[2][0]) == "undefined" ? '&nbsp;' : changeData(arrOdds[2][0])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[2][1]) == "undefined" ? '&nbsp;' : Goal2GoalCn2(arrOdds[2][1])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[2][2]) == "undefined" ? '&nbsp;' : changeData(arrOdds[2][2])) + '</td>');
        html.push('</tr>');
        html.push('</table>');
        strGoals = scheduleId + ",";
        if (matchState > 0 || matchState == -1)//让,大,标准
            strGoals += (typeof (arrOdds[3][7]) == "undefined" ? '' : arrOdds[3][7]) + "," + (typeof (arrOdds[3][6]) == "undefined" ? '' : arrOdds[3][6]) + "," + (typeof (arrOdds[3][8]) == "undefined" ? '' : arrOdds[3][8]) + "," + (typeof (arrOdds[4][7]) == "undefined" ? '' : arrOdds[4][7]) + "," + (typeof (arrOdds[4][6]) == "undefined" ? '' : arrOdds[4][6]) + "," + (typeof (arrOdds[4][8]) == "undefined" ? '' : arrOdds[4][8]) + "," + (typeof (arrOdds[5][7]) == "undefined" ? '' : arrOdds[5][7]) + "," + (typeof (arrOdds[5][6]) == "undefined" ? '' : arrOdds[5][6]) + "," + (typeof (arrOdds[5][8]) == "undefined" ? '' : arrOdds[5][8]);
        else
            strGoals += (typeof (arrOdds[3][4]) == "undefined" ? '' : arrOdds[3][4]) + "," + (typeof (arrOdds[3][3]) == "undefined" ? '' : arrOdds[3][3]) + "," + (typeof (arrOdds[3][5]) == "undefined" ? '' : arrOdds[3][5]) + "," + (typeof (arrOdds[4][4]) == "undefined" ? '' : arrOdds[4][4]) + "," + (typeof (arrOdds[4][3]) == "undefined" ? '' : arrOdds[4][3]) + "," + (typeof (arrOdds[4][5]) == "undefined" ? '' : arrOdds[4][5]) + "," + (typeof (arrOdds[5][4]) == "undefined" ? '' : arrOdds[5][4]) + "," + (typeof (arrOdds[5][3]) == "undefined" ? '' : arrOdds[5][3]) + "," + (typeof (arrOdds[5][5]) == "undefined" ? '' : arrOdds[5][5]);
        html.push('<table width="' + width + '" border="0" cellpadding="0" cellspacing="0">');
        html.push('<tr ' + (ShowAd ? "" : "height=30px") + ' bgcolor="#FDFEE0" style="text-align:center;">');
        html.push('<td>');
        if (ShowAd && sbAd1[0] != "")
            html.push('<div class="item"><a href="' + sbAd1[0] + '" target="_blank"><img style="width:' + (hasRunning ? "515px" : "406px") + ';height:40px;" src="' + sbAd2[0] + '"></a><i></i></div>');
        //    html.push('</td>');
        //    html.push('<td width="' + (hasRunning ? "7" : "6") + '">&nbsp;</td>');
        //    html.push('<td>');
        //    if (ShowAd)
        //        html.push('<a href="' + sbAd1[1] + '" target="_blank"><img style="width:' + (hasRunning ? "254px" : "200px") + ';height:40px;" src="' + sbAd2[1] + '"></a>');
        html.push('</td></tr>');
        html.push('</table>');
        html.push('<table id="fhOddsDetail" width="' + width + 'px" border="0" cellpadding="0" cellspacing="1"  style="background-color:#AEBFCA" odds="' + strGoals + '">');
        html.push(' <tr>');
        html.push('<td width="' + (hasRunning ? "11%" : "12%") + '" bgcolor="#4864B7">&nbsp;</td>');
        if (hasRunning)
            html.push('<td colspan="3" bgcolor="#ECEDEB">现(上半场)</td>');
        html.push('<td colspan="3" bgcolor="#F2F9FD">即(上半场)</td>');
        html.push('<td colspan="3" bgcolor="#FEF7ED">初(上半场)</td>');
        html.push('</tr>');
        html.push('<tr>');
        html.push('<td bgcolor="#4864B7" class="li_ti">亚 <a href="http://vip.titan007.com/changeDetail/handicapHalf.aspx?id=' + scheduleId + '&companyid=' + tempCompanyId + '" target="_blank"><font color=yellow>走势</font></a></td>');
        if (hasRunning) {
            html.push('<td width="35" bgcolor="#ECEDEB">' + (typeof (arrOdds[3][6]) == "undefined" ? '&nbsp;' : changeData(arrOdds[3][6])) + '</td>');
            html.push('<td width="90" bgcolor="#ECEDEB">' + Goal2GoalCn(arrOdds[3][7]) + '</td>');
            html.push('<td width="35" bgcolor="#ECEDEB">' + (typeof (arrOdds[3][6]) == "undefined" ? '&nbsp;' : changeData(arrOdds[3][8])) + '</td>');
        }
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#F2F9FD">' + getStrDiv(arrOdds[3][3], arrOdds[3][0]) + '</td>');
        html.push('<td width="' + (hasRunning ? "90" : "21%") + '" bgcolor="#F2F9FD">' + getStrDiv2(arrOdds[3][4], arrOdds[3][1], 1) + '</td>');
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#F2F9FD">' + getStrDiv(arrOdds[3][5], arrOdds[3][2]) + '</td>');
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#FEF7ED">' + (typeof (arrOdds[3][0]) == "undefined" || typeof (arrOdds[3][4]) == "undefined" ? '&nbsp;' : changeData(arrOdds[3][0])) + '</td>');
        html.push('<td width="' + (hasRunning ? "90" : "21%") + '" bgcolor="#FEF7ED">' + (typeof (arrOdds[3][1]) == "undefined" || typeof (arrOdds[3][4]) == "undefined" ? '&nbsp;' : Goal2GoalCn(arrOdds[3][1])) + '</td>');
        html.push('<td width="' + (hasRunning ? "35" : "11%") + '" bgcolor="#FEF7ED">' + (typeof (arrOdds[3][2]) == "undefined" || typeof (arrOdds[3][4]) == "undefined" ? '&nbsp;' : changeData(arrOdds[3][2])) + '</td>');
        html.push('</tr>');
        html.push(' <tr>');
        html.push('<td bgcolor="#4864B7" class="li_ti">欧 <a href="http://vip.titan007.com/changeDetail/1x2Half.aspx?id=' + scheduleId + '&companyID=' + tempCompanyId + '" target="_blank"><font color=yellow>走势</font></a></td>');
        if (hasRunning) {
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[5][6]) == "undefined" ? '&nbsp;' : changeData(arrOdds[5][6])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[5][7]) == "undefined" ? '&nbsp;' : changeData(arrOdds[5][7])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[5][8]) == "undefined" ? '&nbsp;' : changeData(arrOdds[5][8])) + '</td>');
        }
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[5][3], arrOdds[5][0]) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + (typeof (arrOdds[5][4]) == "undefined" ? '&nbsp;' : getStrDiv(arrOdds[5][4], arrOdds[5][1])) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[5][5], arrOdds[5][2]) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[5][0]) == "undefined" || typeof (arrOdds[5][4]) == "undefined" ? '&nbsp;' : changeData(arrOdds[5][0])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[5][1]) == "undefined" || typeof (arrOdds[5][4]) == "undefined" ? '&nbsp;' : changeData(arrOdds[5][1])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[5][2]) == "undefined" || typeof (arrOdds[5][4]) == "undefined" ? '&nbsp;' : changeData(arrOdds[5][2])) + '</td>');
        html.push(' </tr>');
        html.push('<tr>');
        html.push('<td bgcolor="#4864B7" class="li_ti">大 <a href="http://vip.titan007.com/changeDetail/overunderHalf.aspx?id=' + scheduleId + '&companyid=' + tempCompanyId + '" target="_blank"><font color=yellow>走势</font></a></td>');
        if (hasRunning) {
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[4][6]) == "undefined" ? '&nbsp;' : changeData(arrOdds[4][6])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[4][7]) == "undefined" ? '&nbsp;' : Goal2GoalCn2(arrOdds[4][7])) + '</td>');
            html.push('<td bgcolor="#ECEDEB">' + (typeof (arrOdds[4][8]) == "undefined" ? '&nbsp;' : changeData(arrOdds[4][8])) + '</td>');
        }
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[4][3], arrOdds[4][0]) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + (typeof (arrOdds[4][4]) == "undefined" ? '&nbsp;' : getStrDiv2(arrOdds[4][4], arrOdds[4][1], 2)) + '</td>');
        html.push('<td bgcolor="#F2F9FD">' + getStrDiv(arrOdds[4][5], arrOdds[4][2]) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[4][0]) == "undefined" || typeof (arrOdds[4][4]) == "undefined" ? '&nbsp;' : changeData(arrOdds[4][0])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[4][1]) == "undefined" || typeof (arrOdds[4][4]) == "undefined" ? '&nbsp;' : Goal2GoalCn2(arrOdds[4][1])) + '</td>');
        html.push('<td bgcolor="#FEF7ED">' + (typeof (arrOdds[4][2]) == "undefined" || typeof (arrOdds[4][4]) == "undefined" ? '&nbsp;' : changeData(arrOdds[4][2])) + '</td>');
        html.push(' </tr>');
        html.push('</table>');
        //    html.push("</div>");

        var pos = getElementPos("sound");
        if (hasRunning)
            obj.style.left = (document.body.clientWidth / 2 - 310) + "px";
        else
            obj.style.left = (document.body.clientWidth / 2 - 274) + "px";//200
        //    }
        var scrollTop = Math.max(document.body.scrollTop, document.documentElement.scrollTop);
        var oddsY = postPk.y - scrollTop;
        if (scrollTop == 0) {
            if (oddsY - pos.y < 247)
                obj.style.top = (scrollTop + oddsY) + "px";
            else
                obj.style.top = (oddsY - 230) + "px";
        }
        else {
            if (oddsY < obj.clientHeight)
                obj.style.top = (scrollTop + oddsY) + "px";
            else
                obj.style.top = (scrollTop + oddsY - 230) + "px";
        }
        //-230
        obj.innerHTML = html.join("");
    }
    document.getElementById("ifShow").value = 1;
    MM_showHideLayers('sbOddsDetail', '', 'show');
    showCont++;
}
