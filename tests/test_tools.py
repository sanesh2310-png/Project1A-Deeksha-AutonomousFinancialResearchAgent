from tools.tool_registry import ToolRegistry
from tools.exceptions import ToolNotFoundError, ToolValidationError, ToolExecutionError
from tools import implementations as impl


def test_registry_lists_at_least_ten_tools():
    reg = ToolRegistry()
    assert len(reg.list_tools()) >= 10


def test_registry_validates_missing_required_param():
    reg = ToolRegistry()
    try:
        reg.validate("sec_filing_search", {"ticker": "AAPL"})  # missing filing_type
        assert False, "should have raised"
    except ToolValidationError:
        pass


def test_registry_validates_enum():
    reg = ToolRegistry()
    try:
        reg.validate("sec_filing_search", {"ticker": "AAPL", "filing_type": "NOT_A_TYPE"})
        assert False, "should have raised"
    except ToolValidationError:
        pass


def test_registry_rejects_unknown_tool():
    reg = ToolRegistry()
    try:
        reg.call("not_a_real_tool")
        assert False, "should have raised"
    except ToolNotFoundError:
        pass


def test_company_profile_returns_expected_fields():
    result = impl.company_profile(ticker="MSFT")
    assert result["ticker"] == "MSFT"
    assert "sector" in result and "industry" in result


def test_financial_data_api_returns_years_rows():
    result = impl.financial_data_api(ticker="AAPL", statement_type="income_statement", years=3)
    assert len(result["rows"]) == 3
    assert all("operating_margin_pct" in r for r in result["rows"])


def test_calculation_engine_growth_rate():
    result = impl.calculation_engine(calculation_type="growth_rate", inputs={"old_value": 100, "new_value": 120})
    assert result["result_pct"] == 20.0


def test_calculation_engine_zero_base_raises_non_transient():
    try:
        impl.calculation_engine(calculation_type="growth_rate", inputs={"old_value": 0, "new_value": 120})
        assert False, "should have raised"
    except ToolExecutionError as e:
        assert e.transient is False


def test_report_generator_includes_all_provided_sections():
    result = impl.report_generator(sections={
        "title": "Test Report",
        "executive_summary": "Summary text",
        "risk_assessment": "Risk text",
    })
    assert "Executive Summary" in result["markdown"]
    assert "Risk Assessment" in result["markdown"]
