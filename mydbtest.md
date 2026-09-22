# mydbtest CRUD API

## 작업 결과

- AWS 리전: `ap-northeast-2`
- Lambda 함수: `mydbtest`
- REST API: `mydbtest-rest-api`
- API ID: `7lcsmkwe50`
- 스테이지: `prod`
- MariaDB 데이터베이스: `mockinv`
- 대상 테이블: `upbit_market`
- 기본 URL: `https://7lcsmkwe50.execute-api.ap-northeast-2.amazonaws.com/prod`
- 인증 방식: 없음 (`authorizationType: NONE`)
- API Key: 사용하지 않음

Lambda는 MariaDB 전용 계정으로 `upbit_market` 테이블에만 `SELECT`, `INSERT`, `UPDATE`, `DELETE` 권한을 사용한다.

## API 목록

| 기능 | HTTP 메서드 | 경로 |
|---|---|---|
| 목록 조회 | `GET` | `/markets` |
| 단건 조회 | `GET` | `/markets/{id}` |
| 생성 | `POST` | `/markets` |
| 수정 | `PUT` | `/markets/{id}` |
| 삭제 | `DELETE` | `/markets/{id}` |

목록 조회에는 `limit`과 `offset` 쿼리 파라미터를 사용할 수 있다. `limit`은 최대 500이다.

## 브라우저 주소창에서 조회하기

아래 URL은 브라우저 주소창에 직접 입력할 수 있다.

- 처음 3건 조회:
  <https://7lcsmkwe50.execute-api.ap-northeast-2.amazonaws.com/prod/markets?limit=3>
- ID가 1인 데이터 조회:
  <https://7lcsmkwe50.execute-api.ap-northeast-2.amazonaws.com/prod/markets/1>

## 브라우저 개발자 도구에서 CRUD 테스트

브라우저에서 `F12`를 누르고 **Console** 탭을 연 다음 아래 JavaScript를 실행한다.

### 1. 목록 조회

```javascript
const baseUrl = "https://7lcsmkwe50.execute-api.ap-northeast-2.amazonaws.com/prod";

const list = await fetch(`${baseUrl}/markets?limit=3`).then(r => r.json());
console.table(list.items);
console.log("전체 건수:", list.total);
```

### 2. 테스트 데이터 생성

```javascript
const created = await fetch(`${baseUrl}/markets`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    english_name: "Browser Test Coin",
    korean_name: "브라우저 테스트 코인",
    market_code: "TEST-BROWSER"
  })
}).then(r => r.json());

console.log(created);
const testId = created.upbit_market_id;
```

### 3. 생성한 데이터 조회

```javascript
const item = await fetch(`${baseUrl}/markets/${testId}`).then(r => r.json());
console.log(item);
```

### 4. 데이터 수정

```javascript
const updated = await fetch(`${baseUrl}/markets/${testId}`, {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ english_name: "Browser Test Coin Updated" })
}).then(r => r.json());

console.log(updated);
```

### 5. 테스트 데이터 삭제

```javascript
const deleted = await fetch(`${baseUrl}/markets/${testId}`, {
  method: "DELETE"
}).then(r => r.json());

console.log(deleted);
```

삭제 후 같은 ID를 조회했을 때 HTTP `404`와 `Market not found`가 반환되면 정상이다.

## 검증 결과

- 목록 조회: HTTP `200`, 전체 293건 확인
- 생성: HTTP `201` 확인
- 수정: HTTP `200` 확인
- 단건 조회: HTTP `200` 확인
- 삭제: HTTP `200` 확인
- 삭제 후 조회: HTTP `404` 확인
- 테스트 데이터 삭제 후 전체 293건으로 복구 확인

## 주의 사항

현재 API에는 인증이 없으므로 URL을 아는 누구나 데이터를 생성, 수정, 삭제할 수 있다. 운영 환경에서는 IAM, Cognito, Lambda Authorizer 또는 API Key와 같은 접근 통제를 적용하는 것이 안전하다.
