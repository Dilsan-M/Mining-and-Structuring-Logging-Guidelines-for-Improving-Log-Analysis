Mining and Structuring Logging Guidelines for Improving Log Analysis

## Viewing the Catalogue

There are two main ways to inspect the final logging guideline catalogue:

- **Excel catalogue:** Use **`5.Final Result`** to inspect the final catalogue data, including the consolidated guidelines, dimensions, themes, source information, and related catalogue fields.
- **Visual catalogue:** Use **`logging_catalogue`** for a visual and more convenient representation of the catalogue. This view is intended for browsing the catalogue and exploring its guidelines by dimension and theme.

The Excel workbook should be used when the underlying catalogue data or mappings need to be examined directly, while `logging_catalogue` provides the corresponding visual representation.

This repository contains the research artefacts, processing scripts, and catalogue developed for the Master's thesis “Mining and Structuring Logging Guidelines for Improving Log Analysis.”

## Overview

The project investigates how logging is performed in practice, which logging recommendations appear in academic literature and open-source repositories, and how these recommendations can be structured into a reusable logging guideline catalogue.
Overview

Software logs are essential for debugging, fault localization, monitoring, and later system analysis. However, useful logging depends on several design decisions, including:

    What to log

    Where to log

    How to log

    Which log verbosity level to use

This project combines evidence from a developer study, academic literature, and open-source repositories to collect, normalize, classify, consolidate, and validate practical logging guidelines.

The resulting catalogue is intended to make scattered logging guidance easier to inspect and compare.
Research Questions

The thesis is organized around four main research questions:

    RQ1 — Developer practices and challenges: How do developers implement and use logging, and which challenges occur during logging, log analysis, and fault localization?

    RQ2 — Academic guidance: Which logging recommendations are documented in academic literature?

    RQ3 — Open-source guidance: Which logging recommendations can be identified in open-source repositories and related practical sources?

    RQ4 — Catalogue themes: Which themes and characteristics are represented within the resulting logging guideline catalogue?

## Methodology

The study follows a multi-stage pipeline.
1. Developer Study

A developer survey was used to investigate practical logging behaviour and challenges, including:

    logging implementation,

    log analysis,

    fault localization,

    information developers choose to record,

    tools and logging approaches,

    difficulties encountered when interpreting logs.

2. Academic Literature Collection

Relevant academic publications were reviewed to identify logging recommendations and to establish an initial deductive classification structure.

The literature-derived dimensions used in the catalogue are:
Dimension	Initial deductive themes
What to log	State dump, Execution tracing, Event reporting
Where to log	Assertion-check logging, Return-value-check logging, Exception logging, Logic-branch logging, Observing-point logging
How to log	Logging approach, Logging utility integration, Logging code composition
Log verbosity	FATAL, ERROR, WARN, INFO, DEBUG, TRACE

The deductive themes act as starting points rather than a closed taxonomy. Additional recurring concepts identified in the collected guidance are represented by inductive themes.
3. Open-Source Repository Collection

Repository searches were designed to identify logging-related documentation, standards, conventions, examples, configuration files, and implementation guidance.

Collected material was processed while retaining source provenance so that individual recommendations could be traced back to their original repository or external source.
4. Guideline Extraction

Prescriptive logging content was extracted and assigned to one of four logging dimensions:

<what_to_log>
<where_to_log>
<how_to_log>
<log_verbosity>

Guidelines may originate from prose, code, configuration, examples, or tables when a meaningful logging recommendation can be derived from the source.

Rows from which no meaningful guideline can be derived are marked as NO_GUIDELINE.
5. Guideline Normalization

Extracted content is transformed into concise, self-contained logging guidelines.

Normalization is intended to:

    preserve the original recommendation,

    remove unnecessary source-specific wording,

    avoid adding unsupported information,

    retain meaningful conditions and constraints,

    make recommendations easier to compare across sources.

6. Theme Classification

Each normalized guideline is classified using the literature-derived deductive codebook first.

When no deductive theme sufficiently represents the recommendation, an inductive theme is used.

The classification follows a most-specific-theme rule: when both a broad and a more specific established theme are applicable, the more specific theme is preferred.
7. Semantic Consolidation

Semantically equivalent guidelines are consolidated while preserving unique recommendations and conditions.

The consolidation process is conservative:

    uncertain cases remain separate,

    original source content is retained for traceability,

    guidelines from different dimensions are normally kept separate unless they genuinely express the same underlying recommendation,

    each valid source-level guideline occurrence is mapped to exactly one canonical guideline.

8. Manual Validation

Automated and LLM-assisted processing steps are followed by manual review.

Manual validation is used to inspect:

    extraction quality,

    normalized guideline meaning,

    theme assignments,

    broad-theme classifications,

    consolidation decisions,

    source provenance,

    examples retained from code or configuration.

## Logging Guideline Catalogue

The final catalogue organizes logging recommendations by dimension and theme.
What to log

Recommendations concerning the information that should or should not be recorded, such as events, state information, execution information, contextual information, and sensitive data.
Where to log

Recommendations concerning the program location, execution point, scope, destination, or configuration location associated with logging.
How to log

Recommendations concerning logging approaches, APIs, utilities, message construction, lifecycle management, verification, and related implementation practices.
Log verbosity

Recommendations concerning severity levels, log-level configuration, level selection, and verbosity behaviour.
Traceability

A central goal of the project is to preserve the connection between a canonical guideline and the evidence from which it was derived.

Where available, catalogue entries retain contextual information such as:

    original source content,

    repository/source provenance,

    logging dimension,

    assigned theme,

    theme origin (Deductive or Inductive),

    examples or example reasons,

    source links and related metadata.

This allows consolidated guidelines to remain inspectable rather than becoming detached from their source evidence.
Repository Contents

The repository contains artefacts used during different stages of the study, including:

    repository and literature collection data,

    extracted logging content,

    normalized logging guidelines,

    theme classifications,

    consolidation mappings,

    manually reviewed examples,

    Python scripts used for processing and catalogue generation,

    generated catalogue outputs and supporting thesis artefacts.

Some files represent intermediate processing stages and are retained to support traceability and reproducibility.
Processing Workflow

A simplified overview of the processing pipeline is:

Developer Study
      |
      +------------------------------+
                                     |
Academic Literature                  |
      |                              |
      v                              |
Deductive Codebook                   |
                                     v
Open-Source Sources -> Content Extraction
                           |
                           v
                  Guideline Normalization
                           |
                           v
                    Theme Classification
                           |
                           v
                   Manual Re-evaluation
                           |
                           v
                 Semantic Consolidation
                           |
                           v
                Final Guideline Catalogue
                           |
                           v
                  Analysis and Discussion

## Reproducibility

The processing workflow uses Python-based scripts and spreadsheet outputs for intermediate inspection.

Because several processing stages operate on outputs from previous stages, the artefacts should be interpreted as a pipeline rather than as independent datasets.

When reproducing the workflow:

    start from the collected source data,

    perform content extraction,

    normalize extracted recommendations,

    classify guidelines using the codebook,

    manually inspect uncertain or broad classifications,

    consolidate semantically equivalent guidelines,

    validate the final mappings and catalogue.

Exact prompts, processing decisions, validation procedures, and methodological details are documented in the thesis.
Use of AI-Assisted Processing

AI-assisted processing is used for selected extraction, normalization, classification, and consolidation tasks.

These steps are not treated as fully autonomous analysis. Outputs are subjected to integrity checks and manual validation, and source content is retained to support later inspection.

The thesis documents the prompts, processing stages, and validation procedure in greater detail.
Scope and Limitations

The catalogue reflects the academic literature and open-source sources collected for this study. It should therefore not be interpreted as an exhaustive representation of all possible logging guidance.

Repository metadata such as stars, commit counts, or contributor counts are descriptive context only and are not used as indicators of guideline quality.

The catalogue also distinguishes between source-level guideline occurrences and consolidated canonical guidelines. Multiple source occurrences may therefore support the same canonical recommendation.
Thesis

Title: Mining and Structuring Logging Guidelines for Improving Log Analysis
Author: Dilsan Mahadeva
Year: 2026
Institution: Ruhr University Bochum
Citation

Contact

For questions regarding the dataset, processing pipeline, or catalogue, please use the repository's GitHub issue tracker.
