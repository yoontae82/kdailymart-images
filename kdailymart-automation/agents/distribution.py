"""distribution-planner

역할: 국가별 홍보 채널 배정
입력: 콘텐츠(promo-agent), 판매국
출력: 게시 스케줄
반려 조건: 없음

파이프라인 순서: 6단계 (promo-agent와 병렬 실행).

국가별 채널 매칭 (설계서 3번 섹션):
- SG: Threads/IG Reels, Facebook Marketplace 그룹, TikTok SG (영어, 기존 Threads 운영 노하우 재사용)
- MY: TikTok MY, Facebook 그룹(MY 로컬), Instagram (말레이어/영어 혼용, 말레이어 카피는 로컬 톤 검수 필요)

신규국가 확장 시 채널 선정 공통 원칙 (SG/MY 다음에 열리는 국가에 적용):
그 국가에 채널 운영 노하우가 아직 없으므로, 아래 3개 유형에서 하나씩 우선 채택한 뒤
현지 실제 사용률 데이터로 교체하는 방식을 기본값으로 한다.
1. 숏폼 영상형 채널 (TikTok 계열 - 국가별 앱이 다를 수 있음, 예: 베트남은 TikTok 대신
   Zalo 등 로컬 앱 비중이 높을 수 있으니 진출 전 확인)
2. 로컬 커뮤니티형 채널 (Facebook 그룹 - 대체로 동남아 전역에서 유효하나 그룹 활성도는
   국가별로 다름)
3. 비주얼 채널 (Instagram/Threads류)
CHANNEL_MATRIX에 신규국가를 추가할 때는 이 3유형 중 그 국가에서 실제로 쓰이는 앱으로
치환해서 채워 넣는다. 빈 채널 리스트로 두면 assign_channels가 배정할 곳이 없으므로,
최소 1개 채널은 확정된 뒤에 국가를 추가한다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from promo import PromoContent

Country = Literal["SG", "MY"]
Channel = Literal["threads", "ig_reels", "facebook_marketplace_group", "tiktok", "facebook_local_group", "instagram"]

CHANNEL_MATRIX: dict[Country, list[Channel]] = {
    "SG": ["threads", "ig_reels", "facebook_marketplace_group", "tiktok"],
    "MY": ["tiktok", "facebook_local_group", "instagram"],
}
"""
신규국가를 추가할 때: (1) Channel Literal에 그 국가에서 쓰는 채널 값을 추가하고,
(2) 위 "신규국가 확장 시 채널 선정 공통 원칙" 3유형에 맞춰 최소 1개씩 채운 뒤,
(3) CHANNEL_MATRIX에 항목을 더한다. 국가 코드만 추가하고 채널 리스트를 비워두지 않는다.
"""


@dataclass
class ScheduledPost:
    content: PromoContent
    country: Country
    channel: Channel
    scheduled_at: datetime


def assign_channels(contents: list[PromoContent], country: Country) -> list[ScheduledPost]:
    """국가별 채널 매트릭스(CHANNEL_MATRIX)에 따라 홍보 콘텐츠를 채널/시간에 배정한다.

    TODO(실행 전 필요 사항):
    - 각 채널의 게시 자동화 방식 결정: 공식 API(Threads API, Meta Graph API, TikTok API 등) 사용 가능
      범위 확인 vs 브라우저 자동화 vs 수동 게시 보조(초안만 생성) 중 어디까지 자동화할지 결정
    - 각 채널별 API 크리덴셜/앱 등록 및 각 플랫폼의 자동 게시 정책(스팸/도배 방지 정책) 준수 확인
    - 국가별 게시 스케줄 시간대(SGT/MYT) 및 요일별 배포 빈도 정책
    - MY 말레이어 콘텐츠는 게시 전 로컬 톤 검수(localization-agent.request_local_review) 통과 여부를
      게이트 조건으로 걸어야 함
    """
    raise NotImplementedError("distribution-planner: 채널 배정/스케줄링 로직 미구현.")


def publish_scheduled_posts(posts: list[ScheduledPost]) -> None:
    """예정된 게시물을 실제로 각 채널에 발행한다.

    TODO: 채널별 자동 게시 연동이 완료되기 전까지는 이 함수를 호출하지 않는다.
    """
    raise NotImplementedError("distribution-planner: 채널별 게시 자동화 미구현 (API 크리덴셜 필요).")
