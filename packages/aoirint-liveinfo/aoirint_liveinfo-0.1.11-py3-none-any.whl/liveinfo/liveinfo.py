from urllib.parse import urlparse
from typing import Optional, Literal, Union

from . import __VERSION__
from . import nicolive
from . import ytlive

"""
  Public APIs
"""


default_application_useragent = \
  f'live_info_api_client_py/{__VERSION__} ' \
  '(+https://github.com/aoirint/live_info_api_client_py)'

default_useragent = 'facebookexternalhit/1.1;Googlebot/2.1' \
            f';{default_application_useragent}'


class GetLiveProgramError(Exception):
  pass


def get_live_program(
  live_id_or_url: str,
  service: Optional[str],
  ytlive_api_key: Optional[str],
  useragent: str = default_useragent,
) -> Union[
  nicolive.GetNicoliveProgramNicoliveProgramData,
  ytlive.GetYtliveProgramsSuccessYtliveProgramsData,
]:
  if service is None:
    service = guess_service(live_id_or_url=live_id_or_url)

  if service is None:
    raise GetLiveProgramError(
      'Service not specified and auto selection failed. '
      'Specify an argument: --service=[nicolive]'
    )

  if service == 'nicolive':
    nicolive_program_result = \
      nicolive.get_nicolive_program(
        live_id_or_url=live_id_or_url,
        useragent=useragent,
      )

    if nicolive_program_result.result_type == 'success':
      if nicolive_program_result.data_type == 'nicolive_program':
        return nicolive_program_result.data
      else:
        raise GetLiveProgramError(nicolive_program_result)
    else:
      raise GetLiveProgramError(nicolive_program_result)

  elif service == 'ytlive':
    assert ytlive_api_key is not None, 'ytlive_api_key is required'

    ytlive_programs_result = \
      ytlive.get_ytlive_programs(
        channel_id=live_id_or_url,
        useragent=useragent,
        api_key=ytlive_api_key,
      )

    if ytlive_programs_result.result_type == 'success':
      if ytlive_programs_result.data_type == 'ytlive_programs':
        return ytlive_programs_result.data
      else:
        raise GetLiveProgramError(ytlive_programs_result)
    else:
      raise GetLiveProgramError(ytlive_programs_result)

  else:
    raise GetLiveProgramError(f'Unknown service: {service}')


def guess_service(live_id_or_url: str) -> Optional[Literal['nicolive']]:
  urlp = urlparse(live_id_or_url)

  if urlp.scheme == 'https' and \
     urlp.hostname == 'live.nicovideo.jp':
      return 'nicolive'

  return None
