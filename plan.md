# Screenshot Cleaner 개발 계획 (Plan)

이 문서는 사용자의 스크린샷 디렉토리르 관리하고 정리하는 'Screenshot Cleaner' 앱의 최종 개발 계획 및 사양을 담고 있습니다.

## 1. 프로젝트 개요
- **목적**: `C:\Users\User\OneDrive\Pictures\Screenshots` 디렉토리의 스크린샷들을 미리보고, 선택적으로 삭제하여 저장 공간을 확보합니다.
- **주요 기능**:
  - **자동 브라우저 실행**: 앱 실행 시 관리 페이지가 자동으로 열림
  - **스크린샷 목록 스캔**: 미리보기 및 파일 정보 표시
  - **일괄 삭제 (Batch Delete)**: 여러 파일을 선택하여 한 번에 삭제 및 확보될 용량 실시간 확인
  - **종료 (Finish)**: 사용 완료 후 안전하게 앱 종료 및 브라우저 탭 닫기
  - **통계**: 이미지 삭제로 확보한 누적 공간 표시

## 2. 기술 스택
- **Backend**: Python (FastAPI) - 파일 시스템 제어, 이미지 스트리밍, 서버 제어
- **Frontend**: Vanilla HTML/JS + Modern CSS (유리 효과 테마) - 빠르고 가벼운 UI

## 3. 상세 기능 명세
### 백엔드 (FastAPI)
- `ScreenshotManager`: 파일 스캔, 크기 계산, 물리적 삭제 로직
- `API Endpoints`:
  - `GET /screenshots`: 목록 조회
  - `DELETE /screenshots/{filename}`: 단일 파일 삭제
  - `POST /screenshots/batch-delete`: 다중 파일 일괄 삭제
  - `POST /shutdown`: 서버 프로세스 종료

### 프런트엔드 (Vanilla JS)
- `render()`: 그리드 형태의 카드 레이아웃 생성
- `Selection Logic`: 체크박스를 통한 다중 선택 및 상단 헤더 배치
- `Real-time Feedback`: 선택된 파일 개수와 합산 용량(MB) 표시
- `Auto-close`: 종료 시 `window.close()`를 통한 탭 닫기 시도

## 4. 기대 효과
- 불필요한 스크린샷을 일괄 선택으로 매우 빠르게 정리 가능
- 브라우저 기반의 현대적인 UI로 별도 설치 없이 사용 가능
- 자동 실행 및 종료 기능을 통해 사용자 편의성 극대화
