import dataclasses


@dataclasses.dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type."""

    user_id: int
    payload: str
