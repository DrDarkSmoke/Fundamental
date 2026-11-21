#!/usr/bin/env python3
"""
 Hammer Pro — Preferred Lookup v8
Native desktop (tkinter). Window-title scanner for Hammer Pro sync.
"""
import tkinter as tk
from tkinter import messagebox
import calendar
import gzip
import json, os, sys, threading, time, webbrowser, re
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

try:
    import win32gui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# ══════════════════════════════════════════════════════
#  PALETTE
# ══════════════════════════════════════════════════════
BG   = "#0a0f1a"
BG2  = "#0d1421"
BG3  = "#111827"
BD   = "#1e2d45"
ACC  = "#1e3a5f"
BL   = "#60a5fa"
BL2  = "#3b82f6"
GR   = "#22c55e"
AM   = "#f59e0b"
RD   = "#ef4444"
PU   = "#a78bfa"
TE   = "#34d399"
OR   = "#fb923c"
PK   = "#f472b6"
TX   = "#e2e8f0"
TX2  = "#94a3b8"
TX3  = "#64748b"
TX4  = "#475569"
TX5  = "#334155"

FN   = "Courier New"   # monospace
FNU  = "Segoe UI"      # ui

CEF_SET = set([
    "ACP","ACV","ADX","AEF","AFB","AGD","AIO","AOD","ARDC","ASA","ASG","ASGI","AVK","AWF","AWP",
    "BANX","BBN","BCAT","BCV","BCX","BDJ","BGB","BGH","BGR","BGT","BGX","BGY","BHK","BHV","BIT",
    "BKT","BLW","BME","BMEZ","BMN","BOE","BPRE","BRW","BSL","BST","BSTZ","BTO","BTT","BTX","BTZ",
    "BUI","BWG","BXSY","CAF","CCD","CCIF","CEE","CEF","CET","CEV","CFND","CGO","CHI","CHW","CHY",
    "CIF","CII","CIK","CLM","CMU","CPZ","CRF","CSQ","CXE","CXH","DBL","DFP","DHF","DHY","DLY",
    "DMA","DMB","DMO","DNP","DPG","DSL","DSM","DSU","DTF","DXYZ","EAD","EARN","ECAT","ECC","ECF",
    "EDD","EDF","EEA","EFR","EFT","EHI","EIC","EIM","EMD","EMF","EOD","EOI","EOS","EOT","ERC",
    "ERH","ETB","ETG","ETJ","ETO","ETV","ETW","ETX","ETY","EVF","EVG","EVN","EVT","EVV","EXG",
    "FAX","FCO","FCT","FFA","FFC","FINS","FLC","FMN","FMY","FOF","FPF","FRA","FSCO","FSSL","FT",
    "FTF","FTHY","FUND","FXBY","GAB","GAM","GBAB","GCV","GDL","GDO","GDV","GF","GGN","GGT","GGZ",
    "GHY","GLO","GLQ","GLU","GLV","GNT","GOF","GRF","GRX","GUG","GUT","HEQ","HERZ","HFRO","HGLB",
    "HIO","HIX","HPF","HPI","HPS","HQH","HQL","HTD","HYI","HYT","IAE","IAF","IDE","IFN","IGA",
    "IGD","IGI","IGR","IHD","IIF","IIM","IQI","ISD","JCE","JFR","JGH","JHI","JHS","JLS","JMM",
    "JOF","JPC","JQC","JRI","JRS","KF","KIO","KTF","KYN","LDP","LEO","LGI","MCI","MCN","MCR",
    "MEGI","MFM","MGF","MHD","MHF","MIN","MIY","MMD","MMT","MMU","MPA","MPV","MQY","MSD","MUA",
    "MUC","MUJ","MXE","MXF","MYI","MYN","NAC","NAD","NAN","NAZ","NBB","NBH","NBXG","NCA","NCV",
    "NCZ","NDMO","NEA","NFJ","NHS","NIE","NIM","NKX","NMAI","NMCO","NMI","NML","NMS","NMT","NMZ",
    "NNY","NOM","NPCT","NPFD","NPV","NQP","NRK","NRO","NUV","NUW","NVG","NXG","NXJ","NXP","NZF",
    "OCCI","OIA","OPP","OXLC","PAI","PAXS","PCF","PCM","PCN","PCQ","PDCC","PDI","PDO","PDT","PDX",
    "PEO","PFD","PFL","PFN","PFO","PGP","PGZ","PHK","PHYS","PIM","PML","PMM","PMO","PNI","PPT",
    "PSF","PSLV","PTA","PTY","QQQX","RA","RCG","RCS","RFI","RFM","RFMZ","RGT","RIV","RLTY","RMI",
    "RMM","RMMZ","RMT","RNP","RQI","RSF","RVT","SABA","SBI","SCD","SDHY","SOR","SPE","SPMC","SPPP",
    "SPXX","SRV","STEW","STK","SWZ","TBLD","TDF","TEI","THQ","THW","TSI","TWN","TY","TYG","USA",
    "UTF","UTG","VBF","VCV","VFL","VGI","VGM","VKI","VKQ","VLT","VMO","VPV","VTN","VVR","WDI",
    "WEA","WIA","WIW","XFLT","ZTR"
])

# ══════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════
def _ddir():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'data')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def _load(fn):
    p = os.path.join(_ddir(), fn)
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return {}

def _save(fn, d):
    os.makedirs(_ddir(), exist_ok=True)
    with open(os.path.join(_ddir(), fn), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def rating_col(r):
    return {'GOOD': GR, 'MID': AM, 'NF': BL, 'NR': TX2, 'BAD': RD}.get(str(r).strip(), TX3)

def mn4_col(m):
    return {'YES': GR, 'MIGHT': AM, 'NO': RD}.get(str(m).strip(), TX3)

def type_col(f):
    if not f: return TX2
    fl = f.lower()
    if f.strip() == 'Fixed': return BL
    if ('float' in fl) and ('fixed' in fl or 'fix' in fl): return PU
    if 'float' in fl: return TE
    if 'bb' in fl: return OR
    if 'reset' in fl: return PK
    if 'conv' in fl: return AM
    return TX2

def parse_coupon(c):
    if not c: return None
    try:
        return float(str(c).replace('%','').replace(',','.').strip())
    except:
        return None

def is_floating(p):
    f = (p.get('fixFloat') or '').lower()
    c = (p.get('coupon') or '').lower().strip()
    return 'float' in f or c in ('float','floating')

def fmt_div(d):
    if d is None: return None
    try:
        return f"${float(d):.4f} / Q"
    except:
        return None

def fmt_price(p):
    if p is None: return None
    try:
        return f"${float(p):.2f}"
    except:
        return None

def fmt_pct(p):
    if p is None: return None
    try:
        return f"{float(p):.2f}%"
    except:
        return None

def clean(v):
    if v is None: return ''
    s = str(v).strip()
    return '' if s.lower() in ('none','null','nan','#n/a','#value!') else s


# ══════════════════════════════════════════════════════
#  WINDOW TITLE SCANNER
# ══════════════════════════════════════════════════════

# Hammer Pro Level II window title pattern:
#   "TICKER - Company Name... - Level II"
# This is the most reliable source — we prefer the LEFTMOST such window.
_LEVEL2_RE = re.compile(
    r'^([A-Z]{1,6}(?:-[A-Z0-9]{0,2})?)\s*(?:[-\u2013\u2014].*)?Level\s*II(?:\b|$)',
    re.IGNORECASE
)

def get_window_info():
    """Return list of (x_pos, y_pos, title) for all visible windows."""
    wins = []
    if not HAS_WIN32:
        return wins
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if t:
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    wins.append((rect[0], rect[1], t))  # (left_x, top_y, title)
                except Exception:
                    wins.append((9999, 9999, t))
    try:
        win32gui.EnumWindows(cb, None)
    except Exception:
        pass
    return wins

# Fallback noise filter for non-Level-II scan
_SCAN_SKIP = {
    'CHART','DATA','LEVEL','DAILY','HISTORICAL','HAMMER','PRO',
    'PREFERRED','LOOKUP','SPREAD','SYMBOL','LAST','OPEN','HIGH',
    'LOW','CLOSE','BID','ASK','SIZE','TIME','NET','RAW','IND','CHG','IMBAL',
    'INC','LLC','LTD','CORP','GROUP','TRUST','CAPITAL','STOCK','INCOME',
    'EQUITY','DIVERSIFIED','MANAGED','TAX','CLASS','RATE','SERIES',
    'CUMULATIVE','NON','VANCE','EATON','GOLDMAN','SACHS',
    'CEF','MIN','FUND',
}
_HYPH_RE  = re.compile(r'(?<![A-Z0-9])([A-Z]{1,6}-[A-Z0-9]{0,2})(?![A-Z0-9])')
_PLAIN_RE = re.compile(r'\b([A-Z]{2,7})\b')

def _known_title_ticker(title, tickers):
    u = title.upper()
    for w in sorted((t for t in tickers if t), key=len, reverse=True):
        pat = r'(?<![A-Z0-9])' + re.escape(w.upper()) + r'(?![A-Z0-9])'
        if re.search(pat, u):
            return w.upper()
    return None

def find_ticker(win_info, pref_tickers, cef_tickers):
    """
    Primary:  read the LEFTMOST visible "Level II" Hammer Pro window.
              Title format: "TICKER - Company Name - Level II"
              Only this window reflects the user's active click.
    Fallback: scan all short window titles for known tickers.
    """
    # ── PRIMARY: top-left Level II window ──────────────
    level2 = []
    for x, y, title in win_info:
        m = _LEVEL2_RE.match(title.strip())
        if m:
            level2.append((x, y, m.group(1).upper()))

    if level2:
        level2.sort(key=lambda w: (w[0], w[1]))   # leftmost, then topmost
        return level2[0][2]

    # ── FALLBACK: scan all short titles ─────────────────
    pref_hyph, pref_plain, cef_hyph, cef_plain = [], [], [], []
    for _, _, title in win_info:
        t = title.strip()
        if not t: continue
        if 'PREFERRED LOOKUP' in t.upper(): continue
        if len(t) > 65: continue
        u = t.upper()
        known = _known_title_ticker(u, pref_tickers)
        if known:
            pref_hyph.append(known)
            continue
        known = _known_title_ticker(u, cef_tickers)
        if known:
            cef_hyph.append(known)
            continue
        for m in _HYPH_RE.finditer(u):
            w = m.group(1)
            if w in pref_tickers:  pref_hyph.append(w)
            elif w in cef_tickers: cef_hyph.append(w)
        for m in _PLAIN_RE.finditer(u):
            w = m.group(1)
            if w in _SCAN_SKIP: continue
            if w in pref_tickers:  pref_plain.append(w)
            elif w in cef_tickers: cef_plain.append(w)

    if pref_hyph:  return pref_hyph[0]
    if pref_plain: return pref_plain[0]
    if cef_hyph:   return cef_hyph[0]
    if cef_plain:  return cef_plain[0]
    return None


# ══════════════════════════════════════════════════════
#  SCROLLABLE FRAME HELPER
# ══════════════════════════════════════════════════════
class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=kw.pop('bg', BG), **kw)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        self.sb = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview,
                               bg=BG2, troughcolor=BG, width=6)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')

        self.canvas.configure(yscrollcommand=self.sb.set)
        self.sb.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.inner.bind('<Configure>', self._on_inner)
        self.canvas.bind('<Configure>', self._on_canvas)
        self.canvas.bind_all('<MouseWheel>', self._on_wheel)

    def _on_inner(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas(self, e):
        self.canvas.itemconfig(self._win, width=e.width)

    def _on_wheel(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.canvas.yview_moveto(0)


# ══════════════════════════════════════════════════════
#  TOOLTIP
# ══════════════════════════════════════════════════════
class Tip:
    def __init__(self, widget, text):
        self.w = widget
        self.text = text
        self.tip = None
        widget.bind('<Enter>', self.show)
        widget.bind('<Leave>', self.hide)

    def show(self, e=None):
        x, y, _, _ = self.w.bbox('insert') if hasattr(self.w, 'bbox') else (0,0,0,0)
        x += self.w.winfo_rootx() + 20
        y += self.w.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.w)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f'+{x}+{y}')
        tk.Label(self.tip, text=self.text, bg=BG3, fg=TX2, font=(FNU, 8),
                 padx=6, pady=3, relief='flat', bd=1).pack()

    def hide(self, e=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ══════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════
class App:
    W, H = 330, 590

    def __init__(self):
        self.pref = {}
        self.common = {}
        self.ptoc = {}
        self.cef = {}
        self.earnings = {}
        self.dividends = {}
        self.current = None
        self.scan_on = False
        self.last_scan = None
        self._ac_items = []
        self._common_expanded = {}
        self._take_marks = {}
        self._startup_status = None
        self._startup_bar = None
        self._startup_bar_fill = None

        self.root = tk.Tk()
        self.root.title("Hammer Pro — Preferred Lookup v8")
        self.root.geometry(f"{self.W}x{self.H}")
        self.root.minsize(300, 450)
        self.root.configure(bg=BG)
        try:
            self.root.iconbitmap(default='')
        except Exception:
            pass

        self._reload()
        self._build_ui()
        self._build_categories()

        if self._needs_startup_refresh():
            self._show_startup_loading()
            self.root.after(150, self._start_startup_refresh)
        else:
            self._show_empty()
            self._start_scanner_if_available()

        self.root.mainloop()

    # ── DATA ─────────────────────────────────────────
    def _normalize_cef_data(self, raw):
        out = {}
        if not isinstance(raw, dict):
            return out
        for sym, value in raw.items():
            s = clean(sym).upper()
            if not s:
                continue
            if isinstance(value, dict):
                source = (value.get('sectors') or value.get('indexes') or
                          value.get('sector') or value.get('index') or [])
            else:
                source = value
            items = source if isinstance(source, list) else re.split(r'[,;\n]+', str(source or ''))
            sectors = []
            for item in items:
                text = clean(item)
                if text and text not in sectors:
                    sectors.append(text)
            row = {'sectors': sectors}
            if isinstance(value, dict):
                for key in ('lastPrice', 'lastPriceDate', 'yahooSymbol',
                            'nav', 'discount', 'navDate', 'fundName'):
                    if key in value:
                        row[key] = value.get(key)
            out[s] = row
        return out

    def _cef_sectors(self, sym):
        return self.cef.get(sym.upper(), {}).get('sectors', [])

    def _normalize_earnings_data(self, raw):
        out = {}
        if not isinstance(raw, dict):
            return out
        for sym, value in raw.items():
            s = clean(sym).upper()
            if not s:
                continue
            if isinstance(value, dict):
                session = clean(value.get('session')) or 'daytime'
                item = {
                    'date': clean(value.get('date')),
                    'label': clean(value.get('label')),
                    'session': session,
                }
            else:
                item = {'date': '', 'label': clean(value), 'session': 'daytime'}
            if item.get('date') or item.get('label'):
                out[s] = item
        return out

    def _normalize_dividend_events(self, raw):
        out = {}
        if not isinstance(raw, dict):
            return out
        for sym, value in raw.items():
            s = clean(sym).upper()
            if not s:
                continue
            if isinstance(value, dict):
                item = {
                    'date': clean(value.get('date')),
                    'label': clean(value.get('label')),
                }
            else:
                item = {'date': '', 'label': clean(value)}
            if item.get('date') or item.get('label'):
                out[s] = item
        return out

    def _date_label(self, iso_date):
        try:
            y, m, d = [int(x) for x in iso_date.split('-')]
            dt = date(y, m, d)
            return f"{d} {calendar.month_abbr[m]} {calendar.day_abbr[dt.weekday()]}"
        except Exception:
            return clean(iso_date)

    def _earning_for_common(self, sym):
        if not sym:
            return None
        return self.earnings.get(sym.upper())

    def _dividend_for_pref(self, sym):
        if not sym:
            return None
        return self.dividends.get(sym.upper())

    def _earning_text(self, item):
        if not item:
            return ''
        if clean(item.get('session')).lower() == 'tentative':
            return 'E=Tentative'
        label = self._date_label(clean(item.get('date'))) or clean(item.get('label'))
        session = clean(item.get('session')) or 'daytime'
        session = 'After Close' if session.lower() == 'after close' else ''
        return f"E={label}{('/' + session) if session else ''}".strip()

    def _dividend_text(self, item):
        if not item:
            return ''
        label = self._date_label(clean(item.get('date'))) or clean(item.get('label'))
        return f"D={label}".strip()

    def _earning_is_past(self, item):
        try:
            y, m, d = [int(x) for x in clean(item.get('date')).split('-')]
            return date(y, m, d) < date.today()
        except Exception:
            return False

    def _event_is_today_or_tomorrow(self, item):
        try:
            y, m, d = [int(x) for x in clean(item.get('date')).split('-')]
            delta = (date(y, m, d) - date.today()).days
            return delta in (0, 1)
        except Exception:
            return False

    def _set_take_mark(self, key, ok):
        self._take_marks[key] = {'ok': bool(ok), 'until': time.time() + 5}
        self.root.after(5100, self._clear_take_marks)

    def _take_mark(self, key):
        mark = self._take_marks.get(key)
        if not mark:
            return None
        if time.time() > mark.get('until', 0):
            self._take_marks.pop(key, None)
            return None
        return mark

    def _draw_take_mark(self, parent, key, bg, side='right'):
        mark = self._take_mark(key)
        if not mark:
            return
        ok = mark.get('ok')
        tk.Label(parent, text='✓' if ok else '✕',
                 fg=GR if ok else RD, bg=bg,
                 font=(FNU, 10, 'bold')).pack(side=side, padx=(4,0))

    def _clear_take_marks(self):
        changed = False
        now = time.time()
        for key in list(self._take_marks.keys()):
            if now > self._take_marks[key].get('until', 0):
                self._take_marks.pop(key, None)
                changed = True
        if changed and self.current:
            self.select(self.current)

    def _yahoo_symbol_candidates(self, sym, preferred=False):
        s = clean(sym).upper()
        if not s:
            return []
        candidates = [s]
        if preferred and '-' in s:
            base, suffix = s.split('-', 1)
            suffix = suffix.replace('-', '')
            if not suffix:
                candidates.append(f"{base}-P")
            if suffix and not suffix.startswith('P'):
                candidates.append(f"{base}-P{suffix}")
            if suffix:
                candidates.append(f"{base}-P{suffix.replace('.', '')}")
        elif preferred and len(s) > 4 and s.endswith(('P', 'N', 'O', 'L', 'I', 'Z')):
            candidates.append(s)
        if '.' in s:
            candidates.append(s.replace('.', '-'))
        out = []
        for item in candidates:
            if item and item not in out:
                out.append(item)
        return out

    def _read_url(self, url, timeout=12):
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json,text/html,*/*',
            'Accept-Encoding': 'gzip, deflate',
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
        if raw[:2] == b'\x1f\x8b':
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', 'ignore')

    def _fetch_yahoo_price(self, sym, preferred=False):
        errors = []
        for candidate in self._yahoo_symbol_candidates(sym, preferred=preferred):
            q = urllib.parse.quote(candidate, safe='')
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{q}?range=1d&interval=1d"
            try:
                data = json.loads(self._read_url(url))
                chart = data.get('chart', {})
                err = chart.get('error')
                if err:
                    errors.append(f"{candidate}: {err.get('description') or err}")
                    continue
                result = (chart.get('result') or [None])[0]
                meta = (result or {}).get('meta', {})
                price = meta.get('regularMarketPrice')
                if price is None:
                    quote = ((result or {}).get('indicators', {}).get('quote') or [{}])[0]
                    close = quote.get('close') or []
                    price = next((v for v in reversed(close) if v is not None), None)
                if price is not None:
                    return candidate, float(price)
                errors.append(f"{candidate}: fiyat yok")
            except Exception as exc:
                errors.append(f"{candidate}: {exc}")
        raise RuntimeError('; '.join(errors) or f"{sym}: Yahoo fiyat bulunamadı")

    def _fetch_yahoo_market_cap(self, sym):
        errors = []
        for candidate in self._yahoo_symbol_candidates(sym, preferred=False):
            q = urllib.parse.quote(candidate, safe='')
            url = f"https://finance.yahoo.com/quote/{q}/"
            try:
                html = self._read_url(url)
                m = re.search(r'data-field="marketCap"[^>]*>([^<]+)<', html)
                if not m:
                    m = re.search(r'data-value="([^"]+)"[^>]*data-field="marketCap"', html)
                if m:
                    cap = clean(m.group(1)).replace(' ', '')
                    if cap:
                        if cap[0].isdigit():
                            cap = f"${cap}"
                        return candidate, cap
                errors.append(f"{candidate}: market cap yok")
            except Exception as exc:
                errors.append(f"{candidate}: {exc}")
        raise RuntimeError('; '.join(errors) or f"{sym}: Yahoo market cap bulunamadı")

    def _market_cap_value(self, value):
        s = clean(value).replace('$', '').replace(',', '').upper()
        if not s or s in ('N/A', 'NA', '—'):
            return None
        mult = 1
        if s.endswith('T'):
            mult = 1_000_000_000_000
            s = s[:-1]
        elif s.endswith('B'):
            mult = 1_000_000_000
            s = s[:-1]
        elif s.endswith('M'):
            mult = 1_000_000
            s = s[:-1]
        try:
            return float(s) * mult
        except Exception:
            return None

    def _parse_date_value(self, value):
        s = clean(value)
        if not s:
            return None
        s = s.replace('/', '-').replace('.', '-')
        parts = [p for p in s.split('-') if p]
        if len(parts) != 3:
            return None
        try:
            a, b, c = [int(p) for p in parts]
            if a > 31:
                y, m, d = a, b, c
            elif c > 31:
                d, m, y = a, b, c
            else:
                d, m, y = a, b, c
                if y < 100:
                    y += 2000
            return date(y, m, d)
        except Exception:
            return None

    def _year_only_maturity_date(self, year):
        today = date.today()
        try:
            year = int(year)
            if year < today.year:
                return None
            if year == today.year:
                end_of_year = date(year, 12, 31)
                return end_of_year if end_of_year > today else None
            return date(year, today.month, today.day)
        except Exception:
            return None

    def _parse_maturity_date_value(self, maturity_value, call_date_value):
        direct = self._parse_date_value(maturity_value)
        if direct:
            return direct

        s = clean(maturity_value)
        if not re.fullmatch(r'\d{4}', s):
            return None

        year = int(s)
        call_dt = self._parse_date_value(call_date_value)
        if call_dt and call_dt > date.today():
            try:
                assumed = date(year, call_dt.month, call_dt.day)
                if assumed > date.today():
                    return assumed
            except Exception:
                pass
        return self._year_only_maturity_date(year)

    def _calc_approx_yield(self, annual_income, current_price, target_price, target_date):
        if not target_date or not current_price or current_price <= 0:
            return None
        years = (target_date - date.today()).days / 365.25
        if years <= 0:
            return None
        try:
            return ((annual_income + ((target_price - current_price) / years)) /
                    ((target_price + current_price) / 2)) * 100
        except Exception:
            return None

    def _calc_pref_yields(self, pref_row):
        try:
            annual = float(pref_row.get('div')) * 4
            price = float(pref_row.get('lastPrice'))
        except Exception:
            return None, None
        ytc = self._calc_approx_yield(
            annual, price, 25, self._parse_date_value(pref_row.get('callDate')))
        ytm = self._calc_approx_yield(
            annual, price, 25,
            self._parse_maturity_date_value(pref_row.get('matureDate'),
                                            pref_row.get('callDate')))
        return ytc, ytm

    def _apply_pref_market_data(self, sym, price, yahoo_sym=None):
        p = dict(self.pref.get(sym, {}))
        p['lastPrice'] = round(float(price), 4)
        p['lastPriceDate'] = date.today().isoformat()
        if yahoo_sym:
            p['yahooSymbol'] = yahoo_sym
        try:
            p['currentYield'] = round((float(p.get('div')) * 4 / float(price)) * 100, 2)
        except Exception:
            pass
        ytc, ytm = self._calc_pref_yields(p)
        if ytc is not None:
            p['ytc'] = round(ytc, 2)
        else:
            p.pop('ytc', None)
        if ytm is not None:
            p['ytm'] = round(ytm, 2)
        else:
            p.pop('ytm', None)
        self.pref[sym] = p
        return p

    def _apply_cef_market_data(self, sym, price, yahoo_sym=None):
        row = dict(self.cef.get(sym, {'sectors': []}))
        row['lastPrice'] = round(float(price), 4)
        row['lastPriceDate'] = date.today().isoformat()
        if yahoo_sym:
            row['yahooSymbol'] = yahoo_sym
        self.cef[sym] = row
        return row

    def _fetch_cef_connect_data(self):
        """Tek istekle cefconnect.com'dan tüm CEF'lerin NAV ve Discount verilerini çeker.
        1 günde 1 kez çağrılır; ban riski minimumdur."""
        # cefconnect.com'un kendi frontend'i tarafından kullanılan JSON endpoint
        url = "https://www.cefconnect.com/api/v3/pricingdata"
        headers_override = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.cefconnect.com/',
            'Origin': 'https://www.cefconnect.com',
        }
        req = urllib.request.Request(url, headers=headers_override)
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read()
        if raw[:2] == b'\x1f\x8b':
            raw = gzip.decompress(raw)
        text = raw.decode('utf-8', 'ignore')
        records = json.loads(text)
        # API farklı sarmalama yapısı dönebilir
        if isinstance(records, dict):
            records = (records.get('data') or records.get('Data') or
                       records.get('funds') or records.get('Funds') or [])
        out = {}
        for rec in (records if isinstance(records, list) else []):
            # Ticker alanı farklı isimlerle gelebilir
            ticker = clean(
                rec.get('Ticker') or rec.get('ticker') or
                rec.get('Symbol') or rec.get('symbol') or ''
            ).upper()
            if not ticker:
                continue
            # NAV
            nav = (rec.get('NAV') or rec.get('nav') or
                   rec.get('NetAssetValue') or rec.get('netAssetValue'))
            # Discount/Premium (- = discount, + = premium)
            discount = (rec.get('PremiumDiscount') or rec.get('premiumDiscount') or
                        rec.get('Discount') or rec.get('discount') or
                        rec.get('DiscountPremium') or rec.get('discountPremium'))
            fund_name = clean(
                rec.get('FundName') or rec.get('fundName') or
                rec.get('Name') or rec.get('name') or ''
            )
            nav_date = clean(
                rec.get('NAVDate') or rec.get('navDate') or
                rec.get('PriceDate') or rec.get('priceDate') or ''
            )
            if nav is not None or discount is not None:
                entry = {}
                if nav is not None:
                    try:
                        entry['nav'] = round(float(nav), 4)
                    except Exception:
                        pass
                if discount is not None:
                    try:
                        entry['discount'] = round(float(discount), 4)
                    except Exception:
                        pass
                if fund_name:
                    entry['fundName'] = fund_name
                if nav_date:
                    entry['navDate'] = nav_date
                out[ticker] = entry
        return out

    def _fetch_cef_nav_for_ticker(self, sym):
        """cefconnect.com fund sayfasını çekip NAV + Discount bilgilerini parse eder.
        HTML içindeki __NEXT_DATA__ JSON bloğunu kullanır — API endpoint tahmin etmeye gerek yok."""
        url = f"https://www.cefconnect.com/fund/{sym}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.cefconnect.com/',
        })
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read()
        if raw[:2] == b'\x1f\x8b':
            raw = gzip.decompress(raw)
        html = raw.decode('utf-8', 'ignore')

        result = {}

        # ── Yöntem 1: Next.js __NEXT_DATA__ bloğu ────────────────────────
        m = re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
                      html, re.DOTALL)
        if m:
            try:
                nd = json.loads(m.group(1))
                # Veri ağacını kökten tarayarak NAV ve PremiumDiscount bul
                def _dig(obj, depth=0):
                    if depth > 12 or not isinstance(obj, (dict, list)):
                        return
                    if isinstance(obj, list):
                        for item in obj:
                            _dig(item, depth + 1)
                        return
                    # dict
                    nav_val = (obj.get('NAV') or obj.get('nav') or
                               obj.get('NetAssetValue') or obj.get('netAssetValue'))
                    disc_val = (obj.get('PremiumDiscount') or obj.get('premiumDiscount') or
                                obj.get('Discount') or obj.get('discount') or
                                obj.get('DiscountPremium') or obj.get('discountPremium'))
                    name_val = (obj.get('FundName') or obj.get('fundName') or
                                obj.get('Name') or obj.get('name'))
                    nav_date_val = (obj.get('NAVDate') or obj.get('navDate') or
                                    obj.get('PriceDate') or obj.get('priceDate'))
                    if nav_val is not None and 'nav' not in result:
                        try:
                            result['nav'] = round(float(nav_val), 4)
                        except Exception:
                            pass
                    if disc_val is not None and 'discount' not in result:
                        try:
                            result['discount'] = round(float(disc_val), 4)
                        except Exception:
                            pass
                    if name_val and 'fundName' not in result:
                        n = clean(str(name_val))
                        if n:
                            result['fundName'] = n
                    if nav_date_val and 'navDate' not in result:
                        d = clean(str(nav_date_val))
                        if d:
                            result['navDate'] = d
                    for v in obj.values():
                        _dig(v, depth + 1)
                _dig(nd)
            except Exception:
                pass

        # ── Yöntem 2: HTML içi regex fallback ────────────────────────────
        if 'nav' not in result:
            # NAV: sayı değeri içeren data-label / aria veya metin paterni
            for pat in [
                r'NAV["\s]*[:\s]+\$?([\d]+\.[\d]{2,4})',
                r'"NAV"\s*:\s*([\d.]+)',
                r'nav["\s]*[:\s]+\$?([\d]+\.[\d]{2,4})',
            ]:
                mm = re.search(pat, html, re.IGNORECASE)
                if mm:
                    try:
                        result['nav'] = round(float(mm.group(1)), 4)
                        break
                    except Exception:
                        pass

        if 'discount' not in result:
            for pat in [
                r'Premium[/\s]*Discount["\s]*[:\s]+(-?[\d.]+)%?',
                r'"[Pp]remiumDiscount"\s*:\s*(-?[\d.]+)',
                r'"[Dd]iscount"\s*:\s*(-?[\d.]+)',
            ]:
                mm = re.search(pat, html, re.IGNORECASE)
                if mm:
                    try:
                        result['discount'] = round(float(mm.group(1)), 4)
                        break
                    except Exception:
                        pass

        return result  # {} ise veri bulunamadı

    def _nav_cache_period(self):
        """Yahoo ile aynı 15:00 TR reset mantığı — NAV cache periyodu."""
        return self._turkey_refresh_period()

    def _nav_needs_refresh(self, sym):
        """Bu ticker için NAV verisi bugünün periyoduna ait değilse True döner."""
        cache = _load('cef_nav_data.json')
        entry = cache.get(sym.upper(), {})
        return entry.get('period') != self._nav_cache_period()

    def _save_nav_cache(self, sym, nav_info):
        """nav_info = {nav, discount, fundName, navDate} — cache'e yazar."""
        cache = _load('cef_nav_data.json')
        cache[sym.upper()] = dict(nav_info, period=self._nav_cache_period(),
                                  fetchedAt=time.strftime('%Y-%m-%d %H:%M:%S'))
        _save('cef_nav_data.json', cache)

    def _get_nav_cache(self, sym):
        """Cache'den NAV verisini döner; yoksa {} döner."""
        cache = _load('cef_nav_data.json')
        entry = dict(cache.get(sym.upper(), {}))
        entry.pop('period', None)
        entry.pop('fetchedAt', None)
        return entry

    def _apply_cef_nav_data(self, nav_dict):
        """nav_dict: {TICKER: {nav, discount, fundName, navDate}} → self.cef'e yazar."""
        today_s = date.today().isoformat()
        for ticker, info in nav_dict.items():
            row = dict(self.cef.get(ticker, {'sectors': []}))
            row.update(info)
            row['navFetchDate'] = today_s
            self.cef[ticker] = row

    def _common_needs_warning(self, parent, common_row):
        if not parent or parent.upper() == 'PRIVATE':
            return True
        if not common_row:
            return True
        cap = self._market_cap_value(common_row.get('marketCap'))
        return cap is not None and cap < 1_000_000_000

    def _has_near_event(self, pref_sym, parent):
        return (self._event_is_today_or_tomorrow(self._earning_for_common(parent)) or
                self._event_is_today_or_tomorrow(self._dividend_for_pref(pref_sym)))

    def _reload(self):
        self.pref   = _load('pref_data.json')
        self.common = _load('common_data.json')
        self.ptoc   = _load('pref_to_common.json')
        self.cef    = self._normalize_cef_data(_load('cef_sector_data.json'))
        self.earnings = self._normalize_earnings_data(_load('earnings_data.json'))
        self.dividends = self._normalize_dividend_events(_load('dividend_events.json'))
        # filter noise
        for k in list(self.pref.keys()):
            if k.startswith('PRIVATE') or k.startswith('NO ') or k.startswith('No '):
                del self.pref[k]
        self._all_tickers = set(self.pref.keys()) | CEF_SET | set(self.cef.keys())

    # ── UI BUILD ─────────────────────────────────────
    def _build_ui(self):
        # ─── Header ─────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG2, height=34)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        self._dot = tk.Label(hdr, text='●', fg=TX5, bg=BG2, font=(FNU, 8))
        self._dot.pack(side='left', padx=(8,3), pady=5)

        tk.Label(hdr, text='HAMMER PRO', fg=TX4, bg=BG2,
                 font=(FNU, 8, 'bold')).pack(side='left')

        self._hdr_sym = tk.Label(hdr, text='', fg=BL, bg=BG2,
                                  font=(FN, 10, 'bold'))
        self._hdr_sym.pack(side='left', padx=(6,0))

        self._scan_lbl = tk.Label(hdr, text='', fg=TX5, bg=BG2, font=(FNU, 7))
        self._scan_lbl.pack(side='right', padx=8)

        toolbar = tk.Frame(self.root, bg=BG2, bd=0)
        toolbar.pack(fill='x')
        tk.Frame(toolbar, bg=BD, height=1).pack(fill='x')
        bar = tk.Frame(toolbar, bg=BG2)
        bar.pack(fill='x', padx=6, pady=4)

        cat_b = tk.Label(bar, text='Kategoriler ▾', fg=TX4, bg=BG2,
                         font=(FNU, 8), cursor='hand2', padx=6, pady=3)
        cat_b.pack(side='left')
        cat_b.bind('<Button-1>', lambda e: self._show_category_dropdown(cat_b))
        cat_b.bind('<Enter>', lambda e: cat_b.config(fg=BL, bg=ACC))
        cat_b.bind('<Leave>', lambda e: cat_b.config(fg=TX4, bg=BG2))

        self._cat_summary = tk.Label(bar, text='', fg=TX5, bg=BG2, font=(FNU, 7))
        self._cat_summary.pack(side='left', padx=(4,0))

        add_b = tk.Label(bar, text='＋', fg=TX4, bg=BG2,
                         font=(FNU, 10), cursor='hand2', padx=4)
        add_b.pack(side='right', padx=(4,0))
        add_b.bind('<Button-1>', lambda e: self._open_pref_form(None))
        add_b.bind('<Enter>', lambda e: add_b.config(fg=GR))
        add_b.bind('<Leave>', lambda e: add_b.config(fg=TX4))
        Tip(add_b, 'Yeni Preferred Ekle')

        com_b = tk.Label(bar, text='C＋', fg=TX4, bg=BG2,
                         font=(FNU, 9), cursor='hand2', padx=4)
        com_b.pack(side='right', padx=0)
        com_b.bind('<Button-1>', lambda e: self._quick_add_common())
        com_b.bind('<Enter>', lambda e: com_b.config(fg=AM))
        com_b.bind('<Leave>', lambda e: com_b.config(fg=TX4))
        Tip(com_b, "Common Ekle / Düzenle (mevcut prefin parenti)")

        earn_b = tk.Label(bar, text='E＋', fg=TX4, bg=BG2,
                          font=(FNU, 9), cursor='hand2', padx=4)
        earn_b.pack(side='right', padx=(0,2))
        earn_b.bind('<Button-1>', lambda e: self._open_earnings_form())
        earn_b.bind('<Enter>', lambda e: earn_b.config(fg=AM))
        earn_b.bind('<Leave>', lambda e: earn_b.config(fg=TX4))
        Tip(earn_b, "Yeni Earning Listesi Yükle")

        div_b = tk.Label(bar, text='D＋', fg=TX4, bg=BG2,
                         font=(FNU, 9), cursor='hand2', padx=4)
        div_b.pack(side='right', padx=(0,2))
        div_b.bind('<Button-1>', lambda e: self._open_dividends_form())
        div_b.bind('<Enter>', lambda e: div_b.config(fg=AM))
        div_b.bind('<Leave>', lambda e: div_b.config(fg=TX4))
        Tip(div_b, "Yeni Dividend Listesi Yükle")

        cef_b = tk.Label(bar, text='CEF＋', fg=TX4, bg=BG2,
                         font=(FNU, 8), cursor='hand2', padx=4)
        cef_b.pack(side='right', padx=(0,2))
        cef_b.bind('<Button-1>', lambda e: self._quick_add_cef())
        cef_b.bind('<Enter>', lambda e: cef_b.config(fg=AM))
        cef_b.bind('<Leave>', lambda e: cef_b.config(fg=TX4))
        Tip(cef_b, "CEF Ekle / Düzenle")

        take_b = tk.Label(bar, text='⟳', fg=BL, bg=BG2,
                          font=(FNU, 8, 'bold'), cursor='hand2',
                          padx=7, pady=3,
                          highlightthickness=1, highlightbackground=BD)
        take_b.pack(side='right', padx=(0,6))
        take_b.bind('<Button-1>', lambda e: self._take_data())
        take_b.bind('<Enter>', lambda e: take_b.config(bg=ACC))
        take_b.bind('<Leave>', lambda e: take_b.config(bg=BG2))
        Tip(take_b, "Yahoo Finance fiyat ve market cap güncelle")

        # ─── Search ──────────────────────────────────
        sf = tk.Frame(self.root, bg=BG, pady=4, padx=6)
        sf.pack(fill='x')

        self._sv = tk.StringVar()
        self._sv.trace_add('write', self._on_search_change)
        self._entry = tk.Entry(sf, textvariable=self._sv, bg=BG2, fg=TX,
                               insertbackground=BL, font=(FN, 10),
                               relief='flat', bd=0,
                               highlightthickness=1,
                               highlightbackground=BD,
                               highlightcolor=BL2)
        self._entry.pack(fill='x', ipady=5, padx=2)
        self._entry.bind('<Return>', lambda e: self._search_commit())
        self._entry.bind('<Escape>', lambda e: self._hide_ac())
        self._entry.bind('<Down>', self._ac_down)
        self._entry.bind('<Up>', self._ac_up)

        # Autocomplete listbox
        self._ac_frame = tk.Frame(self.root, bg=BD, bd=1, relief='flat')
        self._ac_list = tk.Listbox(self._ac_frame, bg=BG2, fg=TX2,
                                    selectbackground=ACC, selectforeground=BL,
                                    font=(FN, 9), relief='flat', bd=0,
                                    highlightthickness=0,
                                    activestyle='none', height=7)
        self._ac_list.pack(fill='both', expand=True, padx=1, pady=1)
        self._ac_list.bind('<<ListboxSelect>>', self._ac_select)
        self._ac_list.bind('<Return>', self._ac_select)

        # ─── Content (scrollable) ─────────────────────
        self._scroll = ScrollFrame(self.root)
        self._scroll.pack(fill='both', expand=True, padx=0)
        self._inner = self._scroll.inner  # convenience

    def _build_categories(self):
        cats = {'low': [], 'mid': [], 'high': [], 'float': [], 'other': []}
        for sym, p in self.pref.items():
            if is_floating(p):
                cats['float'].append((sym, p))
            else:
                cv = parse_coupon(p.get('coupon'))
                if cv is None:
                    cats['other'].append((sym, p))
                elif cv < 5.5:    cats['low'].append((sym, p))
                elif cv <= 7.0:   cats['mid'].append((sym, p))
                else:             cats['high'].append((sym, p))

        # sort alphabetically
        for key in cats:
            cats[key].sort(key=lambda x: x[0])

        self._cats = cats
        if hasattr(self, '_cat_summary'):
            self._cat_summary.config(text=f"{sum(len(v) for v in cats.values())} pref")

    # ── SEARCH ───────────────────────────────────────
    def _on_search_change(self, *_):
        q = self._sv.get().upper().strip()
        if not q:
            self._hide_ac()
            return
        matches = sorted([t for t in self._all_tickers
                          if t.startswith(q) or (len(q) >= 2 and q in t)])[:10]
        self._ac_items = matches
        self._ac_list.delete(0, 'end')
        for m in matches:
            label = m
            if m in self.pref:
                label += f"  {self.pref[m].get('fixFloat','')[:8]}"
            elif m in CEF_SET or m in self.cef:
                label += "  CEF"
            self._ac_list.insert('end', label)
        if matches:
            # position dropdown
            x = self._entry.winfo_rootx() - self.root.winfo_rootx()
            y = self._entry.winfo_rooty() - self.root.winfo_rooty() + self._entry.winfo_height() + 6
            self._ac_frame.place(x=x, y=y, width=self._entry.winfo_width())
            self._ac_frame.lift()
        else:
            self._hide_ac()

    def _ac_down(self, e):
        if self._ac_items:
            cur = self._ac_list.curselection()
            nxt = 0 if not cur else min(cur[0]+1, len(self._ac_items)-1)
            self._ac_list.selection_clear(0,'end')
            self._ac_list.selection_set(nxt)
            self._ac_list.see(nxt)

    def _ac_up(self, e):
        if self._ac_items:
            cur = self._ac_list.curselection()
            prv = len(self._ac_items)-1 if not cur else max(cur[0]-1, 0)
            self._ac_list.selection_clear(0,'end')
            self._ac_list.selection_set(prv)
            self._ac_list.see(prv)

    def _ac_select(self, e=None):
        sel = self._ac_list.curselection()
        if sel and self._ac_items:
            self.select(self._ac_items[sel[0]])

    def _search_commit(self):
        q = self._sv.get().upper().strip()
        sel = self._ac_list.curselection()
        if sel and self._ac_items:
            self.select(self._ac_items[sel[0]])
        elif q:
            self.select(q)

    def _hide_ac(self):
        self._ac_frame.place_forget()
        self._ac_items = []

    # ── SELECT / RENDER ───────────────────────────────
    def select(self, sym):
        sym = sym.upper().strip()
        if not sym: return
        self.current = sym
        self._sv.set(sym)
        self._hdr_sym.config(text=f'— {sym}')
        self._hide_ac()

        self._scroll.clear()

        if sym in self.pref:
            self._render_pref(sym)
        elif sym in CEF_SET or sym in self.cef:
            self._render_cef(sym)
        else:
            self._render_notfound(sym)

    def _show_empty(self):
        self.current = None
        self._hdr_sym.config(text='')
        self._scroll.clear()
        f = self._inner
        tk.Label(f, text='⬡', fg=TX5, bg=BG, font=(FN, 24)).pack(pady=(50, 8))
        tk.Label(f, text='Ticker seçin veya arayın', fg=TX5, bg=BG,
                 font=(FNU, 9)).pack()
        if not HAS_WIN32:
            tk.Label(f, text='(pip install pywin32  →  otomatik tespit)',
                     fg=TX5, bg=BG, font=(FNU, 7)).pack(pady=4)

    def _show_startup_loading(self):
        self.current = None
        self._hdr_sym.config(text='— DATA')
        self._scroll.clear()
        f = self._inner
        tk.Label(f, text='DATA ÇEKİLİYOR', fg=BL, bg=BG,
                 font=(FNU, 10, 'bold')).pack(pady=(50, 8))
        self._startup_status = tk.Label(f, text='Hazırlanıyor...', fg=TX3, bg=BG,
                                        font=(FNU, 8))
        self._startup_status.pack(pady=(0,8))
        self._startup_bar = tk.Canvas(f, bg=BG2, highlightthickness=1,
                                      highlightbackground=BD, height=12)
        self._startup_bar.pack(fill='x', padx=28, pady=4)
        self._startup_bar_fill = self._startup_bar.create_rectangle(
            0, 0, 0, 12, fill=BL2, width=0)

    def _update_startup_loading(self, done, total, text):
        if self._startup_status:
            self._startup_status.config(text=f"{done}/{total}  {text}")
        if self._startup_bar:
            w = max(self._startup_bar.winfo_width(), 1)
            pct = 0 if not total else min(1, done / total)
            self._startup_bar.coords(self._startup_bar_fill, 0, 0, int(w * pct), 12)

    def _needs_startup_refresh(self):
        meta = _load('data_fetch_meta.json')
        return meta.get('lastFullRefreshPeriod') != self._turkey_refresh_period()

    def _turkey_refresh_period(self):
        try:
            from zoneinfo import ZoneInfo
            now_tr = datetime.now(ZoneInfo('Europe/Istanbul'))
        except Exception:
            now_tr = datetime.utcnow() + timedelta(hours=3)
        period_day = now_tr.date()
        if now_tr.hour < 15:
            period_day = period_day - timedelta(days=1)
        return period_day.isoformat()

    def _start_scanner_if_available(self):
        if HAS_WIN32:
            self._start_scanner()
        else:
            self._set_scan_status('pywin32 yok', TX3)

    def _start_startup_refresh(self):
        threading.Thread(target=self._startup_refresh_worker, daemon=True).start()

    def _startup_refresh_worker(self):
        pref_syms = sorted(self.pref.keys())
        cef_syms = sorted(set(CEF_SET) | set(self.cef.keys()))
        common_syms = sorted({clean(v).upper() for v in self.ptoc.values()
                              if clean(v) and clean(v).upper() != 'PRIVATE'})
        tasks = [('pref', s) for s in pref_syms]
        tasks += [('cef', s) for s in cef_syms]
        tasks += [('common', s) for s in common_syms]
        total = len(tasks)
        done = 0

        for kind, sym in tasks:
            try:
                if kind == 'pref':
                    yahoo_sym, price = self._fetch_yahoo_price(sym, preferred=True)
                    self._apply_pref_market_data(sym, price, yahoo_sym)
                elif kind == 'cef':
                    yahoo_sym, price = self._fetch_yahoo_price(sym, preferred=False)
                    self._apply_cef_market_data(sym, price, yahoo_sym)
                else:
                    yahoo_sym, market_cap = self._fetch_yahoo_market_cap(sym)
                    c = dict(self.common.get(sym, {}))
                    c['marketCap'] = market_cap
                    c['marketCapUpdated'] = date.today().isoformat()
                    c['marketCapYahooSymbol'] = yahoo_sym
                    self.common[sym] = c
            except Exception:
                pass
            done += 1
            if done % 5 == 0 or done == total:
                self.root.after(0, self._update_startup_loading, done, total, sym)

        _save('pref_data.json', self.pref)
        _save('cef_sector_data.json', self.cef)
        _save('common_data.json', self.common)
        _save('data_fetch_meta.json', {
            'lastFullRefresh': date.today().isoformat(),
            'lastFullRefreshPeriod': self._turkey_refresh_period(),
            'resetTimezone': 'Europe/Istanbul',
            'resetHour': 15,
            'updatedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        self.root.after(0, self._finish_startup_refresh)

    def _finish_startup_refresh(self):
        self._reload()
        self._build_categories()
        self._show_empty()
        self._start_scanner_if_available()

    # ─── PREFERRED VIEW ──────────────────────────────
    def _render_pref(self, sym):
        p = self.pref[sym]
        parent = self.ptoc.get(sym)
        c = self.common.get(parent) if parent else None
        f = self._inner

        # ── Common card ──────────────────────────────
        self._draw_common_card(f, parent or 'PRIVATE', c, sym)

        # ── Preferred card ───────────────────────────
        pref_border = RD if self._has_near_event(sym, parent) else BL2
        card = tk.Frame(f, bg=BG2, bd=1, relief='flat',
                        highlightthickness=1, highlightbackground=pref_border)
        card.pack(fill='x', padx=6, pady=(0, 6))

        # Card header
        ch = tk.Frame(card, bg=BG3)
        ch.pack(fill='x')
        tk.Label(ch, text=sym, fg=TX, bg=BG3,
                 font=(FN, 13, 'bold')).pack(side='left', padx=8, pady=6)

        ft = clean(p.get('fixFloat'))
        if ft:
            tc = type_col(ft)
            badge = tk.Label(ch, text=f' {ft.upper()} ',
                             fg=tc, bg=BG, font=(FNU, 7, 'bold'),
                             padx=2, pady=1, relief='flat')
            badge.pack(side='left', padx=2, pady=6)

        # coupon + div right side
        cr = tk.Frame(ch, bg=BG3)
        cr.pack(side='right', padx=8, pady=4)
        coupon = clean(p.get('coupon')) or '—'
        last_price = p.get('lastPrice')
        current_yield = p.get('currentYield')
        if current_yield is None and last_price is not None and p.get('div') is not None:
            try:
                current_yield = (float(p.get('div')) * 4 / float(last_price)) * 100
            except Exception:
                current_yield = None
        coupon_txt = coupon
        cy_txt = fmt_pct(current_yield)
        if cy_txt:
            coupon_txt = f"{coupon} / {cy_txt}"
        coupon_font = 10 if cy_txt else 12
        coupon_line = tk.Frame(cr, bg=BG3)
        coupon_line.pack(anchor='e')
        tk.Label(coupon_line, text=coupon_txt, fg=BL, bg=BG3,
                 font=(FN, coupon_font, 'bold')).pack(side='left')
        self._draw_take_mark(coupon_line, f'pref:{sym}:price', BG3)
        dv = fmt_div(p.get('div'))
        price_txt = fmt_price(last_price)
        info_txt = dv or 'Div: —'
        if price_txt:
            info_txt = f"Price {price_txt} | {info_txt}"
        tk.Label(cr, text=info_txt, fg=TX4, bg=BG3,
                 font=(FN, 8)).pack(anchor='e')

        earning = self._earning_for_common(parent)
        dividend_event = self._dividend_for_pref(sym)
        if earning or dividend_event:
            evf = tk.Frame(card, bg=BG2)
            evf.pack(fill='x', padx=6, pady=(6,2))
            if earning:
                past = self._earning_is_past(earning)
                earn_bg = '#2a0f0f' if past else '#2a1f0b'
                earn_fg = RD if past else AM
                ef = tk.Frame(evf, bg=earn_bg, padx=6, pady=5,
                              highlightthickness=1,
                              highlightbackground=RD if past else AM)
                ef.pack(side='left', fill='x', expand=True, padx=(0,3))
                tk.Label(ef, text=self._earning_text(earning), fg=earn_fg, bg=earn_bg,
                         font=(FNU, 8, 'bold'), wraplength=130,
                         justify='left').pack(anchor='w')
            if dividend_event:
                past = self._earning_is_past(dividend_event)
                div_bg = '#2a0f0f' if past else '#2a1f0b'
                div_fg = RD if past else AM
                dfv = tk.Frame(evf, bg=div_bg, padx=6, pady=5,
                               highlightthickness=1,
                               highlightbackground=RD if past else AM)
                dfv.pack(side='left', fill='x', expand=True, padx=(3,0))
                tk.Label(dfv, text=self._dividend_text(dividend_event), fg=div_fg, bg=div_bg,
                         font=(FNU, 8, 'bold'), wraplength=130,
                         justify='left').pack(anchor='w')

        # Grid: 3 cells
        grid = tk.Frame(card, bg=BG2)
        grid.pack(fill='x', padx=6, pady=4)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(2, weight=1)

        cells = [
            ('>4M', clean(p.get('mn4')) or '—', mn4_col(p.get('mn4'))),
            ('Rating', clean(p.get('rating')) or '—', rating_col(p.get('rating'))),
            ('Tip', (clean(p.get('fixFloat')) or '—')[:10], type_col(p.get('fixFloat'))),
        ]
        for i, (lbl, val, col) in enumerate(cells):
            cell = tk.Frame(grid, bg=BG, padx=4, pady=4)
            cell.grid(row=0, column=i, sticky='nsew', padx=3, pady=3)
            tk.Label(cell, text=lbl.upper(), fg=TX5, bg=BG,
                     font=(FNU, 7)).pack(anchor='w')
            tk.Label(cell, text=val, fg=col, bg=BG,
                     font=(FN, 10, 'bold')).pack(anchor='w')

        ytc_v, ytm_v = p.get('ytc'), p.get('ytm')
        if p.get('lastPrice') is not None:
            calc_ytc, calc_ytm = self._calc_pref_yields(p)
            ytc_v = calc_ytc if calc_ytc is not None else ytc_v
            ytm_v = calc_ytm if calc_ytm is not None else ytm_v
        ytc = fmt_pct(ytc_v)
        ytm = fmt_pct(ytm_v)
        if ytc or ytm:
            yrow = tk.Frame(card, bg=BG2)
            yrow.pack(fill='x', padx=6, pady=(0,4))
            for lbl, val, col in [('YTC', ytc or '—', AM), ('YTM', ytm or '—', TE)]:
                cell = tk.Frame(yrow, bg=BG, padx=5, pady=4)
                cell.pack(side='left', fill='x', expand=True, padx=3)
                tk.Label(cell, text=lbl, fg=TX5, bg=BG, font=(FNU, 7)).pack(anchor='w')
                tk.Label(cell, text=val, fg=col, bg=BG,
                         font=(FN, 9, 'bold')).pack(anchor='w')

        # Dates
        call = clean(p.get('callDate'))
        mature = clean(p.get('matureDate'))
        if call or mature:
            df = tk.Frame(card, bg=BG, padx=6, pady=4)
            df.pack(fill='x', padx=6, pady=(0,4))
            if call and call.lower() not in ('none',''):
                dc = tk.Frame(df, bg=BG)
                dc.pack(side='left', padx=(0,16))
                tk.Label(dc, text='CALL', fg=TX5, bg=BG, font=(FNU, 7)).pack(anchor='w')
                tk.Label(dc, text=call, fg=AM, bg=BG, font=(FN, 9, 'bold')).pack(anchor='w')
            if mature and mature.lower() not in ('none',''):
                dm = tk.Frame(df, bg=BG)
                dm.pack(side='left')
                tk.Label(dm, text='MATURE', fg=TX5, bg=BG, font=(FNU, 7)).pack(anchor='w')
                tk.Label(dm, text=mature, fg=TX3, bg=BG, font=(FN, 9)).pack(anchor='w')

        # Actions
        af = tk.Frame(card, bg=BG2)
        af.pack(fill='x', padx=6, pady=(2,6))
        self._btn(af, '✏ Düzenle', BL, lambda: self._open_pref_form(sym)).pack(
            side='left', padx=(0,4))
        self._btn(af, '🗑 Sil', RD, lambda: self._confirm_delete(sym)).pack(side='left')

    def _draw_common_card(self, parent_frame, sym, c, pref_sym):
        expanded = self._common_expanded.get(sym, False)
        border = RD if self._common_needs_warning(sym, c) else BD
        card = tk.Frame(parent_frame, bg=BG2, bd=1, relief='flat',
                        highlightthickness=1, highlightbackground=border)
        card.pack(fill='x', padx=6, pady=(6,4))

        # Header
        def toggle():
            self._common_expanded[sym] = not self._common_expanded.get(sym, False)
            self._scroll.clear()
            self._render_pref(pref_sym)

        hf = tk.Frame(card, bg=BG3, cursor='hand2')
        hf.pack(fill='x')
        hf.bind('<Button-1>', lambda e: toggle())

        lf = tk.Frame(hf, bg=BG3)
        lf.pack(side='left', padx=6, pady=5)
        lf.bind('<Button-1>', lambda e: toggle())
        common_lbl = tk.Label(lf, text='▲ COMMON', fg=TX5, bg=BG3, font=(FNU, 7))
        common_lbl.pack(side='left')
        common_lbl.bind('<Button-1>', lambda e: toggle())
        sym_lbl = tk.Label(lf, text=f'  {sym}', fg=TX2, bg=BG3,
                           font=(FN, 10, 'bold'))
        sym_lbl.pack(side='left')
        sym_lbl.bind('<Button-1>', lambda e: toggle())

        arr = '▲' if expanded else '▼'
        arrlbl = tk.Label(hf, text=arr, fg=TX5, bg=BG3, font=(FNU, 8), cursor='hand2')
        arrlbl.pack(side='right', padx=8)
        arrlbl.bind('<Button-1>', lambda e: toggle())

        # Top row: sector + marketcap
        if c:
            tf = tk.Frame(card, bg=BG2)
            tf.pack(fill='x', padx=8, pady=(4,2))
            sector = clean(c.get('sector')) or '—'
            mktcap = clean(c.get('marketCap')) or '—'
            tk.Label(tf, text=sector, fg=TX3, bg=BG2, font=(FNU, 8)).pack(side='left')
            capf = tk.Frame(tf, bg=BG2)
            capf.pack(side='right')
            self._draw_take_mark(capf, f'common:{sym}:marketCap', BG2)
            tk.Label(capf, text=mktcap, fg=TX, bg=BG2,
                     font=(FN, 10, 'bold')).pack(side='right')

        # Expanded section
        if expanded and c:
            xf = tk.Frame(card, bg=BG2)
            xf.pack(fill='x', padx=6, pady=(2,4))

            fields = [
                ('Altman Z', clean(c.get('altman'))),
                ('Current Ratio', clean(c.get('currentRatio'))),
                ('D/E', clean(c.get('de'))),
                ('ROIC/WACC', clean(c.get('roicWacc'))),
            ]
            for lbl, val in fields:
                if val and val not in ('N/A',''):
                    rf = tk.Frame(xf, bg=BG2)
                    rf.pack(fill='x', pady=1)
                    tk.Label(rf, text=lbl, fg=TX5, bg=BG2, font=(FNU, 7),
                             width=12, anchor='w').pack(side='left')
                    tk.Label(rf, text=val, fg=TX2, bg=BG2,
                             font=(FN, 8)).pack(side='right')

            comment = clean(c.get('comment'))
            if comment:
                cf = tk.Frame(xf, bg=BG, padx=5, pady=5)
                cf.pack(fill='x', pady=(4,0))
                tk.Frame(cf, bg=ACC, width=2).pack(side='left', fill='y')
                inner_cf = tk.Frame(cf, bg=BG, padx=5)
                inner_cf.pack(side='left', fill='both')
                tk.Label(inner_cf, text='YORUM', fg=TX5, bg=BG,
                         font=(FNU, 7)).pack(anchor='w')
                tk.Label(inner_cf, text=comment, fg=TX3, bg=BG,
                         font=(FNU, 8), wraplength=240, justify='left').pack(anchor='w')

            self._btn(xf, '✏ Common Düzenle', TX3,
                      lambda s=sym: self._open_common_form(s)).pack(pady=(4,0))
        elif expanded and not c:
            self._btn(card, '＋ Common Bilgisi Ekle', TX3,
                      lambda s=sym: self._open_common_form(s)).pack(padx=8, pady=4)

    # ─── CEF VIEW ────────────────────────────────────
    def _render_cef(self, sym):
        f = self._inner
        url = f"https://www.cefconnect.com/fund/{sym}"
        sectors = self._cef_sectors(sym)
        cef_row = self.cef.get(sym, {})

        # NAV cache'den oku
        nav_info = self._get_nav_cache(sym)
        needs_nav = self._nav_needs_refresh(sym)

        tk.Label(f, text='⬡ CEF', fg=TX5, bg=BG, font=(FNU, 8)).pack(pady=(16,2))

        fund_name = clean(nav_info.get('fundName') or cef_row.get('fundName') or '')
        tk.Label(f, text=sym, fg=TX, bg=BG, font=(FN, 20, 'bold')).pack()
        if fund_name:
            tk.Label(f, text=fund_name, fg=TX3, bg=BG,
                     font=(FNU, 8), wraplength=280, justify='center').pack(pady=(0,2))

        # ── Yahoo fiyatı ─────────────────────────────
        price = cef_row.get('lastPrice')
        price_str = fmt_price(price)
        if price_str:
            tk.Label(f, text=f"Fiyat  {price_str}", fg=BL, bg=BG,
                     font=(FN, 11, 'bold')).pack(pady=(2,4))

        # ── NAV + Discount kartı ─────────────────────
        nav_card = tk.Frame(f, bg=BG2, bd=0,
                            highlightthickness=1,
                            highlightbackground=PU if nav_info else TX5)
        nav_card.pack(fill='x', padx=12, pady=(4,6))

        hdr_f = tk.Frame(nav_card, bg=BG3)
        hdr_f.pack(fill='x')
        tk.Label(hdr_f, text='CEF CONNECT  —  NAV & DİSKONTO',
                 fg=PU, bg=BG3, font=(FNU, 7, 'bold'),
                 padx=8, pady=4).pack(side='left')

        nav_date_s = clean(nav_info.get('navDate') or '')
        if nav_date_s:
            tk.Label(hdr_f, text=nav_date_s, fg=TX5, bg=BG3,
                     font=(FNU, 7), padx=6).pack(side='right')

        # Status label (güncellenir)
        status_lbl = tk.Label(nav_card, text='', fg=TX5, bg=BG2, font=(FNU, 7))
        status_lbl.pack(anchor='w', padx=8)

        cells_f = tk.Frame(nav_card, bg=BG2)
        cells_f.pack(fill='x', padx=6, pady=(4,6))

        def _nd_cell(parent, label, value, color):
            cell = tk.Frame(parent, bg=BG, padx=6, pady=5)
            cell.pack(side='left', fill='x', expand=True, padx=3)
            tk.Label(cell, text=label, fg=TX5, bg=BG, font=(FNU, 7)).pack(anchor='w')
            tk.Label(cell, text=value, fg=color, bg=BG,
                     font=(FN, 11, 'bold')).pack(anchor='w')

        def _draw_nav_cells(info):
            """Hücreleri çiz / yenile."""
            for w in cells_f.winfo_children():
                w.destroy()

            nav = info.get('nav')
            discount = info.get('discount')

            if nav is None and discount is None:
                tk.Label(cells_f, text='Veri alınamadı', fg=TX4, bg=BG2,
                         font=(FNU, 8), padx=8, pady=6).pack(side='left')
                return

            if nav is not None:
                try:
                    nav_val = f"${float(nav):.2f}"
                    nav_col = (GR if price is not None and float(nav) > float(price)
                               else AM)
                except Exception:
                    nav_val = str(nav)
                    nav_col = TE
                _nd_cell(cells_f, 'NAV', nav_val, nav_col)

            if discount is not None:
                try:
                    disc_f_val = float(discount)
                    disc_str = f"{disc_f_val:+.2f}%"
                    disc_col = (GR if disc_f_val < -0.5
                                else RD if disc_f_val > 0.5
                                else AM)
                    disc_label = 'DİSKONTO' if disc_f_val < 0 else 'PREMİUM'
                except Exception:
                    disc_str = str(discount)
                    disc_col = TX2
                    disc_label = 'DİSK/PREM'
                _nd_cell(cells_f, disc_label, disc_str, disc_col)

            # Görsel bar
            if discount is not None:
                try:
                    disc_pct = max(-30.0, min(30.0, float(discount)))
                    bar_wrap = tk.Frame(nav_card, bg=BG2)
                    bar_wrap.pack(fill='x', padx=10, pady=(0, 2))
                    bar_c = tk.Canvas(bar_wrap, bg=BG, highlightthickness=0,
                                      height=6, width=260)
                    bar_c.pack()

                    def _draw_bar(c=bar_c, pct=disc_pct):
                        w = c.winfo_reqwidth()
                        mid = w // 2
                        fill_w = int(abs(pct) / 30 * mid)
                        c.delete('all')
                        c.create_rectangle(0, 0, w, 6, fill=BG3, width=0)
                        c.create_rectangle(mid - 1, 0, mid + 1, 6, fill=TX5, width=0)
                        if pct < 0:
                            x1, x2, col = mid - fill_w, mid, GR
                        else:
                            x1, x2, col = mid, mid + fill_w, RD
                        if fill_w > 0:
                            c.create_rectangle(x1, 1, x2, 5, fill=col, width=0)

                    bar_c.after(10, _draw_bar)

                    lbl_wrap = tk.Frame(nav_card, bg=BG2)
                    lbl_wrap.pack(fill='x', padx=10, pady=(0, 6))
                    tk.Label(lbl_wrap, text='−30%  DİSK', fg=GR, bg=BG2,
                             font=(FNU, 6)).pack(side='left')
                    tk.Label(lbl_wrap, text='PREM  +30%', fg=RD, bg=BG2,
                             font=(FNU, 6)).pack(side='right')
                    tk.Label(lbl_wrap, text='0', fg=TX5, bg=BG2,
                             font=(FNU, 6)).pack()
                except Exception:
                    pass

        # Mevcut cache varsa hemen çiz
        if nav_info:
            _draw_nav_cells(nav_info)
        else:
            status_lbl.config(text='⟳  NAV çekiliyor…', fg=AM)

        # Eğer güncelleme gerekiyorsa arka planda çek
        if needs_nav:
            def _fetch_worker(s=sym):
                try:
                    info = self._fetch_cef_nav_for_ticker(s)
                    if info:
                        self._save_nav_cache(s, info)
                except Exception:
                    info = {}
                self.root.after(0, lambda: _on_nav_done(s, info))

            def _on_nav_done(s, info):
                if self.current != s:
                    return
                status_lbl.config(text='')
                if info:
                    nav_card.config(highlightbackground=PU)
                    _draw_nav_cells(info)
                else:
                    status_lbl.config(text='Veri alınamadı', fg=TX4)

            threading.Thread(target=_fetch_worker, daemon=True).start()

        # ── Sektör kartı ─────────────────────────────
        if sectors:
            sc = tk.Frame(f, bg=BG2, bd=0,
                          highlightthickness=1, highlightbackground=BL2)
            sc.pack(fill='x', padx=12, pady=(0,6))
            tk.Label(sc, text='ENDEKS / SEKTÖR', fg=AM, bg=BG2,
                     font=(FNU, 7, 'bold')).pack(anchor='w', padx=8, pady=(6,0))
            tk.Label(sc, text=', '.join(sectors), fg=TX, bg=BG2,
                     font=(FNU, 10, 'bold'), wraplength=270,
                     justify='left').pack(anchor='w', padx=8, pady=(1,7))
        else:
            tk.Label(f, text='Kapalı Uçlu Fon', fg=TX3, bg=BG,
                     font=(FNU, 8)).pack(pady=(2,4))

        # ── Fiyat tarihi ─────────────────────────────
        price_date = clean(cef_row.get('lastPriceDate'))
        if price_date:
            tk.Label(f, text=f"Yahoo fiyat: {price_date}", fg=TX5, bg=BG,
                     font=(FNU, 7)).pack(pady=(0,4))

        # ── Butonlar ─────────────────────────────────
        url_lbl = tk.Label(f, text=url, fg=TX5, bg=BG, font=(FN, 7))
        url_lbl.pack()

        tk.Button(f, text='🔗  CEF Connect\'te Aç',
                  command=lambda: webbrowser.open(url),
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 10, 'bold'), relief='flat', bd=0,
                  padx=16, pady=8, cursor='hand2').pack(pady=10)
        self._btn(f, '✏ Endeks Düzenle', AM,
                  lambda: self._open_cef_form(sym)).pack(pady=(0,8))

    def _render_notfound(self, sym):
        f = self._inner
        tk.Label(f, text='⬡', fg=TX5, bg=BG, font=(FN, 24)).pack(pady=(40,8))
        tk.Label(f, text=f'{sym} — Listede Bulunamadı', fg=TX4, bg=BG,
                 font=(FNU, 9)).pack()
        tk.Label(f, text='Preferred eklemek için ＋ butonunu kullanın',
                 fg=TX5, bg=BG, font=(FNU, 7)).pack(pady=4)

    # ─── CATEGORY POPUP ──────────────────────────────
    def _show_category_dropdown(self, widget):
        labels = {'low':'Kupon < 5.5%', 'mid':'Kupon 5.5% – 7%',
                  'high':'Kupon 7%+', 'float':'Floating', 'other':'Diğer'}
        order = ['low', 'mid', 'high', 'float', 'other']
        menu = tk.Menu(self.root, tearoff=0, bg=BG2, fg=TX,
                       activebackground=ACC, activeforeground=BL,
                       bd=0, relief='flat')
        for key in order:
            count = len(self._cats.get(key, []))
            menu.add_command(label=f"{labels[key]} ({count})",
                             command=lambda k=key: self._show_cat(k))
        try:
            menu.tk_popup(widget.winfo_rootx(),
                          widget.winfo_rooty() + widget.winfo_height())
        finally:
            menu.grab_release()

    def _show_cat(self, key):
        all_items = self._cats.get(key, [])
        labels = {'low':'Kupon < 5.5%', 'mid':'Kupon 5.5% – 7%',
                  'high':'Kupon 7%+', 'float':'Floating', 'other':'Diğer'}

        popup = tk.Toplevel(self.root)
        popup.title(labels.get(key, key))
        popup.geometry('290x480')
        popup.configure(bg=BG)
        popup.transient(self.root)

        # Header row
        hf = tk.Frame(popup, bg=BG2)
        hf.pack(fill='x')
        tk.Label(hf, text=labels.get(key, key).upper(),
                 fg=BL, bg=BG2, font=(FNU, 9, 'bold'),
                 padx=8, pady=6).pack(side='left')

        # Copy All button in header
        copy_lbl = tk.Label(hf, text='⎘ Tümünü Kopyala', fg=TX5, bg=BG2,
                            font=(FNU, 7), cursor='hand2', padx=6)
        copy_lbl.pack(side='right', pady=4)

        tk.Frame(popup, bg=BD, height=1).pack(fill='x')

        # Search
        sv = tk.StringVar()
        e = tk.Entry(popup, textvariable=sv, bg=BG2, fg=TX,
                     insertbackground=BL, font=(FN, 9),
                     relief='flat', bd=0, highlightthickness=1,
                     highlightbackground=BD, highlightcolor=BL2)
        e.pack(fill='x', padx=4, pady=4, ipady=4)

        frame = tk.Frame(popup, bg=BG)
        frame.pack(fill='both', expand=True)

        sb = tk.Scrollbar(frame, bg=BG2, troughcolor=BG, width=5)
        lb = tk.Listbox(frame, bg=BG, fg=TX2, selectbackground=ACC,
                        selectforeground=BL, font=(FN, 9),
                        relief='flat', bd=0, highlightthickness=0,
                        activestyle='none', yscrollcommand=sb.set,
                        selectmode='extended')
        sb.config(command=lb.yview)
        sb.pack(side='right', fill='y')
        lb.pack(side='left', fill='both', expand=True)

        # Status bar
        status_var = tk.StringVar(value='Çift tıkla: aç  |  Ctrl+C: kopyala')
        tk.Label(popup, textvariable=status_var, fg=TX5, bg=BG2,
                 font=(FNU, 7), pady=2).pack(fill='x', side='bottom')

        visible_items = []

        def fill_list(filter_q=''):
            nonlocal visible_items
            lb.delete(0, 'end')
            fq = filter_q.upper().strip()
            visible_items = []
            for sym, p in all_items:
                if fq and fq not in sym:
                    continue
                cp = clean(p.get('coupon')) or '—'
                rt = clean(p.get('rating')) or ''
                mn = clean(p.get('mn4')) or ''
                lb.insert('end', f'  {sym:<12} {cp:<8} {rt:<5} {mn}')
                visible_items.append((sym, p))
            status_var.set(f'{len(visible_items)} kayıt  |  Çift tıkla: aç  |  Ctrl+C: kopyala')

        fill_list()
        sv.trace_add('write', lambda *_: fill_list(sv.get()))

        def on_select(e):
            sel = lb.curselection()
            if sel:
                raw = lb.get(sel[0]).strip().split()[0]
                popup.destroy()
                self.select(raw)

        def copy_selected(e=None):
            sel = lb.curselection()
            if not sel:
                # No selection → copy all visible
                lines = [lb.get(i) for i in range(lb.size())]
            else:
                lines = [lb.get(i) for i in sel]
            text = '\n'.join(l.strip() for l in lines)
            popup.clipboard_clear()
            popup.clipboard_append(text)
            status_var.set(f'✓ {len(lines)} satır kopyalandı!')
            popup.after(1500, lambda: status_var.set(
                f'{len(visible_items)} kayıt  |  Çift tıkla: aç  |  Ctrl+C: kopyala'))

        def copy_all_symbols():
            """Copy only ticker symbols, one per line."""
            syms = [sym for sym,_ in visible_items]
            text = '\n'.join(syms)
            popup.clipboard_clear()
            popup.clipboard_append(text)
            status_var.set(f'✓ {len(syms)} ticker kopyalandı!')
            popup.after(1500, lambda: status_var.set(
                f'{len(visible_items)} kayıt  |  Çift tıkla: aç  |  Ctrl+C: kopyala'))
            copy_lbl.config(fg=GR)
            popup.after(1500, lambda: copy_lbl.config(fg=TX5))

        lb.bind('<Double-Button-1>', on_select)
        lb.bind('<Return>', on_select)
        lb.bind('<Control-c>', copy_selected)
        lb.bind('<Control-C>', copy_selected)
        copy_lbl.bind('<Button-1>', lambda e: copy_all_symbols())
        copy_lbl.bind('<Enter>', lambda e: copy_lbl.config(fg=BL))
        copy_lbl.bind('<Leave>', lambda e: copy_lbl.config(fg=TX5))

        # Right-click context menu
        ctx = tk.Menu(popup, tearoff=0, bg=BG2, fg=TX, activebackground=ACC,
                      activeforeground=BL, bd=0, relief='flat')
        ctx.add_command(label='Aç',
                        command=lambda: on_select(None))
        ctx.add_command(label='Seçileni Kopyala (satır)',
                        command=lambda: copy_selected())
        ctx.add_separator()
        ctx.add_command(label="Tüm Tickerları Kopyala",
                        command=copy_all_symbols)

        def show_ctx(e):
            idx = lb.nearest(e.y)
            if idx >= 0:
                lb.selection_clear(0, 'end')
                lb.selection_set(idx)
            try: ctx.tk_popup(e.x_root, e.y_root)
            finally: ctx.grab_release()

        lb.bind('<Button-3>', show_ctx)

    # ─── SCANNER ─────────────────────────────────────
    def _start_scanner(self):
        self.scan_on = True
        self._set_scan_status('● DİNLİYOR', GR)
        t = threading.Thread(target=self._scan_loop, daemon=True)
        t.start()

    def _scan_loop(self):
        _no_detect = 0
        while self.scan_on:
            try:
                win_info = get_window_info()
                pref_set = set(self.pref.keys())
                cef_set = CEF_SET | set(self.cef.keys())
                sym = find_ticker(win_info, pref_set, cef_set)
                if sym and sym != self.last_scan:
                    _no_detect = 0
                    self.last_scan = sym
                    self.root.after(0, self._scanner_found, sym)
                elif not sym:
                    # If nothing detectable for ~5 sec, allow re-detection
                    # so next valid ticker triggers an update even if same as before
                    _no_detect += 1
                    if _no_detect >= 8:
                        _no_detect = 0
                        self.last_scan = None
            except Exception:
                pass
            time.sleep(0.6)

    def _scanner_found(self, sym):
        self._set_scan_status(f'● {sym}', AM)
        self.select(sym)
        self.root.after(2000, lambda: self._set_scan_status('● DİNLİYOR', GR))

    def _quick_add_common(self):
        """Open common form pre-filled with current pref's parent symbol."""
        sym = None
        if self.current and self.current in self.pref:
            sym = self.ptoc.get(self.current)
        self._open_common_form(sym)

    def _quick_add_cef(self):
        sym = self.current if self.current and (self.current in self.cef or self.current in CEF_SET) else ''
        self._open_cef_form(sym)

    def _take_data(self):
        sym = self.current
        if sym and (sym in self.cef or sym in CEF_SET) and sym not in self.pref:
            self._set_scan_status('DATA...', AM)
            def cef_worker():
                ok = False
                try:
                    yahoo_sym, price = self._fetch_yahoo_price(sym, preferred=False)
                    self._apply_cef_market_data(sym, price, yahoo_sym)
                    _save('cef_sector_data.json', self.cef)
                    ok = True
                except Exception:
                    pass
                self.root.after(0, lambda: self._finish_cef_take_data(sym, ok))
            threading.Thread(target=cef_worker, daemon=True).start()
            return
        if not sym or sym not in self.pref:
            self._set_scan_status('PREF SEÇ', RD)
            self.root.after(2500, lambda: self._set_scan_status('● DİNLİYOR', GR))
            return

        parent = self.ptoc.get(sym)
        self._set_scan_status('DATA...', AM)

        def worker():
            result = {'errors': []}
            try:
                yahoo_sym, price = self._fetch_yahoo_price(sym, preferred=True)
                result['yahooSymbol'] = yahoo_sym
                result['lastPrice'] = price
                div_v = self.pref.get(sym, {}).get('div')
                if div_v is not None:
                    result['currentYield'] = (float(div_v) * 4 / price) * 100
            except Exception as exc:
                result['errors'].append(f"Fiyat: {exc}")

            if parent:
                try:
                    yahoo_parent, market_cap = self._fetch_yahoo_market_cap(parent)
                    result['parentYahooSymbol'] = yahoo_parent
                    result['marketCap'] = market_cap
                except Exception as exc:
                    result['errors'].append(f"Market Cap: {exc}")

            self.root.after(0, lambda: self._finish_take_data(sym, parent, result))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_cef_take_data(self, sym, ok):
        self._reload()
        if self.current == sym:
            self.select(sym)
        self._set_scan_status('DATA OK' if ok else 'DATA HATA', GR if ok else RD)
        self.root.after(2500, lambda: self._set_scan_status('● DİNLİYOR', GR))

    def _finish_take_data(self, sym, parent, result):
        today_s = date.today().isoformat()
        changed = False
        pref_ok = False
        common_ok = False

        old_pref = dict(self.pref.get(sym, {}))
        old_common = dict(self.common.get(parent, {})) if parent else {}

        if result.get('lastPrice') is not None:
            new_price = round(float(result['lastPrice']), 4)
            old_price = old_pref.get('lastPrice')
            p = self._apply_pref_market_data(sym, new_price, result.get('yahooSymbol', sym))
            _save('pref_data.json', self.pref)
            try:
                pref_ok = old_price is None or round(float(old_price), 4) != new_price
            except Exception:
                pref_ok = True
            if p.get('currentYield') is not None:
                try:
                    pref_ok = pref_ok or round(float(old_pref.get('currentYield')), 2) != p.get('currentYield')
                except Exception:
                    pref_ok = True
            changed = True

        if parent and result.get('marketCap'):
            c = dict(old_common)
            new_cap = result['marketCap']
            c['marketCap'] = new_cap
            c['marketCapUpdated'] = today_s
            c['marketCapYahooSymbol'] = result.get('parentYahooSymbol', parent)
            self.common[parent] = c
            _save('common_data.json', self.common)
            common_ok = clean(old_common.get('marketCap')) != clean(new_cap)
            changed = True

        self._set_take_mark(f'pref:{sym}:price', pref_ok)
        if parent:
            self._set_take_mark(f'common:{parent}:marketCap', common_ok)

        if changed:
            self._reload()
            self._build_categories()

        if self.current == sym:
            self.select(sym)

        if changed and not result.get('errors'):
            self._set_scan_status('DATA OK', GR)
            self.root.after(2000, lambda: self._set_scan_status('● DİNLİYOR', GR))
        elif changed:
            self._set_scan_status('DATA KISMİ', AM)
            self.root.after(2500, lambda: self._set_scan_status('● DİNLİYOR', GR))
        else:
            self._set_scan_status('DATA HATA', RD)
            self.root.after(2500, lambda: self._set_scan_status('● DİNLİYOR', GR))

    def _set_scan_status(self, text, color):
        self._scan_lbl.config(text=text, fg=color)

    # ─── BUTTONS ─────────────────────────────────────
    def _btn(self, parent, text, color, cmd, **kw):
        b = tk.Label(parent, text=text, fg=color, bg=BG2,
                     font=(FNU, 8), cursor='hand2',
                     padx=8, pady=3,
                     highlightthickness=1,
                     highlightbackground=BD, **kw)
        b.bind('<Button-1>', lambda e: cmd())
        b.bind('<Enter>', lambda e: b.config(bg=ACC))
        b.bind('<Leave>', lambda e: b.config(bg=BG2))
        return b

    # ─── FORMS ───────────────────────────────────────
    def _parse_earnings_text(self, raw, start_month, start_year):
        out = {}
        errors = []
        current_date = None
        current_session = 'daytime'
        tentative = False
        previous_day = None
        month = start_month
        year = start_year

        for line_no, line in enumerate(raw.splitlines(), 1):
            text = clean(line).upper()
            if not text:
                continue
            if text == '////':
                tentative = True
                current_date = None
                current_session = 'tentative'
                continue
            if tentative:
                if not re.fullmatch(r'[A-Z0-9.\-]{1,12}', text):
                    errors.append(f"{line_no}: geçersiz ticker {text}")
                    continue
                out[text] = {'date': '', 'label': 'Tentative', 'session': 'tentative'}
                continue
            if text == '****':
                if current_date is None:
                    errors.append(f"{line_no}: **** öncesinde gün yok")
                current_session = 'after close'
                continue
            if re.fullmatch(r'\d{1,2}', text):
                day = int(text)
                if previous_day is not None and day < previous_day:
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                try:
                    current_date = date(year, month, day)
                except ValueError:
                    errors.append(f"{line_no}: geçersiz gün {text}")
                    current_date = None
                previous_day = day
                current_session = 'daytime'
                continue
            if current_date is None:
                errors.append(f"{line_no}: {text} için gün bulunamadı")
                continue
            if not re.fullmatch(r'[A-Z0-9.\-]{1,12}', text):
                errors.append(f"{line_no}: geçersiz ticker {text}")
                continue
            out[text] = {
                'date': current_date.isoformat(),
                'label': self._date_label(current_date.isoformat()),
                'session': current_session,
            }
        return out, errors

    def _parse_dividends_text(self, raw, start_month, start_year):
        out = {}
        errors = []
        current_date = None
        previous_day = None
        month = start_month
        year = start_year

        for line_no, line in enumerate(raw.splitlines(), 1):
            text = clean(line).upper()
            if not text:
                continue
            if re.fullmatch(r'\d{1,2}', text):
                day = int(text)
                if previous_day is not None and day < previous_day:
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                try:
                    current_date = date(year, month, day)
                except ValueError:
                    errors.append(f"{line_no}: geçersiz gün {text}")
                    current_date = None
                previous_day = day
                continue
            if current_date is None:
                errors.append(f"{line_no}: {text} için gün bulunamadı")
                continue
            if not re.fullmatch(r'[A-Z0-9.\-]{1,12}', text):
                errors.append(f"{line_no}: geçersiz ticker {text}")
                continue
            out[text] = {
                'date': current_date.isoformat(),
                'label': self._date_label(current_date.isoformat()),
            }
        return out, errors

    def _open_earnings_form(self):
        today = date.today()

        dlg = tk.Toplevel(self.root)
        dlg.title('Earning Listesi')
        dlg.geometry('370x520')
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text='＋ YENİ EARNING LİSTESİ',
                 fg=BL, bg=BG2, font=(FNU, 9, 'bold'),
                 padx=8, pady=7).pack(fill='x')
        tk.Frame(dlg, bg=BD, height=1).pack(fill='x')

        sf = tk.Frame(dlg, bg=BG, padx=10)
        sf.pack(fill='both', expand=True, pady=8)

        top = tk.Frame(sf, bg=BG)
        top.pack(fill='x', pady=(0,6))
        tk.Label(top, text='BAŞLANGIÇ AY', fg=TX5, bg=BG,
                 font=(FNU, 7)).pack(side='left')
        month_var = tk.StringVar(value=str(today.month))
        month_entry = tk.Entry(top, textvariable=month_var, width=4, bg=BG2, fg=TX,
                               insertbackground=BL, font=(FN, 9), relief='flat',
                               bd=0, highlightthickness=1, highlightbackground=BD,
                               highlightcolor=BL2)
        month_entry.pack(side='left', padx=(6,12), ipady=3)
        tk.Label(top, text='YIL', fg=TX5, bg=BG,
                 font=(FNU, 7)).pack(side='left')
        year_var = tk.StringVar(value=str(today.year))
        year_entry = tk.Entry(top, textvariable=year_var, width=6, bg=BG2, fg=TX,
                              insertbackground=BL, font=(FN, 9), relief='flat',
                              bd=0, highlightthickness=1, highlightbackground=BD,
                              highlightcolor=BL2)
        year_entry.pack(side='left', padx=(6,0), ipady=3)

        tk.Label(sf, text='LİSTE', fg=TX5, bg=BG,
                 font=(FNU, 7)).pack(anchor='w')
        txt = tk.Text(sf, bg=BG2, fg=TX, insertbackground=BL,
                      font=(FN, 9), relief='flat', bd=0,
                      highlightthickness=1, highlightbackground=BD,
                      highlightcolor=BL2, height=17, wrap='none')
        txt.pack(fill='both', expand=True, pady=(2,6))

        replace_var = tk.IntVar(value=1)
        cb = tk.Checkbutton(sf, text='Mevcut earning listesini temizle',
                            variable=replace_var, bg=BG, fg=TX3,
                            activebackground=BG, activeforeground=TX,
                            selectcolor=BG2, font=(FNU, 8), bd=0,
                            highlightthickness=0)
        cb.pack(anchor='w')

        ff = tk.Frame(dlg, bg=BG2)
        ff.pack(fill='x', side='bottom')
        tk.Frame(ff, bg=BD, height=1).pack(fill='x')
        bf = tk.Frame(ff, bg=BG2)
        bf.pack(fill='x', padx=8, pady=6)

        def submit():
            try:
                month = int(month_var.get().strip())
                year = int(year_var.get().strip())
                if month < 1 or month > 12:
                    raise ValueError
            except ValueError:
                messagebox.showerror('Hata', 'Başlangıç ay/yıl geçersiz.', parent=dlg)
                return

            parsed, errors = self._parse_earnings_text(txt.get('1.0', 'end'), month, year)
            if not parsed:
                messagebox.showerror('Hata', 'Kaydedilecek earning bulunamadı.', parent=dlg)
                return

            if replace_var.get():
                self.earnings = parsed
            else:
                self.earnings.update(parsed)

            _save('earnings_data.json', self.earnings)
            self._reload()

            parents = {clean(v).upper() for v in self.ptoc.values() if clean(v)}
            matched_commons = sorted(set(parsed) & parents)
            matched_prefs = sum(1 for v in self.ptoc.values()
                                if clean(v).upper() in parsed)
            unmatched = sorted(set(parsed) - parents)

            dlg.destroy()
            if self.current:
                self.select(self.current)

            msg = (f"{len(parsed)} common kaydedildi.\n"
                   f"{len(matched_commons)} common, {matched_prefs} preferred ile eşleşti.")
            if unmatched:
                msg += f"\n{len(unmatched)} common için preferred parent bulunamadı."
            if errors:
                msg += f"\n{len(errors)} satır atlandı."
            messagebox.showinfo('Earning Listesi', msg, parent=self.root)

        tk.Button(bf, text='💾 Yükle', command=submit,
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left', padx=(0,6))
        tk.Button(bf, text='İptal', command=dlg.destroy,
                  bg=BG2, fg=TX4, activebackground=BG3,
                  font=(FNU, 9), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left')

    def _open_dividends_form(self):
        today = date.today()

        dlg = tk.Toplevel(self.root)
        dlg.title('Dividend Listesi')
        dlg.geometry('370x520')
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text='＋ YENİ DIVIDEND LİSTESİ',
                 fg=BL, bg=BG2, font=(FNU, 9, 'bold'),
                 padx=8, pady=7).pack(fill='x')
        tk.Frame(dlg, bg=BD, height=1).pack(fill='x')

        sf = tk.Frame(dlg, bg=BG, padx=10)
        sf.pack(fill='both', expand=True, pady=8)

        top = tk.Frame(sf, bg=BG)
        top.pack(fill='x', pady=(0,6))
        tk.Label(top, text='BAŞLANGIÇ AY', fg=TX5, bg=BG,
                 font=(FNU, 7)).pack(side='left')
        month_var = tk.StringVar(value=str(today.month))
        tk.Entry(top, textvariable=month_var, width=4, bg=BG2, fg=TX,
                 insertbackground=BL, font=(FN, 9), relief='flat',
                 bd=0, highlightthickness=1, highlightbackground=BD,
                 highlightcolor=BL2).pack(side='left', padx=(6,12), ipady=3)
        tk.Label(top, text='YIL', fg=TX5, bg=BG,
                 font=(FNU, 7)).pack(side='left')
        year_var = tk.StringVar(value=str(today.year))
        tk.Entry(top, textvariable=year_var, width=6, bg=BG2, fg=TX,
                 insertbackground=BL, font=(FN, 9), relief='flat',
                 bd=0, highlightthickness=1, highlightbackground=BD,
                 highlightcolor=BL2).pack(side='left', padx=(6,0), ipady=3)

        tk.Label(sf, text='LİSTE', fg=TX5, bg=BG,
                 font=(FNU, 7)).pack(anchor='w')
        txt = tk.Text(sf, bg=BG2, fg=TX, insertbackground=BL,
                      font=(FN, 9), relief='flat', bd=0,
                      highlightthickness=1, highlightbackground=BD,
                      highlightcolor=BL2, height=17, wrap='none')
        txt.pack(fill='both', expand=True, pady=(2,6))

        replace_var = tk.IntVar(value=1)
        tk.Checkbutton(sf, text='Mevcut dividend listesini temizle',
                       variable=replace_var, bg=BG, fg=TX3,
                       activebackground=BG, activeforeground=TX,
                       selectcolor=BG2, font=(FNU, 8), bd=0,
                       highlightthickness=0).pack(anchor='w')

        ff = tk.Frame(dlg, bg=BG2)
        ff.pack(fill='x', side='bottom')
        tk.Frame(ff, bg=BD, height=1).pack(fill='x')
        bf = tk.Frame(ff, bg=BG2)
        bf.pack(fill='x', padx=8, pady=6)

        def submit():
            try:
                month = int(month_var.get().strip())
                year = int(year_var.get().strip())
                if month < 1 or month > 12:
                    raise ValueError
            except ValueError:
                messagebox.showerror('Hata', 'Başlangıç ay/yıl geçersiz.', parent=dlg)
                return

            parsed, errors = self._parse_dividends_text(txt.get('1.0', 'end'), month, year)
            if not parsed:
                messagebox.showerror('Hata', 'Kaydedilecek dividend bulunamadı.', parent=dlg)
                return

            if replace_var.get():
                self.dividends = parsed
            else:
                self.dividends.update(parsed)
            _save('dividend_events.json', self.dividends)
            self._reload()

            matched = sorted(set(parsed) & set(self.pref.keys()))
            dlg.destroy()
            if self.current:
                self.select(self.current)
            msg = f"{len(parsed)} dividend kaydedildi.\n{len(matched)} preferred ile eşleşti."
            if errors:
                msg += f"\n{len(errors)} satır atlandı."
            messagebox.showinfo('Dividend Listesi', msg, parent=self.root)

        tk.Button(bf, text='💾 Yükle', command=submit,
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left', padx=(0,6))
        tk.Button(bf, text='İptal', command=dlg.destroy,
                  bg=BG2, fg=TX4, activebackground=BG3,
                  font=(FNU, 9), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left')

    def _open_cef_form(self, sym):
        sym = sym.upper().strip()
        sectors = self._cef_sectors(sym)

        dlg = tk.Toplevel(self.root)
        dlg.title(f'CEF — {sym or "Yeni"}')
        dlg.geometry('340x285')
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=f'✏ CEF DÜZENLE — {sym or "YENİ"}',
                 fg=BL, bg=BG2, font=(FNU, 9, 'bold'),
                 padx=8, pady=7).pack(fill='x')
        tk.Frame(dlg, bg=BD, height=1).pack(fill='x')

        sf = tk.Frame(dlg, bg=BG, padx=10)
        sf.pack(fill='both', expand=True, pady=8)

        tf = tk.Frame(sf, bg=BG)
        tf.pack(fill='x', pady=3)
        tk.Label(tf, text='TICKER', fg=TX5, bg=BG, font=(FNU, 7),
                 width=14, anchor='w').pack(side='left')
        sym_entry = tk.Entry(tf, bg=BG2, fg=TX, insertbackground=BL,
                             font=(FN, 9), relief='flat', bd=0,
                             highlightthickness=1, highlightbackground=BD,
                             highlightcolor=BL2)
        sym_entry.insert(0, sym)
        sym_entry.pack(side='left', fill='x', expand=True, ipady=4, padx=2)
        if sym:
            sym_entry.config(state='readonly', fg=TX3)

        rf = tk.Frame(sf, bg=BG)
        rf.pack(fill='both', expand=True, pady=3)
        tk.Label(rf, text='ENDEKS / SEKTÖR', fg=TX5, bg=BG, font=(FNU, 7),
                 width=14, anchor='w').pack(side='left', anchor='n')
        txt = tk.Text(rf, bg=BG2, fg=TX, insertbackground=BL,
                      font=(FN, 9), relief='flat', bd=0,
                      highlightthickness=1, highlightbackground=BD,
                      highlightcolor=BL2, height=5, wrap='word')
        txt.insert('1.0', '\n'.join(sectors))
        txt.pack(side='left', fill='both', expand=True, padx=2)

        ff = tk.Frame(dlg, bg=BG2)
        ff.pack(fill='x', side='bottom')
        tk.Frame(ff, bg=BD, height=1).pack(fill='x')
        bf = tk.Frame(ff, bg=BG2)
        bf.pack(fill='x', padx=8, pady=6)

        def submit():
            s = sym_entry.get().strip().upper()
            if not s:
                messagebox.showerror('Hata', 'Ticker zorunludur!', parent=dlg)
                return
            vals = []
            for item in re.split(r'[,;\n]+', txt.get('1.0', 'end')):
                val = clean(item)
                if val and val not in vals:
                    vals.append(val)
            row = dict(self.cef.get(s, {}))
            row['sectors'] = vals
            self.cef[s] = row
            _save('cef_sector_data.json', self.cef)
            self._reload()
            dlg.destroy()
            self.select(s)

        tk.Button(bf, text='💾 Kaydet', command=submit,
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left', padx=(0,6))
        tk.Button(bf, text='İptal', command=dlg.destroy,
                  bg=BG2, fg=TX4, activebackground=BG3,
                  font=(FNU, 9), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left')

    def _open_pref_form(self, sym):
        p = self.pref.get(sym, {}) if sym else {}
        parent_val = self.ptoc.get(sym, '') if sym else ''
        is_edit = sym is not None

        dlg = tk.Toplevel(self.root)
        dlg.title(f'{"Düzenle" if is_edit else "Ekle"} — Preferred')
        dlg.geometry('340x500')
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=('✏ PREFERRED DÜZENLE' if is_edit else '＋ YENİ PREFERRED'),
                 fg=BL, bg=BG2, font=(FNU, 9, 'bold'),
                 padx=8, pady=7).pack(fill='x')
        tk.Frame(dlg, bg=BD, height=1).pack(fill='x')

        sf = tk.Frame(dlg, bg=BG, padx=10)
        sf.pack(fill='both', expand=True, pady=4)

        fields = {}

        def row(lbl, key, default='', choices=None):
            rf = tk.Frame(sf, bg=BG)
            rf.pack(fill='x', pady=3)
            tk.Label(rf, text=lbl.upper(), fg=TX5, bg=BG, font=(FNU, 7),
                     width=14, anchor='w').pack(side='left')
            if choices:
                v = tk.StringVar(value=default)
                w = tk.OptionMenu(rf, v, *choices)
                w.config(bg=BG2, fg=TX, activebackground=ACC, activeforeground=BL,
                         font=(FN, 9), relief='flat', bd=0, highlightthickness=0,
                         indicatoron=0)
                w['menu'].config(bg=BG2, fg=TX, activebackground=ACC)
                w.pack(side='left', fill='x', expand=True)
                fields[key] = v
            else:
                e = tk.Entry(rf, bg=BG2, fg=TX, insertbackground=BL,
                             font=(FN, 9), relief='flat', bd=0,
                             highlightthickness=1, highlightbackground=BD,
                             highlightcolor=BL2)
                e.insert(0, default)
                e.pack(side='left', fill='x', expand=True, ipady=4, padx=2)
                fields[key] = e

        row('Ticker', 'sym', sym or '')
        row('Parent Common', 'parent', parent_val)

        type_choices = ['Fixed','Floating','FixedToFloat','BB','Floating BB',
                        'Fixed BB','Reset','Fixed To Floating','Conv','']
        row('Tip', 'fixFloat', p.get('fixFloat',''), choices=type_choices)
        row('Kupon Oranı', 'coupon', p.get('coupon',''))
        row('Dividend (Q $)', 'div', str(p.get('div','') or ''))

        rating_choices = ['GOOD','MID','NF','NR','BAD','']
        row('Rating', 'rating', p.get('rating',''), choices=rating_choices)
        row('Call Tarihi', 'callDate', p.get('callDate',''))
        row('Mature Tarihi', 'matureDate', p.get('matureDate',''))

        mn4_choices = ['YES','MIGHT','NO','']
        row('>4M Likidite', 'mn4', p.get('mn4',''), choices=mn4_choices)

        if is_edit:
            fields['sym'].config(state='readonly', fg=TX3)

        # Footer
        ff = tk.Frame(dlg, bg=BG2)
        ff.pack(fill='x', side='bottom')
        tk.Frame(ff, bg=BD, height=1).pack(fill='x')
        bf = tk.Frame(ff, bg=BG2)
        bf.pack(fill='x', padx=8, pady=6)

        def get_val(k):
            w = fields[k]
            return w.get() if isinstance(w, (tk.Entry, tk.StringVar)) else w.get()

        def submit():
            s = get_val('sym').strip().upper()
            if not s:
                messagebox.showerror('Hata', 'Ticker zorunludur!', parent=dlg)
                return
            try:
                div_v = float(get_val('div')) if get_val('div').strip() else None
            except ValueError:
                div_v = None

            pref_row = dict(self.pref.get(s, {}))
            pref_row.update({
                'fixFloat':   get_val('fixFloat'),
                'coupon':     get_val('coupon').strip(),
                'div':        div_v,
                'callDate':   get_val('callDate').strip(),
                'matureDate': get_val('matureDate').strip(),
                'rating':     get_val('rating'),
                'mn4':        get_val('mn4'),
            })
            self.pref[s] = pref_row
            parent_s = get_val('parent').strip().upper()
            if parent_s:
                self.ptoc[s] = parent_s

            _save('pref_data.json', self.pref)
            _save('pref_to_common.json', self.ptoc)
            self._reload()
            self._build_categories()
            dlg.destroy()
            self.select(s)

        tk.Button(bf, text='💾 Kaydet', command=submit,
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left', padx=(0,6))
        tk.Button(bf, text='İptal', command=dlg.destroy,
                  bg=BG2, fg=TX4, activebackground=BG3,
                  font=(FNU, 9), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left')

    def _open_common_form(self, sym):
        c = self.common.get(sym, {})

        dlg = tk.Toplevel(self.root)
        dlg.title(f'Common — {sym}')
        dlg.geometry('340x460')
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=f'✏ COMMON DÜZENLE — {sym}',
                 fg=BL, bg=BG2, font=(FNU, 9, 'bold'),
                 padx=8, pady=7).pack(fill='x')
        tk.Frame(dlg, bg=BD, height=1).pack(fill='x')

        sf = tk.Frame(dlg, bg=BG, padx=10)
        sf.pack(fill='both', expand=True, pady=4)

        fields = {}

        def row(lbl, key, default='', tall=False):
            rf = tk.Frame(sf, bg=BG)
            rf.pack(fill='x', pady=3)
            tk.Label(rf, text=lbl.upper(), fg=TX5, bg=BG, font=(FNU, 7),
                     width=14, anchor='w').pack(side='left', anchor='n')
            if tall:
                t = tk.Text(rf, bg=BG2, fg=TX, insertbackground=BL,
                            font=(FN, 8), relief='flat', bd=0,
                            highlightthickness=1, highlightbackground=BD,
                            highlightcolor=BL2, height=3, wrap='word')
                t.insert('1.0', default)
                t.pack(side='left', fill='x', expand=True, padx=2)
                fields[key] = t
            else:
                e = tk.Entry(rf, bg=BG2, fg=TX, insertbackground=BL,
                             font=(FN, 9), relief='flat', bd=0,
                             highlightthickness=1, highlightbackground=BD,
                             highlightcolor=BL2)
                e.insert(0, default)
                e.pack(side='left', fill='x', expand=True, ipady=4, padx=2)
                fields[key] = e

        row('Ticker', 'sym', sym)
        row('Sektör', 'sector', c.get('sector',''))
        row('Market Cap', 'marketCap', c.get('marketCap',''))
        row('Altman Z', 'altman', c.get('altman',''))
        row('Current Ratio', 'currentRatio', c.get('currentRatio',''))
        row('D/E', 'de', c.get('de',''))
        row('ROIC/WACC', 'roicWacc', c.get('roicWacc',''))
        row('Yorum', 'comment', c.get('comment',''), tall=True)

        fields['sym'].config(state='readonly', fg=TX3)

        ff = tk.Frame(dlg, bg=BG2)
        ff.pack(fill='x', side='bottom')
        tk.Frame(ff, bg=BD, height=1).pack(fill='x')
        bf = tk.Frame(ff, bg=BG2)
        bf.pack(fill='x', padx=8, pady=6)

        def get_val(k):
            w = fields[k]
            if isinstance(w, tk.Text):
                return w.get('1.0','end').strip()
            return w.get()

        def submit():
            s = get_val('sym').strip().upper()
            common_row = dict(self.common.get(s, {}))
            common_row.update({
                'sector': get_val('sector'), 'marketCap': get_val('marketCap'),
                'altman': get_val('altman'), 'currentRatio': get_val('currentRatio'),
                'de': get_val('de'), 'roicWacc': get_val('roicWacc'),
                'comment': get_val('comment'),
            })
            self.common[s] = common_row
            _save('common_data.json', self.common)
            self._reload()
            dlg.destroy()
            if self.current:
                self.select(self.current)

        tk.Button(bf, text='💾 Kaydet', command=submit,
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left', padx=(0,6))
        tk.Button(bf, text='İptal', command=dlg.destroy,
                  bg=BG2, fg=TX4, activebackground=BG3,
                  font=(FNU, 9), relief='flat', bd=0,
                  padx=12, pady=5, cursor='hand2').pack(side='left')

    def _confirm_delete(self, sym):
        dlg = tk.Toplevel(self.root)
        dlg.title('Sil')
        dlg.geometry('280x130')
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=f'"{sym}" silinsin mi?', fg=TX, bg=BG,
                 font=(FNU, 10), pady=20).pack()
        tk.Label(dlg, text='Bu işlem geri alınamaz.', fg=TX3, bg=BG,
                 font=(FNU, 8)).pack()

        bf = tk.Frame(dlg, bg=BG)
        bf.pack(pady=12)

        def do_delete():
            self.pref.pop(sym, None)
            self.ptoc.pop(sym, None)
            _save('pref_data.json', self.pref)
            _save('pref_to_common.json', self.ptoc)
            self._reload()
            self._build_categories()
            dlg.destroy()
            self._show_empty()

        tk.Button(bf, text='Sil', command=do_delete,
                  bg='#3f1515', fg=RD, activebackground='#5a1a1a',
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=14, pady=5, cursor='hand2').pack(side='left', padx=6)
        tk.Button(bf, text='İptal', command=dlg.destroy,
                  bg=BG2, fg=TX4, activebackground=BG3,
                  font=(FNU, 9), relief='flat', bd=0,
                  padx=14, pady=5, cursor='hand2').pack(side='left')


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    App()
