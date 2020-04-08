# PROJECT-personal-recommendation-system-demo

<img width="1273" alt="스크린샷 2020-03-26 오후 2 29 08" src="https://user-images.githubusercontent.com/18637774/77613480-2a00c280-6f6e-11ea-9f9f-65c7875b6890.png">



## 요약 
- 개인용 toy system([toy system 프로그램 관련 요약](https://github.com/kangheeyong/PROJECT-personal-recommendation-system-demo/issues/1#issuecomment-604235209))
- 가상 유저는 확률적 그래프 모델로 설계([가상 유저 생성 방법](https://github.com/kangheeyong/PROJECT-personal-recommendation-system-demo/issues/1#issuecomment-604235101))
- 일간 이용자 수 20만명으로 설정(유저 최대 100만명, 아이템 최대 10만개)
- 가상 유저와 추천 시스템의 연동은 sanic 사용
- micro service architecture의 파이프라인을 위한 google drive, Kafka, MongoDB 사용
- supervisor로 프로세스를 관리하고 slack으로 알림을 받음
- 시스템 환경은 docker hub로 관리
- google drive는 별도의 툴을 만들어 관리




## 개발 환경
- Python 3.7.0 (default, Mar  6 2020, 12:45:48) [GCC 5.4.0 20160609]
- 개인용 library
  - LIB-Feynman(https://github.com/kangheeyong/LIB-Feynman)

## 개발 과정 이슈
- [step 1 기록들](https://github.com/kangheeyong/PROJECT-personal-recommendation-system-demo/issues/1#issuecomment-597509991)
