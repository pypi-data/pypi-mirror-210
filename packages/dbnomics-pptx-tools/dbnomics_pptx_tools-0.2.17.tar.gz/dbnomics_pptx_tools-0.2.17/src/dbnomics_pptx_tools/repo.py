import daiquiri
import pandas as pd
from dbnomics import fetch_series
from pandas import DataFrame

from dbnomics_pptx_tools.cache import SeriesCache

logger = daiquiri.getLogger(__name__)


class SeriesRepo:
    def __init__(self, *, auto_fetch: bool = True, cache: SeriesCache, force: bool = False):
        self._auto_fetch = auto_fetch
        self._cache = cache
        self._force = force

    def load(self, series_id: str) -> DataFrame:
        series_df = self._cache.get(series_id)
        if series_df is not None and not self._force:
            return series_df
        if not self._auto_fetch:
            raise SeriesLoadError(repo=self, series_id=series_id)
        series_df = self._fetch_series_df(series_id)
        self._cache.set(series_id, series_df)
        logger.debug("Series %r was fetched from DBnomics API and added to the cache", series_id)
        return series_df

    def load_many(self, series_ids: list[str]) -> DataFrame:
        return pd.concat([self.load(series_id) for series_id in series_ids])

    def _add_series_id_column(self, df: DataFrame) -> DataFrame:
        return df.assign(series_id=lambda row: row.provider_code + "/" + row.dataset_code + "/" + row.series_code)

    def _fetch_series_df(self, series_id: str) -> DataFrame:
        logger.debug("Fetching series %r from DBnomics API...", series_id)
        df: DataFrame = fetch_series(series_ids=[series_id])
        if df.empty:
            return df
        df = self._add_series_id_column(df)
        return df


class SeriesLoadError(Exception):
    def __init__(self, *, repo: SeriesRepo, series_id: str):
        message = f"Series {series_id!r} could not be loaded."
        super().__init__(message)
        self.repo = repo
        self.series_id = series_id
