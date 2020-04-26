MOST_IMP_WT = 1
IMP_WT = 0.9
DEFAULT_WT = 0.85

court_weights = {
    "SG Court of Appeal": MOST_IMP_WT,
    "SG Privy Council": MOST_IMP_WT,
    "UK House of Lords": MOST_IMP_WT,
    "UK Supreme Court": MOST_IMP_WT,
    "High Court of Australia": MOST_IMP_WT,
    "CA Supreme Court": MOST_IMP_WT,
    
    "SG High Court": IMP_WT,
    "Singapore International Commercial Court": IMP_WT,
    "HK High Court": IMP_WT,
    "HK Court of First Instance": IMP_WT,
    "UK Crown Court": IMP_WT,
    "UK Court of Appeal": IMP_WT,
    "UK High Court": IMP_WT,
    "Federal Court of Australia": IMP_WT,
    "NSW Court of Appeal": IMP_WT,
    "NSW Court of Criminal Appeal": IMP_WT,
    "NSW Supreme Court": IMP_WT,
}

def get_court_weight(court):
    if court in court_weights:
        return court_weights[court]

    return DEFAULT_WT
