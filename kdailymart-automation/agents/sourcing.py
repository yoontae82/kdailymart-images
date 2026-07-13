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


def fetch_candidates(country: Country, category_whitelist: list[str], count: int = 10) -> list[SourcingCandidate]:
    """국가별 안전 카테고리 내에서 실물이 확인된 인기 상품 후보를 count개 만큼 수집한다.

    TODO(실행 전 필요 사항):
    - 도매꾹/쿠팡/네이버 각 사이트의 접근 방식 확정 (공식 API 유무 확인, 없으면 브라우저 자동화 or 스크래핑 방식 결정)
    - 각 사이트 로그인/세션 크리덴셜 (도매꾹 계정 등) 확보 및 안전한 저장 방식(secrets manager) 결정
    - 각 사이트 이용약관/robots.txt 상 스크래핑 허용 여부 확인
    - "실존 확인 스크린샷" 저장 로직 및 저장 위치 (예: data/candidates/<date>/screenshots/) 확정
    - 트렌드 판단 기준 데이터 소스 확정 (판매량/리뷰수 등 어떤 지표를 쓸지)
    - 소싱가 파싱 시 단위(개당/세트당) 오인식 방지 로직 (Day 1 실수 이력: 집게핀 소싱가 4배 오추정)
    """
    raise NotImplementedError("sourcing-agent: 실행 전 위 TODO 항목을 먼저 확정해야 합니다.")


def request_replacement_candidate(rejected: SourcingCandidate, reject_reason: str) -> SourcingCandidate:
    """compliance-agent 또는 margin-agent에서 반려된 후보 대신 대체 후보 1건을 재수집한다.

    TODO: 반려 사유(reject_reason)를 다음 검색에서 어떻게 필터 조건으로 반영할지 로직 필요.
    """
    raise NotImplementedError("sourcing-agent: 대체 후보 수집 로직 미구현.")
