"""cs-agent (CS팀)

역할: 쇼피 구매자 문의에 현지어로 1차 응대하고, 정책/분쟁 소지가 있는 문의는 사람에게 이관한다.
입력: 쇼피 채팅/문의함에 들어온 고객 메시지, 판매국, 관련 주문/상품 정보
출력: 현지어 답변 초안(또는 자동발송) + 에스컬레이션 여부
반려 조건: 없음 (단, 아래 escalation_reasons에 해당하면 자동응답하지 않고 사람에게 이관)

파이프라인 순서: 상시 실행 (일일 10개 등록 파이프라인과는 별도 트랙). master-qa-agent가
CS 응답 SLA와 에스컬레이션 큐 상태를 함께 총괄 감시한다.

절대 자동응답하면 안 되는 케이스 (반드시 사람 이관):
- 환불/반품 분쟁 (금액이 걸린 결정은 사람 판단 필요)
- 실물 없음/발송 불가 문의 (운영 룰북 v2에 실물 없이 등록된 SKU 사례가 있었음 - 거짓 안내 방지)
- 쇼피 정책 위반 신고, 가짜 상품 의혹 등 계정 정지 리스크가 있는 사안
"""

from dataclasses import dataclass
from typing import Literal

Country = Literal["SG", "MY"]

ESCALATION_REASONS = [
    "refund_or_return_dispute",
    "shipment_not_possible_or_out_of_stock",
    "policy_violation_or_counterfeit_report",
    "sentiment_highly_negative_unclear_cause",
]


@dataclass
class CustomerInquiry:
    inquiry_id: str
    country: Country
    language: str
    order_sku: str | None
    message: str


@dataclass
class CsReply:
    inquiry: CustomerInquiry
    reply_text: str
    auto_sent: bool
    escalated: bool
    escalation_reason: str | None = None


def fetch_pending_inquiries(country: Country) -> list[CustomerInquiry]:
    """쇼피 채팅/문의함에서 미응답 고객 문의를 가져온다.

    TODO(실행 전 필요 사항):
    - 쇼피 채팅 접근 방식 결정: 셀러센터 브라우저 자동화 vs 쇼피 Open API의 채팅 관련 엔드포인트 지원 여부 확인
      (listing-agent의 브라우저자동화 방식 결정과 동일한 축의 문제이므로 함께 결정)
    - 미응답 문의를 놓치지 않도록 폴링 주기 또는 웹훅 방식 결정
    """
    raise NotImplementedError("cs-agent: 문의 수집 로직 미구현 (쇼피 접근 방식 미결정).")


def draft_reply(inquiry: CustomerInquiry) -> CsReply:
    """문의 내용을 분석해 현지어 답변 초안을 만들고, ESCALATION_REASONS에 해당하면 자동발송하지 않는다.

    TODO(실행 전 필요 사항):
    - 답변 생성에 쓸 LLM/번역 API 선택 (localization-agent와 동일한 스택 재사용 가능한지 검토)
    - ESCALATION_REASONS 판별 로직: 키워드 매칭으로 시작하되, 오탐(자동응답 가능한 문의를 이관)과
      미탐(이관해야 할 문의를 자동응답) 중 어느 쪽 리스크를 더 보수적으로 잡을지 결정
      (기본값은 "애매하면 이관" 쪽으로 두는 것을 권장 - 자동응답 실수가 분쟁으로 번질 리스크가 더 큼)
    - 자동발송 전 사람 검수를 거칠지(초안만 생성), 즉시 자동발송할지 국가/문의유형별로 정책 결정
    """
    raise NotImplementedError("cs-agent: 답변 생성 로직 미구현.")


def escalate_to_human(inquiry: CustomerInquiry, reason: str) -> None:
    """사람 CS 검토 큐로 문의를 이관한다.

    TODO: 이관 큐/알림 방식 결정 (master-qa-agent의 사람 검토 큐와 통합할지, 별도로 둘지).
    """
    raise NotImplementedError("cs-agent: 이관 로직 미구현.")
