# -*- coding: utf-8 -*-
"""University Explorer — simple, scannable, mobile-first."""

import html as h
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Universities on Policy — TCF Rahnuma",
    page_icon="🎓",
    layout="wide",
)


def load_css(f):
    with open(f) as fh:
        st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)


load_css("style.css")

XLSX = "tcf_docs/university list.xlsx"


@st.cache_data(show_spinner=False)
def load():
    off = pd.read_excel(XLSX, sheet_name="list")
    off = off.dropna(subset=["University Name for Policy", "Group"])
    off.rename(columns={"University Name for Policy": "University"}, inplace=True)
    off["Tier"] = off["Tier"].fillna("—").astype(str).str.strip()
    off["City"] = off["City"].fillna("").astype(str).str.strip()

    prg = pd.read_excel(XLSX, sheet_name="discipline")
    prg = prg.dropna(subset=["Group", "Programmes"])
    pm = prg.groupby("Group")["Programmes"].apply(
        lambda x: sorted(x.unique().tolist())
    ).to_dict()
    return off, pm


off, pm = load()

TIER = {
    "T1": ("#0F766E", "#CCFBF1"), "T2": ("#1D4ED8", "#DBEAFE"),
    "T3": ("#7C3AED", "#EDE9FE"), "T4": ("#B45309", "#FEF3C7"),
    "T4*": ("#B45309", "#FEF3C7"), "—": ("#64748B", "#F1F5F9"),
    "No tier assigned": ("#64748B", "#F1F5F9"),
}

# ---------- topbar ----------
st.markdown(
    '<div class="topbar">'
    '<div class="topbar-brand"><div class="topbar-brand-icon">R</div>'
    "<span>TCF Rahnuma</span></div>"
    '<span style="color:#64748B;font-size:.875rem;font-weight:500;">Universities</span>'
    "</div>",
    unsafe_allow_html=True,
)

st.markdown('<div class="page-wrap page-wrap-wide">', unsafe_allow_html=True)

# ---------- heading ----------
st.markdown(
    '<div style="text-align:center;margin-bottom:1.75rem;">'
    '<p class="page-eyebrow">EXPLORE</p>'
    '<h1 class="page-title" style="margin-bottom:.5rem;">Find your university</h1>'
    '<p class="page-sub" style="margin-bottom:0;">'
    "TCF supports <strong>182 universities</strong> across Pakistan. "
    "Use the filters to narrow down.</p></div>",
    unsafe_allow_html=True,
)

# ---------- filters at top ----------
search = st.text_input(
    "search",
    placeholder="🔍  Search by university name",
    label_visibility="collapsed",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    disc = st.selectbox("Discipline", ["All disciplines"] + sorted(off["Discipline"].dropna().unique()))
with c2:
    avail = sorted(off[off["Discipline"] == disc]["Group"].unique()) if disc != "All disciplines" else sorted(off["Group"].dropna().unique())
    grp = st.selectbox("Field of study", ["All fields"] + avail)
with c3:
    city = st.selectbox("City", ["All cities"] + sorted(c for c in off["City"].unique() if c))
with c4:
    tier = st.selectbox("Tier", ["All tiers"] + sorted(off["Tier"].unique()))

# ---------- apply ----------
df = off.copy()
if search:
    df = df[df["University"].str.contains(search, case=False, na=False)]
if disc != "All disciplines":
    df = df[df["Discipline"] == disc]
if grp != "All fields":
    df = df[df["Group"] == grp]
if city != "All cities":
    df = df[df["City"] == city]
if tier != "All tiers":
    df = df[df["Tier"] == tier]

# ---------- results ----------
if df.empty:
    st.markdown(
        '<div style="text-align:center;padding:3rem 1rem;">'
        '<div style="font-size:2.5rem;">🔍</div>'
        '<h2 style="color:#0F172A;margin:.75rem 0 .5rem;">No match</h2>'
        '<p style="color:#64748B;">Try removing a filter.</p></div>',
        unsafe_allow_html=True,
    )
else:
    unis = (
        df.groupby(["University", "City", "Region", "Sector", "Tier"])
        .agg({"Discipline": lambda x: sorted(x.unique()),
              "Group": lambda x: sorted(x.unique())})
        .reset_index().sort_values("University")
    )

    st.caption(f"**{len(unis)}** universit{'y' if len(unis)==1 else 'ies'} found")

    for _, u in unis.iterrows():
        name = u["University"]
        cty = str(u["City"]).strip() if pd.notna(u["City"]) else ""
        rgn = str(u["Region"]).strip() if pd.notna(u["Region"]) else ""
        sec = u["Sector"]
        tr = u["Tier"]
        groups = u["Group"]
        total_progs = sum(len(pm.get(g, [])) for g in groups)

        fg, bg = TIER.get(tr, ("#64748B", "#F1F5F9"))
        loc = cty
        if rgn and rgn.lower() != "nan" and rgn != cty:
            loc = f"{cty}, {rgn}" if cty else rgn

        loc_html = ""
        if loc:
            loc_html = (
                '<p style="font-size:.85rem;color:#64748B;margin:0 0 .75rem;">'
                f"📍 {h.escape(loc)}</p>"
            )

        sec_label = "🏛 Public" if sec == "Public" else "🏢 Private"

        card = (
            '<div style="'
            "background:#fff;"
            "border:1px solid #E2E8F0;"
            f"border-left:4px solid {fg};"
            "border-radius:2px 12px 12px 2px;"
            "padding:1.25rem 1.5rem;"
            'margin-bottom:.25rem;">'
            # badges
            '<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.35rem;">'
            f'<span style="font-size:.7rem;font-weight:700;padding:.15rem .55rem;'
            f'border-radius:999px;color:{fg};background:{bg};">{h.escape(tr)}</span>'
            f'<span style="font-size:.75rem;color:#64748B;">{sec_label}</span>'
            "</div>"
            # name
            f'<h3 style="font-size:1.125rem;font-weight:700;color:#0F172A;margin:0 0 .2rem;'
            f'line-height:1.3;">{h.escape(name)}</h3>'
            # location
            f"{loc_html}"
            # stats
            '<div style="display:flex;gap:1.5rem;padding-top:.65rem;border-top:1px solid #F1F5F9;">'
            f'<div><span style="font-size:1.1rem;font-weight:800;color:#0F766E;">{len(groups)}</span> '
            f'<span style="font-size:.75rem;color:#94A3B8;">{"field" if len(groups)==1 else "fields"}</span></div>'
            f'<div><span style="font-size:1.1rem;font-weight:800;color:#0F766E;">{total_progs}</span> '
            '<span style="font-size:.75rem;color:#94A3B8;">programmes</span></div>'
            "</div>"
            "</div>"
        )
        st.markdown(card, unsafe_allow_html=True)

        with st.expander("View programmes"):
            for g in groups:
                progs = pm.get(g, [])
                if progs:
                    pills = " ".join(
                        '<span style="display:inline-block;background:#fff;border:1px solid #99F6E4;'
                        "color:#0F766E;padding:.25rem .65rem;border-radius:999px;font-size:.8rem;"
                        f'font-weight:500;margin:0 .25rem .35rem 0;">{h.escape(p)}</span>'
                        for p in progs
                    )
                else:
                    pills = '<span style="color:#94A3B8;font-size:.8rem;font-style:italic;">No programmes listed</span>'

                st.markdown(
                    '<div style="margin-bottom:1rem;">'
                    '<div style="display:flex;align-items:center;gap:.4rem;margin-bottom:.4rem;">'
                    f'<span style="width:7px;height:7px;border-radius:50%;background:{fg};display:inline-block;"></span>'
                    f'<span style="font-size:.8rem;font-weight:700;color:#334155;'
                    f'text-transform:uppercase;letter-spacing:.04em;">{h.escape(g)}</span>'
                    "</div>"
                    f'<div style="padding-left:1rem;">{pills}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )

st.markdown("</div>", unsafe_allow_html=True)
