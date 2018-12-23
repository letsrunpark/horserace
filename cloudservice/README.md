# Github Organization, Amazon EC2, crontab & mysql, Google Colab
===============================
# Github - horserace
- 사용 목적 : 협업 및 버전 관리, 기록

## Git 사용법

- 원격 저장소에서 로컬 저장소로 불러오기
1. git clone <주소>

- 로컬 저장소에서 원격 저장소에 저장하기
1. git add .
2. git commit -m "무슨 내용 commit할 지 간단한 멘트"
3. git push origin master

### Colaborator
- 글 작성, 삭제 등 모든 권한 부여됨

-------------------------------

# Amazon EC2
- 사용 목적 : 가상의 PC를 얻어 연산 처리

[Amazon EC2 사용법](https://docs.aws.amazon.com/ec2/index.html?id=docs_gateway#lang/ko_kr)
## EC2 접속하기
1. key-pair 권한 부여 & 공유
2. ssh -i <key-pair> ec2-user@<my-ip>

## 파일 위치
> /home/~
> /home/~/data : crawling data
> /tmp : codes

-------------------------------
### 파일 이동 to cloud!
- scp -i letsrunpark-id_rsa <myfile> ec2-user@18.218.142.199:/tmp
> ex) scp -i letsrunpark-id_rsa temp_race_send.py ec2-user@18.218.142.199:/tmp

### 모듈 설치
- pip3 install modulename --user

### 코드 실행
- python3 /tmp/filename.py

-------------------------------
* Error in Mac
- sudo chmod 400 letsrunpark-id_rsa
- 비밀번호 : Local PC Password

* EC2에서 쓰는 운영체제 : Linux Redhat (apt-get >>yum)

-------------------------------

## crontab (in EC2)
- 사용 목적 : 특정 시간 주기로 크롤링

### crontab 문법

1. __minute hour day month yoil command__
2. __5 * * * * mkdir test-dir__
> __* 시 5분에 mkdir test-dir__

3. __*/2 * * * * rmdir test-dir__
> __2분마다 rmdir test-dir__

### crontab 내용 편집하기
- crontab -e
> crontab editor 실행하기

- i = 편집모드
- esc , :wq = 편집 종료 후 저장

- crontab -l
> crontab list 보기

- crontab -r
> crontab 내용 삭제

-------------------------------
## MySQL (in EC2)
- 사용 목적 : DB 저장

### MySQL 사용법
- workbench 통해서 들어가기 & Query 작성
- hostname= 18.218.142.199 / port=3306 / pw=

> local에서 EC2로 파일 업로드할때 filezila 이용하면 편하다!

### mysql에 csv 파일 업로드
- 로그인 방법 : mysql --local-infile -uroot -p

-------------------------------
# Google Colab
- 사용 목적 : Neural Network 빠른 GPU 연산

- Google 에서 GPU, CPU 제공하여 ipynb 파일 실행 가능
- 데이터 분석에 필요한 기본적인 패키지 포함
- 무료로 제공되는 서비스

* [Colab YouTube](https://www.youtube.com/watch?v=XRBXMohjQos&t=)
* [Colab 용량, 제약사항](https://colab.research.google.com/drive/151805XTDg--dgHb3-AXJCpnWaqRhop_2#scrollTo=gsqXZwauphVV)

-------------------------------
* [MarkDown 사용법](https://heropy.blog/2017/09/30/markdown/)
* [Markdown Example](https://gist.github.com/rt2zz/e0a1d6ab2682d2c47746950b84c0b6ee)
