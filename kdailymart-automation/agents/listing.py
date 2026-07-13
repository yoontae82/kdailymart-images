"""listing-agent

역할: Global SKU 등록 -> Mass Upload -> 개별 Publish
입력: 카피(localization-agent), 이미지(image-agent), 카테고리ID, 속성값(rulebook/category_master.json)
출력: Item ID, LIVE 상태
반려 조건: Publish 실패

파이프라인 순서: 5단계.

검증된 절차 (운영 룰북 v2):
- 등록 방식: Global SKU -> Mass Upload -> 개별 Publish
- Mass Publish는 "No Product Found"로 실패한 이력이 있음 -> 개별 Publish가 정답 경로
- Global SKU Price 컬럼(K)에는 원가만 입력 (판매가 아님, margin-agent 산출값 사용)
- 성공 컬럼 세트 예시: A(Category) B(Name) C(Description) D(Parent SKU) K(Price=원가)
  L(Stock) M(SKU) N(Cover Image) O~S(Item Image 1~5) Y(Weight) Z/AA/AB(치수) AC(Days to Ship) AE~(속성)
"""

from dataclasses import dataclass
from typing import Literal

from image import ProcessedImageSet
from localization import LocalizedCopy
from margin import MarginResult

Country = Literal["SG", "MY"]


@dataclass
class ListingResult:
    item_id: str | None
    sku: str
    status: Literal["global_sku_only", "mass_uploaded", "live", "publish_failed"]
    failure_reason: str | None = None


def build_mass_upload_row(copy: LocalizedCopy, images: ProcessedImageSet, margin: MarginResult,
                           category_id: int, attributes: dict) -> dict:
    """category_master.json의 컬럼 규칙에 맞춰 Mass Upload 1행 데이터를 조립한다.

    TODO(실행 전 필요 사항):
    - category_master.json에 채워질 각 카테고리의 정확한 컬럼 매핑(A, B, C, K, N, O~ 등)을
      실제 쇼피 템플릿 파일 기준으로 100% 검증 (현재는 2개 카테고리만 draft로 채워짐)
    - Global SKU Price(K 컬럼)에는 반드시 margin.MarginResult.cost_price_krw(원가)만 들어가도록
      하는 검증 단계 필요 (판매가 오입력 방지 - Day 1 실수 재발 방지)
    """
    raise NotImplementedError("listing-agent: Mass Upload 행 조립 로직 미구현.")


def mass_upload(rows: list[dict], country: Country) -> list[ListingResult]:
    """조립된 행들을 쇼피 셀러센터에 Mass Upload 한다.

    TODO(실행 전 필요 사항):
    - 브라우저 자동화 방식 결정: (a) Playwright/Selenium으로 셀러센터 UI 직접 조작
      (b) 쇼피 Open API(공식 연동) 사용 가능 여부 확인 후 전환
      둘 중 무엇을 쓸지에 따라 이후 구현이 완전히 달라지므로 최우선 결정 필요
    - 셀러센터 로그인 크리덴셜 및 2FA/OTP 처리 방식 (자동화 시 OTP 수신 방법)
    - seller.shopee.kr(KRSC) 계정 세션 유지/재로그인 정책
    - MY는 셀러센터 계정 개설 자체가 아직 미확인 상태이므로, 계정 개설 전에는 호출 불가
    """
    raise NotImplementedError("listing-agent: Mass Upload 자동화 미구현 (브라우저 자동화 방식 미결정).")


def publish_individually(uploaded: list[ListingResult]) -> list[ListingResult]:
    """Mass Upload된 상품을 하나씩 개별 Publish 한다 (Mass Publish는 실패 이력이 있어 사용하지 않음).

    TODO: Publish 실패 시 재시도 횟수/사유 로깅, master-qa-agent로의 반려 전달 포맷 필요.
    """
    raise NotImplementedError("listing-agent: 개별 Publish 로직 미구현.")
