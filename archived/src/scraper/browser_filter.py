"""
通过 Playwright 打开 Edge 浏览器，让用户在页面上做赛事筛选，
然后读取筛选结果（选中的联赛列表和比赛 ID 列表）。

用法:
    from src.scraper.browser_filter import open_filter
    result = open_filter()
    print(result['leagues'])    # 选中的联赛 [{id, name, count}, ...]
    print(result['match_ids'])  # 选中的比赛 ID 列表
"""
from playwright.sync_api import sync_playwright


_URL = "https://live.titan007.com/oldIndexall.aspx"

# 注入页面的 JS: 在筛选面板的"确定"按钮旁边添加一个"导出"按钮
_INJECT_EXPORT_BTN = """
(() => {
    // 赛事筛选面板底部
    const bts = document.querySelector('#Layer2 .bts');
    if (!bts || document.getElementById('btnExport')) return;
    const btn = document.createElement('input');
    btn.type = 'button';
    btn.id = 'btnExport';
    btn.value = '>> 导出到脚本';
    btn.style.cssText = 'background:#e74c3c;color:white;font-weight:bold;border:none;padding:4px 12px;cursor:pointer;margin-left:6px;';
    btn.onclick = () => { window.__exportClicked = true; };
    bts.appendChild(btn);

    // 国家筛选面板底部
    const bts2 = document.querySelector('#DivCountry .bts');
    if (!bts2) return;
    const btn2 = btn.cloneNode(true);
    btn2.id = 'btnExport2';
    btn2.onclick = () => { window.__exportClicked = true; };
    bts2.appendChild(btn2);
})()
"""

# 注入页面的 JS: 收集当前筛选结果
_COLLECT_RESULTS = """
(() => {
    function stripHtml(html) {
        const tmp = document.createElement('div');
        tmp.innerHTML = html || '';
        return tmp.textContent || tmp.innerText || '';
    }

    const result = {
        sclass_type: Config.sclassType,
        match_state: Config.secondSclassType,
        is_simple: Config.isSimple,
        leagues: [],
        match_ids: [],
    };

    // 收集选中的联赛: B[j] 结构 [缩写, 繁体名, ?, 颜色, 拼音, ?, 总场次, 显示场次, ?, 后缀ID, 热门状态, ...]
    for (let j = 1; j <= sclasscount; j++) {
        const el = document.getElementById('myleague_' + j);
        if (!el) continue;
        const parent = el.parentElement;
        if (parent.style.display === 'none') continue;
        if (el.classList.contains('on')) {
            result.leagues.push({
                short: B[j][0],
                name: B[j][Config.language < 2 ? Config.language : 0],
                cid: B[j][4] + B[j][9],
                color: B[j][3],
                count: B[j][6],
                shown: B[j][7],
            });
        }
    }

    // 收集当前可见的比赛
    // A[i] 字段: [0]=ID, [2]=联赛简体, [3]=联赛繁体, [5]=主队简体, [6]=主队繁体,
    //            [8]=客队简体, [9]=客队繁体, [13]=状态, [14]=主队进球, [15]=客队进球,
    //            [37]=主队ID, [38]=客队ID
    const langIdx = Config.language < 2 ? Config.language : 0;
    for (let i = 1; i <= matchcount; i++) {
        if (A[i][0] <= 0) continue;
        const tr = document.getElementById('tr1_' + A[i][0]);
        if (tr && tr.style.display !== 'none') {
            result.match_ids.push({
                match_id: A[i][0],
                league: stripHtml(A[i][2 + langIdx]),
                home_id: A[i][37],
                home: stripHtml(A[i][5 + langIdx]),
                away_id: A[i][38],
                away: stripHtml(A[i][8 + langIdx]),
                state: parseInt(A[i][13]),
                score: A[i][14] + '-' + A[i][15],
            });
        }
    }

    return result;
})()
"""

_SCLASS_LABELS = ["所有", "足彩", "竞足", "单场"]
_STATE_LABELS = ["全部", "进行中", "已完场", "未开场", "滚球"]


def open_filter() -> dict:
    """
    打开 Edge 浏览器进入赛事筛选页面，等待用户操作后返回筛选结果。

    Returns:
        dict: {
            'sclass_type': int,   # 0=所有, 1=足彩, 2=竞足, 3=单场
            'match_state': int,   # 0=全部, 1=进行中, 2=已完场, 3=未开场, 4=滚球
            'is_simple': int,     # 1=热门, 0=完整, -1=自定义
            'leagues': list,      # [{short, name, cid, color, count, shown}, ...]
            'match_ids': list,    # [{match_id, league_short, home_id, home, away_id, away, state, score}, ...]
        }
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=False)
        context = browser.new_context(viewport={"width": 1200, "height": 900})
        page = context.new_page()

        print("正在打开赛事页面...")
        page.goto(_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("#table_live", timeout=60000)

        # 注入导出按钮
        page.evaluate(_INJECT_EXPORT_BTN)

        # 自动打开赛事筛选面板
        page.click("#button3")

        print('请在浏览器中做赛事筛选，完成后点击红色 ">> 导出到脚本" 按钮。')

        # 等待用户点击导出按钮 (无超时限制)
        page.wait_for_function("() => window.__exportClicked === true", timeout=0)

        print("正在读取筛选结果...")
        result = page.evaluate(_COLLECT_RESULTS)
        browser.close()

    n_leagues = len(result["leagues"])
    n_matches = len(result["match_ids"])
    print(f"筛选完成: {n_leagues} 个联赛, {n_matches} 场比赛")

    return result


if __name__ == "__main__":
    import sys
    import io

    # Windows 终端 GBK 兼容: 遇到无法编码的字符替换为 ?
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=sys.stdout.encoding, errors="replace")

    result = open_filter()

    print(f"\n=== 赛事类型: {_SCLASS_LABELS[result['sclass_type']]} ===")
    print(f"=== 比赛状态: {_STATE_LABELS[result['match_state']]} ===")

    print(f"\n选中的联赛 ({len(result['leagues'])} 个):")
    for lg in result["leagues"]:
        print(f"  [{lg['cid']}] {lg['name']} ({lg['shown']}/{lg['count']}场)")

    print(f"\n可见的比赛 ({len(result['match_ids'])} 场):")
    for m in result["match_ids"][:30]:
        state_str = {0: "未", -1: "完", 1: "上半", 3: "下半"}.get(m["state"], str(m["state"]))
        print(f"  [{m['match_id']}] {m['home']} vs {m['away']}  {m['score']}  ({state_str})")
    if len(result["match_ids"]) > 30:
        print(f"  ... 共 {len(result['match_ids'])} 场")
