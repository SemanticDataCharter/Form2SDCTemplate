# Contributing to Form2SDCTemplate

Thank you for your interest in contributing to Form2SDCTemplate! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Contribution Workflow](#contribution-workflow)
- [Contribution Types](#contribution-types)
- [Quality Standards](#quality-standards)
- [Review Process](#review-process)
- [Community](#community)

---

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

By participating, you agree to:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community

---

## How Can I Contribute?

There are many ways to contribute to Form2SDCTemplate:

### Encouraged Contributions

The following contributions are always welcome and don't require extensive discussion:

- **Documentation Improvements**: Clarify instructions, fix typos, add examples
- **Template Examples**: Provide sample form descriptions and generated templates
- **Testing**: Test templates with different LLM providers and report results
- **Bug Reports**: Report issues with template generation or documentation
- **Use Case Documentation**: Share how you're using Form2SDCTemplate

### Contributions Requiring Discussion

The following contributions benefit from community discussion before implementation:

- **Template Structure Changes**: Modifications to core template format
- **New Template Patterns**: Addition of new form patterns or capabilities
- **Architecture Changes**: Significant alterations to project structure
- **SDC4 Specification Updates**: Changes related to SDC4 standard evolution

For these contributions, please open an issue first to discuss your proposal.

---

## Getting Started

### Prerequisites

- GitHub account
- Basic understanding of Git and GitHub workflow
- Familiarity with Markdown formatting
- (Optional) Access to LLM platforms (Claude, ChatGPT, etc.) for testing

### Development Environment

Form2SDCTemplate is a documentation-focused project with minimal setup:

1. **Fork the Repository**
   ```bash
   # Visit https://github.com/SemanticDataCharter/Form2SDCTemplate
   # Click "Fork" to create your own copy
   ```

2. **Clone Your Fork**
   ```bash
   git clone git@github.com:YOUR_USERNAME/Form2SDCTemplate.git
   cd Form2SDCTemplate
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream git@github.com:SemanticDataCharter/Form2SDCTemplate.git
   ```

4. **Stay Updated**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

---

## Contribution Workflow

We follow a standard GitHub workflow:

### 1. Create an Issue

For significant changes, create an issue first:
- Describe the problem or enhancement
- Explain your proposed solution
- Wait for maintainer feedback

For small fixes (typos, formatting), you can skip directly to creating a pull request.

### 2. Create a Branch

```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/description` - New features or enhancements
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `test/description` - Testing improvements

### 3. Make Your Changes

- Follow the [Quality Standards](#quality-standards) below
- Test your changes with LLM providers if applicable
- Keep commits focused and atomic
- Write clear commit messages

### 4. Commit Your Changes

```bash
git add .
git commit -m "Brief description of changes

Detailed explanation of what changed and why.
References #issue-number if applicable."
```

Commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- First line should be 50 characters or less
- Add detailed description after blank line if needed
- Reference relevant issues with #issue-number

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

1. Visit your fork on GitHub
2. Click "Pull Request" button
3. Select your branch and the main repository's `main` branch
4. Fill out the pull request template
5. Submit the pull request

### 7. Address Review Feedback

- Respond to reviewer comments
- Make requested changes
- Push updates to your branch (PR updates automatically)
- Re-request review when ready

### 8. Merge

Once approved, a maintainer will merge your pull request.

---

## Contribution Types

### Documentation Improvements

**Examples:**
- Clarifying template instructions
- Adding examples for common form patterns
- Fixing typos or formatting issues
- Improving README or other docs

**Guidelines:**
- Use clear, concise language
- Provide examples where helpful
- Maintain consistent formatting
- Test instructions for accuracy

### Template Enhancements

**Examples:**
- Adding new form pattern examples
- Improving LLM instruction clarity
- Adding data type references
- Enhancing validation guidance

**Guidelines:**
- Test with multiple LLM providers
- Ensure SDC4 compliance
- Document new patterns in CLAUDE.md
- Update CHANGELOG.md

### Bug Fixes

**Examples:**
- Correcting template generation issues
- Fixing broken links or references
- Resolving ambiguous instructions

**Guidelines:**
- Reference the issue being fixed
- Explain the root cause
- Describe the solution
- Add tests if applicable

### Testing and Validation

**Examples:**
- Testing templates with different LLMs
- Validating generated output with sdcvalidator
- Reporting edge cases or failures
- Creating test case documentation

**Guidelines:**
- Document test methodology
- Provide reproducible examples
- Share both successes and failures
- Suggest improvements based on findings

---

## Quality Standards

### Markdown Formatting

- Use consistent heading hierarchy (# for H1, ## for H2, etc.)
- Include blank lines between sections
- Use code blocks with language specification
- Format lists consistently (use `-` for unordered lists)

### Documentation Style

- Write in clear, professional English
- Use active voice ("The template generates..." not "The template is generated...")
- Avoid jargon unless necessary; define technical terms
- Provide examples for complex concepts
- Keep sentences and paragraphs concise

### LLM Compatibility

- Write unambiguous instructions
- Use consistent terminology
- Provide explicit structural examples
- Avoid implicit assumptions
- Test instructions with real LLM interactions

### SDC4 Compliance

- Verify alignment with SDC4 specification
- Reference official standards documentation
- Test generated templates with sdcvalidator
- Maintain semantic correctness

---

## Review Process

### What Reviewers Look For

1. **Correctness**: Does it work as intended?
2. **Clarity**: Is the documentation clear and understandable?
3. **Completeness**: Are all necessary components included?
4. **Consistency**: Does it match existing style and conventions?
5. **Testing**: Has it been adequately tested?

### Timeline Expectations

- **Initial Review**: Within 3-5 business days
- **Follow-up Reviews**: Within 2-3 business days
- **Merge**: After approval and all checks pass

### Review Outcomes

- **Approved**: Ready to merge
- **Changes Requested**: Needs modifications before approval
- **Commented**: Suggestions or questions (not blocking)

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, community chat
- **Email**: security@axius-sdc.com for security issues

### Getting Help

If you're stuck or have questions:

1. Check existing documentation (README, CLAUDE.md)
2. Search existing issues and discussions
3. Open a new discussion for general questions
4. Open an issue for specific problems

### Recognition

Contributors are recognized in several ways:
- Listed in pull request history
- Mentioned in CHANGELOG.md for significant contributions
- GitHub contributor badge on profile

---

## License

By contributing to Form2SDCTemplate, you agree that your contributions will be licensed under the Apache License 2.0, the same license as the project.

You must have the right to submit your contributions (own the code or have permission from the copyright holder).

---

## Questions?

If you have questions about contributing, please:
- Open a [GitHub Discussion](https://github.com/SemanticDataCharter/Form2SDCTemplate/discussions)
- Review [CLAUDE.md](CLAUDE.md) for technical guidance
- Contact the maintainers via email: security@axius-sdc.com

Thank you for contributing to Form2SDCTemplate and the Semantic Data Charter ecosystem!
