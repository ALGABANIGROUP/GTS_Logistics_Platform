"""Static rules for email priority and auto responses."""

PRIORITY_RULES = {
    "CRITICAL": [
        {"contains": ["urgent", "emergency", "critical"]},
        {"from_domain": ["security@gabanilogistics.com", "safety@gabanilogistics.com"]},
        {"subject_contains": ["ALERT", "BREACH", "ACCIDENT"]},
    ],
    "HIGH": [
        {"contains": ["invoice", "payment", "shipment"]},
        {"from_domain": ["accounts@gabanilogistics.com", "freight@gabanilogistics.com"]},
    ],
    "MEDIUM": [
        {"contains": ["inquiry", "question", "support"]},
        {"from_domain": ["customers@gabanilogistics.com"]},
    ],
    "LOW": [
        {"contains": ["newsletter", "marketing", "promotion"]},
        {"from_domain": ["marketing@gabanilogistics.com"]},
    ],
}

AUTO_RESPONSE_RULES = {
    "acknowledgement": {
        "conditions": [
            lambda email: "thank you" in email.get("body", "").lower(),
            lambda email: "confirmation" in email.get("subject", "").lower(),
        ],
        "response_template": "auto_acknowledgement.html",
    },
    "quote_request": {
        "conditions": [
            lambda email: "quote" in email.get("subject", "").lower(),
            lambda email: "price" in email.get("body", "").lower(),
        ],
        "response_template": "auto_quote_response.html",
    },
    "tracking_request": {
        "conditions": [
            lambda email: "tracking" in email.get("subject", "").lower(),
            lambda email: "where is" in email.get("body", "").lower(),
        ],
        "response_template": "auto_tracking_response.html",
    },
}
