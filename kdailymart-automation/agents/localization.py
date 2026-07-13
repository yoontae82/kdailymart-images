"""localization-agent

역할: 상세페이지 카피를 판매국 언어로, 한국산 신뢰도 강조 톤으로 작성
입력: 상품 정보, 국가
출력: 현지어 상세페이지 카피
반려 조건: 없음 (단, distribution 단계에서 MY 말레이어 카피는 로컬 톤 검수 필요)

파이프라인 순서: 4단계 (image-agent와 병렬 실행).

국가별 언어 (설계서 3번 섹션):
- SG: 영어
- MY: 말레이어/영어 혼용 (말레이어 카피는 로컬 톤 검수 필요)
"""

from dataclasses import dataclass
from typing import Literal

from sourcing import SourcingCandidate

Country = Literal["SG", "MY"]


@dataclass
class LocalizedCopy:
    candidate: SourcingCandidate
    country: Country
    language: str
    title: str
    description: str
    reviewed_by_local_speaker: bool = False


def generate_copy(candidate: SourcingCandidate, country: Country) -> LocalizedCopy:
    """상품 정보를 판매국 언어의 상세페이지 카피로 변환한다. 한국산 신뢰도를 강조하는 톤 유지.

    TODO(실행 전 필요 사항):
    - 번역/카피라이팅에 사용할 LLM/번역 API 선택 및 크리덴셜 확보
    - "한국산 신뢰도 강조 톤"에 대한 구체적 스타일 가이드/예시 문구 세트 정리
    - Category ID 별 Mandatory 속성 문구 형식(예: Region of Origin = "Korea", 'South Korea' 아님)과
      카피 생성 결과가 충돌하지 않도록 category_master.json과 연동
    """
    raise NotImplementedError("localization-agent: 카피 생성 로직 미구현 (번역/생성 API 필요).")


def request_local_review(copy: LocalizedCopy) -> LocalizedCopy:
    """MY 말레이어 카피에 대해 로컬 원어민 검수를 요청한다. SG 영어 카피는 이 단계를 생략할 수 있다.

    TODO(실행 전 필요 사항):
    - 말레이어 원어민 검수자를 사람으로 둘지, 검수용 2차 LLM 체크로 대체할지 결정
    - 검수 요청/승인 흐름 (큐, 알림 방식) 설계 필요
    """
    raise NotImplementedError("localization-agent: 로컬 검수 요청 로직 미구현.")
