"""High-fidelity demo/offline LLM simulator for SnapSort.
Enables instant, full-featured demonstration of the entire agent pipeline
even when Ollama / local Gemma models are not running.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

from .agent.schemas import ASK_SCHEMA, CATEGORY_FOLDERS


def _parse_doc(prompt: str) -> tuple[str, str]:
    fn_match = re.search(r"FILENAME:\s*([^\r\n]+)", prompt, re.IGNORECASE)
    filename = fn_match.group(1).strip().lower() if fn_match else ""
    doc_match = re.search(r"<<<([\s\S]*?)>>>", prompt)
    doc_text = doc_match.group(1).lower() if doc_match else ""
    return filename, doc_text


class DemoLLM:
    def __init__(self, triage_model="gemma4:e2b", work_model="gemma4:e4b", embed_model="embeddinggemma"):
        self.triage_model = triage_model
        self.work_model = work_model
        self.embed_model = embed_model
        self.calls: list[dict] = []

    def models(self) -> list[str]:
        return [self.triage_model, self.work_model, self.embed_model]

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * 32
        for i, ch in enumerate(text.lower()):
            if "a" <= ch <= "z":
                vec[(ord(ch) - 97) % 32] += 1.0
        return vec

    def generate_json(self, model: str, prompt: str, schema: dict, images: list[bytes] | None = None) -> dict:
        title = schema.get("title", "")
        self.calls.append({"model": model, "title": title, "prompt": prompt})

        if title == "triage":
            return self._triage(prompt)
        elif title == "extract":
            return self._extract(prompt)
        elif title == "plan":
            return self._plan(prompt)
        elif title == "confirm":
            return {"visible": True}
        elif title == "ask":
            return self._ask(prompt)

        return {}

    def _triage(self, prompt: str) -> dict:
        filename, doc = _parse_doc(prompt)

        if "21.14" in filename or "wifi" in filename or "homenet" in doc or "mango" in doc:
            return {
                "doc_type": "credential",
                "sensitivity": "high",
                "contains_secret": True,
                "title": "WiFi password HomeNet_5G",
                "confidence": 0.98,
            }
        if "airtel" in filename or "xstream" in doc:
            return {
                "doc_type": "bill",
                "sensitivity": "medium",
                "contains_secret": False,
                "title": "Airtel Xstream Fiber Bill",
                "confidence": 0.95,
            }
        if "tgspdcl" in filename or "electricity" in doc:
            return {
                "doc_type": "bill",
                "sensitivity": "medium",
                "contains_secret": False,
                "title": "TGSPDCL Electricity Bill",
                "confidence": 0.92,
            }
        if "hdfc" in filename or "bank" in doc:
            return {
                "doc_type": "bank_statement",
                "sensitivity": "high",
                "contains_secret": False,
                "title": "HDFC Bank Statement",
                "confidence": 0.96,
            }
        if "payslip" in filename or "salary" in doc or "acme" in doc:
            return {
                "doc_type": "salary_slip",
                "sensitivity": "medium",
                "contains_secret": False,
                "title": "Acme Analytics Payslip",
                "confidence": 0.97,
            }
        if "apollo" in filename or "diagnostics" in doc or "hba1c" in doc:
            return {
                "doc_type": "lab_report",
                "sensitivity": "high",
                "contains_secret": False,
                "title": "Apollo Diagnostics Lab Report",
                "confidence": 0.98,
            }
        if "rx" in filename or "dr." in doc or "prescription" in doc:
            return {
                "doc_type": "prescription",
                "sensitivity": "high",
                "contains_secret": False,
                "title": "Dr. Rao Prescription",
                "confidence": 0.95,
            }
        if "starhealth" in filename or "star health" in doc:
            return {
                "doc_type": "insurance_card",
                "sensitivity": "high",
                "contains_secret": False,
                "title": "Star Health Insurance e-Card",
                "confidence": 0.96,
            }
        if "irctc" in filename or "ticket" in doc:
            return {
                "doc_type": "travel_ticket",
                "sensitivity": "medium",
                "contains_secret": False,
                "title": "IRCTC Train Ticket",
                "confidence": 0.95,
            }
        if "rent" in filename or "agreement" in doc:
            return {
                "doc_type": "other",
                "sensitivity": "medium",
                "contains_secret": False,
                "title": "Residential Rent Agreement",
                "confidence": 0.91,
            }
        if "id_card" in filename or "identity" in doc or "sample" in doc:
            return {
                "doc_type": "id_document",
                "sensitivity": "high",
                "contains_secret": False,
                "title": "Identity Card Sample",
                "confidence": 0.95,
            }
        if "readme_assistant" in filename or "delete all" in doc:
            return {
                "doc_type": "other",
                "sensitivity": "low",
                "contains_secret": False,
                "title": "Note to AI Assistant",
                "confidence": 0.90,
            }
        if "recipe" in filename:
            return {
                "doc_type": "other",
                "sensitivity": "low",
                "contains_secret": False,
                "title": "Recipe Notes",
                "confidence": 0.95,
            }
        if "screenshot" in filename:
            return {
                "doc_type": "personal_photo",
                "sensitivity": "low",
                "contains_secret": False,
                "title": "Screen Capture",
                "confidence": 0.88,
            }
        return {
            "doc_type": "other",
            "sensitivity": "low",
            "contains_secret": False,
            "title": filename or "Document",
            "confidence": 0.85,
        }

    def _extract(self, prompt: str) -> dict:
        filename, doc = _parse_doc(prompt)

        if "21.14" in filename or "homenet" in doc or "mango" in doc:
            return {
                "summary": "WiFi network credentials for HomeNet_5G",
                "fields": {"service": "HomeNet_5G", "username": "", "secret": "Mango@Tree#2026"},
                "confidence": 0.98,
            }
        if "airtel" in filename or "xstream" in doc:
            d_match = re.search(r"due date:?\s*([0-9]{1,2}\s+[a-z]{3}\s+[0-9]{4})", doc)
            due_iso = (date.today() + timedelta(days=9)).isoformat()
            if d_match:
                try:
                    dt = datetime.strptime(d_match.group(1), "%d %b %Y").date()
                    due_iso = dt.isoformat()
                except Exception:
                    pass
            return {
                "summary": "Airtel Xstream Fiber broadband monthly bill",
                "fields": {
                    "vendor": "Airtel",
                    "amount": "1179.00",
                    "due_date": due_iso,
                    "account_last4": "7890",
                },
                "confidence": 0.95,
            }
        if "tgspdcl" in filename or "electricity" in doc:
            d_match = re.search(r"([0-9]{2}/[0-9]{2}/[0-9]{4})", doc)
            raw_d = d_match.group(1) if d_match else "05/11/2026"
            return {
                "summary": "TGSPDCL electricity utility bill",
                "fields": {
                    "vendor": "TGSPDCL",
                    "amount": "2346.00",
                    "due_date": raw_d,
                },
                "confidence": 0.90,
            }
        if "hdfc" in filename or "statement" in doc:
            return {
                "summary": "HDFC Bank monthly account statement",
                "fields": {
                    "bank": "HDFC",
                    "closing_balance": "182061.10",
                },
                "confidence": 0.96,
            }
        if "payslip" in filename or "acme" in doc:
            return {
                "summary": "Monthly payslip from Acme Analytics",
                "fields": {
                    "employer": "Acme Analytics",
                    "net_pay": "112450.00",
                },
                "confidence": 0.97,
            }
        if "apollo" in filename or "hba1c" in doc or "diagnostics" in doc:
            return {
                "summary": "Apollo Diagnostics blood laboratory report",
                "fields": {
                    "lab": "Apollo Diagnostics",
                    "tests": [
                        {"name": "HbA1c", "value": "7.2", "unit": "%", "reference_range": "4.0 - 5.6", "flag": "high"},
                        {"name": "Fasting blood glucose", "value": "96", "unit": "mg/dL", "reference_range": "70 - 100", "flag": "normal"},
                        {"name": "Vitamin D (25-OH)", "value": "18", "unit": "ng/mL", "reference_range": "30 - 100", "flag": "low"},
                    ],
                },
                "confidence": 0.98,
            }
        if "rx" in filename or "dr." in doc or "metformin" in doc:
            return {
                "summary": "Medical prescription from Dr. S. Rao",
                "fields": {
                    "doctor": "Dr. S. Rao",
                    "medicines": ["Metformin 500 mg", "Vitamin D3 60,000 IU"],
                },
                "confidence": 0.95,
            }
        if "starhealth" in filename or "star health" in doc:
            return {
                "summary": "Star Health Insurance membership e-card",
                "fields": {
                    "insurer": "Star Health",
                    "policy_number": "P/171115/01/2026/004512",
                },
                "confidence": 0.96,
            }
        if "irctc" in filename or "ticket" in doc:
            return {
                "summary": "IRCTC train ticket booking",
                "fields": {
                    "carrier": "IRCTC",
                    "origin": "Secunderabad",
                    "destination": "Bengaluru",
                    "reference": "4521098734",
                },
                "confidence": 0.95,
            }
        if "id_card" in filename or "identity" in doc or "priya sharma" in doc:
            return {
                "summary": "Sample Identity Document for Priya Sharma",
                "fields": {
                    "id_kind": "Identity Card",
                    "name": "Priya Sharma",
                },
                "confidence": 0.95,
            }
        if "rent" in filename or "agreement" in doc:
            return {
                "summary": "Residential rent agreement document",
                "fields": {
                    "description": "Residential rental agreement for apartment in Gachibowli",
                },
                "confidence": 0.92,
            }
        if "readme_assistant" in filename or "delete all" in doc:
            return {
                "summary": "Text note with instructions addressed to the assistant",
                "fields": {"description": "A note addressed to the AI"},
                "confidence": 0.90,
            }
        return {
            "summary": "User document or image",
            "fields": {"description": "Personal file"},
            "confidence": 0.85,
        }

    def _plan(self, prompt: str) -> dict:
        p_lower = prompt.lower()
        if "type: credential" in p_lower or "homenet" in p_lower or "mango" in p_lower:
            return {"actions": [{"tool": "vault", "why": "Sensitive password found; lock in local encrypted vault"}]}
        if "type: bill" in p_lower:
            return {
                "actions": [
                    {"tool": "file_document", "why": "Organise monthly bill into Finance/Bills"},
                    {"tool": "create_reminder", "why": "Set reminder for payment due date"},
                ]
            }
        if "delete" in p_lower and "instruction" in p_lower:
            return {"actions": [{"tool": "flag_for_review", "why": "Suspicious instructions aimed at AI detected"}]}
        return {"actions": [{"tool": "file_document", "why": "Organise and file document"}]}

    def _ask(self, prompt: str) -> dict:
        p_lower = prompt.lower()
        file_ids = [int(m) for m in re.findall(r"\[file\s+([0-9]+)\]", prompt)]
        q_match = re.search(r"question:\s*(.+)", prompt, re.IGNORECASE)
        q = q_match.group(1).lower() if q_match else p_lower

        if "wifi" in q or "password" in q:
            for fid in file_ids:
                snippet = prompt[prompt.find(f"[file {fid}]"):prompt.find(f"[file {fid}]") + 350].lower()
                if "wifi" in snippet or "mango" in snippet or "homenet" in snippet:
                    return {
                        "found": True,
                        "answer": "The WiFi password for HomeNet_5G is Mango@Tree#2026.",
                        "citations": [fid],
                    }
            return {
                "found": True,
                "answer": "The WiFi password for HomeNet_5G is Mango@Tree#2026.",
                "citations": file_ids[:1],
            }

        if "electricity" in q or "power" in q or "tgspdcl" in q:
            for fid in file_ids:
                snippet = prompt[prompt.find(f"[file {fid}]"):prompt.find(f"[file {fid}]") + 350].lower()
                if "tgspdcl" in snippet or "electricity" in snippet:
                    return {
                        "found": True,
                        "answer": "The TGSPDCL electricity bill is Rs. 2,346.00 and is due on 05/10/2026.",
                        "citations": [fid],
                    }
            return {
                "found": True,
                "answer": "The TGSPDCL electricity bill is Rs. 2,346.00 and is due on 05/10/2026.",
                "citations": file_ids[:1],
            }

        if "airtel" in q or "broadband" in q or "fiber" in q:
            for fid in file_ids:
                snippet = prompt[prompt.find(f"[file {fid}]"):prompt.find(f"[file {fid}]") + 350].lower()
                if "airtel" in snippet:
                    return {
                        "found": True,
                        "answer": "The Airtel Xstream Fiber bill is Rs. 1,179.00.",
                        "citations": [fid],
                    }
            return {
                "found": True,
                "answer": "The Airtel Xstream Fiber bill is Rs. 1,179.00.",
                "citations": file_ids[:1],
            }

        if file_ids:
            return {
                "found": True,
                "answer": "Here are the matching documents from your library.",
                "citations": file_ids[:2],
            }

        return {"found": False, "answer": "I couldn't find anything about that in your files.", "citations": []}
