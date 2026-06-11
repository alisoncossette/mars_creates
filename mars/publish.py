"""Publish the finished post to X / Twitter."""
from __future__ import annotations

import logging
from typing import Protocol

from .config import Settings
from .content import Post

log = logging.getLogger("mars.publish")


class Publisher(Protocol):
    name: str
    def publish(self, post: Post) -> str: ...  # returns a URL


class XPublisher:
    """Posts to X / Twitter (Mars's own handle). Mock if keys are missing."""
    name = "x"

    def __init__(self, settings: Settings):
        self.s = settings
        self.mock = not all(self.s.x_keys.values())

    def publish(self, post: Post) -> str:
        text = self._fit(post.caption)
        if self.mock:
            log.info("[x] MOCK tweet (no X keys): %s", text.replace("\n", " ")[:90])
            return "https://x.com/mars/status/mock"

        import io
        import tweepy

        k = self.s.x_keys
        media_ids = None
        if post.image:  # upload the image via v1.1 media endpoint
            api = tweepy.API(tweepy.OAuth1UserHandler(
                k["api_key"], k["api_secret"], k["access_token"], k["access_secret"]))
            media = api.media_upload(filename="image.jpg", file=io.BytesIO(post.image))
            media_ids = [media.media_id]

        client = tweepy.Client(  # v2 endpoint creates the tweet
            consumer_key=k["api_key"], consumer_secret=k["api_secret"],
            access_token=k["access_token"], access_token_secret=k["access_secret"],
        )
        resp = client.create_tweet(text=text, media_ids=media_ids)
        tid = resp.data.get("id")
        log.info("[x] posted tweet %s", tid)
        return f"https://x.com/i/web/status/{tid}"

    @staticmethod
    def _fit(caption: str, limit: int = 280) -> str:
        """Keep the post under X's limit, preserving the @mention block at the end."""
        if len(caption) <= limit:
            return caption
        parts = caption.split("\n\n", 1)
        if len(parts) == 2:
            lead, tail = parts
            budget = limit - len(tail) - 4
            if budget > 20:
                return lead[:budget].rstrip() + "…\n\n" + tail
        return caption[: limit - 1] + "…"


def build_publishers(settings: Settings) -> list[Publisher]:
    return [XPublisher(settings)]
