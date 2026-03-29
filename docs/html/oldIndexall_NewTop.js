function showhideul(kind) {
    document.getElementById("ulselect").style.display = kind == 0 ? "none" : "block";
}
function showhideul2(kind) {
    document.getElementById("ulselect2").style.display = kind == 0 ? "none" : "block";
}
function showhideul3(kind) {
    document.getElementById("ulselect3").style.display = kind == 0 ? "none" : "block";
}
function check(theForm) {
    if (theForm.UserName.value == '') {
        alert("请输入球探帐号");
        theForm.UserName.focus();
        return false;
    }
    if (theForm.Password.value == '') {
        alert("请输入密码");
        theForm.Password.focus();
        return false;
    }
}
function changeCsDiv(cna) {
    var items = document.getElementById(cna).getElementsByTagName("span");
    var clsName = "b_bb";
    for (var i = 0; i < items.length; i++) { items[i].className = clsName; }
}
function showDiv(cna) {
    document.getElementById(cna).style.display = "block";
}
function hideDiv(cna, event) {

    try {
        if (window.event)
            ev = window.event.toElement;
        else
            ev = event.relatedTarget;
        if (ev.id != cna && ev.id.indexOf("a") == -1) {
            document.getElementById(cna).style.display = "none";
            var items = document.getElementById(cna.replace("div", "")).getElementsByTagName("span");
            for (var i = 0; i < items.length; i++) {
                if (cna == "b_divL9")
                    items[i].className = "b_s9";
            }
        }
    } catch (e) { }
}
function setHomepage(pageURL) {
    if (document.all) {
        document.body.style.behavior = 'url(#default#homepage)';
        document.body.setHomePage(pageURL);
    }
    else if (window.sidebar) {
        if (window.netscape) {
            try {
                netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
            }
            catch (e) {
                alert("该操作被浏览器拒绝，如果想启用该功能，请在地址栏内输入 about:config,然后将项signed.applets.codebase_principal_support 值该为true");
            }
        }
        var prefs = Components.classes['@mozilla.org/preferences-service;1'].getService(Components.interfaces.nsIPrefBranch);
        prefs.setCharPref('browser.startup.homepage', pageURL);
    }
}

function AddFavorite(sURL, sTitle) {
    try {
        window.external.addFavorite(sURL, sTitle);
    }
    catch (e) {
        try {
            window.sidebar.addPanel(sTitle, sURL, "");
        }
        catch (e) {
            alert("加入收藏失败，请使用Ctrl+D进行添加");
        }
    }
}
//sfHover = function () {
//	var sfEls = document.getElementById("web_nav").getElementsByTagName("LI");
//	for (var i=0; i<sfEls.length; i++) {
//		sfEls[i].onmouseover=function() {
//			this.className = (this.className ? this.className + " " : "") + "sfhover";
//		}
//		sfEls[i].onmouseout=function() {
//			this.className = this.className.replace(/\s*?\bsfhover\b/, "");
//		}
//	}
//}
//document.write('<link href="//users.titan007.com/Styles/head_pubic.css" rel="stylesheet" type="text/css" />');
//document.write('<div id="bf_adtop" style="text-align:center; display:none;padding-bottom: 3px;width:950px;background-color:white;"></div>');
//document.write('<div id="lottory_menu"><div id="stop" style="padding-left:5px"><div id="TimeZone" style="float:left" onclick="SelectTimeZone(&#39;timeZone/timezone_gb.htm&#39;)" title="点击：时区设置">GMT+0800</div>');
//document.write('<iframe style="float:left;" src="//users.titan007.com/users/bf_header.aspx?r=007" frameborder=0 scrolling=no width="555px" height="29px" allowTransparency="true" >');
//document.write(' </iframe>');

//document.write('<div style="float:right;" onmousemove="showhideul2(1)" onmouseout="showhideul2(0)"> | <a href="javascript:void(0);">关注收藏</a><ul id="ulselect2" class="kops2" style="display:none;"><li><a href="//weibo.com/bet007com" target="_blank" >微博关注</a></li><li><a href="javascript:AddFavorite(\'//www.titan007.com/\',\'球探网-专业体育彩票数据\');">主网收藏</a></li><li><a href="javascript:AddFavorite(\'//www.titan007.com\',\'球探网-专业体育彩票数据\');">备用收藏</a></li></ul></div>');
//document.write('<div style="float: right;">');
//document.write('| <a href="//www.titan007.com/about/about.html" target="_blank">业务合作</a>');
//document.write('</div>');
//document.write('<div style="float:right;"><a href="//www.titan007.com/app/" target="_blank">手机比分</a></div>');
////document.write('<div style="float: right;">');
////document.write('<a title="设置本站为浏览器首页" href="javascript:setHomepage(\'//www.titan007.com\');">设为首页</a> | ');
////document.write('</div>');
//document.write('</div></div>');

//if (window.attachEvent) window.attachEvent("onload", sfHover);
var homePage = "//live.titan007.com/";
var enUrl = "//www.nowgoal.com";
var name = "足球比分";
var adUrl = '|<a href="//www.apk007.com/" target="_blank">手机娱乐市场</a>';
try {
    if (t == 2) {
        homePage = "//lq3.titan007.com/nba.htm";
        enUrl = "//nowgoal.com/nba.htm";
        name = "篮球比分";
        adUrl = "";
    }
}
catch (e) { }
//控制菜单8：30--18：00不显示菜单，如不需要的此时内隐藏，注释掉以下代码即可
var showMenu = true;
//var da = new Date();
//if ((da.getHours() == 8 && da.getMinutes() >= 30) || da.getHours() > 8)
// {
//if (da.getHours() < 18) 
// {
//  showMenu=false;
//}
//}
//document.write('<div id="site-header"><div class="sitenav-wrap"><div class="sitenav-body"><h1><a href="//www.titan007.com"></a></h1>');
//document.write('<ul class="sitenav">');
//document.write('<li><a id="one-level-0" href="//www.titan007.com/">首页</a></li>');
//document.write('<li><a id="one-level-1" class="one-selected"  href="//live.titan007.com/" target="_blank">足球</a></li>');
//document.write('<li><a id="one-level-2" href="//lq3.titan007.com/nba.htm" target="_blank">篮球</a></li>');
//document.write('<li><a id="one-level-3" href="//bf.titan007.com/tennis.htm" target="_blank">网球</a></li>');
///*document.write('<li><a id="one-level-4" href="//dj.titan007.com/" target="_blank">电竞</a></li>');*/
//document.write('<li><a id="one-level-5" href="//sports.titan007.com/vollyball.shtml" target="_blank">排球</a></li>');
//document.write('<li><a id="one-level-6" href="//sports.titan007.com/baseball.shtml" target="_blank">棒球</a></li>');
//document.write('<li><a id="one-level-7" href="//sports.titan007.com/PingPong.shtml" target="_blank">乒乓球</a></li>');
//document.write('<li><a id="one-level-8" href="//sports.titan007.com/Badminton.shtml" target="_blank">羽毛球</a></li>');
//document.write('<li><a id="one-level-9" href="//sports.titan007.com/snooker.htm" target="_blank">斯诺克</a></li>');
//document.write('<li><a id="one-level-10" href="//sports.titan007.com/football.shtml" target="_blank">美式足球</a></li>');
//document.write('<li><a id="one-level-11" href="//sports.titan007.com/hockey.shtml" target="_blank">冰球</a></li>');
//document.write('<li><a id="one-level-12"  href="//f1.titan007.com/f1_bf.aspx" target="_blank">赛车</a></li>');
//document.write('</ul></div></div>');
//document.write('<div id="site-header-two" class="sitenav-secondary-wrap"><div class="sitenav-body"><span class="sports-data">专业体育数据</span>');
//document.write('<!--足球--><ul id="site-header-two-soccer" class="sitenav-secondary soccer" style="display:block">');
//document.write('<li><a id="two-soccer-level-0"  href="//live.titan007.com/" target="_blank"  class="two-selected">即时比分</a></li>');
//document.write('<li><a id="two-soccer-level-1" href="//jc.titan007.com/index.aspx" target="_blank">竞足</a></li>');
////document.write('<li class="drop-list"><a id="two-soccer-level-2" href="//pl.zqsos.com/" target="_blank" >指数<i></i></a>');
//document.write('<div class="subs"><a href="//pl.zqsos.com/" target="_blank">足球指数</a><a href="//op1.titan007.com/" target="_blank">足球百家</a>');
//document.write('<a href="//zq.titan007.com/cn/League/36.html" target="_blank">让球盘路</a><a href="//pl.zqsos.com/champion/index.aspx" target="_blank">冠军指数</a>');
//document.write('<a href="//pl.zqsos.com/betfa/index.aspx" target="_blank">必发指数</a></div></li>');
//document.write('<li class="drop-list"><a id="two-soccer-level-3" href="//zq.titan007.com/info/index.htm" target="_blank">资料库<i></i></a>');
//document.write('<div class="subs two-col">');
//document.write('<a href="//zq.titan007.com/info/index.htm" target="_blank">足球</a><a href="//zq.titan007.com/cn/League/36.html" target="_blank">英超</a>');
//document.write('<a href="//zq.titan007.com/cn/League/34.html" target="_blank">意甲</a><a href="//zq.titan007.com/cn/League/8.html" target="_blank">德甲</a>');
//document.write('<a href="//zq.titan007.com/cn/League/31.html" target="_blank">西甲</a><a href="//zq.titan007.com/cn/League/11.html" target="_blank">法甲</a>');
//document.write('<a href="//2022.titan007.com" target="_blank">世界杯</a><a href="//zq.titan007.com/cn/League/60.html" target="_blank">中超</a>');
//document.write('<a href="//zq.titan007.com/cn/CupMatch/192.html" target="_blank">亚冠杯</a><a href="//zq.titan007.com/cn/zh/yingchao.html" target="_blank">转会记录</a>');
//document.write('<a href="//zq.titan007.com/cn/paiming.html" target="_blank">世界排名</a><a href="//zq.titan007.com/zhibo.html" target="_blank">电视直播表</a>');
//document.write('</div></li>');
//document.write('<li><a id="two-soccer-level-4" href="//quan.titan007.com/" target="_blank">球圈</a></li><li class="vguess"><i class="new">NEW</i><a id="two-soccer-level-5" href="//guess2.titan007.com/" target="_blank">V猜球</a></li>');
//document.write('<li><a id="two-soccer-level-6" href="//ba2.titan007.com/" target="_blank">球吧</a></li><li><a id="two-soccer-level-7" href="//v.titan007.com/" target="_blank">V推荐</a></li>');
//document.write('<li><a id="two-soccer-level-8" href="//2022.titan007.com" target="_blank">世界杯</a></li><li><a id="two-soccer-level-8" href="//ai.titan007.com/" style="color:#ff5106;" target="_blank">AI预测</a></li></ul>');
//document.write('<!--篮球-->');
//document.write('<ul id="site-header-two-basketball" class="sitenav-secondary basketball"><li><a id="two-basketball-level-0" href="//lq3.titan007.com/nba.htm" target="_blank">即时比分</a></li><li><a id="two-basketball-level-1" href="//jc.titan007.com/index.aspx" target="_blank">竞篮</a></li><li class="drop-list"><a id="two-basketball-level-2" href="//pl.zqsos.com/" target="_blank">指数<i></i></a><div class="subs"><a href="//nba.titan007.com/odds/index.aspx" target="_blank">篮球指数</a><a href="//nba.titan007.com/1x2/" target="_blank">篮球百家</a></div></li><li class="drop-list"><a id="two-basketball-level-3" href="//nba.titan007.com/" target="_blank">资料库<i></i></a>');
//document.write('<div class="subs two-col">');
//document.write('<a href="//nba.titan007.com/" target="_blank">篮球</a><a href="//nba.titan007.com/League/index_cn.aspx?SclassID=1" target="_blank">NBA</a>');
//document.write('<a href="//nba.titan007.com/cn/cupmatch.aspx?SclassID=7" target="_blank">EURO</a><a href="//nba.titan007.com/League/index_cn.aspx?SclassID=5" target="_blank">CBA</a>');
//document.write('</div></li>');
//document.write('<li style="display:none;"><a id="two-basketball-level-4" href="//guess2.titan007.com/" target="_blank">球圈</a></li><li><a id="two-basketball-level-5" href="//guess2.titan007.com/basket/" target="_blank">V猜球</a></li><li><a id="two-basketball-level-6" href="//ba2.titan007.com/?ball=2" target="_blank">球吧</a></li><li><a id="two-basketball-level-7" href="//v.titan007.com/?ball=2" target="_blank">V推荐</a></li></ul>');
//document.write('<!--网球-->');
//document.write('<ul id="site-header-two-tennis" class="sitenav-secondary tennis"><li><a href="//bf.titan007.com/tennis.htm" target="_blank">即时比分</a></li><li><a href="//tennis1.titan007.com/" target="_blank">资料库</a></li></ul>');
////document.write('<!--电竞-->');
////document.write('<ul id="site-header-two-game" class="sitenav-secondary game"><li><a href="//dj.titan007.com/" target="_blank">即时比分</a></li><li><a href="//dj.titan007.com/" target="_blank">资料库</a></li></ul>');
//document.write('<!--排球-->');
//document.write('<ul id="site-header-two-volleyball" class="sitenav-secondary volleyball"><li><a href="//sports.titan007.com/vollyball.aspx" target="_blank">即时比分</a></li><li><a href="#" target="_blank">资料库</a></li></ul>');
//document.write('<!--棒球-->');
//document.write('<ul id="site-header-two-baseball" class="sitenav-secondary baseball"><li><a href="//sports.titan007.com/baseball.aspx" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/BB_Default.aspx?SclassID=1" target="_blank">资料库</a></li></ul>');
//document.write('<!--乒乓球-->');
//document.write('<ul id="site-header-two-tabletennis" class="sitenav-secondary tabletennis"><li><a href="//sports.titan007.com/pingpong.aspx" target="_blank">即时比分</a></li><li><a href="#" target="_blank">资料库</a></li></ul>');
//document.write('<!--羽毛球-->');
//document.write('<ul id="site-header-two-badminton" class="sitenav-secondary badminton"><li><a href="//sports.titan007.com/shuttlecock.aspx" target="_blank">即时比分</a></li><li><a href="#" target="_blank">资料库</a></li></ul>');
//document.write('<!--斯诺克-->');
//document.write('<ul id="site-header-two-snooker" class="sitenav-secondary snooker"><li><a href="//sports.titan007.com/snooker.htm" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/SnookerDB.aspx" target="_blank">资料库</a></li></ul>');
//document.write('<!--美式足球-->');
//document.write('<ul id="site-header-two-football" class="sitenav-secondary football"><li><a href="//sports.titan007.com/football.aspx" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/FB_Default.aspx?SclassID=1" target="_blank">资料库</a></li></ul>');
//document.write('<!--冰球-->');
//document.write('<ul id="site-header-two-hockey" class="sitenav-secondary hockey"><li><a href="//sports.titan007.com/cn/scorePage/IsHockey.aspx" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/Default.aspx?SclassID=187" target="_blank">资料库</a></li></ul>');
//document.write('<!--赛车-->');
//document.write('<ul id="site-header-two-racing" class="sitenav-secondary racing"><li><a href="//f1.titan007.com/f1_bf.aspx" target="_blank">即时比分</a></li><li><a href="//f1.titan007.com/f1/Live.aspx" target="_blank" >资料库</a></li></ul>');
//document.write('</div></div></div>');

//版头
//document.writeln("  <div id='ad'>");
//if(window.location.href.toLowerCase().indexOf("nba")>0 || window.location.href.toLowerCase().indexOf("basket")>0) {
//	document.writeln("");
//	document.writeln("");
//        document.writeln("<a href='//www.838555.com/' target='_blank'><img src='//img.titan007.com/ad/838555.gif' border='0'></a>    <a href='//www.365tylc.com/' target='_blank'><img src='//img2.titan007.com/image/365tylc.gif' border='0'></a>");

//}
//if (window.location.href.toLowerCase().indexOf("sport") > 0 || window.location.href.toLowerCase().indexOf("tennis") > 0 || window.location.href.toLowerCase().indexOf("golf") > 0 || window.location.href.toLowerCase().indexOf("f1") > 0) {
//}
//else {
//}
//document.writeln("    <div style='clear:both'></div>");
//document.writeln("  </div>");
//document.writeln("</div>");


function MM_findObj(n, d) { //v4.01
    var p, i, x; if (!d) d = document; if ((p = n.indexOf("?")) > 0 && parent.frames.length) {
        d = parent.frames[n.substring(p + 1)].document; n = n.substring(0, p);
    }
    if (!(x = d[n]) && d.all) x = d.all[n]; for (i = 0; !x && i < d.forms.length; i++) x = d.forms[i][n];
    for (i = 0; !x && d.layers && i < d.layers.length; i++) x = MM_findObj(n, d.layers[i].document);
    if (!x && d.getElementById) x = d.getElementById(n); return x;
}

function MM_showHideLayers() { //v6.0
    var i, p, v, obj, args = MM_showHideLayers.arguments;
    for (i = 0; i < (args.length - 2); i += 3) if ((obj = MM_findObj(args[i])) != null) {
        v = args[i + 2];
        if (obj.style) { obj = obj.style; v = (v == 'show') ? 'visible' : (v == 'hide') ? 'hidden' : v; }
        obj.visibility = v;
    }
}
if (!window.createPopup) {
    var __createPopup = function () {
        var SetElementStyles = function (element, styleDict) {
            var style = element.style;
            for (var styleName in styleDict) style[styleName] = styleDict[styleName];
        }
        var eDiv = document.createElement('div');
        SetElementStyles(eDiv, { 'position': 'absolute', 'top': 0 + 'px', 'left': 0 + 'px', 'width': 0 + 'px', 'height': 0 + 'px', 'zIndex': 9999, 'display': 'none', 'overflow': 'hidden' });
        eDiv.body = eDiv;
        var opened = false;
        var setOpened = function (b) {
            opened = b;
        }
        var getOpened = function () {
            return opened;
        }
        var getCoordinates = function (oElement) {
            var coordinates = { x: 0, y: 0 };
            while (oElement) {
                coordinates.x += oElement.offsetLeft;
                coordinates.y += oElement.offsetTop;
                oElement = oElement.offsetParent;
            }
            return coordinates;
        }
        return {
            htmlTxt: '',
            document: eDiv,
            isOpen: getOpened(),
            isShow: false,
            hide: function () {
                SetElementStyles(eDiv, { 'top': 0 + 'px', 'left': 0 + 'px', 'width': 0 + 'px', 'height': 0 + 'px', 'display': 'none' });
                eDiv.innerHTML = '';
                this.isShow = false;
            },
            show: function (iY, iX, iWidth, iHeight, oElement) {
                if (!getOpened()) {
                    document.body.appendChild(eDiv); setOpened(true);
                };
                this.htmlTxt = eDiv.innerHTML;
                if (this.isShow) { this.hide(); };
                eDiv.innerHTML = this.htmlTxt;
                var coordinates = getCoordinates(oElement);
                eDiv.style.top = (iX + coordinates.x) + 'px';
                eDiv.style.left = (iY + coordinates.y) + 'px';
                eDiv.style.width = iWidth + 'px';
                eDiv.style.height = iHeight + 'px';
                eDiv.style.display = 'block';
                this.isShow = true;
            }
        }
    }
    window.createPopup = function () {
        return __createPopup();
    }
}
function getCookie22(name) {
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
function getCookie(name) {
    var cname = name;
    var dc = document.cookie;
    if (dc.length > 0) {
        var arrCook = dc.split(';');
        for (var i = 0; i < arrCook.length; i++) {
            arrCook[i] = arrCook[i].replace(/^\s+|\s+$/g, "");
            var arrOne = arrCook[i].split('=');
            if (arrOne.length > 1) {
                if (arrOne[0] == cname)
                    return arrOne[1];
            }
        }
    }
    return null;
}
function writeCookie(name, value) {
    var expire = "";
    var hours = 365;
    expire = new Date((new Date()).getTime() + hours * 3600000);
    expire = ";path=/;expires=" + expire.toGMTString();
    document.cookie = name + "=" + value + expire; //escape(
}
function writeCommonCookie(name, value) {
    var expire = "";
    var hours = 365;
    expire = new Date((new Date()).getTime() + hours * 3600000);
    expire = ";path=/;domain=.titan007.com;expires=" + expire.toGMTString();
    document.cookie = name + "=" + value + expire; //escape(
}
//显示进球窗口
var startani_C, startani_A, startani_B, pop_TC;
var oPopup;
try { oPopup = window.createPopup(); }
catch (e) { }

function ShowCHWindow(str, matchnum) {
    imagewidth = 481;
    imageheight = 28 + 34 * matchnum;
    var st;

    st = "<table width=480 border=0 cellpadding=1 cellspacing=0 bgcolor=#E0B22B id=floatHGScoreDiv>";
    st = st + "  <tr><td><table width=478 border=0 cellpadding=0 cellspacing=0>";
    st = st + "      <tr><td colspan=6><img src=image/bf_open.gif?ver=1 width=478></td></tr>";
    st = st + str;
    // st=st + "<tr bgcolor=#FFFFFF height=20 align=center><td colspan=6><font color=red>广告：</font><font color=blue>编辑88</font></td></tr>";
    st = st + "    </table></td>";
    st = st + "  </tr>";
    st = st + "</table>";
    st = st + "<style type='text/css'>";
    st = st + "#floatHGScoreDiv td {font-family: 'Tahoma', '宋体';font-size: 13px;}";
    st = st + "#floatHGScoreDiv .line td { border-bottom:solid 1px #FFD8CA; line-height:32px;}";
    st = st + "</style>";

    x = 280;
    y = 1;
    var winLoc = 0;
    var scoreTop = document.documentElement.scrollTop || document.body.srcollTop;
    if (scoreTop == undefined)
        scoreTop = 0;
    try { winLoc = document.getElementById("winLocation").selectedIndex; }
    catch (e) { }
    switch (winLoc) {
        case 0:
            x = (document.body.clientWidth - imagewidth) / 2;
            y = 1 + scoreTop;
            break;
        case 1:
            x = (document.body.clientWidth - imagewidth) / 2;//screen.width
            y = screen.height - imageheight - 30;
            break;
        case 2:
            x = 2;
            y = (screen.height - imageheight) / 2;
            break;
        case 3:
            x = document.body.clientWidth - imagewidth - 2;
            y = (screen.height - imageheight) / 2;
            break;
        case 4:
            x = 1;
            y = 1 + scoreTop;
            break;
        case 5:
            x = document.body.clientWidth - imagewidth - 2;
            y = 1 + scoreTop;
            break;
        case 6:
            x = 1;
            y = screen.height - imageheight - 30;
            break;
        case 7:
            x = document.body.clientWidth - imagewidth - 2;
            y = screen.height - imageheight - 30;
            break;
    }

    oPopupBody = oPopup.document.body;
    oPopupBody.innerHTML = st;
    oPopupBody.style.cursor = "pointer";
    oPopupBody.title = "点击关闭";
    oPopupBody.onclick = dismisspopup;
    oPopupBody.oncontextmenu = dismisspopup;
    pop_TC = 40;
    pop();
}

function pop() {
    try {
        oPopup.show(x, y, imagewidth, imageheight);
        startani_A = setTimeout("pop()", 300);  //显示15秒
        if (pop_TC < 0) { dismisspopup(); };
        pop_TC = pop_TC - 1;
    } catch (e) { }
}
function dismisspopup() {
    clearTimeout(startani_A);
    oPopup.hide();
}

function showgoallist(ID) {
    var theUrl;
    try {
        var parm = "";
        var matchindex = getDataIndex(ID);
        if (A[matchindex][13] == "0" && A[matchindex][27] == "1")
            parm = "?lineup=1";
        if (Config.language == 0)
            theUrl = "/detail/" + ID + "cn.htm";
        else if (Config.language == 2)
            theUrl = "/detail/" + ID + "sb.htm";
        else
            theUrl = "/detail/" + ID + ".htm";
    }
    catch (e) {
        if (location.href.split('_').length == 2)
            theUrl = "/detail/" + ID + "cn.htm";
        else
            theUrl = "/detail/" + ID + ".htm";
    }
    window.open(theUrl + parm, "", "");
}
function analysis(ID) {
    var theURL;
    try {
        if (Config.language == 0)
            theURL = "//zq.titan007.com/analysis/" + ID + "cn.htm";
        else if (Config.language == 1)
            theURL = "//zq.titan007.com/analysis/" + ID + ".htm";
        else
            theURL = "//zq.titan007.com/analysis/" + ID + "sb.htm";
    }
    catch (e) {
        if (location.href.split('_').length == 2)
            theURL = "//zq.titan007.com/analysis/" + ID + "cn.htm";
        else
            theURL = "//zq.titan007.com/analysis/" + ID + ".htm";
    }
    window.open(theURL);
}
function AsianOdds(ID) {
    var theURL = "//vip.titan007.com/AsianOdds_n.aspx?id=" + ID;
    window.open(theURL);
}
function TotalOdds(ID) {
    var theURL = "//vip.titan007.com/OverDown_n.aspx?id=" + ID;
    window.open(theURL);
}

function EuropeOdds(ID) {
    var theURL = "//op1.titan007.com/oddslist/" + ID + ".htm";
    window.open(theURL);
}

function TeamPanlu_10(ID) {
    var theURL = "//bf.titan007.com/panlu/" + ID + ".htm";
    window.open(theURL, "", "width=640,height=700,top=10,left=100,resizable=yes,scrollbars=yes");
}
function advices(ID) {
    var theURL = "//ba2.titan007.com/linkmatch/1/" + ID + ".html";
    window.open(theURL);
}



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
