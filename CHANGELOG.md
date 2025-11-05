# Changelog

All notable changes to Form2SDCTemplate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
aligned with SDC Generation 4.

## Version Scheme

- **Major (4.x.x)**: SDC Generation 4 compatibility
- **Minor (4.X.x)**: New template patterns, features, or LLM improvements
- **Patch (4.x.X)**: Bug fixes, documentation updates, minor enhancements

---

## [Unreleased]

### Added
- Brazilian Portuguese (pt-BR) example templates
  - Healthcare: SUS Patient Registration with CNS, CPF, Brazilian states
  - Government: CPF Application form with Receita Federal requirements
  - E-commerce: Customer registration with LGPD compliance and loyalty program
  - Complete Brazilian-specific enumerations (UF states, document types)
  - Brazilian address format (CEP, logradouro, bairro)
  - Healthcare specific fields (tipo sanguíneo, identidade de gênero, raça/cor IBGE)
- Usage examples section in README
  - Example prompts in English, French, Brazilian Portuguese, and Spanish
  - Basic usage prompts for PDF form conversion
  - Advanced usage examples (domain-specific, multiple forms, language-specific)
  - Clear guidance on keyword vs. content language requirements

### Planned
- Usage tutorials and video guides
- Integration examples with sdcvalidator
- Additional language-specific examples (Spanish, German, Japanese)
- Template validation tools

---

## [4.0.0] - 2025-11-05

### Added
- **Form2SDCTemplate.md** - Complete LLM instruction guide for template generation
  - Comprehensive keyword glossary (Type, Description, Enumeration, Constraints, etc.)
  - Complete type reference (user-friendly types and SDC4 types)
  - Multi-language support guidance (keywords in English, content in source language)
  - Step-by-step generation process for LLMs
  - Enumeration syntax (list and table formats)
  - Constraints syntax and examples
  - Sub-cluster organization guidance
  - Component reuse instructions (NIEM, FHIR, HL7v3)
  - Quality checklist for template validation
  - Complete example templates in English and French
- Initial repository structure
- Comprehensive README.md with badges, sections, and professional formatting
- CLAUDE.md with detailed AI-assisted development guidance
- CONTRIBUTING.md with contribution workflow and guidelines
- SECURITY.md with security policy and vulnerability reporting process
- CODE_OF_CONDUCT.md based on Contributor Covenant 2.1
- CHANGELOG.md (this file) for version tracking
- Apache 2.0 LICENSE
- GitHub templates for issues and pull requests
- GitHub workflows for documentation validation
- .gitignore with comprehensive exclusions
- Configuration files (.markdownlint.json, .markdown-link-check.json, .spellcheck.yml)

### Project Structure
- Documentation-focused repository design
- LLM-compatible template approach
- SDC4 ecosystem integration
- Professional open source standards

### Standards Compliance
- Aligned with SDC Generation 4 specifications
- W3C XML Schema (XSD) compliance
- ISO 11179 metadata standards support
- ISO 20022 data component compatibility
- HL7 healthcare data standards

### Documentation
- Quick start guide for users
- Comprehensive feature descriptions
- Use case documentation
- Related projects and ecosystem links
- Version information and compatibility notes
- Support channels and contact information

### Community
- Contribution guidelines with 8-step workflow
- Code of Conduct with SDC-specific values
- Security policy with coordinated disclosure process
- Issue and pull request templates
- Discussion guidelines

### Security
- Vulnerability reporting process established
- Best practices for LLM interaction documented
- Template validation guidance provided
- Privacy considerations outlined

---

## Version History Summary

| Version | Release Date | Major Changes |
|---------|-------------|---------------|
| 4.0.0   | 2025-11-05  | Initial release with full documentation suite |

---

## Migration Guide

### From No Version to 4.0.0

This is the initial release. No migration needed.

**New Users**: Start with the [README.md](README.md) for an overview and quick start guide.

**Contributors**: Review [CONTRIBUTING.md](CONTRIBUTING.md) and [CLAUDE.md](CLAUDE.md) before contributing.

---

## Future Roadmap

### Version 4.1.0 (Planned)
- LLM template markdown file
- Common form pattern examples
- Tutorial documentation
- Video guides

### Version 4.2.0 (Planned)
- Advanced template patterns
- Conditional logic support
- Calculated field examples
- Integration guides

### Version 4.3.0 (Planned)
- Multi-language support
- Internationalization guidance
- Localized examples
- Translation workflows

### Version 5.0.0 (Future)
- Alignment with SDC Generation 5 (when released)
- Breaking changes as needed for SDC5 compatibility

---

## Versioning Policy

### When We Increment Versions

**Major Version (4.x.x → 5.x.x)**
- SDC Generation changes
- Breaking changes to template format
- Major architectural shifts

**Minor Version (4.1.x → 4.2.x)**
- New template patterns or features
- LLM instruction enhancements
- New documentation sections
- Backward-compatible additions

**Patch Version (4.1.1 → 4.1.2)**
- Bug fixes in documentation
- Typo corrections
- Link updates
- Clarifications without functional changes
- Security fixes

### Deprecation Policy

When features are deprecated:
1. Announced in CHANGELOG.md
2. Marked with deprecation notices in documentation
3. Supported for at least 2 minor versions
4. Removed in next major version

---

## Release Notes Format

Each release includes:

### Added
New features, files, or capabilities

### Changed
Changes to existing functionality

### Deprecated
Features marked for future removal

### Removed
Features removed in this version

### Fixed
Bug fixes and corrections

### Security
Security-related changes or fixes

---

## Links

- [Repository](https://github.com/SemanticDataCharter/Form2SDCTemplate)
- [Issue Tracker](https://github.com/SemanticDataCharter/Form2SDCTemplate/issues)
- [Discussions](https://github.com/SemanticDataCharter/Form2SDCTemplate/discussions)
- [SDCRM](https://github.com/SemanticDataCharter/SDCRM) - Parent specification
- [SDC Ecosystem](https://github.com/SemanticDataCharter)

---

## Contributors

Thank you to all contributors who have helped improve Form2SDCTemplate!

See [GitHub Contributors](https://github.com/SemanticDataCharter/Form2SDCTemplate/graphs/contributors) for a full list.

---

*For security-related changes, see [SECURITY.md](SECURITY.md)*

*For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)*

[Unreleased]: https://github.com/SemanticDataCharter/Form2SDCTemplate/compare/v4.0.0...HEAD
[4.0.0]: https://github.com/SemanticDataCharter/Form2SDCTemplate/releases/tag/v4.0.0
