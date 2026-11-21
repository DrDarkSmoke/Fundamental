#!/usr/bin/env python3
"""
 Hammer Pro — Preferred Lookup v8
Native desktop (tkinter). Window-title scanner for Hammer Pro sync.
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import calendar
import gzip
import zlib
import ctypes
import json, os, sys, threading, time, webbrowser, re, statistics
import html as html_lib
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
BG4  = "#05070d"
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
CY   = "#22d3ee"
GD   = "#d6b25e"
TX   = "#e2e8f0"
TX2  = "#94a3b8"
TX3  = "#64748b"
TX4  = "#475569"
TX5  = "#334155"

FN   = "Courier New"   # monospace
FNU  = "Segoe UI"      # ui
CEF_HISTORY_RETENTION_TRADING_DAYS = 252
CEF_CONNECT_RETRY_SECONDS = 6 * 60 * 60
CEF_DETAIL_FETCH_DELAY_SECONDS = 4.0
CEF_DETAIL_SAVE_EVERY = 8

TRADE_QUESTIONS = [
    "What is the setup and overall trade plan?",
    "Have you checked earnings, guidance, and recent company news?",
    "Have you checked key moving averages and technical levels?",
    "When is the next dividend / ex-dividend date?",
    "What is the current candle structure and long-term trend?",
    "What is the worst-case scenario for this trade?",
    "Where is your stop loss and why?",
    "How is the overall market behaving today?",
    "Is this position worth holding overnight? Why?",
    "How is the related sector performing?",
    "How is the ATR and current volatility environment?",
    "What is the expected risk-to-reward ratio?",
    "Are you entering because of FOMO or because the setup is valid?",
]

TRADE_SCORE_LABELS = {
    1: "Very Bad",
    2: "Weak",
    3: "Neutral",
    4: "Good",
    5: "Excellent",
}

TRADE_ANSWER_OPTIONS = {
    TRADE_QUESTIONS[0]: [
        ("Clean plan", "Setup is valid: entry, stop, target, catalyst, and position size are clear. I will take it only if price confirms the plan.", 5),
        ("Caution", "Setup is partly valid but needs confirmation. I will reduce size or wait for a better entry if momentum weakens.", 3),
        ("No plan", "No clean setup or trade plan. Entry, target, or stop is not clear enough, so this trade should be avoided.", 1),
        ("Need check", "I still need to confirm the setup, levels, and catalyst before entering.", 2),
    ],
    TRADE_QUESTIONS[1]: [
        ("Clear", "Earnings, guidance, and recent news have been checked. No obvious negative surprise is blocking the trade.", 5),
        ("Positive", "Recent news or guidance is supportive, but I still need price action to confirm before entering.", 4),
        ("Risk found", "There is negative or uncertain company news. This increases headline risk and makes the trade weaker.", 1),
        ("Unchecked", "Earnings, guidance, and news are not fully checked yet. Do not enter until this is reviewed.", 2),
    ],
    TRADE_QUESTIONS[2]: [
        ("Above levels", "Price is holding above key moving averages and support levels. Technical structure supports the trade.", 5),
        ("Near level", "Price is near an important level. I need confirmation or a better entry before full size.", 3),
        ("Below levels", "Price is below key moving averages or has broken support. Technical risk is high.", 1),
        ("Need levels", "Key moving averages and support/resistance levels still need to be checked.", 2),
    ],
    TRADE_QUESTIONS[3]: [
        ("No issue", "No near ex-dividend or dividend timing issue is expected to affect this trade.", 5),
        ("Near date", "Dividend or ex-dividend timing is near. The trade is still possible, but sizing and timing need caution.", 3),
        ("Dividend risk", "Dividend timing creates extra risk or price adjustment risk. This weakens the trade.", 1),
        ("Unknown", "Next dividend or ex-dividend date is unknown. Check it before entering.", 2),
    ],
    TRADE_QUESTIONS[4]: [
        ("Bullish", "Current candle structure is bullish and aligned with the longer-term trend.", 5),
        ("Neutral", "Candle structure is mixed or consolidating. I need a clearer break or hold before entering.", 3),
        ("Bearish", "Current candle structure is bearish or rejecting key levels. Long trade is not attractive here.", 1),
        ("Reversal", "There may be a reversal attempt, but it is not confirmed yet. Use smaller size or wait.", 2),
    ],
    TRADE_QUESTIONS[5]: [
        ("Defined", "Worst case is a controlled loss at the stop. Position size keeps the loss acceptable.", 5),
        ("Gap risk", "Worst case is a gap through the stop or fast move against the position. Size must be reduced.", 3),
        ("Large loss", "Worst case is too large or unclear. The trade should be avoided until risk is defined.", 1),
        ("Need define", "Worst-case scenario is not fully defined yet. Do not enter until downside is clear.", 2),
    ],
    TRADE_QUESTIONS[6]: [
        ("Support stop", "Stop loss is below the key support or invalidation level. If it breaks, the trade idea is wrong.", 5),
        ("Tight stop", "Stop is tight and based on immediate invalidation. This needs clean execution and smaller size.", 4),
        ("Wide stop", "Stop is wide because volatility is elevated. Size should be reduced to keep dollar risk controlled.", 3),
        ("No stop", "No clear stop loss is defined. This trade should not be entered.", 1),
    ],
    TRADE_QUESTIONS[7]: [
        ("Supportive", "Overall market is supportive today, with risk appetite and index direction helping the trade.", 5),
        ("Mixed", "Market behavior is mixed. The trade can work, but confirmation and smaller size are preferred.", 3),
        ("Weak", "Overall market is weak or selling off. This lowers the quality of the setup.", 1),
        ("Event risk", "Market has event or news risk today. Wait for clarity or reduce size.", 2),
    ],
    TRADE_QUESTIONS[8]: [
        ("Yes", "This position is worth holding overnight because the setup, risk, and catalyst remain valid.", 5),
        ("Small only", "Overnight hold is acceptable only with reduced size because gap or news risk is present.", 3),
        ("No", "This is not worth holding overnight. Risk of gap, news, or trend failure is too high.", 1),
        ("Decide later", "Overnight decision should be made near the close after reviewing price action and news risk.", 2),
    ],
    TRADE_QUESTIONS[9]: [
        ("Strong", "Related sector is strong and showing relative strength. Sector backdrop supports the trade.", 5),
        ("Mixed", "Sector performance is mixed. The individual setup must be strong enough to justify the trade.", 3),
        ("Weak", "Related sector is weak or underperforming. This creates headwind for the trade.", 1),
        ("Unchecked", "Sector performance has not been checked yet. Review sector strength before entering.", 2),
    ],
    TRADE_QUESTIONS[10]: [
        ("Normal", "ATR and volatility are normal. Stop and position size are reasonable for current conditions.", 5),
        ("Elevated", "Volatility is elevated. Trade can still work, but size should be reduced and stop respected.", 3),
        ("Too high", "Volatility is too high for a clean entry. Risk is hard to control, so avoid or wait.", 1),
        ("Low vol", "Volatility is low. Breakout may need confirmation, but risk can be controlled if levels are clear.", 4),
    ],
    TRADE_QUESTIONS[11]: [
        ("2R plus", "Expected risk-to-reward is at least 2:1 and the target is realistic.", 5),
        ("1.5R", "Expected risk-to-reward is acceptable but not ideal. Smaller size or better entry is preferred.", 3),
        ("Bad R:R", "Risk-to-reward is poor. Potential reward does not justify the downside.", 1),
        ("Undefined", "Risk-to-reward is not defined yet. Do not enter until stop and target are clear.", 2),
    ],
    TRADE_QUESTIONS[12]: [
        ("Valid", "Entry is based on a valid setup and predefined plan, not FOMO.", 5),
        ("Some FOMO", "There is some FOMO. I should wait for confirmation or reduce size.", 3),
        ("FOMO", "This entry is mostly FOMO. The correct decision is to skip or wait.", 1),
        ("Pause", "I need to pause and re-check the plan before deciding. No rushed entry.", 2),
    ],
}

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
def _app_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def _ddir():
    return os.path.join(_app_root(), 'data')

# ══════════════════════════════════════════════════════
#  DIVIDEND CALENDAR DATA
# ══════════════════════════════════════════════════════
try:
    from dateutil.relativedelta import relativedelta
    def _add_months(d, n):
        return d + relativedelta(months=n)
except ImportError:
    def _add_months(d, n):
        month = d.month - 1 + n
        year  = d.year + month // 12
        month = month % 12 + 1
        day   = min(d.day, [31,28+int((year%4==0 and(year%100!=0 or year%400==0))),
                             31,30,31,30,31,31,30,31,30,31][month-1])
        return date(year, month, day)

_DIV_HOLIDAYS = {
    date(2026,1,1), date(2026,1,19), date(2026,2,16), date(2026,4,3),
    date(2026,5,25), date(2026,6,19), date(2026,7,3), date(2026,9,7),
    date(2026,11,26), date(2026,12,25),
    date(2027,1,1), date(2027,1,18), date(2027,2,15), date(2027,3,26),
    date(2027,5,31), date(2027,6,18), date(2027,7,5), date(2027,9,6),
    date(2027,11,25), date(2027,12,24), date(2027,12,31),
    date(2028,1,17), date(2028,2,21), date(2028,4,14),
    date(2028,5,29), date(2028,6,19), date(2028,7,4), date(2028,9,4),
    date(2028,11,23), date(2028,12,25),
}

_DIV_MONTHS = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]

_QUARTERLY_RAW = [
{"ticker":"BML-L","lastDate":"2026-01-12"},{"ticker":"T-A","lastDate":"2026-01-12"},
{"ticker":"T-C","lastDate":"2026-01-12"},{"ticker":"TWO-A","lastDate":"2026-01-12"},
{"ticker":"TWO-B","lastDate":"2026-01-12"},{"ticker":"TWO-C","lastDate":"2026-01-12"},
{"ticker":"CMRE-B","lastDate":"2026-01-14"},{"ticker":"CMRE-C","lastDate":"2026-01-14"},
{"ticker":"CMRE-D","lastDate":"2026-01-14"},{"ticker":"DSX-B","lastDate":"2026-01-14"},
{"ticker":"NEWTH","lastDate":"2026-01-14"},{"ticker":"SOJE","lastDate":"2026-01-14"},
{"ticker":"XELLL","lastDate":"2026-01-14"},{"ticker":"ABR-D","lastDate":"2026-01-15"},
{"ticker":"ABR-E","lastDate":"2026-01-15"},{"ticker":"ABR-F","lastDate":"2026-01-15"},
{"ticker":"AFGB","lastDate":"2026-01-15"},{"ticker":"ALTG-A","lastDate":"2026-01-15"},
{"ticker":"AOMN","lastDate":"2026-01-15"},{"ticker":"ATLCL","lastDate":"2026-01-15"},
{"ticker":"BAC-O","lastDate":"2026-01-15"},{"ticker":"BAC-P","lastDate":"2026-01-15"},
{"ticker":"BWSN","lastDate":"2026-01-15"},{"ticker":"CODI-A","lastDate":"2026-01-15"},
{"ticker":"CODI-B","lastDate":"2026-01-15"},{"ticker":"CODI-C","lastDate":"2026-01-15"},
{"ticker":"DHCNI","lastDate":"2026-01-15"},{"ticker":"GAING","lastDate":"2026-01-15"},
{"ticker":"GAINI","lastDate":"2026-01-15"},{"ticker":"GAINL","lastDate":"2026-01-15"},
{"ticker":"GAINN","lastDate":"2026-01-15"},{"ticker":"GAINZ","lastDate":"2026-01-15"},
{"ticker":"GREEL","lastDate":"2026-01-15"},{"ticker":"HCXY","lastDate":"2026-01-15"},
{"ticker":"NEWTZ","lastDate":"2026-01-15"},{"ticker":"NREF-A","lastDate":"2026-01-15"},
{"ticker":"OFSSH","lastDate":"2026-01-15"},{"ticker":"OXSQH","lastDate":"2026-01-15"},
{"ticker":"RCB","lastDate":"2026-01-15"},{"ticker":"RCC","lastDate":"2026-01-15"},
{"ticker":"RILYG","lastDate":"2026-01-15"},{"ticker":"RILYK","lastDate":"2026-01-15"},
{"ticker":"RILYN","lastDate":"2026-01-15"},{"ticker":"RILYT","lastDate":"2026-01-15"},
{"ticker":"RILYZ","lastDate":"2026-01-15"},{"ticker":"XRN-A","lastDate":"2026-01-15"},
{"ticker":"XRN-B","lastDate":"2026-01-15"},{"ticker":"BOH-A","lastDate":"2026-01-16"},
{"ticker":"BOH-B","lastDate":"2026-01-16"},{"ticker":"DDT","lastDate":"2026-01-16"},
{"ticker":"MFICL","lastDate":"2026-01-16"},{"ticker":"SB-C","lastDate":"2026-01-16"},
{"ticker":"SB-D","lastDate":"2026-01-16"},{"ticker":"TBB","lastDate":"2026-01-16"},
{"ticker":"GS-A","lastDate":"2026-01-23"},{"ticker":"GS-C","lastDate":"2026-01-23"},
{"ticker":"GS-D","lastDate":"2026-01-23"},{"ticker":"TEN-F","lastDate":"2026-01-27"},
{"ticker":"C-N","lastDate":"2026-01-29"},{"ticker":"SOJD","lastDate":"2026-01-29"},
{"ticker":"BAC-B","lastDate":"2026-01-30"},{"ticker":"BAC-E","lastDate":"2026-01-30"},
{"ticker":"BAC-Q","lastDate":"2026-01-30"},{"ticker":"BAC-S","lastDate":"2026-01-30"},
{"ticker":"CIMN","lastDate":"2026-01-30"},{"ticker":"CIMO","lastDate":"2026-01-30"},
{"ticker":"CIMP","lastDate":"2026-01-30"},{"ticker":"FLG-U","lastDate":"2026-01-30"},
{"ticker":"FRMEP","lastDate":"2026-01-30"},{"ticker":"MFAN","lastDate":"2026-01-30"},
{"ticker":"MFAO","lastDate":"2026-01-30"},{"ticker":"MITN","lastDate":"2026-01-30"},
{"ticker":"MITP","lastDate":"2026-01-30"},{"ticker":"NEE-T","lastDate":"2026-01-30"},
{"ticker":"NMFCZ","lastDate":"2026-01-30"},{"ticker":"NRUC","lastDate":"2026-01-30"},
{"ticker":"PMTV","lastDate":"2026-01-30"},{"ticker":"PRS","lastDate":"2026-01-30"},
{"ticker":"RITM-A","lastDate":"2026-01-30"},{"ticker":"RITM-B","lastDate":"2026-01-30"},
{"ticker":"RITM-C","lastDate":"2026-01-30"},{"ticker":"RITM-D","lastDate":"2026-01-30"},
{"ticker":"RITM-E","lastDate":"2026-01-30"},{"ticker":"RITM-F","lastDate":"2026-01-30"},
{"ticker":"RPT-C","lastDate":"2026-01-30"},{"ticker":"TVE","lastDate":"2026-01-30"},
{"ticker":"TWOD","lastDate":"2026-01-30"},{"ticker":"HIG-G","lastDate":"2026-02-03"},
{"ticker":"OPP-A","lastDate":"2026-02-03"},{"ticker":"OPP-B","lastDate":"2026-02-03"},
{"ticker":"OPP-C","lastDate":"2026-02-03"},{"ticker":"OZKAP","lastDate":"2026-02-03"},
{"ticker":"RF-C","lastDate":"2026-02-03"},{"ticker":"RIV-A","lastDate":"2026-02-03"},
{"ticker":"HBANZ","lastDate":"2026-02-05"},{"ticker":"ONBPO","lastDate":"2026-02-05"},
{"ticker":"ONBPP","lastDate":"2026-02-05"},{"ticker":"DCOM-","lastDate":"2026-02-06"},
{"ticker":"SYF-A","lastDate":"2026-02-06"},{"ticker":"SYF-B","lastDate":"2026-02-06"},
{"ticker":"CDR-B","lastDate":"2026-02-10"},{"ticker":"CDR-C","lastDate":"2026-02-10"},
{"ticker":"ABXL","lastDate":"2026-02-13"},{"ticker":"AFGD","lastDate":"2026-02-13"},
{"ticker":"AIRTP","lastDate":"2026-02-13"},{"ticker":"AOMD","lastDate":"2026-02-13"},
{"ticker":"ASBA","lastDate":"2026-02-13"},{"ticker":"AUB-A","lastDate":"2026-02-13"},
{"ticker":"BML-G","lastDate":"2026-02-13"},{"ticker":"BML-H","lastDate":"2026-02-13"},
{"ticker":"BML-J","lastDate":"2026-02-13"},{"ticker":"BUSEP","lastDate":"2026-02-13"},
{"ticker":"BWBBP","lastDate":"2026-02-13"},{"ticker":"CCNEP","lastDate":"2026-02-13"},
{"ticker":"CMSD","lastDate":"2026-02-13"},{"ticker":"CNO-A","lastDate":"2026-02-13"},
{"ticker":"CNOBP","lastDate":"2026-02-13"},{"ticker":"DHCNL","lastDate":"2026-02-13"},
{"ticker":"DTG","lastDate":"2026-02-13"},{"ticker":"DTW","lastDate":"2026-02-13"},
{"ticker":"DUK-A","lastDate":"2026-02-13"},{"ticker":"F-B","lastDate":"2026-02-13"},
{"ticker":"F-C","lastDate":"2026-02-13"},{"ticker":"FGBIP","lastDate":"2026-02-13"},
{"ticker":"HBANM","lastDate":"2026-02-13"},{"ticker":"INBKZ","lastDate":"2026-02-13"},
{"ticker":"INN-E","lastDate":"2026-02-13"},{"ticker":"INN-F","lastDate":"2026-02-13"},
{"ticker":"KKRT","lastDate":"2026-02-13"},{"ticker":"LNC-D","lastDate":"2026-02-13"},
{"ticker":"MHNC","lastDate":"2026-02-13"},{"ticker":"NEWTI","lastDate":"2026-02-13"},
{"ticker":"PCG-X","lastDate":"2026-02-13"},{"ticker":"PFH","lastDate":"2026-02-13"},
{"ticker":"PNFP-C","lastDate":"2026-02-13"},{"ticker":"PRH","lastDate":"2026-02-13"},
{"ticker":"RWAYI","lastDate":"2026-02-13"},{"ticker":"RWAYL","lastDate":"2026-02-13"},
{"ticker":"RWAYZ","lastDate":"2026-02-13"},{"ticker":"RWTN","lastDate":"2026-02-13"},
{"ticker":"RWTO","lastDate":"2026-02-13"},{"ticker":"RWTP","lastDate":"2026-02-13"},
{"ticker":"RWTQ","lastDate":"2026-02-13"},{"ticker":"SAJ","lastDate":"2026-02-13"},
{"ticker":"SAT","lastDate":"2026-02-13"},{"ticker":"SAY","lastDate":"2026-02-13"},
{"ticker":"SAZ","lastDate":"2026-02-13"},{"ticker":"SCHW-D","lastDate":"2026-02-13"},
{"ticker":"SCHW-J","lastDate":"2026-02-13"},{"ticker":"SPNT-B","lastDate":"2026-02-13"},
{"ticker":"TFC-I","lastDate":"2026-02-13"},{"ticker":"TFC-O","lastDate":"2026-02-13"},
{"ticker":"TFC-R","lastDate":"2026-02-13"},{"ticker":"COF-I","lastDate":"2026-02-17"},
{"ticker":"COF-J","lastDate":"2026-02-17"},{"ticker":"COF-K","lastDate":"2026-02-17"},
{"ticker":"COF-L","lastDate":"2026-02-17"},{"ticker":"COF-N","lastDate":"2026-02-17"},
{"ticker":"UMH-D","lastDate":"2026-02-17"},{"ticker":"BANC-F","lastDate":"2026-02-19"},
{"ticker":"PBI-B","lastDate":"2026-02-20"},{"ticker":"TEN-E","lastDate":"2026-02-25"},
{"ticker":"VOYA-B","lastDate":"2026-02-25"},{"ticker":"AEFC","lastDate":"2026-02-27"},
{"ticker":"AFGC","lastDate":"2026-02-27"},{"ticker":"AFGE","lastDate":"2026-02-27"},
{"ticker":"APOS","lastDate":"2026-02-27"},{"ticker":"ASB-E","lastDate":"2026-02-27"},
{"ticker":"ASB-F","lastDate":"2026-02-27"},{"ticker":"ATLCP","lastDate":"2026-02-27"},
{"ticker":"BAC-M","lastDate":"2026-02-27"},{"ticker":"BAC-N","lastDate":"2026-02-27"},
{"ticker":"BFH-A","lastDate":"2026-02-27"},{"ticker":"BHFAL","lastDate":"2026-02-27"},
{"ticker":"CFR-B","lastDate":"2026-02-27"},{"ticker":"CHMI-A","lastDate":"2026-02-27"},
{"ticker":"CHMI-B","lastDate":"2026-02-27"},{"ticker":"CIM-A","lastDate":"2026-02-27"},
{"ticker":"CIM-B","lastDate":"2026-02-27"},{"ticker":"CIM-C","lastDate":"2026-02-27"},
{"ticker":"CIM-D","lastDate":"2026-02-27"},{"ticker":"CMSA","lastDate":"2026-02-27"},
{"ticker":"CRBD","lastDate":"2026-02-27"},{"ticker":"CTBB","lastDate":"2026-02-27"},
{"ticker":"EAI","lastDate":"2026-02-27"},{"ticker":"EFSCP","lastDate":"2026-02-27"},
{"ticker":"ELC","lastDate":"2026-02-27"},{"ticker":"FCNCO","lastDate":"2026-02-27"},
{"ticker":"FCNCP","lastDate":"2026-02-27"},{"ticker":"FCRX","lastDate":"2026-02-27"},
{"ticker":"FGN","lastDate":"2026-02-27"},{"ticker":"FGNXP","lastDate":"2026-02-27"},
{"ticker":"GL-D","lastDate":"2026-02-27"},{"ticker":"GPUS-D","lastDate":"2026-02-27"},
{"ticker":"GRBK-A","lastDate":"2026-02-27"},{"ticker":"HWCPZ","lastDate":"2026-02-27"},
{"ticker":"KEY-I","lastDate":"2026-02-27"},{"ticker":"KEY-J","lastDate":"2026-02-27"},
{"ticker":"KEY-K","lastDate":"2026-02-27"},{"ticker":"KEY-L","lastDate":"2026-02-27"},
{"ticker":"KMPB","lastDate":"2026-02-27"},{"ticker":"KREF-A","lastDate":"2026-02-27"},
{"ticker":"MET-A","lastDate":"2026-02-27"},{"ticker":"MET-E","lastDate":"2026-02-27"},
{"ticker":"MET-F","lastDate":"2026-02-27"},{"ticker":"MHLA","lastDate":"2026-02-27"},
{"ticker":"MITT-A","lastDate":"2026-02-27"},{"ticker":"MITT-B","lastDate":"2026-02-27"},
{"ticker":"MITT-C","lastDate":"2026-02-27"},{"ticker":"NEE-N","lastDate":"2026-02-27"},
{"ticker":"NEE-U","lastDate":"2026-02-27"},{"ticker":"NEWTG","lastDate":"2026-02-27"},
{"ticker":"PMT-A","lastDate":"2026-02-27"},{"ticker":"PMT-B","lastDate":"2026-02-27"},
{"ticker":"PMT-C","lastDate":"2026-02-27"},{"ticker":"PMTW","lastDate":"2026-02-27"},
{"ticker":"POWWP","lastDate":"2026-02-27"},{"ticker":"QVCC","lastDate":"2026-02-27"},
{"ticker":"QVCD","lastDate":"2026-02-27"},{"ticker":"RCD","lastDate":"2026-02-27"},
{"ticker":"RF-E","lastDate":"2026-02-27"},{"ticker":"RF-F","lastDate":"2026-02-27"},
{"ticker":"RNR-F","lastDate":"2026-02-27"},{"ticker":"RNR-G","lastDate":"2026-02-27"},
{"ticker":"RZB","lastDate":"2026-02-27"},{"ticker":"SF-B","lastDate":"2026-02-27"},
{"ticker":"SF-C","lastDate":"2026-02-27"},{"ticker":"SF-D","lastDate":"2026-02-27"},
{"ticker":"SIGIP","lastDate":"2026-02-27"},{"ticker":"SOJC","lastDate":"2026-02-27"},
{"ticker":"STT-G","lastDate":"2026-02-27"},{"ticker":"TCBIO","lastDate":"2026-02-27"},
{"ticker":"TMUSI","lastDate":"2026-02-27"},{"ticker":"TMUSL","lastDate":"2026-02-27"},
{"ticker":"TMUSZ","lastDate":"2026-02-27"},{"ticker":"TPGXL","lastDate":"2026-02-27"},
{"ticker":"TVC","lastDate":"2026-02-27"},{"ticker":"UNMA","lastDate":"2026-02-27"},
{"ticker":"UZD","lastDate":"2026-02-27"},{"ticker":"UZE","lastDate":"2026-02-27"},
{"ticker":"UZF","lastDate":"2026-02-27"},{"ticker":"WBS-F","lastDate":"2026-02-27"},
{"ticker":"WFC-C","lastDate":"2026-02-27"},{"ticker":"WFC-D","lastDate":"2026-02-27"},
{"ticker":"WFC-Y","lastDate":"2026-02-27"},{"ticker":"WFC-Z","lastDate":"2026-02-27"},
{"ticker":"WHFCL","lastDate":"2026-02-27"},{"ticker":"ZIONP","lastDate":"2026-02-27"},
{"ticker":"MTB-H","lastDate":"2026-02-28"},{"ticker":"MTB-J","lastDate":"2026-02-28"},
{"ticker":"MTB-K","lastDate":"2026-02-28"},{"ticker":"NLY-F","lastDate":"2026-02-28"},
{"ticker":"NLY-G","lastDate":"2026-02-28"},{"ticker":"NLY-I","lastDate":"2026-02-28"},
{"ticker":"NLY-J","lastDate":"2026-02-28"},{"ticker":"LOB-A","lastDate":"2026-03-02"},
{"ticker":"EQH-A","lastDate":"2026-03-04"},{"ticker":"EQH-C","lastDate":"2026-03-04"},
{"ticker":"MFA-B","lastDate":"2026-03-04"},{"ticker":"MFA-C","lastDate":"2026-03-04"},
{"ticker":"BK-K","lastDate":"2026-03-05"},{"ticker":"FLG-A","lastDate":"2026-03-05"},
{"ticker":"IVR-C","lastDate":"2026-03-05"},{"ticker":"GAM-B","lastDate":"2026-03-06"},
{"ticker":"TRTN-A","lastDate":"2026-03-09"},{"ticker":"TRTN-B","lastDate":"2026-03-09"},
{"ticker":"TRTN-C","lastDate":"2026-03-09"},{"ticker":"TRTN-D","lastDate":"2026-03-09"},
{"ticker":"TRTN-E","lastDate":"2026-03-09"},{"ticker":"TRTN-F","lastDate":"2026-03-09"},
{"ticker":"TRTN-G","lastDate":"2026-03-09"},{"ticker":"BHFAM","lastDate":"2026-03-10"},
{"ticker":"BHFAN","lastDate":"2026-03-10"},{"ticker":"BHFAO","lastDate":"2026-03-10"},
{"ticker":"BHFAP","lastDate":"2026-03-10"},{"ticker":"CTO-A","lastDate":"2026-03-11"},
{"ticker":"ECCU","lastDate":"2026-03-11"},{"ticker":"NCV-A","lastDate":"2026-03-11"},
{"ticker":"PINE-A","lastDate":"2026-03-11"},{"ticker":"CTDD","lastDate":"2026-03-12"},
{"ticker":"DUKB","lastDate":"2026-03-12"},{"ticker":"GJH","lastDate":"2026-03-12"},
{"ticker":"JSM","lastDate":"2026-03-12"},{"ticker":"MER-K","lastDate":"2026-03-12"},
{"ticker":"NCZ-A","lastDate":"2026-03-12"},{"ticker":"SCE-G","lastDate":"2026-03-12"},
{"ticker":"SCE-K","lastDate":"2026-03-12"},{"ticker":"SCE-L","lastDate":"2026-03-12"},
{"ticker":"SCE-M","lastDate":"2026-03-12"},{"ticker":"SCE-N","lastDate":"2026-03-12"},
{"ticker":"SOJF","lastDate":"2026-03-12"},{"ticker":"ACGLN","lastDate":"2026-03-13"},
{"ticker":"ACGLO","lastDate":"2026-03-13"},{"ticker":"ADAMG","lastDate":"2026-03-13"},
{"ticker":"ADAMH","lastDate":"2026-03-13"},{"ticker":"ADAMI","lastDate":"2026-03-13"},
{"ticker":"ADAMO","lastDate":"2026-03-13"},{"ticker":"AMH-G","lastDate":"2026-03-13"},
{"ticker":"AMH-H","lastDate":"2026-03-13"},{"ticker":"AQNB","lastDate":"2026-03-13"},
{"ticker":"ATH-A","lastDate":"2026-03-13"},{"ticker":"ATH-B","lastDate":"2026-03-13"},
{"ticker":"ATH-D","lastDate":"2026-03-13"},{"ticker":"ATH-E","lastDate":"2026-03-13"},
{"ticker":"ATHS","lastDate":"2026-03-13"},{"ticker":"BIPJ","lastDate":"2026-03-13"},
{"ticker":"BWNB","lastDate":"2026-03-13"},{"ticker":"CUBB","lastDate":"2026-03-13"},
{"ticker":"DLR-J","lastDate":"2026-03-13"},{"ticker":"DLR-K","lastDate":"2026-03-13"},
{"ticker":"DLR-L","lastDate":"2026-03-13"},{"ticker":"ECCV","lastDate":"2026-03-13"},
{"ticker":"ECCW","lastDate":"2026-03-13"},{"ticker":"ECCX","lastDate":"2026-03-13"},
{"ticker":"FITBM","lastDate":"2026-03-13"},{"ticker":"GECCO","lastDate":"2026-03-13"},
{"ticker":"GEGGL","lastDate":"2026-03-13"},{"ticker":"HNNAZ","lastDate":"2026-03-13"},
{"ticker":"HTFC","lastDate":"2026-03-13"},{"ticker":"ICR-A","lastDate":"2026-03-13"},
{"ticker":"KKRS","lastDate":"2026-03-13"},{"ticker":"MBINL","lastDate":"2026-03-13"},
{"ticker":"MBINM","lastDate":"2026-03-13"},{"ticker":"MBINN","lastDate":"2026-03-13"},
{"ticker":"MNSBP","lastDate":"2026-03-13"},{"ticker":"MSBIP","lastDate":"2026-03-13"},
{"ticker":"NSA-A","lastDate":"2026-03-13"},{"ticker":"NTRSO","lastDate":"2026-03-13"},
{"ticker":"OXLCG","lastDate":"2026-03-13"},{"ticker":"OXLCI","lastDate":"2026-03-13"},
{"ticker":"OXLCL","lastDate":"2026-03-13"},{"ticker":"OXLCZ","lastDate":"2026-03-13"},
{"ticker":"PMTU","lastDate":"2026-03-13"},{"ticker":"PNFP-A","lastDate":"2026-03-13"},
{"ticker":"PNFP-B","lastDate":"2026-03-13"},{"ticker":"PSA-F","lastDate":"2026-03-13"},
{"ticker":"PSA-G","lastDate":"2026-03-13"},{"ticker":"PSA-H","lastDate":"2026-03-13"},
{"ticker":"PSA-I","lastDate":"2026-03-13"},{"ticker":"PSA-J","lastDate":"2026-03-13"},
{"ticker":"PSA-K","lastDate":"2026-03-13"},{"ticker":"PSA-L","lastDate":"2026-03-13"},
{"ticker":"PSA-M","lastDate":"2026-03-13"},{"ticker":"PSA-N","lastDate":"2026-03-13"},
{"ticker":"PSA-O","lastDate":"2026-03-13"},{"ticker":"PSA-P","lastDate":"2026-03-13"},
{"ticker":"PSA-Q","lastDate":"2026-03-13"},{"ticker":"PSA-R","lastDate":"2026-03-13"},
{"ticker":"PSA-S","lastDate":"2026-03-13"},{"ticker":"REXR-B","lastDate":"2026-03-13"},
{"ticker":"REXR-C","lastDate":"2026-03-13"},{"ticker":"SACH-A","lastDate":"2026-03-13"},
{"ticker":"SCCD","lastDate":"2026-03-13"},{"ticker":"SCCE","lastDate":"2026-03-13"},
{"ticker":"SCCF","lastDate":"2026-03-13"},{"ticker":"SCCG","lastDate":"2026-03-13"},
{"ticker":"SREA","lastDate":"2026-03-13"},{"ticker":"SSSSL","lastDate":"2026-03-13"},
{"ticker":"STRK","lastDate":"2026-03-13"},{"ticker":"SWKHL","lastDate":"2026-03-13"},
{"ticker":"TDS-U","lastDate":"2026-03-13"},{"ticker":"TDS-V","lastDate":"2026-03-13"},
{"ticker":"TFIN-","lastDate":"2026-03-13"},{"ticker":"TFSA","lastDate":"2026-03-13"},
{"ticker":"TPTA","lastDate":"2026-03-13"},{"ticker":"TRINI","lastDate":"2026-03-13"},
{"ticker":"TRINZ","lastDate":"2026-03-13"},{"ticker":"VLYPN","lastDate":"2026-03-13"},
{"ticker":"VLYPO","lastDate":"2026-03-13"},{"ticker":"VLYPP","lastDate":"2026-03-13"},
{"ticker":"VNO-L","lastDate":"2026-03-13"},{"ticker":"VNO-M","lastDate":"2026-03-13"},
{"ticker":"VNO-N","lastDate":"2026-03-13"},{"ticker":"VNO-O","lastDate":"2026-03-13"},
{"ticker":"WAL-A","lastDate":"2026-03-13"},{"ticker":"WFC-A","lastDate":"2026-03-13"},
{"ticker":"WRB-E","lastDate":"2026-03-13"},{"ticker":"WRB-F","lastDate":"2026-03-13"},
{"ticker":"WRB-G","lastDate":"2026-03-13"},{"ticker":"WRB-H","lastDate":"2026-03-13"},
{"ticker":"WSBCO","lastDate":"2026-03-13"},{"ticker":"CHSCL","lastDate":"2026-03-16"},
{"ticker":"CHSCM","lastDate":"2026-03-16"},{"ticker":"CHSCN","lastDate":"2026-03-16"},
{"ticker":"CHSCO","lastDate":"2026-03-16"},{"ticker":"CHSCP","lastDate":"2026-03-16"},
{"ticker":"JXN-A","lastDate":"2026-03-16"},{"ticker":"MBNKO","lastDate":"2026-03-16"},
{"ticker":"DTK","lastDate":"2026-03-17"},{"ticker":"ECF-A","lastDate":"2026-03-18"},
{"ticker":"GAB-G","lastDate":"2026-03-18"},{"ticker":"GAB-H","lastDate":"2026-03-18"},
{"ticker":"GAB-K","lastDate":"2026-03-18"},{"ticker":"GDV-H","lastDate":"2026-03-18"},
{"ticker":"GDV-K","lastDate":"2026-03-18"},{"ticker":"GGN-B","lastDate":"2026-03-18"},
{"ticker":"GGT-E","lastDate":"2026-03-18"},{"ticker":"GGT-G","lastDate":"2026-03-18"},
{"ticker":"GNT-A","lastDate":"2026-03-18"},{"ticker":"GUT-C","lastDate":"2026-03-18"},
{"ticker":"BCV-A","lastDate":"2026-03-19"},{"ticker":"BW-A","lastDate":"2026-03-19"},
{"ticker":"EFC-D","lastDate":"2026-03-19"},{"ticker":"HPP-C","lastDate":"2026-03-19"},
{"ticker":"IPB","lastDate":"2026-03-19"},{"ticker":"SPE-C","lastDate":"2026-03-19"},
{"ticker":"TRTX-C","lastDate":"2026-03-19"},{"ticker":"ACP-A","lastDate":"2026-03-20"},
{"ticker":"CFG-E","lastDate":"2026-03-20"},{"ticker":"CFG-H","lastDate":"2026-03-20"},
{"ticker":"CFG-I","lastDate":"2026-03-20"},{"ticker":"NEWTP","lastDate":"2026-03-23"},
{"ticker":"PRIF-D","lastDate":"2026-03-23"},{"ticker":"PRIF-J","lastDate":"2026-03-23"},
{"ticker":"PRIF-K","lastDate":"2026-03-23"},{"ticker":"PRIF-L","lastDate":"2026-03-23"},
{"ticker":"GSL-B","lastDate":"2026-03-24"},{"ticker":"HFRO-A","lastDate":"2026-03-24"},
{"ticker":"HFRO-B","lastDate":"2026-03-24"},{"ticker":"FHN-E","lastDate":"2026-03-26"},
{"ticker":"FHN-F","lastDate":"2026-03-26"},{"ticker":"IMPPP","lastDate":"2026-03-26"},
{"ticker":"ENJ","lastDate":"2026-03-27"},{"ticker":"FITBI","lastDate":"2026-03-27"},
{"ticker":"FITBO","lastDate":"2026-03-27"},{"ticker":"FITBP","lastDate":"2026-03-27"},
{"ticker":"MGR","lastDate":"2026-03-27"},{"ticker":"MGRB","lastDate":"2026-03-27"},
{"ticker":"MGRD","lastDate":"2026-03-27"},{"ticker":"MGRE","lastDate":"2026-03-27"},
{"ticker":"AGNCL","lastDate":"2026-03-30"},{"ticker":"AGNCM","lastDate":"2026-03-30"},
{"ticker":"AGNCN","lastDate":"2026-03-30"},{"ticker":"AGNCO","lastDate":"2026-03-30"},
{"ticker":"AGNCP","lastDate":"2026-03-30"},{"ticker":"ALL-B","lastDate":"2026-03-30"},
{"ticker":"ALL-H","lastDate":"2026-03-30"},{"ticker":"ALL-I","lastDate":"2026-03-30"},
{"ticker":"ALL-J","lastDate":"2026-03-30"},{"ticker":"ANG-D","lastDate":"2026-03-30"},
{"ticker":"AXS-E","lastDate":"2026-03-30"},{"ticker":"BANFP","lastDate":"2026-03-30"},
{"ticker":"BHR-B","lastDate":"2026-03-30"},{"ticker":"BHR-D","lastDate":"2026-03-30"},
{"ticker":"CLDT-A","lastDate":"2026-03-30"},{"ticker":"DCBG","lastDate":"2026-03-30"},
{"ticker":"EFC-A","lastDate":"2026-03-30"},{"ticker":"EFC-B","lastDate":"2026-03-30"},
{"ticker":"EFC-C","lastDate":"2026-03-30"},{"ticker":"EPR-C","lastDate":"2026-03-30"},
{"ticker":"EPR-E","lastDate":"2026-03-30"},{"ticker":"EPR-G","lastDate":"2026-03-30"},
{"ticker":"FBRT-E","lastDate":"2026-03-30"},{"ticker":"F-D","lastDate":"2026-03-30"},
{"ticker":"FULTP","lastDate":"2026-03-30"},{"ticker":"IIPR-A","lastDate":"2026-03-30"},
{"ticker":"JPM-C","lastDate":"2026-03-30"},{"ticker":"JPM-D","lastDate":"2026-03-30"},
{"ticker":"JPM-J","lastDate":"2026-03-30"},{"ticker":"JPM-K","lastDate":"2026-03-30"},
{"ticker":"JPM-L","lastDate":"2026-03-30"},{"ticker":"JPM-M","lastDate":"2026-03-30"},
{"ticker":"KTH","lastDate":"2026-03-30"},{"ticker":"LBRDP","lastDate":"2026-03-30"},
{"ticker":"MDV-A","lastDate":"2026-03-30"},{"ticker":"PEB-E","lastDate":"2026-03-30"},
{"ticker":"PEB-F","lastDate":"2026-03-30"},{"ticker":"PEB-H","lastDate":"2026-03-30"},
{"ticker":"RC-C","lastDate":"2026-03-30"},{"ticker":"RC-E","lastDate":"2026-03-30"},
{"ticker":"RLJ-A","lastDate":"2026-03-30"},{"ticker":"SEAL-A","lastDate":"2026-03-30"},
{"ticker":"SEAL-B","lastDate":"2026-03-30"},{"ticker":"SFB","lastDate":"2026-03-30"},
{"ticker":"SLG-I","lastDate":"2026-03-30"},{"ticker":"USB-H","lastDate":"2026-03-30"},
{"ticker":"USB-P","lastDate":"2026-03-30"},{"ticker":"USB-Q","lastDate":"2026-03-30"},
{"ticker":"USB-R","lastDate":"2026-03-30"},{"ticker":"USB-S","lastDate":"2026-03-30"},
{"ticker":"AGNCZ","lastDate":"2026-03-31"},{"ticker":"CMSC","lastDate":"2026-03-31"},
{"ticker":"CMS-C","lastDate":"2026-03-31"},{"ticker":"DTB","lastDate":"2026-03-31"},
{"ticker":"EMP","lastDate":"2026-03-31"},{"ticker":"ENO","lastDate":"2026-03-31"},
{"ticker":"FGSN","lastDate":"2026-03-31"},{"ticker":"GPJA","lastDate":"2026-03-31"},
{"ticker":"HBANL","lastDate":"2026-03-31"},{"ticker":"HBANP","lastDate":"2026-03-31"},
{"ticker":"KTN","lastDate":"2026-03-31"},{"ticker":"MS-A","lastDate":"2026-03-31"},
{"ticker":"MS-E","lastDate":"2026-03-31"},{"ticker":"MS-F","lastDate":"2026-03-31"},
{"ticker":"MS-I","lastDate":"2026-03-31"},{"ticker":"MS-K","lastDate":"2026-03-31"},
{"ticker":"MS-L","lastDate":"2026-03-31"},{"ticker":"MS-O","lastDate":"2026-03-31"},
{"ticker":"MS-P","lastDate":"2026-03-31"},{"ticker":"MS-Q","lastDate":"2026-03-31"},
{"ticker":"SHO-H","lastDate":"2026-03-31"},{"ticker":"SHO-I","lastDate":"2026-03-31"},
{"ticker":"SRG-A","lastDate":"2026-03-31"},{"ticker":"UMBFO","lastDate":"2026-03-31"},
{"ticker":"VIASP","lastDate":"2026-03-31"},{"ticker":"WAFDP","lastDate":"2026-03-31"},
{"ticker":"WTFCN","lastDate":"2026-03-31"},{"ticker":"ADAML","lastDate":"2026-04-01"},
{"ticker":"ADAMM","lastDate":"2026-04-01"},{"ticker":"ADAMN","lastDate":"2026-04-01"},
{"ticker":"ACR-C","lastDate":"2026-04-02"},{"ticker":"ACR-D","lastDate":"2026-04-02"},
{"ticker":"ADAMZ","lastDate":"2026-04-02"},{"ticker":"AGM-D","lastDate":"2026-04-02"},
{"ticker":"AGM-E","lastDate":"2026-04-02"},{"ticker":"AGM-F","lastDate":"2026-04-02"},
{"ticker":"AGM-G","lastDate":"2026-04-02"},{"ticker":"AHRT-A","lastDate":"2026-04-02"},
{"ticker":"AIZN","lastDate":"2026-04-02"},{"ticker":"ATLCZ","lastDate":"2026-04-02"},
{"ticker":"BAC-K","lastDate":"2026-04-02"},{"ticker":"BC-C","lastDate":"2026-04-02"},
{"ticker":"BFS-D","lastDate":"2026-04-02"},{"ticker":"BFS-E","lastDate":"2026-04-02"},
{"ticker":"BNH","lastDate":"2026-04-02"},{"ticker":"CDZIP","lastDate":"2026-04-02"},
{"ticker":"DX-C","lastDate":"2026-04-02"},{"ticker":"ETI-","lastDate":"2026-04-02"},
{"ticker":"FRT-C","lastDate":"2026-04-02"},{"ticker":"GNL-A","lastDate":"2026-04-02"},
{"ticker":"GNL-B","lastDate":"2026-04-02"},{"ticker":"GNL-D","lastDate":"2026-04-02"},
{"ticker":"GNL-E","lastDate":"2026-04-02"},{"ticker":"GPMT-A","lastDate":"2026-04-02"},
{"ticker":"HOVNP","lastDate":"2026-04-02"},{"ticker":"KIM-L","lastDate":"2026-04-02"},
{"ticker":"KIM-M","lastDate":"2026-04-02"},{"ticker":"LFMDP","lastDate":"2026-04-02"},
{"ticker":"LFT-A","lastDate":"2026-04-02"},{"ticker":"NHPAP","lastDate":"2026-04-02"},
{"ticker":"NHPBP","lastDate":"2026-04-02"},{"ticker":"RWT-A","lastDate":"2026-04-02"},
{"ticker":"RZC","lastDate":"2026-04-02"},{"ticker":"XOMAO","lastDate":"2026-04-02"},
{"ticker":"XOMAP","lastDate":"2026-04-02"},{"ticker":"DBRG-H","lastDate":"2026-04-09"},
{"ticker":"DBRG-I","lastDate":"2026-04-09"},{"ticker":"DBRG-J","lastDate":"2026-04-09"},
{"ticker":"METCI","lastDate":"2026-04-15"},{"ticker":"METCZ","lastDate":"2026-04-15"},
{"ticker":"PFXNZ","lastDate":"2026-04-15"},{"ticker":"FHN-C","lastDate":"2026-04-16"},
{"ticker":"REGCO","lastDate":"2026-04-16"},{"ticker":"REGCP","lastDate":"2026-04-16"},
{"ticker":"TCPA","lastDate":"2026-04-16"},{"ticker":"PSEC-A","lastDate":"2026-04-21"},
{"ticker":"SR-A","lastDate":"2026-04-24"},{"ticker":"CICC","lastDate":"2026-06-11"},
{"ticker":"CICB","lastDate":"2026-06-12"},
]

_MONTHLY_RAW = [
{"ticker":"ADC-A","lastDate":"2026-02-20"},{"ticker":"ARR-C","lastDate":"2026-02-13"},
{"ticker":"BPOPM","lastDate":"2026-02-15"},{"ticker":"CCID","lastDate":"2026-02-17"},
{"ticker":"ECCC","lastDate":"2026-02-09"},{"ticker":"ECC-D","lastDate":"2026-02-09"},
{"ticker":"ECCF","lastDate":"2026-02-09"},{"ticker":"EICA","lastDate":"2026-02-09"},
{"ticker":"EICC","lastDate":"2026-02-09"},{"ticker":"GJO","lastDate":"2026-02-13"},
{"ticker":"GJP","lastDate":"2026-02-13"},{"ticker":"GJR","lastDate":"2026-02-13"},
{"ticker":"GJS","lastDate":"2026-02-13"},{"ticker":"GJT","lastDate":"2026-02-27"},
{"ticker":"GOODN","lastDate":"2026-02-18"},{"ticker":"GOODO","lastDate":"2026-02-18"},
{"ticker":"LANDO","lastDate":"2026-02-18"},{"ticker":"LANDP","lastDate":"2026-02-18"},
{"ticker":"OCCIM","lastDate":"2026-02-13"},{"ticker":"OCCIN","lastDate":"2026-02-13"},
{"ticker":"OCCIO","lastDate":"2026-02-13"},{"ticker":"OXLCN","lastDate":"2026-02-13"},
{"ticker":"OXLCO","lastDate":"2026-02-13"},{"ticker":"OXLCP","lastDate":"2026-02-13"},
{"ticker":"PDPA","lastDate":"2026-02-15"},{"ticker":"SPMA","lastDate":"2026-02-15"},
{"ticker":"SPME","lastDate":"2026-02-15"},
]

# Build a fast-lookup dict: ticker -> (lastDate, period)
_DIV_CALENDAR = {}
for _item in _QUARTERLY_RAW:
    _DIV_CALENDAR[_item['ticker'].upper()] = (_item['lastDate'], 'quarterly')
for _item in _MONTHLY_RAW:
    _DIV_CALENDAR[_item['ticker'].upper()] = (_item['lastDate'], 'monthly')

def _div_market_closed(d):
    return d.weekday() >= 5 or d in _DIV_HOLIDAYS

def _div_adjust_date(d):
    """Move back to last trading day if d is weekend/holiday."""
    while _div_market_closed(d):
        d -= timedelta(days=1)
    return d

def _compute_next_div_date(last_date_str, period):
    """Return next future ex-dividend date (adjusted) from today."""
    try:
        last = date.fromisoformat(last_date_str)
    except Exception:
        return None
    interval = 3 if period == 'quarterly' else 1
    today = date.today()
    for n in range(1, 200):
        projected = _add_months(last, n * interval)
        adjusted  = _div_adjust_date(projected)
        if adjusted >= today:
            return adjusted
    return None

def _pref_div_border_color(days_left):
    """Return border color for preferred card based on days until next div."""
    if days_left is None:
        return '#3b82f6'  # BL2 default
    if days_left <= 1:
        return '#ef4444'  # RED  — today or tomorrow
    if days_left <= 15:
        return '#f59e0b'  # AMBER — ≤ 15 days
    if days_left <= 30:
        return '#a78bfa'  # PURPLE — ≤ 1 month
    if days_left > 90:
        return '#4b5563'  # GRAY — > 3 months
    return '#3b82f6'      # BL2 — 1-3 months (default)

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

def fmt_signed_pct(p):
    if p is None: return None
    try:
        return f"{float(p):+.2f}%"
    except:
        return None

def clean(v):
    if v is None: return ''
    s = str(v).strip()
    return '' if s.lower() in ('none','null','nan','#n/a','#value!') else s

def apply_dark_window_chrome(win):
    if os.name != 'nt':
        return
    try:
        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id()) or win.winfo_id()
        value = ctypes.c_int(1)
        for attr in (20, 19):
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_void_p(hwnd), ctypes.c_int(attr),
                    ctypes.byref(value), ctypes.sizeof(value))
            except Exception:
                pass
    except Exception:
        pass


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
        self._cef_nav_tickers = set()
        self._cef_history_last_signature = None
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
        self._trade_win = None
        self._cat_menu = None
        self._cat_menu_job = None
        self._cat_close_job = None
        self._cef_pricing_fetching = set()
        self._cef_detail_refreshing = False

        self.root = tk.Tk()
        self.root.title("Hammer Pro — Preferred Lookup v8")
        self.root.geometry(f"{self.W}x{self.H}")
        self.root.minsize(300, 450)
        self.root.configure(bg=BG)
        self.root.option_add('*Background', BG)
        self.root.option_add('*Foreground', TX)
        self.root.option_add('*Entry.Background', BG2)
        self.root.option_add('*Text.Background', BG2)
        self.root.option_add('*Listbox.Background', BG)
        self.root.after(80, lambda: apply_dark_window_chrome(self.root))
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
            self._start_cef_detail_cache_refresh()

        self.root.mainloop()

    def _style_window(self, win):
        win.configure(bg=BG)
        win.after(80, lambda w=win: apply_dark_window_chrome(w))
        return win

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
                            'nav', 'discount', 'navDate', 'fundName',
                            'strategy', 'categoryName', 'cefSummaryAsOf',
                            'price52Avg', 'nav52Avg', 'discount52Avg',
                            'price52High', 'nav52High', 'discount52High',
                            'price52Low', 'nav52Low', 'discount52Low',
                            'zScore3m', 'zScore6m', 'zScore1y',
                            'pdAvg6m', 'pdAvg1y', 'pdAvg3y', 'pdAvg5y',
                            'pricingInfoDate', 'zScoreDate',
                            'pricingInfoPeriod', 'pricingInfoError'):
                    if key in value:
                        row[key] = value.get(key)
            out[s] = row
        return out

    def _cef_sectors(self, sym):
        return self.cef.get(sym.upper(), {}).get('sectors', [])

    def _cef_index_items_from_value(self, value):
        out = []
        if isinstance(value, list):
            raw_items = value
        else:
            raw_items = re.split(r'[,;/\n]+', str(value or ''))
        for item in raw_items:
            text = clean(item).upper()
            if not text:
                continue
            if re.fullmatch(r'[A-Z0-9.\-]{2,14}', text) and text not in out:
                out.append(text)
        return out

    def _cef_label_items_from_value(self, value):
        out = []
        if isinstance(value, list):
            raw_items = value
        else:
            raw_items = re.split(r'[,;\n]+', str(value or ''))
        for item in raw_items:
            text = clean(item)
            if not text:
                continue
            if re.fullmatch(r'[A-Z0-9.\-]{2,14}', text.upper()):
                text = text.upper()
            if text not in out:
                out.append(text)
        return out

    def _cef_indexes(self, sym, nav_info=None, cef_row=None):
        row = cef_row if isinstance(cef_row, dict) else self.cef.get(sym.upper(), {})
        info = nav_info if isinstance(nav_info, dict) else {}
        out = []
        for source in (
            row.get('sectors'), row.get('indexes'), row.get('index'),
            info.get('sectors'), info.get('indexes'), info.get('index'),
            row.get('categoryName'), info.get('categoryName'),
            row.get('strategy'), info.get('strategy'),
        ):
            for item in self._cef_label_items_from_value(source):
                if item not in out:
                    out.append(item)
        return out

    def _cef_category_groups_for_symbol(self, sym):
        ticker = clean(sym).upper()
        if not ticker:
            return []
        groups = []
        cats = getattr(self, '_cef_cats', {}) or {}
        for group, items in cats.items():
            label = clean(group)
            if not label or label == 'Belirtilmemiş':
                continue
            for item_sym, _ in items or []:
                if clean(item_sym).upper() == ticker:
                    if label not in groups:
                        groups.append(label)
                    break
        try:
            groups.sort(key=self._cef_category_sort_key)
        except Exception:
            groups.sort()
        return groups

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

    def _next_div_for_pref(self, sym):
        """Return (next_date, days_left, period) from calendar data or pref overrides."""
        if not sym:
            return None, None, None
        s = sym.upper()
        p = self.pref.get(s, {})
        # User override in pref_data takes priority
        div_date = p.get('divDate')
        div_freq = p.get('divFreq', 'quarterly')
        if not div_date:
            # Fall back to built-in calendar
            cal = _DIV_CALENDAR.get(s)
            if not cal:
                return None, None, None
            div_date, div_freq = cal
        nxt = _compute_next_div_date(div_date, div_freq)
        if nxt is None:
            return None, None, div_freq
        days_left = (nxt - date.today()).days
        return nxt, days_left, div_freq

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

    def _parse_source_date(self, value):
        s = clean(value)
        if not s:
            return None
        s = re.sub(r'^\s*as\s+of\s+', '', s, flags=re.I).strip()
        if 'T' in s:
            s = s.split('T', 1)[0]
        if ' ' in s:
            s = s.split(' ', 1)[0]
        for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                pass
        return self._parse_date_value(s)

    def _source_date_iso(self, *values):
        dates = [self._parse_source_date(v) for v in values]
        dates = [d for d in dates if d is not None]
        return max(dates).isoformat() if dates else ''

    def _epoch_market_date_iso(self, ts, tz_name=''):
        try:
            ts = float(ts)
        except Exception:
            return ''
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(clean(tz_name) or 'America/New_York')
            return datetime.fromtimestamp(ts, tz).date().isoformat()
        except Exception:
            return datetime.fromtimestamp(ts).date().isoformat()

    def _decode_http_body(self, raw, headers=None):
        encoding = ''
        try:
            encoding = clean(headers.get('Content-Encoding')).lower()
        except Exception:
            encoding = ''
        try:
            if raw[:2] == b'\x1f\x8b' or 'gzip' in encoding:
                raw = gzip.decompress(raw)
            elif 'deflate' in encoding:
                try:
                    raw = zlib.decompress(raw)
                except Exception:
                    raw = zlib.decompress(raw, -zlib.MAX_WBITS)
        except Exception:
            pass
        return raw.decode('utf-8', 'ignore')

    def _read_url(self, url, timeout=12):
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            headers = resp.headers
        return self._decode_http_body(raw, headers)

    def _fetch_yahoo_price_info(self, sym, preferred=False):
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
                    ts = meta.get('regularMarketTime')
                    if ts is None:
                        timestamps = (result or {}).get('timestamp') or []
                        ts = timestamps[-1] if timestamps else None
                    return {
                        'symbol': candidate,
                        'price': float(price),
                        'priceDate': self._epoch_market_date_iso(
                            ts, meta.get('exchangeTimezoneName')),
                    }
                errors.append(f"{candidate}: fiyat yok")
            except Exception as exc:
                errors.append(f"{candidate}: {exc}")
        raise RuntimeError('; '.join(errors) or f"{sym}: Yahoo fiyat bulunamadı")

    def _fetch_yahoo_price(self, sym, preferred=False):
        info = self._fetch_yahoo_price_info(sym, preferred=preferred)
        return info.get('symbol'), info.get('price')

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

    def _apply_pref_market_data(self, sym, price, yahoo_sym=None, price_date=None):
        p = dict(self.pref.get(sym, {}))
        p['lastPrice'] = round(float(price), 4)
        p['lastPriceDate'] = clean(price_date) or date.today().isoformat()
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

    def _apply_cef_market_data(self, sym, price, yahoo_sym=None, price_date=None):
        row = dict(self.cef.get(sym, {'sectors': []}))
        row['lastPrice'] = round(float(price), 4)
        row['lastPriceDate'] = clean(price_date) or date.today().isoformat()
        if yahoo_sym:
            row['yahooSymbol'] = yahoo_sym
        self.cef[sym] = row
        return row

    def _cef_record_list(self, payload):
        stack = [payload]
        seen = 0
        while stack and seen < 30:
            seen += 1
            item = stack.pop(0)
            if isinstance(item, list):
                if any(isinstance(x, dict) for x in item):
                    return item
                continue
            if not isinstance(item, dict):
                continue
            for key in ('data', 'Data', 'funds', 'Funds', 'DailyPricing',
                        'rows', 'Rows', 'items', 'Items', 'result', 'Result'):
                if key in item:
                    stack.append(item.get(key))
        return []

    def _cef_connect_recent_failure(self):
        meta = _load('cef_connect_fetch.json')
        if not isinstance(meta, dict):
            return False
        if meta.get('period') != self._turkey_refresh_period():
            return False
        if meta.get('status') != 'error':
            return False
        try:
            return (time.time() - float(meta.get('updatedTs') or 0)) < CEF_CONNECT_RETRY_SECONDS
        except Exception:
            return True

    def _save_cef_connect_fetch_meta(self, status, count=0, error=''):
        _save('cef_connect_fetch.json', {
            'period': self._turkey_refresh_period(),
            'status': status,
            'count': int(count or 0),
            'error': clean(error)[:240],
            'updatedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
            'updatedTs': time.time(),
        })

    def _fetch_cef_connect_data_legacy(self):
        """Tek istekle cefconnect.com'dan tüm CEF'lerin NAV ve Discount verilerini çeker.
        1 günde 1 kez çağrılır; ban riski minimumdur."""
        # cefconnect.com'un kendi frontend'i tarafından kullanılan JSON endpoint
        url = "https://www.cefconnect.com/api/v3/pricingdata"
        headers_override = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.cefconnect.com/',
            'Origin': 'https://www.cefconnect.com',
        }
        req = urllib.request.Request(url, headers=headers_override)
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read()
            headers = resp.headers
        text = self._decode_http_body(raw, headers)
        records = self._cef_record_list(json.loads(text))
        # API farklı sarmalama yapısı dönebilir
        if isinstance(records, dict):
            records = (records.get('data') or records.get('Data') or
                       records.get('funds') or records.get('Funds') or [])
        def _get(rec, *names):
            if not isinstance(rec, dict): return None
            low = {str(k).lower(): k for k in rec}
            for n in names:
                if n in rec: return rec[n]
                k = low.get(str(n).lower())
                if k is not None: return rec[k]
            return None

        out = {}
        for rec in (records if isinstance(records, list) else []):
            ticker = clean(
                _get(rec, 'Ticker', 'ticker', 'Symbol', 'symbol') or ''
            ).upper()
            if not ticker:
                continue
            nav = _get(rec, 'NAV', 'nav', 'NetAssetValue', 'netAssetValue')
            discount = _get(rec, 'PremiumDiscount', 'premiumDiscount',
                           'Discount', 'discount', 'DiscountPremium')
            price = _get(rec, 'Price', 'LastPrice', 'ClosingPrice', 'MarketPrice')
            nav_date = self._source_date_iso(
                _get(rec, 'NAVDate', 'navDate', 'PriceDate', 'priceDate') or '')
            entry = {}
            parsed_nav = self._parse_cef_number(nav)
            parsed_disc = self._parse_cef_number(discount, percent=True)
            parsed_price = self._parse_cef_number(price)
            if parsed_nav is not None:   entry['nav'] = parsed_nav
            if parsed_disc is not None:  entry['discount'] = parsed_disc
            if parsed_price is not None: entry['lastPrice'] = parsed_price
            if nav_date:                 entry['navDate'] = nav_date

            # Ek alanlar (varsa)
            fund_name = clean(_get(rec, 'FundName', 'fundName', 'Fund'))
            strategy = clean(_get(rec, 'Strategy', 'strategy', 'Category', 'category',
                                  'CategoryName', 'categoryName'))
            if fund_name: entry['fundName'] = fund_name
            if strategy:
                entry['strategy'] = strategy
                entry['sectors'] = [strategy]

            as_of = clean(_get(rec, 'AsOfDate', 'asOfDate', 'SummaryAsOf',
                               'LastUpdated', 'lastUpdated'))
            if as_of:
                entry['cefSummaryAsOf'] = f"As of {as_of}" if not as_of.lower().startswith('as of') else as_of

            # 52-week, z-score, pdAvg (API destekliyorsa)
            _52w = [
                (('SharePrice52WkHigh','Price52WkHigh','Price52WeekHigh','price52High'), 'price52High'),
                (('SharePrice52WkLow','Price52WkLow','Price52WeekLow','price52Low'), 'price52Low'),
                (('SharePrice52WkAvg','Price52WkAvg','Price52WeekAvg','price52Avg'), 'price52Avg'),
                (('NAV52WkHigh','Nav52WkHigh','NAV52WeekHigh','nav52High'), 'nav52High'),
                (('NAV52WkLow','Nav52WkLow','NAV52WeekLow','nav52Low'), 'nav52Low'),
                (('NAV52WkAvg','Nav52WkAvg','NAV52WeekAvg','nav52Avg'), 'nav52Avg'),
                (('Discount52WkHigh','Disc52WkHigh','Discount52WeekHigh','discount52High'), 'discount52High'),
                (('Discount52WkLow','Disc52WkLow','Discount52WeekLow','discount52Low'), 'discount52Low'),
                (('Discount52WkAvg','Disc52WkAvg','Discount52WeekAvg','discount52Avg'), 'discount52Avg'),
            ]
            for api_names, local_key in _52w:
                v = self._parse_cef_number(_get(rec, *api_names))
                if v is not None: entry[local_key] = v

            for api_names, local_key in [
                (('ZScore3Mo','ZScore3Month','zScore3m'), 'zScore3m'),
                (('ZScore6Mo','ZScore6Month','zScore6m'), 'zScore6m'),
                (('ZScore1Yr','ZScore1Year','zScore1y'), 'zScore1y'),
            ]:
                v = self._parse_cef_number(_get(rec, *api_names))
                if v is not None: entry[local_key] = v

            for api_names, local_key in [
                (('AvgDiscount6Mo','AvgDiscount6Month','pdAvg6m','AvgPremiumDiscount6Mo'), 'pdAvg6m'),
                (('AvgDiscount1Yr','AvgDiscount1Year','pdAvg1y','AvgPremiumDiscount1Yr'), 'pdAvg1y'),
                (('AvgDiscount3Yr','AvgDiscount3Year','pdAvg3y','AvgPremiumDiscount3Yr'), 'pdAvg3y'),
                (('AvgDiscount5Yr','AvgDiscount5Year','pdAvg5y','AvgPremiumDiscount5Yr'), 'pdAvg5y'),
            ]:
                v = self._parse_cef_number(_get(rec, *api_names), percent=True)
                if v is not None: entry[local_key] = v

            if entry:
                out[ticker] = entry
        return out

    # ── cefdata.xlsx okuyucu ─────────────────────────────────────────────
    def _fetch_cef_connect_data(self):
        """Fetch all CEF daily price/NAV/discount rows with one CEFConnect request."""
        props = [
            'Ticker', 'Price', 'NAV', 'NAVPublished', 'Discount', 'LastUpdated',
            'FundName', 'Category', 'Strategy',
            'SharePrice52WkHigh', 'SharePrice52WkLow', 'SharePrice52WkAvg',
            'NAV52WkHigh', 'NAV52WkLow', 'NAV52WkAvg',
            'Discount52WkHigh', 'Discount52WkLow', 'Discount52WkAvg',
            'ZScore3Mo', 'ZScore6Mo', 'ZScore1Yr',
            'AvgDiscount6Mo', 'AvgDiscount1Yr', 'AvgDiscount3Yr', 'AvgDiscount5Yr',
        ]
        query = urllib.parse.urlencode({
            'props': ','.join(props),
            '_': str(int(time.time() * 1000)),
        }, safe=',')
        url = f"https://www.cefconnect.com/api/v3/DailyPricing?{query}"
        req = urllib.request.Request(url, headers={
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/124.0.0.0 Safari/537.36'),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.cefconnect.com/fundscreener/',
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            headers = resp.headers
        records = self._cef_record_list(json.loads(self._decode_http_body(raw, headers)))

        def get_any(rec, *names):
            if not isinstance(rec, dict):
                return None
            lowered = {str(k).lower(): k for k in rec.keys()}
            for name in names:
                if name in rec:
                    return rec.get(name)
                key = lowered.get(str(name).lower())
                if key is not None:
                    return rec.get(key)
            return None

        out = {}
        for rec in (records if isinstance(records, list) else []):
            ticker = clean(get_any(rec, 'Ticker', 'Symbol', 'ticker', 'symbol')).upper()
            if not ticker:
                continue
            entry = {}
            price = self._parse_cef_number(get_any(
                rec, 'Price', 'LastPrice', 'ClosingPrice', 'MarketPrice'))
            nav = self._parse_cef_number(get_any(
                rec, 'NAV', 'Nav', 'NetAssetValue', 'netAssetValue'))
            discount = self._parse_cef_number(get_any(
                rec, 'Discount', 'PremiumDiscount', 'DiscountPremium',
                'premiumDiscount', 'discountPremium'), percent=True)
            nav_date = self._source_date_iso(
                get_any(rec, 'NAVPublished', 'NAVDate', 'NavDate', 'AsOfDate'))
            price_date = self._source_date_iso(
                get_any(rec, 'LastUpdated', 'PriceDate', 'asOfDate'))
            if price is not None:
                entry['lastPrice'] = price
                if price_date:
                    entry['lastPriceDate'] = price_date
            if nav is not None:
                entry['nav'] = nav
            if discount is not None:
                entry['discount'] = discount

            if nav_date:
                entry['navDate'] = nav_date
            if price_date:
                entry['cefConnectUpdated'] = price_date

            # Ek alanlar (varsa tek istekle al, ban riski yok)
            fund_name = clean(get_any(rec, 'FundName', 'fundName', 'Fund'))
            strategy = clean(get_any(rec, 'Strategy', 'strategy',
                                     'Category', 'category', 'CategoryName'))
            if fund_name:
                entry['fundName'] = fund_name
            if strategy:
                entry['strategy'] = strategy
                entry['sectors'] = [strategy]

            as_of = self._source_date_iso(
                get_any(rec, 'AsOfDate', 'asOfDate', 'SummaryAsOf') or '')
            if as_of:
                entry['cefSummaryAsOf'] = f"As of {as_of}"

            # 52-week data
            for api_names, local_key in [
                (('SharePrice52WkHigh','Price52WkHigh','Price52WeekHigh'), 'price52High'),
                (('SharePrice52WkLow','Price52WkLow','Price52WeekLow'), 'price52Low'),
                (('SharePrice52WkAvg','Price52WkAvg','Price52WeekAvg'), 'price52Avg'),
                (('NAV52WkHigh','Nav52WkHigh','NAV52WeekHigh'), 'nav52High'),
                (('NAV52WkLow','Nav52WkLow','NAV52WeekLow'), 'nav52Low'),
                (('NAV52WkAvg','Nav52WkAvg','NAV52WeekAvg'), 'nav52Avg'),
                (('Discount52WkHigh','Disc52WkHigh','Discount52WeekHigh'), 'discount52High'),
                (('Discount52WkLow','Disc52WkLow','Discount52WeekLow'), 'discount52Low'),
                (('Discount52WkAvg','Disc52WkAvg','Discount52WeekAvg'), 'discount52Avg'),
            ]:
                v = self._parse_cef_number(get_any(rec, *api_names))
                if v is not None:
                    entry[local_key] = v

            # Z-Scores
            for api_names, local_key in [
                (('ZScore3Mo','ZScore3Month','zScore3m'), 'zScore3m'),
                (('ZScore6Mo','ZScore6Month','zScore6m'), 'zScore6m'),
                (('ZScore1Yr','ZScore1Year','zScore1y'), 'zScore1y'),
            ]:
                v = self._parse_cef_number(get_any(rec, *api_names))
                if v is not None:
                    entry[local_key] = v

            # P/D Averages
            for api_names, local_key in [
                (('AvgDiscount6Mo','AvgDiscount6Month','pdAvg6m'), 'pdAvg6m'),
                (('AvgDiscount1Yr','AvgDiscount1Year','pdAvg1y'), 'pdAvg1y'),
                (('AvgDiscount3Yr','AvgDiscount3Year','pdAvg3y'), 'pdAvg3y'),
                (('AvgDiscount5Yr','AvgDiscount5Year','pdAvg5y'), 'pdAvg5y'),
            ]:
                v = self._parse_cef_number(get_any(rec, *api_names), percent=True)
                if v is not None:
                    entry[local_key] = v

            if entry:
                out[ticker] = entry

        if not out:
            raise RuntimeError('CEFConnect DailyPricing returned no usable rows')
        return out

    def _html_text(self, value):
        text = re.sub(r'<[^>]+>', ' ', value or '')
        text = html_lib.unescape(text)
        return re.sub(r'\s+', ' ', text).strip()

    def _extract_html_table_pairs(self, html, table_id):
        m = re.search(
            rf'<table[^>]+id=["\']{re.escape(table_id)}["\'][^>]*>(.*?)</table>',
            html, re.I | re.S)
        if not m:
            return {}
        out = {}
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(1), re.I | re.S):
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.I | re.S)
            if len(cells) < 2:
                continue
            label = self._html_text(cells[0])
            value = self._html_text(cells[1])
            if not label or label.lower() in ('period', 'avg discount', 'zstat'):
                continue
            out[label] = value
        return out

    def _extract_html_table_rows(self, html, table_id):
        m = re.search(
            rf'<table[^>]+id=["\']{re.escape(table_id)}["\'][^>]*>(.*?)</table>',
            html, re.I | re.S)
        if not m:
            return []
        rows = []
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(1), re.I | re.S):
            cells = [
                self._html_text(cell)
                for cell in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.I | re.S)
            ]
            cells = [cell for cell in cells if cell]
            if cells:
                rows.append(cells)
        return rows

    def _extract_html_span(self, html, span_id):
        m = re.search(
            rf'<span[^>]+id=["\']{re.escape(span_id)}["\'][^>]*>(.*?)</span>',
            html, re.I | re.S)
        if not m:
            return ''
        text = self._html_text(m.group(1))
        return re.sub(r'^\s*as\s+of\s+', '', text, flags=re.I).strip()

    def _cef_period_key(self, label):
        text = clean(label).lower()
        if text.startswith('3 month'):
            return '3m'
        if text.startswith('6 month'):
            return '6m'
        if text.startswith('1 year'):
            return '1y'
        if text.startswith('3 year'):
            return '3y'
        if text.startswith('5 year'):
            return '5y'
        return ''

    def _fetch_cef_pricing_info(self, sym):
        ticker = clean(sym).upper()
        if not ticker:
            return {}
        html = self._read_url(f"https://www.cefconnect.com/fund/{urllib.parse.quote(ticker)}", timeout=20)
        summary_rows = self._extract_html_table_rows(
            html, 'ContentPlaceHolder1_cph_main_cph_main_SummaryGrid')
        discount_rows = self._extract_html_table_pairs(
            html, 'ContentPlaceHolder1_cph_main_cph_main_ucPricing_DiscountGrid')
        z_rows = self._extract_html_table_pairs(
            html, 'ContentPlaceHolder1_cph_main_cph_main_ucPricing_ZScoreGridView')
        info = {}

        summary_date = self._extract_html_span(
            html, 'ContentPlaceHolder1_cph_main_cph_main_AsOfLabel')
        if summary_date:
            if not summary_date.lower().startswith('as of'):
                summary_date = f"As of {summary_date}"
            info['cefSummaryAsOf'] = summary_date

        summary_keys = {
            'current': ('lastPrice', 'nav', 'discount'),
            '52 wk avg': ('price52Avg', 'nav52Avg', 'discount52Avg'),
            '52 wk high': ('price52High', 'nav52High', 'discount52High'),
            '52 wk low': ('price52Low', 'nav52Low', 'discount52Low'),
        }
        for row in summary_rows:
            if len(row) < 4:
                continue
            key = clean(row[0]).lower()
            fields = summary_keys.get(key)
            if not fields:
                continue
            price_v = self._parse_cef_number(row[1])
            nav_v = self._parse_cef_number(row[2])
            pd_v = self._parse_cef_number(row[3], percent=True)
            for field, value in zip(fields, (price_v, nav_v, pd_v)):
                if value is not None:
                    info[field] = value

        for label, value in discount_rows.items():
            key = {
                '6m': 'pdAvg6m',
                '1y': 'pdAvg1y',
                '3y': 'pdAvg3y',
                '5y': 'pdAvg5y',
            }.get(self._cef_period_key(label))
            num = self._parse_cef_number(value, percent=True)
            if key and num is not None:
                info[key] = num
        for label, value in z_rows.items():
            key = {
                '3m': 'zScore3m',
                '6m': 'zScore6m',
                '1y': 'zScore1y',
            }.get(self._cef_period_key(label))
            num = self._parse_cef_number(value)
            if key and num is not None:
                info[key] = num

        disc_date = self._extract_html_span(
            html, 'ContentPlaceHolder1_cph_main_cph_main_ucPricing_DiscAsOfLabel')
        z_date = self._extract_html_span(
            html, 'ContentPlaceHolder1_cph_main_cph_main_ucPricing_zScoreAsOfLabel')
        if disc_date:
            info['pricingInfoDate'] = disc_date
        if z_date:
            info['zScoreDate'] = z_date
        if info:
            info['pricingInfoPeriod'] = self._turkey_refresh_period()
        return info

    def _cef_pricing_info_needed(self, nav_info):
        if not isinstance(nav_info, dict):
            return True
        keys = ('price52Avg', 'nav52Avg', 'discount52Avg',
                'price52High', 'nav52High', 'discount52High',
                'price52Low', 'nav52Low', 'discount52Low',
                'pdAvg6m', 'pdAvg1y', 'pdAvg3y', 'pdAvg5y',
                'zScore3m', 'zScore6m', 'zScore1y')
        if all(nav_info.get(k) is not None for k in keys):
            return False
        if nav_info.get('pricingInfoError') and nav_info.get('pricingInfoPeriod') == self._turkey_refresh_period():
            return False
        return True

    def _cef_detail_cache_tickers(self):
        tickers = set(self._cef_tickers())
        for sym, row in (self.cef or {}).items():
            if self._cef_indexes(sym, cef_row=row):
                tickers.add(clean(sym).upper())
        return sorted(t for t in tickers if t)

    def _start_cef_detail_cache_refresh(self):
        if getattr(self, '_cef_detail_refreshing', False):
            return
        cache = getattr(self, '_cef_nav_cache', None) or self._load_nav_cache()
        self._cef_nav_cache = cache
        tickers = [
            sym for sym in self._cef_detail_cache_tickers()
            if self._cef_pricing_info_needed(cache.get(sym, {}))
        ]
        if not tickers:
            return
        self._cef_detail_refreshing = True

        def worker(items):
            cache_local = dict(getattr(self, '_cef_nav_cache', {}) or self._load_nav_cache())
            changed = 0
            for i, ticker in enumerate(items, start=1):
                try:
                    detail = self._fetch_cef_pricing_info(ticker)
                except Exception as exc:
                    detail = {
                        'pricingInfoError': clean(exc)[:160],
                        'pricingInfoPeriod': self._turkey_refresh_period(),
                    }
                if detail:
                    row = dict(cache_local.get(ticker, {}))
                    row.update(detail)
                    if 'pricingInfoError' not in detail:
                        row.pop('pricingInfoError', None)
                    cache_local[ticker] = row
                    changed += 1
                if changed and changed % CEF_DETAIL_SAVE_EVERY == 0:
                    cache_local = self._save_nav_cache(cache_local, source='cefconnect')
                    self._cef_nav_cache = cache_local
                if i < len(items):
                    time.sleep(CEF_DETAIL_FETCH_DELAY_SECONDS)
            if changed:
                cache_local = self._save_nav_cache(cache_local, source='cefconnect')
            self.root.after(0, lambda c=cache_local: self._finish_cef_detail_cache_refresh(c))

        threading.Thread(target=worker, args=(tickers,), daemon=True).start()

    def _finish_cef_detail_cache_refresh(self, cache):
        self._cef_detail_refreshing = False
        if isinstance(cache, dict):
            self._cef_nav_cache = cache
            self._cef_nav_tickers = set(cache.keys())
            self._all_tickers = set(self.pref.keys()) | self._cef_tickers()
            self._build_categories()
        if self.current and self._is_cef_symbol(self.current):
            self.select(self.current)

    def _start_cef_pricing_info_fetch(self, sym):
        ticker = clean(sym).upper()
        if not ticker or ticker in self._cef_pricing_fetching:
            return
        self._cef_pricing_fetching.add(ticker)

        def worker():
            try:
                detail = self._fetch_cef_pricing_info(ticker)
                error = '' if detail else 'pricing info bulunamadi'
            except Exception as exc:
                detail = {}
                error = clean(exc)
            self.root.after(0, lambda: self._finish_cef_pricing_info_fetch(ticker, detail, error))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_cef_pricing_info_fetch(self, sym, detail, error=''):
        self._cef_pricing_fetching.discard(sym)
        cache = dict(getattr(self, '_cef_nav_cache', {}) or self._load_nav_cache())
        row = dict(cache.get(sym, {}))
        if detail:
            row.update(detail)
            row.pop('pricingInfoError', None)
        elif error:
            row['pricingInfoError'] = error[:160]
            row['pricingInfoPeriod'] = self._turkey_refresh_period()
        if row:
            cache[sym] = row
            self._cef_nav_cache = self._save_nav_cache(cache, source='cefconnect')
            self._cef_nav_tickers = set(self._cef_nav_cache.keys())
            self._all_tickers = set(self.pref.keys()) | self._cef_tickers()
        if self.current == sym:
            self.select(sym)

    def _cef_data_path(self):
        """Uygulama klasorundeki cefdata.xlsx yolunu bulur."""
        bases = []
        if getattr(sys, 'frozen', False):
            bases.append(os.path.dirname(os.path.abspath(sys.executable)))
        bases.extend([
            os.path.dirname(os.path.abspath(sys.argv[0])),
            os.path.dirname(os.path.abspath(__file__)),
            os.getcwd(),
        ])
        seen = set()
        for base in bases:
            if not base or base in seen:
                continue
            seen.add(base)
            p = os.path.join(base, 'cefdata.xlsx')
            if os.path.exists(p):
                return p
        raise FileNotFoundError('cefdata.xlsx bulunamadi')

    def _cef_source_meta(self, path):
        st = os.stat(path)
        return {
            'sourcePath': os.path.abspath(path),
            'sourceMtime': st.st_mtime,
            'sourceSize': st.st_size,
        }

    def _parse_cef_number(self, value, percent=False):
        s = clean(value).replace('\u2212', '-')
        if not s:
            return None
        neg = s.startswith('(') and s.endswith(')')
        s = s.strip('()')
        work = re.sub(r'\s+', '', s)
        if ',' in work and '.' not in work:
            work = work.replace(',', '.')
        else:
            work = work.replace(',', '')
        m = re.search(r'[-+]?\d+(?:\.\d+)?', work)
        if not m:
            return None
        try:
            num = float(m.group(0))
        except Exception:
            return None
        if neg:
            num = -abs(num)
        if percent and '%' not in s and abs(num) <= 1:
            num *= 100
        return round(num, 4)

    def _add_cef_excel_row(self, out, vals):
        ticker = clean(vals.get(0)).upper()
        if not ticker or ticker in ('TICKER', 'A'):
            return
        if not re.fullmatch(r'[A-Z0-9.\-]{1,12}', ticker):
            return

        entry = {}
        fund_name = clean(vals.get(1))
        strategy = clean(vals.get(2))
        nav = self._parse_cef_number(vals.get(5))
        discount = self._parse_cef_number(vals.get(6), percent=True)

        if fund_name:
            entry['fundName'] = fund_name
        if strategy:
            entry['sectors'] = self._cef_label_items_from_value(strategy)
            entry['strategy'] = strategy
        if nav is not None:
            entry['nav'] = nav
        if discount is not None:
            entry['discount'] = discount
        if entry:
            out[ticker] = entry

    def _load_cef_xlsx_zip(self, zf, names, ET):
        import posixpath

        main_ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        rel_ns = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        pkg_rel_ns = 'http://schemas.openxmlformats.org/package/2006/relationships'
        main = '{%s}' % main_ns
        rel_attr = '{%s}id' % rel_ns
        wanted = (0, 1, 2, 5, 6)

        def read_xml(name):
            return ET.fromstring(zf.read(name))

        shared = []
        if 'xl/sharedStrings.xml' in names:
            shared_root = read_xml('xl/sharedStrings.xml')
            for item in shared_root.findall('%ssi' % main):
                shared.append(''.join(item.itertext()).strip())

        workbook = read_xml('xl/workbook.xml')
        first_sheet = workbook.find('.//%ssheet' % main)
        sheet_path = 'xl/worksheets/sheet1.xml'
        rid = first_sheet.get(rel_attr) if first_sheet is not None else ''
        if rid and 'xl/_rels/workbook.xml.rels' in names:
            rels = read_xml('xl/_rels/workbook.xml.rels')
            for rel in rels.findall('{%s}Relationship' % pkg_rel_ns):
                if rel.get('Id') == rid:
                    target = (rel.get('Target') or '').replace('\\', '/')
                    sheet_path = (target.lstrip('/') if target.startswith('/')
                                  else posixpath.normpath(posixpath.join('xl', target)))
                    break
        if sheet_path not in names:
            sheet_path = next((n for n in names if n.startswith('xl/worksheets/sheet')), '')
        if not sheet_path:
            return {}

        def col_index(ref):
            m = re.match(r'([A-Z]+)', clean(ref).upper())
            if not m:
                return None
            n = 0
            for ch in m.group(1):
                n = n * 26 + (ord(ch) - ord('A') + 1)
            return n - 1

        out = {}
        sheet_root = read_xml(sheet_path)
        for row in sheet_root.findall('.//%ssheetData/%srow' % (main, main)):
            vals = {}
            for cell in row.findall('%sc' % main):
                idx = col_index(cell.get('r'))
                if idx not in wanted:
                    continue
                ctype = cell.get('t')
                if ctype == 'inlineStr':
                    inline = cell.find('%sis' % main)
                    val = ''.join(inline.itertext()).strip() if inline is not None else ''
                else:
                    v = cell.find('%sv' % main)
                    val = v.text.strip() if v is not None and v.text is not None else ''
                    if ctype == 's' and val:
                        try:
                            val = shared[int(val)]
                        except Exception:
                            pass
                vals[idx] = val
            self._add_cef_excel_row(out, vals)
        return out

    def _load_cef_ods_data(self):
        """cefdata.xlsx icinden yalniz A, B, C, F ve G sutunlarini okur.
        Dosyanin uzantisi xlsx olsa da icerigi ODS ise bagimlilik olmadan XML'den okur."""
        import zipfile
        import xml.etree.ElementTree as ET

        xlsx_path = self._cef_data_path()
        with zipfile.ZipFile(xlsx_path) as zf:
            names = set(zf.namelist())
            if 'content.xml' not in names:
                if 'xl/workbook.xml' in names:
                    return self._load_cef_xlsx_zip(zf, names, ET)
                raise ValueError('cefdata.xlsx desteklenen bir tablo formati tasimiyor')
            root = ET.fromstring(zf.read('content.xml'))

        ns = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        }
        office = '{%s}' % ns['office']
        table_ns = '{%s}' % ns['table']
        text_ns = '{%s}' % ns['text']
        wanted = (0, 1, 2, 5, 6)

        def repeat_count(node, attr, default=1):
            try:
                return max(1, int(node.get(attr, default)))
            except Exception:
                return default

        def cell_text(cell):
            parts = []
            for p in cell.findall('.//%sp' % text_ns):
                t = ''.join(p.itertext()).strip()
                if t:
                    parts.append(t)
            if parts:
                return ' '.join(parts)
            return clean(cell.get(office + 'value') or
                         cell.get(office + 'date-value') or
                         cell.get(office + 'time-value') or '')

        out = {}
        spreadsheet = root.find('.//office:spreadsheet', ns)
        if spreadsheet is None:
            return out

        for sheet in spreadsheet.findall('table:table', ns):
            for row in sheet.findall('table:table-row', ns):
                row_repeat = repeat_count(row, table_ns + 'number-rows-repeated')
                vals = {}
                col = 0
                for cell in list(row):
                    if cell.tag not in (table_ns + 'table-cell',
                                        table_ns + 'covered-table-cell'):
                        continue
                    repeated = repeat_count(cell, table_ns + 'number-columns-repeated')
                    val = '' if cell.tag == table_ns + 'covered-table-cell' else cell_text(cell)
                    end = col + repeated
                    for idx in wanted:
                        if col <= idx < end:
                            vals[idx] = val
                    col = end
                    if col > max(wanted):
                        break

                if row_repeat > 1 and not any(clean(vals.get(i)) for i in wanted):
                    continue

                self._add_cef_excel_row(out, vals)
            if out:
                break
        return out

    def _history_rows_for(self, history, sym):
        rows = history.get(clean(sym).upper(), []) if isinstance(history, dict) else []
        out = []
        for item in rows if isinstance(rows, list) else []:
            if not isinstance(item, dict):
                continue
            try:
                d = date.fromisoformat(clean(item.get('date')))
            except Exception:
                continue
            snap = dict(item)
            snap['_date'] = d
            out.append(snap)
        out.sort(key=lambda r: r['_date'])
        return out

    def _history_value_at_or_before(self, rows, target_date, key):
        for item in reversed(rows):
            if item.get('_date') <= target_date:
                value = self._history_float(item.get(key))
                if value is not None:
                    return value
        return None

    def _calc_cef_history_stats(self, sym, history=None):
        history = history if isinstance(history, dict) else self._load_cef_history()
        rows = self._history_rows_for(history, sym)
        if not rows:
            return {}

        latest = rows[-1]
        latest_date = latest.get('_date')
        latest_nav = self._history_float(latest.get('nav'))
        latest_disc = self._history_float(latest.get('discount'))
        if latest_date is None:
            return {}

        stats = {}
        periods = [
            ('3m', 92, 'navReturn3m', 'zScore3m'),
            ('6m', 183, 'navReturn6m', 'zScore6m'),
            ('1y', 365, 'navReturn1y', 'zScore1y'),
        ]
        for _, calendar_days, nav_key, z_key in periods:
            start_date = latest_date - timedelta(days=calendar_days)
            base_nav = self._history_value_at_or_before(rows, start_date, 'nav')
            if latest_nav is not None and base_nav not in (None, 0):
                stats[nav_key] = round(((latest_nav / base_nav) - 1) * 100, 2)

            window = [
                self._history_float(item.get('discount'))
                for item in rows
                if item.get('_date') >= start_date and
                self._history_float(item.get('discount')) is not None
            ]
            has_full_window = any(item.get('_date') <= start_date for item in rows)
            if has_full_window and latest_disc is not None and len(window) >= 5:
                avg = sum(window) / len(window)
                sd = statistics.pstdev(window)
                if sd > 0:
                    stats[z_key] = round((latest_disc - avg) / sd, 2)
        return stats

    def _enrich_cef_nav_stats(self, nav_dict):
        data = {}
        if not isinstance(nav_dict, dict):
            return data
        self._update_cef_history_snapshot(nav_dict)
        cef_src = getattr(self, 'cef', {}) or {}
        for sym, info in nav_dict.items():
            ticker = clean(sym).upper()
            if not ticker:
                continue
            row = dict(info) if isinstance(info, dict) else {}
            # cef_sector_data'daki strategy/fundName/sectors bilgisini aktar
            cef_row = cef_src.get(ticker, {})
            for field in ('fundName', 'strategy', 'sectors', 'categoryName'):
                if not row.get(field) and cef_row.get(field):
                    row[field] = cef_row[field]
            data[ticker] = row
        return data

    def _save_nav_cache(self, nav_dict, source_path=None, source=None):
        """nav_dict: {TICKER: {nav, discount, ...}} -> cef_nav_data.json'a yazar."""
        existing_source = 'cefdata.xlsx'
        existing_mtime = None
        existing_size = None
        try:
            raw = _load('cef_nav_data.json')
            if isinstance(raw, dict):
                existing_source = raw.get('source', 'cefdata.xlsx')
                existing_mtime = raw.get('sourceMtime')
                existing_size = raw.get('sourceSize')
        except Exception:
            pass

        nav_dict = self._enrich_cef_nav_stats(nav_dict)
        payload = {
            'period':    self._turkey_refresh_period(),
            'updatedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source':    source or existing_source,
            'data':      nav_dict,
        }
        if source_path:
            payload.update(self._cef_source_meta(source_path))
        else:
            if existing_mtime is not None:
                payload['sourceMtime'] = existing_mtime
            if existing_size is not None:
                payload['sourceSize'] = existing_size

        _save('cef_nav_data.json', payload)
        return nav_dict

    def _load_nav_cache(self):
        """Cache'i okur; cefdata.xlsx degistiyse dosyadan yeniler."""
        raw = _load('cef_nav_data.json')
        data = raw.get('data') if isinstance(raw.get('data'), dict) else {}
        current_period = raw.get('period') == self._turkey_refresh_period()
        if current_period and data and raw.get('source') == 'cefconnect':
            return data
        try:
            source_path = self._cef_data_path()
            source_meta = self._cef_source_meta(source_path)
            cached_mtime = float(raw.get('sourceMtime') or 0)
            cached_size = int(raw.get('sourceSize') or -1)
            source_current = (
                abs(cached_mtime - float(source_meta['sourceMtime'])) < 0.001 and
                cached_size == int(source_meta['sourceSize'])
            )
            if current_period and data and source_current:
                return data
            fresh = self._load_cef_ods_data()
            if fresh:
                # Mevcut detayli bilgileri koruyarak yeni verileri merge et
                merged = dict(data) if data else {}
                for ticker, new_info in fresh.items():
                    row = dict(merged.get(ticker, {}))
                    row.update(new_info)
                    merged[ticker] = row
                merged = self._save_nav_cache(merged, source_path, source='cefdata.xlsx')
                return merged
        except Exception:
            pass
        # Periyod degisse bile eski detayli verileri dondur
        return data if data else {}

    def _get_nav_for(self, sym):
        """Tek bir ticker için cache'den NAV verisini döner; yoksa {} döner."""
        if not getattr(self, '_cef_nav_cache', None):
            self._cef_nav_cache = self._load_nav_cache()
        cache = self._cef_nav_cache
        self._cef_nav_tickers = set(cache.keys())
        self._all_tickers = set(self.pref.keys()) | self._cef_tickers()
        return cache.get(sym.upper(), {})

    def _cef_tickers(self):
        return CEF_SET | set(self.cef.keys()) | getattr(self, '_cef_nav_tickers', set())

    def _is_cef_symbol(self, sym):
        return clean(sym).upper() in self._cef_tickers()

    # ── CEF HISTORY ─────────────────────────────────────────────────────
    def _cef_history_path(self):
        return os.path.join(_ddir(), 'history', 'cef_history.json')

    def _history_float(self, value):
        try:
            if value is None:
                return None
            return round(float(value), 4)
        except Exception:
            return None

    def _load_cef_history(self):
        path = self._cef_history_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, encoding='utf-8') as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                return raw
            raise ValueError('invalid history json')
        except Exception:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, separators=(',', ':'))
            except Exception:
                pass
            return {}

    def _save_cef_history(self, history):
        try:
            path = self._cef_history_path()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp_path = path + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, separators=(',', ':'))
            os.replace(tmp_path, path)
            return True
        except Exception:
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            return False

    def _nth_weekday(self, year, month, weekday, nth):
        d = date(year, month, 1)
        while d.weekday() != weekday:
            d += timedelta(days=1)
        return d + timedelta(days=7 * (nth - 1))

    def _last_weekday(self, year, month, weekday):
        d = date(year, month + 1, 1) - timedelta(days=1)
        while d.weekday() != weekday:
            d -= timedelta(days=1)
        return d

    def _observed_us_holiday(self, d):
        if d.weekday() == 5:
            return d - timedelta(days=1)
        if d.weekday() == 6:
            return d + timedelta(days=1)
        return d

    def _easter_date(self, year):
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)

    def _us_market_holidays(self, year):
        cache = getattr(self, '_us_market_holiday_cache', None)
        if cache is None:
            cache = {}
            self._us_market_holiday_cache = cache
        if year in cache:
            return cache[year]

        holidays = set()

        def add_observed(actual):
            observed = self._observed_us_holiday(actual)
            if observed.year == year:
                holidays.add(observed)

        add_observed(date(year, 1, 1))       # New Year's Day
        add_observed(date(year + 1, 1, 1))   # Next New Year observed on Dec 31
        holidays.add(self._nth_weekday(year, 1, 0, 3))   # MLK Day
        holidays.add(self._nth_weekday(year, 2, 0, 3))   # Washington's Birthday
        holidays.add(self._easter_date(year) - timedelta(days=2))  # Good Friday
        holidays.add(self._last_weekday(year, 5, 0))     # Memorial Day
        if year >= 2022:
            add_observed(date(year, 6, 19))  # Juneteenth
        add_observed(date(year, 7, 4))       # Independence Day
        holidays.add(self._nth_weekday(year, 9, 0, 1))   # Labor Day
        holidays.add(self._nth_weekday(year, 11, 3, 4))  # Thanksgiving
        add_observed(date(year, 12, 25))     # Christmas

        cache[year] = holidays
        return holidays

    def _is_us_trading_day(self, d):
        return d.weekday() < 5 and d not in self._us_market_holidays(d.year)

    def _cef_source_data_date(self, nav_dict=None):
        if not isinstance(nav_dict, dict):
            return None
        counts = {}
        for info in nav_dict.values():
            if not isinstance(info, dict):
                continue
            for key in ('lastPriceDate', 'cefConnectUpdated', 'navDate', 'cefSummaryAsOf'):
                d = self._parse_source_date(info.get(key))
                if d is not None:
                    counts[d] = counts.get(d, 0) + 1
                    break
        if not counts:
            return None
        return sorted(counts.items(), key=lambda item: (item[1], item[0]))[-1][0]

    def _cef_history_asof_date(self, nav_dict=None):
        source_date = self._cef_source_data_date(nav_dict)
        if source_date is not None:
            d = source_date
        else:
            try:
                d = date.fromisoformat(self._turkey_refresh_period())
            except Exception:
                d = date.today()
        while not self._is_us_trading_day(d):
            d -= timedelta(days=1)
        return d

    def _cef_history_cutoff_date(self):
        d = self._cef_history_asof_date()
        count = 0
        while count < CEF_HISTORY_RETENTION_TRADING_DAYS:
            if self._is_us_trading_day(d):
                count += 1
            if count < CEF_HISTORY_RETENTION_TRADING_DAYS:
                d -= timedelta(days=1)
        return d

    def _prune_old_history(self, history):
        if not isinstance(history, dict):
            return {}
        try:
            cutoff = self._cef_history_cutoff_date()
        except Exception:
            cutoff = date.today() - timedelta(days=370)

        pruned = {}
        allowed = ('date', 'price', 'nav', 'discount')
        for ticker, rows in history.items():
            sym = clean(ticker).upper()
            if not sym or not isinstance(rows, list):
                continue

            kept = []
            seen_dates = set()
            for item in rows:
                if not isinstance(item, dict):
                    continue
                ds = clean(item.get('date'))
                try:
                    d = date.fromisoformat(ds)
                except Exception:
                    continue
                if d < cutoff:
                    continue

                snap = {'date': ds}
                for key in allowed[1:]:
                    val = self._history_float(item.get(key))
                    if val is not None:
                        snap[key] = val
                if len(snap) <= 1:
                    continue

                if ds in seen_dates:
                    kept = [r for r in kept if r.get('date') != ds]
                seen_dates.add(ds)
                kept.append(snap)

            kept.sort(key=lambda r: r.get('date', ''))
            if len(kept) > CEF_HISTORY_RETENTION_TRADING_DAYS:
                kept = kept[-CEF_HISTORY_RETENTION_TRADING_DAYS:]
            if kept:
                pruned[sym] = kept
        return pruned

    def _update_cef_history_snapshot(self, nav_dict=None):
        try:
            nav_dict = nav_dict if isinstance(nav_dict, dict) else self._load_nav_cache()
            if not nav_dict:
                return False

            asof_date = self._cef_history_asof_date(nav_dict)
            today_s = asof_date.isoformat()
            has_source_date = self._cef_source_data_date(nav_dict) is not None
            source_meta = ''
            try:
                meta = self._cef_source_meta(self._cef_data_path())
                source_meta = f"{meta.get('sourceMtime')}:{meta.get('sourceSize')}"
            except Exception:
                pass

            data_sig = []
            for sym in sorted(nav_dict.keys()):
                info = nav_dict.get(sym) if isinstance(nav_dict.get(sym), dict) else {}
                price = self._history_float((self.cef.get(sym) or {}).get('lastPrice'))
                nav = self._history_float(info.get('nav'))
                discount = self._history_float(info.get('discount'))
                data_sig.append(f"{sym}:{price}:{nav}:{discount}")
            signature = f"{today_s}|{source_meta}|{len(nav_dict)}|{'|'.join(data_sig)}"
            if getattr(self, '_cef_history_last_signature', None) == signature:
                return False

            history = self._load_cef_history()
            pruned = self._prune_old_history(history)
            changed = pruned != history
            if has_source_date:
                for ticker, rows in list(pruned.items()):
                    kept = []
                    for item in rows:
                        try:
                            if date.fromisoformat(clean(item.get('date'))) <= asof_date:
                                kept.append(item)
                        except Exception:
                            pass
                    if kept:
                        if kept != rows:
                            pruned[ticker] = kept
                            changed = True
                    else:
                        pruned.pop(ticker, None)
                        changed = True

            for sym, info in nav_dict.items():
                ticker = clean(sym).upper()
                if not ticker or not isinstance(info, dict):
                    continue

                snap = {'date': today_s}
                price = self._history_float((self.cef.get(ticker) or {}).get('lastPrice'))
                nav = self._history_float(info.get('nav'))
                discount = self._history_float(info.get('discount'))
                if price is not None:
                    snap['price'] = price
                if nav is not None:
                    snap['nav'] = nav
                if discount is not None:
                    snap['discount'] = discount
                if len(snap) <= 1:
                    continue

                rows = list(pruned.get(ticker, []))
                old_rows = list(rows)
                rows = [r for r in rows if r.get('date') != today_s]
                rows.append(snap)
                rows.sort(key=lambda r: r.get('date', ''))
                if len(rows) > CEF_HISTORY_RETENTION_TRADING_DAYS:
                    rows = rows[-CEF_HISTORY_RETENTION_TRADING_DAYS:]
                pruned[ticker] = rows
                if rows != old_rows:
                    changed = True

            if changed:
                if self._save_cef_history(pruned):
                    self._cef_history_last_signature = signature
                    return True
                return False

            self._cef_history_last_signature = signature
            return False
        except Exception:
            return False

    def _apply_cef_nav_data(self, nav_dict):
        """(Eski uyumluluk) nav_dict → self.cef'e yazar."""
        today_s = date.today().isoformat()
        for ticker, info in nav_dict.items():
            row = dict(self.cef.get(ticker, {'sectors': []}))
            row.update(info)
            row['navFetchDate'] = today_s
            self.cef[ticker] = row
        self._update_cef_history_snapshot(nav_dict)

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
        nav_cache = self._load_nav_cache()
        self._cef_nav_cache = nav_cache
        self._cef_nav_tickers = set(nav_cache.keys())
        self._all_tickers = set(self.pref.keys()) | self._cef_tickers()
        self._update_cef_history_snapshot(nav_cache)

    # ── UI BUILD ─────────────────────────────────────
    def _build_ui(self):
        # ─── Header ─────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG4, height=34)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        self._dot = tk.Label(hdr, text='●', fg=GD, bg=BG4, font=(FNU, 8))
        self._dot.pack(side='left', padx=(8,3), pady=5)

        tk.Label(hdr, text='HAMMER PRO', fg=GD, bg=BG4,
                 font=(FNU, 8, 'bold')).pack(side='left')

        self._hdr_sym = tk.Label(hdr, text='', fg=CY, bg=BG4,
                                  font=(FN, 10, 'bold'))
        self._hdr_sym.pack(side='left', padx=(6,0))

        self._scan_lbl = tk.Label(hdr, text='', fg=TX5, bg=BG4, font=(FNU, 7))
        self._scan_lbl.pack(side='right', padx=8)

        toolbar = tk.Frame(self.root, bg=BG2, bd=0)
        toolbar.pack(fill='x')
        tk.Frame(toolbar, bg=BD, height=1).pack(fill='x')
        bar = tk.Frame(toolbar, bg=BG2)
        bar.pack(fill='x', padx=6, pady=4)

        cat_b = tk.Label(bar, text='Kategoriler ▸', fg=TX4, bg=BG2,
                         font=(FNU, 8), cursor='hand2', padx=7, pady=3)
        cat_b.pack(side='left')
        cat_b.bind('<Enter>', lambda e: cat_b.config(fg=BL, bg=ACC))
        cat_b.bind('<Button-1>', lambda e: self._show_categories_menu(cat_b))
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

        # ─── Bottom trade navigation ──────────────────
        trade_nav = tk.Frame(self.root, bg=BG2)
        trade_nav.pack(side='bottom', fill='x')
        tk.Frame(trade_nav, bg=BD, height=1).pack(fill='x')
        btn_row = tk.Frame(trade_nav, bg=BG2)
        btn_row.pack(fill='x', padx=8, pady=5)
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)

        trade_b = tk.Label(btn_row, text='TRADE', fg=TE, bg=BG2,
                           font=(FNU, 9, 'bold'), cursor='hand2',
                           pady=6, highlightthickness=1,
                           highlightbackground=ACC)
        trade_b.grid(row=0, column=0, sticky='nsew', padx=(0, 3))
        trade_b.bind('<Button-1>', lambda e: self._open_trade_panel())
        trade_b.bind('<Enter>', lambda e: trade_b.config(bg=ACC, fg=TX))
        trade_b.bind('<Leave>', lambda e: trade_b.config(bg=BG2, fg=TE))
        Tip(trade_b, "Pre-Trade Evaluation & Trade Journal")

        export_b = tk.Label(btn_row, text='EXPORT', fg=AM, bg=BG2,
                            font=(FNU, 9, 'bold'), cursor='hand2',
                            pady=6, highlightthickness=1,
                            highlightbackground=AM)
        export_b.grid(row=0, column=1, sticky='nsew', padx=(3, 0))
        export_b.bind('<Button-1>', lambda e: self._open_div_export())
        export_b.bind('<Enter>', lambda e: export_b.config(bg='#2a1f0b', fg=AM))
        export_b.bind('<Leave>', lambda e: export_b.config(bg=BG2, fg=AM))
        Tip(export_b, "Dividend Takvimi Export (TXT)")

        # ─── Content (scrollable) ─────────────────────
        self._scroll = ScrollFrame(self.root)
        self._scroll.pack(fill='both', expand=True, padx=0)
        self._inner = self._scroll.inner  # convenience

    def _build_categories(self):
        cats = {'low': [], 'mid': [], 'high': [], 'float': [], 'other': []}
        tip_cats  = {}   # {tip_value: [(sym,p)]}
        mn4_cats  = {}   # {mn4_value: [(sym,p)]}
        rat_cats  = {}   # {rating: [(sym,p)]}
        cef_cats  = {}   # {strategy_or_sector: [(sym,row)]}

        for sym, p in self.pref.items():
            # ── Kupon kategorisi ─────────────────────
            if is_floating(p):
                cats['float'].append((sym, p))
            else:
                cv = parse_coupon(p.get('coupon'))
                if cv is None:
                    cats['other'].append((sym, p))
                elif cv < 5.5:    cats['low'].append((sym, p))
                elif cv <= 7.0:   cats['mid'].append((sym, p))
                else:             cats['high'].append((sym, p))

            # ── Tip kategorisi ───────────────────────
            tip = clean(p.get('fixFloat')) or 'Belirtilmemiş'
            tip_cats.setdefault(tip, []).append((sym, p))

            # ── >4M kategorisi ───────────────────────
            mn4 = clean(p.get('mn4')) or 'Belirtilmemiş'
            mn4_cats.setdefault(mn4, []).append((sym, p))

            # ── Rating kategorisi ────────────────────
            rat = clean(p.get('rating')) or 'Belirtilmemiş'
            rat_cats.setdefault(rat, []).append((sym, p))

        for key in cats:
            cats[key].sort(key=lambda x: x[0])
        for d in (tip_cats, mn4_cats, rat_cats):
            for key in d:
                d[key].sort(key=lambda x: x[0])

        nav_cache = getattr(self, '_cef_nav_cache', {}) or {}
        cef_user_groups = set()
        for sym in sorted(self._cef_tickers()):
            nav_info = nav_cache.get(sym, {}) if isinstance(nav_cache.get(sym), dict) else {}
            cef_row = dict(self.cef.get(sym, {}))
            cef_item = dict(cef_row)
            cef_item.update(nav_info)
            cef_item['_kind'] = 'cef'

            groups = self._cef_indexes(sym, nav_info, cef_row)
            for group in groups:
                cef_user_groups.add(group)
            if not groups:
                groups.append('Belirtilmemiş')
            else:
                cef_item['sectors'] = groups

            seen_groups = set()
            for group in groups:
                if group in seen_groups:
                    continue
                seen_groups.add(group)
                cef_cats.setdefault(group, []).append((sym, cef_item))
        for key in cef_cats:
            cef_cats[key].sort(key=lambda x: x[0])

        self._cats     = cats
        self._tip_cats = tip_cats
        self._mn4_cats = mn4_cats
        self._rat_cats = rat_cats
        self._cef_cats = cef_cats
        self._cef_user_group_names = cef_user_groups

        total = sum(len(v) for v in cats.values())
        if hasattr(self, '_cat_summary'):
            self._cat_summary.config(text=f"{total}P / {len(self._cef_tickers())}C")

    # ─── KATEGORİ MENÜLERİ ───────────────────────────
    def _new_category_menu(self, parent=None, accent=BL):
        return tk.Menu(parent or self.root, tearoff=0, bg=BG2, fg=TX,
                       activebackground=ACC, activeforeground=accent,
                       bd=0, relief='flat')

    def _add_category_items(self, menu, cats, title_prefix, accent_col,
                            order=None, color_fn=None, max_items=None):
        if not cats:
            menu.add_command(label='Kayıt yok', state='disabled')
            return
        if order is None:
            order = sorted(cats.keys(), key=lambda k: (-len(cats[k]), k))
        if max_items:
            order = order[:max_items]
        for key in order:
            items = cats.get(key, [])
            if not items:
                continue
            label = f"{key or '—'}  ({len(items)})"
            kwargs = {}
            if color_fn:
                kwargs['foreground'] = color_fn(key)
            menu.add_command(
                label=label,
                command=lambda k=key, p=title_prefix: (
                    self._hide_categories_menu(),
                    self._show_cat_popup(cats.get(k, []), f"{p}: {k}", accent_col)
                ),
                **kwargs
            )

    def _is_upper_cef_category(self, key):
        text = clean(key)
        return bool(text and any(ch.isalpha() for ch in text) and text == text.upper())

    def _cef_category_sort_key(self, key):
        text = clean(key)
        user_groups = getattr(self, '_cef_user_group_names', set())
        return (0 if text in user_groups else 1,
                0 if self._is_upper_cef_category(text) else 1,
                text.upper(), text)

    def _cancel_categories_job(self, attr):
        job = getattr(self, attr, None)
        if job:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
            setattr(self, attr, None)

    def _schedule_categories_menu(self, widget, delay=360):
        self._cancel_categories_job('_cat_menu_job')
        self._cancel_categories_job('_cat_close_job')
        self._cat_menu_job = self.root.after(
            delay, lambda w=widget: self._show_categories_menu(w))

    def _schedule_categories_close(self, delay=500):
        self._cancel_categories_job('_cat_menu_job')
        self._cancel_categories_job('_cat_close_job')
        if self._cat_menu:
            self._cat_close_job = self.root.after(delay, self._hide_categories_menu)

    def _hide_categories_menu(self):
        self._cancel_categories_job('_cat_menu_job')
        self._cancel_categories_job('_cat_close_job')
        menu = self._cat_menu
        self._cat_menu = None
        if menu:
            try:
                menu.unpost()
                menu.destroy()
            except Exception:
                pass

    def _show_cef_category_selector(self, anchor_widget):
        cats = getattr(self, '_cef_cats', {})
        popup = tk.Toplevel(self.root)
        popup.title('CEF Endeks/Sektör')
        popup.geometry('315x390')
        self._style_window(popup)
        popup.transient(self.root)

        try:
            x = anchor_widget.winfo_rootx() + anchor_widget.winfo_width() + 6
            y = anchor_widget.winfo_rooty()
            popup.geometry(f'+{x}+{y}')
        except Exception:
            pass

        hf = tk.Frame(popup, bg=BG2)
        hf.pack(fill='x')
        tk.Label(hf, text='CEF ENDEKS / SEKTÖR', fg=AM, bg=BG2,
                 font=(FNU, 9, 'bold'), padx=8, pady=6).pack(side='left')
        tk.Button(hf, text='×', command=popup.destroy,
                  bg=BG2, fg=TX4, activebackground=BG3, activeforeground=TX,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=8, pady=2, cursor='hand2').pack(side='right', padx=4, pady=3)
        tk.Frame(popup, bg=BD, height=1).pack(fill='x')

        sv = tk.StringVar()
        e = tk.Entry(popup, textvariable=sv, bg=BG2, fg=TX,
                     insertbackground=BL, font=(FN, 9), relief='flat', bd=0,
                     highlightthickness=1, highlightbackground=BD,
                     highlightcolor=AM)
        e.pack(fill='x', padx=6, pady=6, ipady=4)

        frame = tk.Frame(popup, bg=BG)
        frame.pack(fill='both', expand=True, padx=2)
        sb = tk.Scrollbar(frame, bg=BG2, troughcolor=BG, width=6)
        lb = tk.Listbox(frame, bg=BG, fg=TX2, selectbackground=ACC,
                        selectforeground=AM, font=(FN, 9), relief='flat',
                        bd=0, highlightthickness=0, activestyle='none',
                        yscrollcommand=sb.set)
        sb.config(command=lb.yview)
        sb.pack(side='right', fill='y')
        lb.pack(side='left', fill='both', expand=True)

        status_var = tk.StringVar()
        tk.Label(popup, textvariable=status_var, fg=TX5, bg=BG2,
                 font=(FNU, 7), pady=2).pack(fill='x', side='bottom')

        ordered = sorted(cats.keys(), key=self._cef_category_sort_key)
        visible = []

        def fill_list(*_):
            nonlocal visible
            q = sv.get().upper().strip()
            lb.delete(0, 'end')
            visible = []
            for key in ordered:
                if q and q not in key.upper():
                    continue
                items = cats.get(key, [])
                label = f"  {key:<28} ({len(items)})"
                lb.insert('end', label[:64])
                if key in getattr(self, '_cef_user_group_names', set()):
                    lb.itemconfig('end', fg=CY)
                elif self._is_upper_cef_category(key):
                    lb.itemconfig('end', fg=BL)
                visible.append(key)
            status_var.set(f'{len(visible)} kategori  |  Enter / çift tık: aç')

        def open_selected(e=None):
            sel = lb.curselection()
            if not sel or not visible:
                return
            key = visible[sel[0]]
            popup.destroy()
            self._show_cat_popup(cats.get(key, []), f"CEF Endeks/Sektör: {key}", AM)

        def on_wheel(e):
            lb.yview_scroll(int(-1 * (e.delta / 120)), 'units')
            return 'break'

        fill_list()
        sv.trace_add('write', fill_list)
        lb.bind('<Double-Button-1>', open_selected)
        lb.bind('<Return>', open_selected)
        lb.bind('<MouseWheel>', on_wheel)
        e.bind('<Return>', lambda e: (lb.selection_set(0), open_selected()) if lb.size() else None)
        e.focus_set()

    def _show_categories_menu(self, widget):
        self._hide_categories_menu()
        root_menu = self._new_category_menu(accent=BL)
        self._cat_menu = root_menu

        labels = {'low':'Kupon < 5.5%', 'mid':'Kupon 5.5% - 7%',
                  'high':'Kupon 7%+', 'float':'Floating', 'other':'Diğer'}
        coupon_menu = self._new_category_menu(root_menu, BL)
        for key in ['low', 'mid', 'high', 'float', 'other']:
            count = len(self._cats.get(key, []))
            coupon_menu.add_command(
                label=f"{labels[key]} ({count})",
                command=lambda k=key: (
                    self._hide_categories_menu(),
                    self._show_cat_popup(self._cats.get(k, []), labels[k], BL)
                )
            )
        root_menu.add_cascade(label='Preferred Kupon', menu=coupon_menu)

        tip_menu = self._new_category_menu(root_menu, PU)
        self._add_category_items(tip_menu, getattr(self, '_tip_cats', {}),
                                 'Tip', PU)
        root_menu.add_cascade(label='Preferred Tip', menu=tip_menu)

        mn4_menu = self._new_category_menu(root_menu, AM)
        self._add_category_items(mn4_menu, getattr(self, '_mn4_cats', {}),
                                 '>4M', AM)
        root_menu.add_cascade(label='Preferred >4M', menu=mn4_menu)

        rat_menu = self._new_category_menu(root_menu, TE)
        _grade = {'AAA':0,'AA+':1,'AA':2,'AA-':3,'A+':4,'A':5,'A-':6,
                  'BBB+':7,'BBB':8,'BBB-':9,'BB+':10,'BB':11,'BB-':12,
                  'B+':13,'B':14,'B-':15,'CCC':16,'CC':17,'C':18,'D':19}
        rat_order = sorted(getattr(self, '_rat_cats', {}).keys(),
                           key=lambda k: (_grade.get(k.upper(), 99), k))
        self._add_category_items(
            rat_menu, getattr(self, '_rat_cats', {}), 'Rating', TE,
            order=rat_order,
            color_fn=lambda k: rating_col(k) if k != 'Belirtilmemiş' else TX5
        )
        root_menu.add_cascade(label='Preferred Rating', menu=rat_menu)

        root_menu.add_separator()
        root_menu.add_command(label='CEF Endeks/Sektör...',
                              command=lambda w=widget: (
                                  self._hide_categories_menu(),
                                  self._show_cef_category_selector(w)))

        root_menu.post(widget.winfo_rootx(),
                       widget.winfo_rooty() + widget.winfo_height())

    # ─── KUPON KATEGORİ DROPDOWN ─────────────────────
    def _show_category_dropdown(self, widget):
        labels = {'low':'Kupon < 5.5%', 'mid':'Kupon 5.5% – 7%',
                  'high':'Kupon 7%+', 'float':'Floating', 'other':'Diğer'}
        order  = ['low', 'mid', 'high', 'float', 'other']
        menu = tk.Menu(self.root, tearoff=0, bg=BG2, fg=TX,
                       activebackground=ACC, activeforeground=BL,
                       bd=0, relief='flat')
        for key in order:
            count = len(self._cats.get(key, []))
            menu.add_command(label=f"{labels[key]} ({count})",
                             command=lambda k=key: self._show_cat_popup(
                                 self._cats.get(k, []), labels[k], BL))
        try:
            menu.tk_popup(widget.winfo_rootx(),
                          widget.winfo_rooty() + widget.winfo_height())
        finally:
            menu.grab_release()

    # ─── TİP DROPDOWN ────────────────────────────────
    def _show_tip_dropdown(self, widget):
        cats = getattr(self, '_tip_cats', {})
        order = sorted(cats.keys(), key=lambda k: (-len(cats[k]), k))
        menu = tk.Menu(self.root, tearoff=0, bg=BG2, fg=TX,
                       activebackground=ACC, activeforeground=PU,
                       bd=0, relief='flat')
        for key in order:
            count = len(cats[key])
            menu.add_command(label=f"{key or '—'}  ({count})",
                             command=lambda k=key: self._show_cat_popup(
                                 cats.get(k, []), f"Tip: {k}", PU))
        try:
            menu.tk_popup(widget.winfo_rootx(),
                          widget.winfo_rooty() + widget.winfo_height())
        finally:
            menu.grab_release()

    # ─── >4M DROPDOWN ────────────────────────────────
    def _show_mn4_dropdown(self, widget):
        cats = getattr(self, '_mn4_cats', {})
        order = sorted(cats.keys(), key=lambda k: (-len(cats[k]), k))
        menu = tk.Menu(self.root, tearoff=0, bg=BG2, fg=TX,
                       activebackground=ACC, activeforeground=AM,
                       bd=0, relief='flat')
        for key in order:
            count = len(cats[key])
            menu.add_command(label=f"{key or '—'}  ({count})",
                             command=lambda k=key: self._show_cat_popup(
                                 cats.get(k, []), f">4M: {k}", AM))
        try:
            menu.tk_popup(widget.winfo_rootx(),
                          widget.winfo_rooty() + widget.winfo_height())
        finally:
            menu.grab_release()

    # ─── RATING DROPDOWN ─────────────────────────────
    def _show_rating_dropdown(self, widget):
        cats = getattr(self, '_rat_cats', {})
        # Rating sıralaması: Investment Grade önce
        _grade = {'AAA':0,'AA+':1,'AA':2,'AA-':3,'A+':4,'A':5,'A-':6,
                  'BBB+':7,'BBB':8,'BBB-':9,'BB+':10,'BB':11,'BB-':12,
                  'B+':13,'B':14,'B-':15,'CCC':16,'CC':17,'C':18,'D':19}
        def _sort_key(k):
            return (_grade.get(k.upper(), 99), k)
        order = sorted(cats.keys(), key=_sort_key)
        menu = tk.Menu(self.root, tearoff=0, bg=BG2, fg=TX,
                       activebackground=ACC, activeforeground=TE,
                       bd=0, relief='flat')
        for key in order:
            count = len(cats[key])
            col = rating_col(key) if key != 'Belirtilmemiş' else TX5
            menu.add_command(label=f"{key or '—'}  ({count})",
                             foreground=col,
                             command=lambda k=key: self._show_cat_popup(
                                 cats.get(k, []), f"Rating: {k}", TE))
        try:
            menu.tk_popup(widget.winfo_rootx(),
                          widget.winfo_rooty() + widget.winfo_height())
        finally:
            menu.grab_release()

    # ─── GENEL KATEGORİ POPUP ────────────────────────
    def _show_cat_popup(self, all_items, title, accent_col):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry('310x500')
        self._style_window(popup)
        popup.transient(self.root)

        hf = tk.Frame(popup, bg=BG2)
        hf.pack(fill='x')
        tk.Label(hf, text=title.upper(),
                 fg=accent_col, bg=BG2, font=(FNU, 9, 'bold'),
                 padx=8, pady=6).pack(side='left')
        copy_lbl = tk.Label(hf, text='⎘ Tümünü Kopyala', fg=TX5, bg=BG2,
                            font=(FNU, 7), cursor='hand2', padx=6)
        copy_lbl.pack(side='right', pady=4)

        tk.Frame(popup, bg=BD, height=1).pack(fill='x')

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

        status_var = tk.StringVar(value='Çift tıkla: aç  |  Ctrl+C: kopyala')
        tk.Label(popup, textvariable=status_var, fg=TX5, bg=BG2,
                 font=(FNU, 7), pady=2).pack(fill='x', side='bottom')

        visible_items = []

        def fill_list(fq=''):
            nonlocal visible_items
            lb.delete(0, 'end')
            fq = fq.upper().strip()
            visible_items = []
            for sym, p in all_items:
                p = p or {}
                is_cef = p.get('_kind') == 'cef'
                sectors = p.get('sectors', [])
                haystack = ' '.join([
                    sym,
                    clean(p.get('strategy')),
                    clean(p.get('fundName')),
                    ' '.join(clean(x) for x in sectors if clean(x)),
                ]).upper()
                if fq and fq not in haystack:
                    continue
                if is_cef:
                    price = fmt_price(p.get('lastPrice')) or ''
                    nav = fmt_price(p.get('nav')) or ''
                    disc = fmt_pct(p.get('discount')) or ''
                    user_sectors = [clean(x) for x in sectors if clean(x)]
                    desc = '/'.join(user_sectors[:2]) or clean(p.get('strategy'))
                    lb.insert('end', f'  {sym:<8} {price:<8} NAV {nav:<8} {disc:<8} {desc[:24]}')
                else:
                    cp = clean(p.get('coupon')) or '—'
                    rt = clean(p.get('rating')) or ''
                    mn = clean(p.get('mn4')) or ''
                    ft = clean(p.get('fixFloat')) or ''
                    lb.insert('end', f'  {sym:<10} {cp:<8} {ft:<8} {rt:<5} {mn}')
                visible_items.append((sym, p))
            status_var.set(f'{len(visible_items)} kayıt  |  Çift tıkla: aç  |  Ctrl+C: kopyala')

        fill_list()
        sv.trace_add('write', lambda *_: fill_list(sv.get()))

        def on_dbl(e):
            sel = lb.curselection()
            if sel:
                raw = lb.get(sel[0]).strip().split()[0]
                popup.destroy()
                self.select(raw)

        def copy_sel(e=None):
            sel = lb.curselection()
            lines = [lb.get(i) for i in sel] if sel else [lb.get(i) for i in range(lb.size())]
            popup.clipboard_clear()
            popup.clipboard_append('\n'.join(l.strip() for l in lines))
            status_var.set(f'✓ {len(lines)} satır kopyalandı!')
            popup.after(1500, lambda: status_var.set(
                f'{len(visible_items)} kayıt  |  Çift tıkla: aç  |  Ctrl+C: kopyala'))

        def copy_all():
            syms = [s for s,_ in visible_items]
            popup.clipboard_clear()
            popup.clipboard_append('\n'.join(syms))
            status_var.set(f'✓ {len(syms)} ticker kopyalandı!')
            popup.after(1500, lambda: status_var.set(
                f'{len(visible_items)} kayıt  |  Çift tıkla: aç  |  Ctrl+C: kopyala'))

        lb.bind('<Double-Button-1>', on_dbl)
        lb.bind('<Control-c>', copy_sel)
        popup.bind('<Control-c>', copy_sel)
        popup.bind('<Control-C>', copy_sel)
        copy_lbl.bind('<Button-1>', lambda e: copy_all())
        e.focus_set()


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
            elif self._is_cef_symbol(m):
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
        elif self._is_cef_symbol(sym):
            self._render_cef_clean(sym)
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
        if (now_tr.hour, now_tr.minute) < (14, 50):
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
        common_syms = sorted({clean(v).upper() for v in self.ptoc.values()
                              if clean(v) and clean(v).upper() != 'PRIVATE'})
        tasks = [('pref', s) for s in pref_syms]
        tasks += [('common', s) for s in common_syms]

        # NAV çekimi = 1 adım (cefconnect tek oturum)
        nav_batches = 1
        total = len(tasks) + nav_batches
        done = 0

        # ── 1) Yahoo Finance: fiyatlar + market cap ──────────────────────
        for kind, sym in tasks:
            try:
                if kind == 'pref':
                    quote = self._fetch_yahoo_price_info(sym, preferred=True)
                    self._apply_pref_market_data(
                        sym, quote.get('price'), quote.get('symbol'),
                        quote.get('priceDate'))
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
            if done % 5 == 0 or done == len(tasks):
                self.root.after(0, self._update_startup_loading, done, total, sym)
            time.sleep(0.12)

        # ── 2) cefdata.xlsx: NAV + Premium/Discount okuma ───────────────
        self.root.after(0, self._update_startup_loading, done, total,
                        'CEFConnect toplu veri okunuyor...')
        nav_count = 0
        nav_label = 'cache'
        raw_cache = _load('cef_nav_data.json')
        nav_dict = raw_cache.get('data') if isinstance(raw_cache.get('data'), dict) else {}
        if raw_cache.get('period') == self._turkey_refresh_period() and nav_dict:
            nav_count = len(nav_dict)
            self._cef_nav_cache = nav_dict
        else:
            # Onceki periyodun detayli verilerini (52-week, z-score, pdAvg,
            # fundName, strategy vs.) korumak icin eski cache'i base olarak al
            prev_cache = dict(nav_dict)  # onceki periyodun verileri
            nav_label = 'cefdata.xlsx'
            if not self._cef_connect_recent_failure():
                try:
                    nav_label = 'CEFConnect'
                    try:
                        fresh = self._fetch_cef_connect_data()
                    except Exception as primary_exc:
                        fresh = self._fetch_cef_connect_data_legacy()
                        nav_label = 'CEFConnect legacy'
                    if not fresh:
                        raise RuntimeError('CEFConnect returned no usable rows')
                    # Mevcut detayli bilgileri koruyarak yeni fiyat/nav/discount merge et
                    merged = dict(prev_cache)
                    for ticker, new_info in fresh.items():
                        row = dict(merged.get(ticker, {}))
                        row.update(new_info)
                        merged[ticker] = row
                    nav_dict = merged
                    self._apply_cef_nav_data(fresh)
                    nav_dict = self._save_nav_cache(nav_dict, source='cefconnect')
                    nav_count = len(nav_dict)
                    self._cef_nav_cache = nav_dict
                    self._save_cef_connect_fetch_meta('ok', nav_count)
                except Exception as exc:
                    self._save_cef_connect_fetch_meta('error', 0, exc)
                    nav_label = 'cefdata.xlsx'
            if not nav_count:
                try:
                    fresh_ods = self._load_cef_ods_data()
                    if fresh_ods:
                        merged = dict(prev_cache)
                        for ticker, new_info in fresh_ods.items():
                            row = dict(merged.get(ticker, {}))
                            row.update(new_info)
                            merged[ticker] = row
                        nav_dict = self._save_nav_cache(
                            merged, self._cef_data_path(), source='cefdata.xlsx')
                        nav_count = len(nav_dict)
                        self._cef_nav_cache = nav_dict
                except Exception:
                    pass
        done += 1
        self.root.after(0, self._update_startup_loading, done, total,
                        f'{nav_label} hazir ({nav_count} CEF)')

        _save('pref_data.json', self.pref)
        _save('cef_sector_data.json', self.cef)
        _save('common_data.json', self.common)
        _save('data_fetch_meta.json', {
            'lastFullRefresh': date.today().isoformat(),
            'lastFullRefreshPeriod': self._turkey_refresh_period(),
            'resetTimezone': 'Europe/Istanbul',
            'resetHour': 14,
            'resetMinute': 50,
            'updatedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        self.root.after(0, self._finish_startup_refresh)

    def _finish_startup_refresh(self):
        self._reload()
        self._build_categories()
        self._show_empty()
        self._start_scanner_if_available()
        self._start_cef_detail_cache_refresh()

    # ─── PREFERRED VIEW ──────────────────────────────
    def _render_pref_legacy(self, sym):
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

    def _render_pref(self, sym):
        p = self.pref[sym]
        parent = self.ptoc.get(sym)
        c = self.common.get(parent) if parent else None
        f = self._inner

        self._draw_common_card(f, parent or 'PRIVATE', c, sym)

        last_price = p.get('lastPrice')
        current_yield = p.get('currentYield')
        if current_yield is None and last_price is not None and p.get('div') is not None:
            try:
                current_yield = (float(p.get('div')) * 4 / float(last_price)) * 100
            except Exception:
                current_yield = None

        ytc_v, ytm_v = p.get('ytc'), p.get('ytm')
        if last_price is not None:
            calc_ytc, calc_ytm = self._calc_pref_yields(p)
            ytc_v = calc_ytc if calc_ytc is not None else ytc_v
            ytm_v = calc_ytm if calc_ytm is not None else ytm_v
        ytc = fmt_pct(ytc_v)
        ytm = fmt_pct(ytm_v)
        call = clean(p.get('callDate'))
        mature = clean(p.get('matureDate'))

        def valid_date_text(value):
            return bool(value and value.lower() not in ('none', 'null', 'nan'))

        # Dividend calendar border color
        next_div, days_left, div_freq = self._next_div_for_pref(sym)
        earning_near = self._event_is_today_or_tomorrow(self._earning_for_common(parent))
        if earning_near:
            pref_border = RD
        else:
            pref_border = _pref_div_border_color(days_left)
        card = tk.Frame(f, bg=BG2, bd=1, relief='flat',
                        highlightthickness=2, highlightbackground=pref_border)
        card.pack(fill='x', padx=6, pady=(0, 7))

        header = tk.Frame(card, bg=BG4)
        header.pack(fill='x')
        title = tk.Frame(header, bg=BG4)
        title.pack(side='left', fill='x', expand=True, padx=8, pady=7)
        tk.Label(title, text='PREFERRED', fg=GD, bg=BG4,
                 font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(title, text=sym, fg=TX, bg=BG4,
                 font=(FN, 16, 'bold')).pack(anchor='w')
        if parent:
            tk.Label(title, text=f"COMMON {parent}", fg=TX4, bg=BG4,
                     font=(FNU, 7, 'bold')).pack(anchor='w', pady=(1, 0))

        # Right side badges
        badge_frame = tk.Frame(header, bg=BG4)
        badge_frame.pack(side='right', padx=8, pady=5)

        # Next dividend date badge
        if next_div is not None:
            freq_tag = 'M' if div_freq == 'monthly' else 'Q'
            div_text = f"{next_div.strftime('%b %d')} [{freq_tag}]"
            div_color = pref_border if not earning_near else _pref_div_border_color(days_left)
            if days_left is not None and days_left <= 1:
                days_label = 'BUGÜN!' if days_left <= 0 else 'YARIN!'
            elif days_left is not None and days_left <= 15:
                days_label = f'{days_left}g'
            elif days_left is not None and days_left <= 30:
                days_label = f'{days_left}g'
            else:
                days_label = f'{days_left}g' if days_left is not None else ''
            tk.Label(badge_frame, text=div_text, fg=div_color, bg=BG3,
                     font=(FNU, 8, 'bold'), padx=6, pady=2,
                     highlightthickness=1, highlightbackground=div_color).pack(anchor='e')
            if days_label:
                tk.Label(badge_frame, text=days_label, fg=div_color, bg=BG4,
                         font=(FNU, 7, 'bold')).pack(anchor='e', pady=(1, 0))

        ft = clean(p.get('fixFloat'))
        if ft:
            badge = tk.Label(badge_frame, text=ft.upper(), fg=type_col(ft), bg=BG3,
                             font=(FNU, 7, 'bold'), padx=7, pady=2,
                             highlightthickness=1, highlightbackground=BD)
            badge.pack(anchor='e', pady=(3, 0))

        price_sub = clean(p.get('lastPriceDate'))
        
        # ── Row 1: Price & Dividend Panel ──
        r1 = tk.Frame(card, bg=BG3, padx=10, pady=7, highlightthickness=1, highlightbackground=BD)
        r1.pack(fill='x', padx=8, pady=(8, 4))
        
        # Left: Price
        p_frame = tk.Frame(r1, bg=BG3)
        p_frame.pack(side='left', fill='x', expand=True)
        tk.Label(p_frame, text='FİYAT', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(p_frame, text=fmt_price(last_price) or '--', fg=BL, bg=BG3, font=(FN, 12, 'bold')).pack(anchor='w')
        if price_sub:
            tk.Label(p_frame, text=price_sub, fg=TX4, bg=BG3, font=(FNU, 7)).pack(anchor='w')
            
        # Divider
        tk.Frame(r1, bg=BD, width=1).pack(side='left', fill='y', padx=8)
        
        # Right: Div/Q
        d_frame = tk.Frame(r1, bg=BG3)
        d_frame.pack(side='left', fill='x', expand=True)
        tk.Label(d_frame, text='DIV / Q', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(d_frame, text=fmt_div(p.get('div')) or '--', fg=TE, bg=BG3, font=(FN, 12, 'bold')).pack(anchor='w')
        if p.get('div'):
            tk.Label(d_frame, text='Çeyreklik', fg=TX4, bg=BG3, font=(FNU, 7)).pack(anchor='w')

        # ── Row 2: Coupon & Yield Profile Panel ──
        r2 = tk.Frame(card, bg=BG3, padx=10, pady=7, highlightthickness=1, highlightbackground=BD)
        r2.pack(fill='x', padx=8, pady=4)
        
        col1 = tk.Frame(r2, bg=BG3)
        col1.pack(side='left', fill='x', expand=True)
        
        # Coupon & Current Yield side-by-side!
        cy_row = tk.Frame(col1, bg=BG3)
        cy_row.pack(fill='x', anchor='w')
        
        c_cell = tk.Frame(cy_row, bg=BG3)
        c_cell.pack(side='left', padx=(0, 12))
        tk.Label(c_cell, text='KUPON', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(c_cell, text=clean(p.get('coupon')) or '--', fg=GD, bg=BG3, font=(FN, 11, 'bold')).pack(anchor='w')
        
        y_cell = tk.Frame(cy_row, bg=BG3)
        y_cell.pack(side='left')
        tk.Label(y_cell, text='CURRENT YIELD', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        y_color = GR if current_yield not in (None, '') else TX3
        tk.Label(y_cell, text=fmt_pct(current_yield) or '--', fg=y_color, bg=BG3, font=(FN, 11, 'bold')).pack(anchor='w')
        
        # Divider
        tk.Frame(r2, bg=BD, width=1).pack(side='left', fill='y', padx=8)
        
        col2 = tk.Frame(r2, bg=BG3)
        col2.pack(side='left', fill='x', expand=True)
        
        # YTC & YTM side-by-side
        ytc_row = tk.Frame(col2, bg=BG3)
        ytc_row.pack(fill='x', anchor='w')
        
        ytc_cell = tk.Frame(ytc_row, bg=BG3)
        ytc_cell.pack(side='left', padx=(0, 12))
        tk.Label(ytc_cell, text='YTC', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(ytc_cell, text=ytc or '--', fg=AM, bg=BG3, font=(FN, 10, 'bold')).pack(anchor='w')
        
        ytm_cell = tk.Frame(ytc_row, bg=BG3)
        ytm_cell.pack(side='left')
        tk.Label(ytm_cell, text='YTM', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(ytm_cell, text=ytm or '--', fg=TE, bg=BG3, font=(FN, 10, 'bold')).pack(anchor='w')
        
        date_items = []
        if valid_date_text(call):
            date_items.append(('CALL', call, AM))
        if valid_date_text(mature):
            date_items.append(('MATURE', mature, TE))
        if date_items:
            date_row = tk.Frame(card, bg=BG3, padx=10, pady=6,
                                highlightthickness=1, highlightbackground=BD)
            date_row.pack(fill='x', padx=8, pady=4)
            for i, (lbl, val, col) in enumerate(date_items):
                date_cell = tk.Frame(date_row, bg=BG3)
                date_cell.pack(side='left', fill='x', expand=True)
                tk.Label(date_cell, text=lbl, fg=TX5, bg=BG3,
                         font=(FNU, 7, 'bold')).pack(anchor='w')
                tk.Label(date_cell, text=val, fg=col, bg=BG3,
                         font=(FN, 10, 'bold')).pack(anchor='w')
                if i < len(date_items) - 1:
                    tk.Frame(date_row, bg=BD, width=1).pack(side='left', fill='y', padx=8)

        # ── Row 3: Rating & Liquidity Panel ──
        r3 = tk.Frame(card, bg=BG3, padx=10, pady=7, highlightthickness=1, highlightbackground=BD)
        r3.pack(fill='x', padx=8, pady=4)
        
        # Left: Rating
        rat_frame = tk.Frame(r3, bg=BG3)
        rat_frame.pack(side='left', fill='x', expand=True)
        tk.Label(rat_frame, text='RATING DERECESİ', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(rat_frame, text=clean(p.get('rating')) or '--', fg=rating_col(p.get('rating')), bg=BG3, font=(FN, 11, 'bold')).pack(anchor='w')
        
        # Divider
        tk.Frame(r3, bg=BD, width=1).pack(side='left', fill='y', padx=8)
        
        # Right: Liquidity
        liq_frame = tk.Frame(r3, bg=BG3)
        liq_frame.pack(side='left', fill='x', expand=True)
        tk.Label(liq_frame, text='LİKİDİTE >4M', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(liq_frame, text=clean(p.get('mn4')) or '--', fg=mn4_col(p.get('mn4')), bg=BG3, font=(FN, 11, 'bold')).pack(anchor='w')

        # Events (Earning only — dividend is now shown in header badge)
        earning = self._earning_for_common(parent)
        if earning:
            e_text = self._earning_text(earning)
            if e_text:
                evf = tk.Frame(card, bg=BG2)
                evf.pack(fill='x', padx=8, pady=(4, 5))
                is_past = self._earning_is_past(earning)
                bg = '#2a0f0f' if is_past else '#2a1f0b'
                fg = RD if is_past else AM
                tk.Label(evf, text=e_text, fg=fg, bg=bg,
                         font=(FNU, 8, 'bold'), padx=7, pady=4,
                         wraplength=260, justify='left',
                         highlightthickness=1,
                         highlightbackground=fg).pack(fill='x', padx=2)

        # Actions Panel
        af = tk.Frame(card, bg=BG2)
        af.pack(fill='x', padx=8, pady=(4, 8))
        self._btn(af, 'Düzenle', BL, lambda: self._open_pref_form(sym)).pack(side='left', padx=(0, 6))
        self._btn(af, 'Sil', RD, lambda: self._confirm_delete(sym)).pack(side='left')

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
    # ─── CEF VIEW ────────────────────────────────────
    def _render_cef_legacy(self, sym):
        f  = self._inner
        url = f"https://www.cefconnect.com/fund/{sym}"
        sectors  = self._cef_sectors(sym)
        cef_row  = self.cef.get(sym, {})
        nav_info = self._get_nav_for(sym)

        nav      = nav_info.get('nav')
        discount = nav_info.get('discount')
        fund_name= nav_info.get('fundName') or cef_row.get('fundName') or ''
        strategy = nav_info.get('strategy') or ''
        price    = cef_row.get('lastPrice')

        # ── Başlık ───────────────────────────────────
        tk.Label(f, text='⬡ CEF', fg=TX5, bg=BG, font=(FNU, 7)).pack(pady=(14,0))
        tk.Label(f, text=sym, fg=TX, bg=BG, font=(FN, 22, 'bold')).pack()
        if fund_name:
            tk.Label(f, text=fund_name, fg=TX2, bg=BG,
                     font=(FNU, 8), wraplength=272, justify='center').pack(pady=(1,0))
        if strategy:
            tk.Label(f, text=strategy, fg=TX4, bg=BG,
                     font=(FNU, 7), wraplength=272, justify='center').pack(pady=(1,4))

        # ── Fiyat pill ───────────────────────────────
        if price is not None:
            price_s = fmt_price(price) or '—'
            pf = tk.Frame(f, bg=ACC, padx=10, pady=3)
            pf.pack(pady=(2,8))
            tk.Label(pf, text='FİYAT', fg=TX5, bg=ACC, font=(FNU, 7)).pack(side='left', padx=(0,6))
            tk.Label(pf, text=price_s, fg=BL, bg=ACC, font=(FN, 12, 'bold')).pack(side='left')

        # ── NAV + Discount ana kart ───────────────────
        has_data = nav is not None or discount is not None
        kart = tk.Frame(f, bg=BG2, highlightthickness=1,
                        highlightbackground=TE if has_data else TX5)
        kart.pack(fill='x', padx=10, pady=(0,8))

        kh = tk.Frame(kart, bg=BG3)
        kh.pack(fill='x')
        tk.Label(kh, text='◈  NAV  &  DİSKONTO / PREMİUM',
                 fg=TE, bg=BG3, font=(FNU, 7, 'bold'),
                 padx=8, pady=5).pack(side='left')
        tk.Label(kh, text='cefdata.xlsx', fg=TX5, bg=BG3,
                 font=(FNU, 7), padx=6).pack(side='right')

        if not has_data:
            tk.Label(kart,
                     text='cefdata.xlsx dosyasinda bu ticker bulunamadi\nveya dosya henuz yuklenmedi.',
                     fg=TX4, bg=BG2, font=(FNU, 8),
                     justify='center', pady=10).pack()
        else:
            mrow = tk.Frame(kart, bg=BG2)
            mrow.pack(fill='x', padx=8, pady=(8,4))

            def _metric(parent, label, val_txt, col, sub_txt=''):
                cell = tk.Frame(parent, bg=BG3, padx=8, pady=6)
                cell.pack(side='left', fill='x', expand=True, padx=3)
                tk.Label(cell, text=label, fg=TX4, bg=BG3,
                         font=(FNU, 7)).pack(anchor='w')
                tk.Label(cell, text=val_txt, fg=col, bg=BG3,
                         font=(FN, 13, 'bold')).pack(anchor='w')
                if sub_txt:
                    tk.Label(cell, text=sub_txt, fg=TX4, bg=BG3,
                             font=(FNU, 7)).pack(anchor='w')

            nav_col = TE
            if nav is not None:
                try:
                    nav_s = f"${float(nav):.2f}"
                    if price is not None:
                        diff = float(nav) - float(price)
                        nav_sub = f"Fiyattan {'▲' if diff>0 else '▼'} ${abs(diff):.2f}"
                        nav_col = GR if diff > 0 else OR
                    else:
                        nav_sub = ''
                        nav_col = TE
                except Exception:
                    nav_s, nav_sub, nav_col = str(nav), '', TE
                _metric(mrow, 'NET VARLIK DEĞERİ (NAV)', nav_s, nav_col, nav_sub)

            disc_col = AM
            if discount is not None:
                try:
                    dv = float(discount)
                    disc_s   = f"{dv:+.2f}%"
                    disc_lbl = 'DİSKONTO' if dv < 0 else 'PREMİUM'
                    disc_col = GR if dv < -0.5 else (RD if dv > 0.5 else AM)
                    disc_sub = ('NAV\'dan ucuz ↓' if dv < -0.5
                                else 'NAV\'dan pahalı ↑' if dv > 0.5
                                else 'NAV\'a yakın')
                except Exception:
                    disc_s, disc_lbl, disc_col, disc_sub = str(discount), 'DİSK/PREM', TX2, ''
                _metric(mrow, disc_lbl, disc_s, disc_col, disc_sub)

            if discount is not None:
                try:
                    dv   = float(discount)
                    pct  = max(-30.0, min(30.0, dv))
                    bar_outer = tk.Frame(kart, bg=BG2)
                    bar_outer.pack(fill='x', padx=12, pady=(2,0))

                    top_lbl = tk.Frame(bar_outer, bg=BG2)
                    top_lbl.pack(fill='x')
                    tk.Label(top_lbl, text='−30%', fg=GR, bg=BG2, font=(FNU, 6)).pack(side='left')
                    tk.Label(top_lbl, text=f'{dv:+.2f}%', fg=disc_col, bg=BG2,
                             font=(FNU, 7, 'bold')).pack()
                    tk.Label(top_lbl, text='+30%', fg=RD, bg=BG2, font=(FNU, 6)).pack(side='right')

                    bar_c = tk.Canvas(bar_outer, bg=BG, highlightthickness=0, height=10)
                    bar_c.pack(fill='x', pady=2)

                    def _draw(c=bar_c, p=pct, col=disc_col):
                        c.update_idletasks()
                        w = c.winfo_width()
                        if w < 10: w = 260
                        mid = w // 2
                        fw  = int(abs(p) / 30.0 * mid)
                        c.delete('all')
                        c.create_rectangle(0, 3, w, 7, fill=BG3, width=0)
                        if fw > 0:
                            if p < 0:
                                c.create_rectangle(mid-fw, 2, mid, 8, fill=col, width=0)
                            else:
                                c.create_rectangle(mid, 2, mid+fw, 8, fill=col, width=0)
                        c.create_rectangle(mid-1, 0, mid+1, 10, fill=TX5, width=0)
                        tick = mid + int(p / 30.0 * mid)
                        c.create_rectangle(tick-1, 0, tick+1, 10, fill=TX, width=0)

                    bar_c.bind('<Configure>', lambda e: _draw())
                    bar_c.after(30, _draw)

                    bot_lbl = tk.Frame(bar_outer, bg=BG2)
                    bot_lbl.pack(fill='x')
                    tk.Label(bot_lbl, text='← DİSKONTO (ucuz)',
                             fg=GR, bg=BG2, font=(FNU, 6)).pack(side='left')
                    tk.Label(bot_lbl, text='PREMİUM (pahalı) →',
                             fg=RD, bg=BG2, font=(FNU, 6)).pack(side='right')
                    tk.Frame(kart, bg=BG2, height=8).pack()
                except Exception:
                    pass

        # ── Sektör / Endeks kartı ─────────────────────
        if sectors:
            sc = tk.Frame(f, bg=BG2, highlightthickness=1, highlightbackground=BD)
            sc.pack(fill='x', padx=10, pady=(0,6))
            sh = tk.Frame(sc, bg=BG3)
            sh.pack(fill='x')
            tk.Label(sh, text='◈  ENDEKS / SEKTÖR', fg=AM, bg=BG3,
                     font=(FNU, 7, 'bold'), padx=8, pady=5).pack(side='left')
            tk.Label(sc, text=', '.join(sectors), fg=TX, bg=BG2,
                     font=(FNU, 9), wraplength=260,
                     justify='left', padx=8, pady=6).pack(anchor='w')

        # ── Alt bilgi + butonlar ──────────────────────
        price_date = clean(cef_row.get('lastPriceDate'))
        if price_date:
            tk.Label(f, text=f"Yahoo fiyat: {price_date}",
                     fg=TX5, bg=BG, font=(FNU, 7)).pack(pady=(2,0))
        tk.Label(f, text=url, fg=TX5, bg=BG, font=(FN, 7),
                 cursor='hand2').pack(pady=(4,2))
        tk.Button(f, text='🔗  CEF Connect\'te Aç',
                  command=lambda: webbrowser.open(url),
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=14, pady=7, cursor='hand2').pack(pady=(0,6))
        self._btn(f, '✏ Endeks Düzenle', AM,
                  lambda: self._open_cef_form(sym)).pack(pady=(0,10))

    def _render_cef(self, sym):
        f = self._inner
        url = f"https://www.cefconnect.com/fund/{sym}"
        sectors = self._cef_sectors(sym)
        cef_row = self.cef.get(sym, {})
        nav_info = self._get_nav_for(sym)

        nav = nav_info.get('nav')
        discount = nav_info.get('discount')
        price = nav_info.get('lastPrice', cef_row.get('lastPrice'))
        fund_name = nav_info.get('fundName') or cef_row.get('fundName') or ''
        strategy = nav_info.get('strategy') or cef_row.get('strategy') or ''
        nav_date = clean(nav_info.get('navDate') or nav_info.get('cefConnectUpdated'))
        price_date = clean(nav_info.get('lastPriceDate') or cef_row.get('lastPriceDate'))
        pricing_loading = self._cef_pricing_info_needed(nav_info)
        pricing_error = ''
        if nav_info.get('pricingInfoError') and nav_info.get('pricingInfoPeriod') == self._turkey_refresh_period():
            pricing_error = clean(nav_info.get('pricingInfoError'))

        def num_color(value, good_when_negative=False):
            try:
                v = float(value)
            except Exception:
                return TX3
            if good_when_negative:
                return GR if v < -0.5 else (RD if v > 0.5 else AM)
            return GR if v > 0 else (RD if v < 0 else AM)

        def z_text(value):
            try:
                return f"{float(value):+.2f}"
            except Exception:
                return "--"

        def z_color(value):
            try:
                v = float(value)
            except Exception:
                return TX3
            return GR if v <= -1 else (RD if v >= 1 else AM)

        def metric(parent, label, value, color, sub=''):
            cell = tk.Frame(parent, bg=BG3, padx=7, pady=5,
                            highlightthickness=1, highlightbackground=BD)
            cell.pack(side='left', fill='x', expand=True, padx=2)
            tk.Label(cell, text=label, fg=TX5, bg=BG3,
                     font=(FNU, 7, 'bold')).pack(anchor='w')
            tk.Label(cell, text=value, fg=color, bg=BG3,
                     font=(FN, 11, 'bold')).pack(anchor='w')
            if sub:
                tk.Label(cell, text=sub, fg=TX4, bg=BG3,
                         font=(FNU, 7)).pack(anchor='w')

        card = tk.Frame(f, bg=BG2, highlightthickness=1,
                        highlightbackground=TE if (nav is not None or discount is not None) else BD)
        card.pack(fill='x', padx=8, pady=(8, 6))

        header = tk.Frame(card, bg=BG4)
        header.pack(fill='x')
        left = tk.Frame(header, bg=BG4)
        left.pack(side='left', fill='x', expand=True, padx=8, pady=6)
        tk.Label(left, text='CEF', fg=GD, bg=BG4,
                 font=(FNU, 7, 'bold')).pack(anchor='w')
        tk.Label(left, text=sym, fg=TX, bg=BG4,
                 font=(FN, 18, 'bold')).pack(anchor='w')
        if fund_name:
            tk.Label(left, text=fund_name, fg=TX2, bg=BG4,
                     font=(FNU, 8), wraplength=245, justify='left').pack(anchor='w')
        if strategy:
            tk.Label(left, text=strategy, fg=PU, bg=BG4,
                     font=(FNU, 7), wraplength=245, justify='left').pack(anchor='w', pady=(1,0))

        right = tk.Frame(header, bg=BG4)
        right.pack(side='right', padx=8, pady=7)
        source_txt = nav_date or price_date or 'daily'
        tk.Label(right, text=source_txt, fg=TX5, bg=BG4,
                 font=(FNU, 7)).pack(anchor='e')

        if nav is None and discount is None and price is None:
            tk.Label(card, text='CEFConnect/cefdata verisi henuz yok.',
                     fg=TX4, bg=BG2, font=(FNU, 8),
                     padx=10, pady=10).pack(fill='x')
        else:
            price_txt = fmt_price(price) or "--"
            nav_txt = fmt_price(nav) or "--"
            disc_txt = fmt_signed_pct(discount) or "--"

            nav_sub = ''
            nav_col = TE
            try:
                if nav is not None and price is not None:
                    diff = float(nav) - float(price)
                    nav_sub = f"{diff:+.2f} vs price"
                    nav_col = GR if diff > 0 else OR
            except Exception:
                pass

            # Consolidated Core Stats for CEF
            mrow = tk.Frame(card, bg=BG3, padx=10, pady=8, highlightthickness=1, highlightbackground=BD)
            mrow.pack(fill='x', padx=8, pady=6)
            
            # Left side: Price
            p_frame = tk.Frame(mrow, bg=BG3)
            p_frame.pack(side='left', fill='x', expand=True)
            tk.Label(p_frame, text='FİYAT', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
            tk.Label(p_frame, text=price_txt, fg=BL, bg=BG3, font=(FN, 12, 'bold')).pack(anchor='w')
            
            # Divider 1
            tk.Frame(mrow, bg=BD, width=1).pack(side='left', fill='y', padx=8)
            
            # Middle: NAV
            n_frame = tk.Frame(mrow, bg=BG3)
            n_frame.pack(side='left', fill='x', expand=True)
            tk.Label(n_frame, text='NAV', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
            tk.Label(n_frame, text=nav_txt, fg=nav_col, bg=BG3, font=(FN, 12, 'bold')).pack(anchor='w')
            if nav_sub:
                tk.Label(n_frame, text=nav_sub, fg=TX4, bg=BG3, font=(FNU, 7)).pack(anchor='w')
                
            # Divider 2
            tk.Frame(mrow, bg=BD, width=1).pack(side='left', fill='y', padx=8)
            
            # Right: ISK / PREM
            i_frame = tk.Frame(mrow, bg=BG3)
            i_frame.pack(side='left', fill='x', expand=True)
            tk.Label(i_frame, text='ISK / PREM', fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='w')
            tk.Label(i_frame, text=disc_txt, fg=num_color(discount, True), bg=BG3, font=(FN, 12, 'bold')).pack(anchor='w')

            if discount is not None:
                try:
                    dv = float(discount)
                    pct = max(-30.0, min(30.0, dv))
                    disc_col = num_color(dv, True)
                    bar_outer = tk.Frame(card, bg=BG2)
                    bar_outer.pack(fill='x', padx=10, pady=(2, 6))
                    top_lbl = tk.Frame(bar_outer, bg=BG2)
                    top_lbl.pack(fill='x')
                    tk.Label(top_lbl, text='Discount', fg=GR, bg=BG2,
                             font=(FNU, 6, 'bold')).pack(side='left')
                    tk.Label(top_lbl, text=f'{dv:+.2f}%', fg=disc_col, bg=BG2,
                             font=(FNU, 7, 'bold')).pack()
                    tk.Label(top_lbl, text='Premium', fg=RD, bg=BG2,
                             font=(FNU, 6, 'bold')).pack(side='right')
                    bar_c = tk.Canvas(bar_outer, bg=BG, highlightthickness=0, height=9)
                    bar_c.pack(fill='x', pady=2)

                    def draw_bar(c=bar_c, p=pct, col=disc_col):
                        c.update_idletasks()
                        w = c.winfo_width() or 260
                        mid = w // 2
                        fill_w = int(abs(p) / 30.0 * mid)
                        c.delete('all')
                        c.create_rectangle(0, 3, w, 6, fill=BG3, width=0)
                        if fill_w > 0:
                            if p < 0:
                                c.create_rectangle(mid-fill_w, 1, mid, 8, fill=col, width=0)
                            else:
                                c.create_rectangle(mid, 1, mid+fill_w, 8, fill=col, width=0)
                        c.create_rectangle(mid-1, 0, mid+1, 9, fill=TX5, width=0)
                        tick = mid + int(p / 30.0 * mid)
                        c.create_rectangle(tick-1, 0, tick+1, 9, fill=TX, width=0)

                    bar_c.bind('<Configure>', lambda e: draw_bar())
                    bar_c.after(30, draw_bar)
                except Exception:
                    pass

        stat_card = tk.Frame(f, bg=BG2, highlightthickness=1, highlightbackground=BD)
        stat_card.pack(fill='x', padx=8, pady=(0, 6))
        tk.Label(stat_card, text='CEFCONNECT PRICING INFORMATION',
                 fg=CY, bg=BG3, font=(FNU, 7, 'bold'),
                 padx=8, pady=5).pack(fill='x', anchor='w')

        pd_date = clean(nav_info.get('pricingInfoDate'))
        z_date = clean(nav_info.get('zScoreDate'))
        if pricing_loading or pricing_error:
            status = 'Pricing info cekiliyor...' if pricing_loading else f"Pricing info alinamadi: {pricing_error[:60]}"
            tk.Label(stat_card, text=status, fg=AM if pricing_loading else RD,
                     bg=BG2, font=(FNU, 7), padx=8, pady=4).pack(anchor='w')
        if pd_date or z_date:
            date_line = '  |  '.join(
                part for part in [f"P/D {pd_date}" if pd_date else '',
                                  f"Z {z_date}" if z_date else ''] if part)
            tk.Label(stat_card, text=date_line, fg=TX5, bg=BG2,
                     font=(FNU, 7), padx=8, pady=(5, 0)).pack(anchor='w')

        # Unified P/D historical averages row
        pd_row = tk.Frame(stat_card, bg=BG3, padx=8, pady=6, highlightthickness=1, highlightbackground=BD)
        pd_row.pack(fill='x', padx=6, pady=4)
        
        periods = [('P/D 6M', 'pdAvg6m'), ('P/D 1Y', 'pdAvg1y'), ('P/D 3Y', 'pdAvg3y'), ('P/D 5Y', 'pdAvg5y')]
        for i, (label, key) in enumerate(periods):
            val = nav_info.get(key)
            cell = tk.Frame(pd_row, bg=BG3)
            cell.pack(side='left', fill='x', expand=True)
            tk.Label(cell, text=label, fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='center')
            tk.Label(cell, text=fmt_signed_pct(val) or "--", fg=num_color(val, True), bg=BG3, font=(FN, 10, 'bold')).pack(anchor='center')
            if i < len(periods) - 1:
                tk.Frame(pd_row, bg=BD, width=1).pack(side='left', fill='y', padx=4)

        # Unified Z-Scores row
        z_row = tk.Frame(stat_card, bg=BG3, padx=8, pady=6, highlightthickness=1, highlightbackground=BD)
        z_row.pack(fill='x', padx=6, pady=4)
        
        z_periods = [('Z 3M', 'zScore3m'), ('Z 6M', 'zScore6m'), ('Z 1Y', 'zScore1y')]
        for i, (label, key) in enumerate(z_periods):
            val = nav_info.get(key)
            cell = tk.Frame(z_row, bg=BG3)
            cell.pack(side='left', fill='x', expand=True)
            tk.Label(cell, text=label, fg=TX5, bg=BG3, font=(FNU, 7, 'bold')).pack(anchor='center')
            tk.Label(cell, text=z_text(val), fg=z_color(val), bg=BG3, font=(FN, 10, 'bold')).pack(anchor='center')
            if i < len(z_periods) - 1:
                tk.Frame(z_row, bg=BD, width=1).pack(side='left', fill='y', padx=6)

        user_sectors = [clean(s) for s in self._cef_sectors(sym) if clean(s)]
        scraped_strategy = clean(nav_info.get('strategy') or cef_row.get('strategy'))
        scraped_category = clean(nav_info.get('categoryName') or cef_row.get('categoryName'))
        
        scraped_items = []
        for item in (scraped_strategy, scraped_category):
            if item and item not in user_sectors and item not in scraped_items:
                scraped_items.append(item)

        if user_sectors or scraped_items:
            sc = tk.Frame(f, bg=BG2, highlightthickness=1, highlightbackground=BD)
            sc.pack(fill='x', padx=8, pady=(0, 6))
            tk.Label(sc, text='ENDEKS / SEKTÖR', fg=AM, bg=BG3,
                     font=(FNU, 7, 'bold'), padx=8, pady=5).pack(fill='x', anchor='w')
            
            sf = tk.Frame(sc, bg=BG2, padx=8, pady=6)
            sf.pack(fill='x')
            
            if user_sectors:
                tk.Label(sf, text='Öncelikli Sektörler (Benim Tanımladıklarım):', fg=TX2, bg=BG2,
                         font=(FNU, 7, 'bold')).pack(anchor='w')
                tk.Label(sf, text=', '.join(user_sectors), fg=CY, bg=BG2,
                         font=(FNU, 8, 'bold'), wraplength=270, justify='left', pady=(2, 6)).pack(anchor='w')
                
            if scraped_items:
                tk.Label(sf, text='Ekstra CEFConnect Sektör/Kategori:', fg=TX5, bg=BG2,
                         font=(FNU, 7, 'bold')).pack(anchor='w')
                tk.Label(sf, text=', '.join(scraped_items), fg=TX3, bg=BG2,
                         font=(FNU, 8), wraplength=270, justify='left', pady=(2, 2)).pack(anchor='w')

        foot = tk.Frame(f, bg=BG)
        foot.pack(fill='x', padx=8, pady=(0, 10))
        if price_date:
            tk.Label(foot, text=f"price: {price_date}", fg=TX5, bg=BG,
                     font=(FNU, 7)).pack(anchor='w')
        if nav_date:
            tk.Label(foot, text=f"nav: {nav_date}", fg=TX5, bg=BG,
                     font=(FNU, 7)).pack(anchor='w')
        tk.Label(foot, text=url, fg=TX5, bg=BG, font=(FN, 7),
                 cursor='hand2').pack(anchor='w', pady=(3, 3))
        btns = tk.Frame(foot, bg=BG)
        btns.pack(fill='x')
        tk.Button(btns, text='Linke Git ↗',
                  command=lambda: webbrowser.open(url),
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 8, 'bold'), relief='flat', bd=0,
                  padx=12, pady=6, cursor='hand2').pack(side='left', padx=(0,5))
        self._btn(btns, 'Endeks Duzenle', AM,
                  lambda: self._open_cef_form(sym)).pack(side='left')

    def _render_cef_clean(self, sym):
        f = self._inner
        try:
            self._render_cef_clean_inner(sym, f)
        except Exception as exc:
            import traceback
            tb = traceback.format_exc()
            tk.Label(f, text=f'RENDER HATASI: {exc}', fg='#ff4444', bg=BG,
                     font=(FNU, 9, 'bold'), wraplength=300, justify='left',
                     padx=10, pady=10).pack(anchor='w')
            tk.Label(f, text=tb, fg=TX3, bg=BG,
                     font=(FNU, 7), wraplength=300, justify='left',
                     padx=10).pack(anchor='w')

    def _render_cef_clean_inner(self, sym, f):
        url = f"https://www.cefconnect.com/fund/{sym}"
        sectors = self._cef_sectors(sym)
        cef_row = self.cef.get(sym, {})
        nav_info = self._get_nav_for(sym)

        def _fb(key):
            """nav_info'dan al, yoksa cef_row'dan fallback."""
            v = nav_info.get(key)
            return v if v is not None else cef_row.get(key)

        price = _fb('lastPrice')
        nav = _fb('nav')
        discount = _fb('discount')
        pricing_loading = self._cef_pricing_info_needed(nav_info)
        pricing_error = ''
        if nav_info.get('pricingInfoError') and nav_info.get('pricingInfoPeriod') == self._turkey_refresh_period():
            pricing_error = clean(nav_info.get('pricingInfoError'))
        if pricing_loading:
            self._start_cef_pricing_info_fetch(sym)

        panel_bg = "#101820"
        panel_alt = "#0d1522"
        row_alt = "#132033"
        line_col = "#243247"
        head_col = "#86a33d"
        muted_col = "#7f8ea3"

        def pd_color(value):
            try:
                v = float(value)
            except Exception:
                return TX3
            return GR if v < -0.5 else (RD if v > 0.5 else AM)

        def z_text(value):
            try:
                return f"{float(value):.2f}"
            except Exception:
                return "--"

        def z_color(value):
            try:
                v = float(value)
            except Exception:
                return TX3
            return GR if v <= -1 else (RD if v >= 1 else AM)

        def fmt_pd(value):
            return fmt_pct(value) or "--"

        def panel(parent, title, subtitle='', accent=head_col):
            box = tk.Frame(parent, bg=panel_bg, highlightthickness=1,
                           highlightbackground=line_col)
            box.pack(fill='x', padx=8, pady=(0, 7))
            hf = tk.Frame(box, bg=panel_bg)
            hf.pack(fill='x', padx=10, pady=(8, 5))
            tk.Label(hf, text=title, fg=accent, bg=panel_bg,
                     font=(FNU, 10, 'bold')).pack(anchor='w')
            if subtitle:
                tk.Label(hf, text=subtitle, fg=TX2, bg=panel_bg,
                         font=(FNU, 8, 'bold')).pack(anchor='w', pady=(4, 0))
            return box

        def cell(parent, text, row, column, bg, fg=TX, weight='normal',
                 anchor='e', font_size=9):
            tk.Label(parent, text=text, fg=fg, bg=bg,
                     font=(FNU, font_size, weight), padx=7, pady=7,
                     anchor=anchor).grid(row=row, column=column, sticky='nsew')

        def draw_summary_table(parent):
            table = tk.Frame(parent, bg=line_col)
            table.pack(fill='x', padx=10, pady=(0, 10))
            for i, weight in enumerate((2, 1, 1, 1)):
                table.columnconfigure(i, weight=weight)

            headers = ['', 'Share\nPrice', 'NAV', 'Premium/\nDiscount']
            for i, label in enumerate(headers):
                cell(table, label, 0, i, panel_alt, TX2, 'bold',
                     'w' if i == 0 else 'e', 8)

            rows = [
                ('Current', price, nav, discount),
                ('52 Wk Avg', _fb('price52Avg'),
                 _fb('nav52Avg'), _fb('discount52Avg')),
                ('52 Wk High', _fb('price52High'),
                 _fb('nav52High'), _fb('discount52High')),
                ('52 Wk Low', _fb('price52Low'),
                 _fb('nav52Low'), _fb('discount52Low')),
            ]
            for r, (label, share_v, nav_v, pd_v) in enumerate(rows, start=1):
                bg = panel_bg if r % 2 else row_alt
                cell(table, label, r, 0, bg, TX, 'bold', 'w', 9)
                cell(table, fmt_price(share_v) or "--", r, 1, bg, BL, 'bold')
                cell(table, fmt_price(nav_v) or "--", r, 2, bg, TE, 'bold')
                cell(table, fmt_pd(pd_v), r, 3, bg, pd_color(pd_v), 'bold')

        def draw_two_col_table(parent, rows, value_color_fn=None):
            table = tk.Frame(parent, bg=line_col)
            table.pack(fill='x', padx=10, pady=(0, 10))
            table.columnconfigure(0, weight=2)
            table.columnconfigure(1, weight=1)
            for r, (label, value) in enumerate(rows):
                bg = panel_bg if r % 2 == 0 else row_alt
                cell(table, label, r, 0, bg, TX, 'bold', 'w', 9)
                fg = value_color_fn(value) if value_color_fn else TX
                cell(table, value, r, 1, bg, fg, 'bold', 'e', 10)

        def draw_scale(parent, value, label, low=-20.0, high=20.0,
                       left_text='Discount', right_text='Premium'):
            try:
                v = float(value)
            except Exception:
                return
            wrap = tk.Frame(parent, bg=panel_bg)
            wrap.pack(fill='x', padx=10, pady=(0, 10))
            top = tk.Frame(wrap, bg=panel_bg)
            top.pack(fill='x')
            tk.Label(top, text=left_text, fg=GR, bg=panel_bg,
                     font=(FNU, 7, 'bold')).pack(side='left')
            tk.Label(top, text=f"{label}: {v:+.2f}", fg=pd_color(v), bg=panel_bg,
                     font=(FNU, 8, 'bold')).pack()
            tk.Label(top, text=right_text, fg=RD, bg=panel_bg,
                     font=(FNU, 7, 'bold')).pack(side='right')

            c = tk.Canvas(wrap, bg=panel_alt, highlightthickness=0, height=18)
            c.pack(fill='x', pady=(4, 0))

            def paint(canvas=c, val=v):
                canvas.update_idletasks()
                w = max(canvas.winfo_width(), 1)
                h = 18
                mid = int((0 - low) / (high - low) * w)
                pos = int((max(low, min(high, val)) - low) / (high - low) * w)
                canvas.delete('all')
                canvas.create_rectangle(0, 8, w, 10, fill=line_col, width=0)
                canvas.create_rectangle(mid - 1, 3, mid + 1, h - 3, fill=TX5, width=0)
                canvas.create_rectangle(pos - 2, 2, pos + 2, h - 2, fill=pd_color(val), width=0)

            c.bind('<Configure>', lambda e: paint())
            c.after(30, paint)

        category_groups = self._cef_category_groups_for_symbol(sym)
        if not category_groups:
            category_groups = self._cef_indexes(sym, nav_info, cef_row)
        if category_groups:
            top_box = panel(f, 'Endeks / Sektör', accent=CY)
            tk.Label(top_box, text='  '.join(category_groups), fg=CY, bg=panel_bg,
                     font=(FNU, 11, 'bold'), wraplength=285, justify='left',
                     padx=10).pack(anchor='w', pady=(0, 10))

        summary_box = panel(f, f"CEF  {sym}",
                            clean(_fb('cefSummaryAsOf')),
                            accent=head_col)
        if pricing_loading or pricing_error:
            status = 'Detay cache girişte hazırlanıyor; tıklama istek atmaz.' if pricing_loading else f"CEFConnect alinamadi: {pricing_error[:70]}"
            tk.Label(summary_box, text=status, fg=AM if pricing_loading else RD,
                     bg=panel_bg, font=(FNU, 7), padx=10).pack(anchor='w', pady=(0, 6))
        if price is None and nav is None and discount is None:
            tk.Label(summary_box, text='CEFConnect/cefdata verisi henuz yok.',
                     fg=muted_col, bg=panel_bg, font=(FNU, 8),
                     padx=10).pack(anchor='w', pady=(0, 10))
        draw_summary_table(summary_box)
        draw_scale(summary_box, discount, 'Current P/D')

        pd_box = panel(f, 'Premium/Discount Information',
                       clean(nav_info.get('pricingInfoDate')), accent=head_col)
        pd_rows = [
            ('6 Month', fmt_pd(_fb('pdAvg6m'))),
            ('1 Year', fmt_pd(_fb('pdAvg1y'))),
            ('3 Year', fmt_pd(_fb('pdAvg3y'))),
            ('5 Year', fmt_pd(_fb('pdAvg5y'))),
        ]
        draw_two_col_table(pd_box, pd_rows,
                           lambda v: pd_color(self._parse_cef_number(v, percent=True)))

        z_box = panel(f, 'Z-Score', clean(nav_info.get('zScoreDate')),
                      accent=head_col)
        z_rows = [
            ('3 Month', z_text(_fb('zScore3m'))),
            ('6 Month', z_text(_fb('zScore6m'))),
            ('1 Year', z_text(_fb('zScore1y'))),
        ]
        draw_two_col_table(z_box, z_rows,
                           lambda v: z_color(self._parse_cef_number(v)))
        draw_scale(z_box, _fb('zScore1y'), '1Y Z', low=-3.0, high=3.0,
                   left_text='Cheap', right_text='Rich')

        foot = tk.Frame(f, bg=BG)
        foot.pack(fill='x', padx=8, pady=(0, 10))
        tk.Label(foot, text=url, fg=TX5, bg=BG, font=(FN, 7),
                 cursor='hand2').pack(anchor='w', pady=(3, 3))
        btns = tk.Frame(foot, bg=BG)
        btns.pack(fill='x')
        tk.Button(btns, text='Linke Git ->',
                  command=lambda: webbrowser.open(url),
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 8, 'bold'), relief='flat', bd=0,
                  padx=12, pady=6, cursor='hand2').pack(side='left', padx=(0,5))
        self._btn(btns, 'Endeks Duzenle', AM,
                  lambda: self._open_cef_form(sym)).pack(side='left')

    def _render_notfound(self, sym):
        f = self._inner
        tk.Label(f, text='⬡', fg=TX5, bg=BG, font=(FN, 24)).pack(pady=(40,8))
        tk.Label(f, text=f'{sym} — Listede Bulunamadı', fg=TX4, bg=BG,
                 font=(FNU, 9)).pack()
        tk.Label(f, text='Preferred eklemek için ＋ butonunu kullanın',
                 fg=TX5, bg=BG, font=(FNU, 7)).pack(pady=4)


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
                cef_set = self._cef_tickers()
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
        sym = ''
        for candidate in (self.current, self._sv.get() if hasattr(self, '_sv') else ''):
            text = clean(candidate).upper()
            if text and text not in self.pref and re.fullmatch(r'[A-Z0-9.\-]{1,12}', text):
                sym = text
                break
        self._open_cef_form(sym)

    def _take_data(self):
        sym = self.current
        if sym and self._is_cef_symbol(sym) and sym not in self.pref:
            self._set_scan_status('DATA...', AM)
            def cef_worker():
                ok = False
                try:
                    quote = self._fetch_yahoo_price_info(sym, preferred=False)
                    self._apply_cef_market_data(
                        sym, quote.get('price'), quote.get('symbol'),
                        quote.get('priceDate'))
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
                quote = self._fetch_yahoo_price_info(sym, preferred=True)
                price = quote.get('price')
                result['yahooSymbol'] = quote.get('symbol')
                result['lastPrice'] = price
                result['lastPriceDate'] = quote.get('priceDate')
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
            p = self._apply_pref_market_data(
                sym, new_price, result.get('yahooSymbol', sym),
                result.get('lastPriceDate'))
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

    # ─── TRADE JOURNAL ───────────────────────────────
    def _trade_default_ticker(self):
        for raw in (self.current, self._sv.get() if hasattr(self, '_sv') else ''):
            sym = clean(raw).upper()
            if sym and re.fullmatch(r'[A-Z0-9.\-]{1,12}', sym):
                return sym
        return 'UNKNOWN'

    def _trade_grade(self, avg):
        if avg >= 4.5:
            return 'A+', 'Exceptional Setup', 'Strong Buy Candidate'
        if avg >= 4.0:
            return 'A', 'High Quality', 'Valid Setup'
        if avg >= 3.5:
            return 'B', 'Decent', 'Caution'
        if avg >= 3.0:
            return 'C', 'Weak', 'Caution'
        return 'D', 'Avoid Trade', 'Avoid Trade'

    def _trade_records_dir(self, dt):
        return os.path.join(_app_root(), 'records', dt.strftime('%Y'), dt.strftime('%m'))

    def _save_trade_record(self, record):
        try:
            dt = datetime.strptime(record['date'], '%Y-%m-%d')
        except Exception:
            dt = datetime.now()
        safe_ticker = re.sub(r'[^A-Z0-9.\-]+', '_', clean(record.get('ticker')).upper()).strip('_')
        if not safe_ticker:
            safe_ticker = 'UNKNOWN'
        folder = self._trade_records_dir(dt)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{record['date']}_{safe_ticker}.json")
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
        return path
    def _open_div_export(self):
        """Open month picker dialog and export dividend TXT."""
        dlg = tk.Toplevel(self.root)
        dlg.title('Dividend Export')
        dlg.geometry('320x260')
        self._style_window(dlg)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text='⬇ DIVIDEND EXPORT', fg=AM, bg=BG2,
                 font=(FNU, 9, 'bold'), padx=8, pady=7).pack(fill='x')
        tk.Frame(dlg, bg=BD, height=1).pack(fill='x')

        sf = tk.Frame(dlg, bg=BG, padx=14)
        sf.pack(fill='both', expand=True, pady=8)

        MONTHS_TR = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran',
                     'Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
        now = date.today()

        tk.Label(sf, text='AY', fg=TX5, bg=BG, font=(FNU, 7, 'bold')).pack(anchor='w')
        month_var = tk.StringVar(value=MONTHS_TR[now.month - 1])
        m_menu = tk.OptionMenu(sf, month_var, *MONTHS_TR)
        m_menu.config(bg=BG2, fg=TX, activebackground=ACC, activeforeground=BL,
                      font=(FN, 10), relief='flat', bd=0, highlightthickness=0, indicatoron=0)
        m_menu['menu'].config(bg=BG2, fg=TX, activebackground=ACC)
        m_menu.pack(fill='x', pady=(0, 8))

        tk.Label(sf, text='YIL', fg=TX5, bg=BG, font=(FNU, 7, 'bold')).pack(anchor='w')
        year_var = tk.StringVar(value=str(now.year))
        y_menu = tk.OptionMenu(sf, year_var, '2026', '2027', '2028')
        y_menu.config(bg=BG2, fg=TX, activebackground=ACC, activeforeground=BL,
                      font=(FN, 10), relief='flat', bd=0, highlightthickness=0, indicatoron=0)
        y_menu['menu'].config(bg=BG2, fg=TX, activebackground=ACC)
        y_menu.pack(fill='x', pady=(0, 8))

        status_var = tk.StringVar()
        tk.Label(sf, textvariable=status_var, fg=GR, bg=BG,
                 font=(FNU, 8)).pack(anchor='w', pady=4)

        def do_export():
            month_idx = MONTHS_TR.index(month_var.get()) + 1
            year = int(year_var.get())

            # Build dividend map for the selected month
            import calendar as cal_mod
            num_days = cal_mod.monthrange(year, month_idx)[1]
            dmap = {}

            # Collect all tickers from _DIV_CALENDAR + pref overrides
            all_divs = dict(_DIV_CALENDAR)  # ticker -> (lastDate, period)
            for sym, p in self.pref.items():
                if p.get('divDate'):
                    all_divs[sym.upper()] = (p['divDate'], p.get('divFreq', 'quarterly'))

            for ticker, (last_date, period) in all_divs.items():
                interval = 3 if period == 'quarterly' else 1
                try:
                    last = date.fromisoformat(last_date)
                except Exception:
                    continue
                for n in range(0, 200):
                    projected = _add_months(last, n * interval)
                    adjusted = _div_adjust_date(projected)
                    if adjusted.year == year and adjusted.month == month_idx:
                        entry = {'ticker': ticker, 'period': period}
                        dmap.setdefault(adjusted.day, []).append(entry)
                    if adjusted.year > year or (adjusted.year == year and adjusted.month > month_idx):
                        break

            for day in dmap:
                dmap[day].sort(key=lambda x: (0 if x['period'] == 'monthly' else 1, x['ticker']))

            # Generate text
            lines = []
            for day in range(1, num_days + 1):
                lines.append(str(day))
                for t in dmap.get(day, []):
                    prefix = '[M]' if t['period'] == 'monthly' else ''
                    lines.append(f"{prefix}{t['ticker']}")
            text = '\n'.join(lines)

            month_name = MONTHS_TR[month_idx - 1].lower()
            default_fn = f"dividends_{month_name}_{year}.txt"
            path = filedialog.asksaveasfilename(
                defaultextension='.txt',
                initialfile=default_fn,
                filetypes=[('Text files', '*.txt'), ('All files', '*.*')],
                title='Dividend Listesi Kaydet',
                parent=dlg
            )
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                total = sum(len(v) for v in dmap.values())
                status_var.set(f'✓ {total} ticker, {path.split("/")[-1]}')

        ff = tk.Frame(dlg, bg=BG2)
        ff.pack(fill='x', side='bottom')
        tk.Frame(ff, bg=BD, height=1).pack(fill='x')
        tk.Button(ff, text='⬇ EXPORT TXT', command=do_export,
                  bg=ACC, fg=BL, activebackground=BL2, activeforeground=BG,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=12, pady=6, cursor='hand2').pack(fill='x', padx=8, pady=6)

    def _open_trade_panel(self):
        if self._trade_win and self._trade_win.winfo_exists():
            self._trade_win.lift()
            return

        win = tk.Toplevel(self.root)
        self._trade_win = win
        win.title('TRADE - Pre-Trade Evaluation')
        win.geometry('370x640')
        win.minsize(315, 520)
        self._style_window(win)
        win.transient(self.root)
        win.grab_set()
        win.protocol('WM_DELETE_WINDOW', lambda: (setattr(self, '_trade_win', None), win.destroy()))

        state = {
            'idx': 0,
            'answers': [],
            'score': None,
            'score_buttons': [],
            'saved_path': '',
        }

        # Header
        hdr = tk.Frame(win, bg=BG2, highlightthickness=1, highlightbackground=ACC)
        hdr.pack(fill='x')
        tk.Label(hdr, text='TRADE', fg=TE, bg=BG2,
                 font=(FNU, 10, 'bold'), padx=8, pady=7).pack(side='left')
        ticker_var = tk.StringVar(value=self._trade_default_ticker())
        ticker_entry = tk.Entry(hdr, textvariable=ticker_var, bg=BG, fg=BL,
                                insertbackground=BL, font=(FN, 10, 'bold'),
                                relief='flat', bd=0, width=12,
                                justify='center')
        ticker_entry.pack(side='left', padx=(4, 0), ipady=3)
        tk.Button(hdr, text='x', command=lambda: (setattr(self, '_trade_win', None), win.destroy()),
                  bg=BG2, fg=TX4, activebackground=BG3, activeforeground=TX,
                  font=(FNU, 9, 'bold'), relief='flat', bd=0,
                  padx=8, pady=4, cursor='hand2').pack(side='right', padx=5, pady=3)

        prog = tk.Frame(win, bg=BG)
        prog.pack(fill='x', padx=8, pady=(8, 4))
        qnum_lbl = tk.Label(prog, text='', fg=BL, bg=BG, font=(FNU, 8, 'bold'))
        qnum_lbl.pack(side='left')
        avg_lbl = tk.Label(prog, text='AVG -', fg=TX3, bg=BG, font=(FNU, 8, 'bold'))
        avg_lbl.pack(side='right')
        progress = tk.Canvas(win, height=8, bg=BG2, highlightthickness=1,
                             highlightbackground=BD)
        progress.pack(fill='x', padx=8, pady=(0, 8))
        progress_fill = progress.create_rectangle(0, 0, 0, 8, fill=TE, width=0)

        terminal = tk.Text(win, bg=BG, fg=TX2, insertbackground=TE,
                           font=(FN, 8), relief='flat', bd=0,
                           highlightthickness=1, highlightbackground=BD,
                           height=11, wrap='word', padx=8, pady=8)
        terminal.pack(fill='both', expand=True, padx=8, pady=(0, 8))
        terminal.tag_config('prompt', foreground=BL)
        terminal.tag_config('answer', foreground=TX)
        terminal.tag_config('score', foreground=TE)
        terminal.tag_config('warn', foreground=AM)
        terminal.configure(state='disabled')

        q_frame = tk.Frame(win, bg=BG2, highlightthickness=1, highlightbackground=ACC)
        q_frame.pack(fill='x', padx=8, pady=(0, 8))
        question_lbl = tk.Label(q_frame, text='', fg=TX, bg=BG2,
                                font=(FNU, 9, 'bold'), justify='left',
                                wraplength=320, padx=8, pady=8)
        question_lbl.pack(fill='x')

        quick_frame = tk.Frame(win, bg=BG)
        quick_frame.pack(fill='x', padx=8, pady=(0, 6))
        tk.Label(quick_frame, text='> quick answer', fg=TX5, bg=BG,
                 font=(FNU, 7)).pack(anchor='w')
        quick_btn_box = tk.Frame(quick_frame, bg=BG)
        quick_btn_box.pack(fill='x')

        answer_lbl = tk.Label(win, text='> answer', fg=TX5, bg=BG, font=(FNU, 7))
        answer_lbl.pack(anchor='w', padx=10)
        answer_box = tk.Text(win, bg=BG2, fg=TX, insertbackground=TE,
                             font=(FN, 9), relief='flat', bd=0,
                             highlightthickness=1, highlightbackground=BD,
                             highlightcolor=TE, height=4, wrap='word',
                             padx=7, pady=6)
        answer_box.pack(fill='x', padx=8, pady=(2, 8))

        score_frame = tk.Frame(win, bg=BG)
        score_frame.pack(fill='x', padx=8, pady=(0, 6))
        score_note = tk.Label(score_frame, text='Score: select 1-5', fg=TX5, bg=BG,
                              font=(FNU, 7))
        score_note.pack(anchor='w', pady=(0, 3))
        score_btn_row = tk.Frame(score_frame, bg=BG)
        score_btn_row.pack(fill='x')

        result_frame = tk.Frame(win, bg=BG2, highlightthickness=1, highlightbackground=TE)

        footer = tk.Frame(win, bg=BG2)
        footer.pack(fill='x', side='bottom')
        status_lbl = tk.Label(footer, text='ENTER = next', fg=TX5, bg=BG2, font=(FNU, 7))
        status_lbl.pack(side='left', padx=8)
        next_btn = tk.Button(footer, text='ENTER / NEXT', bg=ACC, fg=TE,
                             activebackground=TE, activeforeground=BG,
                             font=(FNU, 8, 'bold'), relief='flat', bd=0,
                             padx=10, pady=6, cursor='hand2')
        next_btn.pack(side='right', padx=8, pady=6)

        def log(text, tag=None):
            terminal.configure(state='normal')
            if tag:
                terminal.insert('end', text + '\n', tag)
            else:
                terminal.insert('end', text + '\n')
            terminal.see('end')
            terminal.configure(state='disabled')

        def calc_avg(include_current=True):
            scores = [x['score'] for x in state['answers']]
            if include_current and state['score'] is not None:
                scores.append(state['score'])
            if not scores:
                return None
            return round(sum(scores) / len(scores), 2)

        def update_average():
            avg = calc_avg(True)
            if avg is None:
                avg_lbl.config(text='AVG -', fg=TX3)
            else:
                col = GR if avg >= 4 else (AM if avg >= 3 else RD)
                avg_lbl.config(text=f'AVG {avg:.2f}', fg=col)

        def update_progress():
            total = len(TRADE_QUESTIONS)
            done = len(state['answers'])
            pct = done / total if total else 0
            w = progress.winfo_width()
            if w < 20:
                w = 330
            progress.coords(progress_fill, 0, 0, int(w * pct), 8)

        def set_score(score):
            state['score'] = score
            for n, btn in state['score_buttons']:
                selected = n == score
                btn.config(bg=ACC if selected else BG2,
                           fg=TE if selected else TX3,
                           highlightbackground=TE if selected else BD)
            score_note.config(text=f"Score: {score} = {TRADE_SCORE_LABELS[score]}", fg=TE)
            status_lbl.config(text='ENTER = next', fg=TX5)
            update_average()
            answer_box.focus_set()

        def set_quick_answer(answer, score):
            answer_box.configure(state='normal')
            answer_box.delete('1.0', 'end')
            answer_box.insert('1.0', answer)
            set_score(score)
            status_lbl.config(text='quick answer selected', fg=TE)

        def build_quick_answers(question):
            for child in quick_btn_box.winfo_children():
                child.destroy()

            options = TRADE_ANSWER_OPTIONS.get(question, [])
            if not options:
                quick_frame.pack_forget()
                return
            if not quick_frame.winfo_ismapped():
                quick_frame.pack(fill='x', padx=8, pady=(0, 6), before=answer_lbl)

            for label, answer, score in options:
                b = tk.Label(quick_btn_box, text=label, bg=BG2, fg=TX3,
                             font=(FNU, 7, 'bold'), cursor='hand2',
                             padx=5, pady=4, highlightthickness=1,
                             highlightbackground=BD)
                b.pack(side='left', expand=True, fill='x', padx=2, pady=(2, 0))
                b.bind('<Button-1>', lambda e, a=answer, s=score: set_quick_answer(a, s))
                b.bind('<Enter>', lambda e, x=b: x.config(bg=ACC, fg=TX))
                b.bind('<Leave>', lambda e, x=b: x.config(bg=BG2, fg=TX3))

        for n in range(1, 6):
            b = tk.Label(score_btn_row, text=str(n), bg=BG2, fg=TX3,
                         font=(FN, 11, 'bold'), cursor='hand2',
                         padx=11, pady=5, highlightthickness=1,
                         highlightbackground=BD)
            b.pack(side='left', expand=True, fill='x', padx=2)
            b.bind('<Button-1>', lambda e, s=n: set_score(s))
            state['score_buttons'].append((n, b))
        tk.Label(score_frame,
                 text='1 Very Bad  |  2 Weak  |  3 Neutral  |  4 Good  |  5 Excellent',
                 fg=TX5, bg=BG, font=(FNU, 7), wraplength=330,
                 justify='left').pack(anchor='w', pady=(4, 0))

        def show_question():
            if state['idx'] >= len(TRADE_QUESTIONS):
                show_result()
                return
            q = TRADE_QUESTIONS[state['idx']]
            qnum_lbl.config(text=f"QUESTION {state['idx'] + 1}/{len(TRADE_QUESTIONS)}")
            question_lbl.config(text=q)
            build_quick_answers(q)
            answer_box.configure(state='normal')
            answer_box.delete('1.0', 'end')
            state['score'] = None
            for _, btn in state['score_buttons']:
                btn.config(bg=BG2, fg=TX3, highlightbackground=BD)
            score_note.config(text='Score: select 1-5', fg=TX5)
            status_lbl.config(text='ENTER = next', fg=TX5)
            update_average()
            update_progress()
            answer_box.focus_set()

        def submit_current():
            if state['idx'] >= len(TRADE_QUESTIONS):
                return
            answer = answer_box.get('1.0', 'end').strip()
            if not answer:
                status_lbl.config(text='Answer required', fg=AM)
                answer_box.focus_set()
                return
            if state['score'] is None:
                status_lbl.config(text='Score required', fg=AM)
                return

            q = TRADE_QUESTIONS[state['idx']]
            score = int(state['score'])
            state['answers'].append({'question': q, 'answer': answer, 'score': score})
            log(f"> Q{state['idx'] + 1}: {q}", 'prompt')
            log(f"  {answer}", 'answer')
            log(f"  score {score}/5 - {TRADE_SCORE_LABELS[score]}", 'score')
            log("")
            state['idx'] += 1
            answer_box.configure(state='disabled')
            status_lbl.config(text='loading next...', fg=TX5)
            win.after(90, show_question)

        def on_answer_return(e):
            if e.state & 0x0001:
                return None
            submit_current()
            return 'break'

        def show_result():
            answer_box.pack_forget()
            answer_lbl.pack_forget()
            quick_frame.pack_forget()
            score_frame.pack_forget()
            q_frame.pack_forget()
            next_btn.config(text='CLOSE', command=lambda: (setattr(self, '_trade_win', None), win.destroy()))

            avg = round(sum(x['score'] for x in state['answers']) / len(state['answers']), 2)
            grade, grade_desc, status = self._trade_grade(avg)
            now = datetime.now()
            ticker = clean(ticker_var.get()).upper() or 'UNKNOWN'
            record = {
                'ticker': ticker,
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'average_score': avg,
                'grade': grade,
                'grade_description': grade_desc,
                'status': status,
                'questions': state['answers'],
                'post_trade_review': {
                    'closed': False,
                    'close_date': '',
                    'exit_price': None,
                    'pnl': None,
                    'notes': '',
                    'lessons': '',
                },
                'analytics': {
                    'setup_type': '',
                    'sector': '',
                    'overnight_hold': None,
                    'risk_reward': '',
                },
                'schema_version': 1,
            }

            try:
                state['saved_path'] = self._save_trade_record(record)
                save_text = f"Saved: {state['saved_path']}"
            except Exception as exc:
                save_text = f"Save failed: {exc}"

            update_progress()
            avg_lbl.config(text=f'AVG {avg:.2f}', fg=GR if avg >= 4 else (AM if avg >= 3 else RD))
            qnum_lbl.config(text='COMPLETE')
            result_frame.pack(fill='x', padx=8, pady=(0, 8))
            for child in result_frame.winfo_children():
                child.destroy()
            tk.Label(result_frame, text=f"Average Score: {avg:.2f}", fg=TX, bg=BG2,
                     font=(FN, 12, 'bold'), padx=10, pady=5).pack(anchor='w')
            tk.Label(result_frame, text=f"Grade: {grade} ({grade_desc})", fg=TE, bg=BG2,
                     font=(FNU, 10, 'bold'), padx=10, pady=3).pack(anchor='w')
            tk.Label(result_frame, text=f"Status: {status}", fg=BL, bg=BG2,
                     font=(FNU, 10, 'bold'), padx=10, pady=3).pack(anchor='w')
            tk.Label(result_frame, text='Post Trade Review section initialized for later closeout.',
                     fg=TX5, bg=BG2, font=(FNU, 7), padx=10, pady=5).pack(anchor='w')

            log("=== FINAL RESULT ===", 'prompt')
            log(f"Average Score: {avg:.2f}", 'answer')
            log(f"Grade: {grade} ({grade_desc})", 'score')
            log(f"Status: {status}", 'score')
            log(save_text, 'warn' if save_text.startswith('Save failed') else 'answer')
            status_lbl.config(text='record saved' if state['saved_path'] else 'save failed',
                              fg=GR if state['saved_path'] else RD)

        def resize_text(e=None):
            try:
                question_lbl.config(wraplength=max(260, win.winfo_width() - 36))
                update_progress()
            except Exception:
                pass

        next_btn.config(command=submit_current)
        answer_box.bind('<Return>', on_answer_return)
        progress.bind('<Configure>', lambda e: update_progress())
        win.bind('<Configure>', resize_text)
        log('TRADE terminal ready.', 'prompt')
        log('Pick a quick answer or type your own, then press ENTER.', 'answer')
        log('')
        show_question()

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
        self._style_window(dlg)
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
        self._style_window(dlg)
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
        self._style_window(dlg)
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

    def _open_pref_form(self, sym):
        p = self.pref.get(sym, {}) if sym else {}
        parent_val = self.ptoc.get(sym, '') if sym else ''
        is_edit = sym is not None

        dlg = tk.Toplevel(self.root)
        dlg.title(f'{"Düzenle" if is_edit else "Ekle"} — Preferred')
        dlg.geometry('340x580')
        self._style_window(dlg)
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

        # Dividend calendar fields
        tk.Frame(sf, bg=BD, height=1).pack(fill='x', pady=6)
        tk.Label(sf, text='DIVIDEND TAKVİM', fg=AM, bg=BG,
                 font=(FNU, 7, 'bold')).pack(anchor='w')
        # Pre-fill divDate from _DIV_CALENDAR if user hasn't set one
        cal_entry = _DIV_CALENDAR.get((sym or '').upper())
        default_div_date = p.get('divDate', '') or (cal_entry[0] if cal_entry else '')
        default_div_freq = p.get('divFreq', '') or (cal_entry[1] if cal_entry else 'quarterly')
        row('Ex-Div Tarihi', 'divDate', default_div_date)
        freq_choices = ['quarterly', 'monthly', '']
        row('Div Sıklığı', 'divFreq', default_div_freq, choices=freq_choices)

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
            old_s = clean(sym).upper() if is_edit else ''
            if is_edit and s != old_s and s in self.pref:
                messagebox.showerror('Hata', 'Bu ticker zaten var.', parent=dlg)
                return
            try:
                div_v = float(get_val('div')) if get_val('div').strip() else None
            except ValueError:
                div_v = None

            if is_edit and old_s and s != old_s:
                pref_row = dict(self.pref.pop(old_s, {}))
                old_parent = self.ptoc.pop(old_s, None)
                if old_parent and not get_val('parent').strip():
                    self.ptoc[s] = old_parent
            else:
                pref_row = dict(self.pref.get(s, {}))
            pref_row.update({
                'fixFloat':   get_val('fixFloat'),
                'coupon':     get_val('coupon').strip(),
                'div':        div_v,
                'callDate':   get_val('callDate').strip(),
                'matureDate': get_val('matureDate').strip(),
                'rating':     get_val('rating'),
                'mn4':        get_val('mn4'),
                'divDate':    get_val('divDate').strip() or None,
                'divFreq':    get_val('divFreq') or None,
            })
            self.pref[s] = pref_row
            parent_s = get_val('parent').strip().upper()
            if parent_s:
                self.ptoc[s] = parent_s
            else:
                self.ptoc.pop(s, None)

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
        sym = clean(sym).upper()
        c = self.common.get(sym, {})

        dlg = tk.Toplevel(self.root)
        dlg.title(f'Common — {sym}')
        dlg.geometry('340x460')
        self._style_window(dlg)
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
            if not s:
                messagebox.showerror('Hata', 'Ticker zorunludur!', parent=dlg)
                return
            old_s = clean(sym).upper()
            if old_s and s != old_s and s in self.common:
                messagebox.showerror('Hata', 'Bu common zaten var.', parent=dlg)
                return
            if old_s and s != old_s:
                common_row = dict(self.common.pop(old_s, {}))
                for pref_sym, parent_sym in list(self.ptoc.items()):
                    if clean(parent_sym).upper() == old_s:
                        self.ptoc[pref_sym] = s
                if old_s in self._common_expanded:
                    self._common_expanded[s] = self._common_expanded.pop(old_s)
            else:
                common_row = dict(self.common.get(s, {}))
            common_row.update({
                'sector': get_val('sector'), 'marketCap': get_val('marketCap'),
                'altman': get_val('altman'), 'currentRatio': get_val('currentRatio'),
                'de': get_val('de'), 'roicWacc': get_val('roicWacc'),
                'comment': get_val('comment'),
            })
            self.common[s] = common_row
            _save('common_data.json', self.common)
            _save('pref_to_common.json', self.ptoc)
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
        self._style_window(dlg)
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
