import requests
from bs4 import BeautifulSoup, Tag
import json
from dataclasses import dataclass
from typing import Literal, Optional, Union, List
import re
from urllib.parse import urlparse


"""
  Public APIs
"""


@dataclass
class GetNicoliveProgramNicoliveProgramData:
  name: Optional[str]
  description: Optional[str]
  url: Optional[str]
  thumbnail_url: Optional[List[str]]
  start_date: Optional[str]  # ISO8601 timezone-aware datetime string
  end_date: Optional[str]  # ISO8601 timezone-aware datetime string


@dataclass
class GetNicoliveProgramSuccessNicoliveProgramResult:
  result_type: Literal['success']
  data_type: Literal['nicolive_program']
  data: GetNicoliveProgramNicoliveProgramData


@dataclass
class GetNicoliveProgramInvalidLiveIdOrUrlResult:
  result_type: Literal['invalid_live_id_or_url']


@dataclass
class GetNicoliveProgramNotFoundResult:
  result_type: Literal['not_found']


@dataclass
class GetNicoliveProgramMaintenanceResult:
  result_type: Literal['maintenance']


@dataclass
class GetNicoliveProgramUnknownErrorResult:
  result_type: Literal['unknown_error']


GetNicoliveProgramResult = Union[
  GetNicoliveProgramSuccessNicoliveProgramResult,
  GetNicoliveProgramInvalidLiveIdOrUrlResult,
  GetNicoliveProgramNotFoundResult,
  GetNicoliveProgramMaintenanceResult,
  GetNicoliveProgramUnknownErrorResult,
]


def get_nicolive_program(
  live_id_or_url: str,
  useragent: str,
) -> GetNicoliveProgramResult:
  nicolive_watch_result = fetch_nicolive_watch(
    live_id_or_url=live_id_or_url,
    useragent=useragent,
  )

  if nicolive_watch_result.result_type == 'success':
    if nicolive_watch_result.data_type == 'html':
      html = nicolive_watch_result.data.html

      name: Optional[str] = None
      description: Optional[str] = None
      url: Optional[str] = None
      thumbnail_url: Optional[List[str]] = None

      # start_date, end_date
      #   ISO8601 timezone-aware datetime string
      start_date: Optional[str] = None
      end_date: Optional[str] = None

      ogp_result = parse_ogp_in_nicolive_watch_html(html=html)
      if ogp_result.result_type == 'success':
        if ogp_result.data_type == 'ogp':
          ogp_data = ogp_result.data

          url = ogp_data.url

      json_ld_result = parse_json_ld_in_nicolive_watch_html(html=html)
      if json_ld_result.result_type == 'success':
        if json_ld_result.data_type == 'json_ld':
          json_ld_data = json_ld_result.data

          name = json_ld_data.name
          description = json_ld_data.description
          thumbnail_url = json_ld_data.thumbnail_url
          start_date = json_ld_data.start_date
          end_date = json_ld_data.end_date

      return GetNicoliveProgramSuccessNicoliveProgramResult(
        result_type='success',
        data_type='nicolive_program',
        data=GetNicoliveProgramNicoliveProgramData(
          name=name,
          description=description,
          url=url,
          thumbnail_url=thumbnail_url,
          start_date=start_date,
          end_date=end_date,
        )
      )

  elif nicolive_watch_result.result_type == 'invalid_live_id_or_url':
    return GetNicoliveProgramInvalidLiveIdOrUrlResult(
      result_type='invalid_live_id_or_url',
    )

  elif nicolive_watch_result.result_type == 'not_found':
    return GetNicoliveProgramNotFoundResult(
      result_type='not_found',
    )

  elif nicolive_watch_result.result_type == 'maintenance':
    return GetNicoliveProgramMaintenanceResult(
      result_type='maintenance',
    )

  return GetNicoliveProgramUnknownErrorResult(
    result_type='unknown_error',
  )


"""
  Private API: Fetch a watch page HTML
  https://live.nicovideo.jp/watch/{live_id}
"""


@dataclass
class FetchNicoliveWatchSuccessHtmlData:
  html: str


@dataclass
class FetchNicoliveWatchSuccessHtmlResult:
  result_type: Literal['success']
  data_type: Literal['html']
  data: FetchNicoliveWatchSuccessHtmlData


@dataclass
class FetchNicoliveWatchInvalidLiveIdOrUrlResult:
  result_type: Literal['invalid_live_id_or_url']


@dataclass
class FetchNicoliveWatchNotFoundResult:
  result_type: Literal['not_found']


@dataclass
class FetchNicoliveWatchMaintenanceResult:
  result_type: Literal['maintenance']


@dataclass
class FetchNicoliveWatchUnknownResult:
  result_type: Literal['unknown']


FetchNicoliveWatchResult = Union[
  FetchNicoliveWatchSuccessHtmlResult,
  FetchNicoliveWatchInvalidLiveIdOrUrlResult,
  FetchNicoliveWatchNotFoundResult,
  FetchNicoliveWatchMaintenanceResult,
  FetchNicoliveWatchUnknownResult,
]


def validate_live_id(live_id: str) -> bool:
  live_id_patterns = [
    r'lv\d+',
    r'user\/\d+',
    r'co\d+',
    r'ch\d+',
  ]

  for pattern in live_id_patterns:
    if re.fullmatch(pattern, live_id):
      return True

  return False


def validate_live_url_and_get_safe_live_id(live_url: str) -> Optional[str]:
  urlp = urlparse(live_url)

  if urlp.scheme == 'https' and \
      urlp.hostname == 'live.nicovideo.jp' and \
      urlp.path.startswith('/watch/'):
    live_id = urlp.path[7:]  # cut "/watch/"
    if validate_live_id(live_id=live_id):
      return live_id

  return None


def fetch_nicolive_watch(
  live_id_or_url: str,
  useragent: str,
) -> FetchNicoliveWatchResult:
  # validate live_id
  safe_live_id = None

  is_live_id = False
  if validate_live_id(live_id=live_id_or_url):
    is_live_id = True
    safe_live_id = live_id_or_url

  is_live_url = False
  if not is_live_id:
    result = validate_live_url_and_get_safe_live_id(live_url=live_id_or_url)
    if result is not None:
      is_live_url = True
      safe_live_id = result

  if not is_live_id and not is_live_url:
    return FetchNicoliveWatchInvalidLiveIdOrUrlResult(
      result_type='invalid_live_id_or_url',
    )

  assert safe_live_id is not None

  headers = {
    'User-Agent': useragent,
  }

  res = requests.get(
    f'https://live.nicovideo.jp/watch/{safe_live_id}',
    headers=headers,
  )
  status_code = res.status_code
  if status_code == 200:
    html = res.text

    return FetchNicoliveWatchSuccessHtmlResult(
      result_type='success',
      data_type='html',
      data=FetchNicoliveWatchSuccessHtmlData(
        html=html,
      ),
    )

  elif status_code == 404:
    return FetchNicoliveWatchNotFoundResult(
      result_type='not_found',
    )

  elif status_code == 500:
    return FetchNicoliveWatchMaintenanceResult(
      result_type='maintenance',
    )

  return FetchNicoliveWatchUnknownResult(
    result_type='unknown',
  )


"""
  Private API: Parse a live url in a watch page HTML
  https://live.nicovideo.jp/watch/{live_id}
"""


@dataclass
class ParseOgpInNicoliveWatchHtmlSuccessOgpData:
  url: Optional[str]


@dataclass
class ParseOgpInNicoliveWatchHtmlSuccessOgpResult:
  result_type: Literal['success']
  data_type: Literal['ogp']
  data: ParseOgpInNicoliveWatchHtmlSuccessOgpData


@dataclass
class ParseOgpInNicoliveWatchHtmlUnknownErrorResult:
  result_type: Literal['unknown_error']


ParseOgpInNicoliveWatchHtmlResult = Union[
  ParseOgpInNicoliveWatchHtmlSuccessOgpResult,
  ParseOgpInNicoliveWatchHtmlUnknownErrorResult,
]


def parse_ogp_in_nicolive_watch_html(
  html: str,
) -> ParseOgpInNicoliveWatchHtmlResult:
  bs = BeautifulSoup(html, 'html5lib')

  og_url_tag = bs.find('meta', attrs={'property': 'og:url', 'content': True})
  url = og_url_tag['content'] if isinstance(og_url_tag, Tag) else None
  if isinstance(url, list):
    url = url[0]

  return ParseOgpInNicoliveWatchHtmlSuccessOgpResult(
    result_type='success',
    data_type='ogp',
    data=ParseOgpInNicoliveWatchHtmlSuccessOgpData(
      url=url,
    ),
  )


"""
  Private API: Parse a json-ld in a watch page HTML
  https://live.nicovideo.jp/watch/{live_id}
"""


@dataclass
class ParseJsonLdInNicoliveWatchHtmlSuccessJsonLdData:
  name: Optional[str]
  description: Optional[str]
  thumbnail_url: Optional[List[str]]
  start_date: Optional[str]  # ISO8601 timezone-aware datetime string
  end_date: Optional[str]  # ISO8601 timezone-aware datetime string


@dataclass
class ParseJsonLdInNicoliveWatchHtmlSuccessJsonLdResult:
  result_type: Literal['success']
  data_type: Literal['json_ld']
  data: ParseJsonLdInNicoliveWatchHtmlSuccessJsonLdData


@dataclass
class ParseJsonLdInNicoliveWatchHtmlNotFoundResult:
  result_type: Literal['not_found']


@dataclass
class ParseJsonLdInNicoliveWatchHtmlUnknownErrorResult:
  result_type: Literal['unknown_error']


ParseJsonLdInNicoliveWatchHtmlResult = Union[
  ParseJsonLdInNicoliveWatchHtmlSuccessJsonLdResult,
  ParseJsonLdInNicoliveWatchHtmlNotFoundResult,
  ParseJsonLdInNicoliveWatchHtmlUnknownErrorResult,
]


def parse_json_ld_in_nicolive_watch_html(
  html: str,
) -> ParseJsonLdInNicoliveWatchHtmlResult:
  bs = BeautifulSoup(html, 'html5lib')

  json_ld_tag = bs.find('script', attrs={'type': 'application/ld+json'})
  if not isinstance(json_ld_tag, Tag):
    return ParseJsonLdInNicoliveWatchHtmlNotFoundResult(
      result_type='not_found',
    )

  json_ld_text = json_ld_tag.string
  if json_ld_text is None:
    return ParseJsonLdInNicoliveWatchHtmlNotFoundResult(
      result_type='not_found',
    )

  json_ld_data = json.loads(json_ld_text)

  name = json_ld_data.get('name')
  description = json_ld_data.get('description')
  thumbnail_url = json_ld_data.get('thumbnailUrl', [])

  publication = json_ld_data.get('publication', {})

  # start_date, end_date
  #   ISO8601 timezone-aware datetime string
  start_date = publication.get('startDate')
  end_date = publication.get('endDate')

  return ParseJsonLdInNicoliveWatchHtmlSuccessJsonLdResult(
    result_type='success',
    data_type='json_ld',
    data=ParseJsonLdInNicoliveWatchHtmlSuccessJsonLdData(
      name=name,
      description=description,
      thumbnail_url=thumbnail_url,
      start_date=start_date,
      end_date=end_date,
    )
  )
