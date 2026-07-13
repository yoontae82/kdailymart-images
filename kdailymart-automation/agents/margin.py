"""margin-agent

역할: 마진계산기 로직으로 스크리닝
입력: 소싱가, 국가별 수수료 가정(rulebook/country_rules.json의 fee_assumptions)
출력: 마진율, 승인/반려
반려 조건: 순마진 20% 미만 (Adjustment Rate 조정 후 재시도 1회, 그래도 미달이면 탈락)

파이프라인 순서: 3단계.

핵심 전제 (운영 룰북 v2 Day 1 발견 사항):
Global SKU Price = 원가(상품원가+운영비+국내배송비)만 입력한다. 판매가가 아니다.
쇼피가 Global SKU Price에 Commission + Transaction fee(2%) + Cross-border shipping cost를
자동으로 얹어 실제 노출 판매가를 만든다. 마진을 조정하는 레버는
Market Price Adjustment Rate (100% = 마진 0%, 130% = 마진 30%) 이며,
SLS 국제배송비 등을 Global SKU Price에 직접 넣으면 이중가산되어 실제 노출가가 왜곡된다
(Day 1 실수 사례: 판매가 역산값을 넣어 노출가가 의도한 $13.90 대신 $21.39가 됨).
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from compliance import ComplianceResult

Country = Literal["SG", "MY"]
MIN_NET_MARGIN_PCT = 20.0

RULEBOOK_PATH = Path(__file__).resolve().parent.parent / "rulebook" / "country_rules.json"


@dataclass
class MarginResult:
    compliance_result: ComplianceResult
    cost_price_krw: int
    adjustment_rate_pct: float
    net_margin_pct: float
    approved: bool
    retried: bool = False


def load_fee_assumptions(country: Country, path: Path = RULEBOOK_PATH) -> dict:
    """country_rules.json에서 국가별 fee_assumptions를 로드한다."""
    with open(path, encoding="utf-8") as f:
        rules = json.load(f)
    return rules["countries"][country]["fee_assumptions"]


def calculate_margin(cost_price_krw: int, adjustment_rate_pct: float, country: Country) -> float:
    """Global SKU Price(원가) + Adjustment Rate + 국가별 수수료 가정으로 순마진율(%)을 계산한다.

    TODO(실행 전 필요 사항):
    - 정확한 마진 공식 확정 필요: Global SKU Price(원가) 기준으로 쇼피가 자동 가산하는
      Commission / Transaction fee(2%) / Cross-border shipping cost의 실제 산출식을
      셀러센터 시뮬레이터 또는 공식 문서로 재검증 (기존 마진계산기는 "판매가=원가" 전제가
      틀렸던 것으로 확인되어 전면 재설계 필요 상태 - 운영 룰북 v2 참조)
    - MY는 2026-02-01부터 신설된 Platform Support Fee(5%)와 인상된 크로스보더 커미션
      (16.2% -> 18.36%)을 반영한 별도 계산식 필요
    - 환율(KRW -> SGD/MYR) 최신값을 어디서 자동으로 가져올지 (수동 갱신 vs API) 결정
    """
    raise NotImplementedError("margin-agent: 마진 계산 공식 미구현 (재설계 필요).")


def screen_candidate(compliance_result: ComplianceResult, cost_price_krw: int, country: Country,
                      initial_adjustment_rate_pct: float = 130.0) -> MarginResult:
    """마진 20% 기준으로 스크리닝한다. 미달 시 Adjustment Rate를 조정해 1회 재시도한다.

    TODO: 재시도 시 Adjustment Rate를 얼마나/어떻게 올릴지(고정폭 vs 목표마진 역산) 정책 필요.
    """
    raise NotImplementedError("margin-agent: 스크리닝 및 재시도 로직 미구현.")
