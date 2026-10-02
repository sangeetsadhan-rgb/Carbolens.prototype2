
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="CarboLens UAE", page_icon="🌱", layout="wide")

# ============================================================
# CARBOLENS DEMO DATA
# ============================================================
MATERIALS = {
    "Concrete": {
        "category": "Structure", "factor": 0.12, "unit": "kg CO₂e/kg",
        "cost": 0.55,
        "alternatives": [
            {"name": "Low-carbon concrete", "factor": 0.075, "cost": 0.60, "availability": "High"},
            {"name": "Recycled aggregate concrete", "factor": 0.085, "cost": 0.57, "availability": "Medium"},
        ],
    },
    "Steel": {
        "category": "Structure", "factor": 1.85, "unit": "kg CO₂e/kg",
        "cost": 4.20,
        "alternatives": [
            {"name": "Recycled steel", "factor": 1.05, "cost": 4.45, "availability": "High"},
            {"name": "Electric-arc-furnace steel", "factor": 1.20, "cost": 4.35, "availability": "Medium"},
        ],
    },
    "Aluminium": {
        "category": "Facade", "factor": 8.60, "unit": "kg CO₂e/kg",
        "cost": 9.50,
        "alternatives": [
            {"name": "High-recycled-content aluminium", "factor": 3.20, "cost": 9.90, "availability": "Medium"},
            {"name": "Recycled aluminium", "factor": 1.80, "cost": 10.20, "availability": "Medium"},
        ],
    },
    "Glass": {
        "category": "Facade", "factor": 1.20, "unit": "kg CO₂e/kg",
        "cost": 3.10,
        "alternatives": [
            {"name": "High-recycled-content glass", "factor": 0.85, "cost": 3.20, "availability": "High"},
            {"name": "Low-carbon glass", "factor": 0.75, "cost": 3.35, "availability": "Medium"},
        ],
    },
    "Brick": {
        "category": "Envelope", "factor": 0.24, "unit": "kg CO₂e/kg",
        "cost": 0.80,
        "alternatives": [
            {"name": "Low-carbon brick", "factor": 0.16, "cost": 0.84, "availability": "High"},
            {"name": "Compressed earth block", "factor": 0.10, "cost": 0.95, "availability": "Medium"},
        ],
    },
    "Cement": {
        "category": "Binder", "factor": 0.85, "unit": "kg CO₂e/kg",
        "cost": 0.90,
        "alternatives": [
            {"name": "Low-clinker cement", "factor": 0.55, "cost": 0.94, "availability": "High"},
            {"name": "Geopolymer binder", "factor": 0.30, "cost": 1.05, "availability": "Medium"},
        ],
    },
    "Timber": {
        "category": "Structure/Finish", "factor": 0.20, "unit": "kg CO₂e/kg",
        "cost": 5.00,
        "alternatives": [
            {"name": "Certified structural timber", "factor": 0.12, "cost": 5.30, "availability": "Medium"},
        ],
    },
    "Asphalt": {
        "category": "Infrastructure", "factor": 0.05, "unit": "kg CO₂e/kg",
        "cost": 0.35,
        "alternatives": [
            {"name": "Recycled asphalt", "factor": 0.025, "cost": 0.36, "availability": "High"},
        ],
    },
}

# ============================================================
# VISUAL DESIGN / ANIMATION
# ============================================================
st.markdown("""
<style>
@keyframes fadeUp {
    from {opacity:0; transform:translateY(14px);}
    to {opacity:1; transform:translateY(0);}
}
@keyframes glow {
    0%,100% {box-shadow:0 0 0 rgba(34,197,94,0);}
    50% {box-shadow:0 0 26px rgba(34,197,94,.16);}
}
.block-container {padding-top:1.2rem; animation:fadeUp .55s ease-out;}
.hero {
    padding:30px 32px;
    border-radius:24px;
    background:linear-gradient(135deg,#0b1f17,#123c29,#0b1f17);
    color:white;
    margin-bottom:24px;
    animation:fadeUp .6s ease-out, glow 4s ease-in-out infinite;
}
.hero h1 {font-size:3rem; margin:0 0 8px 0;}
.hero p {font-size:1.08rem; opacity:.88; margin:0;}
.card {
    padding:20px;
    border-radius:18px;
    border:1px solid rgba(120,140,130,.20);
    background:rgba(255,255,255,.025);
    transition:transform .2s ease, box-shadow .2s ease;
}
.card:hover {transform:translateY(-3px); box-shadow:0 10px 30px rgba(0,0,0,.10);}
.ai-box {
    padding:24px;
    border-radius:20px;
    border:1px solid rgba(34,197,94,.30);
    background:linear-gradient(135deg,rgba(34,197,94,.10),rgba(16,185,129,.035));
    animation:fadeUp .5s ease-out;
}
.badge {
    display:inline-block;
    padding:5px 10px;
    border-radius:999px;
    background:rgba(34,197,94,.13);
    color:#22c55e;
    font-weight:700;
    font-size:.82rem;
}
.small {color:#7b8580;font-size:.88rem;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
if "project" not in st.session_state:
    st.session_state.project = {
        "name": "UAE Commercial Building",
        "sector": "Construction",
        "location": "UAE",
        "area": 10000.0,
    }

if "rows" not in st.session_state:
    st.session_state.rows = [
        {"Material": "Concrete", "Quantity (kg)": 10000.0},
        {"Material": "Steel", "Quantity (kg)": 2000.0},
        {"Material": "Glass", "Quantity (kg)": 1000.0},
    ]

# ============================================================
# HELPERS
# ============================================================
def calculate(df):
    out = df.copy()
    out["Carbon Factor"] = out["Material"].map(lambda x: MATERIALS[x]["factor"])
    out["Carbon (kg CO₂e)"] = out["Quantity (kg)"] * out["Carbon Factor"]
    out["Estimated Cost (AED)"] = out.apply(
        lambda r: r["Quantity (kg)"] * MATERIALS[r["Material"]]["cost"], axis=1
    )
    return out

def fmt_kg(x):
    return f"{x:,.0f} kg CO₂e"

def recommendation_engine(calc, priority, budget_tolerance, availability):
    """Transparent prototype recommendation engine.
    It ranks alternatives using carbon reduction, cost change and availability.
    """
    results = []
    for _, r in calc.iterrows():
        material = r["Material"]
        qty = r["Quantity (kg)"]
        current_factor = MATERIALS[material]["factor"]
        current_cost = MATERIALS[material]["cost"]
        current_carbon = qty * current_factor
        current_total_cost = qty * current_cost

        for alt in MATERIALS[material]["alternatives"]:
            new_carbon = qty * alt["factor"]
            saving = current_carbon - new_carbon
            reduction = (saving / current_carbon * 100) if current_carbon else 0
            new_cost = qty * alt["cost"]
            cost_change = ((new_cost - current_total_cost) / current_total_cost * 100) if current_total_cost else 0

            availability_bonus = 1 if alt["availability"] == availability else 0
            carbon_score = reduction / 100
            cost_penalty = max(cost_change, 0) / 100

            if priority == "Maximum carbon reduction":
                score = carbon_score * 0.78 - cost_penalty * 0.12 + availability_bonus * 0.10
            elif priority == "Balanced carbon + cost":
                score = carbon_score * 0.55 - cost_penalty * 0.30 + availability_bonus * 0.15
            else:
                score = carbon_score * 0.35 - cost_penalty * 0.50 + availability_bonus * 0.15

            if cost_change <= budget_tolerance:
                score += 0.08

            results.append({
                "Current material": material,
                "Recommended alternative": alt["name"],
                "Carbon reduction": reduction,
                "Carbon saved (kg CO₂e)": saving,
                "Current carbon": current_carbon,
                "Alternative carbon": new_carbon,
                "Cost change": cost_change,
                "Availability": alt["availability"],
                "Score": score,
            })

    return pd.DataFrame(results).sort_values("Score", ascending=False)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 🌱 CarboLens UAE")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🧱 Carbon Calculator", "🤖 AI Alternatives",
     "🧩 AI Design Checker", "📊 Report", "ℹ️ How It Works"]
)

st.sidebar.divider()
st.sidebar.markdown("### Project")
st.session_state.project["name"] = st.sidebar.text_input("Project name", st.session_state.project["name"])
sector_options = ["Construction", "Real Estate", "Automotive", "Industrial", "Government"]
st.session_state.project["sector"] = st.sidebar.selectbox(
    "Sector", sector_options, index=sector_options.index(st.session_state.project["sector"])
)
st.session_state.project["location"] = st.sidebar.text_input("Location", st.session_state.project["location"])
st.session_state.project["area"] = st.sidebar.number_input(
    "Project area (m²)", min_value=1.0, value=float(st.session_state.project["area"])
)

calc = calculate(pd.DataFrame(st.session_state.rows))
total_carbon = calc["Carbon (kg CO₂e)"].sum()
carbon_per_m2 = total_carbon / st.session_state.project["area"]

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
  <span class="badge">UAE • ENTERPRISE CARBON INTELLIGENCE</span>
  <h1>CarboLens</h1>
  <p>Measure carbon. Compare alternatives. Redesign earlier.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# DASHBOARD
# ============================================================
if page == "🏠 Dashboard":
    st.subheader("Project intelligence")
    st.caption(f"{st.session_state.project['name']} · {st.session_state.project['sector']} · {st.session_state.project['location']}")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Embodied carbon", fmt_kg(total_carbon))
    c2.metric("Carbon intensity", f"{carbon_per_m2:,.2f} kg/m²")
    c3.metric("Materials assessed", len(calc))
    c4.metric("Largest hotspot", calc.loc[calc["Carbon (kg CO₂e)"].idxmax(),"Material"])

    st.divider()
    a,b = st.columns(2)
    with a:
        st.markdown("### Carbon hotspots")
        chart = px.bar(calc.sort_values("Carbon (kg CO₂e)", ascending=False),
                       x="Material", y="Carbon (kg CO₂e)",
                       labels={"Carbon (kg CO₂e)":"kg CO₂e"})
        chart.update_layout(transition_duration=500)
        st.plotly_chart(chart, use_container_width=True)
    with b:
        st.markdown("### Carbon share")
        pie = px.pie(calc, names="Material", values="Carbon (kg CO₂e)", hole=.45)
        st.plotly_chart(pie, use_container_width=True)

    biggest = calc.loc[calc["Carbon (kg CO₂e)"].idxmax()]
    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.markdown("### 🤖 CarboLens Insight")
    st.write(
        f"**{biggest['Material']}** is the current carbon hotspot, contributing "
        f"**{biggest['Carbon (kg CO₂e)']:,.0f} kg CO₂e**. "
        "Use the AI Alternatives page to test lower-carbon options."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# CALCULATOR
# ============================================================
elif page == "🧱 Carbon Calculator":
    st.subheader("🧱 Carbon Calculator")
    st.write("Enter project materials and quantities. The prototype calculates quantity × emission factor.")

    edited = st.data_editor(
        pd.DataFrame(st.session_state.rows),
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=list(MATERIALS.keys()), required=True),
            "Quantity (kg)": st.column_config.NumberColumn("Quantity (kg)", min_value=0, step=100.0),
        },
        hide_index=True,
    )
    if st.button("Calculate & save", type="primary"):
        clean = edited.copy()
        clean["Quantity (kg)"] = pd.to_numeric(clean["Quantity (kg)"], errors="coerce").fillna(0)
        clean = clean[clean["Material"].isin(MATERIALS)]
        st.session_state.rows = clean.to_dict("records")
        st.rerun()

    calc = calculate(pd.DataFrame(st.session_state.rows))
    st.dataframe(calc[["Material","Quantity (kg)","Carbon Factor","Carbon (kg CO₂e)","Estimated Cost (AED)"]],
                 use_container_width=True, hide_index=True)
    st.metric("TOTAL EMBODIED CARBON", fmt_kg(calc["Carbon (kg CO₂e)"].sum()))

# ============================================================
# AI ALTERNATIVES
# ============================================================
elif page == "🤖 AI Alternatives":
    st.subheader("🤖 AI Alternatives Finder")
    st.write("Tell CarboLens what matters most. The recommendation engine ranks alternatives using carbon impact, cost and availability.")

    left,right = st.columns([1,1])
    with left:
        priority = st.selectbox(
            "Decision priority",
            ["Maximum carbon reduction", "Balanced carbon + cost", "Lowest cost impact"]
        )
        budget_tolerance = st.slider(
            "Maximum acceptable cost increase (%)", 0, 30, 10, 1
        )
    with right:
        availability = st.selectbox(
            "Preferred availability",
            ["High", "Medium"]
        )
        target_material = st.selectbox(
            "Focus on material",
            ["All materials"] + list(calc["Material"].unique())
        )

    if st.button("✨ Generate recommendations", type="primary"):
        with st.spinner("CarboLens is analyzing material options..."):
            result = recommendation_engine(calc, priority, budget_tolerance, availability)

        if target_material != "All materials":
            result = result[result["Current material"] == target_material]

        if result.empty:
            st.warning("No matching alternatives found.")
        else:
            top = result.iloc[0]
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.markdown("### 🌱 CarboLens recommendation")
            st.markdown(
                f"**Replace {top['Current material']} → {top['Recommended alternative']}**"
            )
            st.write(
                f"This option could reduce the selected component's calculated embodied carbon by "
                f"**{top['Carbon reduction']:.1f}%** or about **{top['Carbon saved (kg CO₂e)']:,.0f} kg CO₂e**."
            )
            st.write(
                f"Estimated cost change: **{top['Cost change']:+.1f}%** · "
                f"Availability: **{top['Availability']}**."
            )
            st.caption(
                "Prototype AI recommendation: the score is generated from the selected priorities. "
                "A production system would also use verified EPD/LCA, supplier, specification and engineering data."
            )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### Ranked options")
            view = result.copy()
            view["Carbon reduction"] = view["Carbon reduction"].map(lambda x: f"{x:.1f}%")
            view["Carbon saved (kg CO₂e)"] = view["Carbon saved (kg CO₂e)"].map(lambda x: f"{x:,.0f}")
            view["Cost change"] = view["Cost change"].map(lambda x: f"{x:+.1f}%")
            view["Score"] = view["Score"].map(lambda x: f"{x:.3f}")
            st.dataframe(
                view[["Current material","Recommended alternative","Carbon reduction",
                      "Carbon saved (kg CO₂e)","Cost change","Availability","Score"]],
                use_container_width=True, hide_index=True
            )

# ============================================================
# DESIGN CHECKER
# ============================================================
elif page == "🧩 AI Design Checker":
    st.subheader("🧩 AI Design Checker")
    st.write(
        "Prototype of the proposed workflow: upload a design, identify carbon hotspots, "
        "then test alternatives. A production version would connect to BIM/CAD/IFC data."
    )
    uploaded = st.file_uploader("Upload a demo design file", type=["csv","txt","json","ifc","obj"])
    if uploaded:
        st.success(f"Design received: {uploaded.name}")
        st.markdown("### Automated checks")
        checks = [
            ("Material mapping", "Components can be mapped to carbon records", "PASS"),
            ("Carbon hotspots", "High-impact materials should be reviewed first", "REVIEW"),
            ("Alternative search", "Lower-carbon options available for mapped materials", "READY"),
            ("Design completeness", "Prototype file received successfully", "PASS"),
        ]
        for title, msg, status in checks:
            if status == "PASS":
                st.success(f"✅ **{title}:** {msg}")
            else:
                st.warning(f"⚠️ **{title}:** {msg}")

        if st.button("Run AI design analysis", type="primary"):
            with st.spinner("Analyzing design components..."):
                result = recommendation_engine(calc, "Maximum carbon reduction", 15, "High")
            st.markdown("### AI analysis result")
            for _, r in result.head(3).iterrows():
                st.info(
                    f"**{r['Current material']} → {r['Recommended alternative']}**  \n"
                    f"Potential reduction: **{r['Carbon reduction']:.1f}%** · "
                    f"Estimated saving: **{r['Carbon saved (kg CO₂e)']:,.0f} kg CO₂e**"
                )
    else:
        st.info("Upload a demo design file to activate the prototype checker.")

# ============================================================
# REPORT
# ============================================================
elif page == "📊 Report":
    st.subheader("📊 Project Report")
    report = f"""CARBOLENS UAE — PROJECT CARBON REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

PROJECT
Name: {st.session_state.project['name']}
Sector: {st.session_state.project['sector']}
Location: {st.session_state.project['location']}
Area: {st.session_state.project['area']:,.0f} m²

CARBON SUMMARY
Total embodied carbon: {total_carbon:,.0f} kg CO₂e
Carbon intensity: {carbon_per_m2:,.2f} kg CO₂e/m²
Materials assessed: {len(calc)}

MATERIAL BREAKDOWN
"""
    for _,r in calc.iterrows():
        report += f"- {r['Material']}: {r['Quantity (kg)']:,.0f} kg × {r['Carbon Factor']:.3f} = {r['Carbon (kg CO₂e)']:,.0f} kg CO₂e\n"
    report += """
NOTE
Prototype factors are illustrative demo values. Real engineering/procurement decisions
require verified LCA/EPD data, project-specific assumptions and professional review.
"""
    st.text_area("Report preview", report, height=450)
    st.download_button("⬇️ Download report", report, file_name="carbolens_project_report.txt", mime="text/plain")

# ============================================================
# HOW IT WORKS
# ============================================================
else:
    st.subheader("ℹ️ How CarboLens works")
    st.markdown("""
### 1. National Carbon Database
A UAE-focused source for embodied-carbon data for materials, products and projects.

### 2. Alternatives Finder
Compares lower-carbon materials, suppliers and methods using carbon, cost and availability.

### 3. AI Design Checker
The proposed production workflow is:

**3D/BIM/CAD upload → material extraction → carbon mapping → hotspot detection → alternatives → revised comparison**

### 4. Enterprise workflow
The full concept can support construction, real estate, automotive, manufacturing,
engineering/design and government users.

### Prototype limitation
This version uses illustrative material factors and a transparent recommendation engine.
It is a demonstration of the product workflow, not a validated engineering/LCA system.
""")

st.sidebar.caption("CarboLens UAE • Future Foundry • Prototype")
