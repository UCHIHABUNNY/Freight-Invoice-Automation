"""Workflow statuses. Step 2 only sets uploaded; later stages are reserved."""

UPLOADED = "uploaded"
EXTRACTING = "extracting"
RECONCILING = "reconciling"
DRAFTED = "drafted"
NEEDS_REVIEW = "needs_review"
APPROVED = "approved"
REJECTED = "rejected"

ALL_STATUSES = (
    UPLOADED,
    EXTRACTING,
    RECONCILING,
    DRAFTED,
    NEEDS_REVIEW,
    APPROVED,
    REJECTED,
)

TERMINAL_STATUSES = (APPROVED, REJECTED)


def empty_status_timestamps() -> dict[str, str | None]:
    return {status: None for status in ALL_STATUSES}
