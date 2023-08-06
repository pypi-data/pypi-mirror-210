from __future__ import annotations

import abc
import enum
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import requests
from pydantic import BaseModel
from requests import Response


class WandCoreClient:
    def __init__(self, token: str, base_url: str) -> None:
        self._token = token
        self._base_url = base_url

    def request(
        self, method: str, path: str, json: dict[str, Any] | None = None
    ) -> Response:
        resp = requests.request(
            method=method,
            url=self._base_url + path,
            headers={"Authorization": f"Bearer {self._token}"},
            json=json,
        )
        resp.raise_for_status()
        return resp


class Source(BaseModel):
    id: str


class FileSourceCreationResult(BaseModel):
    source: Source
    upload_url: str


class Sources:
    def __init__(self, core: WandCoreClient) -> None:
        self._core = core

    def create_web(
        self,
        urls: list[str],
        max_crawl_pages: int = 20,
    ) -> Source:
        res = self._core.request(
            method="post",
            path="/source/web_scraper",
            json={
                "urls": urls,
                "max_crawl_pages": max_crawl_pages,
            },
        ).json()
        return Source(id=res["source_id"])

    def create_file(self, filename: str) -> FileSourceCreationResult:
        res = self._core.request(
            method="post",
            path="/source/file",
            json={
                "filename": filename,
            },
        ).json()
        return FileSourceCreationResult(
            source=Source(id=res["source_id"]), upload_url=res["upload_signed_url"]
        )

    def create_from_filepath(self, filepath: str | Path) -> Source:
        path = Path(filepath)
        res = self.create_file(path.name)
        with path.open() as file:
            requests.put(res.upload_url, data=file)
        return res.source


class ModelStatus(BaseModel):
    progress: int
    training_completed: bool


class Model(BaseModel):
    id: str
    source_ids: list[str]
    status: ModelStatus


class ChatMessageAuthor(str, enum.Enum):
    AI = "ai"
    HUMAN = "human"


class ChatMessage(BaseModel):
    author: ChatMessageAuthor
    message: str


class TrainingListener(abc.ABC):
    @abc.abstractmethod
    def on_model_progress(self, model: Model) -> None:
        pass


class Models:
    def __init__(self, core: WandCoreClient) -> None:
        self._core = core

    def _parse_model_payload(self, payload: Mapping[str, Any]) -> Model:
        return Model(
            id=payload["model_id"],
            source_ids=payload["source_ids"],
            status=ModelStatus(
                progress=payload["status"]["progress"],
                training_completed=payload["status"]["training_completed"],
            ),
        )

    def start_training(self, source_ids: list[str]) -> Model:
        res = self._core.request(
            method="post",
            path="/models",
            json={
                "source_ids": source_ids,
            },
        ).json()
        return self._parse_model_payload(res)

    def get(self, model_id: str) -> Model:
        res = self._core.request(
            method="GET",
            path=f"/models/{model_id}",
        ).json()
        return self._parse_model_payload(res)

    def list_all(self) -> list[Model]:
        res = self._core.request(
            method="GET",
            path=f"/models",
        ).json()
        return [self._parse_model_payload(it) for it in res]

    def infer(
        self, model_id: str, prompt: str, chat_history: Sequence[ChatMessage]
    ) -> str:
        res = self._core.request(
            method="post",
            path=f"/models/{model_id}/infer",
            json={
                "prompt": prompt,
                "chat_history": [
                    {
                        "author": it.author,
                        "message": it.message,
                    }
                    for it in chat_history
                ],
            },
        )
        return res.json()

    def train(
        self, source_ids: list[str], listener: TrainingListener | None = None
    ) -> Model:
        model = self.start_training(source_ids)
        while True:
            model = self.get(model.id)
            if listener:
                listener.on_model_progress(model)
            if model.status.training_completed:
                return model
            time.sleep(1)


class WandClient:
    def __init__(
        self,
        token: str,
        base_url: str,
    ):
        core = WandCoreClient(token=token, base_url=base_url)
        self.source = Sources(core)
        self.models = Models(core)
