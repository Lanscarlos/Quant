# titan007 赛事筛选状态持久化机制分析

> 分析页面：`https://live.titan007.com/oldIndexall.aspx`

## 概述

该页面使用 **Cookie + localStorage 双机制** 来保存筛选状态，刷新后状态得以恢复。具体分为 3 层。

## 1. 全局配置 — Cookie `win007BfCookie`

`commonWs.js` 中 `Config.writeCookie()` 将 20 个配置字段用 `^` 拼接，写入名为 `win007BfCookie` 的 Cookie（有效期 365 小时）：

```
language^rank^explain^redcard^showYellowCard^detail^vs^sound^winLocation^style^oddsSound^guestSound^showSbOddsDetail^oldOrNew^haveLetGoal^haveTotal^haveEurope^isSimple^cornerPopup^onlyTopShowWin
```

页面加载时由 `Config.getCookie("oldindex")` 读取并恢复。其中 **`isSimple`** 字段控制"热门/完整"按钮状态：

| 值  | 含义       |
|-----|----------|
| 1   | 热门       |
| 0   | 完整       |
| -1  | 自定义筛选 |

### 关键代码

```js
// commonWs.js — 写入
Config.writeCookie = function () {
    var value = this.language + "^" + this.rank + "^" + ... + "^" + this.onlyTopShowWin;
    writeCookie("win007BfCookie", value);
}

// commonWs.js — 读取
Config.getCookie = function (type) {
    var Cookie = getCookie("win007BfCookie");
    var Cookie = Cookie.split("^");
    if (Cookie.length != 20) { writeCookie("win007BfCookie", null); }
    else {
        this.language = parseInt(Cookie[0]);
        this.rank = parseInt(Cookie[1]);
        // ... 共 20 个字段
    }
    getConditonList(1); // 顺带读取筛选条件 Cookie
}
```

## 2. 赛事筛选条件 — Cookie `FS007Filter`

`writeConditionCookie()` 将筛选条件写入 `FS007Filter` Cookie：

```
kind^oddsType^idList^sclassType
```

| 字段         | 含义                                                        |
|--------------|-----------------------------------------------------------|
| `kind`       | 1 = 联赛筛选, 2 = 国家筛选, 3 = 盘口筛选                  |
| `oddsType`   | 比赛状态：0 全部 / 1 进行中 / 2 已完场 / 3 未开场 / 4 滚球 |
| `idList`     | 选中的联赛 ID 列表，格式 `_id1_id2_id3_`                   |
| `sclassType` | 0 所有 / 1 足彩 / 2 竞足 / 3 单场                          |

### 过期策略

这个 Cookie 的**过期时间是每天上午 10:30 自动重置**：

```js
// commonWs.js — GetCookieTime()
function GetCookieTime() {
    var d1 = new Date();
    var d2 = new Date();
    if (d1.getHours() * 100 + d1.getMinutes() > 1030) {
        d2 = new Date(d1.getFullYear(), d1.getMonth(), d1.getDate() + 1, 10, 30, 0);
    } else {
        d2 = new Date(d1.getFullYear(), d1.getMonth(), d1.getDate(), 10, 30, 0);
    }
    return d2 - d1;
}
```

### 关键代码

```js
// 写入
function writeConditionCookie(kind, oddsType, idList, sclassType) {
    writeCookie2("FS007Filter", kind + "^" + oddsType + "^" + idList + "^" + sclassType, false, GetCookieTime());
}

// 读取
function getConditonList(kind) {
    var Fs007Filter = getCookie("FS007Filter");
    if (Fs007Filter != "") {
        var arrFilter = Fs007Filter.split("^");
        Config.selectConditonType = arrFilter[0];
        Config.sclassType = arrFilter[3];
        Config.secondSclassType = arrFilter[1];
    }
}
```

## 3. 隐藏比赛列表 — localStorage `Bet007live_hiddenID`

`writeLocalStorage()` 将被隐藏的比赛 ID 列表写入 `localStorage`（带过期时间，默认 365 小时）：

```js
localStorage.setItem("Bet007live_hiddenID", JSON.stringify({
    value: "_id1_id2_id3_",  // base36 编码的比赛 ID
    expiry: now.getTime() + 365 * 3600000
}));
```

### localStorage 封装

```js
function getLocalStorage(key) {
    var itemStr = localStorage.getItem(key);
    if (itemStr != null) {
        var item = JSON.parse(itemStr);
        if (new Date().getTime() > item.expiry) {
            localStorage.removeItem(key); // 过期清除
        } else {
            return item.value;
        }
    }
    return null;
}

function writeLocalStorage(key, value, expiryTime) {
    if (expiryTime == undefined) expiryTime = 365 * 3600000;
    var item = {
        value: value,
        expiry: new Date().getTime() + expiryTime,
    };
    localStorage.setItem(key, JSON.stringify(item));
}
```

### base36 编码压缩

ID 存储前会做 base36 编码以减小体积，读取时再解码：

```js
// 编码：十进制 → base36
function enCookieSchedule(ids) {
    var arrIds = ids.split('_');
    for (var i = 0; i < arrIds.length; i++) {
        tempIds += parseInt(id).toString(36) + "_";
    }
    return tempIds;
}

// 解码：base36 → 十进制
function deCookieSchedule(ids) {
    var arrIds = ids.split('_');
    for (var i = 0; i < arrIds.length; i++) {
        tempIds += parseInt(id, 36).toString() + "_";
    }
    return tempIds;
}
```

### 降级策略

如果浏览器不支持 localStorage，则 fallback 到 Cookie：

```js
var localStorageEnable = isLocalStorageAvailable();

function writeLocalStorage(key, value, expiryTime) {
    if (localStorageEnable) {
        localStorage.setItem(key, JSON.stringify(item));
    } else {
        writeCookie(key, value); // fallback
    }
}
```

## 数据流总结

```
用户点击"确定" (SelectOK)
  ├─ 遍历联赛 checkbox，构建 hiddenID（显示的比赛 ID 列表）
  ├─ writeLocalStorage("Bet007live_hiddenID", encoded_ids)   ← localStorage
  ├─ writeConditionCookie(kind, state, sIDList, sclassType)  ← Cookie: FS007Filter
  └─ Config.writeCookie()                                    ← Cookie: win007BfCookie

页面刷新加载 (ShowBf)
  ├─ Config.getCookie("oldindex")           → 读 Cookie win007BfCookie 恢复全局配置
  │   └─ getConditonList(1)                 → 读 Cookie FS007Filter 恢复筛选条件
  ├─ getLocalStorage("Bet007live_hiddenID") → 读 localStorage 恢复隐藏列表
  └─ MakeTable(true)                        → 根据 hiddenID 和 Config 决定每行显示/隐藏
```

## 涉及的存储 Key 一览

| Key                              | 存储位置     | 有效期            | 用途               |
|----------------------------------|------------|-------------------|--------------------|
| `win007BfCookie`                 | Cookie     | 365 小时          | 全局配置（20 个字段） |
| `FS007Filter`                    | Cookie     | 到次日 10:30 重置  | 赛事筛选条件         |
| `Bet007live_hiddenID`            | localStorage | 365 小时          | 隐藏的比赛 ID 列表   |
| `Bet007live_concernId_AllDomain` | Cookie     | —                 | 置顶的比赛 ID 列表   |

## 结论

**不是浏览器缓存（HTTP Cache），而是主动使用 Cookie + localStorage 的客户端持久化方案。** Cookie 存全局配置和筛选条件，localStorage 存具体隐藏的比赛 ID。页面每次加载时从这些存储中读取状态，在 JS 渲染阶段决定每行比赛的显示/隐藏。

## 相关源码文件

已下载到本地 `docs/html/` 目录供复盘：

- `docs/html/oldIndexall.html` — 页面 HTML
- `docs/html/oldIndexall_func.js` — 比赛渲染辅助函数
- `docs/html/oldIndexall_commonWs.js` — **核心逻辑**（Config、筛选、持久化、WebSocket）
- `docs/html/oldIndexall_NewTop.js` — 顶部导航
- `docs/html/oldIndexall_headcommon.js` — 公共头部