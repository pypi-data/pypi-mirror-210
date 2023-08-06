# GENERATED CODE - DO NOT MODIFY
from __future__ import annotations
from chitose.xrpc import XrpcCallable
from .admin import Admin_
from .identity import Identity_
from .label import Label_
from .moderation import Moderation_
from .repo import Repo_
from .server import Server_
from .sync import Sync_

class Atproto_:
    """We recommend calling methods in this class via the :doc:`chitose.BskyAgent <chitose>` class instead of creating instances of this class directly."""

    def __init__(self, call: XrpcCallable) -> None:
        self.call = call

    @property
    def admin(self):
        return Admin_(self.call)

    @property
    def identity(self):
        return Identity_(self.call)

    @property
    def label(self):
        return Label_(self.call)

    @property
    def moderation(self):
        return Moderation_(self.call)

    @property
    def repo(self):
        return Repo_(self.call)

    @property
    def server(self):
        return Server_(self.call)

    @property
    def sync(self):
        return Sync_(self.call)