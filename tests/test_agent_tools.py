"""
Tests for pure Python logic in agent tool methods.
Uses sys.modules stubs for langchain/structlog to allow import
without the production dependencies installed.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

import asyncio
import pytest


# ── DataAnalystAgent ──────────────────────────────────────────────────────────

from agents.data_analyst import DataAnalystAgent


def test_data_analyst_constructs():
    agent = DataAnalystAgent()
    assert agent.name == "DataAnalyst"
    assert agent.role is not None


def test_parse_stdf_returns_expected_keys():
    agent = DataAnalystAgent()
    result = asyncio.run(agent.parse_stdf(lot_id="LOT_TEST", wafer_id="W01"))
    for key in ["lot_id", "wafer_id", "die_count", "bin_distribution",
                "yield", "top_failing_tests", "parametric_summary"]:
        assert key in result, f"missing key: {key}"


def test_parse_stdf_die_count_positive():
    agent = DataAnalystAgent()
    result = asyncio.run(agent.parse_stdf(lot_id="LOT_X", wafer_id="W05"))
    assert result["die_count"] > 0


def test_parse_stdf_yield_between_0_and_1():
    agent = DataAnalystAgent()
    result = asyncio.run(agent.parse_stdf(lot_id="LOT_X", wafer_id="W05"))
    assert 0.0 <= result["yield"] <= 1.0


def test_parse_stdf_preserves_lot_and_wafer_ids():
    agent = DataAnalystAgent()
    result = asyncio.run(agent.parse_stdf(lot_id="TC41x_LOT123", wafer_id="W03"))
    assert result["lot_id"] == "TC41x_LOT123"
    assert result["wafer_id"] == "W03"


def test_generate_wafer_map_returns_s3_path():
    agent = DataAnalystAgent()
    stdf = {"lot_id": "LOT_A", "wafer_id": "W01"}
    path = asyncio.run(agent.generate_wafer_map(stdf))
    assert path.startswith("s3://")
    assert "LOT_A" in path
    assert "W01" in path


def test_execute_updates_state():
    agent = DataAnalystAgent()
    state = {
        "session_id": "sess-001", "lot_id": "LOT_A", "wafer_id": "W01",
        "bin": 5, "priority": "normal", "messages": [],
    }
    result = asyncio.run(agent.execute(state))
    assert "stdf_data" in result
    assert "wafer_map_path" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0]["agent"] == "DataAnalyst"


# ── StatisticalAnalystAgent ───────────────────────────────────────────────────

from agents.statistical_analyst import StatisticalAnalystAgent


def test_statistical_analyst_constructs():
    agent = StatisticalAnalystAgent()


def test_t_test_returns_expected_keys():
    agent = StatisticalAnalystAgent()
    result = agent._t_test_analysis({"current_bin_rate": 0.18})
    for key in ["test", "t_statistic", "p_value", "conclusion", "confidence"]:
        assert key in result


def test_t_test_p_value_range():
    agent = StatisticalAnalystAgent()
    result = agent._t_test_analysis({"current_bin_rate": 0.18})
    assert 0.0 <= result["p_value"] <= 1.0


def test_anova_returns_expected_keys():
    agent = StatisticalAnalystAgent()
    result = agent._anova_analysis({})
    for key in ["test", "f_statistic", "p_value", "conclusion"]:
        assert key in result


def test_control_chart_returns_expected_keys():
    agent = StatisticalAnalystAgent()
    result = agent._control_chart_analysis({})
    for key in ["mean", "ucl", "lcl", "out_of_control_points", "conclusion"]:
        assert key in result


def test_control_chart_ucl_greater_than_lcl():
    agent = StatisticalAnalystAgent()
    result = agent._control_chart_analysis({})
    assert result["ucl"] > result["lcl"]


def test_outlier_detection_returns_dict():
    agent = StatisticalAnalystAgent()
    result = agent._outlier_detection({})
    assert isinstance(result, dict)
