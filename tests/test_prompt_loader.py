"""The packaged LLM prompt is the one source of truth and teaches the md2pd syntax.

4.6.0 shipped a pre-4.5.0 copy under form2sdc/ (## Root Cluster:, ### Column:),
which prompt_loader tries first, so the Gemini path wrote templates md2pd rejects.
"""
from pathlib import Path

from form2sdc.prompt_loader import load_system_prompt

ROOT = Path(__file__).resolve().parents[1]


def test_packaged_prompt_matches_the_repository_root():
    assert (ROOT / "form2sdc" / "Form2SDCTemplate.md").read_text() == (ROOT / "Form2SDCTemplate.md").read_text()


def test_the_loaded_prompt_teaches_the_md2pd_section_syntax():
    text = load_system_prompt()
    assert text.count("## Data:") > 10
    # The old headings may appear only where the document warns against them.
    old_mentions = [line for line in text.splitlines() if "### Column:" in line or "## Root Cluster:" in line]
    assert old_mentions and all(("not" in line.lower() or "do not" in line.lower()) for line in old_mentions), old_mentions
    assert text.count("### Column:") <= 1
    assert 'template_version: "4.0.0"' in text
