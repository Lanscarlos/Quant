function loadCSS(url) {
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = url;
    document.head.appendChild(link);
}

loadCSS("//img.titan007.com/img2/css/headcommon.css?ver=4");

document.write('<div class="navigationMenu" id="menu"><div id="topMenuContent" class="menuContent"><a href="//www.titan007.com" class="logo"><img src="//img.titan007.com//Images/newLogo.png" alt="新球体育"></a>');
document.write('<ul class="sitenav">');
document.write('<li><a id="one-level-0" href="//www.titan007.com/" target="_blank">首页</a></li>');
document.write('<li><a id="one-level-1" href="//live.titan007.com/" target="_blank">足球直播</a></li>');
document.write('<li><a id="one-level-2" href="//lq3.titan007.com/nba.htm" target="_blank">篮球直播</a></li>');
//document.write('<li><a id="one-level-5" href="//quan.titan007.com/" target="_blank">球圈</a></li>');
document.write('<li><a id="one-level-6" href="//qiuba.titan007.com/" target="_blank">球吧</a></li>');
document.write('<li><a id="one-level-7" href="//v.titan007.com/" target="_blank">分析师</a></li>');
document.write('<li><a id="one-level-10" href="//www.titan007.com/articles" target="_blank">资讯</a></li>');
document.write('<li class="drop-list"><a id="one-level-8" href="//guess2.titan007.com/">V猜球<i></i></a><div class="subs"><a href="//guess2.titan007.com/" target="_blank">足球</a><a href="//guess2.titan007.com/basket/" target="_blank">篮球</a></div></li>');
//document.write('<li><a id="one-level-9" href="//ai.titan007.com/" target="_blank">AI预测</a></li>');
document.write('<li><i class="icon">新</i><a id="one-level-9" href="//aiplus.titan007.com/?from=0" target="_blank">AI预测</a></li>');
//document.write('<li><a id="one-level-11" href="//2025.titan007.com" target="_blank">世俱杯</a></li>');
document.write('<li class="drop-list"><a id="one-level-4" href="//zq.titan007.com/info/index_cn.htm">资料库<i></i></a><div class="subs"><a href="//zq.titan007.com/info/index.htm" target="_blank">足球</a>');
document.write('<a href="//nba.titan007.com/" target="_blank">篮球</a></div></li>');
//document.write('<li><i class="icon">热</i><a id="one-level-10" href="//2024.titan007.com" target="_blank">欧洲杯</a></li>');
document.write('<li class="pcShow"><a href="//bf.titan007.com/tennis.htm" target="_blank">网球</a></li>');
document.write('<li class="pcShow"><a href="//sports.titan007.com/vollyball.aspx" target="_blank">排球</a></li>');
document.write('<li class="pcShow"><a href="//sports.titan007.com/baseball.aspx" target="_blank">棒球</a></li>');
document.write('<li class="pcShow"><a href="//sports.titan007.com/cn/scorePage/IsHockey.aspx" target="_blank">冰球</a></li>');
document.write('<li class="pcShow"><a href="//f1.titan007.com/f1_bf.aspx" target="_blank">赛车</a></li>');
document.write('<li class="pcShow"><a href="//sports.titan007.com/pingpong.aspx" target="_blank">乒乓球</a></li>');
document.write('<li class="pcShow"><a href="//sports.titan007.com/shuttlecock.aspx" target="_blank">羽毛球</a></li>');
document.write('<li class="pcShow"><a href="//sports.titan007.com/snooker.htm" target="_blank">斯诺克</a></li>');
document.write('<li class="pcShow"><a href="//sports.titan007.com/football.shtml" target="_blank">橄榄球</a></li>');
document.write('<li class="drop-list pcHide"><a id="one-level-11"  href="">更多<i></i></a>');
document.write('<div class="subs two-col">');
document.write('<a href="//bf.titan007.com/tennis.htm" target="_blank">网球</a>');
document.write('<a href="//sports.titan007.com/vollyball.aspx" target="_blank">排球</a>');
document.write('<a href="//sports.titan007.com/baseball.aspx" target="_blank">棒球</a>');
document.write('<a href="//sports.titan007.com/cn/scorePage/IsHockey.aspx" target="_blank">冰球</a>');
document.write('<a href="//f1.titan007.com/f1_bf.aspx" target="_blank">赛车</a>');
document.write('<a href="//sports.titan007.com/pingpong.aspx" target="_blank">乒乓球</a>');
document.write('<a href="//sports.titan007.com/shuttlecock.aspx" target="_blank">羽毛球</a>');
document.write('<a href="//sports.titan007.com/snooker.htm" target="_blank">斯诺克</a>');
document.write('<a href="//sports.titan007.com/football.shtml" target="_blank">橄榄球</a>');
document.write('</div></li></ul>');
//http://192.168.10.43:81/    document.write('<script src="//users.titan007.com/users/bfheader.aspx"></script>');
document.write('<script src="//users.titan007.com/users/bfheader.aspx?backurl='+encodeURIComponent(window.location.href)+'"></script>');
document.write('</div></div>');
//二级导航
// document.write('<div id="site-header-two" class="sitenav-secondary-wrap"><div class="sitenav-body"><span class="sports-data">专业体育数据</span>');
//比分页显示时区，其他页面显示描述
document.write('<div id="site-header-two" class="sitenav-secondary-wrap "><div class="sitenav-body"><div id="TimeZone" style="display:none;" class="sports-data" style="float:left" onclick="SelectTimeZone(\'timeZone/timezone_gb.htm\')" title="点击：时区设置"></div><span id="heardTitle" style="display:none;" class="sports-dataTitle">专业体育数据</span>');




//足球
document.write('<ul id="site-header-two-1" class="sitenav-secondary soccer">');
document.write('<li><a  href="//live.titan007.com/" target="_blank">即时比分</a>');
document.write('<a href="//jc.titan007.com/index.aspx" target="_blank">竞足</a>');
document.write('<a href="//zq.titan007.com/info/index.htm" target="_blank">资料库</a></li>');
document.write('<li>');
document.write('<a href="//zq.titan007.com/cn/League/36.html" target="_blank">英超</a>');
document.write('<a href="//zq.titan007.com/cn/League/34.html" target="_blank">意甲</a><a href="//zq.titan007.com/cn/League/8.html" target="_blank">德甲</a>');
document.write('<a href="//zq.titan007.com/cn/League/31.html" target="_blank">西甲</a><a href="//zq.titan007.com/cn/League/11.html" target="_blank">法甲</a>');
document.write('<a href="//zq.titan007.com/cn/League/60.html" target="_blank">中超</a>');
document.write('</li><li>')
document.write('<a href="//zq.titan007.com/cn/zh/yingchao.html" target="_blank">转会记录</a>');
document.write('<a href="//zq.titan007.com/cn/paiming.html" target="_blank">世界排名</a><a href="//zq.titan007.com/zhibo.html" target="_blank">电视直播表</a>');
document.write('</li></ul>');

//篮球
document.write('<ul id="site-header-two-2" class="sitenav-secondary basketball">');
document.write('<li>');
document.write('<a id="two-basketball-level-0" href="//lq3.titan007.com/nba.htm" target="_blank">即时比分</a>');
document.write('<a id="two-basketball-level-1" href="//jc.titan007.com/nba/index.aspx" target="_blank">竞篮</a>');
document.write('<a id="two-basketball-level-3" href="//nba.titan007.com/" target="_blank">资料库</a></li>');
document.write('<li><a href="//nba.titan007.com/League/index_cn.aspx?SclassID=1" target="_blank">NBA</a>');
document.write('<a href="//nba.titan007.com/League/index_cn.aspx?SclassID=2" target="_blank">WNBA</a>');
document.write('<a href="//nba.titan007.com/League/index_cn.aspx?SclassID=5" target="_blank">CBA</a>');
document.write('<a href="//nba.titan007.com/cn/cupmatch.aspx?SclassID=7" target="_blank">EURO</a>');
document.write('</li></ul>');

//网球
document.write('<ul id="site-header-two-3" class="sitenav-secondary tennis">');
document.write('<li><a href="//bf.titan007.com/tennis.htm" target="_blank">即时比分</a>');
document.write('<a href="//tennis1.titan007.com/" target="_blank">资料库</a>');
document.write('</li>');
document.write('<li><a href="//tennis.titan007.com/League/Default.aspx?p=/League/Ranking/2024/1.htm" target="_blank">世界排名</a>');
document.write('<a href="//tennis.titan007.com/League/Default.aspx?p=/League/Technic/2024/1.htm" target="_blank">技术统计</a>');
document.write('<a href="//tennis.titan007.com/League/Default.aspx?p=/League/Player/2024/1.htm" target="_blank">球员资料</a>');
document.write('<a href="//tennis.titan007.com/League/Default.aspx?ki=1" target="_blank">赛程赛果</a>');
document.write('<a href="//tennis.titan007.com/League/Default.aspx?p=/League/Tour/History.aspx" target="_blank">赛事回顾</a>');
document.write('</li></ul>');


document.write('<!--排球-->');
document.write('<ul id="site-header-two-5" class="sitenav-secondary volleyball"><li><a href="//sports.titan007.com/vollyball.aspx" target="_blank">即时比分</a></li></ul>');
document.write('<!--棒球-->');
document.write('<ul id="site-header-two-6" class="sitenav-secondary baseball"><li><a href="//sports.titan007.com/baseball.shtml" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/BB_Default.aspx?SclassID=1" target="_blank">资料库</a></li></ul>');
document.write('<!--乒乓球-->');
document.write('<ul id="site-header-two-7" class="sitenav-secondary tabletennis"><li><a href="//sports.titan007.com/pingpong.aspx" target="_blank">即时比分</a></li></ul>');
document.write('<!--羽毛球-->');
document.write('<ul id="site-header-two-8" class="sitenav-secondary badminton"><li><a href="//sports.titan007.com/badminton.shtml" target="_blank">即时比分</a></li></ul>');
document.write('<!--斯诺克-->');
document.write('<ul id="site-header-two-9" class="sitenav-secondary snooker"><li><a href="//sports.titan007.com/Snooker.shtml" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/SnookerDB.aspx" target="_blank">资料库</a></li></ul>');
document.write('<!--美式足球-->');
document.write('<ul id="site-header-two-10" class="sitenav-secondary football"><li><a href="//sports.titan007.com/football.shtml" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/FB_Default.aspx?SclassID=1" target="_blank">资料库</a></li></ul>');
document.write('<!--冰球-->');
document.write('<ul id="site-header-two-11" class="sitenav-secondary hockey"><li><a href="//sports.titan007.com/hockey.shtml" target="_blank">即时比分</a></li><li><a href="//sports.titan007.com/Default.aspx?SclassID=187" target="_blank">资料库</a></li></ul>');
document.write('<!--赛车-->');
document.write('<ul id="site-header-two-12" class="sitenav-secondary racing"><li><a href="//f1.titan007.com/f1_schedule.aspx" target="_blank">F1赛事</a></li><li><a href="//f1.titan007.com/f1/infodata/schedule.aspx" target="_blank" >赛程</a></li><li><a href="//f1.titan007.com/f1/infodata/track.aspx" target="_blank" >赛道</a></li><li class="lagbtn"><span onclick="ChangeLang(0)" class="on">简体</span><span onclick="ChangeLang(1)">繁体</span></li></ul>');
document.write('</div></div>');

document.write('<div class="select_d1" id = "TimeZoneList_div" style = "width: 660px;height: 480px; display: none;">');
document.write('<div class="select_d2" style="width: 660px">');
document.write('<p class="select_v1">时区设置</p>');
document.write('<p class="select_v2"><a href="javascript:CloseTimeZoneList()" title="点击关闭">[x] 关闭</a></p>');
document.write('</div>');
document.write('<div class="select_d3" id="TimeZoneList"></div>');
document.write('<div class="select_c1"></div>');
document.write('</div>');

function SelectMenu() {
    var url = window.location.href.toLowerCase();
    var selectLev1 = 0;
    var selectLev2 = 0;
    var ballType = 0;
    var isScore = false;
    if (url.indexOf("lq3.") != -1||url.indexOf("nba") != -1) {
        selectLev1 = 2;
        ballType = 2;
        if (url.indexOf("lq3.") != -1 || url.indexOf("bf.titan007.com") != -1) {
            isScore = true;
            selectLev2 = 0;
        }
        else if (url.indexOf("jc.") != -1)
            selectLev2 = 1;
        else {
            selectLev1 = 4;
            selectLev2 = 2;
        }
        document.getElementById("one-level-4").href = "//nba.titan007.com/index_cn.htm";
        document.getElementById("one-level-8").href = "//guess2.titan007.com/basket/";
    }
    else if (url.indexOf("live.") != -1 || url.indexOf("zq.") != -1 || url.indexOf("info.") != -1 || url.indexOf("jc.titan007.com") != -1 || url.indexOf("bf.titan007.com/football") != -1 || url.indexOf("op1") != -1|| url.indexOf("vip.titan") != -1|| url.indexOf("72:808") != -1) {
        selectLev1 = 1;
        ballType = 1;
        if (url.indexOf("live.") != -1 || url.indexOf("bf.titan007.com") != -1)
            selectLev2 = 0;
        else if (url.indexOf("jc.") != -1)
            selectLev2 = 1;
        else {
            selectLev2 = 2;
            selectLev1 = 4;
        }
        if (url.indexOf("detail") ==-1&&(url.indexOf("live.") != -1))
            isScore = true;
    }
    else if (url.indexOf("sports.titan007.com") != -1) {
        isScore = true;
        if (url.indexOf("infodata") != -1) {
            selectLev2 = 1;
            isScore = false;
        }
        if (url.indexOf("vollyball") != -1)
            selectLev1 = 5;
        else if (url.indexOf("baseball") != -1)
            selectLev1 = 6;
        else if (url.indexOf("pingpong") != -1)
            selectLev1 = 7;
        else if (url.indexOf("badminton") != -1)
            selectLev1 = 8;
        else if (url.indexOf("snooker") != -1){
            selectLev1 = 9;
			isScore=false;
		}
        else if (url.indexOf("football") != -1)
            selectLev1 = 10;
        else if (url.indexOf("hockey") != -1)
            selectLev1 = 11;
    }
    else if (url.indexOf("tennis") != -1) {
        selectLev1 = 3;
        selectLev2 = 1;
        if (url.indexOf("bf.titan007.com") != -1) {
            selectLev2 = 0;
            isScore = true;
        }
    }
    else if (url.indexOf("f1.titan007.com") != -1) {
        selectLev1 = 12;
        if (url.indexOf("f1/infodata/track") != -1)//赛道
            selectLev2 = 2;
        else if (url.indexOf("f1/infodata") != -1)//赛程
            selectLev2 = 1;
    }
    if (selectLev1 > 0 && selectLev1 < 5 && selectLev1 !=3)
        document.getElementById("one-level-" + selectLev1).className = "one-selected";
    if (ballType == 2 && selectLev1 == 4) {
        selectLev1 = 2;
        document.getElementById("one-level-4").href = "//nba.titan007.com/index_cn.htm";
        document.getElementById("one-level-8").href = "//guess2.titan007.com/basket/";
    }
    if (ballType == 1 && selectLev1 == 4)
        selectLev1 = 1;
    if (selectLev1 == 0)
        document.getElementById("site-header-two-1").style.display = "block";
    else {
        document.getElementById("site-header-two-" + selectLev1).style.display = "block";
        var arr = document.getElementById("site-header-two-" + selectLev1).getElementsByTagName("a");
        arr[selectLev2].className = "two-selected";
    }
    if (isScore)
        document.getElementById("TimeZone").style.display = "block";
    else
        document.getElementById("heardTitle").style.display = "block";
}
window.addEventListener('load', function () {
    SelectMenu();
});


