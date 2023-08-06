import operator
from typing import Optional, Sequence

from rich import box
from rich.console import RenderableType
from rich.table import Table

from wand_client.cli.config import WandCliSettings
from wand_client.sdk.core import Model, Source


class SettingsFormatter:
    def __call__(self, settings: WandCliSettings) -> RenderableType:
        table = Table(
            box=None,
            show_header=False,
            show_edge=False,
        )
        table.add_column()
        table.add_column(style="bold")
        table.add_row("WAND_API_URL", settings.WAND_API_URL)
        if settings.WAND_TOKEN and ":" in settings.WAND_TOKEN:
            token_id, token_secret = settings.WAND_TOKEN.split(":")
            token_str: Optional[str] = f"{token_id}:{'*' * len(token_secret)}"
        else:
            token_str = settings.WAND_TOKEN
        table.add_row("WAND_TOKEN", token_str)
        return table


class SourceFormatter:
    def __call__(self, source: Source) -> RenderableType:
        table = Table(
            box=None,
            show_header=False,
            show_edge=False,
        )
        table.add_column()
        table.add_column(style="bold")
        table.add_row("Id", source.id)
        return table


class ModelFormatter:
    def __call__(self, model: Model) -> RenderableType:
        table = Table(
            box=None,
            show_header=False,
            show_edge=False,
        )
        table.add_column()
        table.add_column(style="bold")
        table.add_row("Id", model.id)
        table.add_row("Source Ids", ", ".join(model.source_ids))
        table.add_row("Progress", str(model.status.progress))
        table.add_row("Training completed", str(model.status.training_completed))
        return table


class ModelsFormatter:
    def _model_to_table_row(self, model: Model) -> Sequence[str]:
        line = [
            model.id,
            str(model.status.progress),
            str(model.status.training_completed),
        ]
        return line

    def __call__(self, disks: Sequence[Model]) -> RenderableType:
        disks = sorted(disks, key=operator.attrgetter("id"))
        table = Table(box=box.SIMPLE_HEAVY)
        # make sure that the first column is fully expanded
        width = len("1ce961e5172a688b842d")
        table.add_column("Id", style="bold", width=width)
        table.add_column("Progress")
        table.add_column("Training Completed")
        for disk in disks:
            table.add_row(*self._model_to_table_row(disk))
        return table
