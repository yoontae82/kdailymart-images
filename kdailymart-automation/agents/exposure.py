"""exposure-agent (개발팀 - 노출 모니터링 역할)

역할: 등록된 상품이 쇼피 검색/카테고리에서 잘 노출되는지 주기적으로 점검하고,
노출이 저조하면 원인 후보를 산출해 기획팀(sourcing)/홍보팀(promo, distribution)에 전달한다.
입력: listing-agent가 발급한 Item ID/상태, 판매국
출력: 노출 리포트(지표 + 저조 여부) + 원인 후보 목록
반려 조건: 없음 (경고/후속조치 트리거만 발생시킨다 - 상품을 반려하지는 않음)

파이프라인 순서: listing 완료 후 상시 실행 (일일 등록 파이프라인과는 별도 트랙).
master-qa-agent가 이 리포트를 함께 총괄 감시하며, 저조 상태가 지속되면 재작업 큐에 올린다.
"""

from dataclasses import dataclass
from datetime import date
from typing import Literal

from listing import ListingResult

Country = Literal["SG", "MY"]

REMEDIATION_CANDIDATES = [
    "keyword_optimization",       # 상품명/태그에 검색 키워드가 부족한 경우
    "price_competitiveness",      # 동일 카테고리 경쟁 상품 대비 가격 경쟁력 부족
    "image_quality",              # 이미지가 실물과 매칭되지 않거나 품질이 낮은 경우
    "insufficient_reviews",       # 초기 리뷰/판매 이력 부족으로 랭킹 노출이 밀리는 경우
    "category_or_attribute_mismatch",  # 카테고리/속성 선택이 검색 의도와 안 맞는 경우
]
"""
저조 원인 후보 목록. 실제로는 이 중 하나로 단정하기 어려운 경우가 많아, 자동 판정보다는
'가능성이 높은 순서로 리스트업 → 기획팀/홍보팀이 검토'하는 방식을 기본으로 한다.
"""


@dataclass
class ExposureReport:
    listing: ListingResult
    country: Country
    checked_on: date
    impressions: int | None
    clicks: int | None
    search_rank_estimate: int | None
    is_underexposed: bool
    likely_causes: list[str]


def check_exposure(listing: ListingResult, country: Country) -> ExposureReport:
    """등록된 상품의 노출 지표를 조회하고 저조 여부를 판정한다.

    TODO(실행 전 필요 사항):
    - 쇼피 셀러센터의 노출/트래픽 통계를 어디서 가져올지 결정: 셀러센터 대시보드 브라우저 자동화로
      스크래핑할지, 쇼피 Open API에 관련 통계 엔드포인트가 있는지 확인
    - "저조"를 판정하는 구체적 임계치 필요 (예: 등록 후 N일 경과했는데 노출수가 카테고리 평균 대비
      몇 % 미만이면 저조로 볼지) - 데이터가 쌓이기 전까지는 임의 기준으로 시작해야 함
    - 신상품은 원래 초기 노출이 낮을 수 있으므로, "등록 후 며칠까지는 판정 보류" 기간 설정 필요
    """
    raise NotImplementedError("exposure-agent: 노출 조회 로직 미구현 (통계 접근 방식 미결정).")


def suggest_remediation(report: ExposureReport) -> list[str]:
    """저조한 상품에 대해 REMEDIATION_CANDIDATES 중 가능성 높은 원인을 우선순위로 정리해 반환한다.
    이 결과는 sourcing-agent(대체 상품 검토), promo/distribution-agent(홍보 강화)에 전달된다.

    TODO(실행 전 필요 사항):
    - 원인 후보를 어떤 근거로 우선순위화할지 (예: 이미지 품질은 image-agent 로그의
      copyright_cleared/생성 방식과 연동, 가격 경쟁력은 margin-agent의 국가별 시세 데이터 필요)
    - 원인 후보가 여러 개 겹칠 때 기획팀/홍보팀 중 누구에게 먼저 넘길지 우선순위 규칙
    """
    raise NotImplementedError("exposure-agent: 원인 후보 산출 로직 미구현.")
