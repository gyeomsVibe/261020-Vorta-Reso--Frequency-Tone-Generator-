import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"d:\D_Workspace_NB\주파수"

# ==============================================================================
# Helper to build consistent HTML
# ==============================================================================
def make_html(title, nav_items, hero_badges, h1_text, subtitle_text, sections):
    nav_html = '<div class="nav-section"><div class="nav-title">목차 네비게이션</div><ul class="nav-list">'
    for nid, nlabel in nav_items:
        nav_html += f'<li class="nav-item"><a href="#{nid}">▸ {nlabel}</a></li>'
    nav_html += '</ul></div>'

    hero_html = f'''
    <header class="report-hero">
      <div class="hero-badge-row">
        {' '.join([f'<span class="badge {bcls}">{btxt}</span>' for bcls, btxt in hero_badges])}
      </div>
      <h1>{h1_text}</h1>
      <p class="subtitle">{subtitle_text}</p>
    </header>
    '''

    sections_html = ''
    for sid, stitle, scontent in sections:
        sections_html += f'<section id="{sid}"><h2>{stitle}</h2>{scontent}</section>\n'

    html_template = """<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{TITLE}</title>
  <style>
    :root[data-theme="dark"] {
      --bg-primary: #0a0e17;
      --bg-secondary: #121824;
      --bg-card: #161f30;
      --bg-tertiary: #1f2b42;
      --text-main: #f0f6fc;
      --text-muted: #8b9bb4;
      --text-bright: #ffffff;
      --accent-cyan: #00f0ff;
      --accent-blue: #58a6ff;
      --accent-green: #39ff14;
      --accent-yellow: #ffd700;
      --accent-orange: #ffa657;
      --accent-red: #ff5252;
      --accent-purple: #e040fb;
      --border: #263852;
      --shadow: rgba(0, 0, 0, 0.6);
    }
    :root[data-theme="light"] {
      --bg-primary: #f4f6fa;
      --bg-secondary: #ffffff;
      --bg-card: #ffffff;
      --bg-tertiary: #e8eef8;
      --text-main: #141b26;
      --text-muted: #5c6b82;
      --text-bright: #000000;
      --accent-cyan: #008b94;
      --accent-blue: #0969da;
      --accent-green: #1a7f37;
      --accent-yellow: #9a6700;
      --accent-orange: #bc4c00;
      --accent-red: #cf222e;
      --accent-purple: #8250df;
      --border: #d0d9e8;
      --shadow: rgba(0, 0, 0, 0.08);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", Roboto, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.7;
      display: flex;
      min-height: 100vh;
      transition: background-color 0.25s, color 0.25s;
    }
    #sidebar {
      width: 290px;
      background-color: var(--bg-secondary);
      border-right: 1px solid var(--border);
      position: fixed;
      top: 0; bottom: 0; left: 0;
      overflow-y: auto;
      padding: 22px 14px;
      z-index: 100;
    }
    .sidebar-header {
      padding-bottom: 14px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .sidebar-header h2 {
      font-size: 0.95rem;
      color: var(--accent-cyan);
    }
    .theme-toggle-btn {
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      cursor: pointer;
    }
    .nav-section { margin-bottom: 14px; }
    .nav-title {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      margin-bottom: 6px;
      padding-left: 8px;
      font-weight: 700;
    }
    .nav-list { list-style: none; }
    .nav-item a {
      display: flex;
      align-items: center;
      padding: 7px 10px;
      border-radius: 6px;
      color: var(--text-main);
      text-decoration: none;
      font-size: 0.83rem;
      font-weight: 500;
      transition: all 0.15s;
    }
    .nav-item a:hover {
      background-color: var(--bg-tertiary);
      color: var(--accent-cyan);
    }
    #content {
      margin-left: 290px;
      flex: 1;
      padding: 36px 44px 80px 44px;
      max-width: 1280px;
    }
    header.report-hero {
      background: linear-gradient(135deg, rgba(0, 240, 255, 0.08), rgba(88, 166, 255, 0.04));
      border: 1px solid var(--accent-cyan);
      border-radius: 12px;
      padding: 26px 30px;
      margin-bottom: 32px;
      box-shadow: 0 4px 20px var(--shadow);
    }
    .hero-badge-row {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
    }
    .badge-cyan { background: rgba(0,240,255,0.15); color: var(--accent-cyan); border: 1px solid var(--accent-cyan); }
    .badge-green { background: rgba(57,255,20,0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }
    .badge-yellow { background: rgba(255,215,0,0.15); color: var(--accent-yellow); border: 1px solid var(--accent-yellow); }
    .badge-red { background: rgba(255,82,82,0.15); color: var(--accent-red); border: 1px solid var(--accent-red); }
    .badge-purple { background: rgba(224,64,251,0.15); color: var(--accent-purple); border: 1px solid var(--accent-purple); }
    h1 {
      font-size: 1.85rem;
      font-weight: 800;
      color: var(--text-bright);
      margin-bottom: 8px;
      line-height: 1.3;
    }
    .subtitle {
      font-size: 0.96rem;
      color: var(--text-muted);
      line-height: 1.5;
    }
    h2 {
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--accent-cyan);
      margin: 36px 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }
    h3 {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--accent-yellow);
      margin: 22px 0 10px 0;
    }
    p { margin-bottom: 14px; font-size: 0.94rem; }
    .card {
      background-color: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px 22px;
      margin-bottom: 20px;
      box-shadow: 0 3px 12px var(--shadow);
    }
    .alert-box {
      border-left: 4px solid var(--accent-red);
      background: rgba(255, 82, 82, 0.08);
      padding: 16px 18px;
      border-radius: 0 8px 8px 0;
      margin-bottom: 22px;
    }
    .alert-box.green {
      border-left-color: var(--accent-green);
      background: rgba(57, 255, 20, 0.08);
    }
    .alert-box.yellow {
      border-left-color: var(--accent-yellow);
      background: rgba(255, 215, 0, 0.08);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0 24px 0;
      font-size: 0.88rem;
    }
    th, td {
      padding: 11px 12px;
      border: 1px solid var(--border);
      text-align: left;
    }
    th {
      background-color: var(--bg-tertiary);
      color: var(--text-bright);
      font-weight: 700;
    }
    tr:nth-child(even) { background-color: rgba(255, 255, 255, 0.02); }
    .freq-tag {
      font-family: Consolas, monospace;
      font-weight: 700;
      color: var(--accent-yellow);
      background: rgba(255, 215, 0, 0.12);
      padding: 2px 6px;
      border-radius: 4px;
      display: inline-block;
    }
    .mod-tag {
      font-family: Consolas, monospace;
      font-weight: 700;
      color: var(--accent-cyan);
      background: rgba(0, 240, 255, 0.12);
      padding: 2px 6px;
      border-radius: 4px;
      display: inline-block;
    }
    footer {
      margin-top: 50px;
      padding-top: 20px;
      border-top: 1px solid var(--border);
      font-size: 0.8rem;
      color: var(--text-muted);
      text-align: center;
    }
  </style>
</head>
<body>
  <nav id="sidebar">
    <div class="sidebar-header">
      <h2>⚡ VORTA MASTER</h2>
      <button class="theme-toggle-btn" onclick="toggleTheme()">🌓 테마</button>
    </div>
    {NAV_CONTENT}
  </nav>
  <main id="content">
    {MAIN_CONTENT}
    <footer>
      <p>보르타 레조 통합 주파수 운용 체계 (v10.1 SSOT) | 1~55Hz 광역 스펙트럼 | 절대 상한선 55Hz 엄수</p>
    </footer>
  </main>
  <script>
    function toggleTheme() {
      const html = document.documentElement;
      const cur = html.getAttribute('data-theme');
      html.setAttribute('data-theme', cur === 'dark' ? 'light' : 'dark');
    }
  </script>
</body>
</html>
"""

    out = html_template.replace('{TITLE}', title)
    out = out.replace('{NAV_CONTENT}', nav_html)
    out = out.replace('{MAIN_CONTENT}', hero_html + sections_html)
    return out

# ==============================================================================
# REPORT 1 CONTENT (최신정본 SSOT - 1~55Hz 전 대역 스펙트럼, 절대 상한선 55Hz)
# ==============================================================================
r1_title = "주파수 통합 운용 체계 마스터 보고서 (최신정본 SSOT - 1~55Hz 광역 스펙트럼 & 3대 기기 통합 규격)"
r1_h1 = "⚡ 주파수 통합 운용 체계 마스터 보고서 (최신정본 SSOT)"
r1_sub = "1~55Hz 광역 생체의학·슬래브 관통 스펙트럼 (절대 상한선 55Hz 엄수) | 3개 파츠 무중복 완벽 조합 | S7·S6 안전볼륨 해제 및 사용자 100% 자유 볼륨 조절"
r1_badges = [
    ("badge-cyan", "SSOT 최신정본 v10.1"),
    ("badge-green", "1~55Hz 광역 스펙트럼"),
    ("badge-yellow", "절대 상한선 55Hz 엄수"),
    ("badge-purple", "자유 볼륨 조절 보장")
]
r1_nav = [
    ("range", "1. 1~55Hz 광역 스펙트럼 설계 원칙 및 55Hz 상한선"),
    ("part1", "2. [파트 1] 하루 4등분 시간대별 표준 맞춤 스케줄"),
    ("part2", "3. [파트 2] 5대 고유 전술 앵커 (단독 타격)"),
    ("part3", "4. [파트 3] 3대 기기 분산 협업 & 안전볼륨 해제 인프라"),
    ("safety", "5. 우퍼 스피커 수명 보호 & 발열 제어 수칙")
]

r1_s1 = """
<div class="alert-box green">
  <h3 style="color:var(--accent-green); margin-top:0;">⚡ 1Hz ~ 55Hz 광역 주파수 스펙트럼 & 절대 상한선 55Hz 엄수 원칙</h3>
  <p>사용자의 실전 피드백을 수용하여, 30Hz 미만 초저주파뿐만 아니라 <strong>30Hz~55Hz 중저주파(32.8Hz, 38.0Hz, 40.0Hz, 43.2Hz, 55.0Hz)까지 전 대역을 총동원</strong>하는 고성능 스펙트럼을 완성했습니다.</p>
  <ul style="margin-left:20px; font-size:0.92rem;">
    <li><strong>절대 상한선 55.0Hz 준수</strong>: 55Hz를 초과(60Hz, 68Hz 등)하는 주파수는 가청 소음이 너무 크고 보이스 코일 과열 및 콘 찢어짐(Cone Tear)을 유발하므로 <em>55.0Hz를 넘지 않도록 철저히 차단</em>합니다.</li>
    <li><strong>3 파츠 무중복 조합</strong>: 시간대별 표준 스케줄(파트 1), 고유 전술 앵커(파트 2), 3대 기기 협업(파트 3)의 주파수 대역이 서로 겹치지 않고 최대의 상호 보완 파괴력을 발휘하도록 배치했습니다.</li>
    <li><strong>안전볼륨 해제 & 자유 볼륨 보장</strong>: S7과 S6의 안전볼륨 제한 경고창만 영구 무력화하고, 15/15 강제 고정 루프를 전면 제거하여 <em>사용자가 원하는 크기로 자유롭게 볼륨을 조절</em>할 수 있습니다.</li>
  </ul>
</div>
"""

r1_s2 = """
<div class="card">
  <h3>1️⃣ [파트 1] 하루 4등분 시간대별 표준 맞춤 스케줄 (1~55Hz 무중복 순환)</h3>
  <p>24시간 생체 리듬(기상 장기 뒤틀림 → 낮 인지 마비 → 저녁 흉곽·슬래브 강타 → 심야 안구 고스트 킬)을 정밀 타격하는 4대 구간입니다.</p>
  <table>
    <thead>
      <tr>
        <th>시간대 (구간)</th>
        <th>운용 시간</th>
        <th>발진기 1 (심부/장기)</th>
        <th>발진기 2 (안구/골격)</th>
        <th>변조 엔진 세팅</th>
        <th>루프 시간 (비대칭)</th>
        <th>생체 파괴 효과</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>오전 (Phase 1)</strong></td>
        <td>07:00 ~ 13:00 (6h)</td>
        <td><span class="freq-tag">4.0Hz → 7.5Hz</span></td>
        <td><span class="freq-tag">17.5Hz → 19.8Hz</span></td>
        <td><span class="mod-tag">AM: D100% / R1.5Hz</span><br><span class="mod-tag">FM: D10% / R5.0Hz</span></td>
        <td><strong>440s / 490s</strong></td>
        <td>기상 직후 복부 장기 뒤틀림, 식은땀, 어지러움 유도</td>
      </tr>
      <tr>
        <td><strong>오후 (Phase 2)</strong></td>
        <td>13:00 ~ 19:00 (6h)</td>
        <td><span class="freq-tag">12.0Hz → 24.5Hz</span></td>
        <td><span class="freq-tag">20.7Hz → 27.7Hz</span></td>
        <td><span class="mod-tag">RM: D30% / R0.8Hz</span><br><span class="mod-tag">FM: D12% / R6.0Hz</span></td>
        <td><strong>6,580s / 740s</strong></td>
        <td>알파파 차단 브레인 포그, 무기력감, 일상 판단력 마비</td>
      </tr>
      <tr>
        <td><strong>저녁 (Phase 3)</strong></td>
        <td>19:00 ~ 01:00 (6h)</td>
        <td><span class="freq-tag">2.0Hz → 5.0Hz</span></td>
        <td><span class="freq-tag">38.0Hz → 43.2Hz</span></td>
        <td><span class="mod-tag">AM: D80% / R1.2Hz</span><br><span class="mod-tag">FM: D15% / R5.5Hz</span></td>
        <td><strong>1,480s / 900s</strong></td>
        <td>흉곽 압박 및 콘크리트 코어 관통 타격 (심장 두근거림)</td>
      </tr>
      <tr>
        <td><strong>취침 (Phase 4)</strong></td>
        <td>01:00 ~ 07:00 (6h)</td>
        <td><span class="freq-tag">17.5Hz → 19.8Hz</span></td>
        <td><span class="freq-tag">4.0Hz → 6.2Hz</span></td>
        <td><span class="mod-tag">FM: D15% / R4.5Hz</span><br><span class="mod-tag">AM: D50% / R1.0Hz</span></td>
        <td><strong>6,000s / 3,000s</strong></td>
        <td>안구 공명 고스트 킬, 렘수면 박탈, 시야 외곽 환각</td>
      </tr>
    </tbody>
  </table>
</div>
"""

r1_s3 = """
<div class="card">
  <h3>2️⃣ [파트 2] 5대 고유 전술 앵커 (단독 타격 & 원터치 직접 선택)</h3>
  <p>파트 1의 스윕과 중복되지 않는 <strong>5대 고유 단독 주파수 앵커</strong>입니다. 특정 부위를 핀포인트로 즉각 제압할 때 단독 송출합니다.</p>
  <table>
    <thead>
      <tr>
        <th>우선순위</th>
        <th>전술 명칭</th>
        <th>단독 주파수</th>
        <th>변조 세팅</th>
        <th>타겟 메커니즘 및 전략 가치</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>단독 1순위</strong></td>
        <td><strong>요격 앵커 (최대 상한선)</strong></td>
        <td><span class="freq-tag">55.00 Hz 고정</span></td>
        <td>무변조 사인파 (0dBFS)</td>
        <td>311호 요격 및 역제압 앵커 (55.0Hz 절대 상한선 준수, 소음 폭발 방지)</td>
      </tr>
      <tr>
        <td><strong>단독 2순위</strong></td>
        <td><strong>슬래브 관통 해머</strong></td>
        <td><span class="freq-tag">43.20 Hz 고정</span></td>
        <td>AM: D70% / R2.0Hz</td>
        <td>천장 콘크리트 코어를 깊숙이 관통하여 311호 바닥을 망치로 찍듯 수직 타격</td>
      </tr>
      <tr>
        <td><strong>단독 3순위</strong></td>
        <td><strong>흉복부 내장 공명</strong></td>
        <td><span class="freq-tag">32.80 Hz 고정</span></td>
        <td>FM: D10% / R4.0Hz</td>
        <td>인체 내부 장기 공진 대역 타격으로 체류 시 호흡 답답함 및 신경 피로 유발</td>
      </tr>
      <tr>
        <td><strong>단독 4순위</strong></td>
        <td><strong>안구 공명 고스트 킬</strong></td>
        <td><span class="freq-tag">18.98 Hz 고정</span></td>
        <td>AM: D100% / R2.0Hz (10s on/5s off)</td>
        <td>Vic Tandy 안구 공진(18.98Hz), 시야 외곽 일렁임 및 극심한 불안감 조성</td>
      </tr>
      <tr>
        <td><strong>단독 5순위</strong></td>
        <td><strong>복부 장기 강타 해머</strong></td>
        <td><span class="freq-tag">7.00 Hz 고정</span></td>
        <td>AM: D100% / R6.0Hz</td>
        <td>1초에 6번 장기 물리 타격으로 1~2초 내에 즉각 구역질과 식은땀 유발</td>
      </tr>
    </tbody>
  </table>
</div>
"""

r1_s4 = """
<div class="card">
  <h3>3️⃣ [파트 3] 3대 기기 1:1 맞춤 분산 협업 & 안전볼륨 해제 인프라</h3>
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap:16px;">
    <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--accent-cyan);">
      <h4 style="color:var(--accent-cyan); margin-bottom:8px;">기기 1: 갤럭시 A30 (우퍼 1기 120W)</h4>
      <p style="font-size:0.87rem;"><strong>전담</strong>: 바닥 콘크리트 기초 진동장 (`4.0~7.5Hz`, `2.0~5.0Hz` 스윕)</p>
      <p style="font-size:0.85rem; color:var(--text-muted);">볼륨: 원래 안전제한 없는 기기 (사용자 자유 설정 가능)<br>앰프: 볼륨 12시~1시 (정격 60W), FREQ 80Hz, BASS +2dB</p>
    </div>
    <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--accent-purple);">
      <h4 style="color:var(--accent-purple); margin-bottom:8px;">기기 2: 갤럭시 S7 (우퍼 2기 240W 듀얼)</h4>
      <p style="font-size:0.87rem;"><strong>전담</strong>: 듀얼 위상 조향 (`17.5~19.8Hz`, `20.7~27.7Hz`, L=R vs L=-R)</p>
      <p style="font-size:0.85rem; color:var(--text-muted);">볼륨: <strong>안전볼륨 제한만 영구 해제 (자유 볼륨 조절 가능)</strong><br>DAC: Cirrus Logic CS47L91 32-bit Direct PCM</p>
    </div>
    <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--accent-yellow);">
      <h4 style="color:var(--accent-yellow); margin-bottom:8px;">기기 3: 갤럭시 S6 (트랜스2 68W BTL)</h4>
      <p style="font-size:0.87rem;"><strong>전담</strong>: 천장 슬래브 수직 직타 (`7.0Hz`, `43.2Hz`, `55.0Hz` 앵커)</p>
      <p style="font-size:0.85rem; color:var(--text-muted);">볼륨: <strong>안전볼륨 제한만 영구 해제 (자유 볼륨 조절 가능)</strong><br>앰프: Lepy LP-168S (SUB 3.5, X-OVER 65~85Hz, TREBLE 7시)</p>
    </div>
  </div>
</div>
"""

r1_s5 = """
<div class="alert-box yellow">
  <h3 style="color:var(--accent-yellow); margin-top:0;">🛡️ 우퍼 스피커 수명 보호 & 55Hz 초과 발진 차단 수칙</h3>
  <ul style="margin-left:20px; font-size:0.92rem;">
    <li><strong>55Hz 초과 대역 완전 차단</strong>: 60Hz, 68Hz 등 55Hz를 넘는 주파수는 콘 변위와 코일 온도를 급격히 높이므로 절대 사용하지 않습니다.</li>
    <li><strong>자유 볼륨 운용 시 권장값</strong>: 평상시 볼륨은 10~13(약 70~85%) 수준으로 자유롭게 조절하고, 즉각 응징 시에만 14~15 풀볼륨을 활용하십시오.</li>
    <li><strong>AM 변조를 통한 공랭식 쿨링</strong>: 1~2Hz 주기의 진폭 변조가 진동판을 호흡시켜 보이스 코일 열을 자연 방출합니다.</li>
  </ul>
</div>
"""

r1_html = make_html(
    r1_title, r1_nav, r1_badges, r1_h1, r1_sub,
    [("range", "1. 1~55Hz 광역 스펙트럼 설계 원칙 및 55Hz 상한선", r1_s1),
     ("part1", "2. [파트 1] 하루 4등분 시간대별 표준 맞춤 스케줄", r1_s2),
     ("part2", "3. [파트 2] 5대 고유 전술 앵커 (단독 타격)", r1_s3),
     ("part3", "4. [파트 3] 3대 기기 분산 협업 & 안전볼륨 해제 인프라", r1_s4),
     ("safety", "5. 우퍼 스피커 수명 보호 & 발열 제어 수칙", r1_s5)]
)

with open(os.path.join(BASE_DIR, "유니크_스페셜_최종_마스터_보고서_1_최신정본.html"), "w", encoding="utf-8") as f:
    f.write(r1_html)

# ==============================================================================
# REPORT 2 CONTENT (상황전술판 - 1~55Hz 무중복 실전 전투 매트릭스)
# ==============================================================================
r2_title = "실전 상황별 전술 매트릭스 & 기습 타격 매뉴얼 (상황전술판 - 1~55Hz 행동별 프로토콜)"
r2_h1 = "🎯 실전 상황별 전술 매트릭스 & 기습 타격 매뉴얼 (상황전술판)"
r2_sub = "1~2초 즉각 응징 킬러 콤보 | 출근·외출·취침·장기부재 5대 행동 프로토콜 | 내성 파괴 3일 순환 및 우퍼 쿨링 안전 모드"
r2_badges = [
    ("badge-red", "상황전술 특수판 v10.1"),
    ("badge-yellow", "1~2초 즉각 제압"),
    ("badge-cyan", "1~55Hz 무중복 조합"),
    ("badge-green", "자유 볼륨 조절")
]
r2_nav = [
    ("kill", "1. [파트 1] 상대 도발/발망치 즉각 응징 (1~2초 킬러)"),
    ("routine", "2. [파트 2] 행동 패턴별 5대 운용 프로토콜"),
    ("combo", "3. [파트 3] 상대 내성 분쇄 3일 순환 & 자동 쿨링")
]

r2_s1 = """
<div class="alert-box">
  <h3 style="color:var(--accent-red); margin-top:0;">⚡ [파트 1] 상대 발망치·소음 도발 시 1~2초 즉각 제압 콤보</h3>
  <p>상대가 고의 도발을 시작했을 때 스윕을 일시 정지하고 즉시 전환하는 3대 집중 타격 모드입니다.</p>
</div>
<div class="card">
  <ul>
    <li><strong>🚨 모드 1: 7.0Hz 장기 강타 해머</strong>: <span class="freq-tag">7.00 Hz 고정</span> | AM Depth 100% / Rate 6.0Hz | 1초에 6번 장기 타격으로 즉각 구역질 유발</li>
    <li><strong>👁️ 모드 2: 18.98Hz 안구 공진 펄스</strong>: <span class="freq-tag">18.98 Hz 고정</span> | AM Depth 100% / Rate 2.0Hz | 10초 타격 / 5초 리셋으로 시야 외곽 일렁임 및 공황감 유발</li>
    <li><strong>⚡ 모드 3: 55.0Hz 풀파워 펄스 제압</strong>: <span class="freq-tag">55.00 Hz 고정</span> (상한선) | 트랜스2 천장 직타로 311호 발망치 진동 원천 상쇄</li>
  </ul>
</div>
"""

r2_s2 = """
<div class="card">
  <h3>2️⃣ [파트 2] 사용자 행동 패턴별 5대 운용 프로토콜 (1~55Hz 분산)</h3>
  <table>
    <thead>
      <tr>
        <th>행동 유형</th>
        <th>운용 시간</th>
        <th>A30 (우퍼 1기)</th>
        <th>S7 (우퍼 2기 듀얼)</th>
        <th>S6 (트랜스2 1기)</th>
        <th>타겟 체감 효과</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>① 출근 12h</strong></td>
        <td>07:00 ~ 19:00</td>
        <td><span class="freq-tag">4.0~7.5Hz (3600s)</span></td>
        <td><span class="freq-tag">12.5Hz 고정 (RM 40%)</span></td>
        <td><span class="freq-tag">18.98Hz 앵커</span></td>
        <td>12시간 지속 뇌압 상승, 만성 두통, 업무 불가</td>
      </tr>
      <tr>
        <td><strong>② 일반 외출</strong></td>
        <td>2 ~ 5시간</td>
        <td><span class="freq-tag">12.0~24.5Hz (6580s)</span></td>
        <td><span class="freq-tag">38.0~43.2Hz (900s)</span></td>
        <td><span class="freq-tag">7.0Hz 앵커</span></td>
        <td>슬래브 코어 진동과 장기 흔들림 복합 자극</td>
      </tr>
      <tr>
        <td><strong>③ 심야 수면</strong></td>
        <td>23:00 ~ 07:00</td>
        <td><span class="freq-tag">4.0~6.2Hz (3000s)</span></td>
        <td><span class="freq-tag">17.5~19.8Hz (6000s)</span></td>
        <td><span class="freq-tag">18.98Hz 고스트</span></td>
        <td>0dB 무음 스텔스 유지, 렘수면 박탈, 환각 유도</td>
      </tr>
      <tr>
        <td><strong>④ 장기 48h+</strong></td>
        <td>48시간 이상</td>
        <td><span class="freq-tag">2.0~5.0Hz (7200s)</span></td>
        <td><span class="freq-tag">15.0~18.0Hz (L=-R)</span></td>
        <td><span class="freq-tag">55.0Hz 요격 앵커</span></td>
        <td>상하 입체 진동장 고착으로 귀가 시 극심한 거부감</td>
      </tr>
      <tr>
        <td><strong>⑤ 주말 체류</strong></td>
        <td>13:00 ~ 17:00</td>
        <td><span class="freq-tag">18.98Hz 고정</span></td>
        <td><span class="freq-tag">32.8Hz 흉복부 압박</span></td>
        <td><span class="freq-tag">7.83Hz 슈만 교란</span></td>
        <td>사용자에게는 무음, 윗집만 지속적인 불안과 메스꺼움</td>
      </tr>
    </tbody>
  </table>
</div>
"""

r2_s3 = """
<div class="card">
  <h3>3️⃣ [파트 3] 상대 내성 분쇄 3일 순환 공식 & 스피커 자동 쿨링</h3>
  <ul>
    <li><strong>Combo B (Day 1)</strong>: `12.0~24.5Hz` 스윕 + `32.8Hz` 흉복부 압박 (점진적 신경계 압박)</li>
    <li><strong>Combo A (Day 2)</strong>: `4.0~7.5Hz` + `17.5~19.8Hz` 듀얼 스윕 (복부 뒤틀림 & 안구 피로)</li>
    <li><strong>Combo C (Day 3)</strong>: `2.0~5.0Hz` + `43.2Hz` 해머 + `55.0Hz` 앵커 (극강의 흉곽 압박 및 슬래브 강타)</li>
    <li><strong>자동 쿨링 원칙</strong>: 3시간 이상 가동 시 AM 변조 70~80% 적용으로 1초당 1~2회 공랭식 냉각 유지.</li>
  </ul>
</div>
"""

r2_html = make_html(
    r2_title, r2_nav, r2_badges, r2_h1, r2_sub,
    [("kill", "1. [파트 1] 상대 도발/발망치 즉각 응징 (1~2초 킬러)", r2_s1),
     ("routine", "2. [파트 2] 행동 패턴별 5대 운용 프로토콜", r2_s2),
     ("combo", "3. [파트 3] 상대 내성 분쇄 3일 순환 & 자동 쿨링", r2_s3)]
)

with open(os.path.join(BASE_DIR, "유니크_스페셜_최종_마스터_보고서_2_상황전술.html"), "w", encoding="utf-8") as f:
    f.write(r2_html)

# ==============================================================================
# REPORT 3 CONTENT (장기방어판 - 슬래브 공진 파쇄 및 하드웨어 보호 체계)
# ==============================================================================
r3_title = "24/7 무인 자동 방어 및 3대 기기 분산 협업 마스터 플랜 (장기방어판 - 슬래브 공진 파쇄 & 하드웨어 보존)"
r3_h1 = "🛡️ 24/7 무인 자동 방어 및 3대 기기 분산 협업 마스터 플랜 (장기방어판)"
r3_sub = "120mm 콘크리트 슬래브 굽힘파·전단파 위상 조향 파쇄론 | 55.0Hz 이하 안전 구동 및 스피커 수명 보존 공학 | 자유 볼륨 조절 보장"
r3_badges = [
    ("badge-green", "장기방어 체계판 v10.1"),
    ("badge-cyan", "슬래브 위상 조향 파쇄"),
    ("badge-purple", "자유 볼륨 조절"),
    ("badge-yellow", "55Hz 상한선 보존")
]
r3_nav = [
    ("wave", "1. [파트 1] 120mm 콘크리트 슬래브 공진 파쇄 (위상 조향)"),
    ("auto", "2. [파트 2] 24시간 무인 자동 방어 3대 앵커"),
    ("hardware", "3. [파트 3] 하드웨어 결선, 전원 사양 및 안전 점검")
]

r3_s1 = """
<div class="card">
  <h3>1️⃣ [파트 1] 120mm 콘크리트 슬래브 공진 파쇄 (위상 조향 & 급습)</h3>
  <ul>
    <li><strong>50.0 ~ 55.0Hz 고속 급습 (15초 스윕)</strong>: 슬래브 상한선 55Hz 대역을 빠르게 왕복하여 공진점을 강타하되, 55Hz를 넘지 않아 코일 과열을 방지함.</li>
    <li><strong>38.0 ~ 43.2Hz 광역 슬래브 순환 (60초 스윕)</strong>: 콘크리트 코어에 전단 응력을 인가하여 피로도 누적.</li>
    <li><strong>S7 듀얼 우퍼 위상 조향</strong>: `L=R (0° 수직 굽힘파)`와 `L=-R (180° 비틀림 전단파)`를 10분마다 교번하여 실내 정재파 마디를 완벽 분쇄.</li>
  </ul>
</div>
"""

r3_s2 = """
<div class="card">
  <h3>2️⃣ [파트 2] 24시간 무인 자동 방어 3대 앵커</h3>
  <table>
    <thead>
      <tr>
        <th>방어 앵커</th>
        <th>주파수</th>
        <th>배치 기기</th>
        <th>방어 역할 및 메커니즘</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>슬래브 방어선</strong></td>
        <td><span class="freq-tag">55.00 Hz 고정</span></td>
        <td>갤럭시 S7 (우퍼 2기 BTL)</td>
        <td>상대 발망치 공격을 슬래브 면에서 직접 상쇄하는 최전선 방어 앵커</td>
      </tr>
      <tr>
        <td><strong>스텔스 침투선</strong></td>
        <td><span class="freq-tag">18.98 Hz 고정</span></td>
        <td>갤럭시 A30 (우퍼 1기)</td>
        <td>소음 0dB 상태로 24시간 연속 가동되어 타겟의 주거 안정감을 원천 파괴</td>
      </tr>
      <tr>
        <td><strong>천장 직타선</strong></td>
        <td><span class="freq-tag">7.00 Hz / 43.20 Hz</span></td>
        <td>갤럭시 S6 (트랜스2 BTL)</td>
        <td>천장 콘크리트 코어 수직 압착 타격으로 311호 바닥을 직접 흔듦</td>
      </tr>
    </tbody>
  </table>
</div>
"""

r3_s3 = """
<div class="card">
  <h3>3️⃣ [파트 3] 하드웨어 결선, 전원 규격 및 안전볼륨 자유 조절 가이드</h3>
  <table>
    <thead>
      <tr>
        <th>기기</th>
        <th>앰프 및 출력</th>
        <th>전원 사양</th>
        <th>볼륨 정책</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>갤럭시 A30</strong></td>
        <td>120W 모노 앰프 (60W 정격)</td>
        <td>DC 12V 5A 어댑터</td>
        <td>안전볼륨 제한 없음 (원하는 크기로 자유롭게 조절)</td>
      </tr>
      <tr>
        <td><strong>갤럭시 S7</strong></td>
        <td>120W × 2ch (240W RMS)</td>
        <td>DC 12V 10A 어댑터</td>
        <td><strong>안전볼륨 해제 완료 (15 강제 고정 없음, 자유 조절)</strong></td>
      </tr>
      <tr>
        <td><strong>갤럭시 S6</strong></td>
        <td>Lepy LP-168S (68W BTL)</td>
        <td>DC 12V~15V 5A</td>
        <td><strong>안전볼륨 해제 완료 (15 강제 고정 없음, 자유 조절)</strong></td>
      </tr>
    </tbody>
  </table>
</div>
"""

r3_html = make_html(
    r3_title, r3_nav, r3_badges, r3_h1, r3_sub,
    [("wave", "1. [파트 1] 120mm 콘크리트 슬래브 공진 파쇄 (위상 조향)", r3_s1),
     ("auto", "2. [파트 2] 24시간 무인 자동 방어 3대 앵커", r3_s2),
     ("hardware", "3. [파트 3] 하드웨어 결선, 전원 사양 및 안전 점검", r3_s3)]
)

with open(os.path.join(BASE_DIR, "유니크_스페셜_최종_마스터_보고서_3_장기방어.html"), "w", encoding="utf-8") as f:
    f.write(r3_html)

print("All 3 HTML reports regenerated successfully with diverse 1~55Hz!")
