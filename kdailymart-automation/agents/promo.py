"""promo-agent

역할: 카드뉴스/인포그래픽 등 특정 포맷에 한정하지 않고, 상품/채널에 맞는 홍보 콘텐츠를 제작
입력: 상품 정보, 이미지(image-agent)
출력: 홍보 콘텐츠 세트 (포맷 자유 - 콘텐츠 타입은 distribution-planner가 배정할 채널에 맞춰 결정)
반려 조건: 없음

파이프라인 순서: 6단계 (distribution-planner와 병렬 실행).

포맷은 카드뉴스/인포그래픽으로 제한하지 않는다. 채널 특성에 맞게 숏폼 영상 스크립트,
릴스/틱톡용 콘티, 캡션 단독형 등 무엇이든 가능하며, ContentFormat은 새 포맷 추가 시
Literal에 값을 더하는 방식으로 확장한다 (임의 문자열을 허용하면 오타가 나도 걸러지지 않으므로
채널 담당자가 실제 쓰는 포맷만 명시적으로 추가하는 편이 안전하다).
"""

from dataclasses import dataclass
from typing import Literal

from image import ProcessedImageSet
from listing import ListingResult
from localization import LocalizedCopy

ContentFormat = Literal[
    "card_news", "infographic", "short_caption",
    "short_form_video_script", "reels_storyboard", "single_image_post",
]


@dataclass
class PromoContent:
    listing: ListingResult
    content_format: ContentFormat
    asset_path: str
    caption: str


def generate_promo_set(copy: LocalizedCopy, images: ProcessedImageSet, listing: ListingResult) -> list[PromoContent]:
    """등록 완료된 상품에 대해 채널에 맞는 홍보 콘텐츠 세트(포맷 무관)를 생성한다.

    TODO(실행 전 필요 사항):
    - 콘텐츠 생성 도구 선택: 이미지 편집/디자인 자동화 API(예: Canva API) vs
      코드 기반 렌더링(예: HTML/CSS -> 이미지 캡처) vs AI 이미지/영상 생성 중 방식 결정.
      포맷(카드뉴스/인포그래픽/숏폼 등)별로 도구가 다를 수 있으므로 ContentFormat -> 도구 매핑 필요
    - 템플릿(브랜드 톤, 로고, 색상 가이드, 숏폼 스크립트 톤) 확정
    - 생성물 저장 위치 규칙 (outputs/promo/<date>/<sku>/<content_format>/ 등) 및 파일명 규칙
    - listing.ListingResult가 "live" 상태가 아닌 경우(publish_failed) 홍보 콘텐츠를
      생성하지 않도록 하는 가드 로직
    - 어떤 국가/채널에 어떤 포맷을 우선 배정할지는 distribution.py의 채널 전략과 맞물리므로,
      이 함수가 국가/채널 정보를 받아 포맷을 선택하게 할지, distribution-planner가 사후에
      포맷을 걸러낼지 역할 분리를 결정
    """
    raise NotImplementedError("promo-agent: 홍보 콘텐츠 생성 로직 미구현 (도구/템플릿 미결정).")
