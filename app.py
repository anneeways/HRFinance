# Create a minimal test version to check what's working
with open('minimal_test.py', 'w', encoding='utf-8') as f:
    f.write("""import streamlit as st

st.title("Test - Does this work?")
st.write("If you see this, Streamlit is working!")

# Test basic inputs
name = st.text_input("Your name:")
if name:
    st.write(f"Hello {name}!")

# Test number input
number = st.number_input("Pick a number:", value=42)
st.write(f"You picked: {number}")

st.success("✅ Basic Streamlit functionality works!")
""")

print("✅ Minimal test app created: minimal_test.py")
print("🧪 Please test this first to see if basic Streamlit works")
