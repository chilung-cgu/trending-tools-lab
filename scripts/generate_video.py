"""由固定快照生成可重現的 HyperFrames composition。"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate():
    snapshots = json.loads((ROOT / 'data/index.json').read_text())['snapshots']
    output = ROOT / 'video'
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'node_modules/gsap/dist/gsap.min.js', output / 'assets/gsap.min.js')
    (output / 'assets/LICENSE.gsap.txt').write_text('GSAP 3.14.2 · GreenSock\nLicense: https://gsap.com/standard-license\n')
    scenes = ['''<section id="intro" class="clip" data-start="0" data-duration="3" data-track-index="0">
      <div class="content"><p class="eyebrow">GITHUB TRENDING / FOUR SNAPSHOTS</p>
      <h1>四週開源觀察</h1><p class="subtitle">同一份榜單資料，從瀏覽變成影片。</p>
      <p class="note">2026.09.21 → 2026.10.12 · 週榜前三名</p></div></section>''']
    for i, snapshot in enumerate(snapshots):
        rows = []
        for item in snapshot['weekly'][:3]:
            rows.append(f'''<div class="row"><span class="rank">{item['rank']:02}</span>
              <div class="repo"><strong>{html.escape(item['full_name'])}</strong>
              <small>{html.escape(item['language'] or '未標示語言')}</small></div>
              <div class="stars">{item['period_stars']:,}<small>stars this week</small></div></div>''')
        scenes.append(f'''<section id="week{i}" class="clip" data-start="{3+i*6}" data-duration="6" data-track-index="0">
          <div class="content"><p class="eyebrow">SNAPSHOT {i+1:02} / 04</p><h2>{snapshot['date']}</h2>
          <div class="rows">{''.join(rows)}</div><p class="note">排名依當日 GitHub Trending 順序；區間 stars 並非排序依據。</p></div></section>''')
    scenes.append('''<section id="outro" class="clip" data-start="27" data-duration="3" data-track-index="0">
      <div class="content"><p class="eyebrow">READ THE DATA CAREFULLY</p><h2>快照，是觀察起點。</h2>
      <p class="subtitle">滾動區間可能重疊，stars 不跨期累加。</p>
      <p class="subtitle">未進 Top 10，只代表未觀察到。</p>
      <p class="note">Source: chilung-cgu/github-trending-crawler · 非即時榜單</p></div></section>''')
    animation = []
    for name, start in [('intro', 0)] + [(f'week{i}', 3+i*6) for i in range(4)] + [('outro', 27)]:
        animation.append(f'tl.fromTo("#{name} .content", {{opacity:0,y:28}}, {{opacity:1,y:0,duration:0.5,ease:"power2.out"}}, {start});')
    document = '''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
      <meta name="viewport" content="width=1280, height=720"><title>四週開源觀察</title>
      <script src="./assets/gsap.min.js"></script><style>
      *{box-sizing:border-box}html,body{margin:0;width:1280px;height:720px;overflow:hidden;background:#101b25;color:#f5f0e6;font-family:sans-serif}
      #root{width:100%;height:100%;position:relative}.clip{position:absolute;inset:0;padding:58px 76px;background:#101b25}
      .content{height:100%;display:flex;flex-direction:column;justify-content:center}.eyebrow{color:#a9dec5;letter-spacing:3px;font-size:19px;margin:0 0 20px}
      h1{font-size:80px;line-height:1.2;margin:12px 0 30px}h2{font-size:56px;margin:0 0 24px;line-height:1.2}
      .subtitle{font-size:29px;margin:8px 0;line-height:1.6}.note{font-size:19px;color:#c2cbd1;margin-top:28px;line-height:1.5}
      .rows{display:flex;flex-direction:column;gap:12px}.row{display:flex;align-items:center;gap:24px;background:#1d303e;border-radius:12px;padding:16px 22px;min-height:100px}
      .rank{font-size:27px;color:#a9dec5;width:42px}.repo{flex:1;min-width:0}.repo strong{display:block;font-size:28px;overflow-wrap:anywhere;line-height:1.25}
      small{display:block;font-size:16px;color:#c2cbd1;margin-top:8px}.stars{text-align:right;font-size:33px;color:#a9dec5;min-width:170px}
      </style></head><body><div id="root" data-composition-id="trending" data-start="0" data-duration="30" data-width="1280" data-height="720" data-fps="24">'''
    document += ''.join(scenes) + '<script>const tl=gsap.timeline({paused:true});' + ''.join(animation) + 'window.__timelines["trending"]=tl;</script></div></body></html>'
    (output / 'index.html').write_text(document)


if __name__ == '__main__':
    generate()
