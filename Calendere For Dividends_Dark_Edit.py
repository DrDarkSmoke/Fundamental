#!/usr/bin/env python3
"""
Dividend Ex-Date Calendar
Run: python dividend_calendar.py
Requires: Python 3.8+ (no extra installs needed)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
import json
import os
from datetime import date, timedelta

# ─── TRY TO IMPORT DATEUTIL, FALL BACK TO MANUAL ─────────────────────────────
try:
    from dateutil.relativedelta import relativedelta
    def add_months(d, n):
        return d + relativedelta(months=n)
except ImportError:
    def add_months(d, n):
        month = d.month - 1 + n
        year = d.year + month // 12
        month = month % 12 + 1
        day = min(d.day, [31,28+int((year%4==0 and(year%100!=0 or year%400==0))),
                          31,30,31,30,31,31,30,31,30,31][month-1])
        return date(year, month, day)

# ─── NYSE HOLIDAYS ────────────────────────────────────────────────────────────
HOLIDAYS = {
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

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
DAYS_SHORT = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

# ─── TICKER DATA ─────────────────────────────────────────────────────────────
QUARTERLY_RAW = [
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

MONTHLY_RAW = [
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

CUSTOM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_tickers.json")
OVERRIDES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticker_date_overrides.json")

# ─── DATE LOGIC ──────────────────────────────────────────────────────────────
def is_holiday(d):
    return d in HOLIDAYS

def is_market_closed(d):
    return d.weekday() >= 5 or is_holiday(d)

def legacy_adjust_date(d):
    if d.weekday() == 5:  # Saturday → go backward
        while d.weekday() in (5, 6) or is_holiday(d):
            d -= timedelta(days=1)
    else:  # Sunday or holiday → go forward
        while d.weekday() == 6 or is_holiday(d):
            d += timedelta(days=1)
    return d

def legacy_get_date_in_month(last_date_str, period, target_year, target_month):
    interval = 3 if period == "quarterly" else 1
    last = date.fromisoformat(last_date_str)
    for n in range(1, 121):
        candidate = add_months(last, n * interval)
        if candidate.year == target_year and candidate.month == target_month:
            return candidate
        if candidate.year > target_year or (candidate.year == target_year and candidate.month > target_month):
            return None
    return None

def legacy_load_custom():
    if os.path.exists(CUSTOM_FILE):
        with open(CUSTOM_FILE) as f:
            return json.load(f)
    return []

def legacy_save_custom(data):
    with open(CUSTOM_FILE, "w") as f:
        json.dump(data, f, indent=2)

def legacy_build_dividend_map(year, month, custom_tickers):
    all_tickers = (
        [dict(t, period="quarterly", source="excel") for t in QUARTERLY_RAW] +
        [dict(t, period="monthly", source="excel") for t in MONTHLY_RAW] +
        custom_tickers
    )
    dmap = {}
    for t in all_tickers:
        projected = legacy_get_date_in_month(t["lastDate"], t["period"], year, month)
        if not projected:
            continue
        adjusted = legacy_adjust_date(projected)
        if adjusted.year != year or adjusted.month != month:
            continue
        day = adjusted.day
        dmap.setdefault(day, []).append(t)
    for day in dmap:
        dmap[day].sort(key=lambda x: (0 if x["period"]=="monthly" else 1, x["ticker"]))
    return dmap

def legacy_generate_text(year, month, dmap):
    import calendar
    num_days = calendar.monthrange(year, month)[1]
    lines = [f"{MONTHS[month-1].upper()} {year} — EX-DIVIDEND LIST", "=" * 40, ""]
    for day in range(1, num_days + 1):
        if day in dmap:
            lines.append(str(day))
            for t in dmap[day]:
                lines.append(t["ticker"])
    return "\n".join(lines)

# ─── GUI ─────────────────────────────────────────────────────────────────────
def adjust_date(d):
    while is_market_closed(d):
        d -= timedelta(days=1)
    return d

def month_index(year, month):
    return (year * 12) + month

def iter_occurrences_for_month(last_date_str, period, target_year, target_month):
    interval = 3 if period == "quarterly" else 1
    last = date.fromisoformat(last_date_str)
    target_idx = month_index(target_year, target_month)
    hits = []
    for n in range(0, 121):
        projected = add_months(last, n * interval)
        adjusted = adjust_date(projected)
        if month_index(adjusted.year, adjusted.month) == target_idx:
            hits.append((projected, adjusted))
    return hits

def load_custom():
    if os.path.exists(CUSTOM_FILE):
        try:
            with open(CUSTOM_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(
                "Custom tickers",
                "custom_tickers.json could not be read. Custom entries were loaded as empty.",
            )
    return []

def load_overrides():
    if os.path.exists(OVERRIDES_FILE):
        try:
            with open(OVERRIDES_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(
                "Date overrides",
                "ticker_date_overrides.json could not be read. Built-in date fixes were loaded as empty.",
            )
    return []

def save_custom(data):
    with open(CUSTOM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_overrides(data):
    with open(OVERRIDES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def ticker_key(ticker, period):
    return (ticker.strip().upper(), period)

def get_builtin_tickers():
    return (
        [dict(t, period="quarterly", source="excel") for t in QUARTERLY_RAW]
        + [dict(t, period="monthly", source="excel") for t in MONTHLY_RAW]
    )

def apply_overrides(tickers, date_overrides):
    override_map = {
        ticker_key(item["ticker"], item["period"]): item["lastDate"]
        for item in date_overrides
    }
    merged = []
    for ticker in tickers:
        entry = dict(ticker)
        original_last_date = entry["lastDate"]
        override_last_date = override_map.get(ticker_key(entry["ticker"], entry["period"]))
        if override_last_date:
            entry["lastDate"] = override_last_date
            entry["baseLastDate"] = original_last_date
            entry["overridden"] = override_last_date != original_last_date
        else:
            entry["baseLastDate"] = original_last_date
            entry["overridden"] = False
        merged.append(entry)
    return merged

def get_all_tickers(custom_tickers, date_overrides):
    builtin = apply_overrides(get_builtin_tickers(), date_overrides)
    custom = [dict(item, overridden=False, baseLastDate=item["lastDate"]) for item in custom_tickers]
    return builtin + custom

def build_dividend_map(year, month, custom_tickers, ticker_filter="", date_overrides=None):
    all_tickers = get_all_tickers(custom_tickers, date_overrides or [])
    dmap = {}
    ticker_filter = ticker_filter.strip().upper()
    for ticker in all_tickers:
        if ticker_filter and ticker_filter not in ticker["ticker"].upper():
            continue
        for projected, adjusted in iter_occurrences_for_month(
            ticker["lastDate"], ticker["period"], year, month
        ):
            entry = dict(ticker)
            entry["projectedDate"] = projected.isoformat()
            entry["effectiveDate"] = adjusted.isoformat()
            entry["adjusted"] = projected != adjusted
            dmap.setdefault(adjusted.day, []).append(entry)

    for day in dmap:
        dmap[day].sort(
            key=lambda item: (
                0 if item["period"] == "monthly" else 1,
                item["ticker"],
            )
        )
    return dmap

def generate_text(year, month, dmap):
    num_days = calendar.monthrange(year, month)[1]
    lines = []
    for day in range(1, num_days + 1):
        lines.append(str(day))
        for ticker in dmap.get(day, []):
            lines.append(ticker["ticker"])
    return "\n".join(lines)

class LegacyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dividend Ex-Date Calendar")
        self.geometry("820x680")
        self.configure(bg="#0a0e1a")
        self.resizable(True, True)
        self.custom_tickers = load_custom()

        # Style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#0f1628", background="#0f1628",
                        foreground="#e0f0ff", selectbackground="#1a2540",
                        selectforeground="#00d4ff", font=("Courier New", 10))
        style.configure("Treeview", background="#0f1628", foreground="#e0f0ff",
                        fieldbackground="#0f1628", font=("Courier New", 10),
                        rowheight=22)
        style.configure("Treeview.Heading", background="#0d1525", foreground="#4ec9b0",
                        font=("Courier New", 10, "bold"))
        style.map("Treeview", background=[("selected","#1a2e50")])

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        BG, FG, ACC = "#0a0e1a", "#e0f0ff", "#00d4ff"
        BTN = dict(bg="#0f1628", fg=ACC, font=("Courier New", 10, "bold"),
                   relief="flat", bd=0, padx=14, pady=7, cursor="hand2",
                   activebackground="#1a2540", activeforeground=ACC)
        BTN2 = dict(bg="#0f1628", fg="#4ec9b0", font=("Courier New", 10, "bold"),
                    relief="flat", bd=0, padx=14, pady=7, cursor="hand2",
                    activebackground="#1a2540", activeforeground="#4ec9b0")
        BTN3 = dict(bg="#0f1628", fg="#ffa94d", font=("Courier New", 10, "bold"),
                    relief="flat", bd=0, padx=14, pady=7, cursor="hand2",
                    activebackground="#1a2540", activeforeground="#ffa94d")

        # Title
        tk.Label(self, text="◆ EX-DIVIDEND CALENDAR ◆",
                 bg=BG, fg=ACC, font=("Courier New", 14, "bold")).pack(pady=(16,4))
        tk.Label(self, text="NYSE HOLIDAY + WEEKEND ADJUSTED",
                 bg=BG, fg="#1e3a50", font=("Courier New", 8)).pack()

        # Controls bar
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill="x", padx=16, pady=10)

        tk.Label(ctrl, text="MONTH", bg=BG, fg="#2a5080",
                 font=("Courier New", 8)).pack(side="left", padx=(0,4))
        now = date.today()
        self.month_var = tk.StringVar(value=MONTHS[now.month - 1].upper())
        month_cb = ttk.Combobox(ctrl, textvariable=self.month_var,
                                values=[m.upper() for m in MONTHS],
                                width=10, state="readonly")
        month_cb.pack(side="left", padx=(0,12))

        tk.Label(ctrl, text="YEAR", bg=BG, fg="#2a5080",
                 font=("Courier New", 8)).pack(side="left", padx=(0,4))
        self.year_var = tk.StringVar(value=str(now.year))
        year_cb = ttk.Combobox(ctrl, textvariable=self.year_var,
                               values=["2026","2027","2028"],
                               width=6, state="readonly")
        year_cb.pack(side="left", padx=(0,12))

        tk.Button(ctrl, text="▸ VIEW", command=self._refresh, **BTN).pack(side="left", padx=4)
        tk.Button(ctrl, text="⬇ EXTRACT .TXT", command=self._extract, **BTN2).pack(side="left", padx=4)
        tk.Button(ctrl, text="+ ADD TICKER", command=self._add_dialog, **BTN3).pack(side="left", padx=4)
        if self.custom_tickers:
            tk.Button(ctrl, text="⚙ MANAGE", command=self._manage_dialog,
                      bg="#0f1628", fg="#ff6b6b", font=("Courier New",10,"bold"),
                      relief="flat", bd=0, padx=10, pady=7, cursor="hand2",
                      activebackground="#1a2540").pack(side="left", padx=4)

        # Stats bar
        self.stats_var = tk.StringVar()
        tk.Label(self, textvariable=self.stats_var, bg=BG, fg="#2a5080",
                 font=("Courier New", 9)).pack()

        # Tree
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=16, pady=(6,16))

        cols = ("day", "dow", "tickers", "count")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                 selectmode="browse")
        self.tree.heading("day",     text="DAY")
        self.tree.heading("dow",     text="")
        self.tree.heading("tickers", text="TICKERS")
        self.tree.heading("count",   text="#")
        self.tree.column("day",     width=50,  stretch=False, anchor="center")
        self.tree.column("dow",     width=38,  stretch=False, anchor="center")
        self.tree.column("tickers", width=600, stretch=True,  anchor="w")
        self.tree.column("count",   width=40,  stretch=False, anchor="center")

        self.tree.tag_configure("has",   background="#0c1422", foreground="#e0f0ff")
        self.tree.tag_configure("empty", background="#0a0e1a", foreground="#131f35")
        self.tree.tag_configure("wknd",  background="#0a0e1a", foreground="#2a1515")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _get_sel(self):
        m = MONTHS.index(self.month_var.get().capitalize()) + 1
        y = int(self.year_var.get())
        return y, m

    def _refresh(self):
        y, m = self._get_sel()
        import calendar
        dmap = build_dividend_map(y, m, self.custom_tickers)
        num_days = calendar.monthrange(y, m)[1]
        for row in self.tree.get_children():
            self.tree.delete(row)

        dow_names = ["Mon","Tue","Wed","Thu","Fri","SAT","SUN"]
        total = sum(len(v) for v in dmap.values())
        monthly_c = sum(1 for v in dmap.values() for t in v if t["period"]=="monthly")
        quarterly_c = sum(1 for v in dmap.values() for t in v if t["period"]=="quarterly")
        custom_c   = sum(1 for v in dmap.values() for t in v if t.get("source")=="custom")
        self.stats_var.set(
            f"  Monthly: {monthly_c}   Quarterly: {quarterly_c}   Custom: {custom_c}   Total: {total}"
        )

        for day in range(1, num_days + 1):
            d = date(y, m, day)
            dow = d.weekday()
            dow_str = dow_names[dow]
            weekend = dow >= 5
            hol = is_holiday(d)
            tickers = dmap.get(day, [])
            if tickers:
                ticker_str = "  ".join(
                    f"[M]{t['ticker']}" if t["period"]=="monthly"
                    else f"★{t['ticker']}" if t.get("source")=="custom"
                    else t["ticker"]
                    for t in tickers
                )
                tag = "has"
            else:
                ticker_str = "—" if not (weekend or hol) else ""
                tag = "wknd" if (weekend or hol) else "empty"
            self.tree.insert("", "end",
                values=(str(day).zfill(2), dow_str, ticker_str, len(tickers) if tickers else ""),
                tags=(tag,))

    def _extract(self):
        y, m = self._get_sel()
        dmap = build_dividend_map(y, m, self.custom_tickers)
        text = generate_text(y, m, dmap)
        default = f"dividends_{MONTHS[m-1].lower()}_{y}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default,
            filetypes=[("Text files","*.txt"),("All files","*.*")],
            title="Save Dividend List"
        )
        if path:
            with open(path, "w") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"List saved to:\n{path}")

    def _add_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Ticker")
        dlg.geometry("360x280")
        dlg.configure(bg="#0a0e1a")
        dlg.grab_set()

        BG, FG = "#0a0e1a", "#e0f0ff"
        lbl = lambda txt: tk.Label(dlg, text=txt, bg=BG, fg="#2a5080",
                                   font=("Courier New",8), anchor="w")
        ent_style = dict(bg="#0f1628", fg="#e0f0ff", insertbackground="#e0f0ff",
                         font=("Courier New",11), relief="flat", bd=1,
                         highlightthickness=1, highlightcolor="#00d4ff",
                         highlightbackground="#1a2540")

        lbl("TICKER SYMBOL").pack(anchor="w", padx=24, pady=(20,2))
        ticker_e = tk.Entry(dlg, **ent_style); ticker_e.pack(fill="x", padx=24)

        lbl("PERIOD").pack(anchor="w", padx=24, pady=(12,2))
        period_var = tk.StringVar(value="monthly")
        pf = tk.Frame(dlg, bg=BG); pf.pack(fill="x", padx=24)
        for p in ["monthly","quarterly"]:
            tk.Radiobutton(pf, text=p.upper(), variable=period_var, value=p,
                           bg=BG, fg="#4ec9b0", selectcolor="#0f1628",
                           activebackground=BG, activeforeground="#4ec9b0",
                           font=("Courier New",9)).pack(side="left", padx=8)

        lbl("LAST EX-DIV DATE (YYYY-MM-DD)").pack(anchor="w", padx=24, pady=(12,2))
        date_e = tk.Entry(dlg, **ent_style); date_e.pack(fill="x", padx=24)

        err_var = tk.StringVar()
        tk.Label(dlg, textvariable=err_var, bg=BG, fg="#ff6b6b",
                 font=("Courier New",8)).pack(pady=4)

        def confirm():
            ticker = ticker_e.get().strip().upper()
            period = period_var.get()
            last = date_e.get().strip()
            if not ticker:
                err_var.set("Ticker required"); return
            try:
                date.fromisoformat(last)
            except ValueError:
                err_var.set("Date must be YYYY-MM-DD"); return
            self.custom_tickers.append(
                {"ticker": ticker, "period": period, "lastDate": last, "source": "custom"}
            )
            save_custom(self.custom_tickers)
            self._refresh()
            dlg.destroy()

        tk.Button(dlg, text="+ ADD", command=confirm,
                  bg="#0f1628", fg="#4ec9b0", font=("Courier New",11,"bold"),
                  relief="flat", bd=0, padx=20, pady=8, cursor="hand2",
                  activebackground="#1a2540").pack(pady=(4,0))

    def _manage_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Manage Custom Tickers")
        dlg.geometry("480x360")
        dlg.configure(bg="#0a0e1a")
        dlg.grab_set()

        BG = "#0a0e1a"
        tk.Label(dlg, text="CUSTOM TICKERS", bg=BG, fg="#ffa94d",
                 font=("Courier New",11,"bold")).pack(pady=(16,8))

        frame = tk.Frame(dlg, bg=BG); frame.pack(fill="both", expand=True, padx=16)
        cols = ("ticker","period","lastDate")
        tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse", height=10)
        tree.heading("ticker",   text="TICKER")
        tree.heading("period",   text="PERIOD")
        tree.heading("lastDate", text="LAST DATE")
        tree.column("ticker",   width=120, anchor="center")
        tree.column("period",   width=100, anchor="center")
        tree.column("lastDate", width=120, anchor="center")
        for t in self.custom_tickers:
            tree.insert("", "end", values=(t["ticker"], t["period"].upper(), t["lastDate"]))
        tree.pack(fill="both", expand=True)

        def delete_sel():
            sel = tree.selection()
            if not sel: return
            idx = tree.index(sel[0])
            self.custom_tickers.pop(idx)
            save_custom(self.custom_tickers)
            tree.delete(sel[0])
            self._refresh()

        tk.Button(dlg, text="✕ DELETE SELECTED", command=delete_sel,
                  bg="#0f1628", fg="#ff6b6b", font=("Courier New",10,"bold"),
                  relief="flat", bd=0, padx=16, pady=7, cursor="hand2",
                  activebackground="#1a2540").pack(pady=12)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.palette = {
            "bg": "#090f1d",
            "surface": "#111827",
            "surface_alt": "#182235",
            "border": "#263246",
            "text": "#e5edf8",
            "muted": "#8ea0bb",
            "accent": "#39d0ad",
            "accent_soft": "#15373a",
            "blue": "#6ea8ff",
            "blue_soft": "#16273d",
            "amber": "#f2b35d",
            "amber_soft": "#382917",
            "danger": "#ff7d86",
            "danger_soft": "#3d1d26",
            "holiday_soft": "#2c2520",
        }
        self.title("Dividend Ex-Date Calendar")
        self.geometry("1160x820")
        self.minsize(980, 700)
        self.configure(bg=self.palette["bg"])
        self.custom_tickers = load_custom()
        self.date_overrides = load_overrides()
        self.row_payload = {}
        self.stat_vars = {}
        self.context_var = tk.StringVar()
        self.notice_var = tk.StringVar()
        self.filter_var = tk.StringVar()
        self._build_styles()
        self._build_ui()
        self._sync_custom_button()
        self._refresh()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "App.TCombobox",
            padding=7,
            fieldbackground=self.palette["surface"],
            background=self.palette["surface"],
            foreground=self.palette["text"],
            bordercolor=self.palette["border"],
            arrowcolor=self.palette["accent"],
            relief="flat",
        )
        style.map(
            "App.TCombobox",
            fieldbackground=[("readonly", self.palette["surface"])],
            foreground=[("readonly", self.palette["text"])],
            selectbackground=[("readonly", self.palette["accent_soft"])],
            selectforeground=[("readonly", self.palette["text"])],
        )
        style.configure(
            "Calendar.Treeview",
            background=self.palette["surface"],
            fieldbackground=self.palette["surface"],
            foreground=self.palette["text"],
            bordercolor=self.palette["border"],
            rowheight=30,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Calendar.Treeview.Heading",
            background=self.palette["surface_alt"],
            foreground=self.palette["text"],
            bordercolor=self.palette["border"],
            relief="flat",
            padding=(10, 8),
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "Calendar.Treeview",
            background=[("selected", self.palette["accent_soft"])],
            foreground=[("selected", self.palette["text"])],
        )

    def _make_card(self, parent, bg=None):
        return tk.Frame(
            parent,
            bg=bg or self.palette["surface"],
            highlightbackground=self.palette["border"],
            highlightthickness=1,
            bd=0,
        )

    def _make_button(self, parent, text, command, tone="primary"):
        styles = {
            "primary": (self.palette["accent"], "#08120f", "#2db796"),
            "secondary": (self.palette["blue"], "#08111c", "#588fdc"),
            "warm": (self.palette["amber"], "#1b1308", "#d89b46"),
            "danger": (self.palette["danger"], "#17090c", "#e16870"),
            "muted": (self.palette["surface_alt"], self.palette["text"], "#202d44"),
        }
        bg, fg, active = styles[tone]
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active,
            activeforeground=fg,
            disabledforeground="#9ca39d",
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
        )

    def _make_stat_card(self, parent, title, bg):
        card = self._make_card(parent, bg=bg)
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(
            card,
            text=title.upper(),
            bg=bg,
            fg=self.palette["muted"],
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w", padx=16, pady=(14, 6))
        value_var = tk.StringVar(value="0")
        tk.Label(
            card,
            textvariable=value_var,
            bg=bg,
            fg=self.palette["text"],
            font=("Georgia", 20, "bold"),
        ).pack(anchor="w", padx=16, pady=(0, 14))
        return value_var

    def _build_ui(self):
        shell = tk.Frame(self, bg=self.palette["bg"])
        shell.pack(fill="both", expand=True, padx=24, pady=24)

        header = self._make_card(shell)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Dividend Calendar",
            bg=self.palette["surface"],
            fg=self.palette["text"],
            font=("Georgia", 22, "bold"),
        ).pack(anchor="w", padx=22, pady=(18, 4))
        tk.Label(
            header,
            text="Projected ex-dividend dates with NYSE weekend and holiday handling.",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=22)
        tk.Label(
            header,
            textvariable=self.context_var,
            bg=self.palette["surface"],
            fg=self.palette["accent"],
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w", padx=22, pady=(8, 18))

        controls = self._make_card(shell)
        controls.pack(fill="x", pady=(14, 12))

        top_row = tk.Frame(controls, bg=self.palette["surface"])
        top_row.pack(fill="x", padx=20, pady=(18, 12))

        selectors = tk.Frame(top_row, bg=self.palette["surface"])
        selectors.pack(side="left", fill="x", expand=True)

        tk.Label(
            selectors,
            text="Month",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI Semibold", 9),
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))
        tk.Label(
            selectors,
            text="Year",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI Semibold", 9),
        ).grid(row=0, column=1, sticky="w", padx=(0, 12))

        years = sorted({d.year for d in HOLIDAYS} | {date.today().year})
        now = date.today()
        default_year = now.year if now.year in years else years[0]
        self.month_var = tk.StringVar(value=MONTHS[now.month - 1])
        self.year_var = tk.StringVar(value=str(default_year))

        month_cb = ttk.Combobox(
            selectors,
            textvariable=self.month_var,
            values=MONTHS,
            width=14,
            state="readonly",
            style="App.TCombobox",
        )
        month_cb.grid(row=1, column=0, sticky="w", padx=(0, 12))
        month_cb.bind("<<ComboboxSelected>>", self._refresh)

        year_cb = ttk.Combobox(
            selectors,
            textvariable=self.year_var,
            values=[str(year) for year in years],
            width=8,
            state="readonly",
            style="App.TCombobox",
        )
        year_cb.grid(row=1, column=1, sticky="w", padx=(0, 12))
        year_cb.bind("<<ComboboxSelected>>", self._refresh)

        actions = tk.Frame(top_row, bg=self.palette["surface"])
        actions.pack(side="right")
        self.view_button = self._make_button(actions, "Refresh", self._refresh, "muted")
        self.view_button.pack(side="left", padx=4)
        self.export_button = self._make_button(actions, "Export TXT", self._extract, "secondary")
        self.export_button.pack(side="left", padx=4)
        self.add_button = self._make_button(actions, "Add ticker", self._add_dialog, "warm")
        self.add_button.pack(side="left", padx=4)
        self.manage_button = self._make_button(actions, "Manage data", self._manage_dialog, "primary")
        self.manage_button.pack(side="left", padx=4)

        search_row = tk.Frame(controls, bg=self.palette["surface"])
        search_row.pack(fill="x", padx=20, pady=(0, 18))
        tk.Label(
            search_row,
            text="Filter by ticker",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w")
        filter_wrap = tk.Frame(search_row, bg=self.palette["surface"])
        filter_wrap.pack(fill="x", pady=(6, 0))
        self.filter_entry = tk.Entry(
            filter_wrap,
            textvariable=self.filter_var,
            bg=self.palette["surface_alt"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            highlightcolor=self.palette["accent"],
            font=("Segoe UI", 10),
        )
        self.filter_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.filter_entry.bind("<KeyRelease>", self._refresh)
        clear_btn = self._make_button(filter_wrap, "Clear", self._clear_filter, "muted")
        clear_btn.pack(side="left", padx=(8, 0))

        stats = tk.Frame(shell, bg=self.palette["bg"])
        stats.pack(fill="x", pady=(0, 12))
        self.stat_vars["total"] = self._make_stat_card(stats, "Visible events", self.palette["accent_soft"])
        self.stat_vars["monthly"] = self._make_stat_card(stats, "Monthly", self.palette["blue_soft"])
        self.stat_vars["quarterly"] = self._make_stat_card(stats, "Quarterly", self.palette["surface_alt"])
        self.stat_vars["custom"] = self._make_stat_card(stats, "Custom / Fixes", self.palette["amber_soft"])

        legend = self._make_card(shell)
        legend.pack(fill="x", pady=(0, 12))
        legend_row = tk.Frame(legend, bg=self.palette["surface"])
        legend_row.pack(fill="x", padx=18, pady=(14, 8))
        for label, fg, bg in [
            ("M = monthly", self.palette["blue"], self.palette["blue_soft"]),
            ("Q = quarterly", self.palette["accent"], self.palette["accent_soft"]),
            ("Custom = your entries", self.palette["amber"], self.palette["amber_soft"]),
            ("Adjusted = moved to previous trading day", self.palette["danger"], self.palette["danger_soft"]),
        ]:
            tk.Label(
                legend_row,
                text=label,
                bg=bg,
                fg=fg,
                padx=10,
                pady=5,
                font=("Segoe UI Semibold", 9),
            ).pack(side="left", padx=(0, 8))
        tk.Label(
            legend,
            textvariable=self.notice_var,
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 14))

        table_card = self._make_card(shell)
        table_card.pack(fill="both", expand=True)
        tk.Label(
            table_card,
            text="Month view",
            bg=self.palette["surface"],
            fg=self.palette["text"],
            font=("Segoe UI Semibold", 11),
        ).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(
            table_card,
            text="Each row shows the effective ex-date after exchange-closed adjustments.",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 10))

        table_wrap = tk.Frame(table_card, bg=self.palette["surface"])
        table_wrap.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        cols = ("date", "day", "market", "preview", "flags", "count")
        self.tree = ttk.Treeview(
            table_wrap,
            columns=cols,
            show="headings",
            selectmode="browse",
            style="Calendar.Treeview",
        )
        self.tree.heading("date", text="Date")
        self.tree.heading("day", text="Day")
        self.tree.heading("market", text="Market")
        self.tree.heading("preview", text="Ticker preview")
        self.tree.heading("flags", text="Flags")
        self.tree.heading("count", text="Count")
        self.tree.column("date", width=70, anchor="center", stretch=False)
        self.tree.column("day", width=72, anchor="center", stretch=False)
        self.tree.column("market", width=100, anchor="center", stretch=False)
        self.tree.column("preview", width=450, anchor="w")
        self.tree.column("flags", width=240, anchor="w")
        self.tree.column("count", width=70, anchor="center", stretch=False)
        self.tree.tag_configure("event", background=self.palette["surface"], foreground=self.palette["text"])
        self.tree.tag_configure("custom", background=self.palette["amber_soft"], foreground=self.palette["text"])
        self.tree.tag_configure("quiet", background="#0f1626", foreground=self.palette["muted"])
        self.tree.tag_configure("closed", background=self.palette["holiday_soft"], foreground=self.palette["text"])

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

        detail_card = self._make_card(shell)
        detail_card.pack(fill="x", pady=(12, 0))
        tk.Label(
            detail_card,
            text="Selected day details",
            bg=self.palette["surface"],
            fg=self.palette["text"],
            font=("Segoe UI Semibold", 11),
        ).pack(anchor="w", padx=18, pady=(16, 8))

        detail_wrap = tk.Frame(detail_card, bg=self.palette["surface"])
        detail_wrap.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.detail_text = tk.Text(
            detail_wrap,
            height=8,
            wrap="word",
            bg=self.palette["surface"],
            fg=self.palette["text"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Consolas", 10),
            padx=4,
            pady=4,
        )
        detail_scroll = ttk.Scrollbar(detail_wrap, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scroll.set)
        self.detail_text.pack(side="left", fill="both", expand=True)
        detail_scroll.pack(side="right", fill="y")
        self._set_detail_text("Select a day to inspect its full ticker list.")

    def _sync_custom_button(self):
        custom_count = len(self.custom_tickers)
        override_count = len(self.date_overrides)
        self.manage_button.configure(
            text=f"Manage data ({custom_count} custom / {override_count} fixes)",
            state="normal",
        )

    def _clear_filter(self):
        if self.filter_var.get():
            self.filter_var.set("")
            self._refresh()

    def _set_detail_text(self, text):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")

    def _get_sel(self):
        month = MONTHS.index(self.month_var.get()) + 1
        year = int(self.year_var.get())
        return year, month

    def _format_preview(self, tickers):
        names = [ticker["ticker"] for ticker in tickers]
        if not names:
            return ""
        preview = ", ".join(names[:5])
        if len(names) > 5:
            preview += f", +{len(names) - 5} more"
        return preview

    def _format_flags(self, tickers):
        if not tickers:
            return ""
        monthly_count = sum(1 for ticker in tickers if ticker["period"] == "monthly")
        quarterly_count = sum(1 for ticker in tickers if ticker["period"] == "quarterly")
        custom_count = sum(1 for ticker in tickers if ticker.get("source") == "custom")
        corrected_count = sum(1 for ticker in tickers if ticker.get("overridden"))
        adjusted_count = sum(1 for ticker in tickers if ticker.get("adjusted"))
        flags = []
        if monthly_count:
            flags.append(f"M {monthly_count}")
        if quarterly_count:
            flags.append(f"Q {quarterly_count}")
        if custom_count:
            flags.append(f"Custom {custom_count}")
        if corrected_count:
            flags.append(f"Corrected {corrected_count}")
        if adjusted_count:
            flags.append(f"Adjusted {adjusted_count}")
        return " | ".join(flags)

    def _build_detail_text(self, current_date, tickers, market_label):
        lines = [
            f"{MONTHS[current_date.month - 1]} {current_date.day}, {current_date.year} ({DAYS_SHORT[current_date.weekday()]})",
            f"Market: {market_label}",
            "",
        ]
        if not tickers:
            lines.append("No dividend events for this day.")
            if market_label != "Open":
                lines.append("The market is closed on this date.")
            return "\n".join(lines)

        lines.append(f"Visible events: {len(tickers)}")
        lines.append("")
        for ticker in tickers:
            tags = ["Monthly" if ticker["period"] == "monthly" else "Quarterly"]
            if ticker.get("source") == "custom":
                tags.append("Custom")
            if ticker.get("overridden"):
                tags.append(f"Corrected from {ticker['baseLastDate']}")
            if ticker.get("adjusted"):
                tags.append(f"Adjusted from {ticker['projectedDate']}")
            lines.append(f"- {ticker['ticker']} | {' | '.join(tags)}")
        return "\n".join(lines)

    def _on_row_selected(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        payload = self.row_payload.get(selection[0])
        if payload:
            self._set_detail_text(payload)

    def _refresh(self, _event=None):
        year, month = self._get_sel()
        filter_text = self.filter_var.get().strip()
        current_selection = self.tree.selection()
        selected_day = None
        if current_selection:
            values = self.tree.item(current_selection[0], "values")
            if values:
                selected_day = int(values[0])

        dmap = build_dividend_map(year, month, self.custom_tickers, filter_text, self.date_overrides)
        num_days = calendar.monthrange(year, month)[1]
        total = sum(len(items) for items in dmap.values())
        monthly_count = sum(1 for items in dmap.values() for ticker in items if ticker["period"] == "monthly")
        quarterly_count = sum(1 for items in dmap.values() for ticker in items if ticker["period"] == "quarterly")
        custom_count = sum(1 for items in dmap.values() for ticker in items if ticker.get("source") == "custom")
        corrected_count = sum(1 for items in dmap.values() for ticker in items if ticker.get("overridden"))

        self.context_var.set(
            f"Viewing {MONTHS[month - 1]} {year}. Holiday coverage is loaded for 2026-2028."
        )
        if filter_text:
            self.notice_var.set(f'Filtered by "{filter_text.upper()}". Matching rows stay visible in the calendar.')
        else:
            self.notice_var.set(
                f"Tip: use the filter box to jump directly to a ticker symbol. Active date fixes: {len(self.date_overrides)}."
            )

        self.stat_vars["total"].set(str(total))
        self.stat_vars["monthly"].set(str(monthly_count))
        self.stat_vars["quarterly"].set(str(quarterly_count))
        self.stat_vars["custom"].set(str(custom_count + corrected_count))

        for row in self.tree.get_children():
            self.tree.delete(row)
        self.row_payload = {}

        day_to_item = {}
        for day in range(1, num_days + 1):
            current_date = date(year, month, day)
            weekend = current_date.weekday() >= 5
            holiday = is_holiday(current_date)
            if holiday:
                market_label = "Holiday"
            elif weekend:
                market_label = "Weekend"
            else:
                market_label = "Open"

            tickers = dmap.get(day, [])
            preview = self._format_preview(tickers)
            flags = self._format_flags(tickers)
            count_text = str(len(tickers)) if tickers else ""

            if tickers:
                tag = "custom" if any(ticker.get("source") == "custom" for ticker in tickers) else "event"
            elif market_label != "Open":
                preview = "Market closed"
                flags = "No events"
                tag = "closed"
            else:
                flags = "No events"
                tag = "quiet"

            item_id = self.tree.insert(
                "",
                "end",
                values=(str(day).zfill(2), DAYS_SHORT[current_date.weekday()], market_label, preview, flags, count_text),
                tags=(tag,),
            )
            day_to_item[day] = item_id
            self.row_payload[item_id] = self._build_detail_text(current_date, tickers, market_label)

        preferred_day = selected_day
        if preferred_day not in day_to_item:
            preferred_day = next((day for day in range(1, num_days + 1) if dmap.get(day)), 1)
        preferred_item = day_to_item.get(preferred_day)
        if preferred_item:
            self.tree.selection_set(preferred_item)
            self.tree.focus(preferred_item)
            self.tree.see(preferred_item)
            self._on_row_selected()

    def _extract(self):
        year, month = self._get_sel()
        dmap = build_dividend_map(year, month, self.custom_tickers, self.filter_var.get().strip(), self.date_overrides)
        text = generate_text(year, month, dmap)
        default = f"dividends_{MONTHS[month - 1].lower()}_{year}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Dividend List",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"List saved to:\n{path}")

    def _create_modal(self, title, geometry):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry(geometry)
        dlg.configure(bg=self.palette["bg"])
        dlg.transient(self)
        dlg.grab_set()
        return dlg

    def _add_dialog(self):
        dlg = self._create_modal("Add Ticker", "470x360")
        card = self._make_card(dlg)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            card,
            text="Add custom ticker",
            bg=self.palette["surface"],
            fg=self.palette["text"],
            font=("Georgia", 17, "bold"),
        ).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            card,
            text="Use the latest known ex-dividend date. Future months are projected from that anchor.",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 14))

        field_wrap = tk.Frame(card, bg=self.palette["surface"])
        field_wrap.pack(fill="x", padx=18)

        label_style = dict(bg=self.palette["surface"], fg=self.palette["muted"], font=("Segoe UI Semibold", 9))
        entry_style = dict(
            bg=self.palette["surface_alt"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            highlightcolor=self.palette["accent"],
            font=("Segoe UI", 11),
        )

        tk.Label(field_wrap, text="Ticker symbol", **label_style).pack(anchor="w")
        ticker_entry = tk.Entry(field_wrap, **entry_style)
        ticker_entry.pack(fill="x", ipady=8, pady=(6, 12))

        tk.Label(field_wrap, text="Period", **label_style).pack(anchor="w")
        period_var = tk.StringVar(value="monthly")
        period_row = tk.Frame(field_wrap, bg=self.palette["surface"])
        period_row.pack(fill="x", pady=(6, 12))
        for period in ("monthly", "quarterly"):
            tk.Radiobutton(
                period_row,
                text=period.title(),
                value=period,
                variable=period_var,
                bg=self.palette["surface"],
                fg=self.palette["text"],
                activebackground=self.palette["surface"],
                activeforeground=self.palette["text"],
                selectcolor=self.palette["accent_soft"],
                font=("Segoe UI", 10),
            ).pack(side="left", padx=(0, 14))

        tk.Label(field_wrap, text="Last ex-div date (YYYY-MM-DD)", **label_style).pack(anchor="w")
        date_entry = tk.Entry(field_wrap, **entry_style)
        date_entry.pack(fill="x", ipady=8, pady=(6, 8))

        err_var = tk.StringVar()
        tk.Label(
            card,
            textvariable=err_var,
            bg=self.palette["surface"],
            fg=self.palette["danger"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 12))

        button_row = tk.Frame(card, bg=self.palette["surface"])
        button_row.pack(fill="x", padx=18, pady=(0, 18))

        def confirm():
            ticker = ticker_entry.get().strip().upper()
            period = period_var.get()
            last_date = date_entry.get().strip()
            if not ticker:
                err_var.set("Ticker is required.")
                return
            try:
                date.fromisoformat(last_date)
            except ValueError:
                err_var.set("Date must use YYYY-MM-DD format.")
                return

            payload = {"ticker": ticker, "period": period, "lastDate": last_date, "source": "custom"}
            existing_idx = next(
                (
                    idx
                    for idx, item in enumerate(self.custom_tickers)
                    if item["ticker"] == ticker and item["period"] == period
                ),
                None,
            )
            if existing_idx is None:
                self.custom_tickers.append(payload)
            else:
                self.custom_tickers[existing_idx] = payload

            save_custom(self.custom_tickers)
            self._sync_custom_button()
            self._refresh()
            dlg.destroy()

        self._make_button(button_row, "Save ticker", confirm, "warm").pack(side="left")
        self._make_button(button_row, "Cancel", dlg.destroy, "muted").pack(side="left", padx=(8, 0))

        ticker_entry.focus_set()
        dlg.bind("<Return>", lambda _event: confirm())

    def _find_custom_index(self, ticker, period):
        key = ticker_key(ticker, period)
        for idx, item in enumerate(self.custom_tickers):
            if ticker_key(item["ticker"], item["period"]) == key:
                return idx
        return None

    def _find_override_index(self, ticker, period):
        key = ticker_key(ticker, period)
        for idx, item in enumerate(self.date_overrides):
            if ticker_key(item["ticker"], item["period"]) == key:
                return idx
        return None

    def _get_manageable_records(self, filter_text=""):
        term = filter_text.strip().upper()
        records = get_all_tickers(self.custom_tickers, self.date_overrides)
        if term:
            records = [item for item in records if term in item["ticker"].upper()]
        records.sort(
            key=lambda item: (
                item["ticker"],
                0 if item["source"] == "custom" else 1,
                0 if item["period"] == "monthly" else 1,
            )
        )
        return records

    def _edit_record_dialog(self, record, on_saved):
        dlg = self._create_modal("Edit Ticker Date", "470x330")
        card = self._make_card(dlg)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            card,
            text=f"Edit {record['ticker']}",
            bg=self.palette["surface"],
            fg=self.palette["text"],
            font=("Georgia", 17, "bold"),
        ).pack(anchor="w", padx=18, pady=(18, 6))

        source_note = (
            "Custom ticker entry. Saving will update custom_tickers.json."
            if record["source"] == "custom"
            else "Built-in database entry. Saving here stores a local date fix in ticker_date_overrides.json."
        )
        tk.Label(
            card,
            text=source_note,
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
            wraplength=400,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        info = tk.Frame(card, bg=self.palette["surface"])
        info.pack(fill="x", padx=18)
        tk.Label(info, text=f"Period: {record['period'].title()}", bg=self.palette["surface"], fg=self.palette["text"], font=("Segoe UI Semibold", 10)).pack(anchor="w")
        if record["source"] != "custom":
            tk.Label(
                info,
                text=f"Original database date: {record['baseLastDate']}",
                bg=self.palette["surface"],
                fg=self.palette["muted"],
                font=("Segoe UI", 9),
            ).pack(anchor="w", pady=(4, 0))

        entry_style = dict(
            bg=self.palette["surface_alt"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            highlightcolor=self.palette["accent"],
            font=("Segoe UI", 11),
        )

        field = tk.Frame(card, bg=self.palette["surface"])
        field.pack(fill="x", padx=18, pady=(16, 0))
        tk.Label(
            field,
            text="Last ex-div date (YYYY-MM-DD)",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w")
        date_var = tk.StringVar(value=record["lastDate"])
        date_entry = tk.Entry(field, textvariable=date_var, **entry_style)
        date_entry.pack(fill="x", ipady=8, pady=(6, 8))

        err_var = tk.StringVar()
        tk.Label(
            card,
            textvariable=err_var,
            bg=self.palette["surface"],
            fg=self.palette["danger"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 12))

        button_row = tk.Frame(card, bg=self.palette["surface"])
        button_row.pack(fill="x", padx=18, pady=(0, 18))

        def save_record():
            last_date = date_var.get().strip()
            try:
                date.fromisoformat(last_date)
            except ValueError:
                err_var.set("Date must use YYYY-MM-DD format.")
                return

            if record["source"] == "custom":
                idx = self._find_custom_index(record["ticker"], record["period"])
                payload = {
                    "ticker": record["ticker"],
                    "period": record["period"],
                    "lastDate": last_date,
                    "source": "custom",
                }
                if idx is None:
                    self.custom_tickers.append(payload)
                else:
                    self.custom_tickers[idx] = payload
                save_custom(self.custom_tickers)
            else:
                idx = self._find_override_index(record["ticker"], record["period"])
                payload = {
                    "ticker": record["ticker"],
                    "period": record["period"],
                    "lastDate": last_date,
                }
                if last_date == record["baseLastDate"]:
                    if idx is not None:
                        self.date_overrides.pop(idx)
                elif idx is None:
                    self.date_overrides.append(payload)
                else:
                    self.date_overrides[idx] = payload
                save_overrides(self.date_overrides)

            self._sync_custom_button()
            self._refresh()
            on_saved()
            dlg.destroy()

        self._make_button(button_row, "Save date", save_record, "primary").pack(side="left")
        if record["source"] != "custom":
            def reset_to_base():
                date_var.set(record["baseLastDate"])
            self._make_button(button_row, "Use original", reset_to_base, "muted").pack(side="left", padx=(8, 0))
        self._make_button(button_row, "Cancel", dlg.destroy, "muted").pack(side="left", padx=(8, 0))

        date_entry.focus_set()
        dlg.bind("<Return>", lambda _event: save_record())

    def _manage_dialog(self):
        dlg = self._create_modal("Manage Ticker Data", "860x620")
        card = self._make_card(dlg)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            card,
            text="Ticker data manager",
            bg=self.palette["surface"],
            fg=self.palette["text"],
            font=("Georgia", 17, "bold"),
        ).pack(anchor="w", padx=18, pady=(18, 4))
        tk.Label(
            card,
            text="Edit built-in dates through local fixes, or update and delete your custom tickers.",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 12))

        filter_row = tk.Frame(card, bg=self.palette["surface"])
        filter_row.pack(fill="x", padx=18, pady=(0, 12))
        tk.Label(
            filter_row,
            text="Search ticker",
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w")
        filter_var = tk.StringVar()
        entry_style = dict(
            bg=self.palette["surface_alt"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            highlightcolor=self.palette["accent"],
            font=("Segoe UI", 10),
        )
        filter_entry = tk.Entry(filter_row, textvariable=filter_var, **entry_style)
        filter_entry.pack(fill="x", ipady=8, pady=(6, 0))

        table_wrap = tk.Frame(card, bg=self.palette["surface"])
        table_wrap.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        cols = ("ticker", "period", "lastDate", "baseDate", "source", "status")
        tree = ttk.Treeview(
            table_wrap,
            columns=cols,
            show="headings",
            selectmode="browse",
            style="Calendar.Treeview",
            height=15,
        )
        tree.heading("ticker", text="Ticker")
        tree.heading("period", text="Period")
        tree.heading("lastDate", text="Current date")
        tree.heading("baseDate", text="Original date")
        tree.heading("source", text="Source")
        tree.heading("status", text="Status")
        tree.column("ticker", width=140, anchor="center")
        tree.column("period", width=100, anchor="center")
        tree.column("lastDate", width=130, anchor="center")
        tree.column("baseDate", width=130, anchor="center")
        tree.column("source", width=120, anchor="center")
        tree.column("status", width=140, anchor="center")
        tree.tag_configure("custom_row", background=self.palette["surface_alt"], foreground=self.palette["text"])
        tree.tag_configure("fixed_row", background=self.palette["accent_soft"], foreground=self.palette["text"])
        tree.tag_configure("base_row", background=self.palette["surface"], foreground=self.palette["text"])

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        summary_var = tk.StringVar()
        tk.Label(
            card,
            textvariable=summary_var,
            bg=self.palette["surface"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 10))

        row_map = {}

        def selected_record():
            selection = tree.selection()
            if not selection:
                return None
            return row_map.get(selection[0])

        def populate():
            tree.delete(*tree.get_children())
            row_map.clear()
            records = self._get_manageable_records(filter_var.get())
            for record in records:
                source_label = "Custom" if record["source"] == "custom" else "Built-in"
                if record["source"] == "custom":
                    status = "Custom"
                    tag = "custom_row"
                elif record.get("overridden"):
                    status = "Corrected"
                    tag = "fixed_row"
                else:
                    status = "Original"
                    tag = "base_row"
                original_date = record["baseLastDate"] if record["source"] != "custom" else "-"
                item_id = tree.insert(
                    "",
                    "end",
                    values=(
                        record["ticker"],
                        record["period"].title(),
                        record["lastDate"],
                        original_date,
                        source_label,
                        status,
                    ),
                    tags=(tag,),
                )
                row_map[item_id] = record

            summary_var.set(
                f"Rows: {len(records)} | Custom entries: {len(self.custom_tickers)} | Local fixes: {len(self.date_overrides)}"
            )
            children = tree.get_children()
            if children:
                tree.selection_set(children[0])

        def edit_selected():
            record = selected_record()
            if not record:
                return
            self._edit_record_dialog(record, populate)

        def reset_selected():
            record = selected_record()
            if not record:
                return
            if record["source"] == "custom":
                messagebox.showinfo("Reset date", "Custom tickers do not have a built-in source date to reset to.")
                return
            idx = self._find_override_index(record["ticker"], record["period"])
            if idx is None:
                messagebox.showinfo("Reset date", f"{record['ticker']} is already using the original database date.")
                return
            self.date_overrides.pop(idx)
            save_overrides(self.date_overrides)
            self._sync_custom_button()
            self._refresh()
            populate()

        def delete_custom_selected():
            record = selected_record()
            if not record:
                return
            if record["source"] != "custom":
                messagebox.showinfo("Delete custom ticker", "Only custom tickers can be deleted here.")
                return
            idx = self._find_custom_index(record["ticker"], record["period"])
            if idx is None:
                return
            if not messagebox.askyesno("Delete ticker", f"Remove {record['ticker']} from custom tickers?"):
                return
            self.custom_tickers.pop(idx)
            save_custom(self.custom_tickers)
            self._sync_custom_button()
            self._refresh()
            populate()

        tree.bind("<Double-1>", lambda _event: edit_selected())
        filter_entry.bind("<KeyRelease>", lambda _event: populate())

        button_row = tk.Frame(card, bg=self.palette["surface"])
        button_row.pack(fill="x", padx=18, pady=(0, 18))
        self._make_button(button_row, "Edit selected", edit_selected, "primary").pack(side="left")
        self._make_button(button_row, "Reset built-in date", reset_selected, "secondary").pack(side="left", padx=(8, 0))
        self._make_button(button_row, "Delete custom", delete_custom_selected, "danger").pack(side="left", padx=(8, 0))
        self._make_button(button_row, "Close", dlg.destroy, "muted").pack(side="left", padx=(8, 0))

        populate()
        filter_entry.focus_set()

if __name__ == "__main__":
    app = App()
    app.mainloop()
