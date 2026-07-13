"""distribution-planner

역할: 국가별 홍보 채널 배정
입력: 콘텐츠(promo-agent), 판매국
출력: 게시 스케줄
반려 조건: 없음

파이프라인 순서: 6단계 (promo-agent와 병렬 실행).

국가별 채널 매칭 (설계서 3번 섹션):
- SG: Threads/IG Reels, Facebook Marketplace 그룹, TikTok SG (영어, 기존 Threads 운영 노하우 재사용)
- MY: TikTok MY, Facebook 그룹(MY 로컬), Instagram (말레이어/영어 혼용, 말레이어 카피는 로컬 톤 검수 필요)
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
