# Form2SDCTemplate: LLM Instructions for Creating SDCStudio Templates

**VERSION:** 4.1.0
**TARGET:** Large Language Models (Claude, ChatGPT, etc.)
**PURPOSE:** Generate SDCStudio-compliant dataset templates from form descriptions

---

## Instructions for Large Language Models

You are tasked with creating an SDCStudio template from a form description provided by the user. This document contains all the information you need to generate a properly formatted template.

### Critical Language Requirements

**KEYWORDS MUST BE IN ENGLISH:**
- All markdown keyword labels MUST be in English (e.g., `**Type**:`, `**Description**:`, `**Enumeration**:`)
- All SDC4 data types MUST be in English (e.g., `text`, `integer`, `date`)
- All template structure keywords MUST be in English (e.g., `Column:`, `Root Cluster:`)

**CONTENT SHOULD MATCH SOURCE LANGUAGE:**
- Column names should be in the same language as the source form/PDF
- Descriptions should be in the same language as the source form/PDF
- Business rules should be in the same language as the source form/PDF
- Enumeration values and labels should be in the same language as the source form/PDF
- Examples should reflect the source language and format

**Example:**
If analyzing a French form:
```markdown
### Column: nom_complet
**Type**: text
**Description**: Nom complet du patient (prénom et nom de famille)
**Constraints**:
  - required: true
**Examples**: Jean Dupont, Marie Martin
```

---

## Template Structure Overview

Every template MUST follow this structure:

```
1. YAML Front Matter (metadata)
2. Dataset Overview (purpose and context)
3. Subject Section (optional — who the record is about)
4. Provider Section (optional — who provided the data)
5. Participation Sections (optional — other involved parties)
6. Root Cluster (primary data grouping)
7. Column Definitions (individual fields)
8. Additional Clusters (optional logical groupings)
```

---

## PART 1: YAML Front Matter

Start every template with YAML front matter enclosed in `---`:

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Dataset Name Here"
  description: "Brief description of the dataset"
  domain: "Healthcare|Finance|Government|Retail|etc."  # Optional
  creator: "Creator Name"                               # Optional
  project: "project_ct_id"                             # Optional
enrichment:
  enable_llm: true                                      # Optional: false for fast parsing
---
```

**Required Fields:**
- `template_version`: Always use `"4.0.0"`
- `dataset.name`: Clear, descriptive name for the dataset
- `dataset.description`: Brief overview (1-2 sentences)

**Optional Fields:**
- `dataset.domain`: Industry or domain (Healthcare, Finance, Government, Retail, Manufacturing, etc.)
- `dataset.creator`: Name of person or team creating the template
- `dataset.project`: CT_ID of parent project if linking to existing project
- `enrichment.enable_llm`: Set to `true` for semantic enhancement, `false` or omit for fast parsing

---

## PART 2: Dataset Overview Section

After the YAML front matter, provide a dataset overview:

```markdown
# Dataset Overview

[2-4 sentence description of the dataset purpose and scope]

**Purpose**: [Why this dataset exists and what problem it solves]

**Business Context**:
- Primary use: [Main use case or application]
- Secondary use: [Additional use cases if applicable]
- Stakeholders: [Who uses or needs this data]
```

**Guidelines:**
- Keep overview concise but informative
- Explain the business value
- Identify key stakeholders
- Use the same language as the source form for descriptions

---

## PART 3: Subject, Provider, and Participation Sections (Optional)

The SDC4 reference model supports three structural participation slots on every Data Model (DM). These sections define **who** is involved with the data, separate from **what** the data contains (which goes in the Root Cluster).

- **Subject** — The party the record is about (patient, citizen, vessel, taxpayer)
- **Provider** — The party that provided or maintains the data (hospital, registry office, port authority)
- **Participation** — Other involved parties (attending physician, registrar, lab technician)

**All three are optional.** Templates without them work exactly as before — all data goes into the Root Cluster. Use them when the form clearly identifies actors/participants beyond the data payload.

### Subject Section

Defines who the record is about. Only **one** `## Subject:` per template.

```markdown
## Subject: [Party Name]
**Description**: [Who this party is and their role]

### Column: column_name
**Type**: [type]
**Description**: [description]
**Examples**: [examples]
```

Columns under `## Subject:` become the Party's **details Cluster** — demographic or identity components (names, IDs, dates of birth) that describe the subject.

### Provider Section

Defines who provided or maintains the data. Only **one** `## Provider:` per template.

```markdown
## Provider: [Provider Name]
**Description**: [Who this provider is]

### Column: column_name
**Type**: [type]
**Description**: [description]
**Examples**: [examples]
```

### Participation Section

Defines other involved parties. **Multiple** `## Participation:` sections are allowed (the DM has a many-to-many relationship with Participations).

```markdown
## Participation: [Participant Name]
**Description**: [Role of this participant]
**Function**: [Function/role label]
**Function Description**: [What this function means]
**Mode**: [Interaction mode label]
**Mode Description**: [What this mode means]

### Column: column_name
**Type**: [type]
**Description**: [description]
**Examples**: [examples]
```

**Participation-specific keywords:**

| Keyword | Required | Description |
|---------|----------|-------------|
| `**Description**:` | No | Description of this participation |
| `**Function**:` | No | Role/function label (e.g., "Civil Registrar", "Attending Physician") |
| `**Function Description**:` | No | Explanation of the function |
| `**Mode**:` | No | Interaction mode (e.g., "In Person", "By Telephone", "Electronic") |
| `**Mode Description**:` | No | Explanation of the mode |

### Key Rules

1. **All three sections are optional** — existing templates without them work unchanged
2. **Only one `## Subject:` and one `## Provider:`** per template
3. **Multiple `## Participation:` sections allowed** (one per participant role)
4. **Columns are isolated** — columns under Subject/Provider/Participation do NOT appear in the data cluster
5. **Same column syntax** — `### Column:` entries use the same keywords as data cluster columns (`**Type**:`, `**Description**:`, `**ReuseComponent**:`, etc.)
6. **`**ReuseComponent**:` works** in party columns for cross-project component reuse

### When to Use These Sections

**Use Subject/Provider/Participation when:**
- The form clearly identifies a person or organization the record is about (patient, applicant, vessel)
- The form identifies who collects or maintains the data (hospital, government agency)
- The form identifies other participants (registrar, attending physician, inspector)
- Demographic data (names, IDs, birth dates) should be modeled separately from the data payload

**Keep everything in Root Cluster when:**
- The form is purely data-focused (sensor readings, financial transactions)
- There's no clear "who" beyond the data itself
- The form is simple and flat

---

## PART 4: Root Cluster Section

Define the primary data cluster:

```markdown
## Root Cluster: [Cluster Name]

[Description of what this cluster represents]

**Purpose**: [What this cluster contains and represents]
**Business Context**: [How this cluster is used in the business]
```

**Cluster Naming:**
- Use descriptive names that reflect the data grouping
- Examples: "Patient Demographics", "Order Information", "Incident Report"
- Use the source language for cluster names if the form is not in English

---

## PART 5: Column Definitions

This is the core of the template. For each field in the form, create a column definition.

### Basic Column Structure

```markdown
### Column: column_name
**Type**: [type]
**Description**: [Detailed description of the field]
**Constraints**:           # Optional but recommended
  - required: true|false
  - range: [min, max]      # For numeric types
  - precision: N           # For decimal types
  - format: "description"  # For string types
**Business Rules**: [Any business logic or validation rules]  # Optional
**Relationships**: [How this field relates to others]         # Optional
**Examples**: [example1, example2, example3]
```

### Complete Keyword Glossary

#### REQUIRED KEYWORDS (Must be present)

**`**Type**:`** (REQUIRED)
- Specifies the data type of the column
- Must be one of the types listed in the Type Reference below
- Always in English
- Example: `**Type**: integer`

**`**Description**:`** (REQUIRED)
- Detailed explanation of what this column contains
- Should be clear and comprehensive
- Use the source language for the description text
- Example: `**Description**: Patient's age in completed years`

**`**Examples**:`** (REQUIRED)
- 2-3 representative sample values
- Comma-separated list
- Should reflect real-world data patterns
- Use appropriate format for the data type
- Use source language for values
- Example: `**Examples**: 25, 42, 67`

#### CONDITIONAL KEYWORDS (Required in certain contexts)

**`**Units**:`** (REQUIRED for numeric quantities)
- Measurement units for numeric values
- Required for `integer` and `decimal` types when they represent quantities
- Examples: years, USD, kg, meters, items, count
- Example: `**Units**: years`

**`**Enumeration**:`** (REQUIRED for categorical fields)
- List of allowed values for categorical data
- Use when field has fixed set of options
- Two formats supported (see Enumeration Syntax section)
- Example:
  ```markdown
  **Enumeration**:
    - active: Account in good standing
    - suspended: Temporarily suspended
    - closed: Permanently closed
  ```

#### OPTIONAL KEYWORDS (Enhance the template)

**`**Constraints**:`**
- Validation rules and requirements
- Use bullet list format
- Common constraints:
  - `required: true|false` - Whether field is mandatory
  - `range: [min, max]` - Min/max values for numeric types (use `null` for unbounded)
  - `precision: N` - Decimal places for decimal types
  - `format: "description"` - Format requirements for strings
  - `unique: true` - Whether values must be unique
- Example:
  ```markdown
  **Constraints**:
    - required: true
    - range: [0, 120]
  ```

**`**Business Rules**:`**
- Business logic or validation rules beyond simple constraints
- Calculations, dependencies, or complex validations
- Use source language
- Example: `**Business Rules**: Must be 18+ for account creation`

**`**Relationships**:`**
- How this column relates to other columns
- Dependencies, derivations, or references
- Use source language
- Example: `**Relationships**: Derived from birth_date`

**`**Semantic Links**:`**
- URIs to ontology terms or standard codes
- Use for standards compliance (LOINC, SNOMED CT, HL7, etc.)
- List format, one URI per line
- Example:
  ```markdown
  **Semantic Links**:
    - https://loinc.org/21112-8/
    - http://snomed.info/id/248153007
  ```

**`**Reuse**:`** (Legacy syntax)
- Reference to existing component by CT_ID
- Example: `**Reuse**: ct_abc123xyz`

**`**ReuseComponent**:`** (New syntax - recommended)
- Reference to existing component by project and label
- Format: `@ProjectName:ComponentLabel`
- Examples:
  - `**ReuseComponent**: @NIEM:StateUSPostalServiceCode`
  - `**ReuseComponent**: @FHIR:Patient`
  - `**ReuseComponent**: @MyProject:CustomerEmail`

#### DOCUMENTATION KEYWORDS (Included in Description field)

These keywords are for enrichment and are included in the description field:

- `**Ontology Mappings**:` - Standard ontology codes
- `**Standard**:` - Compliance standards
- `**NIH CDE Source**:` - NIH CDE reference URL
- `**PHI Status**:` - HIPAA PHI classification
- `**Clinical Significance**:` - Medical importance
- `**HL7 Security Classification**:` - HL7 security labels
- `**Access Control Requirements**:` - Access restrictions
- `**De-identification Considerations**:` - De-ID guidance
- `**Calculation Method**:` - Derived field calculation
- `**Important Distinctions**:` - Key clarifications
- `**Important Notes**:` - Additional context

---

## PART 6: Type Reference

### User-Friendly Types (Recommended)

Use these simple, intuitive type names. The system will map them to SDC4 types automatically:

| Type Name | Description | Use For | Example |
|-----------|-------------|---------|---------|
| `text` | Free text, strings | Names, comments, open-ended fields | Full name, notes |
| `integer` | Whole numbers | Counts, ages, quantities | Age: 25, Count: 100 |
| `decimal` | Numbers with decimals | Prices, measurements, percentages | Price: 19.99, Weight: 68.5 |
| `boolean` | True/False values | Yes/No questions, flags | Is active: true |
| `date` | Dates only | Birth dates, registration dates | 2024-01-15 |
| `datetime` | Dates with time | Timestamps, appointment times | 2024-01-15T09:30:00 |
| `time` | Time only | Daily schedules, opening hours | 09:30:00 |
| `identifier` | IDs, codes, keys | Customer IDs, order numbers, UUIDs | CUST-12345, 550e8400-e29b... |
| `email` | Email addresses | Contact emails | user@example.com |
| `url` | Web links | Website URLs, profile links | https://example.com |

### Explicit SDC4 Types (Advanced)

If you need precise control, use explicit SDC4 types:

| SDC4 Type | Description | When to Use |
|-----------|-------------|-------------|
| `XdString` | Free text | Text without enumeration |
| `XdToken` | Categorical text | Text with fixed values (enumeration) |
| `XdCount` | Integer counts | Integers with units (items, count) |
| `XdOrdinal` | Ordinal values | Integers with enumeration (ranking, scale) |
| `XdQuantity` | Measured quantities | Decimals with units (kg, meters, USD) |
| `XdFloat` | Floating point | General decimals without high precision needs |
| `XdDouble` | High-precision decimals | Scientific measurements, coordinates |
| `XdBoolean` | Boolean | True/false, yes/no |
| `XdTemporal` | Dates/times | Any date, time, or datetime |
| `XdString` | Identifiers | IDs, codes, keys |
| `XdLink` | URLs | Web links, references |
| `XdFile` | File references | File uploads, attachments |

### Intelligent Type Mapping

The system uses context clues to choose the correct SDC4 type:

**Name Patterns (Highest Priority):**
- Columns ending in `_id`, `_code`, `_key` → `XdString`
- Columns ending in `_url`, `_link` → `XdLink`
- Columns starting with `is_`, `has_`, or ending in `_flag` → `XdBoolean`
- Columns ending in `_date`, `_at`, or named `created`, `updated` → `XdTemporal`

**Context-Based Mapping:**
- `integer` + units → `XdCount`
- `integer` + enumeration → `XdOrdinal`
- `integer` + name pattern `*_id` → `XdString`
- `decimal` + units → `XdQuantity`
- `decimal` + precision: 2 → `XdQuantity` (currency-like)
- `decimal` + precision: >10 → `XdDouble` (high precision)
- `text` + enumeration → `XdToken`
- `text` + no enumeration → `XdString`

---

## PART 7: Enumeration Syntax

For fields with a fixed set of allowed values, use enumeration.

### List Format (Recommended - Simple)

```markdown
**Enumeration**:
  - value1: Description of value 1
  - value2: Description of value 2
  - value3: Description of value 3
```

**Example:**
```markdown
**Enumeration**:
  - active: Account in good standing
  - suspended: Temporarily suspended
  - closed: Permanently closed
```

### Table Format (More Structured)

```markdown
**Enumeration**:
| Value | Label | Description |
|-------|-------|-------------|
| 1 | Active | Account in good standing |
| 2 | Suspended | Temporarily suspended |
| 3 | Closed | Permanently closed |
```

**Important:**
- Always use `**Enumeration**:` (NOT `**Values**:` or `**Value**:`)
- Use source language for value labels and descriptions
- Provide clear, descriptive labels for each value
- Include all possible values

---

## PART 8: Constraints Syntax

Define validation rules using a bullet list:

```markdown
**Constraints**:
  - required: true|false
  - range: [min, max]           # For numeric types
  - precision: N                # For decimal types (number of decimal places)
  - format: "description"       # For string types
  - unique: true                # If values must be unique
```

**Examples:**

Age constraint:
```markdown
**Constraints**:
  - required: true
  - range: [0, 120]
```

Currency constraint:
```markdown
**Constraints**:
  - required: true
  - precision: 2
  - range: [0, 999999.99]
```

Email constraint:
```markdown
**Constraints**:
  - required: true
  - format: "valid email address"
```

Identifier constraint:
```markdown
**Constraints**:
  - required: true
  - unique: true
  - format: "UUID v4"
```

---

---

## PART 10: Component Reuse (Advanced)

Reuse existing components from standard libraries or other projects instead of recreating them.

### When to Use Component Reuse

**Standards Compliance:**
- Using NIEM components for government/civic data
- Using FHIR components for healthcare data
- Using HL7v3 components for healthcare interoperability

**Time Savings:**
- Common patterns like addresses, state codes, dates
- Standard code lists (incident types, status codes)
- Validated components from trusted sources

### Component Reuse Syntax

```markdown
### Column: state_code
**ReuseComponent**: @ProjectName:ComponentLabel
**Description**: [Description in source language]
```

**Format:** `@ProjectName:ComponentLabel`
- `ProjectName`: Name of project containing the component (e.g., NIEM, FHIR, HL7v3)
- `ComponentLabel`: Exact label of the published component

**Examples:**

NIEM state code:
```markdown
### Column: state
**ReuseComponent**: @NIEM:StateUSPostalServiceCode
**Description**: US state postal abbreviation
**Examples**: CA, NY, TX
```

FHIR patient demographics:
```markdown
## Cluster: Patient Information
**ReuseComponent**: @FHIR:Patient
**Description**: Standard patient demographics
```

Custom organizational component:
```markdown
### Column: department_code
**ReuseComponent**: @OrgStandards:DepartmentCode
**Description**: Internal department identifier
**Examples**: HR, IT, FIN
```

### Cluster-Level Reuse

You can also reuse entire clusters:

```markdown
## Cluster: Mailing Address
**ReuseComponent**: @NIEM:USAddress
**Description**: Standard US postal address
```

This inherits all columns from the NIEM USAddress cluster (street, city, state, zip, etc.)

---

## PART 11: Complete Example Templates

### Example 1: Healthcare Patient Registration (English)

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Patient Registration"
  description: "Patient demographic and registration information"
  domain: "Healthcare"
  creator: "Clinical Systems Team"
enrichment:
  enable_llm: true
---

# Dataset Overview

Patient registration data collected at intake for all clinical encounters.

**Purpose**: Capture essential patient demographics and contact information for clinical care

**Business Context**:
- Primary use: Patient identification and contact
- Secondary use: Demographic reporting and compliance
- Stakeholders: Registration staff, Clinical staff, Billing department

## Root Cluster: Patient Demographics

Patient identification and demographic information.

**Purpose**: Unique patient identification and essential demographics
**Business Context**: Required for all clinical encounters and billing

### Column: patient_id
**Type**: identifier
**Description**: Unique patient identifier assigned at registration
**Constraints**:
  - required: true
  - unique: true
**Examples**: PAT-12345, PAT-98765

### Column: first_name
**Type**: text
**Description**: Patient's legal first name
**Constraints**:
  - required: true
**Examples**: John, Mary, Wei

### Column: last_name
**Type**: text
**Description**: Patient's legal last name
**Constraints**:
  - required: true
**Examples**: Smith, Johnson, Chen

### Column: date_of_birth
**Type**: date
**Description**: Patient's date of birth
**Constraints**:
  - required: true
  - format: "YYYY-MM-DD"
**Business Rules**: Used to calculate age; must be past date
**Examples**: 1985-03-15, 1970-12-01

### Column: gender
**Type**: text
**Description**: Patient's gender identity
**Enumeration**:
  - male: Male
  - female: Female
  - other: Other
  - unknown: Unknown or not disclosed
**Examples**: male, female

### Column: email
**Type**: email
**Description**: Primary contact email address
**Constraints**:
  - format: "valid email"
**Examples**: john.smith@example.com, patient@email.org

### Column: phone
**Type**: text
**Description**: Primary contact phone number
**Constraints**:
  - format: "valid phone number with area code"
**Examples**: (555) 123-4567, 555-987-6543

## Cluster: Insurance Information

Health insurance coverage details.

**Purpose**: Track patient insurance for billing purposes

### Column: insurance_provider
**Type**: text
**Description**: Name of insurance company
**Examples**: Blue Cross Blue Shield, Aetna, UnitedHealthcare

### Column: policy_number
**Type**: identifier
**Description**: Insurance policy or member ID number
**Constraints**:
  - required: true
**Examples**: ABC12345678, XYZ-987-654-321

### Column: group_number
**Type**: identifier
**Description**: Insurance group number from employer
**Examples**: GRP-1234, 999-88-777
```

### Example 2: French Government Form

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Demande de Permis de Construire"
  description: "Formulaire de demande de permis de construire pour travaux"
  domain: "Government"
  creator: "Service d'Urbanisme"
enrichment:
  enable_llm: true
---

# Dataset Overview

Formulaire de demande de permis de construire pour tous travaux de construction ou d'agrandissement.

**Purpose**: Collecter les informations nécessaires pour l'examen des demandes de permis de construire

**Business Context**:
- Primary use: Instruction des demandes de permis
- Secondary use: Archivage et statistiques
- Stakeholders: Service d'urbanisme, Commission d'urbanisme, Demandeurs

## Root Cluster: Informations Demandeur

Informations sur le demandeur du permis.

**Purpose**: Identification et coordonnées du demandeur
**Business Context**: Requis pour toute correspondance officielle

### Column: numero_dossier
**Type**: identifier
**Description**: Numéro unique de dossier attribué à la demande
**Constraints**:
  - required: true
  - unique: true
**Examples**: PC-2024-001, PC-2024-002

### Column: nom
**Type**: text
**Description**: Nom de famille du demandeur (ou raison sociale si entreprise)
**Constraints**:
  - required: true
**Examples**: Dupont, Martin, SARL Construction

### Column: prenom
**Type**: text
**Description**: Prénom du demandeur (si personne physique)
**Examples**: Jean, Marie, Pierre

### Column: adresse
**Type**: text
**Description**: Adresse postale complète du demandeur
**Constraints**:
  - required: true
**Examples**: 15 rue de la République, 45 Avenue des Champs

### Column: code_postal
**Type**: text
**Description**: Code postal
**Constraints**:
  - required: true
  - format: "5 chiffres"
**Examples**: 75001, 69002, 13001

### Column: ville
**Type**: text
**Description**: Ville de résidence
**Constraints**:
  - required: true
**Examples**: Paris, Lyon, Marseille

### Column: telephone
**Type**: text
**Description**: Numéro de téléphone de contact
**Constraints**:
  - format: "10 chiffres"
**Examples**: 0601020304, 0412345678

### Column: email
**Type**: email
**Description**: Adresse email de contact
**Constraints**:
  - format: "email valide"
**Examples**: jean.dupont@exemple.fr, contact@entreprise.fr

## Cluster: Informations Terrain

Informations sur le terrain concerné par la demande.

**Purpose**: Localisation et caractéristiques du terrain

### Column: adresse_terrain
**Type**: text
**Description**: Adresse du terrain où seront réalisés les travaux
**Constraints**:
  - required: true
**Examples**: 28 rue du Château, Parcelle ZA 123

### Column: reference_cadastrale
**Type**: identifier
**Description**: Référence cadastrale de la parcelle
**Constraints**:
  - required: true
**Examples**: AB 123, ZC 456

### Column: surface_terrain
**Type**: decimal
**Description**: Surface totale du terrain
**Units**: m²
**Constraints**:
  - required: true
  - range: [0, null]
**Examples**: 500.00, 1200.50, 2500.00

### Column: zone_urbanisme
**Type**: text
**Description**: Zone du Plan Local d'Urbanisme (PLU)
**Enumeration**:
  - UA: Zone urbaine dense
  - UB: Zone urbaine mixte
  - UC: Zone urbaine pavillonnaire
  - AU: Zone à urbaniser
  - A: Zone agricole
  - N: Zone naturelle
**Examples**: UA, UB, N

### Column: surface_construction
**Type**: decimal
**Description**: Surface de plancher de la construction projetée
**Units**: m²
**Constraints**:
  - required: true
  - range: [0, null]
**Business Rules**: Doit respecter le coefficient d'occupation des sols (COS) de la zone
**Examples**: 150.00, 200.50, 350.00

### Column: hauteur_construction
**Type**: decimal
**Description**: Hauteur totale de la construction projetée
**Units**: mètres
**Constraints**:
  - required: true
  - range: [0, null]
**Business Rules**: Doit respecter les règles du PLU pour la zone
**Examples**: 7.50, 12.00, 15.50
```

### Example 3: Brazilian Healthcare Patient Registration (pt-BR)

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Cadastro de Paciente SUS"
  description: "Formulário de cadastro de paciente para atendimento no Sistema Único de Saúde"
  domain: "Healthcare"
  creator: "Secretaria Municipal de Saúde"
enrichment:
  enable_llm: true
---

# Dataset Overview

Dados cadastrais de pacientes para atendimento no SUS, incluindo informações demográficas, contato e documentação.

**Purpose**: Registrar pacientes para atendimento na rede pública de saúde

**Business Context**:
- Primary use: Identificação e prontuário eletrônico de pacientes
- Secondary use: Estatísticas epidemiológicas e planejamento de saúde pública
- Stakeholders: Profissionais de saúde, Gestores de UBS, Secretaria de Saúde

## Root Cluster: Dados Pessoais

Informações de identificação e dados demográficos do paciente.

**Purpose**: Identificação única e dados básicos do paciente
**Business Context**: Obrigatório para todos os atendimentos no SUS

### Column: numero_cartao_sus
**Type**: identifier
**Description**: Número do Cartão Nacional de Saúde (CNS)
**Constraints**:
  - required: true
  - unique: true
  - format: "15 dígitos"
**Business Rules**: Validar dígito verificador conforme algoritmo do CNS
**Examples**: 123456789012345, 987654321098765

### Column: cpf
**Type**: identifier
**Description**: Cadastro de Pessoa Física
**Constraints**:
  - required: true
  - unique: true
  - format: "11 dígitos, pode conter pontos e traço"
**Business Rules**: Validar dígito verificador do CPF
**Examples**: 123.456.789-00, 987.654.321-11

### Column: nome_completo
**Type**: text
**Description**: Nome completo do paciente conforme documento de identidade
**Constraints**:
  - required: true
**Examples**: Maria da Silva Santos, João Pedro Oliveira, Ana Carolina Ferreira

### Column: nome_social
**Type**: text
**Description**: Nome social do paciente (opcional)
**Business Rules**: Deve ser utilizado em todos os atendimentos e documentos quando informado
**Examples**: João Silva, Maria Santos

### Column: data_nascimento
**Type**: date
**Description**: Data de nascimento do paciente
**Constraints**:
  - required: true
  - format: "DD/MM/AAAA"
**Business Rules**: Deve ser data passada; usado para calcular idade
**Examples**: 15/03/1985, 22/08/1992, 10/12/2010

### Column: sexo
**Type**: text
**Description**: Sexo biológico registrado no documento
**Enumeration**:
  - M: Masculino
  - F: Feminino
**Constraints**:
  - required: true
**Examples**: M, F

### Column: identidade_genero
**Type**: text
**Description**: Identidade de gênero autodeclarada
**Enumeration**:
  - homem_cisgenero: Homem cisgênero
  - mulher_cisgenero: Mulher cisgênero
  - homem_transgenero: Homem transgênero
  - mulher_transgenero: Mulher transgênero
  - nao_binario: Não-binário
  - outro: Outro
  - nao_informado: Não deseja informar
**Examples**: homem_cisgenero, mulher_transgenero

### Column: raca_cor
**Type**: text
**Description**: Raça/cor autodeclarada conforme IBGE
**Enumeration**:
  - branca: Branca
  - preta: Preta
  - parda: Parda
  - amarela: Amarela
  - indigena: Indígena
**Business Rules**: Coleta conforme classificação do IBGE para estatísticas de saúde
**Examples**: parda, branca

### Column: nome_mae
**Type**: text
**Description**: Nome completo da mãe do paciente
**Constraints**:
  - required: true
**Business Rules**: Campo obrigatório para identificação em casos de homônimos
**Examples**: Maria José da Silva, Ana Paula Santos

### Column: nome_pai
**Type**: text
**Description**: Nome completo do pai do paciente (opcional)
**Examples**: José da Silva, Paulo Santos

## Cluster: Endereço

Informações de endereço residencial do paciente.

**Purpose**: Localização para contato e área de abrangência da UBS

### Column: cep
**Type**: text
**Description**: Código de Endereçamento Postal
**Constraints**:
  - required: true
  - format: "8 dígitos, pode conter hífen"
**Examples**: 01310-100, 20040-020, 30130-100

### Column: logradouro
**Type**: text
**Description**: Nome da rua, avenida, travessa, etc.
**Constraints**:
  - required: true
**Examples**: Rua das Flores, Avenida Paulista, Travessa do Comércio

### Column: numero
**Type**: text
**Description**: Número do imóvel
**Constraints**:
  - required: true
**Examples**: 123, 45, S/N

### Column: complemento
**Type**: text
**Description**: Complemento do endereço (apartamento, bloco, etc.)
**Examples**: Apto 101, Bloco B, Casa 2

### Column: bairro
**Type**: text
**Description**: Bairro ou distrito
**Constraints**:
  - required: true
**Examples**: Centro, Copacabana, Vila Mariana

### Column: municipio
**Type**: text
**Description**: Nome do município
**Constraints**:
  - required: true
**Examples**: São Paulo, Rio de Janeiro, Belo Horizonte

### Column: uf
**Type**: text
**Description**: Unidade Federativa (Estado)
**Enumeration**:
  - AC: Acre
  - AL: Alagoas
  - AP: Amapá
  - AM: Amazonas
  - BA: Bahia
  - CE: Ceará
  - DF: Distrito Federal
  - ES: Espírito Santo
  - GO: Goiás
  - MA: Maranhão
  - MT: Mato Grosso
  - MS: Mato Grosso do Sul
  - MG: Minas Gerais
  - PA: Pará
  - PB: Paraíba
  - PR: Paraná
  - PE: Pernambuco
  - PI: Piauí
  - RJ: Rio de Janeiro
  - RN: Rio Grande do Norte
  - RS: Rio Grande do Sul
  - RO: Rondônia
  - RR: Roraima
  - SC: Santa Catarina
  - SP: São Paulo
  - SE: Sergipe
  - TO: Tocantins
**Constraints**:
  - required: true
**Examples**: SP, RJ, MG

## Cluster: Contato

Informações de contato do paciente.

**Purpose**: Comunicação e agendamento de consultas

### Column: telefone_celular
**Type**: text
**Description**: Número de telefone celular com DDD
**Constraints**:
  - format: "DDD + 9 dígitos"
**Examples**: (11) 98765-4321, (21) 99876-5432

### Column: telefone_fixo
**Type**: text
**Description**: Número de telefone fixo com DDD
**Constraints**:
  - format: "DDD + 8 dígitos"
**Examples**: (11) 3456-7890, (21) 2345-6789

### Column: email
**Type**: email
**Description**: Endereço de e-mail para contato
**Constraints**:
  - format: "e-mail válido"
**Examples**: maria.silva@email.com.br, joao.santos@gmail.com

### Column: whatsapp
**Type**: boolean
**Description**: Se o telefone celular possui WhatsApp
**Business Rules**: Usado para envio de lembretes de consulta
**Examples**: true, false

## Cluster: Informações Clínicas

Dados clínicos básicos do paciente.

**Purpose**: Informações essenciais para atendimento

### Column: tipo_sanguineo
**Type**: text
**Description**: Tipo sanguíneo e fator Rh
**Enumeration**:
  - A+: A positivo
  - A-: A negativo
  - B+: B positivo
  - B-: B negativo
  - AB+: AB positivo
  - AB-: AB negativo
  - O+: O positivo
  - O-: O negativo
  - desconhecido: Desconhecido
**Examples**: O+, A+, AB-

### Column: alergias
**Type**: text
**Description**: Lista de alergias conhecidas (medicamentos, alimentos, outros)
**Business Rules**: Informação crítica - deve ser destacada em todos os atendimentos
**Examples**: Dipirona, Penicilina, Nenhuma alergia conhecida

### Column: doencas_cronicas
**Type**: text
**Description**: Doenças crônicas diagnosticadas
**Examples**: Diabetes tipo 2, Hipertensão arterial, Asma

### Column: medicamentos_uso_continuo
**Type**: text
**Description**: Medicamentos em uso contínuo
**Examples**: Losartana 50mg, Metformina 850mg, Nenhum
```

### Example 4: Brazilian Government CPF Application (pt-BR)

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Solicitação de CPF"
  description: "Formulário para inscrição ou regularização do Cadastro de Pessoas Físicas"
  domain: "Government"
  creator: "Receita Federal do Brasil"
enrichment:
  enable_llm: true
---

# Dataset Overview

Dados necessários para inscrição ou regularização do CPF (Cadastro de Pessoas Físicas) junto à Receita Federal.

**Purpose**: Cadastrar ou atualizar informações de pessoas físicas no CPF

**Business Context**:
- Primary use: Emissão de CPF para brasileiros e estrangeiros residentes
- Secondary use: Atualização cadastral e regularização
- Stakeholders: Receita Federal, Bancos, Cidadãos, Empresas

## Root Cluster: Dados do Requerente

Informações pessoais do solicitante do CPF.

**Purpose**: Identificação completa do requerente
**Business Context**: Base para emissão do CPF e validação de identidade

### Column: protocolo
**Type**: identifier
**Description**: Número de protocolo da solicitação
**Constraints**:
  - required: true
  - unique: true
  - format: "12 dígitos"
**Examples**: 202411050001, 202411050002

### Column: tipo_solicitacao
**Type**: text
**Description**: Tipo de solicitação de CPF
**Enumeration**:
  - primeira_via: Primeira via - nunca teve CPF
  - segunda_via: Segunda via - perda ou extravio
  - regularizacao: Regularização - CPF cancelado ou suspenso
  - alteracao_cadastral: Alteração cadastral - mudança de dados
**Constraints**:
  - required: true
**Examples**: primeira_via, alteracao_cadastral

### Column: nome_completo
**Type**: text
**Description**: Nome completo conforme documento de identidade (sem abreviações)
**Constraints**:
  - required: true
**Business Rules**: Deve corresponder exatamente ao nome no documento de identificação
**Examples**: José Carlos da Silva Filho, Maria Aparecida Santos

### Column: data_nascimento
**Type**: date
**Description**: Data de nascimento
**Constraints**:
  - required: true
  - format: "DD/MM/AAAA"
**Business Rules**: Deve ser data passada
**Examples**: 15/03/1985, 22/08/1970

### Column: sexo
**Type**: text
**Description**: Sexo conforme documento de identidade
**Enumeration**:
  - M: Masculino
  - F: Feminino
**Constraints**:
  - required: true
**Examples**: M, F

### Column: nome_mae
**Type**: text
**Description**: Nome completo da mãe (sem abreviações)
**Constraints**:
  - required: true
**Business Rules**: Campo obrigatório conforme Lei 9.454/1997
**Examples**: Maria José da Silva, Ana Paula Santos

### Column: nome_pai
**Type**: text
**Description**: Nome completo do pai (sem abreviações)
**Business Rules**: Campo opcional conforme Lei 9.454/1997
**Examples**: João da Silva, Paulo Roberto Santos

### Column: naturalidade_municipio
**Type**: text
**Description**: Município de nascimento
**Constraints**:
  - required: true
**Examples**: São Paulo, Rio de Janeiro, Salvador

### Column: naturalidade_uf
**Type**: text
**Description**: Estado de nascimento
**ReuseComponent**: @Brasil:UnidadeFederativa
**Constraints**:
  - required: true
**Examples**: SP, RJ, BA

### Column: nacionalidade
**Type**: text
**Description**: Nacionalidade do requerente
**Enumeration**:
  - brasileira: Brasileira
  - naturalizado_brasileiro: Naturalizado brasileiro
  - estrangeira: Estrangeira
**Constraints**:
  - required: true
**Examples**: brasileira, estrangeira

### Column: pais_nascimento
**Type**: text
**Description**: País de nascimento (se estrangeiro)
**Examples**: Brasil, Portugal, Argentina

## Cluster: Documentação

Documentos de identificação do requerente.

**Purpose**: Validação de identidade

### Column: tipo_documento
**Type**: text
**Description**: Tipo de documento de identificação apresentado
**Enumeration**:
  - rg: Registro Geral (RG)
  - cnh: Carteira Nacional de Habilitação
  - ctps: Carteira de Trabalho
  - passaporte: Passaporte
  - rne: Registro Nacional de Estrangeiro
  - crnm: Carteira de Registro Nacional Migratório
**Constraints**:
  - required: true
**Examples**: rg, cnh

### Column: numero_documento
**Type**: identifier
**Description**: Número do documento de identificação
**Constraints**:
  - required: true
**Examples**: 12.345.678-9, AB123456

### Column: orgao_emissor
**Type**: text
**Description**: Órgão emissor do documento
**Constraints**:
  - required: true
**Examples**: SSP, DETRAN, IFP

### Column: uf_emissao
**Type**: text
**Description**: UF do órgão emissor
**ReuseComponent**: @Brasil:UnidadeFederativa
**Constraints**:
  - required: true
**Examples**: SP, RJ, MG

### Column: data_emissao
**Type**: date
**Description**: Data de emissão do documento
**Constraints**:
  - required: true
  - format: "DD/MM/AAAA"
**Business Rules**: Deve ser data passada e posterior à data de nascimento
**Examples**: 10/05/2015, 22/03/2020

### Column: titulo_eleitor
**Type**: identifier
**Description**: Número do título de eleitor (se brasileiro maior de 16 anos)
**Constraints**:
  - format: "12 dígitos"
**Examples**: 123456789012, 987654321098

## Cluster: Endereço Residencial

Endereço residencial do requerente.

**Purpose**: Localização para correspondência da Receita Federal

### Column: cep
**Type**: text
**Description**: Código de Endereçamento Postal
**Constraints**:
  - required: true
  - format: "8 dígitos"
**Examples**: 01310100, 20040020

### Column: tipo_logradouro
**Type**: text
**Description**: Tipo do logradouro
**Enumeration**:
  - rua: Rua
  - avenida: Avenida
  - travessa: Travessa
  - alameda: Alameda
  - praca: Praça
  - rodovia: Rodovia
  - estrada: Estrada
**Constraints**:
  - required: true
**Examples**: rua, avenida

### Column: logradouro
**Type**: text
**Description**: Nome do logradouro (sem o tipo)
**Constraints**:
  - required: true
**Examples**: das Flores, Paulista, do Comércio

### Column: numero
**Type**: text
**Description**: Número do imóvel
**Constraints**:
  - required: true
**Examples**: 123, 1000, S/N

### Column: complemento
**Type**: text
**Description**: Complemento do endereço
**Examples**: Apto 101, Bloco B, Casa 2, Sala 305

### Column: bairro
**Type**: text
**Description**: Bairro ou distrito
**Constraints**:
  - required: true
**Examples**: Centro, Jardim Paulista, Copacabana

### Column: municipio
**Type**: text
**Description**: Nome do município
**Constraints**:
  - required: true
**Examples**: São Paulo, Rio de Janeiro, Brasília

### Column: uf
**Type**: text
**Description**: Unidade Federativa
**ReuseComponent**: @Brasil:UnidadeFederativa
**Constraints**:
  - required: true
**Examples**: SP, RJ, DF

## Cluster: Contato

Informações de contato para comunicação oficial.

**Purpose**: Canal de comunicação com a Receita Federal

### Column: ddd
**Type**: text
**Description**: Código de Discagem Direta a Distância
**Constraints**:
  - required: true
  - format: "2 dígitos"
**Examples**: 11, 21, 47

### Column: telefone
**Type**: text
**Description**: Número do telefone (fixo ou celular)
**Constraints**:
  - required: true
  - format: "8 ou 9 dígitos"
**Examples**: 98765-4321, 3456-7890

### Column: email
**Type**: email
**Description**: Endereço de e-mail para comunicações oficiais
**Constraints**:
  - format: "e-mail válido"
**Business Rules**: E-mail será usado para notificações da Receita Federal
**Examples**: jose.silva@email.com.br, maria@empresa.com.br
```

### Example 5: Brazilian E-commerce Customer Registration (pt-BR)

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Cadastro de Cliente E-commerce"
  description: "Formulário de cadastro de clientes para loja virtual"
  domain: "Retail"
  creator: "Equipe de Tecnologia"
enrichment:
  enable_llm: true
---

# Dataset Overview

Dados cadastrais de clientes para compras online, incluindo informações pessoais, endereço de entrega e preferências.

**Purpose**: Registrar clientes e facilitar processo de compra online

**Business Context**:
- Primary use: Gestão de clientes e processamento de pedidos
- Secondary use: Marketing digital e programa de fidelidade
- Stakeholders: Equipe comercial, Marketing, Logística

## Root Cluster: Dados do Cliente

Informações básicas de identificação do cliente.

**Purpose**: Identificação única e contato com cliente
**Business Context**: Base para todo relacionamento comercial

### Column: id_cliente
**Type**: identifier
**Description**: Identificador único do cliente no sistema
**Constraints**:
  - required: true
  - unique: true
  - format: "UUID"
**Examples**: 550e8400-e29b-41d4-a716-446655440000, 6ba7b810-9dad-11d1-80b4-00c04fd430c8

### Column: nome_completo
**Type**: text
**Description**: Nome completo do cliente
**Constraints**:
  - required: true
**Examples**: Carlos Eduardo Silva, Fernanda Oliveira Santos

### Column: cpf
**Type**: identifier
**Description**: CPF do cliente (opcional para pessoa física)
**Constraints**:
  - format: "11 dígitos"
  - unique: true
**Business Rules**: Obrigatório para emissão de nota fiscal; validar dígito verificador
**Examples**: 123.456.789-00, 987.654.321-11

### Column: cnpj
**Type**: identifier
**Description**: CNPJ para compras empresariais
**Constraints**:
  - format: "14 dígitos"
  - unique: true
**Business Rules**: Usado para compras de pessoa jurídica; validar dígito verificador
**Examples**: 12.345.678/0001-90, 98.765.432/0001-10

### Column: tipo_pessoa
**Type**: text
**Description**: Tipo de cadastro (pessoa física ou jurídica)
**Enumeration**:
  - fisica: Pessoa Física
  - juridica: Pessoa Jurídica
**Constraints**:
  - required: true
**Examples**: fisica, juridica

### Column: data_nascimento
**Type**: date
**Description**: Data de nascimento (pessoa física)
**Constraints**:
  - format: "DD/MM/AAAA"
**Business Rules**: Usado para validar maioridade e campanhas de aniversário
**Examples**: 15/08/1988, 22/03/1995

### Column: genero
**Type**: text
**Description**: Gênero do cliente (opcional)
**Enumeration**:
  - masculino: Masculino
  - feminino: Feminino
  - outro: Outro
  - nao_informar: Prefiro não informar
**Business Rules**: Usado para personalização de campanhas
**Examples**: feminino, masculino

### Column: email
**Type**: email
**Description**: E-mail principal para login e comunicações
**Constraints**:
  - required: true
  - unique: true
  - format: "e-mail válido"
**Business Rules**: Usado como login principal; deve ser verificado
**Examples**: carlos.silva@email.com.br, fernanda@empresa.com

### Column: email_verificado
**Type**: boolean
**Description**: Indica se o e-mail foi verificado
**Constraints**:
  - required: true
**Business Rules**: Cliente deve verificar e-mail antes de primeira compra
**Examples**: true, false

### Column: telefone_celular
**Type**: text
**Description**: Telefone celular com DDD
**Constraints**:
  - required: true
  - format: "(DD) 9XXXX-XXXX"
**Business Rules**: Usado para comunicação sobre pedidos e entregas
**Examples**: (11) 98765-4321, (21) 99876-5432

### Column: data_cadastro
**Type**: datetime
**Description**: Data e hora do cadastro no sistema
**Constraints**:
  - required: true
**Examples**: 2024-11-05T14:30:00, 2024-10-15T09:15:00

### Column: status_cadastro
**Type**: text
**Description**: Status atual do cadastro
**Enumeration**:
  - ativo: Cadastro ativo e em uso
  - inativo: Cadastro inativo (sem compras há 12+ meses)
  - bloqueado: Bloqueado por fraude ou inadimplência
  - pendente: Pendente de verificação
**Constraints**:
  - required: true
**Examples**: ativo, pendente

## Cluster: Endereço de Entrega Principal

Endereço principal para entrega de produtos.

**Purpose**: Local de entrega padrão para pedidos

### Column: nome_destinatario
**Type**: text
**Description**: Nome do destinatário para a entrega
**Constraints**:
  - required: true
**Business Rules**: Pode ser diferente do nome do cliente
**Examples**: Carlos Eduardo Silva, Maria Santos (trabalho)

### Column: cep
**Type**: text
**Description**: CEP do endereço de entrega
**Constraints**:
  - required: true
  - format: "8 dígitos"
**Business Rules**: Usado para cálculo de frete
**Examples**: 01310-100, 20040-020

### Column: logradouro
**Type**: text
**Description**: Nome da rua/avenida
**Constraints**:
  - required: true
**Examples**: Rua Augusta, Avenida Paulista

### Column: numero
**Type**: text
**Description**: Número do endereço
**Constraints**:
  - required: true
**Examples**: 1000, 234, S/N

### Column: complemento
**Type**: text
**Description**: Complemento do endereço (apartamento, bloco, etc.)
**Business Rules**: Importante para entregas em condomínios
**Examples**: Apto 101 Bloco B, Casa 2, Torre 3

### Column: ponto_referencia
**Type**: text
**Description**: Ponto de referência para facilitar localização
**Examples**: Próximo ao metrô, Em frente à padaria, Ao lado do posto

### Column: bairro
**Type**: text
**Description**: Bairro do endereço
**Constraints**:
  - required: true
**Examples**: Consolação, Copacabana, Savassi

### Column: cidade
**Type**: text
**Description**: Cidade do endereço de entrega
**Constraints**:
  - required: true
**Examples**: São Paulo, Rio de Janeiro, Belo Horizonte

### Column: uf
**Type**: text
**Description**: Estado do endereço de entrega
**ReuseComponent**: @Brasil:UnidadeFederativa
**Constraints**:
  - required: true
**Examples**: SP, RJ, MG

## Cluster: Preferências de Compra

Preferências e histórico de compras do cliente.

**Purpose**: Personalização e segmentação de marketing

### Column: categorias_interesse
**Type**: text
**Description**: Categorias de produtos de interesse do cliente
**Enumeration**:
  - eletronicos: Eletrônicos e Informática
  - moda: Moda e Vestuário
  - casa: Casa e Decoração
  - esportes: Esportes e Lazer
  - livros: Livros e Cultura
  - beleza: Beleza e Perfumaria
  - infantil: Infantil e Bebês
  - alimentos: Alimentos e Bebidas
**Business Rules**: Usado para recomendações personalizadas
**Examples**: eletronicos, moda

### Column: aceita_newsletter
**Type**: boolean
**Description**: Aceita receber newsletter com ofertas e novidades
**Constraints**:
  - required: true
**Business Rules**: Conforme LGPD, necessita consentimento explícito
**Examples**: true, false

### Column: aceita_sms
**Type**: boolean
**Description**: Aceita receber SMS com informações de pedidos e ofertas
**Constraints**:
  - required: true
**Business Rules**: Conforme LGPD, necessita consentimento explícito
**Examples**: true, false

### Column: aceita_whatsapp
**Type**: boolean
**Description**: Aceita receber mensagens via WhatsApp
**Constraints**:
  - required: true
**Business Rules**: Conforme LGPD, necessita consentimento explícito
**Examples**: true, false

### Column: valor_total_compras
**Type**: decimal
**Description**: Valor total acumulado de todas as compras
**Units**: BRL
**Constraints**:
  - range: [0, null]
  - precision: 2
**Relationships**: Soma de todos os pedidos finalizados
**Business Rules**: Atualizado após confirmação de pagamento
**Examples**: 1250.50, 5432.10, 15000.00

### Column: numero_pedidos
**Type**: integer
**Description**: Quantidade total de pedidos realizados
**Units**: pedidos
**Constraints**:
  - range: [0, null]
**Relationships**: Contagem de todos os pedidos finalizados
**Examples**: 5, 12, 48

### Column: ticket_medio
**Type**: decimal
**Description**: Valor médio por pedido
**Units**: BRL
**Constraints**:
  - range: [0, null]
  - precision: 2
**Relationships**: valor_total_compras / numero_pedidos
**Business Rules**: Calculado automaticamente; atualizado após cada compra
**Examples**: 250.10, 452.67, 312.50

### Column: ultima_compra
**Type**: date
**Description**: Data da última compra realizada
**Constraints**:
  - format: "DD/MM/AAAA"
**Business Rules**: Usado para identificar clientes inativos
**Examples**: 15/10/2024, 22/09/2024

### Column: nivel_fidelidade
**Type**: text
**Description**: Nível no programa de fidelidade
**Enumeration**:
  - bronze: Bronze (0-999 pontos)
  - prata: Prata (1000-4999 pontos)
  - ouro: Ouro (5000-9999 pontos)
  - diamante: Diamante (10000+ pontos)
**Business Rules**: Calculado com base em pontos acumulados; oferece descontos progressivos
**Examples**: bronze, prata, ouro
```

### Example 6: Civil Registry with Subject/Provider/Participation

This example demonstrates the SDC4 participation model — separating **who** (Subject, Provider, Participation) from **what** (Root Cluster data).

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Civil Registry Birth Record"
  description: "Registration of births in the civil registry"
  domain: "Government"
  creator: "Registry Administration"
enrichment:
  enable_llm: true
---

# Dataset Overview

Official birth registration data maintained by the civil registry office.

**Purpose**: Record and manage birth registrations for legal identity

**Business Context**:
- Primary use: Legal identity establishment and vital statistics
- Secondary use: Demographic analysis and census support
- Stakeholders: Registry offices, Ministry of Interior, Citizens

## Subject: Registered Person
**Description**: The individual whose birth is being registered

### Column: national_id
**Type**: identifier
**Description**: Unique national citizen identifier
**Constraints**:
  - required: true
  - unique: true
**Examples**: CID-2024-001234, CID-2024-005678

### Column: given_name
**Type**: text
**Description**: Given name of the registered person
**Constraints**:
  - required: true
**Examples**: María, Carlos, Ana

### Column: family_name
**Type**: text
**Description**: Family name (surname) of the registered person
**Constraints**:
  - required: true
**Examples**: García, López, Martínez

### Column: date_of_birth
**Type**: date
**Description**: Date of birth
**Constraints**:
  - required: true
  - format: "YYYY-MM-DD"
**Examples**: 2024-03-15, 2024-07-22

### Column: sex
**Type**: text
**Description**: Biological sex as recorded at birth
**Enumeration**:
  - male: Male
  - female: Female
  - indeterminate: Indeterminate
**Constraints**:
  - required: true
**Examples**: male, female

## Provider: Registry Office
**Description**: The government office that maintains this birth record

### Column: office_name
**Type**: text
**Description**: Official name of the civil registry office
**Constraints**:
  - required: true
**Examples**: Central Registry Office, District 5 Registry

### Column: office_code
**Type**: identifier
**Description**: Unique identifier for the registry office
**Constraints**:
  - required: true
**Examples**: REG-001, REG-042

### Column: jurisdiction
**Type**: text
**Description**: Geographic jurisdiction of the registry office
**Examples**: Central District, Northern Province

## Participation: Registrar
**Description**: The civil officer who processed and recorded the birth registration
**Function**: Civil Registrar
**Function Description**: Officer authorized by law to record civil events
**Mode**: In Person

### Column: officer_id
**Type**: identifier
**Description**: Employee identifier of the registrar
**Constraints**:
  - required: true
**Examples**: OFF-1234, OFF-5678

### Column: officer_name
**Type**: text
**Description**: Full name of the registrar
**Constraints**:
  - required: true
**Examples**: Elena Rodríguez, Miguel Fernández

## Participation: Declarant
**Description**: The person who declared the birth to the registry office
**Function**: Birth Declarant
**Function Description**: Parent or authorized person declaring the birth
**Mode**: In Person

### Column: declarant_name
**Type**: text
**Description**: Full name of the person declaring the birth
**Constraints**:
  - required: true
**Examples**: José García López, Carmen Martínez Ruiz

### Column: relationship
**Type**: text
**Description**: Relationship of declarant to the registered person
**Enumeration**:
  - mother: Mother
  - father: Father
  - legal_guardian: Legal Guardian
  - authorized_representative: Authorized Representative
**Constraints**:
  - required: true
**Examples**: mother, father

## Root Cluster: Birth Record Data

Core birth registration data and administrative details.

**Purpose**: Official record of the birth event
**Business Context**: Legal document for vital statistics and identity

### Column: registration_number
**Type**: identifier
**Description**: Unique registration number for this birth record
**Constraints**:
  - required: true
  - unique: true
**Examples**: BR-2024-001234, BR-2024-005678

### Column: registration_date
**Type**: date
**Description**: Date the birth was officially registered
**Constraints**:
  - required: true
  - format: "YYYY-MM-DD"
**Business Rules**: Must be on or after the date of birth
**Examples**: 2024-03-20, 2024-08-01

### Column: place_of_birth
**Type**: text
**Description**: Location where the birth occurred
**Constraints**:
  - required: true
**Examples**: City General Hospital, Home - 123 Oak Street

### Column: birth_type
**Type**: text
**Description**: Type of birth (single or multiple)
**Enumeration**:
  - single: Single birth
  - twin: Twin birth
  - triplet: Triplet birth
  - other_multiple: Other multiple birth
**Examples**: single, twin
```

**This produces a DM with:**
- `subject` → Party "Registered Person" with details Cluster (5 demographic components)
- `provider` → Party "Registry Office" with details Cluster (3 components)
- `participations` → [Participation "Registrar", Participation "Declarant"] each with performer details
- `data` → Cluster "Birth Record Data" (4 components for the registration event itself)

---

## PART 12: LLM Generation Guidelines

### Step-by-Step Process

When a user provides a form or form description, follow these steps:

**1. Analyze the Form**
- Identify all fields, sections, and groupings
- Determine the language of the form
- Note any hierarchical structure
- Identify field types (text, number, date, checkbox, etc.)
- Look for enumerated values (dropdowns, radio buttons, checkboxes)
- **Identify participants**: Is there a clear subject (patient, applicant, citizen)? A provider (hospital, agency)? Other participants (registrar, physician)?

**2. Create YAML Front Matter**
- Generate an appropriate dataset name (in source language if not English)
- Write a clear description
- Identify the domain/industry
- Set `template_version` to `"4.0.0"`
- Decide on enrichment (default to `true` unless user specifies otherwise)

**3. Write Dataset Overview**
- Explain the purpose in 2-4 sentences
- Identify stakeholders and use cases
- Use source language for all text

**4. Identify Subject/Provider/Participation (if applicable)**
- If the form has a clear "about whom" (patient, applicant, citizen) → create `## Subject:` section
- If the form identifies who maintains the data (hospital, agency, office) → create `## Provider:` section
- If the form identifies other participants (registrar, physician, inspector) → create `## Participation:` sections
- Place demographic/identity fields (names, IDs, birth dates) under the appropriate party section, NOT the Root Cluster
- Skip this step if the form is purely data-focused with no clear actors

**5. Create Root Cluster**
- Name it appropriately based on the form's main content (the data payload, not the participants)
- Provide purpose and business context
- Use source language for names and descriptions

**6. Convert Each Form Field to a Column**
- Use field label as column name (convert to lowercase_with_underscores)
- Map field type to appropriate SDC4 type
- Write detailed description in source language
- Add constraints (required, format, range)
- Include enumeration if field has fixed options
- Provide realistic examples in source language

**7. Organize with Multiple Clusters**
- Group related fields into separate clusters
- Use form sections as guidance
- Create hierarchical structure if form has multiple levels

**8. Review and Validate**
- Ensure all REQUIRED keywords are present (Type, Description, Examples)
- Verify all keywords are in English
- Check that content is in source language
- Confirm enumeration syntax is correct
- Validate constraint syntax

### Common Patterns to Recognize

**Personal Information:**
- Names → `text` type
- Emails → `email` type
- Phone numbers → `text` type with format constraint
- IDs/Numbers → `identifier` type
- Birth dates → `date` type
- Age → `integer` type with `years` units

**Address Information:**
- Consider using `@NIEM:USAddress` for US addresses
- Street → `text`
- City → `text`
- State → `text` with enumeration or `@NIEM:StateUSPostalServiceCode`
- Postal/ZIP code → `text` with format constraint
- Country → `text` with enumeration

**Financial Information:**
- Monetary amounts → `decimal` type with `USD` (or appropriate currency) units
- Quantities → `integer` type with appropriate units
- Percentages → `decimal` type with `percentage` or `%` units

**Status Fields:**
- Boolean questions (Yes/No) → `boolean` type
- Status with options → `text` type with enumeration
- Priority/Rating scales → `integer` type with enumeration (XdOrdinal)

**Dates and Times:**
- Dates → `date` type
- Timestamps → `datetime` type
- Durations → `integer` type with `days`, `hours`, or appropriate units

### Error Prevention

**DO:**
- ✅ Use `**Enumeration**:` for categorical fields
- ✅ Include `**Examples**:` for every column
- ✅ Add `**Units**:` for all quantified numbers
- ✅ Use lowercase_with_underscores for column names
- ✅ Keep all keywords in English
- ✅ Write content in source language
- ✅ Provide detailed descriptions
- ✅ Use consistent formatting

**DON'T:**
- ❌ Use `**Values**:` or `**Value**:` (use `**Enumeration**:` instead)
- ❌ Use `**Unit**:` (use `**Units**:` plural)
- ❌ Use `**Example**:` (use `**Examples**:` plural)
- ❌ Use `**Data Type**:` (use `**Type**:`)
- ❌ Forget to add constraints for required fields
- ❌ Mix languages in keywords
- ❌ Use vague descriptions like "the value" or "data field"
- ❌ Forget the YAML front matter

---

## PART 13: Quality Checklist

Before providing the template to the user, verify:

**Structure:**
- [ ] YAML front matter present with `template_version: "4.0.0"`
- [ ] Dataset Overview section with Purpose and Business Context
- [ ] At least one Root Cluster defined
- [ ] All data columns are under a cluster
- [ ] Subject/Provider/Participation sections used when form has clear actors (optional but recommended)
- [ ] Demographic fields (names, IDs, birth dates) placed under Subject, not Root Cluster (when Subject is used)
- [ ] No more than one `## Subject:` and one `## Provider:` section

**Keywords (English):**
- [ ] All keywords use English (Type, Description, Enumeration, etc.)
- [ ] All data types in English (text, integer, date, etc.)
- [ ] All structural keywords in English (Column:, Root Cluster:, Subject:, Provider:, Participation:, etc.)

**Content (Source Language):**
- [ ] Column names in source language (or English if form is English)
- [ ] Descriptions in source language
- [ ] Enumeration values and labels in source language
- [ ] Examples in source language and format
- [ ] Business rules in source language

**Required Fields:**
- [ ] Every column has `**Type**:`
- [ ] Every column has `**Description**:`
- [ ] Every column has `**Examples**:`

**Conditional Requirements:**
- [ ] Numeric columns have `**Units**:` (except identifiers)
- [ ] Categorical fields have `**Enumeration**:`
- [ ] Required fields marked with `required: true` in constraints

**Quality:**
- [ ] Descriptions are detailed and clear
- [ ] Examples are realistic and properly formatted
- [ ] Enumerations include all options from the form
- [ ] Constraints match form validation rules
- [ ] Cluster organization is logical

---

## PART 14: Example Interaction

**User Input:**
"Create a template for a patient intake form with fields for: patient ID, full name, date of birth, gender (male/female/other), email, phone, emergency contact name, and emergency contact phone."

**Your Response Should Include:**

```yaml
---
template_version: "4.0.0"
dataset:
  name: "Patient Intake Form"
  description: "Patient demographic and emergency contact information collected at intake"
  domain: "Healthcare"
  creator: "Clinical Staff"
enrichment:
  enable_llm: true
---

# Dataset Overview

Patient intake information collected during registration, including demographics and emergency contact details.

**Purpose**: Capture essential patient information for clinical care and emergency situations

**Business Context**:
- Primary use: Patient identification and contact
- Secondary use: Emergency notifications
- Stakeholders: Registration staff, Clinical staff, Emergency services

## Root Cluster: Patient Information

Core patient demographic and contact information.

**Purpose**: Unique patient identification and contact details
**Business Context**: Required for all clinical encounters

### Column: patient_id
**Type**: identifier
**Description**: Unique patient identifier assigned at registration
**Constraints**:
  - required: true
  - unique: true
**Examples**: PAT-001234, PAT-005678

### Column: full_name
**Type**: text
**Description**: Patient's complete legal name (first and last)
**Constraints**:
  - required: true
**Examples**: John Smith, Mary Johnson, Wei Chen

### Column: date_of_birth
**Type**: date
**Description**: Patient's date of birth
**Constraints**:
  - required: true
  - format: "YYYY-MM-DD"
**Business Rules**: Must be past date; used to calculate current age
**Examples**: 1985-03-15, 1970-12-01, 2000-08-22

### Column: gender
**Type**: text
**Description**: Patient's gender identity
**Enumeration**:
  - male: Male
  - female: Female
  - other: Other gender identity
**Constraints**:
  - required: true
**Examples**: male, female, other

### Column: email
**Type**: email
**Description**: Patient's primary email address for communications
**Constraints**:
  - format: "valid email address"
**Examples**: john.smith@example.com, mary.j@email.org

### Column: phone
**Type**: text
**Description**: Patient's primary contact phone number
**Constraints**:
  - format: "phone number with area code"
**Examples**: (555) 123-4567, 555-987-6543

## Cluster: Emergency Contact

Emergency contact person information.

**Purpose**: Contact person in case of patient emergency
**Business Context**: Critical for emergency situations when patient cannot communicate

### Column: emergency_contact_name
**Type**: text
**Description**: Full name of emergency contact person
**Constraints**:
  - required: true
**Examples**: Jane Smith, Robert Johnson

### Column: emergency_contact_phone
**Type**: text
**Description**: Phone number of emergency contact person
**Constraints**:
  - required: true
  - format: "phone number with area code"
**Examples**: (555) 234-5678, 555-876-5432
```

---

## PART 15: SDCStudio Component Catalog API

If you have HTTP/tool access, you can query SDCStudio's public component catalog to find reusable components instead of guessing `@Project:Label` references.

### Endpoint

```
GET {server_url}/api/v1/catalog/components/
```

### Authentication

Optional. Anonymous access is allowed with rate limits (200 requests/hour). To get higher limits (2000/hour), include the header:

```
Authorization: Token <api_key>
```

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Text search across label and description | `?search=gender` |
| `type` | Filter by component type | `?type=XdString` |
| `project` | Filter by project name | `?project=NIEM` |

Parameters can be combined: `?search=code&type=XdToken&project=NIEM`

### Available Component Types

XdString, XdBoolean, XdCount, XdQuantity, XdFloat, XdDouble, XdOrdinal, XdTemporal, XdLink, XdFile, XdToken, Cluster, Units, Party, Participation, Audit, Attestation, XdInterval, ReferenceRange, SimpleReferenceRange

### Response Format

```json
{
    "count": 42,
    "page": 1,
    "page_size": 50,
    "results": [
        {
            "ct_id": "ct_abc123",
            "label": "StateUSPostalServiceCode",
            "description": "US state postal codes",
            "component_type": "XdToken",
            "project_name": "NIEM",
            "reuse_ref": "@NIEM:StateUSPostalServiceCode"
        }
    ]
}
```

### Usage in Template Generation

When building a template, search the catalog for relevant components before creating new ones. Use the `reuse_ref` value directly in `**ReuseComponent**:` fields.

**Example workflow:**
1. User describes a form with a "State" dropdown field
2. Search the catalog: `GET /api/v1/catalog/components/?search=state&type=XdToken`
3. Find `@NIEM:StateUSPostalServiceCode` in results
4. Use it in the template:

```markdown
### Column: state
**Type**: identifier
**Description**: US state selection
**ReuseComponent**: @NIEM:StateUSPostalServiceCode
```

This avoids creating a duplicate component and leverages existing, validated definitions.

---

## Summary

You now have everything needed to generate SDCStudio templates:

1. **YAML Front Matter** - Always start with this
2. **Dataset Overview** - Explain the purpose
3. **Subject/Provider/Participation** - Model who is involved (optional but recommended when actors exist)
4. **Root Cluster** - Primary data grouping (the "what")
5. **Columns** - Individual fields with Type, Description, Examples, and optional constraints
6. **Multiple Clusters** - Logical groupings for related fields
7. **Language Rules** - Keywords in English, content in source language
8. **Quality Checklist** - Validate before providing to user
9. **Catalog API** - Query published components for reuse (if HTTP access available)

**Remember:**
- Keywords MUST be in English
- Content SHOULD match source language
- Always include Type, Description, and Examples for every column
- Use appropriate data types based on field content
- Add units for numeric quantities
- Use enumeration for categorical fields
- Provide realistic, source-language examples
- Use Subject/Provider/Participation sections when the form has identifiable actors
- Keep demographic data (names, IDs, birth dates) in Subject section, not in Root Cluster

Generate templates that are clear, complete, and ready to upload to SDCStudio!
