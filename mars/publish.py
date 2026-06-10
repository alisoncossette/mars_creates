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
    """Pushes the post to Linode Object Storage (S3), served via Akamai CDN.
    Mock (no S3 configured): writes to ./out and returns a local path."""
    name = "gallery"

    def __init__(self, settings: Settings):
        self.s = settings

    def publish(self, post: Post) -> str:
        slug = f"post-{int(time.time())}"
        meta = {"caption": post.caption, "quote": post.quote, "handle": post.handle,
                "alt": post.alt_text, "event": post.event}

        if not self.s.s3_configured:
            os.makedirs("out", exist_ok=True)
            with open(f"out/{slug}.json", "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            if post.image:
                with open(f"out/{slug}.jpg", "wb") as f:
                    f.write(post.image)
            log.info("[gallery] MOCK wrote out/%s.* (set LINODE_S3_* to push to Akamai)", slug)
            return f"out/{slug}.json"

        # Real: PUT to Linode Object Storage; Akamai CDN fronts it.
        import boto3  # lazy — only needed for real uploads
        s3 = boto3.client(
            "s3",
            endpoint_url=self.s.s3_endpoint,
            region_name=self.s.s3_region,
            aws_access_key_id=self.s.s3_key,
            aws_secret_access_key=self.s.s3_secret,
        )
        img_key = f"{slug}.jpg"
        s3.put_object(Bucket=self.s.s3_bucket, Key=img_key, Body=post.image or b"",
                      ContentType="image/jpeg", ACL="public-read")
        s3.put_object(Bucket=self.s.s3_bucket, Key=f"{slug}.json",
                      Body=json.dumps(meta).encode(), ContentType="application/json", ACL="public-read")
        log.info("[gallery] pushed %s to s3://%s", img_key, self.s.s3_bucket)
        if self.s.cdn_base_url:
            return f"{self.s.cdn_base_url.rstrip('/')}/{img_key}"
        return f"{self.s.s3_endpoint.rstrip('/')}/{self.s.s3_bucket}/{img_key}"


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
