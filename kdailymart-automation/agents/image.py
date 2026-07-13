"""image-agent

역할: 원본 이미지 -> AI 누끼/착용샷/1:1 1200x1200 이미지 생성
입력: 원본 이미지 URL
출력: 가공 이미지 세트 + GitHub 업로드 (CDN: yoontae82/kdailymart-images -> raw.githubusercontent.com)
반려 조건: 원본 저작권 미확인

파이프라인 순서: 4단계 (localization-agent와 병렬 실행).

이미지 규격 (운영 룰북 v2에서 검증됨):
- 대량등록은 이미지를 URL로만 받는다 (파일 업로드 불가) -> GitHub raw URL 필수
- 1:1 정사각 1200x1200 JPG
- 컬럼: Cover image(필수) + Item Image 1~8
"""

from dataclasses import dataclass
from typing import Literal

from sourcing import SourcingCandidate

ImageKind = Literal["cutout", "worn_shot", "cover_1200x1200"]


@dataclass
class ProcessedImageSet:
    candidate: SourcingCandidate
    cover_image_url: str
    item_image_urls: list[str]
    copyright_cleared: bool


def verify_image_rights(candidate: SourcingCandidate) -> bool:
    """원본 이미지의 사용 권한(공급사 허가/자체 촬영/라이선스 확보 등)을 확인한다.

    TODO(실행 전 필요 사항):
    - 공급사 이미지 사용허가를 어떤 절차로 요청/기록할지 (이메일 템플릿, 승인 기록 저장 위치)
    - 자체 확보가 안 될 경우 "AI 생성" 또는 "샘플 구매 후 촬영" 중 어느 경로를 기본값으로 할지 결정
    - 타 셀러 이미지 무단 도용 여부를 자동으로 걸러낼 방법 (역이미지 검색 등) 필요 여부 검토
    """
    raise NotImplementedError("image-agent: 이미지 저작권 확인 로직 미구현.")


def generate_processed_images(candidate: SourcingCandidate) -> ProcessedImageSet:
    """원본 이미지를 누끼/착용샷/1200x1200 커버 이미지로 가공한다.

    TODO(실행 전 필요 사항):
    - 이미지 생성 API 선택 및 API 키 확보 (예: OpenAI Images, Stability AI, Google 등 중 택1)
    - "실물과 매칭되는" 이미지를 강제하는 검수 단계 필요 (상상 제작 금지 - master-qa 체크리스트 항목).
      즉 원본 실물 사진 없이는 이 함수가 절대 호출되지 않도록 sourcing-agent 단계에서 보장해야 함.
    - 누끼/착용샷 각각에 필요한 프롬프트/파라미터 표준화
    - 생성 실패/저품질 결과에 대한 재시도 및 사람 검수 fallback 정책
    """
    raise NotImplementedError("image-agent: 이미지 생성 로직 미구현 (API 키 필요).")


def upload_to_github_cdn(image_set: ProcessedImageSet, repo: str = "yoontae82/kdailymart-images") -> ProcessedImageSet:
    """가공된 이미지를 GitHub 저장소에 업로드하고 raw.githubusercontent.com URL을 채운다.

    TODO(실행 전 필요 사항):
    - GitHub 업로드용 크리덴셜(Personal Access Token 등) 확보 및 안전한 보관 방식
      (운영 룰북 v2에 "GitHub 토큰 Revoke" 액션 아이템이 있었음 - 기존 토큰 재사용 금지, 새 토큰 발급 필요)
    - 업로드 대상 폴더/파일명 규칙 (기존 aloe/, clips/, prod2/, prod3/ 폴더 네이밍 방식과의 정합성)
    - 업로드 후 GitHub raw URL이 실제로 정상 렌더링되는지 확인하는 헬스체크 로직
    """
    raise NotImplementedError("image-agent: GitHub 업로드 로직 미구현 (크리덴셜 필요).")
