"""
TemplateGenerator -- renders Jinja2 IaC templates for each finding.
Templates are stored in app/templates/{deliverable_template_id}/
Each template folder: main.bicep (phase1), main.tf (phase2), README.md
"""
from __future__ import annotations
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)
TEMPLATES_DIR = Path(__file__).parent / "templates"


class TemplateGenerator:
    def __init__(self, templates_dir: Path = TEMPLATES_DIR) -> None:
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
            keep_trailing_newline=True,
        )

    def generate(self, findings: list[dict], scan_id: str, subscription_id: str) -> list[dict]:
        """
        For each finding that has a deliverable_template_id, render the templates.
        Returns list of {finding_id, template_id, files: [{name, content}]}.
        """
        artifacts: list[dict] = []
        for finding in findings:
            tmpl_id = finding.get("deliverable_template_id")
            if not tmpl_id:
                continue
            files = []
            for tpl_name in ("main.bicep", "main.tf", "README.md"):
                rel = f"{tmpl_id}/{tpl_name}"
                try:
                    tpl = self.env.get_template(rel)
                    rendered = tpl.render(
                        scan_id=scan_id,
                        subscription_id=subscription_id,
                        finding=finding,
                    )
                    files.append({"name": tpl_name, "content": rendered})
                except TemplateNotFound:
                    pass  # template file may not exist; skip silently
                except Exception as exc:
                    logger.warning("[%s] template render error (%s): %s", scan_id, rel, exc)

            if files:
                artifacts.append({
                    "finding_id": finding.get("id"),
                    "template_id": tmpl_id,
                    "files": files,
                })
        return artifacts
