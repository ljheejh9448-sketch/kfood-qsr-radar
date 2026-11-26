# Global QSR · K-Food Radar

국가별 맥도날드·KFC 등 글로벌 QSR K-Food 메뉴 출시 이력을 정리하고, 새로운 관련 기사를 매주 자동으로 수집하는 홈페이지입니다.

## 웹사이트

https://ljheejh9448-sketch.github.io/kfood-qsr-radar/

## 주요 기능

- 2026년 글로벌 QSR K-Food 메뉴 조사 이력 **65건**(기존 조사 자료, 전수 재검증 아님)
- 국가·브랜드·Flavor·판매 유형별 필터 및 검색
- 메뉴 상세 정보와 원문 링크
- CSV 내보내기
- 매주 일요일 **22:00 KST** Google News RSS에서 새 기사 후보 수집
- 새 기사 후보는 **검토 대기**로 표시하며, 확정 출시 이력에 자동 추가하지 않음

## 운영 방식

- `site/index.html`: 홈페이지(기존 조사 데이터 65건을 포함한 독립형 화면)
- `site/data/candidates.json`: 주간 신규 기사 후보 DB
- `scripts/weekly_scan.py`: Google News RSS 기사 검색 및 중복 제거 스크립트
- `.github/workflows/deploy-pages.yml`: 홈페이지 GitHub Pages 게시
- `.github/workflows/weekly-monitor.yml`: 매주 일요일 밤 10시(한국시간) 기사 후보 업데이트 후 홈페이지 배포

## 최초 배포 설정

GitHub 저장소의 **Settings → Pages → Build and deployment → Source: GitHub Actions**를 선택합니다.

GitHub Actions의 `Publish K-Food Radar`를 한 번 수동 실행해 최초 배포할 수 있습니다. 이후 site 경로 변경 시 자동 재배포합니다.

주간 모니터링은 `Weekly K-Food QSR discovery`에서 수동 실행해 테스트할 수 있습니다. GitHub의 scheduled workflow는 일부 상황에서 지연되거나 비활성화될 수 있습니다.

> **주의:** 이 저장소와 GitHub Pages는 공개일 수 있습니다. 출처가 확인된 공개 자료만 등록하고, 회사 기밀이나 개인정보를 게시하지 마세요. 뉴스 검색 결과는 실제 메뉴 출시를 뜻하지 않습니다.


## 관리자 편집 (사진 교체·메뉴 수정·신규 등록)

관리자 화면: https://ljheejh9448-sketch.github.io/kfood-qsr-radar/admin.html

- 지정된 관리자 GitHub 계정과 저장소 전용 Fine-grained personal access token (`Contents: Read and write`)으로 인증합니다.
- 업로드한 사진은 최대 1600px의 WebP로 변환해 `site/assets/uploads/`에 저장합니다.
- 메뉴 수정·추가·삭제는 `site/data/launches.json`에 저장됩니다. GitHub Actions가 자동 재배포합니다.
- 토큰은 브라우저 탭 메모리에서만 사용하며 저장·전송(제3자 대상)하지 않습니다. 토큰은 GitHub API 요청에만 사용합니다.
- 편집 종료 후 **로그아웃**, 토큰 공유 금지, 공개 가능한 데이터·사진만 등록해야 합니다.

자세한 사용 방법: [ADMIN_GUIDE_KO.md](ADMIN_GUIDE_KO.md)


## 주간 기사 검토 워크플로

관리자 편집 페이지의 **주간 기사 검토** 탭을 이용해 수집된 기사를 검토하고, 확인된 메뉴를 출시 이력으로 등록할 수 있습니다. 기사 제목·브랜드·원문 링크는 자동 연결되며, 실제 출시일·국가·메뉴명은 관리자가 확인해 입력해야 합니다.

- **검토 대기**: RSS가 수집했으나 출시 여부를 확정하지 않은 기사
- **출시 이력 등록**: 검증 후 메뉴 DB에 저장해 원본 기사와 연결한 항목
- **검토 제외**: 출시 기록과 관련 없거나 적용하지 않기로 판단한 기사 (다시 검토 가능)

주간 스캔은 원문 기사 후보를 갱신하지만 자동으로 출시 메뉴를 확정하지 않습니다.

## 2026-11-26 업로드 엑셀 반영

제공받은 `QSR Trend Monitoring.xlsx` 시트 내용을 기존 데이터와 분리하여 홈페이지에 반영했습니다.

- `QSR K-FOOD MONITORING`: 엑셀 13개 캠페인 행을 `site/data/launches.json`에 `recordType: excel-monitoring`으로 추가
- `QSR LTO MONITORING`: 원본 엑셀에 헤더만 존재, 데이터 없음(빈 섹션으로 표시)
- `MONTHLY KEY TAKEAWAY`: 원본 엑셀에 헤더만 존재, 데이터 없음(빈 섹션으로 표시)
- 기존 상품별 DB는 유지합니다. 캠페인 행과 상품별 행은 중복될 수 있습니다.
- 관리자는 관리자 페이지에서 **출시 이력 → 엑셀 모니터링** 필터를 선택해 13개 기록을 편집하거나 사진을 별도로 업로드할 수 있습니다.
- 엑셀 내 이미지 파일들은 출처·재게시 권한 확인 없이 공개 GitHub 저장소로 자동 업로드하지 않았습니다.
- 주간 RSS 수집은 엑셀 13개 사례를 자동 수정하지 않습니다. 뉴스 후보 검토 후 관리자가 메뉴로 등록해야 합니다.
