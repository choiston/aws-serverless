# AWS 서버리스 배포 실습 — Node.js · Python · Java + API Gateway
 
> **Hands-on AWS serverless examples with Lambda, API Gateway, CI/CD, and AI service integrations in Node.js, Python, and Java**

> **AWS Lambda와 Amazon API Gateway를 활용한 서버리스 함수 배포 실습 레포**
> Node.js, Python, Java 세 가지 런타임으로 Lambda 함수를 작성하고,
> AWS 콘솔 · AWS CLI · Serverless Framework · GitHub Actions CI/CD 네 가지 방법으로 배포하는 전 과정을 다룹니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-20.x-green?logo=node.js)](nodejs/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](python/)
[![Java](https://img.shields.io/badge/Java-17-red?logo=openjdk)](java/)
[![Serverless](https://img.shields.io/badge/Serverless_Framework-3.x-fd5750?logo=serverless)](https://www.serverless.com/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=amazonaws)](https://aws.amazon.com/lambda/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?logo=githubactions)](https://github.com/features/actions)

---

## 목차

1. [사전 지식: API · REST API · CORS](#사전-지식-api--rest-api--cors)
   - [API란?](#1-apiapplication-programming-interface란)
   - [REST API란?](#2-rest-api란)
   - [CORS란?](#3-corscross-origin-resource-sharing란)
   - [SSL/TLS와 HTTPS, 로드밸런서 연동](#4-api-보안을-위한-ssltls와-https)
2. [기술 스택](#기술-스택)
3. [아키텍처](#아키텍처)
   - [주가 데이터 AI/ML 파이프라인](#주가-데이터-aiml-파이프라인-stock-pipeline)
   - [API Gateway + Lambda](#api-gateway--lambda-hello-api)
   - [S3 이벤트 트리거 + Lambda](#s3-이벤트-트리거--lambda)
   - [GitHub Actions 배포 파이프라인](#github-actions-배포-파이프라인)
4. [디렉터리 구조](#디렉터리-구조)
5. [사전 준비](#사전-준비)
6. [AWS CLI 설치 및 설정](#aws-cli-설치-및-설정)
7. [AWS Lambda 이해](#aws-lambda-이해)
8. [Node.js Lambda 배포](#nodejs-lambda-배포)
9. [Python Lambda 배포](#python-lambda-배포)
10. [Java Lambda 배포](#java-lambda-배포)
11. [API Gateway 연동](#api-gateway-연동)
12. [GitHub Actions CI/CD 자동 배포](#github-actions-cicd-자동-배포)
13. [권한 오류 해결 가이드](#권한-오류-해결-가이드)
14. [AWS CLI 명령어 모음](#aws-cli-명령어-모음)
15. [추가 실습](#추가-실습)

---

## 사전 지식: API · REST API · CORS

이 레포는 "Lambda 함수를 API Gateway 뒤에 두고 HTTP로 호출한다"는 구조를 반복해서 다룹니다.
그래서 **API가 무엇인지, REST API 규칙이 무엇인지, 브라우저에서 호출할 때 왜 CORS 오류가 나는지, 왜 HTTPS(SSL/TLS)가 필수이고 로드밸런서와는 어떻게 연결하는지**를 먼저 이해해 두면
이후 실습 코드(`nodejs/handler.js`, `python/handler.py`, `java/.../HelloHandler.java`, 각 `serverless.yaml`)가 훨씬 쉽게 읽힙니다.

### 1. API(Application Programming Interface)란?

**API는 "프로그램끼리 서로 대화하기 위해 미리 약속한 규칙"** 입니다.
사람이 카페에서 주문할 때 메뉴판(무엇을 시킬 수 있는지)과 주문 방법(카운터에서 말한다)이 정해져 있듯이,
프로그램도 "어떤 기능을, 어떤 형식으로 요청하면, 어떤 형식으로 응답이 오는지"를 정해 둔 것이 API입니다.

| 구분 | 예시 | 설명 |
| ---- | ---- | ---- |
| 라이브러리 API | `JSON.parse()`, `boto3.client("s3")` | 같은 프로세스 안에서 함수를 호출하는 약속 |
| 운영체제 API | 파일 열기, 네트워크 소켓 | 프로그램이 OS 기능을 사용하는 약속 |
| **웹 API** | `GET https://.../dev/hello?name=Alice` | **네트워크(HTTP)를 통해 다른 서버의 기능을 사용하는 약속** — 이 레포가 다루는 것 |

웹 API에서는 항상 두 역할이 등장합니다.

```
  클라이언트 (요청하는 쪽)                 서버 (응답하는 쪽)
  브라우저 / curl / Postman / 다른 Lambda   API Gateway + Lambda
        │                                        │
        │ ── 요청(Request): 메서드 + URL + 헤더 + 본문 ──▶ │
        │                                        │
        │ ◀── 응답(Response): 상태 코드 + 헤더 + 본문 ── │
```

**요청(Request)** 의 구성 요소

| 요소 | 의미 | 예시 |
| ---- | ---- | ---- |
| HTTP 메서드 | 무엇을 하고 싶은지(동사) | `GET`, `POST`, `PUT`, `DELETE` |
| URL(경로) | 어떤 자원에 대해서인지(명사) | `/users`, `/users/42` |
| 쿼리 스트링 | URL 뒤에 붙는 부가 조건 | `?name=Alice&limit=10` |
| 헤더(Header) | 요청에 대한 메타 정보 | `Content-Type: application/json`, `Authorization: Bearer ...` |
| 본문(Body) | 서버에 보낼 실제 데이터(주로 JSON) | `{"name": "Alice", "email": "a@b.com"}` |

**응답(Response)** 의 구성 요소

| 요소 | 의미 | 예시 |
| ---- | ---- | ---- |
| 상태 코드(Status Code) | 처리 결과를 숫자로 요약 | `200 OK`, `201 Created`, `404 Not Found`, `500 Internal Server Error` |
| 헤더 | 응답에 대한 메타 정보 | `Content-Type: application/json`, `Access-Control-Allow-Origin: *` |
| 본문 | 실제 응답 데이터 | `{"message": "Hello, Alice!"}` |

Lambda 핸들러가 반환하는 객체가 정확히 이 "응답"의 구조입니다. `python/handler.py`를 보면 다음과 같습니다.

```python
return {
    "statusCode": 200,                                  # 상태 코드
    "headers": {"Content-Type": "application/json"},   # 헤더
    "body": json.dumps(body),                           # 본문 (반드시 문자열)
}
```

즉 **API Gateway는 HTTP 요청을 `event` 객체로 바꿔 Lambda에 넘기고, Lambda가 돌려준 객체를 다시 HTTP 응답으로 바꿔 클라이언트에 전달**하는 번역기 역할을 합니다. 이 구조를 "Lambda Proxy 통합"이라고 부르며, 자세한 event / response 형태는 [AWS Lambda 이해](#aws-lambda-이해) 절에서 다룹니다.

### 2. REST API란?

REST(Representational State Transfer)는 웹 API를 설계할 때 널리 쓰이는 **설계 스타일(규칙 모음)** 입니다.
"어떤 형식으로 요청하면 되는지"를 팀마다 새로 정하지 않아도 되도록, HTTP가 원래 가진 의미를 최대한 그대로 활용합니다.
REST 규칙을 따르는 API를 **REST API** 또는 **RESTful API**라고 부릅니다.

#### 핵심 원칙 4가지

**① 자원(Resource)은 URL로, 행위(Action)는 HTTP 메서드로 표현한다**

URL에는 동사를 쓰지 않고 **명사(자원 이름)** 만 씁니다. "무엇을 할지"는 메서드가 결정합니다.

| 하고 싶은 일 | ❌ REST답지 않은 설계 | ✅ REST 설계 |
| ---- | ---- | ---- |
| 사용자 목록 조회 | `GET /getUsers` | `GET /users` |
| 사용자 생성 | `POST /createUser` | `POST /users` |
| 42번 사용자 조회 | `GET /getUser?id=42` | `GET /users/42` |
| 42번 사용자 수정 | `POST /updateUser?id=42` | `PUT /users/42` |
| 42번 사용자 삭제 | `GET /deleteUser?id=42` | `DELETE /users/42` |

**② HTTP 메서드는 정해진 의미대로 사용한다 (CRUD 매핑)**

| 메서드 | CRUD | 의미 | 멱등성* | 본문 |
| ---- | ---- | ---- | ---- | ---- |
| `GET` | Read | 자원 조회. 서버 상태를 바꾸지 않음 | O | 없음 |
| `POST` | Create | 새 자원 생성. 호출할 때마다 새로 만들어짐 | X | 있음 |
| `PUT` | Update | 자원 전체 교체(없으면 생성하기도 함) | O | 있음 |
| `PATCH` | Update | 자원 일부만 수정 | △ | 있음 |
| `DELETE` | Delete | 자원 삭제 | O | 보통 없음 |
| `OPTIONS` | — | "이 URL은 어떤 메서드/헤더를 허용하나요?" 질의. **CORS 사전 요청에 사용** | O | 없음 |

\* 멱등성(Idempotent): 같은 요청을 여러 번 보내도 결과가 한 번 보낸 것과 같은 성질. 네트워크 오류 시 재시도해도 안전한지 판단하는 기준입니다.

**③ 상태 코드로 결과를 알린다**

| 범위 | 의미 | 자주 쓰는 코드 |
| ---- | ---- | ---- |
| 2xx | 성공 | `200 OK`(조회·수정 성공), `201 Created`(생성 성공), `204 No Content`(삭제 성공, 본문 없음) |
| 4xx | 클라이언트 잘못 | `400 Bad Request`(입력값 오류), `401 Unauthorized`(인증 없음), `403 Forbidden`(권한 없음), `404 Not Found`(자원 없음) |
| 5xx | 서버 잘못 | `500 Internal Server Error`(코드 예외), `502 Bad Gateway`(Lambda 응답 형식 오류 시 API Gateway가 반환), `504 Gateway Timeout`(Lambda 타임아웃) |

> 💡 Lambda에서 응답 객체 형식이 잘못되면(예: `body`가 문자열이 아닐 때) API Gateway는 `502 Bad Gateway`를 돌려줍니다. 실습 중 502가 보이면 Lambda 코드의 반환값부터 확인하세요.

**④ 무상태(Stateless)**

서버는 이전 요청을 기억하지 않습니다. 매 요청은 그 자체로 처리에 필요한 모든 정보(인증 토큰, 파라미터 등)를 담아야 합니다.
이 원칙 덕분에 Lambda처럼 **요청마다 다른 인스턴스에서 실행되는** 환경에서도 REST API가 자연스럽게 동작합니다.

#### 이 레포의 REST API 예시 (`nodejs/serverless.yaml` → `usersApi`)

```
GET    /users          → 사용자 목록 조회
POST   /users          → 사용자 생성       (본문: {"name": "...", "email": "..."})
GET    /users/{id}     → 특정 사용자 조회
PUT    /users/{id}     → 특정 사용자 수정
DELETE /users/{id}     → 특정 사용자 삭제
```

`{id}` 처럼 중괄호로 감싼 부분을 **경로 파라미터(Path Parameter)** 라고 하며, Lambda에서는 `event.pathParameters.id`로 읽습니다.
쿼리 스트링(`?name=Alice`)은 `event.queryStringParameters.name`, 본문은 `event.body`(JSON 문자열)로 전달됩니다.

`curl`로 직접 호출해 보면 이렇게 됩니다.

```bash
# 조회 (GET, 본문 없음)
curl https://<api-id>.execute-api.ap-northeast-2.amazonaws.com/dev/users/42

# 생성 (POST, JSON 본문 + Content-Type 헤더)
curl -X POST https://<api-id>.execute-api.ap-northeast-2.amazonaws.com/dev/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# 삭제 (DELETE)
curl -X DELETE https://<api-id>.execute-api.ap-northeast-2.amazonaws.com/dev/users/42
```

#### API Gateway의 "REST API"와 "HTTP API"

AWS API Gateway에는 두 종류의 API 유형이 있어 이름이 헷갈리기 쉽습니다.

| 유형 | 설명 | 이 레포 |
| ---- | ---- | ---- |
| **REST API** (v1) | 기능이 많고(사용량 계획, 요청 검증, WAF 등) 설정이 세밀함. Serverless Framework의 `events: - http:` | ✅ 사용 |
| **HTTP API** (v2) | 더 가볍고 저렴하며 지연이 낮음. Serverless Framework의 `events: - httpApi:` | 미사용 |

여기서 "REST API"는 AWS의 상품명이며, 위에서 설명한 REST 설계 원칙과는 별개입니다. 두 유형 모두 REST 스타일로 설계할 수 있습니다.

### 3. CORS(Cross-Origin Resource Sharing)란?

실습 중 가장 자주 만나는 오류가 바로 이것입니다.

```
Access to fetch at 'https://abc123.execute-api.ap-northeast-2.amazonaws.com/dev/hello'
from origin 'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

`curl`이나 Postman으로는 잘 되는데 **브라우저의 JavaScript(`fetch`, `axios`)로 호출하면 실패**한다면 거의 100% CORS 문제입니다.

#### 3-1. 출처(Origin)란?

**출처 = 프로토콜 + 호스트(도메인) + 포트** 세 가지의 조합입니다. 하나라도 다르면 "다른 출처(Cross-Origin)"입니다.

| URL | `http://localhost:3000`과 같은 출처인가? | 이유 |
| ---- | ---- | ---- |
| `http://localhost:3000/page.html` | ✅ 같음 | 경로만 다름 |
| `https://localhost:3000` | ❌ 다름 | 프로토콜(http ≠ https) |
| `http://localhost:8080` | ❌ 다름 | 포트(3000 ≠ 8080) |
| `http://127.0.0.1:3000` | ❌ 다름 | 호스트(localhost ≠ 127.0.0.1) |
| `https://abc123.execute-api.ap-northeast-2.amazonaws.com` | ❌ 다름 | 전부 다름 |

#### 3-2. 왜 브라우저가 막는가? — 동일 출처 정책(Same-Origin Policy)

브라우저에는 **"웹 페이지의 스크립트는 자기 출처의 자원만 읽을 수 있다"** 는 보안 규칙이 기본으로 켜져 있습니다.
이것이 없다면, 악성 사이트 `evil.com`의 스크립트가 여러분이 로그인해 둔 `bank.com`의 API를 몰래 호출해 계좌 정보를 읽어갈 수 있습니다.

그런데 정상적인 서비스에서도 프론트엔드(`localhost:3000` 또는 `myapp.com`)와 백엔드 API(`xxx.execute-api.amazonaws.com`)의 출처가 다른 경우가 대부분입니다.
그래서 **"서버가 명시적으로 허락한 출처에 한해 브라우저가 예외를 허용하는 방법"** 이 필요하고, 그 표준이 CORS입니다.

핵심을 정리하면 다음과 같습니다.

- CORS 검사는 **브라우저만** 수행합니다. `curl`, Postman, 서버 간 호출, Lambda → Lambda 호출에는 CORS가 전혀 관여하지 않습니다.
- 요청은 실제로 서버까지 도달하고 Lambda도 실행됩니다. 다만 **응답이 돌아온 뒤 브라우저가 응답 헤더를 검사해서 JavaScript에 넘겨줄지 말지를 결정**합니다.
- 허락 여부는 **서버가 응답 헤더로** 알려줍니다. 따라서 CORS 오류는 프론트엔드 코드가 아니라 **서버(Lambda / API Gateway) 쪽 설정**으로 해결합니다.

#### 3-3. 동작 방식

**(A) 단순 요청(Simple Request)** — `GET`, `HEAD`, 또는 `Content-Type`이 폼 형식인 `POST`이고 커스텀 헤더가 없는 경우

```
브라우저 (localhost:3000)                          API Gateway + Lambda
      │                                                    │
      │ ── GET /dev/hello  (Origin: http://localhost:3000) ──▶ │
      │                                                    │  Lambda 실행
      │ ◀── 200 OK                                        │
      │     Access-Control-Allow-Origin: *   ◀── 이 헤더가 있어야 JS가 응답을 읽을 수 있음
      │     {"message": "Hello, Alice!"}                  │
```

브라우저는 요청에 `Origin` 헤더를 자동으로 붙여 보내고, 응답의 `Access-Control-Allow-Origin` 값이 `*` 이거나 자신의 출처와 일치하면 응답을 JavaScript에 전달합니다. 헤더가 없으면 위의 오류를 냅니다.

**(B) 사전 요청(Preflight Request)** — `PUT`, `DELETE`, `PATCH`, 또는 `Content-Type: application/json`인 `POST`, 또는 `Authorization` 같은 커스텀 헤더가 있는 경우

브라우저는 실제 요청을 보내기 **전에** `OPTIONS` 메서드로 "이런 요청 보내도 되나요?"라고 먼저 물어봅니다.

```
브라우저 (localhost:3000)                          API Gateway
      │                                                    │
      │ ── ① OPTIONS /dev/users  ────────────────────────▶ │  ← 사전 요청 (Lambda 미실행)
      │       Origin: http://localhost:3000                │
      │       Access-Control-Request-Method: POST          │
      │       Access-Control-Request-Headers: content-type │
      │                                                    │
      │ ◀── ② 200 OK  ─────────────────────────────────── │  ← API Gateway가 MOCK 통합으로 응답
      │       Access-Control-Allow-Origin: *               │
      │       Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
      │       Access-Control-Allow-Headers: Content-Type,Authorization,...
      │                                                    │
      │ ── ③ POST /dev/users  (실제 요청) ────────────────▶ │  → Lambda 실행
      │       Content-Type: application/json               │
      │       {"name": "Alice"}                            │
      │                                                    │
      │ ◀── ④ 201 Created                                  │
      │       Access-Control-Allow-Origin: *  ◀── 실제 응답에도 헤더 필요
```

> ⚠️ 흔한 함정: **사전 요청(①②)과 실제 응답(④) 양쪽 모두** CORS 헤더가 있어야 합니다. `OPTIONS`는 API Gateway가 처리하고, 실제 응답 헤더는 Lambda 코드가 직접 넣어야 하므로 **두 군데를 모두 설정**해야 합니다.

#### 3-4. CORS 관련 응답 헤더 정리

| 헤더 | 의미 | 예시 값 |
| ---- | ---- | ---- |
| `Access-Control-Allow-Origin` | 허용할 출처. `*`는 모든 출처 허용 | `*` 또는 `https://myapp.com` |
| `Access-Control-Allow-Methods` | 허용할 HTTP 메서드 (사전 요청 응답용) | `GET,POST,PUT,DELETE,OPTIONS` |
| `Access-Control-Allow-Headers` | 클라이언트가 보내도 되는 헤더 (사전 요청 응답용) | `Content-Type,Authorization` |
| `Access-Control-Allow-Credentials` | 쿠키·인증 정보 포함 허용. `true`일 때는 Origin에 `*`를 쓸 수 없음 | `true` |
| `Access-Control-Max-Age` | 사전 요청 결과를 브라우저가 캐시할 초 단위 시간 | `86400` |

#### 3-5. 이 레포에서 CORS가 설정된 위치

**① API Gateway 쪽 (사전 요청 OPTIONS 처리)** — 각 `serverless.yaml`의 `cors: true`

```yaml
functions:
  usersApi:
    handler: handler.usersApi
    events:
      - http:
          path: users
          method: post
          cors: true      # ← OPTIONS 메서드와 CORS 응답 헤더를 API Gateway에 자동 생성
```

`cors: true` 한 줄이면 Serverless Framework가 해당 경로에 `OPTIONS` 메서드(MOCK 통합)를 추가하고
`Access-Control-Allow-Origin: *`, `Allow-Methods`, `Allow-Headers`를 포함한 사전 요청 응답을 구성해 줍니다.
허용 출처를 제한하려면 다음과 같이 객체 형태로 적습니다.

```yaml
      - http:
          path: users
          method: post
          cors:
            origin: "https://myapp.com"
            headers:
              - Content-Type
              - Authorization
            allowCredentials: false
```

**② Lambda 쪽 (실제 응답에 헤더 삽입)** — `nodejs/handler.js`의 `response()` 헬퍼

```js
function response(statusCode, body) {
  return {
    statusCode,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",                       // ← 실제 응답용 CORS 헤더
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    },
    body: JSON.stringify(body),
  };
}
```

Java의 `HelloHandler.java`도 동일하게 `headers.put("Access-Control-Allow-Origin", "*")`를 넣고 있습니다.
반면 `python/handler.py`의 기본 `hello` 함수는 `Content-Type`만 반환하므로, 브라우저에서 호출하려면 아래처럼 헤더를 추가해야 합니다.

```python
return {
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",   # ← 추가
    },
    "body": json.dumps(body),
}
```

**③ AWS 콘솔 / CLI로 직접 API Gateway를 만든 경우**

콘솔에서 리소스를 선택한 뒤 **"CORS 활성화"** 버튼을 누르면 ①과 같은 OPTIONS 메서드가 생성됩니다.
단, 이 작업 후에는 반드시 **API를 스테이지에 다시 배포**해야 반영됩니다. ("설정은 했는데 여전히 CORS 오류"의 가장 흔한 원인)

#### 3-6. CORS 오류 체크리스트

| 증상 | 확인할 것 |
| ---- | ---- |
| `curl`은 되는데 브라우저만 안 됨 | CORS 문제 맞음. 아래 항목 순서대로 확인 |
| `No 'Access-Control-Allow-Origin' header` | Lambda 응답 `headers`에 `Access-Control-Allow-Origin` 넣었는지 |
| `Response to preflight request doesn't pass` | `serverless.yaml`에 `cors: true` 있는지 / 콘솔에서 CORS 활성화 후 재배포했는지 |
| `Method OPTIONS is not allowed` | 해당 경로에 OPTIONS 메서드가 없음. `cors: true` 추가 후 `serverless deploy` |
| 500 에러인데 CORS 오류로 보임 | Lambda가 예외로 죽으면 헤더 없이 응답되어 CORS 오류처럼 보임. CloudWatch 로그 먼저 확인 |
| 인증 쿠키가 안 넘어감 | `Allow-Credentials: true` + `Allow-Origin`에 `*` 대신 구체적 출처 지정 + 클라이언트 `credentials: "include"` |

> 🔒 **운영 환경 권고**: 실습에서는 편의상 `Access-Control-Allow-Origin: *`를 사용하지만, 실제 서비스에서는 프론트엔드의 정확한 출처(예: `https://myapp.com`)만 허용하세요.

### 4. API 보안을 위한 SSL/TLS와 HTTPS

CORS가 "브라우저가 누구의 요청을 허용할지"에 관한 것이라면, SSL/TLS는 **"오가는 데이터를 중간에서 누가 훔쳐보거나 바꾸지 못하게 하는 것"** 에 관한 것입니다.
API를 인터넷에 공개하는 순간 이 두 가지는 함께 고려해야 합니다.

#### 4-1. 왜 HTTP가 아니라 HTTPS여야 하는가?

HTTP는 요청과 응답을 **평문(plain text)** 으로 보냅니다. 같은 Wi-Fi에 있는 사람, ISP, 중간 라우터 어디서든 내용을 그대로 볼 수 있습니다.

```
[HTTP]  브라우저 ──── POST /users {"email":"alice@x.com","password":"1234"} ────▶ 서버
                         ▲ 카페 Wi-Fi, 통신사, 프록시 … 누구나 읽고 바꿀 수 있음

[HTTPS] 브라우저 ──── 8f3a9c…(암호화된 바이트) ──────────────────────────────▶ 서버
                         ▲ 내용을 읽을 수도, 바꿀 수도, 서버를 사칭할 수도 없음
```

SSL/TLS(Secure Sockets Layer / Transport Layer Security)는 HTTP 아래에 깔려 다음 세 가지를 보장합니다. SSL은 옛 이름이고 현재 실제로 쓰이는 프로토콜은 **TLS 1.2 / 1.3** 이지만, 관용적으로 "SSL 인증서"라고 부릅니다.

| 보장 | 의미 | 없으면 생기는 문제 |
| ---- | ---- | ---- |
| **기밀성(Confidentiality)** | 본문·헤더·쿼리 스트링이 암호화됨 | 비밀번호, API 키, `Authorization` 토큰 유출 |
| **무결성(Integrity)** | 전송 중 데이터가 바뀌면 즉시 감지됨 | 응답 JSON에 악성 스크립트 삽입, 결제 금액 변조 |
| **서버 인증(Authentication)** | 접속한 서버가 진짜 `api.myapp.com`인지 인증서로 검증 | 가짜 서버로 유도하는 중간자(MITM) 공격, 피싱 |

API 관점에서 HTTPS가 특히 중요한 이유는 다음과 같습니다.

- **인증 토큰이 헤더에 실린다.** `Authorization: Bearer eyJ...` 는 이 값만 있으면 누구나 그 사용자인 척할 수 있습니다. HTTP로 보내면 토큰이 그대로 노출됩니다.
- **쿼리 스트링도 노출된다.** `GET /users?apiKey=abcd1234` 같은 요청은 HTTP에서는 URL 전체가 평문입니다. HTTPS에서는 호스트 이름만 보이고 경로·쿼리는 암호화됩니다.
- **브라우저 기능 제약.** 최신 브라우저는 HTTP 페이지에서 Geolocation, Service Worker, 카메라 등 다수의 API를 차단하고, HTTPS 페이지에서 HTTP API를 호출하면 **혼합 콘텐츠(Mixed Content)** 로 막습니다. 즉 프론트엔드가 HTTPS면 백엔드 API도 반드시 HTTPS여야 합니다.
- **HTTP/2, HTTP/3는 사실상 HTTPS 전용.** 성능 향상도 TLS 위에서만 얻을 수 있습니다.

#### 4-2. TLS 동작 원리 요약

TLS는 접속 초기에 **핸드셰이크(handshake)** 로 서버를 검증하고 세션 키를 합의한 뒤, 이후 모든 데이터를 그 키로 대칭 암호화합니다.

```
브라우저                                                      서버 (api.myapp.com)
   │                                                               │
   │ ── ① ClientHello: 지원하는 TLS 버전·암호 스위트 목록 ────────▶ │
   │                                                               │
   │ ◀── ② ServerHello + 인증서(공개키 포함, CA가 서명) ────────── │
   │                                                               │
   │  ③ 인증서 검증                                                │
   │     · 도메인 이름이 api.myapp.com과 일치하는가?               │
   │     · 유효 기간 안인가?                                       │
   │     · 신뢰하는 CA(인증 기관)의 서명인가? (OS/브라우저 내장 목록) │
   │                                                               │
   │ ── ④ 키 교환(ECDHE): 양쪽이 같은 세션 키를 계산 ─────────────▶ │
   │                                                               │
   │ ═══ ⑤ 이후 HTTP 요청/응답은 세션 키로 대칭 암호화 ═══════════ │
```

핵심 용어

| 용어 | 설명 |
| ---- | ---- |
| **인증서(Certificate)** | "이 공개키는 `api.myapp.com`의 것이다"라고 CA가 서명한 파일. 도메인 이름, 공개키, 유효 기간, 발급자 포함 |
| **CA(Certificate Authority)** | 인증서를 발급·서명하는 신뢰 기관. Let's Encrypt, DigiCert, **Amazon(ACM)** 등 |
| **인증서 체인** | 서버 인증서 → 중간 CA → 루트 CA 순으로 서명이 이어짐. 브라우저는 루트 CA 목록을 내장하고 있어 체인을 따라 검증 |
| **TLS 종료(TLS Termination)** | 암호화를 풀어주는 지점. API Gateway·ALB·CloudFront가 이 역할을 대신하므로 **Lambda 코드는 암호화를 전혀 신경 쓰지 않아도 됨** |
| **ACM(AWS Certificate Manager)** | AWS가 무료로 공개 인증서를 발급·자동 갱신해 주는 서비스. API Gateway, ALB, CloudFront에 바로 연결 가능 (EC2에는 직접 설치 불가) |

> 💡 실습에서 "SSL 인증서를 사야 하나?"라는 질문이 자주 나옵니다. AWS 관리형 서비스(API Gateway, ALB, CloudFront)에 붙일 인증서는 **ACM에서 무료**이며 갱신도 자동입니다. 필요한 것은 **본인 소유의 도메인** 뿐입니다.

#### 4-3. API Gateway는 기본적으로 HTTPS 전용이다

API Gateway가 만들어 주는 기본 엔드포인트는 **HTTP를 아예 받지 않습니다.** 아래처럼 호출하면 연결 자체가 거부됩니다.

```bash
# HTTPS — 정상
curl https://abc123.execute-api.ap-northeast-2.amazonaws.com/dev/hello

# HTTP — 연결 거부 (API Gateway는 80번 포트를 열지 않음)
curl http://abc123.execute-api.ap-northeast-2.amazonaws.com/dev/hello
# curl: (7) Failed to connect ... port 80
```

`*.execute-api.amazonaws.com` 도메인에 대한 인증서는 AWS가 관리하므로, 실습용으로는 **아무 설정 없이 이미 HTTPS가 적용된 상태**입니다.
다만 운영 환경에서는 다음 이유로 **사용자 지정 도메인(Custom Domain)** 을 붙이는 것이 일반적입니다.

- `abc123.execute-api...` 대신 `api.myapp.com` 같은 읽기 쉬운 주소 사용
- API를 다시 만들어 ID가 바뀌어도 클라이언트 주소는 유지
- CORS `Allow-Origin`, 쿠키 도메인 등을 자사 도메인 기준으로 정리
- TLS 최소 버전(`TLS_1_2`) 정책 지정, 인증서 직접 관리

**사용자 지정 도메인 연결 절차 (AWS CLI, 리전 엔드포인트 기준)**

```bash
# ① ACM에서 인증서 요청 (REGIONAL API는 API와 같은 리전, EDGE API는 반드시 us-east-1)
aws acm request-certificate \
  --domain-name api.myapp.com \
  --validation-method DNS \
  --region ap-northeast-2
# → 출력된 CNAME 레코드를 Route 53(또는 도메인 등록 업체 DNS)에 추가하면 몇 분 내 ISSUED 상태가 됨

# ② API Gateway에 도메인 등록 + 인증서 연결 + TLS 1.2 이상 강제
aws apigateway create-domain-name \
  --domain-name api.myapp.com \
  --regional-certificate-arn arn:aws:acm:ap-northeast-2:123456789012:certificate/xxxx \
  --endpoint-configuration types=REGIONAL \
  --security-policy TLS_1_2 \
  --region ap-northeast-2
# → 응답의 regionalDomainName (d-xxxx.execute-api.ap-northeast-2.amazonaws.com) 와
#    regionalHostedZoneId 를 메모

# ③ 도메인 ↔ API 스테이지 매핑 (api.myapp.com/  →  <rest-api-id>/dev)
aws apigateway create-base-path-mapping \
  --domain-name api.myapp.com \
  --rest-api-id abc123 \
  --stage dev \
  --region ap-northeast-2

# ④ Route 53에 ALIAS 레코드 추가: api.myapp.com → regionalDomainName
aws route53 change-resource-record-sets \
  --hosted-zone-id Z0123456789ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.myapp.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "<regionalHostedZoneId>",
          "DNSName": "<regionalDomainName>",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'

# ⑤ 확인
curl -v https://api.myapp.com/hello?name=Alice 2>&1 | grep -E "SSL connection|subject:|HTTP/"
```

**Serverless Framework로 자동화** — `serverless-domain-manager` 플러그인을 쓰면 위 ②~④를 `serverless.yaml`에서 선언합니다.

```yaml
plugins:
  - serverless-domain-manager

custom:
  customDomain:
    domainName: api.myapp.com
    certificateName: api.myapp.com   # ACM에 발급된 인증서 이름
    endpointType: regional
    securityPolicy: tls_1_2
    basePath: ""
    stage: ${sls:stage}
    createRoute53Record: true
```

```bash
npm i -D serverless-domain-manager
sls create_domain      # 도메인·인증서·Route 53 레코드 생성 (최초 1회, 수십 분 소요 가능)
sls deploy             # 이후 배포마다 base path mapping 자동 갱신
```

#### 4-4. API Gateway와 HTTPS 로드밸런서를 함께 쓰는 세 가지 패턴

"API Gateway에 로드밸런서를 붙인다"는 말은 실제로는 **어느 쪽이 앞에 서느냐**에 따라 세 가지 다른 구성을 의미합니다.
먼저 알아둘 제약이 하나 있습니다.

> ⚠️ **ALB는 API Gateway의 공개 엔드포인트를 직접 대상(target)으로 등록할 수 없습니다.** ALB 대상 그룹의 유형은 `instance`, `ip`, `lambda` 세 가지뿐입니다.
> 따라서 "ALB → API Gateway" 형태를 원한다면 ALB가 API Gateway를 건너뛰고 **Lambda를 직접 호출**하거나(패턴 A), API Gateway 앞에는 ALB 대신 **CloudFront**를 두는 것(패턴 C)이 정석입니다.

| 패턴 | 구성 | 언제 쓰는가 |
| ---- | ---- | ---- |
| **A. ALB → Lambda** | API Gateway 없이 ALB가 TLS 종료 + 라우팅 + Lambda 호출 | 이미 ALB 뒤에 EC2/ECS 서비스가 있고, 같은 도메인의 일부 경로만 Lambda로 처리하고 싶을 때. 요청량이 매우 많아 API Gateway 요금이 부담될 때 |
| **B. API Gateway → VPC Link → NLB/ALB** | API Gateway가 앞, 로드밸런서는 VPC 안 백엔드(EC2/ECS) 앞 | Lambda와 기존 VPC 서비스(Spring Boot, Django 등)를 **하나의 API Gateway 도메인**으로 통합할 때 |
| **C. CloudFront → API Gateway** | CloudFront가 전 세계 엣지에서 TLS 종료 + 캐시 + WAF | 글로벌 사용자 지연 감소, 응답 캐싱, DDoS/WAF 보호, 정적 사이트(S3)와 API를 같은 도메인으로 묶을 때 |

전체 그림으로 보면 다음과 같습니다.

```
                    [패턴 A]                       [패턴 B]                        [패턴 C]

  클라이언트 ── HTTPS ──▶ ALB (ACM 인증서)   클라이언트 ── HTTPS ──▶ API Gateway   클라이언트 ── HTTPS ──▶ CloudFront (ACM, WAF)
                          │ TLS 종료                                │ (ACM)                              │ TLS 종료·캐시
                          ├─ /api/*  ─▶ Lambda                      ├─ /hello   ─▶ Lambda               ├─ /api/*  ─▶ API Gateway ─▶ Lambda
                          └─ /*      ─▶ EC2 / ECS                   └─ /legacy/* ─▶ VPC Link ─▶ NLB     └─ /*      ─▶ S3 (정적 사이트)
                                                                                    └─▶ EC2 / ECS (VPC 내부)
```

#### 4-5. 패턴 A — ALB(HTTPS 리스너) → Lambda 직접 연결

ALB는 Lambda 함수를 대상 그룹에 등록할 수 있습니다. API Gateway 없이도 HTTPS 엔드포인트가 생기며, 같은 ALB의 다른 경로를 EC2/ECS로 보낼 수 있습니다.

```
클라이언트 ── https://api.myapp.com/hello ──▶ ALB ── HTTPS 리스너(443, ACM 인증서) ──┐
                                                  ├── 규칙: path = /hello*  → 대상 그룹(lambda) → hello-nodejs
                                                  ├── 규칙: path = /*       → 대상 그룹(instance) → EC2
                                                  └── HTTP 리스너(80) → 443으로 301 리다이렉트
```

**AWS CLI 절차**

```bash
# ① Lambda용 대상 그룹 생성 (VPC 지정 불필요)
aws elbv2 create-target-group \
  --name hello-lambda-tg \
  --target-type lambda
# → TargetGroupArn 메모

# ② ALB가 Lambda를 호출할 수 있도록 리소스 기반 권한 추가
aws lambda add-permission \
  --function-name hello-nodejs \
  --statement-id alb-invoke \
  --action lambda:InvokeFunction \
  --principal elasticloadbalancing.amazonaws.com \
  --source-arn arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:targetgroup/hello-lambda-tg/xxxx

# ③ Lambda를 대상으로 등록
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:...:targetgroup/hello-lambda-tg/xxxx \
  --targets Id=arn:aws:lambda:ap-northeast-2:123456789012:function:hello-nodejs

# ④ ALB 생성 (퍼블릭 서브넷 2개 이상, 443 인바운드를 허용한 보안 그룹)
aws elbv2 create-load-balancer \
  --name api-alb \
  --scheme internet-facing \
  --subnets subnet-aaaa subnet-bbbb \
  --security-groups sg-xxxx
# → LoadBalancerArn, DNSName 메모

# ⑤ HTTPS 리스너 생성: ACM 인증서 연결 + TLS 1.2/1.3만 허용
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/app/api-alb/xxxx \
  --protocol HTTPS --port 443 \
  --certificates CertificateArn=arn:aws:acm:ap-northeast-2:123456789012:certificate/xxxx \
  --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...:targetgroup/hello-lambda-tg/xxxx

# ⑥ HTTP(80) → HTTPS(443) 강제 리다이렉트 리스너
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/app/api-alb/xxxx \
  --protocol HTTP --port 80 \
  --default-actions 'Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'

# ⑦ Route 53: api.myapp.com → ALB DNSName (A ALIAS)
# ⑧ 확인
curl -I https://api.myapp.com/hello?name=Alice
curl -I http://api.myapp.com/hello           # → 301 Location: https://...
```

**Serverless Framework로 선언** — 이미 존재하는 ALB 리스너에 규칙만 추가합니다.

```yaml
functions:
  hello:
    handler: index.handler
    events:
      - alb:
          listenerArn: arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:listener/app/api-alb/xxxx/yyyy
          priority: 10
          conditions:
            path: /hello
            method:
              - GET
```

**ALB 이벤트는 API Gateway 이벤트와 형식이 조금 다릅니다.** 같은 Lambda를 두 경로로 노출한다면 아래 차이를 처리해야 합니다.

| 항목 | API Gateway (REST, Proxy 통합) | ALB |
| ---- | ---- | ---- |
| 요청 구분 | `event.requestContext.apiId` | `event.requestContext.elb.targetGroupArn` |
| 경로 파라미터 | `event.pathParameters.id` 자동 파싱 | **없음.** `event.path`를 직접 파싱해야 함 |
| 쿼리 스트링 | `queryStringParameters` | `queryStringParameters` (URL 인코딩된 상태로 전달) |
| 응답 `statusDescription` | 불필요 | `"200 OK"` 형태로 넣는 것을 권장 |
| 응답 크기 제한 | 10 MB | **1 MB** |
| 타임아웃 | 29초 | ALB 유휴 타임아웃(기본 60초) |
| CORS | `cors: true`로 OPTIONS 자동 생성 | **자동 처리 없음.** Lambda에서 OPTIONS 요청에 직접 응답해야 함 |

`nodejs/handler.js`의 `response()` 헬퍼는 두 경우 모두에서 그대로 동작합니다. ALB에서 CORS 사전 요청을 받으려면 핸들러 앞부분에 다음을 추가하면 됩니다.

```js
if (event.httpMethod === "OPTIONS") {
  return response(204, "");   // headers에 Access-Control-Allow-* 가 이미 포함됨
}
```

#### 4-6. 패턴 B — API Gateway → VPC Link → NLB/ALB (VPC 내부 백엔드 연결)

Lambda 외에 VPC 안에서 돌고 있는 EC2·ECS 서비스(예: Spring Boot, Django)를 **같은 API Gateway 도메인 아래**에 두고 싶을 때 씁니다.
API Gateway는 인터넷에서 TLS를 종료하고, VPC Link라는 프라이빗 터널을 통해 VPC 내부 로드밸런서로 요청을 넘깁니다. 백엔드는 인터넷에 노출되지 않습니다.

```
클라이언트 ── HTTPS ──▶ API Gateway (REST API, ACM)
                          ├─ GET  /hello          ─▶ Lambda (hello-nodejs)
                          └─ ANY  /legacy/{proxy+} ─▶ VPC Link ─▶ 내부 NLB ─▶ EC2 / ECS (프라이빗 서브넷)
                                                       (인터넷 미노출)
```

| API 유형 | VPC Link가 연결할 수 있는 로드밸런서 |
| ---- | ---- |
| REST API (v1) — 이 레포 | **NLB(Network Load Balancer)** 만 가능 |
| HTTP API (v2) | ALB, NLB, Cloud Map 모두 가능 |

**AWS CLI 절차 (REST API + 내부 NLB)**

```bash
# ① VPC 내부용 NLB가 이미 있다고 가정 (scheme: internal, 대상: EC2/ECS)
# ② VPC Link 생성 (수 분 소요, status가 AVAILABLE 될 때까지 대기)
aws apigateway create-vpc-link \
  --name legacy-link \
  --target-arns arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:loadbalancer/net/internal-nlb/xxxx
# → VpcLinkId 메모

# ③ /legacy/{proxy+} 리소스에 HTTP_PROXY 통합을 VPC_LINK 방식으로 연결
aws apigateway put-integration \
  --rest-api-id abc123 \
  --resource-id <legacy-proxy-resource-id> \
  --http-method ANY \
  --type HTTP_PROXY \
  --integration-http-method ANY \
  --connection-type VPC_LINK \
  --connection-id <VpcLinkId> \
  --uri 'http://internal-nlb-xxxx.elb.ap-northeast-2.amazonaws.com/{proxy}' \
  --request-parameters '{"integration.request.path.proxy":"method.request.path.proxy"}'

# ④ 스테이지 재배포
aws apigateway create-deployment --rest-api-id abc123 --stage-name dev
```

**Serverless Framework로 선언**

```yaml
functions:
  hello:
    handler: index.handler
    events:
      - http: { path: hello, method: get, cors: true }

# Lambda 없이 순수 프록시 라우트는 serverless-apigateway-route 계열 플러그인 또는
# resources 블록(CloudFormation)으로 선언합니다.
resources:
  Resources:
    LegacyVpcLink:
      Type: AWS::ApiGateway::VpcLink
      Properties:
        Name: legacy-link
        TargetArns:
          - arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:loadbalancer/net/internal-nlb/xxxx
```

> 💡 이 구성에서 API Gateway ↔ NLB 구간은 AWS 내부망(PrivateLink)이라 HTTP로 두어도 인터넷에 노출되지 않습니다. 다만 규정상 종단 간 암호화가 필요하면 NLB에 TLS 리스너를 두고 `--uri`를 `https://`로 지정합니다.

#### 4-7. 패턴 C — CloudFront → API Gateway (엣지 HTTPS + 캐시 + WAF)

CloudFront는 전 세계 엣지 로케이션에서 TLS를 종료하는 CDN이며, API Gateway를 오리진(origin)으로 둘 수 있습니다. 로드밸런서는 아니지만 "API Gateway 앞에 HTTPS 계층을 하나 더 두는" 목적으로 가장 흔히 쓰이는 방식입니다.

```
사용자(서울) ─┐                                  ┌─ /api/*  ─▶ API Gateway (ap-northeast-2) ─▶ Lambda
사용자(도쿄) ─┼─ HTTPS ─▶ CloudFront (엣지, ACM us-east-1, WAF) ─┤
사용자(LA)  ─┘            · TLS 종료 · GET 응답 캐시 · 지리 차단      └─ /*      ─▶ S3 (React/Vue 정적 사이트)
```

장점

- **같은 도메인에서 프론트엔드와 API 제공** → 출처가 같아지므로 **CORS 설정 자체가 불필요**해짐
- `GET /prices` 같은 읽기 응답을 엣지에 캐시해 Lambda 호출 수와 지연 감소
- AWS WAF 연결로 SQL 인젝션·봇·Rate Limit 차단, AWS Shield로 DDoS 방어
- 인증서는 **us-east-1 리전의 ACM**에서 발급해야 함 (CloudFront 제약)

**핵심 설정 (AWS CLI)**

```bash
# ① us-east-1에 인증서 발급
aws acm request-certificate --domain-name myapp.com \
  --subject-alternative-names "*.myapp.com" \
  --validation-method DNS --region us-east-1

# ② CloudFront 배포 생성 시 오리진과 동작(behavior)을 지정
#    - 오리진 1: abc123.execute-api.ap-northeast-2.amazonaws.com  (OriginPath: /dev, 프로토콜: https-only)
#    - 오리진 2: myapp-site.s3.ap-northeast-2.amazonaws.com
#    - 동작: /api/*  → 오리진 1, 캐시 정책: CachingDisabled(또는 GET만 TTL 부여),
#            오리진 요청 정책: AllViewerExceptHostHeader  ← Host 헤더를 넘기면 API Gateway가 403 반환
#    - 동작: /*      → 오리진 2
#    - ViewerProtocolPolicy: redirect-to-https
#    - ViewerCertificate: ①의 ACM ARN, MinimumProtocolVersion: TLSv1.2_2021
aws cloudfront create-distribution --distribution-config file://cf-config.json

# ③ Route 53: myapp.com → CloudFront 도메인(dxxxx.cloudfront.net) A ALIAS
```

> ⚠️ CloudFront 뒤에 API Gateway를 둘 때 가장 흔한 실수 두 가지: **(1)** 오리진 경로에 스테이지(`/dev`)를 빠뜨려 `{"message":"Missing Authentication Token"}` 발생, **(2)** `Host` 헤더를 그대로 전달해 API Gateway가 `403 Forbidden` 반환. 오리진 요청 정책에서 Host 헤더를 제외해야 합니다.

#### 4-8. HTTPS·로드밸런서 관련 체크리스트

| 상황 | 확인할 것 |
| ---- | ---- |
| `curl: (60) SSL certificate problem` | 인증서 도메인과 호출 주소 불일치, 또는 ACM 인증서가 아직 `PENDING_VALIDATION` |
| 브라우저 "안전하지 않음" 경고 | 자체 서명 인증서 사용 중. ACM 공개 인증서로 교체 |
| ALB 대상 그룹이 `unhealthy` | Lambda 대상은 상태 검사가 기본 꺼져 있음. Lambda 리소스 권한(`add-permission`)이 빠졌는지 확인 |
| ALB 경유 시 502 | Lambda 응답에 `statusCode`가 없거나 응답이 1 MB 초과. 또는 `isBase64Encoded` 불일치 |
| VPC Link 통합 시 504 | NLB 대상 EC2의 보안 그룹이 NLB 서브넷 대역을 허용하지 않음 |
| CloudFront 경유 시 403 | Host 헤더 전달됨 → 오리진 요청 정책 수정. 또는 API Gateway 리소스 정책이 CloudFront IP를 막음 |
| CloudFront 경유 시 `Missing Authentication Token` | 오리진 경로에 스테이지 이름(`/dev`) 누락 |
| HTTP로 호출하면 응답이 없음 | API Gateway는 원래 80번 포트 미지원. ALB/CloudFront에서는 80 → 443 리다이렉트 리스너/정책 추가 |
| TLS 1.0/1.1 클라이언트 차단하고 싶음 | API GW: `--security-policy TLS_1_2`, ALB: `ELBSecurityPolicy-TLS13-1-2-2021-06`, CloudFront: `TLSv1.2_2021` |

> 🔒 **운영 환경 최소 기준**: (1) 모든 엔드포인트 HTTPS 전용 + HTTP는 301 리다이렉트, (2) TLS 1.2 이상만 허용, (3) ACM 인증서 자동 갱신, (4) `Authorization` 토큰·API 키는 절대 쿼리 스트링에 넣지 않고 헤더로 전달, (5) 인터넷 노출 API에는 WAF 또는 API Gateway 사용량 계획(Usage Plan)으로 Rate Limit 적용.

---

## 기술 스택

### 런타임 및 언어

| 언어    | 버전     | Lambda 런타임 식별자 | 핸들러 진입점                |
| ------- | -------- | -------------------- | ---------------------------- |
| Node.js | 20.x     | `nodejs20.x`       | `index.handler`            |
| Python  | 3.12     | `python3.12`       | `handler.hello`            |
| Java    | 17 (LTS) | `java17`           | `com.example.HelloHandler` |

### AWS 서비스

| 서비스                           | 역할                                                                        |
| -------------------------------- | --------------------------------------------------------------------------- |
| **AWS Lambda**             | 서버리스 함수 실행 환경. 요청 시에만 컨테이너를 띄워 코드를 실행하고 과금   |
| **Amazon API Gateway**     | HTTP 요청을 Lambda로 라우팅하는 관리형 API 엔드포인트 (REST API / HTTP API) |
| **Amazon S3**              | 객체 스토리지. Lambda의 이벤트 트리거 소스로도 활용                         |
| **Amazon CloudWatch Logs** | Lambda 실행 로그 자동 수집 및 조회                                          |
| **AWS IAM**                | Lambda 실행 역할, 사용자 권한 정책 관리                                     |
| **AWS CloudFormation**     | Serverless Framework 배포 시 내부적으로 사용하는 인프라 프로비저닝 엔진     |

### 배포 도구

| 도구                           | 버전 | 용도                                                                                  |
| ------------------------------ | ---- | ------------------------------------------------------------------------------------- |
| **AWS CLI**              | v2   | Lambda 함수 생성·업데이트·호출, API Gateway 설정 등 모든 AWS 작업을 터미널에서 수행 |
| **Serverless Framework** | 3.x  | `serverless.yaml` 하나로 Lambda + API Gateway + IAM 역할을 자동 생성·배포          |
| **GitHub Actions**       | —   | `main` 브랜치 push 시 변경된 언어 디렉터리만 자동 감지하여 Lambda에 배포            |
| **Apache Maven**         | 3.8+ | Java 빌드 및 의존성 관리.`maven-shade-plugin`으로 Lambda용 Fat JAR 생성             |

### AWS SDK

| SDK                    | 버전                        | 언어    | 용도                                                             |
| ---------------------- | --------------------------- | ------- | ---------------------------------------------------------------- |
| AWS SDK for JavaScript | v2 (`aws-sdk`)            | Node.js | S3 업로드 스크립트 (`upload.js`) — 유지보수 모드              |
| AWS SDK for JavaScript | v3 (`@aws-sdk/client-s3`) | Node.js | S3 업로드 스크립트 (`upload2.js`, `upload3.js`) — 권장 버전 |
| Boto3                  | 최신                        | Python  | S3 이벤트 트리거 Lambda 내부에서 S3 객체 읽기                    |
| AWS Lambda Java Core   | 1.2.3                       | Java    | `RequestHandler` 인터페이스 및 `Context` 제공                |
| AWS Lambda Java Events | 3.11.4                      | Java    | `APIGatewayProxyRequestEvent` 등 API GW 이벤트 타입 제공       |

### CI/CD 파이프라인 구성 요소

| 구성 요소                                    | 역할                                                  |
| -------------------------------------------- | ----------------------------------------------------- |
| `aws-actions/configure-aws-credentials@v4` | GitHub Actions 실행기에 AWS 자격 증명을 안전하게 주입 |
| `actions/setup-java@v4`                    | Java 빌드 환경 세팅 (Temurin JDK 17, Maven 캐시)      |
| `git diff --name-only`                     | 변경된 파일 목록으로 배포 대상 디렉터리 감지          |
| `aws lambda update-function-code`          | ZIP 또는 JAR를 Lambda에 업로드                        |
| `aws lambda wait function-updated`         | 배포 완료까지 대기 (최대 5분)                         |

---

## 아키텍처

### API Gateway + Lambda (Hello API)

```
클라이언트 (브라우저 / curl / Postman)
        │
        │  HTTP GET /hello?name=Alice
        ▼
┌────────────────────────────────────┐
│         Amazon API Gateway         │
│  REST API  ·  스테이지: dev        │
│  리소스: /hello  ·  메서드: GET    │
│  통합 유형: Lambda Proxy           │
└──────────────────┬─────────────────┘
                   │  event 객체 전달
                   ▼
┌────────────────────────────────────┐
│           AWS Lambda               │
│  런타임: Node.js / Python / Java   │
│  핸들러: index.handler 등          │
│  메모리: 128 MB (Java: 512 MB)     │
│  타임아웃: 3 s (Java: 15 s)        │
└──────────┬─────────────────────────┘
           │  로그 자동 전송
           ▼
┌────────────────────────────────────┐
│       Amazon CloudWatch Logs       │
│  로그 그룹: /aws/lambda/<함수명>    │
└────────────────────────────────────┘
```

### S3 이벤트 트리거 + Lambda

```
사용자
  │  aws s3 cp face1.png s3://edumgt-bucket-logs/
  ▼
┌──────────────────┐     ObjectCreated 이벤트
│    Amazon S3     │ ──────────────────────────▶ ┌──────────────────┐
│  edumgt-bucket-  │                             │   AWS Lambda     │
│  logs            │                             │  s3-event-logger │
└──────────────────┘                             └────────┬─────────┘
                                                          │  로그 기록
                                                          ▼
                                                 ┌──────────────────┐
                                                 │  CloudWatch Logs │
                                                 └──────────────────┘
```

### 주가 데이터 AI/ML 파이프라인 (Stock Pipeline)

```mermaid
flowchart TD
    EB["⏰ EventBridge Scheduler<br/>매일 16:00 KST<br/>장 마감 후 자동 트리거"]

    subgraph SFN["AWS Step Functions — 워크플로우 제어"]
        direction TB

        subgraph S1["Step 1 · 수집"]
            BC["AWS Batch<br/>Collect Job<br/>(Fargate)"]
        end

        subgraph S2["Step 2 · 정제 (병렬)"]
            direction LR
            BR["AWS Batch<br/>Refine Job<br/>(Fargate)"]
            GL["AWS Glue<br/>ETL Job<br/>(Spark)"]
        end

        subgraph S3["Step 3 · AI/ML 분석"]
            SM["Amazon SageMaker<br/>ML Pipeline<br/>(XGBoost)"]
        end

        S1 --> S2
        S2 --> S3
    end

    RAW[("Amazon S3<br/>Raw Bucket<br/>CSV · 원시 데이터")]
    PROC[("Amazon S3<br/>Processed Bucket<br/>Parquet · 정제 데이터")]
    DDB[("Amazon DynamoDB<br/>stock-pipeline-analysis<br/>초고속 NoSQL 조회")]

    LM["AWS Lambda<br/>Python 3.12<br/>API Handler"]
    APIGW["Amazon API Gateway<br/>REST API<br/>GET /analysis/{ticker}"]
    CLIENT["Client<br/>App / Web / curl"]

    EB -->|StartExecution| SFN
    BC -->|적재| RAW
    BR -->|읽기| RAW
    BR -->|적재| PROC
    GL -->|읽기| RAW
    GL -->|적재| PROC
    SM -->|읽기| PROC
    SM -->|분석 결과 적재| DDB

    DDB -->|조회| LM
    LM -->|응답| APIGW
    APIGW -->|HTTPS| CLIENT

    style EB    fill:#FF9900,color:#fff,stroke:#FF9900
    style RAW   fill:#569A31,color:#fff,stroke:#569A31
    style PROC  fill:#569A31,color:#fff,stroke:#569A31
    style DDB   fill:#4053D6,color:#fff,stroke:#4053D6
    style LM    fill:#FF9900,color:#fff,stroke:#FF9900
    style APIGW fill:#A020F0,color:#fff,stroke:#A020F0
    style CLIENT fill:#232F3E,color:#fff,stroke:#232F3E
```

#### 데이터 흐름 요약

| 단계        | 서비스                | 입력                | 출력                                  |
| ----------- | --------------------- | ------------------- | ------------------------------------- |
| 트리거      | EventBridge Scheduler | 매일 16:00 KST 크론 | Step Functions 실행                   |
| Step 1 수집 | AWS Batch (Fargate)   | 외부 주가 API       | S3 Raw (CSV)                          |
| Step 2 정제 | AWS Batch + Glue ETL  | S3 Raw              | S3 Processed (Parquet, 이동평균 포함) |
| Step 3 분석 | SageMaker Pipeline    | S3 Processed        | DynamoDB (ML 분석 결과)               |
| API 제공    | Lambda + API Gateway  | DynamoDB 조회       | HTTPS JSON 응답                       |

#### Scripts 구성

```
scripts/
├── 00_config.sh          # 공통 환경변수 및 유틸 함수
├── 01_iam.sh             # IAM 역할·정책 생성
├── 02_s3.sh              # S3 버킷 (Raw / Processed / Scripts)
├── 03_dynamodb.sh        # DynamoDB 테이블 + GSI + TTL
├── 04_batch.sh           # Batch 컴퓨팅 환경·작업 대기열·작업 정의
├── 05_glue.sh            # Glue ETL Job (PySpark)
├── 06_sagemaker.sh       # SageMaker Pipeline
├── 07_lambda_apigw.sh    # Lambda 함수 + API Gateway
├── 08_stepfunctions.sh   # Step Functions 상태 머신
├── 09_eventbridge.sh     # EventBridge 스케줄러
├── deploy_all.sh         # 전체 배포 (순서대로 실행)
├── destroy_all.sh        # 전체 삭제 (역순)
├── lambda/
│   └── handler.py        # Lambda API 핸들러 소스
└── step-functions/
    └── workflow.json     # Step Functions 상태 머신 정의 템플릿
```

**전체 배포:**

```bash
# 기본 (dev 환경)
./scripts/deploy_all.sh

# prod 환경
ENV=prod ./scripts/deploy_all.sh prod
```

---

### GitHub Actions 배포 파이프라인

```
git push → main
     │
     ▼
┌─────────────────────────────────────────────────────┐
│               GitHub Actions                        │
│                                                     │
│  [detect-changes]                                   │
│   git diff HEAD~1 HEAD                              │
│   nodejs/ 변경? → nodejs=true/false                 │
│   python/ 변경? → python=true/false                 │
│   java/   변경? → java=true/false                   │
│       │                                             │
│       ├── nodejs=true ──▶ [deploy-nodejs]           │
│       │                    zip → update-function-code│
│       │                    wait function-updated     │
│       │                                             │
│       ├── python=true ──▶ [deploy-python]           │
│       │                    zip → update-function-code│
│       │                    wait function-updated     │
│       │                                             │
│       └── java=true   ──▶ [deploy-java]             │
│                            mvn package              │
│                            update-function-code     │
│                            wait function-updated    │
└─────────────────────────────────────────────────────┘
     │ (각 잡 병렬 실행)
     ▼
AWS Lambda 함수 코드 업데이트 완료
```

---

## 디렉터리 구조

```
aws-serverless/
├── .github/
│   └── workflows/
│       └── deploy-lambda.yml    # GitHub Actions CI/CD 워크플로
│
├── nodejs/                      # Node.js Lambda 실습
│   ├── handler.js               # Serverless Framework용 핸들러
│   ├── index.js                 # AWS CLI 배포용 핸들러
│   ├── serverless.yaml          # Serverless Framework 설정 (API GW 자동 생성)
│   ├── package.json
│   └── lambda-s3/               # S3 이벤트 트리거 실습
│       ├── index.js             # S3 이벤트 Lambda 핸들러 (Node.js, SDK v2)
│       ├── test.py              # S3 이벤트 Lambda 핸들러 (Python, Boto3)
│       ├── upload.js            # S3 파일 업로드 — AWS SDK v2
│       ├── upload2.js           # S3 파일 업로드 — AWS SDK v3
│       ├── upload3.js           # S3 파일 업로드 — AWS SDK v3 (dotenv 미사용)
│       ├── lamdatest.js         # Lambda 로컬 실행 테스트 유틸
│       ├── trust.json           # IAM 신뢰 정책 (lambda.amazonaws.com)
│       ├── s3log.json           # IAM 권한 정책 (S3 GetObject + CloudWatch Logs)
│       ├── snsnoti.json         # S3 버킷 이벤트 알림 구성
│       ├── s3-event.json        # Lambda 테스트용 S3 이벤트 페이로드
│       ├── response.json        # aws lambda invoke 결과 저장 파일
│       ├── sample.json          # 샘플 테스트 데이터
│       └── face1-4.png          # S3 업로드 테스트용 이미지
│
├── python/                      # Python Lambda 실습
│   ├── handler.py               # 기본 Hello Lambda 핸들러
│   ├── ai_handler.py            # Amazon Comprehend / Rekognition 연동 예제
│   ├── events/
│   │   ├── ai-text-event.json   # 텍스트 AI 분석 테스트 이벤트
│   │   └── ai-image-event.json  # 이미지 레이블 분석 테스트 이벤트
│   └── serverless.yaml          # Serverless Framework 설정
│
├── java/                        # Java Lambda 실습
│   ├── pom.xml                  # Maven 빌드 설정 (maven-shade-plugin으로 Fat JAR)
│   ├── serverless.yaml          # Serverless Framework 설정
│   └── src/main/java/com/example/
│       └── HelloHandler.java    # RequestHandler 구현체
│
└── docs/
    ├── images/                  # 메인 README 스크린샷 (콘솔 가이드)
    └── lambda-s3/
        └── README.md            # Lambda + S3 이벤트 트리거 실습 가이드
```

---

## 사전 준비

| 도구                 | 버전 | 설치 방법                                    |
| -------------------- | ---- | -------------------------------------------- |
| AWS 계정             | —   | [무료 가입](https://aws.amazon.com/free/)     |
| AWS CLI              | v2   | [아래 설치 가이드](#aws-cli-설치-및-설정)     |
| Node.js              | 18+  | [nodejs.org](https://nodejs.org/)             |
| Python               | 3.12 | [python.org](https://www.python.org/)         |
| Java (JDK)           | 17   | [adoptium.net](https://adoptium.net/)         |
| Maven                | 3.8+ | [maven.apache.org](https://maven.apache.org/) |
| Serverless Framework | 3.x  | `npm install -g serverless@3`              |

---

## AWS CLI 설치 및 설정

### 설치

**macOS / Linux**

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

**Windows (PowerShell)**

```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
aws --version
```

### 자격 증명 설정

```bash
aws configure
# AWS Access Key ID     [None]: <YOUR_ACCESS_KEY>
# AWS Secret Access Key [None]: <YOUR_SECRET_KEY>
# Default region name   [None]: ap-northeast-2
# Default output format [None]: json
```

설정 파일은 `~/.aws/credentials`와 `~/.aws/config`에 저장됩니다.

> **보안 팁:** 장기 자격 증명(Access Key) 대신 IAM Identity Center(SSO) 또는 EC2 인스턴스 역할을 권장합니다.

### 설정 확인

```bash
aws sts get-caller-identity
# {
#   "UserId": "AIDAXXXXXXXXXX",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

---

## AWS Lambda 이해

### Lambda란?

AWS Lambda는 **서버를 직접 관리하지 않고 코드를 실행**할 수 있는 이벤트 기반 컴퓨팅 서비스입니다.
함수 코드(ZIP 또는 JAR)를 업로드하면 AWS가 실행 환경 전체를 관리합니다.

| 항목      | 전통적인 서버 (EC2)              | AWS Lambda                |
| --------- | -------------------------------- | ------------------------- |
| 서버 관리 | OS 패치, 프로세스 관리 직접 수행 | AWS가 전부 관리           |
| 비용      | 미사용 시간도 과금               | 실행된 시간(ms)만 과금    |
| 확장      | Auto Scaling 직접 설정           | 요청량에 따라 자동 확장   |
| 배포      | ssh + git pull + 재시작          | ZIP 업로드 또는 CLI 한 줄 |
| 유지보수  | 직접 책임                        | 런타임 업데이트만 신경    |

### 핸들러 함수 구조

Lambda는 **이벤트(event)**와 **컨텍스트(context)**를 인자로 받는 함수를 진입점으로 사용합니다.

**Node.js**

```javascript
exports.handler = async (event, context) => {
  // event: 트리거 소스(API GW, S3 등)에서 전달된 데이터
  // context: 함수 이름, 남은 실행 시간, 로그 스트림 이름 등 런타임 정보
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "Hello" }),
  };
};
```

**Python**

```python
def hello(event, context):
    # event: dict 타입, context: LambdaContext 객체
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello"})
    }
```

**Java**

```java
// RequestHandler<입력타입, 출력타입> 인터페이스 구현
public class HelloHandler
        implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {
    @Override
    public APIGatewayProxyResponseEvent handleRequest(
            APIGatewayProxyRequestEvent input, Context context) {
        // input: API Gateway 요청 객체, context: 런타임 정보
        return new APIGatewayProxyResponseEvent().withStatusCode(200).withBody("Hello");
    }
}
```

### 이벤트(event) 객체 구조

API Gateway를 통해 Lambda가 호출될 때 전달되는 `event` 객체 예시:

```json
{
  "httpMethod": "GET",
  "path": "/hello",
  "queryStringParameters": { "name": "Alice" },
  "headers": { "Accept": "application/json" },
  "body": null,
  "isBase64Encoded": false
}
```

S3 이벤트로 호출될 때:

```json
{
  "Records": [{
    "eventSource": "aws:s3",
    "eventName": "ObjectCreated:Put",
    "s3": {
      "bucket": { "name": "edumgt-bucket-logs" },
      "object": { "key": "face1.png", "size": 12345 }
    }
  }]
}
```

### 응답(response) 객체 구조

API Gateway 프록시 통합 사용 시 반드시 아래 형식으로 응답해야 합니다:

```json
{
  "statusCode": 200,
  "headers": { "Content-Type": "application/json" },
  "body": "{\"message\": \"Hello, Alice!\"}"
}
```

> `body`는 반드시 **문자열**이어야 합니다. `JSON.stringify()` 또는 `json.dumps()`로 직렬화하세요.

### 실행 모델: 콜드 스타트 vs 웜 스타트

```
첫 번째 요청 (콜드 스타트)
  컨테이너 생성 → 런타임 초기화 → 핸들러 코드 로드 → 함수 실행
  소요 시간: 수백 ms ~ 수 초 (Java는 특히 길 수 있음)

이후 요청 (웜 스타트)
  기존 컨테이너 재사용 → 함수 실행만 수행
  소요 시간: 수 ms 수준
```

콜드 스타트 최소화 방법:

- Java: 메모리를 512 MB 이상으로 설정
- Node.js / Python: 핸들러 외부에서 무거운 초기화 코드 실행 (컨테이너 재사용 시 재실행 안 됨)
- Lambda SnapStart (Java 21+) 사용

### 주요 제한 사항

| 항목                         | 제한                                  |
| ---------------------------- | ------------------------------------- |
| 함수 코드 패키지 크기 (압축) | 50 MB (직접 업로드), 250 MB (S3 경유) |
| 최대 실행 시간               | 15분                                  |
| 메모리                       | 128 MB ~ 10,240 MB                    |
| 동시 실행 수                 | 기본 1,000 (리전별, 증설 가능)        |
| 환경 변수                    | 최대 4 KB                             |
| `/tmp` 임시 저장소         | 최대 10,240 MB                        |

### IAM 실행 역할

Lambda 함수는 실행 시 **IAM 역할(Execution Role)**을 통해 다른 AWS 서비스에 접근합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

필요한 권한을 역할에 연결합니다:

- 기본 로그 기록: `AWSLambdaBasicExecutionRole`
- S3 읽기: `AmazonS3ReadOnlyAccess`
- CloudWatch 전체: `CloudWatchEventsFullAccess`

---

## Node.js Lambda 배포

### 핸들러 코드 (`nodejs/index.js`)

```javascript
exports.handler = async (event) => {
  const name = event.queryStringParameters?.name || 'World';
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: `Hello, ${name}!` }),
  };
};
```

### Serverless Framework용 핸들러 (`nodejs/handler.js`)

```javascript
module.exports.hello = async (event) => {
  const name = event.queryStringParameters?.name || "Good Morning";
  return {
    statusCode: 200,
    body: JSON.stringify({ message: `Good Morning, ${name}` }),
  };
};
```

### 콘솔 배포 절차

1. **AWS 콘솔 → Lambda → 함수 생성** 클릭
2. **새로 작성** 선택
3. **런타임**: `Node.js 20.x`
4. 코드 탭에 위 핸들러 코드 붙여넣기
5. **배포** → **테스트** 실행

![Lambda 함수 생성 결과](docs/images/image-1.png)

### AWS CLI 배포

**1단계 — 코드 압축**

```bash
cd nodejs

# Linux / macOS
zip function.zip index.js

# Windows PowerShell
Compress-Archive -Path index.js -DestinationPath function.zip
```

**2단계 — Lambda 함수 생성** (최초 1회)

```bash
aws lambda create-function \
  --function-name edumgt-lambda-nodejs \
  --runtime nodejs22.x \
  --role arn:aws:iam::086015456585:role/lambda-test \
  --handler index.handler \
  --zip-file fileb://function.zip \
  --region ap-northeast-2
```

**3단계 — 코드 업데이트** (이후 변경 시)

```bash
aws lambda update-function-code \
  --function-name edumgt-lambda-nodejs \
  --zip-file fileb://function.zip \
  --region ap-northeast-2
```

**4단계 — 함수 호출 테스트**

```bash
aws lambda invoke \
  --function-name edumgt-lambda-nodejs \
  --payload '{"queryStringParameters":{"name":"Alice"}}' \
  --cli-binary-format raw-in-base64-out \
  response.json
cat response.json
# {"statusCode":200,"body":"{\"message\":\"Hello, Alice!\"}"}
```

### Serverless Framework 배포

```bash
npm install -g serverless@3    # 최초 1회 설치

cd nodejs
serverless deploy              # Lambda + API Gateway 자동 생성

# 배포 후 출력 예시:
# endpoints:
#   GET - https://xxxx.execute-api.ap-northeast-2.amazonaws.com/dev/hello
# functions:
#   hello: hello-api-dev-hello

serverless remove              # 생성된 모든 리소스 삭제
```

`nodejs/serverless.yaml`:

```yaml
service: hello-api

provider:
  name: aws
  runtime: nodejs18.x
  region: ap-northeast-2

functions:
  hello:
    handler: handler.hello
    events:
      - http:
          path: hello
          method: get
```

---

## Python Lambda 배포

### 핸들러 코드 (`python/handler.py`)

```python
import json

def hello(event, context):
    query_params = event.get("queryStringParameters") or {}
    name = query_params.get("name", "World")
    body = {"message": f"Hello, {name}!", "language": "Python"}
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
```

### 콘솔 배포 절차

1. **AWS 콘솔 → Lambda → 함수 생성**
2. **런타임**: `Python 3.12`
3. **핸들러** 설정: `handler.hello`
4. **배포** → **테스트** 이벤트:
   ```json
   { "queryStringParameters": { "name": "Alice" } }
   ```

### AWS CLI 배포

```bash
cd python
zip function.zip handler.py

# 함수 생성
aws lambda create-function \
  --function-name edumgt-lambda-python \
  --runtime python3.12 \
  --role arn:aws:iam::<ACCOUNT_ID>:role/<ROLE_NAME> \
  --handler handler.hello \
  --zip-file fileb://function.zip \
  --region ap-northeast-2

# 코드 업데이트
aws lambda update-function-code \
  --function-name edumgt-lambda-python \
  --zip-file fileb://function.zip \
  --region ap-northeast-2

# 호출 테스트
aws lambda invoke \
  --function-name edumgt-lambda-python \
  --payload '{"queryStringParameters":{"name":"Alice"}}' \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

### Serverless Framework 배포

```bash
cd python
serverless deploy
```

`python/serverless.yaml`:

```yaml
service: hello-api-python

provider:
  name: aws
  runtime: python3.12
  region: ap-northeast-2
  stage: ${opt:stage, 'dev'}
  environment:
    AI_DEFAULT_LANGUAGE: ko
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - comprehend:DetectSentiment
            - comprehend:DetectEntities
            - comprehend:DetectPiiEntities
            - rekognition:DetectLabels
          Resource: "*"

functions:
  hello:
    handler: handler.hello
    events:
      - http:
          path: hello
          method: get
          cors: true
```

### AWS AI 리소스 연동 예제

`python/`에는 기본 Hello API 외에도 **Amazon Comprehend**와 **Amazon Rekognition**을 직접 호출하는 Python Lambda 예제가 포함되어 있습니다.

| 엔드포인트 | 연결 서비스 | 입력 | 반환 예시 |
| --- | --- | --- | --- |
| `POST /ai/text/analyze` | Amazon Comprehend | 본문 `text`, `language_code`, `detect_pii` | 감정 분석, 개체명 추출, PII 탐지 |
| `POST /ai/image/labels` | Amazon Rekognition | 본문 `s3_bucket`, `s3_key` 또는 `image_bytes_base64` | 이미지 레이블, 카테고리, 신뢰도 |

관련 파일:

- [`python/ai_handler.py`](python/ai_handler.py)
- [`python/events/ai-text-event.json`](python/events/ai-text-event.json)
- [`python/events/ai-image-event.json`](python/events/ai-image-event.json)

`python/serverless.yaml`에는 두 AI API에 필요한 IAM 권한도 함께 선언되어 있으므로, 별도 콘솔 작업 없이 `serverless deploy`로 바로 배포할 수 있습니다.

```bash
cd python
serverless deploy --stage dev
serverless info
```

배포 후 텍스트 분석 예시:

```bash
curl -X POST https://<api-id>.execute-api.ap-northeast-2.amazonaws.com/dev/ai/text/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Smith from Seattle said the Lambda rollout was smooth and shared john@example.com for follow-up.",
    "language_code": "en",
    "detect_pii": true
  }'
```

Lambda 직접 호출 예시:

```bash
aws lambda invoke \
  --function-name hello-api-python-dev-aiTextAnalyze \
  --payload fileb://events/ai-text-event.json \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

이미지 분석은 S3 객체 경로만 넘기면 됩니다:

```bash
curl -X POST https://<api-id>.execute-api.ap-northeast-2.amazonaws.com/dev/ai/image/labels \
  -H "Content-Type: application/json" \
  -d '{
    "s3_bucket": "replace-with-your-bucket",
    "s3_key": "images/sample.png",
    "max_labels": 8,
    "min_confidence": 75
  }'
```

---

## Java Lambda 배포

### 핸들러 코드 (`java/src/main/java/com/example/HelloHandler.java`)

Java Lambda는 `RequestHandler<입력, 출력>` 인터페이스를 구현합니다.
API Gateway 프록시 통합 이벤트에는 `APIGatewayProxyRequestEvent`와 `APIGatewayProxyResponseEvent`를 사용합니다.

```java
package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import java.util.HashMap;
import java.util.Map;

public class HelloHandler
        implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    @Override
    public APIGatewayProxyResponseEvent handleRequest(
            APIGatewayProxyRequestEvent input, Context context) {

        Map<String, String> params = input.getQueryStringParameters();
        String name = (params != null && params.containsKey("name"))
                ? params.get("name") : "World";

        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", "application/json");
        String body = String.format(
                "{\"message\": \"Hello, %s!\", \"language\": \"Java\"}", name);

        return new APIGatewayProxyResponseEvent()
                .withStatusCode(200)
                .withHeaders(headers)
                .withBody(body);
    }
}
```

### Maven 빌드 구조 (`java/pom.xml`)

`maven-shade-plugin`을 사용해 의존성을 모두 포함한 **Fat JAR(Uber JAR)**를 빌드합니다.
Lambda는 외부 의존성을 직접 설치할 수 없으므로, 필요한 모든 클래스를 하나의 JAR에 묶어야 합니다.

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-shade-plugin</artifactId>
    <version>3.5.1</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals><goal>shade</goal></goals>
        </execution>
    </executions>
</plugin>
```

```bash
cd java
mvn package
# 결과물: target/hello-lambda-1.0-SNAPSHOT.jar (Fat JAR, 수 MB)
```

### 콘솔 배포 절차

1. Maven으로 JAR 빌드: `mvn package`
2. **AWS 콘솔 → Lambda → 함수 생성**
3. **런타임**: `Java 17`
4. **코드** 탭 → **.jar 파일 업로드**
5. **핸들러** 설정: `com.example.HelloHandler`
6. **메모리**: 최소 `512 MB` (Java 콜드스타트 특성상 권장)
7. **타임아웃**: `15초`

### AWS CLI 배포

```bash
cd java
mvn package -q

# 함수 생성
aws lambda create-function \
  --function-name edumgt-lambda-java \
  --runtime java17 \
  --role arn:aws:iam::086015456585:role/lambda-test \
  --handler com.example.HelloHandler \
  --zip-file fileb://target/hello-lambda-1.0-SNAPSHOT.jar \
  --memory-size 512 \
  --timeout 15 \
  --region ap-northeast-2

# 코드 업데이트
aws lambda update-function-code \
  --function-name edumgt-lambda-java \
  --zip-file fileb://target/hello-lambda-1.0-SNAPSHOT.jar \
  --region ap-northeast-2

# 호출 테스트
aws lambda invoke \
  --function-name edumgt-lambda-java \
  --payload '{"queryStringParameters":{"name":"Alice"}}' \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

### Serverless Framework 배포

```bash
cd java
mvn package -q    # JAR 먼저 빌드
serverless deploy
```

`java/serverless.yaml`:

```yaml
service: hello-api-java

provider:
  name: aws
  runtime: java17
  region: ap-northeast-2

package:
  artifact: target/hello-lambda-1.0-SNAPSHOT.jar  # 빌드된 Fat JAR 경로

functions:
  hello:
    handler: com.example.HelloHandler
    memorySize: 512
    timeout: 15
    events:
      - http:
          path: hello
          method: get
          cors: true
```

---

## API Gateway 연동

API Gateway는 HTTP 요청을 받아 Lambda 함수로 전달하는 **관리형 API 엔드포인트**입니다.
**Lambda 프록시 통합** 방식을 사용하면 요청 전체(헤더, 쿼리스트링, 바디 등)가 event 객체로 그대로 전달됩니다.

### 방법 A — AWS 콘솔

1. **AWS 콘솔 → API Gateway** 이동
2. **REST API → 구축** 선택
3. 새 **리소스** `/hello` 생성
4. **GET 메서드** 추가 → 통합 유형: **Lambda 함수**, **Lambda 프록시 통합** 활성화
5. **API 배포** → 새 **스테이지** 생성 (예: `dev`)
6. **호출 URL** 확인 후 테스트:
   ```
   https://<API_ID>.execute-api.ap-northeast-2.amazonaws.com/dev/hello?name=Alice
   ```

![API Gateway 설정 화면](docs/images/image.png)
![Lambda 함수 연결](docs/images/image-2.png)
![Lambda 함수 연결 상세](docs/images/image-3.png)
![리소스 생성](docs/images/image-5.png)
![메서드 생성 입력](docs/images/image-8.png)
![메서드 생성 확인](docs/images/image-9.png)
![GET 메서드 Lambda 통합](docs/images/image-10.png)
![배포 URL 확인](docs/images/image-11.png)
![스테이지 생성](docs/images/image-12.png)
![재배포](docs/images/image-13.png)

### 방법 B — AWS CLI

```bash
# 1. REST API 생성
API_ID=$(aws apigateway create-rest-api \
  --name "hello-api" \
  --query 'id' --output text)

# 2. 루트 리소스 ID 조회
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[?path==`/`].id' --output text)

# 3. /hello 리소스 생성
RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part hello \
  --query 'id' --output text)

# 4. GET 메서드 생성
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method GET \
  --authorization-type NONE

# 5. Lambda 프록시 통합 설정
LAMBDA_ARN="arn:aws:lambda:ap-northeast-2:086015456585:function:hello-api-dev-hello"
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:ap-northeast-2:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations"

# 6. API Gateway의 Lambda 호출 권한 부여
aws lambda add-permission \
  --function-name hello-api-dev-hello \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:ap-northeast-2:086015456585:${API_ID}/*/*"

# 7. 스테이지 배포
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name dev

echo "엔드포인트: https://c8wy9s5c3m.execute-api.ap-northeast-2.amazonaws.com/dev/hello"
```

### 방법 C — Serverless Framework (자동)

각 언어 디렉터리의 `serverless.yaml`에 `http` 이벤트가 정의되어 있으면
`serverless deploy` 한 번으로 Lambda + API Gateway + IAM 권한이 모두 자동으로 구성됩니다.
내부적으로 CloudFormation 스택을 생성합니다.

---

## GitHub Actions CI/CD 자동 배포

`main` 브랜치에 push 할 때마다 **변경된 언어 디렉터리만 감지**하여 해당 Lambda 함수를 자동으로 업데이트합니다.
워크플로 파일: [`.github/workflows/deploy-lambda.yml`](.github/workflows/deploy-lambda.yml)

### 워크플로 전체 흐름

```
push to main
    │
    ▼
① detect-changes 잡
   - git diff HEAD~1 HEAD 로 변경 파일 목록 추출
   - nodejs/, python/, java/ 각 경로 포함 여부 판별
   - 결과를 job output으로 전달 (nodejs=true/false 등)
    │
    ├─ nodejs=true ──▶ ② deploy-nodejs 잡 (병렬)
    │                   - actions/checkout@v4
    │                   - aws-actions/configure-aws-credentials@v4
    │                   - zip function.zip index.js handler.js
    │                   - aws lambda update-function-code
    │                   - aws lambda wait function-updated
    │                   - (선택) lambda-s3/index.js도 동일하게 배포
    │
    ├─ python=true ──▶ ③ deploy-python 잡 (병렬)
    │                   - zip function.zip handler.py
    │                   - aws lambda update-function-code
    │                   - aws lambda wait function-updated
    │
    └─ java=true   ──▶ ④ deploy-java 잡 (병렬)
                        - actions/setup-java@v4 (Temurin 17, Maven 캐시)
                        - mvn package -q  (Fat JAR 빌드)
                        - aws lambda update-function-code
                        - aws lambda wait function-updated
```

### 워크플로 상세 설명

#### ① 변경 감지 잡 (`detect-changes`)

```yaml
- name: Detect changed directories
  id: filter
  run: |
    BASE=$(git rev-parse HEAD~1 2>/dev/null || git hash-object -t tree /dev/null)
    CHANGED=$(git diff --name-only "$BASE" HEAD)

    grep -q "^nodejs/" <<< "$CHANGED" && echo "nodejs=true" >> "$GITHUB_OUTPUT" \
                                      || echo "nodejs=false" >> "$GITHUB_OUTPUT"
    grep -q "^python/" <<< "$CHANGED" && echo "python=true" >> "$GITHUB_OUTPUT" \
                                      || echo "python=false" >> "$GITHUB_OUTPUT"
    grep -q "^java/"   <<< "$CHANGED" && echo "java=true"   >> "$GITHUB_OUTPUT" \
                                      || echo "java=false"   >> "$GITHUB_OUTPUT"
```

- `git hash-object -t tree /dev/null`: 최초 커밋처럼 `HEAD~1`이 없을 때의 폴백 (빈 트리 해시)
- `$GITHUB_OUTPUT`: 잡 간 값을 전달하는 GitHub Actions 공식 메커니즘

#### ② 조건부 실행

```yaml
deploy-nodejs:
  needs: detect-changes
  if: needs.detect-changes.outputs.nodejs == 'true'
```

`nodejs/` 아래 파일이 하나도 바뀌지 않으면 이 잡은 **스킵**됩니다.
세 개의 배포 잡은 서로 `needs` 관계 없이 **병렬**로 실행됩니다.

#### ③ AWS 자격 증명 주입

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ${{ env.AWS_REGION }}
```

GitHub Secrets에 저장된 IAM 자격 증명을 실행기(ubuntu-latest)의 환경 변수로 주입합니다.
이후 `aws` CLI 명령이 자동으로 이 자격 증명을 사용합니다.

#### ④ 배포 및 완료 대기

```bash
aws lambda update-function-code \
  --function-name ${{ vars.LAMBDA_NODEJS_FUNCTION_NAME }} \
  --zip-file fileb://function.zip \
  --region ${{ env.AWS_REGION }}

aws lambda wait function-updated \
  --function-name ${{ vars.LAMBDA_NODEJS_FUNCTION_NAME }} \
  --region ${{ env.AWS_REGION }}
```

`update-function-code`는 비동기로 처리됩니다.
`wait function-updated`는 Lambda가 `Active` 상태가 될 때까지 폴링하여 배포 성공을 확인합니다.

### GitHub 설정 방법

**Settings → Secrets and variables → Actions**

#### Secrets (민감 정보 — 암호화 저장)

| 이름                      | 값                   |
| ------------------------- | -------------------- |
| `AWS_ACCESS_KEY_ID`     | IAM 사용자 액세스 키 |
| `AWS_SECRET_ACCESS_KEY` | IAM 사용자 시크릿 키 |

#### Variables (공개 설정값 — 평문 저장)

| 이름                               | 예시 값                    | 설명                     |
| ---------------------------------- | -------------------------- | ------------------------ |
| `LAMBDA_NODEJS_FUNCTION_NAME`    | `edumgt-lambda-nodejs`   | Node.js Lambda 함수 이름 |
| `LAMBDA_PYTHON_FUNCTION_NAME`    | `edumgt-lambda-python`   | Python Lambda 함수 이름  |
| `LAMBDA_JAVA_FUNCTION_NAME`      | `edumgt-lambda-java`     | Java Lambda 함수 이름    |
| `LAMBDA_S3_NODEJS_FUNCTION_NAME` | `edumgt-lambda-function` | S3 트리거 Lambda (선택)  |

> **주의:** `update-function-code`는 **이미 존재하는 함수**만 업데이트합니다.
> 함수를 처음 만들 때는 콘솔 또는 AWS CLI로 `create-function`을 먼저 실행해야 합니다.

### GitHub Actions용 IAM 최소 권한 정책

GitHub Actions 전용 IAM 사용자를 만들고 아래 권한만 부여하는 것을 권장합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaDeployOnly",
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration"
      ],
      "Resource": "arn:aws:lambda:ap-northeast-2:<ACCOUNT_ID>:function:edumgt-lambda-*"
    }
  ]
}
```

`lambda:GetFunctionConfiguration`은 `wait function-updated` 내부 폴링에 필요합니다.

### 워크플로 실행 확인

GitHub 레포지터리 → **Actions** 탭에서 실행 결과를 확인할 수 있습니다:

```
✅ detect-changes      — 변경 파일 감지 완료
✅ deploy-nodejs       — Node.js Lambda 배포 완료: edumgt-lambda-nodejs
⏭ deploy-python       — 변경 없음, 스킵
⏭ deploy-java         — 변경 없음, 스킵
```

---

## 권한 오류 해결 가이드

### CloudFormation 권한 오류

```
User ... is not authorized to perform: cloudformation:CreateChangeSet
```

**해결:** IAM → 사용자 → 권한 → `AWSCloudFormationFullAccess` 정책 추가

![CloudFormation 권한 추가](docs/images/image-15.png)
![정책 확인](docs/images/image-16.png)

### API Gateway 권한 오류

```
... not authorized to perform: apigateway:PUT ...
```

**해결:** `AmazonAPIGatewayAdministrator` 정책 추가

![API Gateway 권한](docs/images/image-17.png)
![API Gateway 권한 상세](docs/images/image-18.png)

### CloudFormation 스택 롤백 오류

```
Stack ... is in UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS state
```

**해결:** 스택 삭제 후 재시도

```bash
aws cloudformation delete-stack --stack-name hello-api-dev
```

![스택 에러](docs/images/image-19.png)
![삭제 성공](docs/images/image-20.png)
![삭제 실패 시 전체 삭제](docs/images/image-21.png)

### CloudWatch Logs 권한 오류

```
logs:TagResource permission is required
```

**해결:** `logs:TagResource` 권한이 포함된 커스텀 정책 추가

![CloudWatch Logs 권한 오류](docs/images/image-22.png)
![권한 추가](docs/images/image-23.png)
![권한 추가 상세](docs/images/image-24.png)
![정책 생성](docs/images/image-25.png)
![정책 생성 완료](docs/images/image-29.png)
![추가 설정 1](docs/images/image-30.png)
![추가 설정 2](docs/images/image-31.png)

### Log Group 중복 오류

```
Resource of type 'AWS::Logs::LogGroup' ... already exists.
```

**해결:** 기존 Log Group 삭제 후 재실행

```bash
aws logs delete-log-group --log-group-name /aws/lambda/<FUNCTION_NAME>
```

![Log Group 중복](docs/images/image-32.png)
![완료 화면](docs/images/image-33.png)

---

## AWS CLI 명령어 모음

```bash
# ── Lambda ────────────────────────────────────────────────────────────
# 함수 목록 조회
aws lambda list-functions --region ap-northeast-2

# 함수 정보 조회
aws lambda get-function --function-name <FUNCTION_NAME>

# 함수 설정 조회 (런타임, 메모리, 핸들러 등)
aws lambda get-function-configuration --function-name <FUNCTION_NAME>

# 함수 호출
aws lambda invoke \
  --function-name <FUNCTION_NAME> \
  --payload '{"queryStringParameters":{"name":"Test"}}' \
  --cli-binary-format raw-in-base64-out \
  output.json && cat output.json

# 함수 코드 업데이트
aws lambda update-function-code \
  --function-name <FUNCTION_NAME> \
  --zip-file fileb://function.zip \
  --region ap-northeast-2

# 함수 업데이트 완료 대기
aws lambda wait function-updated --function-name <FUNCTION_NAME>

# 함수 삭제
aws lambda delete-function --function-name <FUNCTION_NAME>

# ── API Gateway ────────────────────────────────────────────────────────
# REST API 목록 조회
aws apigateway get-rest-apis

# ── CloudFormation ─────────────────────────────────────────────────────
# 스택 목록 조회
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# 스택 삭제
aws cloudformation delete-stack --stack-name <STACK_NAME>

# ── S3 ─────────────────────────────────────────────────────────────────
# 버킷 생성 (서울 리전)
aws s3api create-bucket \
  --bucket <BUCKET_NAME> \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2

# 파일 업로드
aws s3 cp face1.png s3://<BUCKET_NAME>/

# 버킷/객체 목록
aws s3 ls
aws s3 ls s3://<BUCKET_NAME>/

# ── CloudWatch Logs ────────────────────────────────────────────────────
# 로그 그룹 목록
aws logs describe-log-groups

# 로그 스트림 목록
aws logs describe-log-streams --log-group-name /aws/lambda/<FUNCTION_NAME>

# 로그 이벤트 조회
aws logs get-log-events \
  --log-group-name /aws/lambda/<FUNCTION_NAME> \
  --log-stream-name <LOG_STREAM_NAME>

# 로그 그룹 삭제
aws logs delete-log-group --log-group-name /aws/lambda/<FUNCTION_NAME>

# ── IAM ────────────────────────────────────────────────────────────────
# 역할의 연결 정책 목록
aws iam list-attached-role-policies --role-name <ROLE_NAME>

# Lambda에 권한 추가 (S3 → Lambda 호출 허용)
aws lambda add-permission \
  --function-name <FUNCTION_NAME> \
  --principal s3.amazonaws.com \
  --statement-id AllowS3Invoke \
  --action lambda:InvokeFunction \
  --source-arn arn:aws:s3:::<BUCKET_NAME>
```

![S3 버킷 생성](docs/images/image-36.png)
![CloudWatch Logs 조회](docs/images/image-35.png)

---

## 추가 실습

- [Lambda + S3 이벤트 트리거 실습 가이드](docs/lambda-s3/README.md)S3에 파일 업로드 시 Lambda 자동 실행 → CloudWatch Logs 확인까지 전 과정 실습
- AWS Well-Architected 참고: https://aws.amazon.com/ko/architecture

![Well-Architected 소개](docs/images/image-37.png)
![Well-Architected 참고](docs/images/image-38.png)

---

### RDS 연동

```bash
mysql -h database-edumgt.cg0ugoglztrn.ap-northeast-2.rds.amazonaws.com -P 3306 -u root -p --ssl-mode=VERIFY_IDENTITY --ssl-ca=./global-bundle.pem
```

---

```bash
curl -X POST https://qri7el2x7z4ym4zowsk3go5uey0bjmti.lambda-url.ap-northeast-2.on.aws/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "홍길동",
    "password": "mypassword",
    "phone": "010-1234-5678",
    "email": "hong@example.com"
  }'
```

![alt text](image.png)

---




# AWS AI 서비스별 ML/DL 알고리즘 및 내부 아키텍처 가이드

AWS의 AI/ML 서비스는 크게 **전통적 머신러닝(ML) 알고리즘**을 사용하는 서비스와, **심층 신경망 기반의 딥러닝(DL) 및 생성형 AI(GenAI)** 기술을 사용하는 서비스로 분류됩니다. 본 문서는 주요 서비스의 핵심 기술과 내부 데이터 흐름을 상세히 다룹니다.

---

## 1. AWS AI 리소스별 핵심 기술 및 알고리즘 분류

### 1) 딥러닝(DL) 및 생성형 AI 기반 서비스

대규모 비정형 데이터(텍스트, 이미지, 음성, 영상)를 처리하는 서비스들은 심층 신경망(Deep Neural Networks) 구조를 기반으로 작동합니다.

* **Amazon Bedrock / Amazon Q**
  * **핵심 기술:** 트랜스포머(Transformer) 기반 거대언어모델(LLM - 예: Amazon Nova, Claude, Llama) 및 확산 모델(Diffusion Model - 이미지 생성)
* **Amazon Rekognition**
  * **핵심 기술:** 합성곱 신경망(CNN), 비전 트랜스포머(ViT), 객체 탐지(YOLO, SSD 계열), 고속 근사 최근접 이웃(ANN) 검색 알고리즘
* **Amazon Comprehend**
  * **핵심 기술:** BERT, RoBERTa 계열의 양방향 트랜스포머 인코더, 조건부 확률장(CRF), 잠재 디리클레 할당(LDA - 토픽 모델링용)
* **Amazon Transcribe**
  * **핵심 기술:** Conformer/Transformer 백본, 연결주의 시간 분류(CTC) 디코더, 주파수 변환(Log-Mel Spectrogram), 화자 분리(Diarization) 클러스터링
* **Amazon Polly**
  * **핵심 기술:** WaveNet 스타일의 생성형 신경망, Tacotron 계열의 음성 합성 신경망(TTS)
* **Amazon Lex**
  * **핵심 기술:** 트랜스포머 기반 자연어 이해(NLU), 시퀀스-투-시퀀스(Seq2Seq) 대화 관리 기술
* **Amazon Textract**
  * **핵심 기술:** CNN + 트랜스포머 결합 구조 (LayoutLM 계열의 문서 구조 이해 기술)

### 2) 전통적 머신러닝(ML) 기반 서비스

정형 데이터(엑셀, DB), 시계열 예측, 통계성 분석에는 연산 효율성과 설명 가능성이 높은 통계/머신러닝 알고리즘이 사용됩니다.

* **Amazon Forecast**
  * **핵심 기술:** 통계 기반 알고리즘(ARIMA, ETS) + 딥러닝 기반 시계열 모델(DeepAR, CNN-QR) 하이브리드 구성
* **Amazon Fraud Detector**
  * **핵심 기술:** 그레이디언트 부스팅 트리(GBDT, 주로 XGBoost 계열) 및 로지스틱 회귀 알고리즘
* **Amazon Personalize**
  * **핵심 기술:** 협업 필터링(Collaborative Filtering), 행렬 분해(Matrix Factorization) 및 사용자 행동 분석을 위한 순환 신경망(HRNN)

### 3) ML/DL 통합 플랫폼

* **Amazon SageMaker AI**
  * **전통적 ML:** XGBoost, Linear Learner, K-Means, PCA, Random Forest 등 내장 제공
  * **딥러닝 프레임워크:** PyTorch, TensorFlow, Hugging Face 등을 활용한 커스텀 모델(CNN, RNN, LLM 등) 학습 및 배포 지원

---

## 2. 주요 서비스별 내부 기술 구조 및 데이터 흐름

### 📌 Amazon Bedrock (생성형 AI 오케스트레이션)

대규모 언어 모델(LLM)과 기초 모델(FM)을 안전하고 확장성 있게 서빙하기 위한 플랫폼입니다.

#### 💡 내부 기술 구조

* **분산 추론 게이트웨이:** API 요청을 수신하여 다중 가용영역(Multi-AZ)에 분산된 컴퓨트 레이어로 실시간 로드 밸런싱을 수행합니다.
* **전용 칩 기반 가속 클러스터:** AWS Inferentia2, Trainium 가속기 및 GPU를 활용하여 모델 가상화 기술 기반의 고속 추론을 제공합니다.
* **RAG (검색 증강 생성) 엔진:** 입력 프롬프트를 벡터로 임베딩하여 Amazon OpenSearch Serverless 등 벡터 데이터베이스와 실시간 매칭합니다.

#### 🔄 데이터 흐름

1. **요청 수신:** 사용자 앱이 프롬프트(텍스트/이미지)와 함께 API를 호출합니다.
2. **가드레일 검증:** Bedrock Guardrails가 유해 콘텐츠 및 개인정보(PII) 누출 여부를 먼저 필터링합니다.
3. **컨텍스트 보강 (RAG 활성화 시):** 지식 가방(Knowledge Bases)을 거쳐 관련 문서를 벡터 검색한 후 원래 프롬프트에 결합합니다.
4. **모델 추론:** 완성된 프롬프트가 대형 언어 모델(LLM)에 전달되어 차례대로 다음 토큰을 확률 연산합니다.
5. **스트리밍 반환:** 생성되는 토큰을 청크(Chunk) 단위로 사용자 화면에 실시간 응답합니다.

---

### 📌 Amazon Rekognition (컴퓨터 비전 분석)

이미지와 비디오 내부의 객체, 얼굴, 텍스트 등을 탐지하는 멀티태스킹 비전 파이프라인입니다.

#### 💡 내부 기술 구조

* **전처리 디코딩 레이어:** 입력된 미디어 파일의 압축을 메모리상에 풀고 고정 해상도로 리사이징 및 정규화를 수행합니다.
* **다중 작업 CNN/ViT:** 이미지 1장당 객체 탐지, 텍스트 인식, 얼굴 분석 등 전용 백본(Backbone) 신경망들이 비동기 병렬로 작동합니다.
* **특징 매칭 엔진 (K-NN):** 추출한 얼굴 특징 벡터를 기반으로 대규모 얼굴 컬렉션 DB 내에서 근사 최근접 이웃(ANN) 검색을 수행합니다.

#### 🔄 데이터 흐름

1. **미디어 입력:** Base64 이미지 바이트 데이터나 Amazon S3 객체 URI를 통해 API 요청이 들어옵니다.
2. **텐서 변환:** 이미지 디코딩 및 비디오 프레임 단위 샘플링 후 학습 가능한 텐서(Tensor) 배열로 변환합니다.
3. **병렬 모델 추론:** 다중 신경망 구조를 동시에 거치며 객체 좌표(Bounding Box) 추출 및 얼굴 임베딩 벡터 생성이 수행됩니다.
4. **매칭 및 포스트 프로세싱:** 사전에 수립된 신뢰도 임계값(Threshold)을 넘는 결과만 최종 선별합니다.
5. **결과 출력:** 객체 레이블 정보와 매칭 유사도 등을 담은 구조화된 JSON 형태로 클라이언트에 반환합니다.

---

### 📌 Amazon Transcribe (음성 인식 - STT)

오디오 파일 또는 스트림 데이터를 텍스트 시퀀스로 변환하는 오디오 전용 딥러닝 시스템입니다.

#### 💡 내부 기술 구조

* **어쿠스틱 피처 추출기:** 아날로그 오디오 신호를 20~30ms 단위로 분할하여 주파수 텐서 데이터(Log-Mel Spectrogram)로 가공합니다.
* **Conformer / Transformer 백본:** 소음 제어와 문맥 이해에 탁월한 CNN 및 Self-Attention 하이브리드 신경망을 활용해 음향 특징을 인식합니다.
* **CTC 디코더:** 음성 데이터와 텍스트 문장의 길이 불일치 문제를 해결하기 위해 타임스탬프 기반 정렬 알고리즘을 수행합니다.

#### 🔄 데이터 흐름

1. **음성 주입:** S3 배치 업로드 혹은 웹소켓(WebSocket) 스트림을 통해 오디오 신호가 수신됩니다.
2. **주파수 인코딩:** 음성 신호가 원시 데이터에서 시각화된 주파수 맵 형태로 디코딩됩니다.
3. **신경망 디코딩:** Conformer 신경망과 CTC 레이어를 거쳐 발음 기호 및 단어 시퀀스로 추론됩니다.
4. **텍스트 가공:** 화자 분리(Diarization) 클러스터링과 구두점 자동 삽입 알고리즘이 적용됩니다.
5. **결과 반환:** 텍스트 문장과 화자 정보, 타임스탬프가 매핑된 JSON 결과가 반환됩니다.

---

### 📌 Amazon Comprehend (자연어 처리 - NLP)

텍스트 문서 내 비즈니스 가치와 의미를 추출하는 양방향 자연어 이해(NLU) 엔진입니다.

#### 💡 내부 기술 구조

* **토크나이저:** 문장을 WordPiece 또는 BPE 알고리즘 기반으로 분리하여 모르는 단어(OOV) 문제를 방지합니다.
* **양방향 트랜스포머 (BERT 계열):** 주변 단어들과의 어텐션(Attention) 가중치를 분석하여 동음이의어의 의미를 정확하게 문맥적으로 인지합니다.
* **CRF 레이어 / LDA 모델:** 문장 속 명사들의 배치 순서 확률을 바탕으로 개체명을 인식하며, 대량 문서 분석 시 통계적 토픽 모델링을 실행합니다.

#### 🔄 데이터 흐름

1. **원문 입력:** 분석을 원하는 일반 텍스트 문서가 인풋으로 들어옵니다.
2. **토큰화 및 정규화:** 불필요한 기호 제거 및 어휘 분석을 위한 토큰화가 이루어집니다.
3. **문맥 임베딩:** 고차원 문맥 벡터로 변환된 데이터가 BERT 계열 분류 레이어로 전달됩니다.
4. **추론 및 태깅:** 감정 상태(긍정/부정), 핵심 구절, 개인정보(PII) 스코어가 계산됩니다.
5. **구조화:** 최종 식별된 개체 정보와 신뢰도 점수가 취합되어 JSON 데이터로 출력됩니다.

---

### 📌 Amazon Forecast (시계열 수요 예측)

비즈니스의 정형 데이터를 학습하여 미래의 특정 시점 가치를 다각도로 예측하는 하이브리드 프레임워크입니다.

#### 💡 내부 기술 구조

* **DeepAR (시계열 RNN):** 여러 연관 시계열 데이터의 상호 관계를 하나의 거대한 순환 신경망 구조로 동시에 학습하는 알고리즘입니다.
* **CNN-QR (Convolutional Quantile Regression):** 인과 관계 학습에 빠른 CNN 구조를 시계열에 접목하여 특정 단일 값이 아닌 '확률 구간별 분위수'를 산출합니다.
* **통계/ML 백엔드 (ARIMA, Prophet):** 단순한 주기성을 가졌거나 데이터 기간이 짧을 때는 경량 통계 분석 모델을 동적으로 앙상블합니다.

#### 🔄 데이터 흐름

1. **데이터 수집:** 핵심 시계열 데이터(매출 이력 등)와 메타데이터가 입력됩니다.
2. **피처 엔지니어링:** 누락된 값(결측치)을 대체하고 날짜/요일 정보 등의 특성을 자동 추출합니다.
3. **Auto Predictor 실행:** 데이터셋 규모에 알맞은 알고리즘(DeepAR / CNN-QR / ARIMA 등)이 앙상블 형태로 학습/추론됩니다.
4. **분위수 평가:** 예측의 불확실성을 감안하여 p10, p50, p90 등의 확률 기반 구간 값이 도출됩니다.
5. **예측치 내보내기:** 결과 데이터가 가시화되거나 S3 버킷으로 자동 내보내기(Export) 처리됩니다.

---

## 3. Python Lambda로 AWS AI 리소스 호출 예제

이 레포에는 위 개념 설명을 바로 실습할 수 있도록 [`python/ai_handler.py`](python/ai_handler.py) 예제가 추가되어 있습니다. API Gateway가 HTTP 요청을 받으면 Lambda가 본문을 해석한 뒤 AWS AI 서비스에 위임하고, 결과를 다시 JSON으로 반환하는 구조입니다.

```text
Client
  -> API Gateway
  -> Lambda (python/ai_handler.py)
  -> Amazon Comprehend or Amazon Rekognition
  -> JSON Response
```

### 예제 1. Amazon Comprehend 텍스트 분석

사용 시나리오:

- 고객 리뷰 감정 분석
- 문의 문장에서 상품명, 지역명, 브랜드명 추출
- 영어 또는 스페인어 본문에 대한 PII 포함 여부 사전 점검

요청 예시:

```json
{
  "text": "John Smith from Seattle said the delivery was quick, but he wants updates sent to john@example.com.",
  "language_code": "en",
  "detect_pii": true
}
```

응답 예시:

```json
{
  "service": "amazon-comprehend",
  "language_code": "en",
  "sentiment": "MIXED",
  "entity_count": 2,
  "entities": [
    { "text": "John Smith", "type": "PERSON", "score": 0.9981 },
    { "text": "Seattle", "type": "LOCATION", "score": 0.9724 }
  ],
  "pii_entities": [
    { "type": "NAME", "score": 0.9999, "begin_offset": 0, "end_offset": 10 },
    { "type": "EMAIL", "score": 0.9997, "begin_offset": 70, "end_offset": 86 }
  ]
}
```

### 예제 2. Amazon Rekognition 이미지 레이블 분석

사용 시나리오:

- 업로드 이미지 자동 태깅
- 상품 사진 분류 전처리
- 운영자 검수용 메타데이터 생성

요청 예시:

```json
{
  "s3_bucket": "replace-with-your-bucket",
  "s3_key": "images/sample.png",
  "max_labels": 8,
  "min_confidence": 75
}
```

응답 예시:

```json
{
  "service": "amazon-rekognition",
  "label_count": 3,
  "labels": [
    { "name": "Laptop", "confidence": 98.41, "categories": ["Electronics"] },
    { "name": "Screen", "confidence": 95.8, "categories": ["Electronics"] },
    { "name": "Office", "confidence": 82.13, "categories": ["Indoors"] }
  ]
}
```

### 배포 포인트

- `python/serverless.yaml`에 `comprehend:DetectSentiment`, `comprehend:DetectEntities`, `comprehend:DetectPiiEntities`, `rekognition:DetectLabels` 권한이 포함되어 있습니다.
- Boto3는 Lambda Python 런타임에 기본 포함되어 있어 별도 패키징 없이 예제를 실행할 수 있습니다.
- `DetectPiiEntities`는 언어 제약이 있어, 예제 코드에서는 `en` 또는 `es`가 아니면 경고를 반환하고 본문 감정/개체 분석만 계속 수행합니다.
- 샘플 이벤트는 [`python/events/ai-text-event.json`](python/events/ai-text-event.json), [`python/events/ai-image-event.json`](python/events/ai-image-event.json)에 넣어 두었습니다.
