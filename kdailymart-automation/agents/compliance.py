"""compliance-agent

역할: 국가별 금지/규제 카테고리 필터 (rulebook/country_rules.json 대조)
입력: 후보 리스트(sourcing-agent 출력), 판매국
출력: 승인/반려 + 사유
반려 조건: HSA/NEA/Safety Mark/CCP/할랄/NPRA 등 국가별 규제 저촉

파이프라인 순서: 2단계. 탈락분은 sourcing-agent로 반송하여 대체 후보를 요청한다.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sourcing import SourcingCandidate

Country = Literal["SG", "MY"]

RULEBOOK_PATH = Path(__file__).resolve().parent.parent / "rulebook" / "country_rules.json"


@dataclass
class ComplianceResult:
    candidate: SourcingCandidate
    approved: bool
    reason: str
    matched_rule_key: str | None = None


def load_country_rules(path: Path = RULEBOOK_PATH) -> dict:
    """rulebook/country_rules.json을 로드한다. (이 함수 자체는 실행 가능하지만, 아래 판정 로직은 미구현)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_candidate(candidate: SourcingCandidate, country: Country, rules: dict) -> ComplianceResult:
    """후보 상품 하나를 국가별 규제와 대조하여 승인/반려를 판정한다.

    TODO(실행 전 필요 사항):
    - candidate.category_hint(자유 텍스트/사이트 카테고리)를 country_rules.json의
      restricted_categories.key / category_master.json 카테고리 트리로 매핑하는 분류기 필요
      (단순 문자열 매칭으로는 부족 - 예: "마스크팩" -> health_beauty, "할랄 미인증 스낵" -> food_beverage_non_halal)
    - MY 할랄 인증 여부 판정 로직: 상품 이미지/상세정보에서 할랄 인증 마크(JAKIM) 존재 여부를
      사람이 확인할지, 이미지 인식으로 자동 판별할지 결정 필요
    - country_rules.json 자체가 draft이므로, 카테고리가 늘어날 때마다 규제 항목을 계속 보강해야 함
    - 반려 시 sourcing-agent.request_replacement_candidate로 넘길 표준 사유 포맷 확정
    """
    raise NotImplementedError("compliance-agent: 카테고리 분류 및 규제 대조 로직 미구현.")


def filter_candidates(candidates: list[SourcingCandidate], country: Country) -> list[ComplianceResult]:
    """후보 리스트 전체를 국가별로 필터링한다."""
    rules = load_country_rules()
    return [check_candidate(c, country, rules) for c in candidates]
