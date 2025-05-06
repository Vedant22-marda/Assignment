import streamlit as st
import re

# --- Conversion Maps ---
UNIT_CONVERSION = {
    "cm": 1,
    "inches": 2.54,
    "inch": 2.54,
    "m": 100,
    "meters": 100,
    "km": 100000,
    "kms": 100000
}

ROMAN_SIZE_ORDER = {
    "xs": 1, "s": 2, "m": 3, "l": 4,
    "xl": 5, "xxl": 6, "xxxl": 7
}

# --- Classification Logic ---
def convert_size(val):
    match = re.match(r"(\d*\.?\d+)\s*(cm|inches|inch|m|meters|km|kms)", val.strip().lower())
    if match:
        number, unit = match.groups()
        return float(number) * UNIT_CONVERSION[unit]
    val_clean = val.strip().lower()
    return ROMAN_SIZE_ORDER.get(val_clean, None)

def classify(item):
    item = item.strip().lower()
    if item in ROMAN_SIZE_ORDER:
        return "shirts"
    elif re.match(r"\d+(\.\d+)?\s*(cm|inches|inch|m|meters|km|kms)", item):
        return "sizes"
    elif re.match(r"^\d+(\.\d+)?$", item):
        return "number"
    elif len(item) == 1 and item.isalpha():
        return "alphabet"
    elif item.isalpha():
        return "words"
    else:
        return None

def orchestrator(input_str, selected_types, sort_order):
    items = [i.strip() for i in input_str.split(",") if i.strip()]
    classified = {k: [] for k in ["sizes", "shirts", "number", "words", "alphabet"]}

    for item in items:
        cat = classify(item)
        if cat in selected_types:
            classified[cat].append(item)

    reverse = sort_order == "Descending"
    results = {}

    if "sizes" in selected_types:
        results["Sizes"] = sorted(
            classified["sizes"],
            key=lambda x: convert_size(x) or float("inf"),
            reverse=reverse
        )
    if "shirts" in selected_types:
        results["Shirts"] = sorted(
            classified["shirts"],
            key=lambda x: ROMAN_SIZE_ORDER.get(x.strip().lower(), float("inf")),
            reverse=reverse
        )
    if "number" in selected_types:
        results["Numbers"] = sorted(
            classified["number"], key=float, reverse=reverse
        )
    if "words" in selected_types:
        results["Words"] = sorted(classified["words"], reverse=reverse)
    if "alphabet" in selected_types:
        results["Alphabet"] = sorted(classified["alphabet"], reverse=reverse)

    return results

# --- Streamlit UI ---
st.set_page_config("Attribute Sorter Agent", layout="wide")
st.title("🧠 Smart Attribute Sorting Agent")

with st.sidebar:
    st.markdown("### 🤖 Sorting Agent Guide")
    st.info("1. Choose sort order\n2. Select types\n3. Enter comma-separated items\n4. Click **Sort**")
    st.markdown("Supports:")
    st.code("• Sizes (10 cm, 2 inches, etc)\n• Shirt Sizes (S, M, XL...)\n• Numbers\n• Alphabet\n• Words")

# Sorting order
sort_order = st.radio("Select sorting order:", ["Ascending", "Descending"], horizontal=True)

# Attribute type selection
type_options = ["sizes", "shirts", "number", "words", "alphabet"]
selected_types = st.multiselect(
    "Select attribute types to sort:",
    options=type_options,
    default=["sizes", "shirts", "number", "words"],
    help="Pick the types of data you want to sort"
)

# Input
uploaded_file = st.file_uploader("📤 Upload a .txt file (comma-separated values):", type=["txt"])
example = "red, blue, green, 5, 10 cm, 1 km, XL, M, 3.14, hello, a, t"

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🧪 Try Example"):
        st.session_state.example = example

user_input = uploaded_file.read().decode("utf-8") if uploaded_file else st.text_area(
    "✍️ Enter comma-separated values:",
    value=st.session_state.get("example", "")
)

# Sort
if st.button("🚀 Sort Attributes"):
    if not user_input.strip():
        st.warning("Please enter or upload values to sort.")
    else:
        result = orchestrator(user_input, selected_types, sort_order)

        if result:
            st.subheader("✅ Sorted Results")
            cols = st.columns(len(result))
            for idx, (label, items) in enumerate(result.items()):
                with cols[idx]:
                    st.markdown(f"#### {label}")
                    st.success(", ".join(items))
        else:
            st.warning("No matching attributes found based on selected types.")

        with st.expander("🧠 How Sorting Works"):
            st.markdown("""
            - **Sizes**: Numeric with units (e.g., 5 cm, 2 inches)
            - **Shirts**: S, M, L, XL...
            - **Numbers**: Plain numbers
            - **Words**: Alphabet-only words
            - **Alphabet**: Single-letter characters (e.g., a, b, c)
            """)
