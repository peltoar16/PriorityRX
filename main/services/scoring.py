# Simple severity scoring functions for demo purposes.
# In production, replace with validated clinical mappings and libraries.

CHARLSON_MAP = {
    'I50': 2,  # heart failure
    'C': 6,    # cancer prefix
    'E10': 1,  # diabetes type 1
    'E11': 1,  # diabetes type 2
}

def compute_charlson(icd_codes):
    score = 0
    for code in icd_codes:
        for prefix, weight in CHARLSON_MAP.items():
            if code.startswith(prefix):
                score += weight
    return score

def compute_severity(patient, prescription, icd_codes):
    # base severity from charlson
    base = compute_charlson(icd_codes)
    if patient.terminal_illness:
        base += 10
    # if prescription flagged as critical (demo: check name)
    med = prescription.medication_id
    if med and 'opioid' in (prescription.dosage_instructions or '').lower():
        base += 15
    # normalize to 0-100
    score = min(max(base * 5, 0), 100)
    return score
