from enum import Enum


class ClauseType(str, Enum):
    """Supported clause types."""
    PAYMENT = "payment"
    TERMINATION = "termination"
    RENEWAL = "renewal"
    CONFIDENTIALITY = "confidentiality"
    LIABILITY = "liability"
    INDEMNIFICATION = "indemnification"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    DISPUTE_RESOLUTION = "dispute_resolution"
    NON_COMPETE = "non_compete"
    DATA_PROTECTION = "data_protection"
    GOVERNING_LAW = "governing_law"
    OTHER = "other"


CLAUSE_DESCRIPTIONS = {
    ClauseType.PAYMENT: "Clauses about payment terms, fees, pricing, invoicing",
    ClauseType.TERMINATION: "Clauses about termination rights, notice periods, exit conditions",
    ClauseType.RENEWAL: "Clauses about automatic renewal, renewal terms, extension options",
    ClauseType.CONFIDENTIALITY: "Clauses about confidential information, NDA provisions",
    ClauseType.LIABILITY: "Clauses about liability limits, damages exclusions",
    ClauseType.INDEMNIFICATION: "Clauses about indemnification obligations",
    ClauseType.INTELLECTUAL_PROPERTY: "Clauses about IP ownership, licensing, usage rights",
    ClauseType.DISPUTE_RESOLUTION: "Clauses about dispute resolution, arbitration, jurisdiction",
    ClauseType.NON_COMPETE: "Clauses about non-compete, non-solicitation restrictions",
    ClauseType.DATA_PROTECTION: "Clauses about data protection, privacy, GDPR compliance",
    ClauseType.GOVERNING_LAW: "Clauses about governing law, jurisdiction",
    ClauseType.OTHER: "Other clauses not fitting above categories",
}
