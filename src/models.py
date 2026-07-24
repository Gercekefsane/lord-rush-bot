"""Data models and constants for Lords Rush Bot"""

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================
# GAME TYPE CONSTANTS
# ============================================

GAME_LR = 'lr'
GAME_CHOICES = [GAME_LR]
GAME_NAMES = {GAME_LR: 'Lords Rush'}
GAME_ICONS = {GAME_LR: '⚔️'}


class GiftCodeStatus(Enum):
    """Gift code validation states"""
    PENDING = 0
    VALIDATED = 1
    INVALID = 2
    EXPIRED = 3


class RedemptionResult(Enum):
    """Result of a gift code redemption attempt"""
    SUCCESS = "success"            # err_code 20000
    ALREADY_USED = "already_used"  # err_code 40008
    INVALID = "invalid"            # err_code 40014 (CDK_NOT_FOUND)
    KID_MISMATCH = "kid_mismatch"  # err_code 40020 (needs review)
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    UNKNOWN = "unknown"


@dataclass
class PlayerInfo:
    """Registration record for a player.

    Lords Rush exposes no player-info API (the `/player` route returns 404),
    so the bot stores the FID + kingdom supplied at registration and redeems
    against them. `kid` (kingdom id) is required by the redeem call.
    """
    fid: int
    kid: int  # kingdom id — required for redemption
    nickname: Optional[str] = None
    game_type: str = GAME_LR

    @property
    def kingdom_display(self) -> str:
        return f"#{self.kid}" if self.kid else "Unknown"


@dataclass
class GiftCode:
    """Gift code data model"""
    code: str
    game_type: str = GAME_LR
    status: GiftCodeStatus = GiftCodeStatus.PENDING
    discovered_at: Optional[str] = None
    validated_at: Optional[str] = None


@dataclass
class Alliance:
    """Alliance data model"""
    alliance_id: int
    tag: str
    name: str
    game_type: str = GAME_LR
    owner_id: Optional[int] = None
    chat_id: Optional[int] = None
    suspended: bool = False
    priority: int = 0


@dataclass
class RedemptionReport:
    """Report for a gift code redemption batch"""
    code: str
    alliance_tag: str
    total: int = 0
    success: int = 0
    already_used: int = 0
    failed: int = 0
    errors: dict = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        return (self.success / self.total * 100) if self.total > 0 else 0.0


# ============================================
# API REQUEST SIGNING
# ============================================

def generate_sign(params: str, encrypt_key: str) -> str:
    """Generate MD5 signature for game API requests.

    Args:
        params: Sorted, URL-encoded form parameters
            (e.g. 'cdk=ABC&fid=123&kid=45&time=1690000000')
        encrypt_key: Per-game secret key (never committed to this repo).

    Returns:
        MD5 hex digest string.
    """
    return hashlib.md5(
        (params + encrypt_key).encode('utf-8')
    ).hexdigest()


def build_giftcode_request(fid: int, cdk: str, kid: int, encrypt_key: str) -> str:
    """Build a signed request body for Lords Rush gift-code redemption.

    Signature scheme (Century Games'): the request params in ALPHABETICAL
    order (cdk, fid, kid, time), joined with '&', followed by a per-game
    secret key, hashed with MD5. Timestamp is unix SECONDS. `kid` is required.
    There is no captcha and no player-login step.

    Returns:
        A URL-encoded form body string including the `sign` field.
    """
    current_time = int(time.time())  # unix seconds
    sorted_params = f"cdk={cdk}&fid={fid}&kid={kid}&time={current_time}"
    sign = generate_sign(sorted_params, encrypt_key)
    return f"sign={sign}&{sorted_params}"
