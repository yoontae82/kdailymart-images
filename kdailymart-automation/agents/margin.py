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


# 운영 룰북 v2가 "100%=마진0, 130%=마진30%"를 실증한 건 SG 헤어핀 카테고리 실제 LIVE 등록
# 사례 하나뿐이다. MY는 2026-02-01 신설된 Platform Support Fee(5%)와 인상된 크로스보더 커미션이
# 이 단순 관계에 얼마나 영향을 주는지 아직 셀러센터로 재검증되지 않았다. 그래서 이 국가는
# "검증됨" 취급하지 않고, MarginResult.formula_verified=False로 표시해 하류(master_qa 등)에서
# 사람 재검토를 요구할 수 있게 한다.
FORMULA_VERIFIED_COUNTRIES: dict[Country, bool] = {
    "SG": True,
    "MY": False,
}

# Adjustment Rate를 무한정 올려 20% 마진 문턱을 억지로 맞추면 노출가가 비경쟁적으로 뛴다.
# 재시도 시에도 이 상한을 넘기지 않는다 (넘겨야 한다면 그 상품은 진짜로 마진이 안 나오는 것).
MAX_ADJUSTMENT_RATE_PCT = 150.0


@dataclass
class MarginResult:
    compliance_result: ComplianceResult
    cost_price_krw: int
    adjustment_rate_pct: float
    net_margin_pct: float
    approved: bool
    formula_verified: bool
    retried: bool = False


def load_fee_assumptions(country: Country, path: Path = RULEBOOK_PATH) -> dict:
    """country_rules.json에서 국가별 fee_assumptions를 로드한다."""
    with open(path, encoding="utf-8") as f:
        rules = json.load(f)
    return rules["countries"][country]["fee_assumptions"]


def _unverified_fee_correction_pct(country: Country) -> float:
    """formula_verified=False인 국가에서, 룰북에 명시된 추가 수수료 레이어(예: MY Platform Support
    Fee)를 안전 마진에서 미리 차감하는 보수적 보정치. Adjustment Rate 다이얼이 이 수수료까지
    이미 자동으로 흡수하는지 여부가 검증 전이므로, "verified 전까지는 손해 보는 쪽으로 가정한다."
    """
    if FORMULA_VERIFIED_COUNTRIES.get(country, False):
        return 0.0
    fees = load_fee_assumptions(country)
    platform_support_fee = fees.get("platform_support_fee_pct", {})
    return platform_support_fee.get("value", 0.0) if isinstance(platform_support_fee, dict) else 0.0


def calculate_margin(cost_price_krw: int, adjustment_rate_pct: float, country: Country) -> float:
    """Global SKU Price(원가) + Adjustment Rate로 순마진율(%)을 계산한다.

    공식: net_margin_pct = adjustment_rate_pct - 100 - (검증 안 된 국가의 추가 수수료 보정치)
    이 관계(100%=마진0, 130%=마진30%)는 운영 룰북 v2에 명시된 쇼피의 실제 동작이며, SG는
    Day 1 실제 LIVE 등록으로 확인됐다 (FORMULA_VERIFIED_COUNTRIES["SG"]=True).

    ⚠️ MY는 이 관계가 아직 셀러센터로 재검증되지 않았다 (FORMULA_VERIFIED_COUNTRIES["MY"]=False).
    Platform Support Fee(5%)를 안전하게 미리 차감한 보수적 추정치일 뿐이며, 실제 리스팅 전에
    MY 셀러센터의 실제 계산 결과와 반드시 대조해야 한다 - 다르면 이 함수와 country_rules.json의
    global_sku_price_rule을 함께 갱신할 것.

    TODO(실행 전 필요 사항):
    - MY 공식을 실제 셀러센터 값으로 재검증하고 FORMULA_VERIFIED_COUNTRIES["MY"]를 True로 갱신
    - 크로스보더 커미션 인상분(16.2% -> 18.36%)이 Adjustment Rate 다이얼에 이미 흡수되는지,
      아니면 별도로 반영해야 하는지 확인 (현재는 흡수된다고 가정하고 보정치에 포함 안 함)
    - 환율(KRW -> SGD/MYR)은 이 함수에서 다루지 않는다 (cost_price_krw, net_margin_pct 모두
      원화 기준 비율 계산이라 환율 자체는 margin 계산에 영향 없음 - 노출가 표시에만 필요)
    """
    return adjustment_rate_pct - 100.0 - _unverified_fee_correction_pct(country)


def screen_candidate(compliance_result: ComplianceResult, cost_price_krw: int, country: Country,
                      initial_adjustment_rate_pct: float = 130.0) -> MarginResult:
    """마진 20% 기준으로 스크리닝한다. 미달 시 Adjustment Rate를 20% 마진을 만드는 값까지
    올려서(단, MAX_ADJUSTMENT_RATE_PCT 상한 이내) 1회 재시도한다. 그래도 미달이면 탈락시킨다.
    """
    net_margin_pct = calculate_margin(cost_price_krw, initial_adjustment_rate_pct, country)
    formula_verified = FORMULA_VERIFIED_COUNTRIES.get(country, False)

    if net_margin_pct >= MIN_NET_MARGIN_PCT:
        return MarginResult(
            compliance_result=compliance_result, cost_price_krw=cost_price_krw,
            adjustment_rate_pct=initial_adjustment_rate_pct, net_margin_pct=net_margin_pct,
            approved=True, formula_verified=formula_verified, retried=False,
        )

    correction = _unverified_fee_correction_pct(country)
    required_rate_pct = min(100.0 + MIN_NET_MARGIN_PCT + correction, MAX_ADJUSTMENT_RATE_PCT)
    retried_margin_pct = calculate_margin(cost_price_krw, required_rate_pct, country)

    return MarginResult(
        compliance_result=compliance_result, cost_price_krw=cost_price_krw,
        adjustment_rate_pct=required_rate_pct, net_margin_pct=retried_margin_pct,
        approved=retried_margin_pct >= MIN_NET_MARGIN_PCT, formula_verified=formula_verified, retried=True,
    )
