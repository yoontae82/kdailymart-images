"""master-qa-agent

역할: 전 단계 로그와 룰북 대조, 오류 시 해당 에이전트에 수정지시 재큐잉
입력: 전 단계 로그 (sourcing/compliance/margin/image/localization/listing/promo/distribution)
출력: 통과/반려 + 수정지시 + 일일 리포트 (logs/master-qa/에 저장)
반려 조건: 아래 체크리스트 미충족

파이프라인 순서: 7단계 (마지막 단계, 전체 파이프라인 최종 게이트).

정지 조건: 3회 연속 반려되는 상품은 자동 재시도를 중단하고 사람 검토 큐로 이관한다.

체크리스트 (설계서 4번 섹션, ChecklistItem 순서 고정):
1. Category ID가 룰북/HiddenCatProps와 일치하는가
2. Global SKU Price = 원가만 입력되었는가 (판매가 아님)
3. DTS가 허용범위 내인가 (Pre-order DTS Range 시트 대조)
4. Mandatory/Conditional Mandatory 속성이 전부 채워졌는가
5. 이미지가 실물과 매칭되는가 (상상 제작 금지)
6. 마진계산기 기준 순마진 >= 20%인가
7. 국가별 규제 카테고리에 저촉되지 않는가
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Literal

from listing import ListingResult

MAX_RETRIES = 3


class ChecklistItem(str, Enum):
    CATEGORY_ID_MATCHES_RULEBOOK = "category_id_matches_rulebook"
    GLOBAL_SKU_PRICE_IS_COST_ONLY = "global_sku_price_is_cost_only"
    DTS_WITHIN_ALLOWED_RANGE = "dts_within_allowed_range"
    MANDATORY_ATTRIBUTES_FILLED = "mandatory_attributes_filled"
    IMAGE_MATCHES_REAL_PRODUCT = "image_matches_real_product"
    NET_MARGIN_AT_LEAST_20PCT = "net_margin_at_least_20pct"
    NO_COUNTRY_REGULATION_CONFLICT = "no_country_regulation_conflict"


@dataclass
class ChecklistResult:
    item: ChecklistItem
    passed: bool
    detail: str = ""


@dataclass
class QaVerdict:
    sku: str
    checklist_results: list[ChecklistResult]
    retry_count: int
    approved: bool
    correction_instruction: str | None = None
    escalate_to_human: bool = False


def run_checklist(listing: ListingResult, pipeline_logs: dict) -> list[ChecklistResult]:
    """7개 체크리스트 항목을 전 단계 로그와 대조하여 판정한다.

    TODO(실행 전 필요 사항):
    - pipeline_logs 스키마 확정: 각 agent(sourcing/compliance/margin/image/localization/listing)가
      실제로 어떤 필드를 로그로 남길지 정의해야 이 함수에서 대조 가능
    - 항목별 판정 로직을 rulebook/country_rules.json, rulebook/category_master.json과
      실제로 연결 (현재 두 파일 모두 draft 상태이며 카테고리가 2개만 채워져 있음)
    - "이미지가 실물과 매칭되는가"는 자동 판정이 어려울 수 있음 -> 사람 검수 큐로 넘길지,
      이미지 유사도 모델로 자동 판정할지 결정 필요
    """
    raise NotImplementedError("master-qa-agent: 체크리스트 판정 로직 미구현.")


def requeue_with_correction(verdict: QaVerdict, failing_agent: Literal[
    "sourcing", "compliance", "margin", "image", "localization", "listing", "promo", "distribution"
]) -> None:
    """체크리스트 실패 항목에 해당하는 에이전트에 수정지시를 내리고 재큐잉한다.
    retry_count가 MAX_RETRIES(3)에 도달하면 자동 재시도를 중단하고 사람 검토 큐로 이관한다.

    TODO(실행 전 필요 사항):
    - 재큐잉 큐 구현 방식 결정 (파일 기반 큐 vs 메시지 큐 vs 단순 함수 재호출)
    - 사람 검토 큐 이관 시 알림 방식 (예: 이메일/Slack/카카오톡 등) 결정
    """
    raise NotImplementedError("master-qa-agent: 재큐잉 로직 미구현.")


def write_daily_report(verdicts: list[QaVerdict], report_date: date) -> str:
    """logs/master-qa/<report_date>.json 형식으로 일일 리포트를 저장하고 경로를 반환한다.

    TODO: 리포트 포맷(승인/반려 수, 반려 사유 분포, 사람 검토 큐 건수 등) 확정 필요.
    """
    raise NotImplementedError("master-qa-agent: 일일 리포트 저장 로직 미구현.")
