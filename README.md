# Form2SDCTemplate

[![Version](https://img.shields.io/badge/version-4.2.3-blue)](https://github.com/SemanticDataCharter/Form2SDCTemplate)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![SDC](https://img.shields.io/badge/SDC-4.0-purple)](https://github.com/SemanticDataCharter/SDCRM)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SemanticDataCharter/Form2SDCTemplate/blob/main/notebooks/form_to_template.ipynb)

Convert PDF, DOCX, and image forms into SDC4-compliant templates — powered by Gemini AI.

---

## Overview

Form2SDCTemplate provides two ways to generate SDC4 templates:

1. **Google Colab Notebook** (new) — Upload a form, get a validated template automatically
2. **Manual LLM Usage** — Upload `Form2SDCTemplate.md` to any LLM as instructions

Both approaches produce standards-compliant SDC4 templates ready for SDCStudio upload.

## Quick Start with Google Colab

The fastest way to convert a form to an SDC4 template:

1. Open the [Form2SDCTemplate Colab notebook](https://colab.research.google.com/github/SemanticDataCharter/Form2SDCTemplate/blob/main/notebooks/form_to_template.ipynb)
2. Enter your [Google AI API key](https://aistudio.google.com/apikey)
3. Upload your form (PDF, DOCX, PNG, JPG)
4. Download the generated SDC4 markdown template
5. Upload to SDCStudio for processing

### Quick Start with Python

```bash
pip install "form2sdc[gemini]"
```

```python
from form2sdc.analyzer import GeminiAnalyzer
from form2sdc.core import FormToTemplatePipeline
from pathlib import Path

analyzer = GeminiAnalyzer(api_key="YOUR_KEY")
pipeline = FormToTemplatePipeline(analyzer)
result = pipeline.process(Path("your_form.pdf"))

print(result.template)       # SDC4 markdown
print(result.validation.valid)  # True if valid
```

### Validate an existing template

```python
from form2sdc.validator import Form2SDCValidator

validator = Form2SDCValidator()
result = validator.validate(open("template.md").read())

if result.valid:
    print("Template is valid!")
else:
    for error in result.errors:
        print(f"[{error.code}] {error.message}")
```

## Manual LLM Usage

### Option 1: Direct Download (Recommended)

1. Click on [Form2SDCTemplate.md](Form2SDCTemplate.md) in this repository
2. Look for the **Download** button (down arrow ⬇) in the upper right of the file view
3. Save the file to your computer
4. Upload `Form2SDCTemplate.md` to your preferred LLM (Claude, ChatGPT, etc.)
5. Provide your form description, PDF, or requirements to the LLM
6. Review the generated template and upload it to SDCStudio for processing

### Option 2: Clone Repository (For Contributors)

1. Clone this repository:
   ```bash
   git clone https://github.com/SemanticDataCharter/Form2SDCTemplate.git
   cd Form2SDCTemplate
   ```

2. Upload `Form2SDCTemplate.md` to your preferred LLM (e.g., Claude, ChatGPT, etc.)

3. Provide your form description, PDF, or requirements to the LLM

4. The LLM will generate a properly formatted SDCStudio template

5. Review the generated template and upload it to SDCStudio for processing

## Features

### LLM-Optimized Instructions
- Comprehensive step-by-step guide for AI assistants
- Complete keyword glossary with usage examples
- Clear structure and formatting requirements
- Multi-language support (keywords in English, content in source language)

### SDC4 Compliance
- Generates templates conforming to SDC 4.0 specifications
- Supports all SDC4 data types (XdString, XdCount, XdQuantity, etc.)
- User-friendly type system (text, integer, decimal, date, etc.)
- Intelligent type mapping based on context clues

### Complete Template Generation
- YAML front matter with metadata
- Dataset overview and business context
- Root and sub-cluster organization
- Column definitions with constraints and enumerations
- Component reuse support (NIEM, FHIR, HL7v3)
- Example templates in English, French, and Brazilian Portuguese

### Rapid Development
- Eliminates manual template creation
- Reduces development time from hours to minutes
- Enables iterative refinement through conversational AI
- Supports forms in any language

## Use Cases

This tool is designed for:

- **Healthcare Organizations** developing clinical data collection forms
- **Research Institutions** creating standardized research data templates
- **Data Architects** prototyping SDC4 template structures
- **Developers** integrating SDC4 into existing systems
- **Data Governance Teams** standardizing data collection processes

## Documentation

- [Form2SDCTemplate.md](Form2SDCTemplate.md) - Complete LLM instructions and reference guide
- [CLAUDE.md](CLAUDE.md) - Detailed guidance for AI-assisted development
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to this project
- [SECURITY.md](SECURITY.md) - Security policy and vulnerability reporting
- [CHANGELOG.md](CHANGELOG.md) - Version history and release notes

## How It Works

1. **Upload Instructions**: Upload `Form2SDCTemplate.md` to an LLM (Claude, ChatGPT, etc.)
2. **Provide Form**: Share your form description, PDF, or requirements
3. **LLM Generates**: The LLM creates a properly formatted template following SDC4 specifications
4. **Review & Upload**: Review the generated template and upload to SDCStudio
5. **Automatic Processing**: SDCStudio's MD2PD system parses and validates the template

## Usage Examples

Below are example prompts showing how to request template generation from an LLM. Upload `Form2SDCTemplate.md` first, then use one of these prompts along with your form/PDF.

### English (en)

```
Please use the instructions in Form2SDCTemplate.md along with the attached PDF form
to create an SDCStudio template in markdown format.

Key requirements:
- Use English keywords (Type, Description, Enumeration, etc.)
- Keep all field names, descriptions, and values in the same language as the form
- Include all fields from the PDF with appropriate data types
- Add constraints for required fields and validation rules
- Use enumerations for dropdown lists and radio buttons
- Provide realistic examples for each field
```

### French (fr)

```
Veuillez utiliser les instructions dans Form2SDCTemplate.md avec le formulaire PDF
ci-joint pour créer un template SDCStudio au format markdown.

Exigences clés :
- Utiliser les mots-clés en anglais (Type, Description, Enumeration, etc.)
- Conserver tous les noms de champs, descriptions et valeurs dans la langue du formulaire
- Inclure tous les champs du PDF avec les types de données appropriés
- Ajouter des contraintes pour les champs obligatoires et les règles de validation
- Utiliser des énumérations pour les listes déroulantes et boutons radio
- Fournir des exemples réalistes pour chaque champ
```

### Brazilian Portuguese (pt-BR)

```
Por favor, use as instruções no Form2SDCTemplate.md junto com o formulário PDF
anexado para criar um template SDCStudio em formato markdown.

Requisitos principais:
- Usar palavras-chave em inglês (Type, Description, Enumeration, etc.)
- Manter todos os nomes de campos, descrições e valores no idioma do formulário
- Incluir todos os campos do PDF com os tipos de dados apropriados
- Adicionar restrições para campos obrigatórios e regras de validação
- Usar enumerações para listas suspensas e botões de opção
- Fornecer exemplos realistas para cada campo
```

### Spanish (es)

```
Por favor, utiliza las instrucciones en Form2SDCTemplate.md junto con el formulario PDF
adjunto para crear una plantilla SDCStudio en formato markdown.

Requisitos clave:
- Usar palabras clave en inglés (Type, Description, Enumeration, etc.)
- Mantener todos los nombres de campos, descripciones y valores en el idioma del formulario
- Incluir todos los campos del PDF con los tipos de datos apropiados
- Agregar restricciones para campos obligatorios y reglas de validación
- Usar enumeraciones para listas desplegables y botones de opción
- Proporcionar ejemplos realistas para cada campo
```

### Advanced Usage Examples

**With specific domain context:**

```
I'm uploading a healthcare patient intake form (PDF attached). Please use
Form2SDCTemplate.md to create a template.

Additional context:
- Domain: Healthcare
- This form will be used in a clinical setting
- Fields like patient_id, date_of_birth, and medical_record_number should use
  identifier type
- Include HIPAA-relevant field classifications where applicable
- Enable LLM enrichment (set enable_llm: true)
```

**Multiple forms/sections:**

```
I have three related forms (PDFs attached):
1. Patient Demographics
2. Medical History
3. Insurance Information

Please use Form2SDCTemplate.md to create a single template with three sub-clusters,
one for each form. Use appropriate data types and maintain the relationships between
sections.
```

**Form in specific language:**

```
Attached is a Brazilian government form (Cadastro de Contribuinte) in Portuguese.
Please use Form2SDCTemplate.md to generate the template.

Important:
- Keep all keywords in English (Type, Description, etc.)
- Keep all content in Portuguese (field names, descriptions, examples)
- Include Brazilian-specific fields (CPF, CNPJ, CEP, UF)
- Use proper Brazilian address format
- Include all 27 Brazilian states in UF enumeration
```

## Related Projects

Part of the Semantic Data Charter ecosystem:

- [SDCRM](https://github.com/SemanticDataCharter/SDCRM) - Reference model and schemas
- [SDCObsidianTemplate](https://github.com/SemanticDataCharter/SDCObsidianTemplate) - Obsidian vault template
- [sdcvalidator](https://github.com/SemanticDataCharter/sdcvalidator) - Python validation library
- [sdcvalidatorJS](https://github.com/SemanticDataCharter/sdcvalidatorJS) - JavaScript/npm validator

## System Requirements

**For Colab/Python usage:**
- Python 3.10+
- Google AI API key (free tier available at [aistudio.google.com](https://aistudio.google.com/apikey))

**For manual LLM usage:**
- LLM with markdown file upload capability (Claude, ChatGPT, etc.)
- Basic understanding of form structure and data collection

**Optional:** SDCStudio for template testing and refinement

## Standards Compliance

Form2SDCTemplate supports generation of templates compliant with:

- W3C XML Schema (XSD)
- W3C RDF/OWL for semantic modeling
- ISO 11179 metadata standards
- ISO 20022 data component specifications
- HL7 standards for healthcare data

## Version Information

**Current Version:** 4.2.3

The major version (4.x.x) aligns with SDC Generation 4, ensuring compatibility across the SDC4 ecosystem. See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- How to submit issues and feature requests
- Guidelines for pull requests
- Development workflow and testing procedures
- Community standards and code of conduct

## Security

For security concerns or vulnerability reports, please refer to our [SECURITY.md](SECURITY.md) policy or contact security@axius-sdc.com.

## License

Copyright 2025 Axius-SDC, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Acknowledgments

This project builds upon:

- The Semantic Data Charter (SDC) framework
- International standards from W3C, ISO, and HL7
- Open source contributions from the data modeling community
- Academic research in semantic data representation (12+ peer-reviewed papers, 165+ citations)

## Support

- **Issues:** [GitHub Issues](https://github.com/SemanticDataCharter/Form2SDCTemplate/issues)
- **Discussions:** [GitHub Discussions](https://github.com/SemanticDataCharter/Form2SDCTemplate/discussions)
- **Email:** security@axius-sdc.com
- **Website:** Coming soon

---

**Semantic Data Charter™** and **SDC™** are trademarks of Axius-SDC, Inc.
