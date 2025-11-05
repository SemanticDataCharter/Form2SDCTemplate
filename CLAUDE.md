# CLAUDE.md - AI-Assisted Development Guide

This document provides detailed guidance for developers and AI assistants (like Claude) working on the Form2SDCTemplate project.

---

## Project Overview

### Purpose
Form2SDCTemplate is a specialized tool that bridges human-readable form descriptions and machine-readable SDC4 (Semantic Data Charter Generation 4) template specifications. It provides structured markdown documentation optimized for Large Language Models to automatically generate SDCStudio templates.

### Core Objective
Enable rapid, AI-assisted creation of standards-compliant SDC4 templates without requiring deep technical expertise in XML Schema, RDF/OWL, or metadata standards.

---

## Architecture

### Project Structure

```
Form2SDCTemplate/
├── LICENSE                 # Apache 2.0 license
├── README.md              # Primary documentation
├── CLAUDE.md              # This file
├── CONTRIBUTING.md        # Contribution guidelines
├── SECURITY.md            # Security policy
├── CODE_OF_CONDUCT.md     # Community standards
├── CHANGELOG.md           # Version history
├── .github/               # GitHub templates and workflows
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
└── templates/             # (Planned) LLM-optimized markdown templates
    └── form-template.md   # (Planned) Main template file
```

### Design Philosophy

1. **LLM-First Design**: All documentation and templates are structured for optimal AI comprehension
2. **Minimal Dependencies**: No runtime dependencies; pure markdown-based approach
3. **Standards Compliance**: Outputs conform to SDC4 specifications
4. **Iterative Refinement**: Support conversational template development

---

## Technical Context

### SDC4 Framework

Form2SDCTemplate generates templates for the Semantic Data Charter Generation 4 (SDC4) ecosystem:

- **Governance Layer**: Enforces compliance with W3C XML Schema, ISO 11179, ISO 20022
- **Semantic Layer**: Embeds meaning through RDF/OWL ontologies
- **Quality Layer**: Mandates data validation and ExceptionalValue handling

### Core SDC4 Concepts

**Data Types**: String, Integer, Decimal, Boolean, Date, DateTime, Time, Coded (controlled vocabulary), Measured (quantity with units)

**Governance Models**: Metadata registration, version control, provenance tracking

**Semantic Annotations**: Concept mappings, terminology bindings, relationship definitions

---

## Development Guidelines

### For AI Assistants

When working on this project:

1. **Understand SDC4 Context**: Review [SDCRM](https://github.com/SemanticDataCharter/SDCRM) for specification details
2. **Maintain LLM Compatibility**: Ensure all templates remain clear and unambiguous for AI parsing
3. **Preserve Standards Compliance**: Generated templates must validate against SDC4 schemas
4. **Test with Multiple LLMs**: Verify templates work across different AI models (Claude, GPT-4, etc.)
5. **Document Examples**: Provide concrete examples for common form patterns

### Code Quality Standards

- **Markdown Formatting**: Use consistent heading hierarchy, code blocks, and formatting
- **Clear Instructions**: Write step-by-step guidance that both humans and LLMs can follow
- **Example Patterns**: Include examples for common use cases (clinical forms, surveys, data collection)
- **Error Handling**: Document how to handle ambiguous or incomplete form descriptions

### Testing Approach

1. **Template Validation**: Test templates with multiple LLM providers
2. **Output Verification**: Validate generated XML against SDC4 schemas using [sdcvalidator](https://github.com/SemanticDataCharter/sdcvalidator)
3. **Round-Trip Testing**: Ensure templates can be parsed back into form descriptions
4. **Edge Cases**: Test with complex forms (nested sections, conditional logic, calculations)

---

## Common Tasks

### Adding a New Template Pattern

1. Create a new section in the template markdown file
2. Provide clear field descriptions and data type specifications
3. Include an example showing expected LLM input and output
4. Test with at least two different LLM providers
5. Document in CHANGELOG.md

### Updating for SDC4 Specification Changes

1. Review SDCRM repository for specification updates
2. Identify affected template sections
3. Update markdown instructions to reflect changes
4. Update version number following semantic versioning
5. Add migration notes to CHANGELOG.md

### Improving LLM Comprehension

1. Analyze failed or incorrect generations
2. Identify ambiguous instructions or missing context
3. Add clarifying examples or constraints
4. Test improvements with multiple LLMs
5. Document patterns in this CLAUDE.md file

---

## Key Dependencies and Relationships

### Upstream Dependencies
- **SDCRM**: Reference model and schema definitions
- **SDC4 Specification**: Normative requirements for template structure

### Downstream Consumers
- **sdcvalidator**: Validates generated templates
- **SDCStudio**: (Future) Template editor and management tool
- **User LLMs**: Claude, ChatGPT, and other AI assistants

---

## Common Patterns and Examples

### Basic Form Structure
```markdown
Form: Patient Registration
Sections:
  - Demographics
    - Name (String, required)
    - Date of Birth (Date, required)
    - Gender (Coded, required, valueSet: AdministrativeGender)
  - Contact Information
    - Email (String, optional)
    - Phone (String, optional)
```

### Data Type Specifications
- String: Free text, specify max length if applicable
- Coded: Controlled vocabulary, specify valueSet
- Measured: Numeric value with units, specify unit system
- Date/DateTime: ISO 8601 format

### Validation Rules
- Required vs. Optional fields
- Conditional visibility (show field X if Y is selected)
- Calculated fields (field C = A + B)
- Range constraints (age between 0-120)

---

## Troubleshooting

### Template Generation Issues

**Problem**: LLM generates invalid XML structure
- **Solution**: Review template instructions for clarity; add explicit structural examples

**Problem**: Missing semantic annotations
- **Solution**: Ensure template includes guidance on concept mappings and terminology bindings

**Problem**: Inconsistent data types
- **Solution**: Provide clear data type reference table in template documentation

---

## Version Strategy

This project follows semantic versioning aligned with SDC4:

- **Major (4.x.x)**: SDC Generation 4 compatibility
- **Minor (4.X.x)**: New template patterns or LLM improvements
- **Patch (4.x.X)**: Bug fixes and documentation updates

---

## Resources

### Internal Documentation
- [README.md](README.md) - User-facing documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution workflow
- [CHANGELOG.md](CHANGELOG.md) - Version history

### External Resources
- [SDCRM Repository](https://github.com/SemanticDataCharter/SDCRM)
- [SDC4 Specification](https://github.com/SemanticDataCharter/SDCRM/blob/main/sdc4/specification/sdc4-specification.md)
- [sdcvalidator Documentation](https://github.com/SemanticDataCharter/sdcvalidator)

### Standards References
- W3C XML Schema: https://www.w3.org/XML/Schema
- W3C RDF/OWL: https://www.w3.org/OWL/
- ISO 11179: Metadata registries
- ISO 20022: Financial data standards
- HL7 Standards: Healthcare interoperability

---

## Contact and Support

For questions or clarifications:
- **Issues**: [GitHub Issues](https://github.com/SemanticDataCharter/Form2SDCTemplate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SemanticDataCharter/Form2SDCTemplate/discussions)
- **Email**: security@axius-sdc.com

---

**Note to AI Assistants**: This document is specifically designed to provide you with the context needed to effectively contribute to this project. When making changes, prioritize clarity, standards compliance, and LLM compatibility. Always test your modifications with real LLM interactions before submitting.
