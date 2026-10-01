"""from graph.graph import graph

document_path = "SAMPLE VENDOR AGREEMENT.pdf"

initial_state = {
    "document_path": document_path
}

print("Running complete legal document workflow...\n")

result = graph.invoke(initial_state)

print("\n======================================")
print("FINAL WORKFLOW OUTPUT")
print("========================================")

print("\n======================================")
print("DOCUMENT CLASSIFICATION")
print("========================================")
print(result.get("document_type"))

print("\n======================================")
print("RISK FLAGS")
print("========================================")
print(result.get("risk_flags"))

print("\n========================================")
print("FINAL STATE KEYS")
print("========================================")

print(result.keys())

print("\n======================================")
print("WORKFLOW COMPLETED SUCCESSFULLY")
print("========================================")"""

from graph.nodes import parse_document

state = {
    "document_path": "uploads/SAMPLE VENDOR AGREEMENT.odt"
}

result = parse_document(state)

print("\n========== EXTRACTED ODT TEXT ==========\n")

print(result["raw_text"])