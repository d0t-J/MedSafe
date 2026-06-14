# app.py
# This is our frontend built entirely in Python using Streamlit.
# Supports single drug analysis AND multiple drug analysis
# with a prominent interaction warning box when multiple drugs
# are entered.

import streamlit as st
from drug_service import fetch_multiple_drugs
from ai_service import analyze_drug, analyze_interaction

# ── PAGE SETUP ──
st.set_page_config(
    page_title="MedSafe — Medicine Safety Checker",
    page_icon="💊",
    layout="centered"
)

# ── HEADER ──
st.title("💊 MedSafe")
st.caption("AI-powered medicine safety checker using official FDA data")
st.divider()

# ── INPUT SECTION ──
drug_input = st.text_input(
    label="Enter medicine name(s)",
    placeholder="e.g. Aspirin   or   Ibuprofen, Warfarin",
    help="Enter one medicine for safety info, or multiple medicines separated by commas to also check interactions"
)

# ── QUICK TRY BUTTONS ──
st.caption("Quick examples — click to fill:")

# All examples in one row using a selectbox styled as buttons
EXAMPLES = {
    "— Select an example —":        "",
    "💊 Aspirin (single drug)":      "Aspirin",
    "💊 Paracetamol (single drug)":  "Paracetamol",
    "💊 Ibuprofen (single drug)":    "Ibuprofen",
    "💊 Warfarin (single drug)":     "Warfarin",
    "🔬 Aspirin + Ibuprofen":        "Aspirin, Ibuprofen",
    "🔬 Ibuprofen + Warfarin":       "Ibuprofen, Warfarin",
    "🔬 Metformin + Lisinopril":     "Metformin, Lisinopril",
    "🔬 Aspirin + Warfarin":         "Aspirin, Warfarin",
    "🔬 Amoxicillin + Ibuprofen":    "Amoxicillin, Ibuprofen",
}

selected_example = st.selectbox(
    label="quick_example",
    options=list(EXAMPLES.keys()),
    label_visibility="collapsed"
)

# If user selected an example fill the input
if EXAMPLES[selected_example]:
    drug_input = EXAMPLES[selected_example]

if st.button("Check Safety", type="primary"):

    # ── INPUT VALIDATION ──
    if not drug_input.strip():
        st.warning("Please enter at least one medicine name.")

    else:
        # Parse comma separated drug names into a clean list
        drugs = [d.strip() for d in drug_input.split(",") if d.strip()]

        if len(drugs) > 5:
            st.warning("Please enter no more than 5 medicines at a time.")

        else:
            with st.spinner("Fetching FDA data and analyzing with Claude AI..."):

                try:
                    # ── STEP 1: Fetch FDA data for all drugs ──
                    drug_data_list = fetch_multiple_drugs(drugs)

                    st.divider()

                    # ── STEP 2: Show individual analysis for each drug ──
                    for drug_data in drug_data_list:

                        # Get a display name for the drug
                        display_name = (
                            drug_data.get("brand_name") or
                            drug_data.get("normalized_name") or
                            drug_data.get("original_name")
                        )

                        # Show a subheader for each drug
                        st.subheader(f"💊 {display_name} — Safety Information")
                        st.success("Powered by OpenFDA + Claude AI")

                        # Get Claude's individual analysis for this drug
                        individual_analysis = analyze_drug(drug_data)
                        st.markdown(individual_analysis)

                        # ── RAW FDA DATA EXPANDER for this drug ──
                        DISPLAY_FIELDS = {
                            "indications_and_usage":     "What Is This Drug For",
                            "boxed_warning":             "Black Box Warning",
                            "warnings":                  "Warnings",
                            "contraindications":         "Who Must Never Take This",
                            "adverse_reactions":         "Side Effects",
                            "drug_interactions":         "Drug Interactions",
                            "do_not_use":                "Do Not Use If",
                            "ask_doctor":                "Ask Your Doctor First",
                            "ask_doctor_or_pharmacist":  "Ask Doctor Or Pharmacist",
                            "when_using":                "While Taking This Drug",
                            "stop_use":                  "Stop Use And See A Doctor If",
                            "pregnancy":                 "Pregnancy And Breastfeeding",
                            "information_for_patients":  "Patient Information",
                            "dosage_and_administration": "Dosage",
                        }

                        with st.expander(
                            f"📂 View Raw FDA Data — {display_name}",
                            expanded=False
                        ):
                            if not drug_data.get("found"):
                                st.error(
                                    f"❌ {drug_data.get('original_name')} "
                                    f"— Not found in FDA database"
                                )
                            else:
                                st.markdown(
                                    f"**💊 {drug_data.get('brand_name')} "
                                    f"({drug_data.get('generic_name')})**"
                                )
                                for field_key, field_label in DISPLAY_FIELDS.items():
                                    has_data = bool(drug_data.get(field_key))
                                    icon = "✅" if has_data else "❌"
                                    st.write(f"{icon} {field_label}")

                        st.divider()

                    # ── STEP 3: Show interaction analysis if multiple drugs ──
                    # This only runs when the user entered 2 or more drugs
                    if len(drug_data_list) >= 2:

                        # Get names of all drugs for the heading
                        all_names = []
                        for drug in drug_data_list:
                            name = (
                                drug.get("brand_name") or
                                drug.get("normalized_name") or
                                drug.get("original_name")
                            )
                            all_names.append(name)
                        names_string = " + ".join(all_names)

                        # Get Claude's interaction analysis
                        interaction_analysis = analyze_interaction(drug_data_list)

                        # ── PROMINENT INTERACTION BOX ──
                        # This is the special highlighted section your teacher asked for
                        # st.container creates a visual grouping
                        # We use custom HTML to create the prominent colored background
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #fff3cd;
                                border: 2px solid #ff9800;
                                border-radius: 12px;
                                padding: 24px;
                                margin-top: 8px;
                                margin-bottom: 16px;
                            ">
                                <h3 style="color: #e65100; margin-top: 0;">
                                    ⚠️ Drug Interaction Analysis
                                </h3>
                                <h4 style="color: #bf360c; margin-bottom: 16px;">
                                    {names_string}
                                </h4>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Show the actual interaction text from Claude
                        # in a separate warning styled container
                        with st.container(border=True):
                            st.markdown(
                                "🔬 **Based on official FDA label data:**"
                            )
                            st.markdown(interaction_analysis)

                        st.divider()

                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

# ── FOOTER ──
st.divider()
st.caption(
    "MedSafe is not a substitute for professional medical advice. "
    "Always consult a doctor or pharmacist."
)