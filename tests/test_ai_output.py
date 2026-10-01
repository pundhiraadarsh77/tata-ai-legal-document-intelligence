# --------------------------------------------------
# AI Output Tests
# --------------------------------------------------

def test_ai_output_models_import():

    from graph.nodes import (
        Clause,
        Clause_Extraction,
        Sufficiency_Check,
        RiskFlag,
        RiskAnalysisOutput
    )

    assert Clause is not None
    assert Clause_Extraction is not None
    assert Sufficiency_Check is not None
    assert RiskFlag is not None
    assert RiskAnalysisOutput is not None