"""sourcing-agent

역할: 도매꾹/쿠팡/네이버에서 트렌드 + 실물 확인된 인기 상품 10개 후보를 산출한다.
입력: 카테고리 화이트리스트(rulebook/country_rules.json의 safe_categories), 최근 판매 트렌드
출력: 후보 리스트 (상품명, 실제 소싱가, 이미지 URL, 실존 확인 스크린샷)
반려 조건: 실물 미확인 상품 (운영 룰북 v2 마스터 원칙 #4 - 상상으로 상품을 만들지 않는다)

파이프라인 순서: 1단계. compliance-agent에게 후보 리스트를 전달한다.
"""

from dataclasses import dataclass, field
from typing import Literal

Country = Literal["SG", "MY"]


@dataclass
class SourcingCandidate:
    product_name: str
    source_site: Literal["domeggook", "coupang", "naver"]
    source_url: str
    source_price_krw: int
    image_urls: list[str]
    existence_proof_screenshot_path: str
    category_hint: str
    country: Country


POPULARITY_SIGNALS = {
    "coupang": ["판매량 배지(로켓배송/베스트)", "리뷰 수", "평점", "순위(카테고리 랭킹 100위 이내)"],
    "naver": ["구매건수", "리뷰 수", "네이버쇼핑 랭킹순 노출 순위"],
    "domeggook": ["최근 거래건수(실질 사입 지표)", "미노출(도매 특성상 판매량 배지가 약함 -> 쿠팡/네이버 교차검증 필수)"],
}
"""
인기도 판단 기준. 도매꾹은 도매 사이트 특성상 판매량 지표가 약하므로, 도매꾹에서 소싱처(원가)를
찾은 뒤 동일/유사 상품이 쿠팡·네이버에서 실제로 잘 팔리는지 교차검증하는 2단계 방식을 기본으로 한다:
(1) 쿠팡/네이버에서 카테고리 화이트리스트 내 상위 랭킹 상품 스캔 -> 인기 상품 후보 확정
(2) 그 상품과 동일/유사한 실물을 도매꾹에서 원가 소싱 -> 실물 확인 스크린샷 확보
순서를 반대로 하면(도매꾹 먼저 훑기) "안 팔리는데 소싱만 가능한" 상품이 섞여 들어갈 위험이 크다.
"""


def fetch_candidates(country: Country, category_whitelist: list[str], count: int = 10) -> list[SourcingCandidate]:
    """국가별 카테고리 화이트리스트 내에서 실물이 확인된 인기 상품 후보를 count개 만큼 수집한다.
    category_whitelist는 rulebook/country_rules.json의 safe_categories 또는
    expansion_policy 절차를 거쳐 확정된 unrestricted 카테고리 목록에서 가져온다.

    TODO(실행 전 필요 사항):
    - 도매꾹/쿠팡/네이버 각 사이트의 접근 방식 확정 (공식 API 유무 확인, 없으면 브라우저 자동화 or 스크래핑 방식 결정)
    - 각 사이트 로그인/세션 크리덴셜 (도매꾹 계정 등) 확보 및 안전한 저장 방식(secrets manager) 결정
    - 각 사이트 이용약관/robots.txt 상 스크래핑 허용 여부 확인
    - "실존 확인 스크린샷" 저장 로직 및 저장 위치 (예: data/candidates/<date>/screenshots/) 확정
    - POPULARITY_SIGNALS에 정리된 지표를 실제 점수화하는 랭킹 함수 구현 (예: 리뷰수*가중치 + 판매배지 가점)
      및 사이트별 지표를 하나의 비교 가능한 점수로 정규화하는 방법 결정
    - 소싱가 파싱 시 단위(개당/세트당) 오인식 방지 로직 (Day 1 실수 이력: 집게핀 소싱가 4배 오추정)
    """
    raise NotImplementedError("sourcing-agent: 실행 전 위 TODO 항목을 먼저 확정해야 합니다.")


def request_replacement_candidate(rejected: SourcingCandidate, reject_reason: str) -> SourcingCandidate:
    """compliance-agent 또는 margin-agent에서 반려된 후보 대신 대체 후보 1건을 재수집한다.

    TODO: 반려 사유(reject_reason)를 다음 검색에서 어떻게 필터 조건으로 반영할지 로직 필요.
    """
    raise NotImplementedError("sourcing-agent: 대체 후보 수집 로직 미구현.")
