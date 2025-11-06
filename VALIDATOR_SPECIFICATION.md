# Form2SDCTemplate Validator Specification

**Version:** 1.0.0
**Date:** November 2025
**Status:** Community Specification
**License:** Apache-2.0

---

## Table of Contents

1. [Introduction](#introduction)
2. [Template Format Specification](#template-format-specification)
3. [Validation Rule Catalog](#validation-rule-catalog)
4. [Error Message Standard](#error-message-standard)
5. [Reference Implementation Pseudocode](#reference-implementation-pseudocode)
6. [Language-Specific Implementation Guides](#language-specific-implementation-guides)
7. [Test Suite Specification](#test-suite-specification)
8. [JSON Schema](#json-schema)
9. [Integration Examples](#integration-examples)
10. [Community Contribution Guide](#community-contribution-guide)

---

## 1. Introduction

### 1.1 Purpose

This specification defines the validation requirements for Form2SDCTemplate markdown documents. It provides a complete reference for building validators in any programming language that can process markdown and YAML.

**Goals:**
- Enable community-driven validator implementations
- Ensure consistent validation across different tools and languages
- Provide clear, actionable error messages to users
- Support pre-LLM validation to catch issues before expensive API calls
- Maintain compatibility with SDC4 reference model requirements

### 1.2 Philosophy

Form2SDCTemplate validators should:

1. **Be Permissive**: Allow LLMs maximum flexibility to interpret instructions
2. **Catch Errors Early**: Detect structural issues before LLM processing
3. **Provide Actionable Feedback**: Guide users to fix issues with clear messages
4. **Be Language-Agnostic**: Use standard formats (markdown, YAML, JSON) that work in any language
5. **Support Incremental Adoption**: Start with CRITICAL errors, add sophistication over time

### 1.3 Use Cases

**Pre-Upload Validation:**
- Users validate templates before uploading to SDCStudio
- IDEs provide real-time validation feedback
- CI/CD pipelines check templates before deployment

**Community Tool Development:**
- Python validators for local development
- Node.js validators for web applications
- Rust validators for high-performance tooling
- IDE plugins (VS Code, JetBrains, etc.)

**LLM Provider Validation:**
- Pre-process templates before sending to Claude, ChatGPT, Gemini
- Optimize prompts based on validation results
- Track validation metrics for quality improvement

---

## 2. Template Format Specification

### 2.1 Document Structure

A valid Form2SDCTemplate document consists of:

```markdown
---
# YAML Front Matter (Required)
project_name: "string"
source_language: "string"
template_version: "string"
---

# Markdown Body (Required)

Root Cluster Component (Required)

Child components with keywords (Optional)
```

### 2.2 YAML Front Matter

**Required Fields:**
- `project_name`: Non-empty string, no special characters except `-`, `_`, spaces
- `source_language`: Valid language code (ISO 639-1 or full name)
- `template_version`: Semantic version string aligned with SDC specification (currently "4.0.0" for SDC4)

**Optional Fields:**
- `description`: String describing the template
- `author`: Author name or organization
- `created_date`: ISO 8601 date string
- `keywords`: Array of strings for categorization
- `notes`: Additional information

**Example:**
```yaml
---
project_name: "Patient Demographics"
source_language: "English"
template_version: "4.0.0"
description: "Demographics for clinical trial enrollment"
author: "Clinical Research Team"
created_date: "2025-01-15"
keywords: ["demographics", "clinical-trial", "patient-data"]
notes: "Based on FDA form 1572"
---
```

### 2.3 Markdown Body Structure

**Required Elements:**

1. **Root Cluster Component**
   - Must be the first component after front matter
   - Must use `Type: Cluster` keyword
   - Represents the top-level data structure

2. **Component Blocks**
   - Separated by blank lines
   - Start with component name (heading or bold text)
   - Contain keyword lines in format `**Keyword**: Value`

**Example:**
```markdown
---
project_name: "Example"
source_language: "English"
template_version: "4.0.0"
---

## Patient Record

**Type**: Cluster
**Description**: Container for all patient information

### Patient Name

**Type**: XdString
**Description**: Full legal name of the patient
**Pattern**: ^[A-Za-z\s'-]+$
**Min Length**: 2
**Max Length**: 100

### Age

**Type**: XdCount
**Description**: Patient age in years
**Units**: years
**Min Magnitude**: 0
**Max Magnitude**: 120
```

### 2.4 Keyword Glossary

#### 2.4.1 Universal Keywords (Valid for All Types)

| Keyword | Description | Value Format | Required |
|---------|-------------|--------------|----------|
| **Type** | SDC4 data type | One of: Cluster, XdString, XdBoolean, XdCount, XdQuantity, XdFloat, XdDouble, XdTemporal, XdOrdinal, XdRatio, XdInterval, XdFile, XdLink, XdToken | Yes (first keyword) |
| **Description** | Human-readable explanation | Free text | Recommended |
| **Examples** | Sample valid values | Free text, may include lists | Optional |

#### 2.4.2 String-Type Keywords (XdString, XdToken)

| Keyword | Description | Value Format | Constraints |
|---------|-------------|--------------|-------------|
| **Pattern** | Regular expression | Valid regex pattern | Optional |
| **Enumeration** | List of allowed values | Comma-separated or bulleted list | Mutually exclusive with Pattern |
| **Min Length** | Minimum character count | Positive integer | Optional |
| **Max Length** | Maximum character count | Positive integer ≥ Min Length | Optional |

**Example:**
```markdown
### Country Code

**Type**: XdString
**Description**: ISO 3166-1 alpha-2 country code
**Pattern**: ^[A-Z]{2}$
**Min Length**: 2
**Max Length**: 2
```

#### 2.4.3 Quantified-Type Keywords (XdCount, XdQuantity, XdFloat, XdDouble)

| Keyword | Description | Value Format | Required |
|---------|-------------|--------------|----------|
| **Units** | Unit of measurement | Unit symbols or references | Yes |
| **Min Magnitude** | Minimum numeric value | Integer (XdCount) or Decimal (others) | Optional |
| **Max Magnitude** | Maximum numeric value | Integer or Decimal ≥ Min | Optional |
| **Precision** | Total significant digits | Positive integer | Optional (XdQuantity only) |
| **Fraction Digits** | Decimal places | Non-negative integer | Optional (XdQuantity only) |

**Units Syntax:**
```markdown
# Simple unit list
**Units**: kg, g, mg

# Inline unit definitions
**Units**:
- kg (kilograms)
- g (grams)
- mg (milligrams)

# Reference to existing component
**Units**: @Common:WeightUnits
```

**Example:**
```markdown
### Body Temperature

**Type**: XdQuantity
**Description**: Core body temperature
**Units**: °C, °F
**Min Magnitude**: 35.0
**Max Magnitude**: 42.0
**Precision**: 4
**Fraction Digits**: 1
```

#### 2.4.4 Temporal-Type Keywords (XdTemporal)

| Keyword | Description | Value Format | Constraints |
|---------|-------------|--------------|-------------|
| **Temporal Type** | Date/time granularity | One of: date, time, datetime, duration | Recommended |
| **Min Date** | Earliest allowed date | ISO 8601 date string | Optional |
| **Max Date** | Latest allowed date | ISO 8601 date string ≥ Min Date | Optional |

**Example:**
```markdown
### Birth Date

**Type**: XdTemporal
**Description**: Date of birth
**Temporal Type**: date
**Min Date**: 1900-01-01
**Max Date**: 2025-12-31
```

#### 2.4.5 Ordinal-Type Keywords (XdOrdinal)

| Keyword | Description | Value Format | Required |
|---------|-------------|--------------|----------|
| **Enumeration** | Ordered list of symbols | Numbered or ordered list | Yes |

**Example:**
```markdown
### Pain Level

**Type**: XdOrdinal
**Description**: Patient-reported pain intensity
**Enumeration**:
1. None
2. Mild
3. Moderate
4. Severe
5. Excruciating
```

#### 2.4.6 Boolean-Type Keywords (XdBoolean)

| Keyword | Description | Value Format | Constraints |
|---------|-------------|--------------|-------------|
| **Default Value** | Initial boolean state | "true" or "false" | Optional |

**Example:**
```markdown
### Consent Given

**Type**: XdBoolean
**Description**: Patient consent for data collection
**Default Value**: false
```

#### 2.4.7 File-Type Keywords (XdFile)

| Keyword | Description | Value Format | Constraints |
|---------|-------------|--------------|-------------|
| **Media Types** | Allowed MIME types | Comma-separated list | Optional |
| **Max Size** | Maximum file size | Integer with unit (e.g., "10MB") | Optional |

**Example:**
```markdown
### Medical Image

**Type**: XdFile
**Description**: Diagnostic imaging file
**Media Types**: image/jpeg, image/png, application/dicom
**Max Size**: 50MB
```

#### 2.4.8 Cluster-Type Keywords (Cluster)

| Keyword | Description | Value Format | Constraints |
|---------|-------------|--------------|-------------|
| **Cardinality** | Instance count constraints | "min..max" (e.g., "1..5") | Optional |

**Example:**
```markdown
### Medications

**Type**: Cluster
**Description**: List of current medications
**Cardinality**: 0..*
```

### 2.5 Component Reuse Syntax

Reference existing components from other projects:

**Format:** `@ProjectName:ComponentLabel`

**Examples:**
```markdown
### Patient Address

**Type**: @Common:PostalAddress

### Weight Measurement

**Type**: XdQuantity
**Units**: @Common:WeightUnits
```

**Validation Rules:**
- Project name and component label must be non-empty
- Format must be exactly `@ProjectName:ComponentLabel` (no spaces)
- Cannot reference components from the same project (use Labels directly)

### 2.6 Keyword Corrections

The following keyword aliases are automatically corrected:

| User Input | Corrected To | Reason |
|------------|--------------|--------|
| Values | Enumeration | Historical naming |
| Unit | Units | Singular/plural consistency |
| Min Length | Min Length | Spacing normalization |
| Max Length | Max Length | Spacing normalization |

Validators SHOULD warn about deprecated keywords but accept them.

---

## 3. Validation Rule Catalog

### 3.1 Validation Severity Levels

| Level | Code Prefix | Description | Action |
|-------|-------------|-------------|--------|
| **CRITICAL** | `E-` | Blocks LLM processing entirely | Must fix before upload |
| **ERROR** | `W-` | Likely to cause incorrect model generation | Should fix |
| **WARNING** | `W-` | Best practice violation or ambiguity | Review recommended |
| **SUGGESTION** | `S-` | Improvement opportunity | Optional enhancement |

### 3.2 CRITICAL Rules (24)

#### 3.2.1 Document Structure (E-DOC)

| Code | Rule | Example |
|------|------|---------|
| E-DOC-001 | Document must start with YAML front matter | Missing `---` delimiters |
| E-DOC-002 | YAML front matter must be valid YAML syntax | Unclosed quotes, invalid indentation |
| E-DOC-003 | `project_name` is required in front matter | Empty or missing field |
| E-DOC-004 | `source_language` is required in front matter | Empty or missing field |
| E-DOC-005 | `template_version` is required in front matter | Empty or missing field |
| E-DOC-006 | Markdown body must exist after front matter | Empty document after `---` |
| E-DOC-007 | Root cluster component is required | First component is not Type: Cluster |

**Example Error:**
```json
{
  "code": "E-DOC-003",
  "severity": "CRITICAL",
  "message": "Missing required field 'project_name' in YAML front matter",
  "line": 2,
  "column": 1,
  "context": "---\nsource_language: English",
  "fix": "Add 'project_name: \"Your Project Name\"' to front matter"
}
```

#### 3.2.2 Component Structure (E-CMP)

| Code | Rule | Example |
|------|------|---------|
| E-CMP-001 | Every component must have a **Type** keyword | Component missing Type |
| E-CMP-002 | **Type** must be a valid SDC4 data type | Type: InvalidType |
| E-CMP-003 | **Type** must be the first keyword in component | Description before Type |
| E-CMP-004 | Component name must be non-empty | Blank heading or bold text |
| E-CMP-005 | Component name must be unique within project | Duplicate "Patient Name" |

**Example Error:**
```json
{
  "code": "E-CMP-002",
  "severity": "CRITICAL",
  "message": "Invalid Type 'String' - must be one of: XdString, XdBoolean, XdCount, ...",
  "line": 15,
  "column": 10,
  "context": "**Type**: String",
  "fix": "Change to 'XdString' for text data"
}
```

#### 3.2.3 Required Fields (E-REQ)

| Code | Rule | Example |
|------|------|---------|
| E-REQ-001 | XdCount, XdQuantity, XdFloat, XdDouble require **Units** | Missing Units keyword |
| E-REQ-002 | **Units** value must be non-empty | `**Units**: ` (blank) |
| E-REQ-003 | XdOrdinal requires **Enumeration** | Missing Enumeration |
| E-REQ-004 | Root cluster must be Type: Cluster | Root is XdString |

**Example Error:**
```json
{
  "code": "E-REQ-001",
  "severity": "CRITICAL",
  "message": "XdQuantity components require a **Units** keyword",
  "line": 42,
  "column": 1,
  "context": "### Blood Pressure\n**Type**: XdQuantity\n**Description**: Systolic BP",
  "fix": "Add '**Units**: mmHg' or appropriate unit"
}
```

#### 3.2.4 Business Logic (E-BIZ)

| Code | Rule | Example |
|------|------|---------|
| E-BIZ-001 | XdBoolean cannot have **Enumeration** | XdBoolean with Enumeration |
| E-BIZ-002 | XdBoolean cannot have **Pattern** | XdBoolean with Pattern |
| E-BIZ-003 | XdString cannot have both Pattern and Enumeration | Both keywords present |
| E-BIZ-004 | **Min Length** must be ≤ **Max Length** | Min: 10, Max: 5 |
| E-BIZ-005 | **Min Magnitude** must be ≤ **Max Magnitude** | Min: 100, Max: 50 |
| E-BIZ-006 | **Min Date** must be ≤ **Max Date** | Min: 2025-01-01, Max: 2020-01-01 |
| E-BIZ-007 | **Pattern** must be valid regular expression | Unclosed bracket in regex |

**Example Error:**
```json
{
  "code": "E-BIZ-003",
  "severity": "CRITICAL",
  "message": "XdString cannot have both **Pattern** and **Enumeration** - choose one",
  "line": 28,
  "column": 1,
  "context": "**Pattern**: ^[A-Z]+$\n**Enumeration**: Red, Green, Blue",
  "fix": "Remove either Pattern (for free text) or Enumeration (for fixed choices)"
}
```

#### 3.2.5 Syntax Errors (E-SYN)

| Code | Rule | Example |
|------|------|---------|
| E-SYN-001 | Keyword format must be `**Keyword**: Value` | Missing colon or asterisks |
| E-SYN-002 | Numeric values must be valid numbers | "abc" for Min Magnitude |
| E-SYN-003 | Component reference must follow `@Project:Label` format | `@Invalid Format` |

**Example Error:**
```json
{
  "code": "E-SYN-001",
  "severity": "CRITICAL",
  "message": "Invalid keyword format - must be '**Keyword**: Value' with bold markers and colon",
  "line": 35,
  "column": 3,
  "context": "Type: XdString",
  "fix": "Change to '**Type**: XdString'"
}
```

### 3.3 WARNING Rules (15)

#### 3.3.1 Best Practices (W-BP)

| Code | Rule | Impact |
|------|------|--------|
| W-BP-001 | **Description** keyword is strongly recommended | Reduces LLM context quality |
| W-BP-002 | Component names should be descriptive (>3 characters) | Ambiguous intent |
| W-BP-003 | **Examples** improve LLM understanding | Reduces accuracy |
| W-BP-004 | Quantified types should specify Min/Max Magnitude | Unbounded data |
| W-BP-005 | String types should specify Max Length | Memory/storage risk |
| W-BP-006 | XdTemporal should specify Temporal Type | Ambiguous granularity |
| W-BP-007 | Cluster components should have child components | Empty structure |

**Example Warning:**
```json
{
  "code": "W-BP-001",
  "severity": "WARNING",
  "message": "Missing **Description** keyword - LLM may misinterpret component purpose",
  "line": 50,
  "column": 1,
  "context": "### SSN\n**Type**: XdString",
  "fix": "Add '**Description**: Social Security Number (###-##-####)'"
}
```

#### 3.3.2 Ambiguity Detection (W-AMB)

| Code | Rule | Impact |
|------|------|--------|
| W-AMB-001 | Multiple interpretations possible for component name | Inconsistent generation |
| W-AMB-002 | Description contains conflicting information | Confusion |
| W-AMB-003 | Units list without definitions | LLM may guess units |
| W-AMB-004 | Enumeration without clear ordering (for XdOrdinal) | Incorrect ordinality |

**Example Warning:**
```json
{
  "code": "W-AMB-003",
  "severity": "WARNING",
  "message": "Units list lacks definitions - LLM may misinterpret symbols",
  "line": 62,
  "column": 1,
  "context": "**Units**: m, cm, mm",
  "fix": "Clarify: '**Units**: m (meters), cm (centimeters), mm (millimeters)'"
}
```

#### 3.3.3 Deprecated Syntax (W-DEP)

| Code | Rule | Migration |
|------|------|-----------|
| W-DEP-001 | Keyword "Values" is deprecated | Use "Enumeration" |
| W-DEP-002 | Keyword "Unit" is deprecated | Use "Units" (plural) |

**Example Warning:**
```json
{
  "code": "W-DEP-001",
  "severity": "WARNING",
  "message": "Keyword '**Values**' is deprecated - use '**Enumeration**' instead",
  "line": 45,
  "column": 1,
  "context": "**Values**: Red, Green, Blue",
  "fix": "Change to '**Enumeration**: Red, Green, Blue'"
}
```

### 3.4 SUGGESTION Rules (12)

#### 3.4.1 Optimization (S-OPT)

| Code | Suggestion | Benefit |
|------|------------|---------|
| S-OPT-001 | Consider adding **Examples** for complex patterns | Improves LLM accuracy |
| S-OPT-002 | Simplified descriptions improve LLM parsing | Faster processing |
| S-OPT-003 | Reuse common components via @Project:Label | Reduces duplication |
| S-OPT-004 | Use XdToken instead of XdString for codes | Better semantic meaning |
| S-OPT-005 | Define Units as separate component for reuse | Consistency |

**Example Suggestion:**
```json
{
  "code": "S-OPT-003",
  "severity": "SUGGESTION",
  "message": "Consider reusing common address component",
  "line": 78,
  "column": 1,
  "context": "### Patient Address\n**Type**: Cluster",
  "fix": "If available, use '**Type**: @Common:PostalAddress' to reuse existing structure"
}
```

#### 3.4.2 Quality Improvements (S-QL)

| Code | Suggestion | Benefit |
|------|------------|---------|
| S-QL-001 | Add semantic context to improve RDF generation | Better ontology linking |
| S-QL-002 | Include units of measurement in Description | Clearer intent |
| S-QL-003 | Specify validation rules explicitly | Accurate constraints |
| S-QL-004 | Use consistent naming conventions | Maintainability |
| S-QL-005 | Add metadata (author, date) to front matter | Traceability |

**Example Suggestion:**
```json
{
  "code": "S-QL-002",
  "severity": "SUGGESTION",
  "message": "Include units in description for better LLM understanding",
  "line": 90,
  "column": 1,
  "context": "**Description**: Patient weight",
  "fix": "Clarify: '**Description**: Patient weight in kilograms or pounds'"
}
```

### 3.5 Context-Aware Validation

Some rules require understanding the broader context:

#### 3.5.1 Type Context Suggestions

When a component lacks a **Type** keyword, suggest based on:

| Indicator | Suggested Type | Example |
|-----------|----------------|---------|
| Name contains "name", "address", "description" | XdString | "Patient Name" |
| Name contains "count", "number", "age" | XdCount | "Visit Count" |
| Name contains "weight", "height", "temperature" | XdQuantity | "Body Weight" |
| Name contains "date", "time" | XdTemporal | "Birth Date" |
| Name contains "status", "level", "grade" | XdOrdinal | "Pain Level" |
| Name contains "is", "has", "enabled" | XdBoolean | "Is Active" |

**Example:**
```json
{
  "code": "E-CMP-001",
  "severity": "CRITICAL",
  "message": "Missing **Type** keyword",
  "line": 105,
  "column": 1,
  "context": "### Patient Name",
  "suggestion": "Based on component name, consider 'XdString'"
}
```

#### 3.5.2 Constraint Suggestions

When constraints are missing, suggest defaults:

| Type | Missing Constraint | Suggested Default |
|------|-------------------|-------------------|
| XdString | Max Length | 255 (database standard) |
| XdCount | Min Magnitude | 0 (non-negative counts) |
| XdQuantity | Precision | 10 total, 2 decimal |
| XdTemporal (date) | Min Date | 1900-01-01 |
| XdTemporal (date) | Max Date | 2100-12-31 |

---

## 4. Error Message Standard

### 4.1 JSON Error Format

All validators MUST output errors in this JSON structure:

```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-CMP-002",
      "severity": "CRITICAL",
      "message": "Invalid Type 'String' - must be one of: XdString, XdBoolean, ...",
      "line": 15,
      "column": 10,
      "context": "**Type**: String",
      "fix": "Change to 'XdString' for text data",
      "component": "Patient Name",
      "keyword": "Type"
    }
  ],
  "warnings": [
    {
      "code": "W-BP-001",
      "severity": "WARNING",
      "message": "Missing **Description** keyword",
      "line": 50,
      "column": 1,
      "context": "### SSN\n**Type**: XdString",
      "fix": "Add '**Description**: Social Security Number (###-##-####)'",
      "component": "SSN",
      "keyword": null
    }
  ],
  "suggestions": [
    {
      "code": "S-OPT-003",
      "severity": "SUGGESTION",
      "message": "Consider reusing common address component",
      "line": 78,
      "column": 1,
      "context": "### Patient Address\n**Type**: Cluster",
      "fix": "If available, use '**Type**: @Common:PostalAddress'",
      "component": "Patient Address",
      "keyword": "Type"
    }
  ],
  "metadata": {
    "validator": "form2sdc-validator-python",
    "version": "1.0.0",
    "validation_time": "2025-01-15T10:30:45Z",
    "document": "patient-form.md",
    "total_components": 12,
    "critical_count": 1,
    "warning_count": 3,
    "suggestion_count": 2
  }
}
```

### 4.2 Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `valid` | boolean | Yes | True if no CRITICAL or ERROR issues |
| `errors` | array | Yes | CRITICAL issues blocking processing |
| `warnings` | array | Yes | Issues that should be addressed |
| `suggestions` | array | Yes | Optional improvements |
| `metadata` | object | Yes | Validation context |

**Error/Warning/Suggestion Object:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Error code from catalog (e.g., "E-CMP-002") |
| `severity` | string | Yes | "CRITICAL", "WARNING", or "SUGGESTION" |
| `message` | string | Yes | Human-readable error description |
| `line` | integer | Yes | Line number in markdown file (1-indexed) |
| `column` | integer | No | Column number (1-indexed) |
| `context` | string | Yes | Relevant snippet of markdown (up to 100 chars) |
| `fix` | string | Yes | Actionable suggestion to resolve issue |
| `component` | string | No | Name of component where issue occurred |
| `keyword` | string | No | Keyword where issue occurred (if applicable) |

**Metadata Object:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `validator` | string | Yes | Validator implementation name |
| `version` | string | Yes | Validator version (semantic versioning) |
| `validation_time` | string | Yes | ISO 8601 timestamp |
| `document` | string | Yes | File name or path |
| `total_components` | integer | Yes | Number of components detected |
| `critical_count` | integer | Yes | Count of CRITICAL errors |
| `warning_count` | integer | Yes | Count of WARNING issues |
| `suggestion_count` | integer | Yes | Count of SUGGESTION items |

### 4.3 Exit Codes

Validators SHOULD use these exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | No CRITICAL or WARNING issues |
| 1 | Validation Failed | CRITICAL errors present |
| 2 | Warnings Present | No CRITICAL errors, but warnings exist |
| 3 | Invalid Input | Cannot parse input file |
| 4 | Internal Error | Validator implementation error |

---

## 5. Reference Implementation Pseudocode

### 5.1 Main Validation Flow

```pseudocode
function validateTemplate(markdownContent: string) -> ValidationResult:
    result = new ValidationResult()

    # Phase 1: Pre-Parse Validation
    yamlBlock, markdownBody = extractYAMLAndBody(markdownContent)

    if yamlBlock is null:
        result.addError("E-DOC-001", line=1, message="Missing YAML front matter")
        return result

    try:
        frontMatter = parseYAML(yamlBlock)
    catch YAMLError as e:
        result.addError("E-DOC-002", line=e.line, message="Invalid YAML: " + e.message)
        return result

    validateFrontMatter(frontMatter, result)

    if result.hasCriticalErrors():
        return result

    # Phase 2: Parse Components
    components = parseComponents(markdownBody, result)

    if components.isEmpty():
        result.addError("E-DOC-006", line=yamlBlock.endLine, message="No components found")
        return result

    # Phase 3: Validate Each Component
    for component in components:
        validateComponent(component, result)

    # Phase 4: Cross-Component Validation
    validateRootCluster(components[0], result)
    validateComponentNames(components, result)

    # Phase 5: Context-Aware Suggestions
    addSuggestions(components, result)

    return result
```

### 5.2 Front Matter Validation

```pseudocode
function validateFrontMatter(frontMatter: object, result: ValidationResult):
    # Required fields
    if "project_name" not in frontMatter or frontMatter["project_name"].isEmpty():
        result.addError("E-DOC-003", line=2, message="Missing required field 'project_name'")

    if "source_language" not in frontMatter or frontMatter["source_language"].isEmpty():
        result.addError("E-DOC-004", line=2, message="Missing required field 'source_language'")

    if "template_version" not in frontMatter or frontMatter["template_version"].isEmpty():
        result.addError("E-DOC-005", line=2, message="Missing required field 'template_version'")

    # Optional quality suggestions
    if "description" not in frontMatter:
        result.addSuggestion("S-QL-005", line=2, message="Consider adding 'description' field")

    if "author" not in frontMatter:
        result.addSuggestion("S-QL-005", line=2, message="Consider adding 'author' field")
```

### 5.3 Component Parsing

```pseudocode
function parseComponents(markdownBody: string, result: ValidationResult) -> List<Component>:
    components = []
    currentComponent = null
    lineNumber = 0

    for line in markdownBody.splitLines():
        lineNumber++

        # Detect component start (heading or bold text at line start)
        if line.matches("^#+\\s+(.+)") or line.matches("^\\*\\*(.+?)\\*\\*\\s*$"):
            if currentComponent is not null:
                components.add(currentComponent)

            componentName = extractComponentName(line)
            currentComponent = new Component(name=componentName, startLine=lineNumber)

        # Detect keyword line
        else if line.matches("^\\*\\*(.+?)\\*\\*:\\s*(.*)"):
            if currentComponent is null:
                result.addError("E-SYN-001", line=lineNumber,
                    message="Keyword found outside component block")
                continue

            keyword, value = extractKeywordValue(line)
            keyword = normalizeKeyword(keyword)
            currentComponent.addKeyword(keyword, value, lineNumber)

    # Add last component
    if currentComponent is not null:
        components.add(currentComponent)

    return components
```

### 5.4 Component Validation

```pseudocode
function validateComponent(component: Component, result: ValidationResult):
    # Rule E-CMP-001: Type is required
    if "Type" not in component.keywords:
        result.addError("E-CMP-001", line=component.startLine,
            message="Missing **Type** keyword",
            suggestion=suggestTypeFromName(component.name))
        return

    # Rule E-CMP-002: Type must be valid
    typeValue = component.keywords["Type"]
    validTypes = ["Cluster", "XdString", "XdBoolean", "XdCount", "XdQuantity",
                  "XdFloat", "XdDouble", "XdTemporal", "XdOrdinal", "XdRatio",
                  "XdInterval", "XdFile", "XdLink", "XdToken"]

    if typeValue not in validTypes:
        result.addError("E-CMP-002", line=component.keywords["Type"].line,
            message=f"Invalid Type '{typeValue}' - must be one of: {validTypes.join(', ')}")
        return

    # Rule E-CMP-003: Type must be first keyword
    if component.keywords.firstKey() != "Type":
        result.addError("E-CMP-003", line=component.startLine,
            message="**Type** must be the first keyword in component")

    # Type-specific validation
    if typeValue in ["XdCount", "XdQuantity", "XdFloat", "XdDouble"]:
        validateQuantifiedType(component, result)

    else if typeValue == "XdString":
        validateStringType(component, result)

    else if typeValue == "XdBoolean":
        validateBooleanType(component, result)

    else if typeValue == "XdTemporal":
        validateTemporalType(component, result)

    else if typeValue == "XdOrdinal":
        validateOrdinalType(component, result)

    # Universal recommendations
    if "Description" not in component.keywords:
        result.addWarning("W-BP-001", line=component.startLine,
            message="Missing **Description** keyword - LLM may misinterpret purpose")

    if component.name.length < 3:
        result.addWarning("W-BP-002", line=component.startLine,
            message=f"Component name '{component.name}' is too short - use descriptive names")
```

### 5.5 Quantified Type Validation

```pseudocode
function validateQuantifiedType(component: Component, result: ValidationResult):
    # Rule E-REQ-001: Units required
    if "Units" not in component.keywords:
        result.addError("E-REQ-001", line=component.startLine,
            message=f"{component.keywords['Type']} requires **Units** keyword")
        return

    # Rule E-REQ-002: Units must be non-empty
    unitsValue = component.keywords["Units"]
    if unitsValue.isEmpty():
        result.addError("E-REQ-002", line=component.keywords["Units"].line,
            message="**Units** value cannot be empty")

    # Suggestion: Add units definitions for clarity
    if not unitsValue.contains("("):  # No parenthetical definitions
        result.addWarning("W-AMB-003", line=component.keywords["Units"].line,
            message="Units lack definitions - LLM may misinterpret symbols")

    # Rule E-BIZ-005: Min ≤ Max
    if "Min Magnitude" in component.keywords and "Max Magnitude" in component.keywords:
        minVal = parseNumeric(component.keywords["Min Magnitude"])
        maxVal = parseNumeric(component.keywords["Max Magnitude"])

        if minVal > maxVal:
            result.addError("E-BIZ-005", line=component.keywords["Max Magnitude"].line,
                message=f"Min Magnitude ({minVal}) exceeds Max Magnitude ({maxVal})")

    # Suggestion: Specify magnitude constraints
    if "Min Magnitude" not in component.keywords and "Max Magnitude" not in component.keywords:
        result.addWarning("W-BP-004", line=component.startLine,
            message="Consider specifying Min/Max Magnitude constraints")
```

### 5.6 String Type Validation

```pseudocode
function validateStringType(component: Component, result: ValidationResult):
    hasPattern = "Pattern" in component.keywords
    hasEnumeration = "Enumeration" in component.keywords

    # Rule E-BIZ-003: Cannot have both Pattern and Enumeration
    if hasPattern and hasEnumeration:
        result.addError("E-BIZ-003", line=component.keywords["Enumeration"].line,
            message="XdString cannot have both **Pattern** and **Enumeration**")

    # Rule E-BIZ-007: Pattern must be valid regex
    if hasPattern:
        patternValue = component.keywords["Pattern"]
        try:
            compileRegex(patternValue)
        catch RegexError as e:
            result.addError("E-BIZ-007", line=component.keywords["Pattern"].line,
                message=f"Invalid regex pattern: {e.message}")

    # Rule E-BIZ-004: Min ≤ Max Length
    if "Min Length" in component.keywords and "Max Length" in component.keywords:
        minLen = parseInt(component.keywords["Min Length"])
        maxLen = parseInt(component.keywords["Max Length"])

        if minLen > maxLen:
            result.addError("E-BIZ-004", line=component.keywords["Max Length"].line,
                message=f"Min Length ({minLen}) exceeds Max Length ({maxLen})")

    # Suggestion: Specify Max Length
    if "Max Length" not in component.keywords:
        result.addWarning("W-BP-005", line=component.startLine,
            message="Consider specifying **Max Length** to prevent unbounded strings")
```

### 5.7 Boolean Type Validation

```pseudocode
function validateBooleanType(component: Component, result: ValidationResult):
    # Rule E-BIZ-001: No Enumeration
    if "Enumeration" in component.keywords:
        result.addError("E-BIZ-001", line=component.keywords["Enumeration"].line,
            message="XdBoolean cannot have **Enumeration** keyword")

    # Rule E-BIZ-002: No Pattern
    if "Pattern" in component.keywords:
        result.addError("E-BIZ-002", line=component.keywords["Pattern"].line,
            message="XdBoolean cannot have **Pattern** keyword")
```

### 5.8 Root Cluster Validation

```pseudocode
function validateRootCluster(firstComponent: Component, result: ValidationResult):
    # Rule E-DOC-007: First component must be Cluster
    if "Type" not in firstComponent.keywords or firstComponent.keywords["Type"] != "Cluster":
        result.addError("E-DOC-007", line=firstComponent.startLine,
            message="First component must be Type: Cluster (root cluster required)")
```

---

## 6. Language-Specific Implementation Guides

### 6.1 Python Implementation

**Recommended Libraries:**
- `PyYAML` or `ruamel.yaml` for YAML parsing
- `re` (built-in) for regex validation
- `dataclasses` for structured error objects

**Example Structure:**

```python
from dataclasses import dataclass
from typing import List, Optional
import yaml
import re

@dataclass
class ValidationError:
    code: str
    severity: str  # "CRITICAL", "WARNING", "SUGGESTION"
    message: str
    line: int
    column: Optional[int]
    context: str
    fix: str
    component: Optional[str] = None
    keyword: Optional[str] = None

@dataclass
class ValidationResult:
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    suggestions: List[ValidationError]
    metadata: dict

class Form2SDCValidator:
    VALID_TYPES = [
        "Cluster", "XdString", "XdBoolean", "XdCount", "XdQuantity",
        "XdFloat", "XdDouble", "XdTemporal", "XdOrdinal", "XdRatio",
        "XdInterval", "XdFile", "XdLink", "XdToken"
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []

    def validate(self, markdown_content: str) -> ValidationResult:
        """Main validation entry point."""
        # Extract YAML and markdown body
        yaml_block, markdown_body = self._extract_yaml_and_body(markdown_content)

        if not yaml_block:
            self._add_error("E-DOC-001", 1, "Missing YAML front matter")
            return self._build_result()

        # Parse YAML
        try:
            front_matter = yaml.safe_load(yaml_block)
        except yaml.YAMLError as e:
            self._add_error("E-DOC-002", e.problem_mark.line, f"Invalid YAML: {e}")
            return self._build_result()

        # Validate front matter
        self._validate_front_matter(front_matter)

        # Parse components
        components = self._parse_components(markdown_body)

        if not components:
            self._add_error("E-DOC-006", 10, "No components found in markdown body")
            return self._build_result()

        # Validate each component
        for component in components:
            self._validate_component(component)

        # Cross-component validation
        self._validate_root_cluster(components[0])

        return self._build_result()

    def _extract_yaml_and_body(self, content: str):
        """Extract YAML front matter and markdown body."""
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            return match.group(1), match.group(2)
        return None, content

    def _validate_front_matter(self, front_matter: dict):
        """Validate required YAML fields."""
        required_fields = ["project_name", "source_language", "template_version"]

        for field in required_fields:
            if field not in front_matter or not front_matter[field]:
                code = f"E-DOC-00{required_fields.index(field) + 3}"
                self._add_error(code, 2, f"Missing required field '{field}'")

    def _parse_components(self, markdown_body: str):
        """Parse component blocks from markdown."""
        components = []
        current_component = None

        for line_num, line in enumerate(markdown_body.split('\n'), start=1):
            # Detect component heading
            if re.match(r'^#+\s+(.+)', line) or re.match(r'^\*\*(.+?)\*\*\s*$', line):
                if current_component:
                    components.append(current_component)

                name_match = re.search(r'#+\s+(.+)|^\*\*(.+?)\*\*', line)
                name = name_match.group(1) or name_match.group(2)
                current_component = {
                    'name': name,
                    'start_line': line_num,
                    'keywords': {}
                }

            # Detect keyword line
            elif re.match(r'^\*\*(.+?)\*\*:\s*(.*)', line):
                if current_component:
                    kw_match = re.match(r'^\*\*(.+?)\*\*:\s*(.*)', line)
                    keyword = kw_match.group(1)
                    value = kw_match.group(2)
                    current_component['keywords'][keyword] = {
                        'value': value,
                        'line': line_num
                    }

        if current_component:
            components.append(current_component)

        return components

    def _validate_component(self, component: dict):
        """Validate individual component."""
        # Check for Type keyword
        if 'Type' not in component['keywords']:
            self._add_error(
                "E-CMP-001",
                component['start_line'],
                "Missing **Type** keyword",
                component=component['name']
            )
            return

        # Validate Type value
        type_value = component['keywords']['Type']['value']
        if type_value not in self.VALID_TYPES:
            self._add_error(
                "E-CMP-002",
                component['keywords']['Type']['line'],
                f"Invalid Type '{type_value}' - must be one of: {', '.join(self.VALID_TYPES)}",
                component=component['name']
            )
            return

        # Type-specific validation
        if type_value in ["XdCount", "XdQuantity", "XdFloat", "XdDouble"]:
            self._validate_quantified(component)
        elif type_value == "XdString":
            self._validate_string(component)
        elif type_value == "XdBoolean":
            self._validate_boolean(component)

    def _validate_quantified(self, component: dict):
        """Validate quantified types."""
        if 'Units' not in component['keywords']:
            self._add_error(
                "E-REQ-001",
                component['start_line'],
                f"{component['keywords']['Type']['value']} requires **Units** keyword",
                component=component['name']
            )

    def _validate_string(self, component: dict):
        """Validate XdString components."""
        has_pattern = 'Pattern' in component['keywords']
        has_enum = 'Enumeration' in component['keywords']

        if has_pattern and has_enum:
            self._add_error(
                "E-BIZ-003",
                component['keywords']['Enumeration']['line'],
                "XdString cannot have both **Pattern** and **Enumeration**",
                component=component['name']
            )

    def _validate_boolean(self, component: dict):
        """Validate XdBoolean components."""
        if 'Enumeration' in component['keywords']:
            self._add_error(
                "E-BIZ-001",
                component['keywords']['Enumeration']['line'],
                "XdBoolean cannot have **Enumeration** keyword",
                component=component['name']
            )

    def _validate_root_cluster(self, first_component: dict):
        """Validate root cluster."""
        if 'Type' not in first_component['keywords'] or \
           first_component['keywords']['Type']['value'] != 'Cluster':
            self._add_error(
                "E-DOC-007",
                first_component['start_line'],
                "First component must be Type: Cluster"
            )

    def _add_error(self, code: str, line: int, message: str,
                   component: Optional[str] = None, keyword: Optional[str] = None):
        """Add error to results."""
        error = ValidationError(
            code=code,
            severity="CRITICAL" if code.startswith("E-") else "WARNING",
            message=message,
            line=line,
            column=None,
            context="",
            fix="",
            component=component,
            keyword=keyword
        )

        if error.severity == "CRITICAL":
            self.errors.append(error)
        else:
            self.warnings.append(error)

    def _build_result(self) -> ValidationResult:
        """Build final validation result."""
        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            suggestions=self.suggestions,
            metadata={
                'validator': 'form2sdc-validator-python',
                'version': '1.0.0',
                'total_components': 0
            }
        )

# Usage
if __name__ == "__main__":
    validator = Form2SDCValidator()

    with open("template.md", "r") as f:
        content = f.read()

    result = validator.validate(content)

    if result.valid:
        print("✅ Validation passed!")
    else:
        print(f"❌ Validation failed with {len(result.errors)} errors")
        for error in result.errors:
            print(f"  Line {error.line}: {error.message}")
```

### 6.2 Node.js Implementation

**Recommended Libraries:**
- `js-yaml` for YAML parsing
- `marked` for markdown parsing (optional)
- TypeScript for type safety

**Example Structure:**

```typescript
// types.ts
export interface ValidationError {
  code: string;
  severity: 'CRITICAL' | 'WARNING' | 'SUGGESTION';
  message: string;
  line: number;
  column?: number;
  context: string;
  fix: string;
  component?: string;
  keyword?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  suggestions: ValidationError[];
  metadata: {
    validator: string;
    version: string;
    validation_time: string;
    document: string;
    total_components: number;
    critical_count: number;
    warning_count: number;
    suggestion_count: number;
  };
}

// validator.ts
import * as yaml from 'js-yaml';
import { ValidationError, ValidationResult } from './types';

export class Form2SDCValidator {
  private static readonly VALID_TYPES = [
    'Cluster', 'XdString', 'XdBoolean', 'XdCount', 'XdQuantity',
    'XdFloat', 'XdDouble', 'XdTemporal', 'XdOrdinal', 'XdRatio',
    'XdInterval', 'XdFile', 'XdLink', 'XdToken'
  ];

  private errors: ValidationError[] = [];
  private warnings: ValidationError[] = [];
  private suggestions: ValidationError[] = [];

  public validate(markdownContent: string): ValidationResult {
    // Reset state
    this.errors = [];
    this.warnings = [];
    this.suggestions = [];

    // Extract YAML and markdown body
    const { yamlBlock, markdownBody } = this.extractYAMLAndBody(markdownContent);

    if (!yamlBlock) {
      this.addError('E-DOC-001', 1, 'Missing YAML front matter');
      return this.buildResult();
    }

    // Parse YAML
    let frontMatter: any;
    try {
      frontMatter = yaml.load(yamlBlock);
    } catch (e: any) {
      this.addError('E-DOC-002', e.mark?.line || 1, `Invalid YAML: ${e.message}`);
      return this.buildResult();
    }

    // Validate front matter
    this.validateFrontMatter(frontMatter);

    // Parse components
    const components = this.parseComponents(markdownBody);

    if (components.length === 0) {
      this.addError('E-DOC-006', 10, 'No components found in markdown body');
      return this.buildResult();
    }

    // Validate each component
    components.forEach(component => this.validateComponent(component));

    // Cross-component validation
    this.validateRootCluster(components[0]);

    return this.buildResult();
  }

  private extractYAMLAndBody(content: string): { yamlBlock: string | null; markdownBody: string } {
    const pattern = /^---\s*\n(.*?)\n---\s*\n(.*)$/s;
    const match = content.match(pattern);

    if (match) {
      return { yamlBlock: match[1], markdownBody: match[2] };
    }
    return { yamlBlock: null, markdownBody: content };
  }

  private validateFrontMatter(frontMatter: any): void {
    const requiredFields = ['project_name', 'source_language', 'template_version'];
    const errorCodes = ['E-DOC-003', 'E-DOC-004', 'E-DOC-005'];

    requiredFields.forEach((field, index) => {
      if (!frontMatter || !frontMatter[field] || frontMatter[field].trim() === '') {
        this.addError(errorCodes[index], 2, `Missing required field '${field}'`);
      }
    });
  }

  private parseComponents(markdownBody: string): any[] {
    const components: any[] = [];
    let currentComponent: any = null;

    const lines = markdownBody.split('\n');
    lines.forEach((line, index) => {
      const lineNum = index + 1;

      // Detect component heading
      const headingMatch = line.match(/^#+\s+(.+)/) || line.match(/^\*\*(.+?)\*\*\s*$/);
      if (headingMatch) {
        if (currentComponent) {
          components.push(currentComponent);
        }
        currentComponent = {
          name: headingMatch[1],
          start_line: lineNum,
          keywords: {}
        };
      }

      // Detect keyword line
      const keywordMatch = line.match(/^\*\*(.+?)\*\*:\s*(.*)/);
      if (keywordMatch && currentComponent) {
        const keyword = keywordMatch[1];
        const value = keywordMatch[2];
        currentComponent.keywords[keyword] = { value, line: lineNum };
      }
    });

    if (currentComponent) {
      components.push(currentComponent);
    }

    return components;
  }

  private validateComponent(component: any): void {
    // Check for Type keyword
    if (!component.keywords.Type) {
      this.addError('E-CMP-001', component.start_line, 'Missing **Type** keyword', component.name);
      return;
    }

    // Validate Type value
    const typeValue = component.keywords.Type.value;
    if (!Form2SDCValidator.VALID_TYPES.includes(typeValue)) {
      this.addError(
        'E-CMP-002',
        component.keywords.Type.line,
        `Invalid Type '${typeValue}' - must be one of: ${Form2SDCValidator.VALID_TYPES.join(', ')}`,
        component.name
      );
      return;
    }

    // Type-specific validation
    if (['XdCount', 'XdQuantity', 'XdFloat', 'XdDouble'].includes(typeValue)) {
      this.validateQuantified(component);
    } else if (typeValue === 'XdString') {
      this.validateString(component);
    } else if (typeValue === 'XdBoolean') {
      this.validateBoolean(component);
    }
  }

  private validateQuantified(component: any): void {
    if (!component.keywords.Units) {
      this.addError(
        'E-REQ-001',
        component.start_line,
        `${component.keywords.Type.value} requires **Units** keyword`,
        component.name
      );
    }
  }

  private validateString(component: any): void {
    const hasPattern = !!component.keywords.Pattern;
    const hasEnum = !!component.keywords.Enumeration;

    if (hasPattern && hasEnum) {
      this.addError(
        'E-BIZ-003',
        component.keywords.Enumeration.line,
        'XdString cannot have both **Pattern** and **Enumeration**',
        component.name
      );
    }
  }

  private validateBoolean(component: any): void {
    if (component.keywords.Enumeration) {
      this.addError(
        'E-BIZ-001',
        component.keywords.Enumeration.line,
        'XdBoolean cannot have **Enumeration** keyword',
        component.name
      );
    }
  }

  private validateRootCluster(firstComponent: any): void {
    if (!firstComponent.keywords.Type || firstComponent.keywords.Type.value !== 'Cluster') {
      this.addError('E-DOC-007', firstComponent.start_line, 'First component must be Type: Cluster');
    }
  }

  private addError(
    code: string,
    line: number,
    message: string,
    component?: string,
    keyword?: string
  ): void {
    const error: ValidationError = {
      code,
      severity: code.startsWith('E-') ? 'CRITICAL' : 'WARNING',
      message,
      line,
      context: '',
      fix: '',
      component,
      keyword
    };

    if (error.severity === 'CRITICAL') {
      this.errors.push(error);
    } else {
      this.warnings.push(error);
    }
  }

  private buildResult(): ValidationResult {
    return {
      valid: this.errors.length === 0,
      errors: this.errors,
      warnings: this.warnings,
      suggestions: this.suggestions,
      metadata: {
        validator: 'form2sdc-validator-nodejs',
        version: '1.0.0',
        validation_time: new Date().toISOString(),
        document: '',
        total_components: 0,
        critical_count: this.errors.length,
        warning_count: this.warnings.length,
        suggestion_count: this.suggestions.length
      }
    };
  }
}

// Usage
import * as fs from 'fs';

const validator = new Form2SDCValidator();
const content = fs.readFileSync('template.md', 'utf-8');
const result = validator.validate(content);

if (result.valid) {
  console.log('✅ Validation passed!');
} else {
  console.log(`❌ Validation failed with ${result.errors.length} errors`);
  result.errors.forEach(error => {
    console.log(`  Line ${error.line}: ${error.message}`);
  });
}
```

### 6.3 Rust Implementation

**Recommended Crates:**
- `serde_yaml` for YAML parsing
- `regex` for pattern matching
- `serde` for JSON serialization

**Example Structure:**

```rust
// src/types.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationError {
    pub code: String,
    pub severity: String, // "CRITICAL", "WARNING", "SUGGESTION"
    pub message: String,
    pub line: usize,
    pub column: Option<usize>,
    pub context: String,
    pub fix: String,
    pub component: Option<String>,
    pub keyword: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationResult {
    pub valid: bool,
    pub errors: Vec<ValidationError>,
    pub warnings: Vec<ValidationError>,
    pub suggestions: Vec<ValidationError>,
    pub metadata: ValidationMetadata,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationMetadata {
    pub validator: String,
    pub version: String,
    pub validation_time: String,
    pub document: String,
    pub total_components: usize,
    pub critical_count: usize,
    pub warning_count: usize,
    pub suggestion_count: usize,
}

// src/validator.rs
use regex::Regex;
use serde_yaml;
use std::collections::HashMap;
use crate::types::*;

pub struct Form2SDCValidator {
    errors: Vec<ValidationError>,
    warnings: Vec<ValidationError>,
    suggestions: Vec<ValidationError>,
}

impl Form2SDCValidator {
    const VALID_TYPES: &'static [&'static str] = &[
        "Cluster", "XdString", "XdBoolean", "XdCount", "XdQuantity",
        "XdFloat", "XdDouble", "XdTemporal", "XdOrdinal", "XdRatio",
        "XdInterval", "XdFile", "XdLink", "XdToken"
    ];

    pub fn new() -> Self {
        Self {
            errors: Vec::new(),
            warnings: Vec::new(),
            suggestions: Vec::new(),
        }
    }

    pub fn validate(&mut self, markdown_content: &str) -> ValidationResult {
        // Reset state
        self.errors.clear();
        self.warnings.clear();
        self.suggestions.clear();

        // Extract YAML and markdown body
        let (yaml_block, markdown_body) = self.extract_yaml_and_body(markdown_content);

        if yaml_block.is_none() {
            self.add_error("E-DOC-001", 1, "Missing YAML front matter", None, None);
            return self.build_result();
        }

        // Parse YAML
        let front_matter: HashMap<String, serde_yaml::Value> = match serde_yaml::from_str(&yaml_block.unwrap()) {
            Ok(fm) => fm,
            Err(e) => {
                self.add_error("E-DOC-002", 1, &format!("Invalid YAML: {}", e), None, None);
                return self.build_result();
            }
        };

        // Validate front matter
        self.validate_front_matter(&front_matter);

        // Parse components
        let components = self.parse_components(&markdown_body);

        if components.is_empty() {
            self.add_error("E-DOC-006", 10, "No components found in markdown body", None, None);
            return self.build_result();
        }

        // Validate each component
        for component in &components {
            self.validate_component(component);
        }

        // Cross-component validation
        if let Some(first) = components.first() {
            self.validate_root_cluster(first);
        }

        self.build_result()
    }

    fn extract_yaml_and_body(&self, content: &str) -> (Option<String>, String) {
        let re = Regex::new(r"(?s)^---\s*\n(.*?)\n---\s*\n(.*)$").unwrap();

        if let Some(captures) = re.captures(content) {
            let yaml_block = captures.get(1).map(|m| m.as_str().to_string());
            let markdown_body = captures.get(2).map(|m| m.as_str().to_string()).unwrap_or_default();
            (yaml_block, markdown_body)
        } else {
            (None, content.to_string())
        }
    }

    fn validate_front_matter(&mut self, front_matter: &HashMap<String, serde_yaml::Value>) {
        let required_fields = vec!["project_name", "source_language", "template_version"];
        let error_codes = vec!["E-DOC-003", "E-DOC-004", "E-DOC-005"];

        for (field, code) in required_fields.iter().zip(error_codes.iter()) {
            if !front_matter.contains_key(*field) ||
               front_matter.get(*field).and_then(|v| v.as_str()).map(|s| s.is_empty()).unwrap_or(true) {
                self.add_error(code, 2, &format!("Missing required field '{}'", field), None, None);
            }
        }
    }

    fn parse_components(&self, markdown_body: &str) -> Vec<Component> {
        let mut components = Vec::new();
        let mut current_component: Option<Component> = None;

        let heading_re = Regex::new(r"^#+\s+(.+)").unwrap();
        let bold_re = Regex::new(r"^\*\*(.+?)\*\*\s*$").unwrap();
        let keyword_re = Regex::new(r"^\*\*(.+?)\*\*:\s*(.*)").unwrap();

        for (line_num, line) in markdown_body.lines().enumerate() {
            let line_num = line_num + 1;

            // Detect component heading
            if let Some(cap) = heading_re.captures(line).or_else(|| bold_re.captures(line)) {
                if let Some(comp) = current_component.take() {
                    components.push(comp);
                }
                current_component = Some(Component {
                    name: cap[1].to_string(),
                    start_line: line_num,
                    keywords: HashMap::new(),
                });
            }

            // Detect keyword line
            if let Some(cap) = keyword_re.captures(line) {
                if let Some(ref mut comp) = current_component {
                    let keyword = cap[1].to_string();
                    let value = cap[2].to_string();
                    comp.keywords.insert(keyword, KeywordValue { value, line: line_num });
                }
            }
        }

        if let Some(comp) = current_component {
            components.push(comp);
        }

        components
    }

    fn validate_component(&mut self, component: &Component) {
        // Check for Type keyword
        if !component.keywords.contains_key("Type") {
            self.add_error("E-CMP-001", component.start_line, "Missing **Type** keyword",
                          Some(component.name.clone()), None);
            return;
        }

        // Validate Type value
        let type_value = &component.keywords["Type"].value;
        if !Self::VALID_TYPES.contains(&type_value.as_str()) {
            self.add_error(
                "E-CMP-002",
                component.keywords["Type"].line,
                &format!("Invalid Type '{}' - must be one of: {}", type_value, Self::VALID_TYPES.join(", ")),
                Some(component.name.clone()),
                None
            );
            return;
        }

        // Type-specific validation
        match type_value.as_str() {
            "XdCount" | "XdQuantity" | "XdFloat" | "XdDouble" => self.validate_quantified(component),
            "XdString" => self.validate_string(component),
            "XdBoolean" => self.validate_boolean(component),
            _ => {}
        }
    }

    fn validate_quantified(&mut self, component: &Component) {
        if !component.keywords.contains_key("Units") {
            let type_value = &component.keywords["Type"].value;
            self.add_error(
                "E-REQ-001",
                component.start_line,
                &format!("{} requires **Units** keyword", type_value),
                Some(component.name.clone()),
                None
            );
        }
    }

    fn validate_string(&mut self, component: &Component) {
        let has_pattern = component.keywords.contains_key("Pattern");
        let has_enum = component.keywords.contains_key("Enumeration");

        if has_pattern && has_enum {
            self.add_error(
                "E-BIZ-003",
                component.keywords["Enumeration"].line,
                "XdString cannot have both **Pattern** and **Enumeration**",
                Some(component.name.clone()),
                None
            );
        }
    }

    fn validate_boolean(&mut self, component: &Component) {
        if component.keywords.contains_key("Enumeration") {
            self.add_error(
                "E-BIZ-001",
                component.keywords["Enumeration"].line,
                "XdBoolean cannot have **Enumeration** keyword",
                Some(component.name.clone()),
                None
            );
        }
    }

    fn validate_root_cluster(&mut self, first_component: &Component) {
        if !first_component.keywords.contains_key("Type") ||
           first_component.keywords["Type"].value != "Cluster" {
            self.add_error(
                "E-DOC-007",
                first_component.start_line,
                "First component must be Type: Cluster",
                None,
                None
            );
        }
    }

    fn add_error(&mut self, code: &str, line: usize, message: &str,
                 component: Option<String>, keyword: Option<String>) {
        let error = ValidationError {
            code: code.to_string(),
            severity: if code.starts_with("E-") { "CRITICAL" } else { "WARNING" }.to_string(),
            message: message.to_string(),
            line,
            column: None,
            context: String::new(),
            fix: String::new(),
            component,
            keyword,
        };

        if error.severity == "CRITICAL" {
            self.errors.push(error);
        } else {
            self.warnings.push(error);
        }
    }

    fn build_result(&self) -> ValidationResult {
        ValidationResult {
            valid: self.errors.is_empty(),
            errors: self.errors.clone(),
            warnings: self.warnings.clone(),
            suggestions: self.suggestions.clone(),
            metadata: ValidationMetadata {
                validator: "form2sdc-validator-rust".to_string(),
                version: "1.0.0".to_string(),
                validation_time: chrono::Utc::now().to_rfc3339(),
                document: String::new(),
                total_components: 0,
                critical_count: self.errors.len(),
                warning_count: self.warnings.len(),
                suggestion_count: self.suggestions.len(),
            },
        }
    }
}

#[derive(Debug, Clone)]
struct Component {
    name: String,
    start_line: usize,
    keywords: HashMap<String, KeywordValue>,
}

#[derive(Debug, Clone)]
struct KeywordValue {
    value: String,
    line: usize,
}

// Usage (src/main.rs)
use std::fs;

fn main() {
    let content = fs::read_to_string("template.md").expect("Failed to read file");
    let mut validator = Form2SDCValidator::new();
    let result = validator.validate(&content);

    if result.valid {
        println!("✅ Validation passed!");
    } else {
        println!("❌ Validation failed with {} errors", result.errors.len());
        for error in &result.errors {
            println!("  Line {}: {}", error.line, error.message);
        }
    }

    // Output JSON
    let json = serde_json::to_string_pretty(&result).unwrap();
    println!("{}", json);
}
```

---

## 7. Test Suite Specification

### 7.1 Test Categories

Validators MUST pass these test suites:

1. **Valid Templates** - Should produce `valid: true`
2. **CRITICAL Errors** - Should detect E-* codes
3. **WARNING Issues** - Should detect W-* codes
4. **Edge Cases** - Boundary conditions and unusual syntax

### 7.2 Valid Template Tests

#### Test 1: Minimal Valid Template

```markdown
---
project_name: "Minimal"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster
**Description**: Root cluster

### Name

**Type**: XdString
**Description**: Person's name
```

**Expected Result:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

#### Test 2: Complete Template with All Types

```markdown
---
project_name: "Complete Example"
source_language: "English"
template_version: "1.0.0"
description: "Comprehensive test template"
author: "Test Suite"
---

## Patient Record

**Type**: Cluster
**Description**: Complete patient information
**Cardinality**: 1..1

### Patient Name

**Type**: XdString
**Description**: Full legal name
**Pattern**: ^[A-Za-z\s'-]+$
**Min Length**: 2
**Max Length**: 100
**Examples**: John Doe, Mary O'Brien

### Age

**Type**: XdCount
**Description**: Age in years
**Units**: years
**Min Magnitude**: 0
**Max Magnitude**: 120

### Weight

**Type**: XdQuantity
**Description**: Body weight
**Units**: kg, lb
**Min Magnitude**: 0.0
**Max Magnitude**: 500.0
**Precision**: 5
**Fraction Digits**: 1

### Temperature

**Type**: XdFloat
**Description**: Body temperature
**Units**: °C, °F
**Min Magnitude**: 35.0
**Max Magnitude**: 42.0

### Birth Date

**Type**: XdTemporal
**Description**: Date of birth
**Temporal Type**: date
**Min Date**: 1900-01-01
**Max Date**: 2025-12-31

### Consent Given

**Type**: XdBoolean
**Description**: Patient consent for treatment
**Default Value**: false

### Pain Level

**Type**: XdOrdinal
**Description**: Self-reported pain intensity
**Enumeration**:
1. None
2. Mild
3. Moderate
4. Severe

### Medical Report

**Type**: XdFile
**Description**: Diagnostic report file
**Media Types**: application/pdf, image/jpeg
**Max Size**: 10MB
```

**Expected Result:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "suggestions": [...]  // May contain optimization suggestions
}
```

### 7.3 CRITICAL Error Tests

#### Test 3: Missing YAML Front Matter

```markdown
## Root

**Type**: Cluster
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-DOC-001",
      "severity": "CRITICAL",
      "message": "Missing YAML front matter"
    }
  ]
}
```

#### Test 4: Missing Required Fields

```markdown
---
project_name: "Test"
---

## Root

**Type**: Cluster
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-DOC-004",
      "message": "Missing required field 'source_language'"
    },
    {
      "code": "E-DOC-005",
      "message": "Missing required field 'template_version'"
    }
  ]
}
```

#### Test 5: Invalid Component Type

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Name

**Type**: String
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-CMP-002",
      "message": "Invalid Type 'String' - must be one of: XdString, ...",
      "component": "Name"
    }
  ]
}
```

#### Test 6: Missing Units for Quantified Type

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Weight

**Type**: XdQuantity
**Description**: Body weight
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-REQ-001",
      "message": "XdQuantity requires **Units** keyword",
      "component": "Weight"
    }
  ]
}
```

#### Test 7: XdString with Pattern and Enumeration

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Color

**Type**: XdString
**Pattern**: ^[A-Z]+$
**Enumeration**: Red, Green, Blue
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-BIZ-003",
      "message": "XdString cannot have both **Pattern** and **Enumeration**",
      "component": "Color"
    }
  ]
}
```

#### Test 8: XdBoolean with Enumeration

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Active

**Type**: XdBoolean
**Enumeration**: Yes, No
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-BIZ-001",
      "message": "XdBoolean cannot have **Enumeration** keyword",
      "component": "Active"
    }
  ]
}
```

#### Test 9: First Component Not Cluster

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

### Name

**Type**: XdString
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-DOC-007",
      "message": "First component must be Type: Cluster"
    }
  ]
}
```

### 7.4 Edge Case Tests

#### Test 10: Keyword Corrections

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Status

**Type**: XdString
**Values**: Active, Inactive
```

**Expected Result:**
```json
{
  "valid": true,
  "warnings": [
    {
      "code": "W-DEP-001",
      "message": "Keyword '**Values**' is deprecated - use '**Enumeration**'"
    }
  ]
}
```

#### Test 11: Component Reuse

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Address

**Type**: @Common:PostalAddress
```

**Expected Result:**
```json
{
  "valid": true,
  "errors": []
}
```

#### Test 12: Empty Units Value

```markdown
---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Weight

**Type**: XdQuantity
**Units**:
```

**Expected Result:**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E-REQ-002",
      "message": "**Units** value cannot be empty"
    }
  ]
}
```

### 7.5 Test Execution

Validators SHOULD provide:

**Test Runner:**
```bash
# Run all tests
./run-tests.sh

# Run specific test category
./run-tests.sh --category critical-errors

# Run single test
./run-tests.sh --test test-003
```

**Test Report Format:**
```
Form2SDCTemplate Validator Test Suite
======================================
Validator: form2sdc-validator-python v1.0.0

Valid Templates:        2/2   ✅
CRITICAL Error Tests:   7/7   ✅
WARNING Tests:          3/3   ✅
Edge Case Tests:        5/5   ✅
-----------------------------------
Total:                 17/17  ✅

All tests passed! 🎉
```

---

## 8. JSON Schema

### 8.1 YAML Front Matter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Form2SDCTemplate Front Matter",
  "description": "Schema for YAML front matter in Form2SDCTemplate documents",
  "type": "object",
  "required": ["project_name", "source_language", "template_version"],
  "properties": {
    "project_name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "Name of the project/data model"
    },
    "source_language": {
      "type": "string",
      "minLength": 1,
      "description": "Language of the source document (ISO 639-1 code or full name)"
    },
    "template_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version of the template format"
    },
    "description": {
      "type": "string",
      "description": "Optional description of the template"
    },
    "author": {
      "type": "string",
      "description": "Author or organization"
    },
    "created_date": {
      "type": "string",
      "format": "date",
      "description": "Creation date (ISO 8601)"
    },
    "keywords": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Keywords for categorization"
    },
    "notes": {
      "type": "string",
      "description": "Additional notes or information"
    }
  },
  "additionalProperties": false
}
```

### 8.2 Validation Result Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Form2SDCTemplate Validation Result",
  "description": "Schema for validation results from Form2SDCTemplate validators",
  "type": "object",
  "required": ["valid", "errors", "warnings", "suggestions", "metadata"],
  "properties": {
    "valid": {
      "type": "boolean",
      "description": "True if no CRITICAL or ERROR issues detected"
    },
    "errors": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ValidationIssue"
      },
      "description": "CRITICAL issues that block processing"
    },
    "warnings": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ValidationIssue"
      },
      "description": "Issues that should be addressed"
    },
    "suggestions": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ValidationIssue"
      },
      "description": "Optional improvements"
    },
    "metadata": {
      "$ref": "#/definitions/ValidationMetadata"
    }
  },
  "definitions": {
    "ValidationIssue": {
      "type": "object",
      "required": ["code", "severity", "message", "line", "context", "fix"],
      "properties": {
        "code": {
          "type": "string",
          "pattern": "^[EWS]-[A-Z]+-\\d{3}$",
          "description": "Error code from catalog (e.g., E-CMP-002)"
        },
        "severity": {
          "type": "string",
          "enum": ["CRITICAL", "WARNING", "SUGGESTION"]
        },
        "message": {
          "type": "string",
          "minLength": 1,
          "description": "Human-readable error description"
        },
        "line": {
          "type": "integer",
          "minimum": 1,
          "description": "Line number in markdown file"
        },
        "column": {
          "type": "integer",
          "minimum": 1,
          "description": "Optional column number"
        },
        "context": {
          "type": "string",
          "maxLength": 200,
          "description": "Relevant snippet of markdown"
        },
        "fix": {
          "type": "string",
          "minLength": 1,
          "description": "Actionable suggestion to resolve issue"
        },
        "component": {
          "type": "string",
          "description": "Name of component where issue occurred"
        },
        "keyword": {
          "type": "string",
          "description": "Keyword where issue occurred"
        }
      }
    },
    "ValidationMetadata": {
      "type": "object",
      "required": [
        "validator",
        "version",
        "validation_time",
        "document",
        "total_components",
        "critical_count",
        "warning_count",
        "suggestion_count"
      ],
      "properties": {
        "validator": {
          "type": "string",
          "description": "Validator implementation name"
        },
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$",
          "description": "Validator version"
        },
        "validation_time": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp"
        },
        "document": {
          "type": "string",
          "description": "File name or path"
        },
        "total_components": {
          "type": "integer",
          "minimum": 0,
          "description": "Number of components detected"
        },
        "critical_count": {
          "type": "integer",
          "minimum": 0
        },
        "warning_count": {
          "type": "integer",
          "minimum": 0
        },
        "suggestion_count": {
          "type": "integer",
          "minimum": 0
        }
      }
    }
  }
}
```

---

## 9. Integration Examples

### 9.1 Pre-Commit Hook

**`.git/hooks/pre-commit`** (Python validator):

```bash
#!/bin/bash
# Form2SDCTemplate Pre-Commit Hook

echo "🔍 Validating Form2SDCTemplate files..."

# Find all .md files in templates directory
template_files=$(git diff --cached --name-only --diff-filter=ACM | grep '^templates/.*\.md$')

if [ -z "$template_files" ]; then
    echo "✅ No template files to validate"
    exit 0
fi

# Run validator on each file
has_errors=0

for file in $template_files; do
    echo "Validating: $file"

    result=$(python3 -m form2sdc_validator "$file" --json)
    valid=$(echo "$result" | jq -r '.valid')

    if [ "$valid" != "true" ]; then
        echo "❌ Validation failed for $file"
        echo "$result" | jq '.errors[]'
        has_errors=1
    else
        warnings=$(echo "$result" | jq '.warnings | length')
        if [ "$warnings" -gt 0 ]; then
            echo "⚠️  $warnings warnings for $file"
        else
            echo "✅ $file is valid"
        fi
    fi
done

if [ $has_errors -eq 1 ]; then
    echo ""
    echo "❌ Commit blocked: Fix validation errors before committing"
    exit 1
fi

echo "✅ All templates validated successfully"
exit 0
```

### 9.2 CI/CD Pipeline (GitHub Actions)

**`.github/workflows/validate-templates.yml`**:

```yaml
name: Validate Form2SDCTemplates

on:
  push:
    paths:
      - 'templates/**/*.md'
  pull_request:
    paths:
      - 'templates/**/*.md'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install validator
        run: npm install -g form2sdc-validator

      - name: Validate templates
        run: |
          echo "🔍 Validating all template files..."

          find templates -name "*.md" | while read file; do
            echo "Validating: $file"

            if ! form2sdc-validator "$file" --strict; then
              echo "❌ Validation failed for $file"
              exit 1
            fi
          done

          echo "✅ All templates validated successfully"

      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation-report.json
```

### 9.3 VS Code Extension

**Extension Configuration** (`package.json`):

```json
{
  "name": "form2sdc-validator",
  "displayName": "Form2SDCTemplate Validator",
  "description": "Real-time validation for Form2SDCTemplate markdown files",
  "version": "1.0.0",
  "publisher": "sdcstudio",
  "engines": {
    "vscode": "^1.75.0"
  },
  "activationEvents": [
    "onLanguage:markdown"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "title": "Form2SDCTemplate Validator",
      "properties": {
        "form2sdc.enableValidation": {
          "type": "boolean",
          "default": true,
          "description": "Enable real-time validation"
        },
        "form2sdc.showSuggestions": {
          "type": "boolean",
          "default": true,
          "description": "Show optimization suggestions"
        }
      }
    }
  }
}
```

**Extension Logic** (`extension.ts`):

```typescript
import * as vscode from 'vscode';
import { Form2SDCValidator } from './validator';

export function activate(context: vscode.ExtensionContext) {
  const validator = new Form2SDCValidator();
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('form2sdc');

  // Validate on file open and save
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(doc => validateDocument(doc)),
    vscode.workspace.onDidSaveTextDocument(doc => validateDocument(doc)),
    vscode.workspace.onDidChangeTextDocument(e => validateDocument(e.document))
  );

  function validateDocument(document: vscode.TextDocument) {
    if (document.languageId !== 'markdown') {
      return;
    }

    // Check if file is in templates directory
    if (!document.fileName.includes('/templates/')) {
      return;
    }

    const result = validator.validate(document.getText());
    const diagnostics: vscode.Diagnostic[] = [];

    // Add errors
    result.errors.forEach(error => {
      const range = new vscode.Range(error.line - 1, 0, error.line - 1, 100);
      const diagnostic = new vscode.Diagnostic(
        range,
        error.message,
        vscode.DiagnosticSeverity.Error
      );
      diagnostic.code = error.code;
      diagnostic.source = 'Form2SDCTemplate';
      diagnostics.push(diagnostic);
    });

    // Add warnings
    result.warnings.forEach(warning => {
      const range = new vscode.Range(warning.line - 1, 0, warning.line - 1, 100);
      const diagnostic = new vscode.Diagnostic(
        range,
        warning.message,
        vscode.DiagnosticSeverity.Warning
      );
      diagnostic.code = warning.code;
      diagnostic.source = 'Form2SDCTemplate';
      diagnostics.push(diagnostic);
    });

    // Add suggestions (as info)
    if (vscode.workspace.getConfiguration('form2sdc').get('showSuggestions')) {
      result.suggestions.forEach(suggestion => {
        const range = new vscode.Range(suggestion.line - 1, 0, suggestion.line - 1, 100);
        const diagnostic = new vscode.Diagnostic(
          range,
          suggestion.message,
          vscode.DiagnosticSeverity.Information
        );
        diagnostic.code = suggestion.code;
        diagnostic.source = 'Form2SDCTemplate';
        diagnostics.push(diagnostic);
      });
    }

    diagnosticCollection.set(document.uri, diagnostics);
  }

  // Show status in status bar
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.text = "$(check) Form2SDC";
  statusBarItem.tooltip = "Template validation active";
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);
}
```

### 9.4 REST API Endpoint

**Express.js Example**:

```typescript
import express from 'express';
import multer from 'multer';
import { Form2SDCValidator } from './validator';

const app = express();
const upload = multer();
const validator = new Form2SDCValidator();

// POST /api/validate
app.post('/api/validate', upload.single('template'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const content = req.file.buffer.toString('utf-8');
  const result = validator.validate(content);

  res.json(result);
});

// POST /api/validate/url
app.post('/api/validate/url', express.json(), async (req, res) => {
  const { url } = req.body;

  if (!url) {
    return res.status(400).json({ error: 'Missing url parameter' });
  }

  try {
    const response = await fetch(url);
    const content = await response.text();
    const result = validator.validate(content);

    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch URL' });
  }
});

app.listen(3000, () => {
  console.log('Form2SDCTemplate Validator API running on port 3000');
});
```

---

## 10. Community Contribution Guide

### 10.1 Proposing New Validation Rules

**Process:**

1. **Open GitHub Issue** with title: `[RULE] Brief description`
2. **Provide Template:**
   ```markdown
   ## Proposed Rule

   **Code:** E-XXX-### or W-XXX-### or S-XXX-###
   **Category:** (DOC, CMP, REQ, BIZ, SYN, BP, AMB, OPT, QL)
   **Severity:** CRITICAL / WARNING / SUGGESTION

   ## Description

   Describe what the rule validates and why it's important.

   ## Example Violation

   ```markdown
   (Show markdown that should trigger this rule)
   ```

   ## Expected Error

   ```json
   {
     "code": "...",
     "message": "...",
     "fix": "..."
   }
   ```

   ## Rationale

   Explain why this rule improves validation quality.
   ```

3. **Community Discussion** - minimum 3 approvals from maintainers
4. **Implementation** - Add to rule catalog and test suite
5. **Documentation Update** - Update this spec with new rule

### 10.2 Reporting Bugs

**Bug Report Template:**

```markdown
## Bug Description

Clear description of the validation issue.

## Template Content

```markdown
(Paste the markdown that causes the issue)
```

## Expected Behavior

What validation result should occur?

## Actual Behavior

What validation result actually occurred?

## Validator Implementation

- Implementation: (Python/Node/Rust/Other)
- Version: X.Y.Z
- Platform: (Linux/macOS/Windows)

## Reproduction Steps

1. Step 1
2. Step 2
3. ...
```

### 10.3 Versioning Policy

This specification uses **Semantic Versioning**:

- **Major version** (X.0.0): Breaking changes to validation rules or JSON format
- **Minor version** (0.X.0): New validation rules or non-breaking enhancements
- **Patch version** (0.0.X): Bug fixes, clarifications, typos

**Current Version:** 1.0.0

**Changelog:**
- 1.0.0 (2025-01-15): Initial release with 51 validation rules

### 10.4 Language Implementation Checklist

When implementing a new language validator:

- [ ] Implement all 24 CRITICAL rules (E-*)
- [ ] Implement at least 10 WARNING rules (W-*)
- [ ] Support JSON error output format
- [ ] Pass all test suite cases
- [ ] Provide CLI interface
- [ ] Include README with installation instructions
- [ ] Add to official validator registry
- [ ] Provide example usage
- [ ] Include performance benchmarks
- [ ] Support stdin/file input

### 10.5 Official Validator Registry

Maintained validators:

| Language | Repository | Maintainer | Status |
|----------|-----------|------------|--------|
| Python | TBD | Community | Planned |
| Node.js | TBD | Community | Planned |
| Rust | TBD | Community | Planned |
| Go | TBD | Community | Proposed |
| Java | TBD | Community | Proposed |

**Submit Your Implementation:**
Open a PR to add your validator to this registry with:
- Link to public repository
- Installation instructions
- Test coverage report
- Performance benchmarks

---

## Appendix A: Error Code Quick Reference

### CRITICAL (E-*)

| Code | Category | Description |
|------|----------|-------------|
| E-DOC-001 | Document | Missing YAML front matter |
| E-DOC-002 | Document | Invalid YAML syntax |
| E-DOC-003 | Document | Missing project_name |
| E-DOC-004 | Document | Missing source_language |
| E-DOC-005 | Document | Missing template_version |
| E-DOC-006 | Document | Empty markdown body |
| E-DOC-007 | Document | Missing root cluster |
| E-CMP-001 | Component | Missing Type keyword |
| E-CMP-002 | Component | Invalid Type value |
| E-CMP-003 | Component | Type not first keyword |
| E-CMP-004 | Component | Empty component name |
| E-CMP-005 | Component | Duplicate component name |
| E-REQ-001 | Required | Missing Units for quantified type |
| E-REQ-002 | Required | Empty Units value |
| E-REQ-003 | Required | Missing Enumeration for XdOrdinal |
| E-REQ-004 | Required | Root is not Cluster |
| E-BIZ-001 | Business | XdBoolean cannot have Enumeration |
| E-BIZ-002 | Business | XdBoolean cannot have Pattern |
| E-BIZ-003 | Business | XdString has both Pattern and Enumeration |
| E-BIZ-004 | Business | Min Length > Max Length |
| E-BIZ-005 | Business | Min Magnitude > Max Magnitude |
| E-BIZ-006 | Business | Min Date > Max Date |
| E-BIZ-007 | Business | Invalid regex pattern |
| E-SYN-001 | Syntax | Invalid keyword format |
| E-SYN-002 | Syntax | Invalid numeric value |
| E-SYN-003 | Syntax | Invalid component reference |

### WARNING (W-*)

| Code | Category | Description |
|------|----------|-------------|
| W-BP-001 | Best Practice | Missing Description |
| W-BP-002 | Best Practice | Component name too short |
| W-BP-003 | Best Practice | Missing Examples |
| W-BP-004 | Best Practice | Missing magnitude constraints |
| W-BP-005 | Best Practice | Missing Max Length |
| W-BP-006 | Best Practice | Missing Temporal Type |
| W-BP-007 | Best Practice | Empty Cluster |
| W-AMB-001 | Ambiguity | Ambiguous component name |
| W-AMB-002 | Ambiguity | Conflicting description |
| W-AMB-003 | Ambiguity | Units without definitions |
| W-AMB-004 | Ambiguity | Unclear ordinality |
| W-DEP-001 | Deprecated | Keyword "Values" deprecated |
| W-DEP-002 | Deprecated | Keyword "Unit" deprecated |

### SUGGESTION (S-*)

| Code | Category | Description |
|------|----------|-------------|
| S-OPT-001 | Optimization | Add Examples for patterns |
| S-OPT-002 | Optimization | Simplify descriptions |
| S-OPT-003 | Optimization | Reuse common components |
| S-OPT-004 | Optimization | Use XdToken for codes |
| S-OPT-005 | Optimization | Define Units separately |
| S-QL-001 | Quality | Add semantic context |
| S-QL-002 | Quality | Include units in description |
| S-QL-003 | Quality | Specify validation rules |
| S-QL-004 | Quality | Use consistent naming |
| S-QL-005 | Quality | Add metadata to front matter |

---

## Appendix B: Keyword Summary Table

| Keyword | Applicable Types | Required | Value Format | Notes |
|---------|------------------|----------|--------------|-------|
| Type | All | Yes | Valid SDC4 type | Must be first keyword |
| Description | All | Recommended | Free text | Improves LLM understanding |
| Examples | All | Optional | Free text | Helps LLM generate accurate models |
| Pattern | XdString, XdToken | Optional | Valid regex | Mutually exclusive with Enumeration |
| Enumeration | XdString, XdOrdinal | Conditional | List | Required for XdOrdinal, exclusive with Pattern for XdString |
| Min Length | XdString, XdToken | Optional | Positive integer | Must be ≤ Max Length |
| Max Length | XdString, XdToken | Optional | Positive integer | Must be ≥ Min Length |
| Units | XdCount, XdQuantity, XdFloat, XdDouble | Yes | Unit symbols or @ref | Can be inline or reference |
| Min Magnitude | Quantified types | Optional | Number | Must be ≤ Max Magnitude |
| Max Magnitude | Quantified types | Optional | Number | Must be ≥ Min Magnitude |
| Precision | XdQuantity | Optional | Positive integer | Total significant digits |
| Fraction Digits | XdQuantity | Optional | Non-negative integer | Decimal places |
| Temporal Type | XdTemporal | Recommended | date, time, datetime, duration | Clarifies granularity |
| Min Date | XdTemporal | Optional | ISO 8601 date | Must be ≤ Max Date |
| Max Date | XdTemporal | Optional | ISO 8601 date | Must be ≥ Min Date |
| Default Value | XdBoolean | Optional | "true" or "false" | Initial state |
| Media Types | XdFile | Optional | MIME types | Comma-separated |
| Max Size | XdFile | Optional | Integer with unit | e.g., "10MB" |
| Cardinality | Cluster | Optional | "min..max" | Instance count constraints |

---

## Appendix C: Resources

### Official Documentation

- **Form2SDCTemplate Repository:** [GitHub URL]
- **SDC4 Reference Model:** [Documentation URL]
- **SDCStudio Platform:** [https://sdcstudio.example.com](https://sdcstudio.example.com)

### Community

- **Discussion Forum:** [Forum URL]
- **Issue Tracker:** [GitHub Issues URL]
- **Slack Channel:** #form2sdc-validators

### Related Specifications

- **YAML 1.2:** https://yaml.org/spec/1.2/spec.html
- **CommonMark Markdown:** https://spec.commonmark.org/
- **Semantic Versioning:** https://semver.org/

---

## License

This specification is licensed under **Apache-2.0**.

Community implementations may use any OSI-approved license.

---

## Acknowledgments

This specification was developed for the Form2SDCTemplate community with input from SDCStudio developers and early adopters. Special thanks to all contributors who helped refine validation rules and implementation examples.

**Contributors:**
- Tim Cook (SDCStudio Lead Developer)
- Claude AI (Anthropic) - Specification drafting assistance

---

**End of Form2SDCTemplate Validator Specification v1.0.0**
