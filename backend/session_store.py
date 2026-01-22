from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from uuid import uuid4

from .schemas import Action, ActionRecord, ActionType, GameStatePublic, Street


DEFAULT_PLAYER_ID = "player"


def default_state(session_id: str) -> GameStatePublic:
    return GameStatePublic(
        session_id=session_id,
        street=Street.PREFLOP,
        pot=0,
        community_cards=[],
        hand=["As", "Kd"],
        stacks={DEFAULT_PLAYER_ID: 1000},
        bets={DEFAULT_PLAYER_ID: 0},
        current_player=DEFAULT_PLAYER_ID,
        legal_actions=[
            ActionType.CHECK,
            ActionType.CALL,
            ActionType.RAISE,
            ActionType.FOLD,
        ],
        action_history=[],
    )


@dataclass
class SessionData:
    session_id: str
    state: GameStatePublic


class SessionStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionData] = {}

    def get_or_create(self, session_id: Optional[str]) -> Tuple[SessionData, bool]:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id], False

        if not session_id:
            session_id = uuid4().hex

        session = SessionData(session_id=session_id, state=default_state(session_id))
        self._sessions[session_id] = session
        return session, True

    def record_action(self, session_id: str, action: Action) -> GameStatePublic:
        session = self._sessions[session_id]
        session.state.action_history.append(
            ActionRecord(player_id=DEFAULT_PLAYER_ID, action=action)
        )

        if action.action == ActionType.RAISE and action.amount:
            session.state.pot += action.amount
            session.state.bets[DEFAULT_PLAYER_ID] += action.amount

        return session.state
