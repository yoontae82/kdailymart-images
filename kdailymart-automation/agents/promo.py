"""promo-agent

역할: 카드뉴스/인포그래픽/기타 포맷 홍보 콘텐츠 제작
입력: 상품 정보, 이미지(image-agent)
출력: 홍보 콘텐츠 세트
반려 조건: 없음

파이프라인 순서: 6단계 (distribution-planner와 병렬 실행).
"""

from dataclasses import dataclass
from typing import Literal

from image import ProcessedImageSet
from listing import ListingResult
from localization import LocalizedCopy

ContentFormat = Literal["card_news", "infographic", "short_caption"]


@dataclass
class PromoContent:
    listing: ListingResult
    content_format: ContentFormat
    asset_path: str
    caption: str


def generate_promo_set(copy: LocalizedCopy, images: ProcessedImageSet, listing: ListingResult) -> list[PromoContent]:
    """등록 완료된 상품에 대해 카드뉴스/인포그래픽 등 홍보 콘텐츠 세트를 생성한다.

    TODO(실행 전 필요 사항):
    - 콘텐츠 생성 도구 선택: 이미지 편집/디자인 자동화 API(예: Canva API) vs
      코드 기반 렌더링(예: HTML/CSS -> 이미지 캡처) vs AI 이미지 생성 중 방식 결정
    - 카드뉴스/인포그래픽 템플릿(브랜드 톤, 로고, 색상 가이드) 확정
    - 생성물 저장 위치 규칙 (outputs/promo/<date>/<sku>/ 등) 및 파일명 규칙
    - listing.ListingResult가 "live" 상태가 아닌 경우(publish_failed) 홍보 콘텐츠를
      생성하지 않도록 하는 가드 로직
    """
    raise NotImplementedError("promo-agent: 홍보 콘텐츠 생성 로직 미구현 (도구/템플릿 미결정).")
