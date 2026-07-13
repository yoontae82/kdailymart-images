"""master-qa-agent (마스터 - 5개 팀 총괄)

역할: 전 단계 로그와 룰북 대조, 오류 시 해당 에이전트에 수정지시 재큐잉.
5개 팀(기획=sourcing, 디자인=image+localization, 개발=listing+exposure,
홍보=promo+distribution, CS=cs) 전체를 총괄하며 두 트랙을 감시한다:

트랙 1 - 신규 상품 QA (아래 체크리스트, 상품 단위, 파이프라인 7단계 최종 게이트)
트랙 2 - 상시 운영 오버사이트 (CS 응답 SLA, 노출 저조 상품) - 일일 파이프라인과 무관하게 계속 실행

입력: 전 단계 로그 (sourcing/compliance/margin/image/localization/listing/promo/distribution/cs/exposure)
출력: 통과/반려 + 수정지시 + 일일 리포트 (logs/master-qa/에 저장)
반려 조건 (트랙 1): 아래 체크리스트 미충족

파이프라인 순서: 트랙 1은 7단계 (마지막 단계, 전체 파이프라인 최종 게이트). 트랙 2는 상시.

정지 조건: 3회 연속 반려되는 상품은 자동 재시도를 중단하고 사람 검토 큐로 이관한다.
(CS 에스컬레이션과 노출 저조 이슈는 상품 반려가 아니라 해당 팀 재작업 지시로 처리한다.)

체크리스트 (설계서 4번 섹션, ChecklistItem 순서 고정, 트랙 1 전용):
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

from cs import CsReply
from exposure import ExposureReport
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
    "sourcing", "compliance", "margin", "image", "localization", "listing", "promo", "distribution",
    "cs", "exposure",
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


class OperationsIssue(str, Enum):
    """트랙 2(상시 운영 오버사이트) 전용 이슈 유형. 상품 반려가 아니라 팀별 재작업 지시로 이어진다."""
    CS_SLA_BREACHED = "cs_sla_breached"                     # CS 응답 지연/미응답
    CS_ESCALATION_BACKLOG = "cs_escalation_backlog"         # 사람 이관 큐가 쌓이는 중
    LISTING_UNDEREXPOSED = "listing_underexposed"           # exposure-agent가 저조로 판정한 상품 존재


@dataclass
class OperationsVerdict:
    checked_on: date
    issues: list[OperationsIssue]
    cs_backlog_count: int
    underexposed_skus: list[str]
    routed_to: dict[str, str]
    """이슈별로 어느 팀에 재작업을 지시했는지 (예: {"KDM-HAIR-CLIP5": "sourcing+promo"})."""


def run_operations_oversight(cs_replies: list[CsReply], exposure_reports: list[ExposureReport],
                              report_date: date) -> OperationsVerdict:
    """CS 응답 SLA와 상품 노출 상태를 총괄 점검하고, 문제가 있으면 해당 팀(CS/기획/홍보)에
    재작업을 지시한다. 신규 상품 QA(run_checklist)와 달리 이 트랙은 상품을 반려하지 않고
    운영 이슈를 팀별로 라우팅하는 데 집중한다.

    TODO(실행 전 필요 사항):
    - CS SLA 기준 확정 (예: 문의 접수 후 몇 시간 내 응답이 정상인지, 국가별로 다를 수 있음)
    - exposure-agent의 ExposureReport.is_underexposed가 True인 상품을 얼마나 지속 관찰한 뒤
      기획팀(대체 상품 검토)/홍보팀(홍보 강화) 중 어디로 먼저 넘길지 우선순위 규칙
    - CS 에스컬레이션 백로그가 임계치를 넘으면(사람이 못 따라가는 상황) 자동 응대 범위를
      일시적으로 넓힐지, 아니면 그대로 사람 검토를 기다릴지 정책 결정
    """
    raise NotImplementedError("master-qa-agent: 운영 오버사이트 로직 미구현.")


def write_operations_report(verdict: OperationsVerdict, report_date: date) -> str:
    """logs/master-qa/operations-<report_date>.json 형식으로 운영 오버사이트 리포트를 저장한다.
    write_daily_report(신규 상품 QA)와 별도 파일로 관리해 두 트랙의 로그가 섞이지 않게 한다.

    TODO: 리포트 포맷 확정 필요 (write_daily_report와 동일 이슈).
    """
    raise NotImplementedError("master-qa-agent: 운영 리포트 저장 로직 미구현.")
