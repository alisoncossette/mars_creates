"""Publish the finished post. Two targets: a gallery (served via Akamai CDN) and X."""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Protocol

from .config import Settings
from .content import Post

log = logging.getLogger("mars.publish")


class Publisher(Protocol):
    name: str
    def publish(self, post: Post) -> str: ...  # returns a URL


class GalleryPublisher:
    """Uploads the post to the Akamai-fronted gallery. Mock: writes to ./out and returns a path."""
    name = "gallery"

    def __init__(self, settings: Settings):
        self.s = settings

    def publish(self, post: Post) -> str:
        slug = f"post-{int(time.time())}"
        payload = {"caption": post.caption, "quote": post.quote, "alt": post.alt_text, "event": post.event}
        if not self.s.gallery_upload_url:
            os.makedirs("out", exist_ok=True)
            with open(f"out/{slug}.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            if post.image:
                with open(f"out/{slug}.jpg", "wb") as f:
                    f.write(post.image)
            log.info("[gallery] MOCK wrote out/%s.*", slug)
            return f"out/{slug}.json"
        # TODO(akamai): PUT image + payload to gallery origin; Akamai CDN serves gallery_base_url/<slug>.
        import httpx  # lazy — only needed for real uploads
        files = {"image": ("hero.jpg", post.image, "image/jpeg")}
        httpx.post(self.s.gallery_upload_url, data={"meta": json.dumps(payload)}, files=files, timeout=30)
        return f"{self.s.gallery_base_url.rstrip('/')}/{slug}"


class XPublisher:
    """Posts to X / Twitter (Mars's own handle). Mock: logs and returns a fake URL."""
    name = "x"

    def __init__(self, settings: Settings):
        self.s = settings
        self.mock = not all(self.s.x_keys.values())

    def publish(self, post: Post) -> str:
        if self.mock:
            log.info("[x] MOCK tweet: %s", post.caption.replace("\n", " ")[:80])
            return "https://x.com/mars/status/mock"
        # TODO(x): tweepy client with self.s.x_keys; upload media (post.image) + create tweet (post.caption).
        return "https://x.com/mars/status/real"


def build_publishers(settings: Settings) -> list[Publisher]:
    pubs: list[Publisher] = []
    if settings.publish_gallery:
        pubs.append(GalleryPublisher(settings))
    if settings.publish_x:
        pubs.append(XPublisher(settings))
    return pubs
