# 1. Python 3.6+ 확인
python --version

# 2. 의존성 설치 (디스코드 웹훅 목적)
pip install requests psutil

# 3. 모듈 복사 후 바로 사용!
from logger import get_logger

# 구조
CommonLogger/
├── README.md              # 사용 가이드
├── example_usage1.py       # 간단 예시
├── example_usage2.py       # 간단 예시 (상황별)
└── logger/               # 핵심 모듈 (이것만 필요합니다.)
    ├── __init__.py
    ├── discord.py
    ├── handlers.py
    ├── log_config.py
    ├── resource_monitor.py
    └── logger.py


# 주의 사항
딱 3개 주의해야함.
message
exc_info
level 
-> 키워드로 사용해서는 안됨
