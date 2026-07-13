"""Compose okinawa-combined.html: tabbed page = WebGL terrain diorama + MapLibre real map
with trip planner (fuzzy search Photon+Nominatim, routing FOSSGIS-OSRM car/foot),
3D extruded buildings (OpenFreeMap vector tiles) and a route fly-through mode.
Terrain CSS/markup/JS are taken verbatim from the verified okinawa-3d.html."""
import io, os

BASE = os.path.dirname(os.path.abspath(__file__))
t = io.open(os.path.join(BASE, "okinawa-3d.html"), encoding="utf-8").read()

terrain_css = t.split("<style>")[1].split("</style>")[0]
after_style = t.split("</style>", 1)[1]
terrain_markup = after_style.split("<script>")[0].strip()
terrain_js = after_style.split("<script>", 1)[1].rsplit("</script>", 1)[0]

extra_css = """
  /* ---- real-map view (r- prefixed to avoid clashes) ---- */
  #view-real #map { position: fixed; inset: 0; transition: filter 1.2s ease; }
  #view-real #map.wx-rain { filter: brightness(0.8) saturate(0.7) contrast(1.03); }
  #view-real #map.wx-sun { filter: brightness(1.04) saturate(1.1); }

  .r-wx {
    display: flex; align-items: center; gap: 9px; margin-top: 11px;
    background: rgba(10, 34, 54, 0.65); border: 1px solid var(--line);
    border-radius: 4px; padding: 7px 10px;
  }
  .r-wx .ic { font-size: 21px; line-height: 1; flex: none; }
  .r-wx .tx { min-width: 0; }
  .r-wx .tx b { display: block; font-size: 11.5px; font-weight: 600; letter-spacing: 0.03em; }
  .r-wx .tx span { display: block; font-size: 9px; color: var(--muted); margin-top: 2px; font-variant-numeric: tabular-nums; }
  .r-wx .rd { margin-left: auto; flex: none; display: flex; align-items: center; gap: 4px; font-size: 10px; color: var(--muted); cursor: pointer; }
  .r-wx .rd input { accent-color: #2c7d8a; width: 13px; height: 13px; cursor: pointer; }
  .stop-row .wxs { flex: none; font-size: 10px; color: var(--muted); min-width: 46px; text-align: right; font-variant-numeric: tabular-nums; }
  .r-panel {
    position: fixed; top: 64px; left: 14px; z-index: 10; width: 276px;
    max-height: calc(100vh - 90px); overflow-y: auto;
    background: var(--panel); border: 1px solid var(--line); border-radius: 4px;
    padding: 14px 16px 13px; color: var(--text);
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 12px 40px rgba(0, 6, 12, 0.45);
  }
  .r-eyebrow { font-family: var(--font-display); font-size: 9.5px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--reef); margin-bottom: 6px; }
  .r-title { font-family: var(--font-display); font-size: 22px; font-weight: 700; letter-spacing: 0.04em; }
  .r-title small { display: block; font-family: var(--font-jp); font-size: 10.5px; font-weight: 600; letter-spacing: 0.18em; color: var(--muted); margin-top: 4px; }

  .r-search { position: relative; display: flex; gap: 6px; margin-top: 12px; }
  .r-search input {
    flex: 1; min-width: 0; font-family: var(--font-jp); font-size: 12px; color: var(--text);
    background: rgba(10, 34, 54, 0.9); border: 1px solid rgba(126, 214, 206, 0.35);
    border-radius: 3px; padding: 7px 9px; outline: none;
  }
  .r-search input:focus-visible { border-color: var(--reef); }
  .r-search input::placeholder { color: #5f7889; }
  .r-search button {
    font-family: var(--font-jp); font-size: 12px; font-weight: 600; color: #071826; cursor: pointer;
    background: var(--reef); border: none; border-radius: 3px; padding: 7px 13px; white-space: nowrap;
  }
  .r-search button:hover { background: #7fe3d8; }
  .r-search button:focus-visible { outline: 2px solid var(--coral); outline-offset: 2px; }
  .r-sug {
    position: absolute; top: calc(100% + 4px); left: 0; right: 0; z-index: 40;
    background: #0a2236; border: 1px solid var(--line); border-radius: 4px;
    max-height: 190px; overflow-y: auto; box-shadow: 0 10px 30px rgba(0, 6, 12, 0.6);
  }
  .r-sug:empty { display: none; }
  .r-sug button {
    display: block; width: 100%; text-align: left; cursor: pointer;
    font-family: var(--font-jp); font-size: 11.5px; color: var(--text);
    background: transparent; border: none; border-bottom: 1px solid rgba(126, 214, 206, 0.08);
    padding: 7px 10px;
  }
  .r-sug button:hover, .r-sug button.sel { background: rgba(95, 212, 200, 0.14); }
  .r-sug .k { display: block; font-size: 9px; color: var(--muted); margin-top: 2px; letter-spacing: 0.05em; }
  .r-note { margin-top: 6px; font-size: 9px; color: #5f7889; line-height: 1.5; }

  .r-itin { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line); }
  .r-itin-head { display: flex; justify-content: space-between; align-items: baseline; font-size: 11px; font-weight: 600; letter-spacing: 0.1em; }
  .r-itin-head .sum { font-family: var(--font-display); font-size: 11px; color: var(--reef); font-variant-numeric: tabular-nums; letter-spacing: 0.05em; font-weight: 600; }
  .r-mode { display: flex; align-items: center; gap: 5px; margin-top: 8px; }
  .r-mode .m {
    font-family: var(--font-jp); font-size: 10.5px; color: var(--muted); cursor: pointer;
    background: transparent; border: 1px solid rgba(126, 214, 206, 0.25); border-radius: 999px;
    padding: 3px 12px; transition: background 0.15s, color 0.15s;
  }
  .r-mode .m:hover { color: var(--text); }
  .r-mode .m.active { color: var(--text); background: rgba(95, 212, 200, 0.16); border-color: rgba(126, 214, 206, 0.5); }
  .r-mode .bld { margin-left: auto; display: flex; align-items: center; gap: 4px; font-size: 10.5px; color: var(--muted); cursor: pointer; }
  .r-mode .bld input { accent-color: #2c7d8a; width: 13px; height: 13px; cursor: pointer; }
  #stops { list-style: none; margin: 8px 0 0; padding: 0; }
  #stops li { margin: 0; }
  .leg { font-size: 9.5px; color: var(--muted); padding: 3px 0 3px 28px; font-variant-numeric: tabular-nums; }
  .stop-row { display: flex; align-items: center; gap: 7px; padding: 4px 0; }
  .stop-no {
    flex: none; width: 19px; height: 19px; border-radius: 50%; background: var(--coral);
    color: #fff; font-family: var(--font-display); font-size: 11px; font-weight: 700;
    text-align: center; line-height: 19px;
  }
  .stop-name { flex: 1; min-width: 0; font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .stop-row .op {
    flex: none; width: 18px; height: 18px; padding: 0; cursor: pointer; border-radius: 3px;
    background: transparent; border: 1px solid rgba(126, 214, 206, 0.25);
    color: var(--muted); font-size: 10px; line-height: 16px;
  }
  .stop-row .op:hover { background: rgba(95, 212, 200, 0.15); color: var(--text); }
  .stop-row .op:disabled { opacity: 0.25; cursor: default; }
  .r-drive { display: flex; gap: 6px; margin-top: 9px; }
  .r-drive button {
    font-family: var(--font-jp); font-size: 12px; font-weight: 600; cursor: pointer;
    border-radius: 3px; padding: 7px 0; letter-spacing: 0.08em; transition: background 0.15s;
  }
  #playBtn {
    flex: 1; color: var(--text); background: rgba(255, 107, 107, 0.14);
    border: 1px solid rgba(255, 107, 107, 0.5);
  }
  #playBtn:hover:enabled { background: rgba(255, 107, 107, 0.28); }
  #stopBtn {
    width: 72px; color: var(--muted); background: transparent;
    border: 1px solid rgba(126, 214, 206, 0.3);
  }
  #stopBtn:hover:enabled { background: rgba(95, 212, 200, 0.12); color: var(--text); }
  .r-drive button:disabled { opacity: 0.35; cursor: default; }
  .r-drive button:focus-visible { outline: 2px solid var(--coral); outline-offset: 2px; }
  .r-spd { display: flex; align-items: center; gap: 4px; margin-top: 7px; font-size: 10px; color: var(--muted); }
  .r-spd .s {
    font-family: var(--font-jp); font-size: 10px; color: var(--muted); cursor: pointer;
    background: transparent; border: 1px solid rgba(126, 214, 206, 0.25); border-radius: 999px;
    padding: 2px 9px; font-variant-numeric: tabular-nums;
  }
  .r-spd .s:hover { color: var(--text); }
  .r-spd .s.active { color: var(--text); background: rgba(95, 212, 200, 0.16); border-color: rgba(126, 214, 206, 0.5); }
  #rideInfo { margin-left: auto; font-variant-numeric: tabular-nums; letter-spacing: 0.04em; }
  #routeMsg { font-size: 10px; color: #ffb3b3; margin-top: 5px; min-height: 1em; }
  .r-empty { font-size: 10px; color: #5f7889; margin-top: 6px; line-height: 1.6; }

  .r-mark {
    width: 24px; height: 24px; border-radius: 50%; background: var(--coral);
    color: #fff; font-family: var(--font-display); font-size: 12px; font-weight: 700;
    text-align: center; line-height: 22px; border: 2px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45); cursor: default;
  }

  .r-chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 11px; padding-top: 10px; border-top: 1px solid var(--line); }
  .r-chips button {
    font-family: var(--font-jp); font-size: 10.5px; color: var(--text); cursor: pointer;
    background: rgba(95, 212, 200, 0.08); border: 1px solid rgba(126, 214, 206, 0.32);
    border-radius: 999px; padding: 4px 10px; transition: background 0.15s;
  }
  .r-chips button:hover { background: rgba(95, 212, 200, 0.2); }
  .r-chips button:focus-visible { outline: 2px solid var(--reef); outline-offset: 2px; }
  .r-chips button.home { border-color: rgba(255, 107, 107, 0.45); background: rgba(255, 107, 107, 0.08); }
  .r-chips button.home:hover { background: rgba(255, 107, 107, 0.2); }

  /* ---- view switcher ---- */
  .viewtabs {
    position: fixed; top: 14px; left: 50%; transform: translateX(-50%); z-index: 30;
    display: flex; gap: 4px; padding: 4px;
    background: var(--panel); border: 1px solid var(--line); border-radius: 999px;
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 8px 30px rgba(0, 6, 12, 0.4);
  }
  .viewtabs .vt {
    font-family: var(--font-jp); font-size: 12px; letter-spacing: 0.08em; color: var(--muted);
    background: transparent; border: 1px solid transparent; border-radius: 999px;
    padding: 6px 16px; cursor: pointer; transition: background 0.15s, color 0.15s;
  }
  .viewtabs .vt:hover { color: var(--text); }
  .viewtabs .vt:focus-visible { outline: 2px solid var(--reef); outline-offset: 2px; }
  .viewtabs .vt.active {
    color: var(--text); background: rgba(95, 212, 200, 0.14);
    border-color: rgba(126, 214, 206, 0.4);
  }
  .view { display: none; }
  .view.active { display: block; }
  #real-fail { display: none; margin-top: 10px; font-size: 11px; color: #ffb3b3; line-height: 1.7; }

  @media (max-width: 640px) {
    .panel, .r-panel { top: 64px; }
    .r-panel { right: 14px; width: auto; }
  }
"""

real_markup = """
<!-- ============ view: real map + trip planner ============ -->
<div id="view-real" class="view">
  <div id="map"></div>
  <div class="r-panel">
    <div class="r-eyebrow">Trip Planner · OpenStreetMap</div>
    <div class="r-title">OKINAWA<small>旅程プランナー</small></div>
    <div id="real-fail">地図ライブラリを読み込めませんでした。インターネット接続のある環境でこのビューをご利用ください。</div>

    <div class="r-search">
      <input id="q" type="search" placeholder="ホテル・ビーチ名などで検索" autocomplete="off" aria-label="スポット検索">
      <button id="addBtn" type="button">追加</button>
      <div class="r-sug" id="sug"></div>
    </div>
    <div class="r-note">あいまい検索対応（例：万座 / ビーチ / ハレクラニ / 美ら海水族館）。候補をクリックか「追加」で旅程に入ります。</div>

    <div class="r-wx">
      <span class="ic" id="wxIcon">…</span>
      <div class="tx"><b id="wxMain">天気を取得中…</b><span id="wxSub"></span></div>
      <label class="rd"><input type="checkbox" id="radar" checked> 雨雲</label>
    </div>

    <div class="r-itin">
      <div class="r-itin-head">旅程<span class="sum" id="routeSum"></span></div>
      <div class="r-mode">
        <button type="button" class="m active" id="modeCar">車</button>
        <button type="button" class="m" id="modeFoot">徒歩</button>
        <label class="bld"><input type="checkbox" id="bld" checked> 3D建物</label>
      </div>
      <ol id="stops"></ol>
      <div class="r-empty" id="emptyMsg">スポットを2つ以上追加すると、ルートと所要時間を自動計算します。</div>
      <div class="r-drive">
        <button id="playBtn" type="button" disabled>▶ 走行ビュー 開始</button>
        <button id="stopBtn" type="button" disabled>■ 終了</button>
      </div>
      <div class="r-spd">速度
        <button type="button" class="s active" data-s="1">×1</button>
        <button type="button" class="s" data-s="2">×2</button>
        <button type="button" class="s" data-s="4">×4</button>
        <span id="rideInfo"></span>
      </div>
      <div id="routeMsg" role="status"></div>
    </div>

    <div class="r-chips" id="chips"></div>
    <div class="r-note">検索: Nominatim + Photon / ルート: OSRM (FOSSGIS) / 建物: OpenFreeMap / 天気: Open-Meteo / 雨雲: RainViewer（所要時間・天気は目安）</div>
  </div>
</div>
"""

real_js = r"""
/* ============ real map + trip planner (lazy init) ============ */
var realMap = null;

function initRealMap() {
  if (realMap) return;
  if (typeof maplibregl === "undefined") {
    document.getElementById("real-fail").style.display = "block";
    return;
  }
  realMap = new maplibregl.Map({
    container: "map",
    center: [127.90, 26.48],
    zoom: 9,
    pitch: 55,
    bearing: -15,
    maxPitch: 85,
    style: {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          maxzoom: 19,
          attribution: "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors | 標高: Mapzen/AWS | ルート: OSRM | 建物: OpenFreeMap"
        },
        dem: {
          type: "raster-dem",
          encoding: "terrarium",
          tiles: ["https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"],
          tileSize: 256,
          maxzoom: 15
        },
        ofm: { type: "vector", url: "https://tiles.openfreemap.org/planet" }
      },
      layers: [
        { id: "bg", type: "background", paint: { "background-color": "#0b2b47" } },
        { id: "osm", type: "raster", source: "osm", paint: { "raster-fade-duration": 150 } }
      ]
    }
  });
  window.__map = realMap;
  realMap.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
  realMap.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
  realMap.on("load", function () {
    realMap.setTerrain({ source: "dem", exaggeration: 1.4 });
    realMap.addControl(new maplibregl.TerrainControl({ source: "dem", exaggeration: 1.4 }), "top-right");
    realMap.addLayer({
      id: "bld3d",
      type: "fill-extrusion",
      source: "ofm",
      "source-layer": "building",
      minzoom: 14,
      paint: {
        "fill-extrusion-color": ["interpolate", ["linear"],
          ["coalesce", ["get", "render_height"], 8],
          0, "#e6dfd1", 25, "#d3c9b6", 70, "#bbb09b"],
        "fill-extrusion-height": ["coalesce", ["get", "render_height"], 8],
        "fill-extrusion-base": ["coalesce", ["get", "render_min_height"], 0],
        "fill-extrusion-opacity": 0.95,
        "fill-extrusion-vertical-gradient": true
      }
    });
    realMap.addSource("route", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    realMap.addLayer({
      id: "route-line",
      type: "line",
      source: "route",
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": "#ff6b6b", "line-width": 4.5, "line-opacity": 0.9 }
    });
    applyBld();
    fetchRoute(); // in case stops were queued before load
    refreshCenterWx();
    updateRadar();
  });
  realMap.on("dragstart", function () { stopDrive(false); });
  var wxMoveTimer = null;
  realMap.on("moveend", function () {
    clearTimeout(wxMoveTimer);
    wxMoveTimer = setTimeout(refreshCenterWx, 2500);
  });

  var SPOTS = [
    { jp: "全体を見る", c: [127.90, 26.48], z: 9, p: 55, b: -15, home: true },
    { jp: "恩納リゾート帯", c: [127.868, 26.503], z: 14.6, p: 62, b: -25 },
    { jp: "那覇・国際通り", c: [127.690, 26.215], z: 15.4, p: 55, b: 0 },
    { jp: "北谷アメリカンビレッジ", c: [127.756, 26.316], z: 15.2, p: 58, b: -10 },
    { jp: "美ら海水族館", c: [127.878, 26.694], z: 15.0, p: 60, b: 20 },
    { jp: "瀬底ビーチ", c: [127.853, 26.647], z: 15.2, p: 58, b: 0 },
    { jp: "残波岬・ニライビーチ", c: [127.716, 26.437], z: 14.8, p: 58, b: -20 },
    { jp: "古宇利島", c: [128.019, 26.708], z: 14.6, p: 60, b: 10 }
  ];
  var chips = document.getElementById("chips");
  SPOTS.forEach(function (s) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = s.jp;
    if (s.home) b.className = "home";
    b.addEventListener("click", function () {
      stopDrive(false);
      var view = { center: s.c, zoom: s.z, pitch: s.p, bearing: s.b };
      if (reducedMotion) realMap.jumpTo(view);
      else realMap.flyTo(Object.assign({ duration: 2200, essential: true }, view));
    });
    chips.appendChild(b);
  });
}

var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ---------- trip planner state ---------- */
var stops = [];           // {name, lon, lat}
var markers = [];
var routeLegs = null;
var lastGeom = null;      // route geometry coordinates [[lon,lat],...]
var sugResults = [];
var sugTimer = null;
var pendingAdd = false;
window.__stops = stops;

var MODES = {
  // eyeH: camera height above the street (m), kmps: ride speed at x1 (km/s)
  car:  { url: "https://routing.openstreetmap.de/routed-car/route/v1/driving/",  label: "車で",  eyeH: 12, look: 0.10, kmps: 0.020 },
  foot: { url: "https://routing.openstreetmap.de/routed-foot/route/v1/foot/",    label: "徒歩", eyeH: 9,  look: 0.05, kmps: 0.006 }
};
var travelMode = "car";

var JTYPE = {
  hotel: "ホテル", guest_house: "ゲストハウス", hostel: "ホステル", motel: "モーテル",
  beach: "ビーチ", beach_resort: "ビーチリゾート", resort: "リゾート",
  attraction: "観光スポット", viewpoint: "展望スポット", aquarium: "水族館",
  theme_park: "テーマパーク", museum: "博物館", castle: "城・グスク", monument: "史跡",
  restaurant: "レストラン", cafe: "カフェ", fast_food: "軽食",
  island: "島", islet: "小島", peak: "山", cape: "岬", park: "公園", garden: "庭園",
  village: "集落", town: "町", city: "市", suburb: "地区", bay: "湾", marina: "マリーナ",
  camp_site: "キャンプ場", zoo: "動物園", supermarket: "スーパー", mall: "モール"
};

function inOkinawa(s) { return s.lon > 126.5 && s.lon < 129.0 && s.lat > 25.7 && s.lat < 27.5; }

function photonSearch(q) {
  var url = "https://photon.komoot.io/api/?q=" + encodeURIComponent(q) +
            "&limit=8&lat=26.45&lon=127.9&bbox=126.7,25.8,128.6,27.2";
  return fetch(url).then(function (r) { return r.json(); }).then(function (d) {
    return (d.features || []).map(function (f) {
      var pr = f.properties || {};
      return {
        name: pr.name || pr.street || q,
        kind: JTYPE[pr.osm_value] || pr.osm_value || "",
        area: [pr.city || pr.county || pr.district, pr.state].filter(Boolean).join(" "),
        lon: f.geometry.coordinates[0],
        lat: f.geometry.coordinates[1]
      };
    }).filter(inOkinawa);
  });
}

function nominatimSearch(q) {
  var url = "https://nominatim.openstreetmap.org/search?q=" + encodeURIComponent(q) +
            "&format=jsonv2&viewbox=126.7,27.2,128.6,25.8&bounded=1&limit=6" +
            "&accept-language=ja&addressdetails=1";
  return fetch(url).then(function (r) { return r.json(); }).then(function (d) {
    return (d || []).map(function (r2) {
      var a = r2.address || {};
      return {
        name: (r2.display_name || q).split(",")[0],
        kind: JTYPE[r2.type] || r2.type || "",
        area: [a.city || a.town || a.village || a.county, a.province || a.state].filter(Boolean).join(" "),
        lon: parseFloat(r2.lon),
        lat: parseFloat(r2.lat)
      };
    }).filter(inOkinawa);
  });
}

function searchSpots(q, thenAdd) {
  Promise.allSettled([nominatimSearch(q), photonSearch(q)]).then(function (rs) {
    var merged = [];
    rs.forEach(function (r) {
      if (r.status !== "fulfilled") return;
      r.value.forEach(function (s) {
        var dup = merged.some(function (m) {
          return m.name === s.name ||
                 (Math.abs(m.lon - s.lon) < 0.002 && Math.abs(m.lat - s.lat) < 0.002);
        });
        if (!dup) merged.push(s);
      });
    });
    if (!rs.some(function (r) { return r.status === "fulfilled"; })) {
      setMsg("検索サービスに接続できませんでした");
      pendingAdd = false;
      return;
    }
    sugResults = merged.slice(0, 8);
    renderSug();
    if (thenAdd && pendingAdd) {
      pendingAdd = false;
      if (sugResults.length) addStop(sugResults[0]);
      else setMsg("「" + q + "」は沖縄周辺で見つかりませんでした");
    }
  });
}

function renderSug() {
  var box = document.getElementById("sug");
  box.innerHTML = "";
  sugResults.forEach(function (s) {
    var b = document.createElement("button");
    b.type = "button";
    var k = document.createElement("span");
    b.textContent = s.name;
    k.className = "k";
    k.textContent = [s.kind, s.area].filter(Boolean).join(" · ");
    b.appendChild(k);
    b.addEventListener("click", function () { addStop(s); });
    box.appendChild(b);
  });
}

function clearSug() {
  sugResults = [];
  document.getElementById("sug").innerHTML = "";
}

function setMsg(m) { document.getElementById("routeMsg").textContent = m || ""; }

function addStop(s) {
  stopDrive(false);
  stops.push({ name: s.name, lon: s.lon, lat: s.lat });
  document.getElementById("q").value = "";
  clearSug();
  setMsg("");
  updateItinerary();
  if (realMap) {
    if (stops.length === 1) {
      realMap.flyTo({ center: [s.lon, s.lat], zoom: 14.5, duration: 1600, essential: true });
    } else {
      realMap.fitBounds(boundsOf(stops), { padding: { top: 90, right: 90, bottom: 90, left: 320 }, maxZoom: 15, duration: 1600 });
    }
  }
}

function boundsOf(list) {
  var b = [[list[0].lon, list[0].lat], [list[0].lon, list[0].lat]];
  list.forEach(function (s) {
    b[0][0] = Math.min(b[0][0], s.lon); b[0][1] = Math.min(b[0][1], s.lat);
    b[1][0] = Math.max(b[1][0], s.lon); b[1][1] = Math.max(b[1][1], s.lat);
  });
  return b;
}

function fmtDur(sec) {
  var m = Math.round(sec / 60);
  if (m >= 60) return Math.floor(m / 60) + "時間" + (m % 60) + "分";
  return m + "分";
}
function fmtDist(m) { return (m / 1000).toFixed(1) + "km"; }

function updateItinerary() {
  var ol = document.getElementById("stops");
  ol.innerHTML = "";
  stops.forEach(function (s, i) {
    var li = document.createElement("li");
    if (i > 0) {
      var leg = document.createElement("div");
      leg.className = "leg";
      leg.textContent = (routeLegs && routeLegs[i - 1])
        ? "↓ " + MODES[travelMode].label + " " + fmtDur(routeLegs[i - 1].duration) + "・" + fmtDist(routeLegs[i - 1].distance)
        : "↓ 計算中…";
      li.appendChild(leg);
    }
    var row = document.createElement("div");
    row.className = "stop-row";
    var no = document.createElement("span");
    no.className = "stop-no"; no.textContent = i + 1;
    var nm = document.createElement("span");
    nm.className = "stop-name"; nm.textContent = s.name; nm.title = s.name;
    var wx = document.createElement("span");
    wx.className = "wxs"; wx.textContent = s.wx || "";
    row.appendChild(no); row.appendChild(nm); row.appendChild(wx);
    [["↑", i === 0, function () { swap(i, i - 1); }],
     ["↓", i === stops.length - 1, function () { swap(i, i + 1); }],
     ["×", false, function () { stopDrive(false); stops.splice(i, 1); routeLegs = null; updateItinerary(); }]
    ].forEach(function (op) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "op"; b.textContent = op[0]; b.disabled = op[1];
      b.addEventListener("click", op[2]);
      row.appendChild(b);
    });
    li.appendChild(row);
    ol.appendChild(li);
  });
  document.getElementById("emptyMsg").style.display = stops.length >= 2 ? "none" : "block";
  refreshMarkers();
  fetchRoute();
  refreshStopsWx();
}

function swap(a, b) {
  stopDrive(false);
  var tmp = stops[a]; stops[a] = stops[b]; stops[b] = tmp;
  routeLegs = null;
  updateItinerary();
}

function refreshMarkers() {
  markers.forEach(function (m) { m.remove(); });
  markers = [];
  if (!realMap) return;
  stops.forEach(function (s, i) {
    var el = document.createElement("div");
    el.className = "r-mark";
    el.textContent = i + 1;
    markers.push(new maplibregl.Marker({ element: el }).setLngLat([s.lon, s.lat]).addTo(realMap));
  });
}

var routeSeq = 0;
function fetchRoute() {
  var sum = document.getElementById("routeSum");
  if (!realMap || stops.length < 2) {
    routeLegs = null;
    lastGeom = null;
    rideUI();
    sum.textContent = "";
    if (realMap && realMap.getSource("route")) {
      realMap.getSource("route").setData({ type: "FeatureCollection", features: [] });
    }
    return;
  }
  var seq = ++routeSeq;
  var coords = stops.map(function (s) { return s.lon + "," + s.lat; }).join(";");
  var url = MODES[travelMode].url + coords + "?overview=full&geometries=geojson&steps=false";
  sum.textContent = "計算中…";
  fetch(url).then(function (r) { return r.json(); }).then(function (d) {
    if (seq !== routeSeq) return; // stale response
    if (!d.routes || !d.routes.length) {
      setMsg("ルートが見つかりませんでした（離島間は" + (travelMode === "car" ? "車" : "徒歩") + "ルート不可）");
      sum.textContent = "";
      routeLegs = null;
      lastGeom = null;
      rideUI();
      return;
    }
    var rt = d.routes[0];
    routeLegs = rt.legs;
    lastGeom = rt.geometry.coordinates;
    rideUI();
    sum.textContent = "合計 " + fmtDur(rt.duration) + "・" + fmtDist(rt.distance);
    setMsg("");
    if (realMap.getSource("route")) {
      realMap.getSource("route").setData({ type: "Feature", properties: {}, geometry: rt.geometry });
    }
    var legs = document.querySelectorAll("#stops .leg");
    legs.forEach(function (el, i) {
      if (routeLegs[i]) el.textContent = "↓ " + MODES[travelMode].label + " " + fmtDur(routeLegs[i].duration) + "・" + fmtDist(routeLegs[i].distance);
    });
  }).catch(function () {
    if (seq !== routeSeq) return;
    setMsg("ルートサービスに接続できませんでした");
    sum.textContent = "";
  });
}

/* ---------- route fly-through (street-level drive / walk view) ---------- */
var ride = { active: false, paused: false, d: 0, total: 0, mult: 1, raf: 0, lastNow: 0 };
var rideCum = null, ridePts = null, rideSeg = 1, ridePrevBearing = null, rideCam = null, rideFrame = 0;
var RIDE_KX = 111.32 * Math.cos(26.45 * Math.PI / 180), RIDE_KY = 110.57;

function ridePointAt(d) {
  while (rideSeg < rideCum.length - 1 && rideCum[rideSeg] < d) rideSeg++;
  while (rideSeg > 1 && rideCum[rideSeg - 1] > d) rideSeg--;
  var f = (d - rideCum[rideSeg - 1]) / Math.max(1e-9, rideCum[rideSeg] - rideCum[rideSeg - 1]);
  return [ridePts[rideSeg - 1][0] + (ridePts[rideSeg][0] - ridePts[rideSeg - 1][0]) * f,
          ridePts[rideSeg - 1][1] + (ridePts[rideSeg][1] - ridePts[rideSeg - 1][1]) * f];
}

// Solve the orbital camera so the eye sits eyeH meters above the street,
// directly over the viewer position: given pitch 85 and the viewport height,
// pick zoom so cameraToCenterDistance*cos(pitch) = eyeH, and shift the map
// center forward by the camera's ground offset.
function rideCamera() {
  var mode = MODES[travelMode];
  var pitch = 85, lat = 26.3;
  var h = realMap.getContainer().clientHeight || 800;
  var c2cPx = 1.5 * h; // camera-to-center distance in px (fov 36.87 deg)
  var mpp = mode.eyeH / (c2cPx * Math.cos(pitch * Math.PI / 180));
  var zoom = Math.min(21.5, Math.log2(156543.03392 * Math.cos(lat * Math.PI / 180) / mpp));
  var aheadKm = c2cPx * mpp * Math.sin(pitch * Math.PI / 180) / 1000;
  return { pitch: pitch, zoom: zoom, aheadKm: aheadKm, lookKm: mode.look, kmps: mode.kmps };
}

function rideUI() {
  var play = document.getElementById("playBtn"), stop = document.getElementById("stopBtn");
  play.disabled = !lastGeom && !ride.active;
  stop.disabled = !ride.active;
  play.textContent = !ride.active ? "▶ 走行ビュー 開始" : (ride.paused ? "▶ 再開" : "⏸ 一時停止");
  if (!ride.active) document.getElementById("rideInfo").textContent = "";
}

function rideStep(now) {
  if (!ride.active || ride.paused) return;
  var dt = Math.min(0.1, (now - ride.lastNow) / 1000);
  ride.lastNow = now;
  ride.d += dt * rideCam.kmps * ride.mult;
  if (ride.d >= ride.total) { endRide(true); return; }
  var pos = ridePointAt(ride.d);
  var look = ridePointAt(Math.min(ride.total, ride.d + rideCam.lookKm));
  var bx = (look[0] - pos[0]) * RIDE_KX, by = (look[1] - pos[1]) * RIDE_KY;
  if (bx !== 0 || by !== 0) {
    var target = Math.atan2(bx, by) * 180 / Math.PI;
    if (ridePrevBearing === null) ridePrevBearing = target;
    var diff = ((target - ridePrevBearing + 540) % 360) - 180;
    ridePrevBearing += diff * 0.05;
  }
  var center = ridePointAt(Math.min(ride.total, ride.d + rideCam.aheadKm));
  realMap.jumpTo({ center: center, bearing: ridePrevBearing || 0, pitch: rideCam.pitch, zoom: rideCam.zoom });
  if (++rideFrame % 12 === 0) {
    document.getElementById("rideInfo").textContent =
      Math.round(ride.d / ride.total * 100) + "%・残り " + fmtDist((ride.total - ride.d) * 1000);
  }
  ride.raf = requestAnimationFrame(rideStep);
}

function startRide() {
  if (!realMap || !lastGeom || lastGeom.length < 2) return;
  ridePts = lastGeom;
  rideCum = [0];
  for (var i = 1; i < ridePts.length; i++) {
    var dx = (ridePts[i][0] - ridePts[i - 1][0]) * RIDE_KX, dy = (ridePts[i][1] - ridePts[i - 1][1]) * RIDE_KY;
    rideCum.push(rideCum[i - 1] + Math.hypot(dx, dy));
  }
  ride.total = rideCum[rideCum.length - 1];
  ride.d = 0; rideSeg = 1; ridePrevBearing = null; rideFrame = 0;
  rideCam = rideCamera();
  ride.active = true; ride.paused = false;
  if (realMap.getLayer("bld3d")) realMap.setPaintProperty("bld3d", "fill-extrusion-opacity", 0.8);
  rideUI();
  ride.lastNow = performance.now();
  ride.raf = requestAnimationFrame(rideStep);
}

function pauseRide() {
  ride.paused = true;
  cancelAnimationFrame(ride.raf);
  rideUI();
}

function resumeRide() {
  ride.paused = false;
  ride.lastNow = performance.now();
  rideUI();
  ride.raf = requestAnimationFrame(rideStep);
}

function endRide(finished) {
  if (!ride.active) return;
  ride.active = false; ride.paused = false;
  cancelAnimationFrame(ride.raf);
  if (realMap && realMap.getLayer("bld3d")) realMap.setPaintProperty("bld3d", "fill-extrusion-opacity", 0.95);
  rideUI();
  if (finished && realMap && stops.length >= 2) {
    realMap.fitBounds(boundsOf(stops), { padding: { top: 90, right: 90, bottom: 90, left: 320 }, maxZoom: 15, duration: 1800 });
  }
}

function stopDrive(finished) { endRide(finished); } // shared by add/remove/mode/tab handlers

document.getElementById("playBtn").addEventListener("click", function () {
  if (!ride.active) startRide();
  else if (ride.paused) resumeRide();
  else pauseRide();
});
document.getElementById("stopBtn").addEventListener("click", function () { endRide(false); });
document.querySelectorAll(".r-spd .s").forEach(function (b) {
  b.addEventListener("click", function () {
    ride.mult = +b.getAttribute("data-s");
    document.querySelectorAll(".r-spd .s").forEach(function (x) { x.classList.toggle("active", x === b); });
  });
});

/* ---------- mode & buildings toggles ---------- */
function setMode(m) {
  if (travelMode === m) return;
  stopDrive(false);
  travelMode = m;
  document.getElementById("modeCar").classList.toggle("active", m === "car");
  document.getElementById("modeFoot").classList.toggle("active", m === "foot");
  routeLegs = null;
  updateItinerary();
}
document.getElementById("modeCar").addEventListener("click", function () { setMode("car"); });
document.getElementById("modeFoot").addEventListener("click", function () { setMode("foot"); });

function applyBld() {
  if (!realMap || !realMap.getLayer("bld3d")) return;
  var on = document.getElementById("bld").checked;
  realMap.setLayoutProperty("bld3d", "visibility", on ? "visible" : "none");
}
document.getElementById("bld").addEventListener("change", applyBld);

/* ---------- real-time weather (Open-Meteo) + rain radar (RainViewer) ---------- */
function wxInfo(code) {
  if (code === 0) return { i: "☀️", t: "快晴", k: "sun" };
  if (code === 1) return { i: "🌤️", t: "晴れ", k: "sun" };
  if (code === 2) return { i: "⛅", t: "晴れ時々くもり", k: "sun" };
  if (code === 3) return { i: "☁️", t: "くもり", k: "" };
  if (code === 45 || code === 48) return { i: "🌫️", t: "霧", k: "" };
  if (code >= 51 && code <= 57) return { i: "🌦️", t: "霧雨", k: "rain" };
  if (code >= 61 && code <= 67) return { i: "🌧️", t: "雨", k: "rain" };
  if (code >= 71 && code <= 77) return { i: "🌨️", t: "雪", k: "" };
  if (code >= 80 && code <= 82) return { i: "🌦️", t: "にわか雨", k: "rain" };
  if (code === 85 || code === 86) return { i: "🌨️", t: "にわか雪", k: "" };
  if (code >= 95) return { i: "⛈️", t: "雷雨", k: "rain" };
  return { i: "☁️", t: "—", k: "" };
}

function fetchWx(lats, lons) {
  var url = "https://api.open-meteo.com/v1/forecast?latitude=" + lats.join(",") +
            "&longitude=" + lons.join(",") +
            "&current=temperature_2m,weather_code,precipitation,wind_speed_10m&timezone=Asia%2FTokyo";
  return fetch(url).then(function (r) { return r.json(); }).then(function (d) {
    return Array.isArray(d) ? d : [d];
  });
}

function refreshCenterWx() {
  if (!realMap) return;
  var c = realMap.getCenter();
  if (c.lat < 24 || c.lat > 28.5 || c.lng < 125 || c.lng > 130.5) return; // stay regional
  fetchWx([c.lat.toFixed(3)], [c.lng.toFixed(3)]).then(function (arr) {
    var cur = arr[0] && arr[0].current;
    if (!cur) return;
    var w = wxInfo(cur.weather_code);
    document.getElementById("wxIcon").textContent = w.i;
    document.getElementById("wxMain").textContent = w.t + " " + Math.round(cur.temperature_2m) + "°C";
    var t = (cur.time || "").slice(11, 16);
    document.getElementById("wxSub").textContent =
      "降水 " + cur.precipitation + "mm・風 " + Math.round(cur.wind_speed_10m) + "km/h・地図中心 " + t + " 更新";
    var mapEl = document.getElementById("map");
    mapEl.classList.toggle("wx-rain", w.k === "rain");
    mapEl.classList.toggle("wx-sun", w.k === "sun");
  }).catch(function () {
    document.getElementById("wxMain").textContent = "天気を取得できませんでした";
  });
}

function refreshStopsWx() {
  if (!stops.length) return;
  var snapshot = stops.slice();
  fetchWx(snapshot.map(function (s) { return s.lat.toFixed(3); }),
          snapshot.map(function (s) { return s.lon.toFixed(3); }))
    .then(function (arr) {
      snapshot.forEach(function (s, i) {
        var cur = arr[i] && arr[i].current;
        if (cur) s.wx = wxInfo(cur.weather_code).i + " " + Math.round(cur.temperature_2m) + "°";
      });
      // update rendered rows in place (list may have re-rendered meanwhile)
      var rows = document.querySelectorAll("#stops .stop-row .wxs");
      rows.forEach(function (el, i) { if (stops[i] && stops[i].wx) el.textContent = stops[i].wx; });
    }).catch(function () {});
}

var radarRetryArmed = false;
function updateRadar() {
  if (!realMap) return;
  if (!realMap.isStyleLoaded()) { // style still loading: retry once it settles
    if (!radarRetryArmed) {
      radarRetryArmed = true;
      realMap.once("idle", function () { radarRetryArmed = false; updateRadar(); });
    }
    return;
  }
  var on = document.getElementById("radar").checked;
  try {
    if (realMap.getLayer("rainradar")) realMap.removeLayer("rainradar");
    if (realMap.getSource("rainradar")) realMap.removeSource("rainradar");
  } catch (e) { /* style transitions */ }
  if (!on) return;
  fetch("https://api.rainviewer.com/public/weather-maps.json")
    .then(function (r) { return r.json(); })
    .then(function (d) {
      var past = d.radar && d.radar.past;
      if (!past || !past.length || realMap.getLayer("rainradar")) return;
      var path = past[past.length - 1].path;
      try {
        realMap.addSource("rainradar", {
          type: "raster",
          tiles: [d.host + path + "/256/{z}/{x}/{y}/2/1_1.png"],
          tileSize: 256,
          maxzoom: 9, // RainViewer serves low zooms only; overscale beyond
          attribution: "雨雲: RainViewer"
        });
        realMap.addLayer({
          id: "rainradar", type: "raster", source: "rainradar",
          paint: { "raster-opacity": 0.6, "raster-fade-duration": 300 }
        }, realMap.getLayer("bld3d") ? "bld3d" : undefined);
      } catch (e) { /* style got torn down mid-flight; next refresh retries */ }
    }).catch(function () {});
}
document.getElementById("radar").addEventListener("change", updateRadar);

setInterval(function () {
  if (!realMap) return;
  refreshCenterWx();
  refreshStopsWx();
  if (document.getElementById("radar").checked) updateRadar(); // pull newest radar frame
}, 10 * 60 * 1000);
window.__wx = { center: refreshCenterWx, stops: refreshStopsWx, radar: updateRadar };

/* ---------- search box wiring ---------- */
var qInput = document.getElementById("q");
qInput.addEventListener("input", function () {
  var q = qInput.value.trim();
  clearTimeout(sugTimer);
  if (q.length < 2) { clearSug(); return; }
  sugTimer = setTimeout(function () { searchSpots(q, false); }, 400);
});
qInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter") { e.preventDefault(); doAdd(); }
  if (e.key === "Escape") clearSug();
});
document.getElementById("addBtn").addEventListener("click", doAdd);
function doAdd() {
  var q = qInput.value.trim();
  if (sugResults.length) { addStop(sugResults[0]); return; }
  if (!q) return;
  pendingAdd = true;
  clearTimeout(sugTimer);
  searchSpots(q, true);
}
document.addEventListener("click", function (e) {
  if (!e.target.closest(".r-search")) clearSug();
});
window.__addStop = addStop;
window.__startDrive = startRide;
window.__ride = ride;

/* ============ view switcher ============ */
document.querySelectorAll(".viewtabs .vt").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var target = btn.getAttribute("data-view");
    if (target !== "real") stopDrive(false);
    document.querySelectorAll(".viewtabs .vt").forEach(function (b) {
      b.classList.toggle("active", b === btn);
      b.setAttribute("aria-selected", b === btn ? "true" : "false");
    });
    document.querySelectorAll(".view").forEach(function (v) {
      v.classList.toggle("active", v.id === "view-" + target);
    });
    if (target === "real") {
      initRealMap();
      if (realMap) realMap.resize();
    }
  });
});
"""

out = """<meta charset="utf-8">
<title>沖縄 3Dマップ — 立体地形図 &amp; 旅程プランナー</title>
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css">
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<style>{terrain_css}{extra_css}</style>

<div class="viewtabs" role="tablist" aria-label="表示切替">
  <button type="button" class="vt active" data-view="terrain" role="tab" aria-selected="true">立体地形図</button>
  <button type="button" class="vt" data-view="real" role="tab" aria-selected="false">リアルマップ・旅程</button>
</div>

<!-- ============ view: terrain diorama ============ -->
<div id="view-terrain" class="view active">
{terrain_markup}
</div>
{real_markup}
<script>{terrain_js}</script>
<script>
(function () {{
  "use strict";
{real_js}
}})();
</script>
""".format(terrain_css=terrain_css, extra_css=extra_css, terrain_markup=terrain_markup,
           real_markup=real_markup, terrain_js=terrain_js, real_js=real_js)

dest = os.path.join(BASE, "okinawa-combined.html")
io.open(dest, "w", encoding="utf-8").write(out)
print("wrote", dest, len(out), "chars")
