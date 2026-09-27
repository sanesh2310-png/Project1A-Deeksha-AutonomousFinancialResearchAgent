# Evaluation Report

Automated + heuristic metrics across all 8 challenges.

## Challenge 1: Single-Company Profile (Difficulty 1/5)

- Query type: `company_profile` (complexity 1/5)
- Tools used: vector_db_search, company_profile, financial_data_api, web_search
- Degradation notes: 0

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.4 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 1.0 |
| FA-4_entity_accuracy | 0.0 |
| FA-5_hallucination_rate | 0.6 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 4 |
| CO-3_temporal_coverage_years | 3 |
| CO-4_risk_factor_coverage | 0.0 |
| AD-1_insight_density | 4.0 |
| AD-2_cross_source_synthesis | 0 |
| AD-3_quantitative_reasoning | 0 |
| AD-4_forward_looking_sections | 0 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 0 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 1.0 |
| AB-2_error_recovery_rate | 1.0 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.333 |
| AB-5_latency_seconds | 0.08 |
| benchmark_keyword_overlap | 0.5 |

## Challenge 2: Earnings Analysis (Difficulty 2/5)

- Query type: `earnings_analysis` (complexity 1/5)
- Tools used: vector_db_search, financial_data_api, earnings_transcript, news_sentiment, web_search
- Degradation notes: 0

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.368 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 1.0 |
| FA-4_entity_accuracy | 0.0 |
| FA-5_hallucination_rate | 0.632 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 5 |
| CO-3_temporal_coverage_years | 3 |
| CO-4_risk_factor_coverage | 0.0 |
| AD-1_insight_density | 4.0 |
| AD-2_cross_source_synthesis | 0 |
| AD-3_quantitative_reasoning | 0 |
| AD-4_forward_looking_sections | 1 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 0 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 1.0 |
| AB-2_error_recovery_rate | 1.0 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.25 |
| AB-5_latency_seconds | 0.13 |
| benchmark_keyword_overlap | 0.4 |

## Challenge 3: Risk Assessment (Difficulty 2/5)

- Query type: `risk_assessment` (complexity 2/5)
- Tools used: vector_db_search, sec_filing_search, financial_data_api, news_sentiment, earnings_transcript
- Degradation notes: 0

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.45 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 1.0 |
| FA-4_entity_accuracy | 0.0 |
| FA-5_hallucination_rate | 0.55 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 5 |
| CO-3_temporal_coverage_years | 3 |
| CO-4_risk_factor_coverage | 1.0 |
| AD-1_insight_density | 4.67 |
| AD-2_cross_source_synthesis | 0 |
| AD-3_quantitative_reasoning | 0 |
| AD-4_forward_looking_sections | 1 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 0 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 1.0 |
| AB-2_error_recovery_rate | 1.0 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.25 |
| AB-5_latency_seconds | 0.14 |

## Challenge 4: Industry Comparison (Difficulty 3/5)

- Query type: `industry_comparison` (complexity 3/5)
- Tools used: vector_db_search, financial_data_api, financial_data_api, sec_filing_search, earnings_transcript, earnings_transcript, peer_comparison, calculation_engine, web_search
- Degradation notes: 0

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.235 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 0.0 |
| FA-4_entity_accuracy | 1.0 |
| FA-5_hallucination_rate | 0.765 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 7 |
| CO-3_temporal_coverage_years | 3 |
| CO-4_risk_factor_coverage | 1.0 |
| AD-1_insight_density | 4.87 |
| AD-2_cross_source_synthesis | 1 |
| AD-3_quantitative_reasoning | 1 |
| AD-4_forward_looking_sections | 2 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 1 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 1.0 |
| AB-2_error_recovery_rate | 1.0 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.125 |
| AB-5_latency_seconds | 0.12 |
| benchmark_keyword_overlap | 0.8 |

## Challenge 5: Contradictory Data Handling (Difficulty 3/5)

- Query type: `contradictory_data` (complexity 3/5)
- Tools used: vector_db_search, financial_data_api, sec_filing_search, news_sentiment, earnings_transcript, fact_checker
- Degradation notes: 0

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.45 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 1.0 |
| FA-4_entity_accuracy | 0.0 |
| FA-5_hallucination_rate | 0.55 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 6 |
| CO-3_temporal_coverage_years | 3 |
| CO-4_risk_factor_coverage | 1.0 |
| AD-1_insight_density | 3.69 |
| AD-2_cross_source_synthesis | 0 |
| AD-3_quantitative_reasoning | 0 |
| AD-4_forward_looking_sections | 1 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 0 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 1.0 |
| AB-2_error_recovery_rate | 1.0 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.2 |
| AB-5_latency_seconds | 0.12 |

## Challenge 6: Ambiguous Query Handling (Difficulty 4/5)

- Query type: `general_research` (complexity 1/5)
- Tools used: vector_db_search, company_profile, web_search, news_sentiment
- Degradation notes: 0

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.667 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 1.0 |
| FA-4_entity_accuracy | 0.0 |
| FA-5_hallucination_rate | 0.333 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 4 |
| CO-3_temporal_coverage_years | 0 |
| CO-4_risk_factor_coverage | 0.0 |
| AD-1_insight_density | 0.0 |
| AD-2_cross_source_synthesis | 0 |
| AD-3_quantitative_reasoning | 0 |
| AD-4_forward_looking_sections | 0 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 0 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 1.0 |
| AB-2_error_recovery_rate | 1.0 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.333 |
| AB-5_latency_seconds | 0.08 |

## Challenge 7: Sector Analysis With Memory (Difficulty 4/5)

- Query type: `risk_assessment` (complexity 2/5)
- Tools used: vector_db_search, sec_filing_search, financial_data_api, news_sentiment, earnings_transcript
- Degradation notes: 0

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.45 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 1.0 |
| FA-4_entity_accuracy | 0.0 |
| FA-5_hallucination_rate | 0.55 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 5 |
| CO-3_temporal_coverage_years | 3 |
| CO-4_risk_factor_coverage | 1.0 |
| AD-1_insight_density | 3.78 |
| AD-2_cross_source_synthesis | 0 |
| AD-3_quantitative_reasoning | 0 |
| AD-4_forward_looking_sections | 1 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 0 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 1.0 |
| AB-2_error_recovery_rate | 1.0 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.25 |
| AB-5_latency_seconds | 0.08 |

## Challenge 8: Full Research Report With Degradation (Difficulty 5/5)

- Query type: `contradictory_data` (complexity 2/5)
- Tools used: vector_db_search, financial_data_api, sec_filing_search, news_sentiment, earnings_transcript, fact_checker
- Degradation notes: 10

| Metric | Value |
|---|---|
| FA-1_numerical_accuracy_rate | 0.0 |
| FA-2_citation_accuracy | 1.0 |
| FA-3_temporal_accuracy | 1.0 |
| FA-4_entity_accuracy | 1.0 |
| FA-5_hallucination_rate | 1.0 |
| CO-1_section_coverage | 1.0 |
| CO-2_data_source_diversity | 5 |
| CO-3_temporal_coverage_years | 0 |
| CO-4_risk_factor_coverage | 0.0 |
| AD-1_insight_density | 0.0 |
| AD-2_cross_source_synthesis | 0 |
| AD-3_quantitative_reasoning | 0 |
| AD-4_forward_looking_sections | 0 |
| CS-1_logical_flow_score | 5.0 |
| CS-2_internal_consistency_contradictions | 0 |
| CS-3_executive_summary_quality | 5.0 |
| CS-4_professional_formatting | 1.0 |
| AB-1_tool_efficiency | 0.833 |
| AB-2_error_recovery_rate | 0.4 |
| AB-3_planning_quality_qualitative | see docs/trace_gallery.md |
| AB-4_memory_utilization | 0.0 |
| AB-5_latency_seconds | 1.14 |
