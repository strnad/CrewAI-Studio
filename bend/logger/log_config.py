from enum import Enum
class LogLevel(Enum):
    """로그 레벨 정의"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    
    @classmethod
    def from_string(cls, level_str):
        """문자열을 LogLevel로 변환"""
        return cls[level_str.upper()]
    
# =====================================
# 사용자 필수 설정 (프로젝트마다 변경)
# =====================================

# 프로젝트 기본 설정
PROJECT_ROOT = "/data/workspace/CommonLogger"  # 프로젝트 절대 경로
GLOBAL_LOG_LEVEL = LogLevel.DEBUG              # 최소 출력 레벨
OUTPUT_MODE = "BOTH"                           # FILE | STDOUT(PM2,CONSOLE) | BOTH

# Discord 알림 설정
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1407612841858568223/mMPeJT8nibILitFEaxM4boGH-aJsIr9omT5_z0O-nV_lnHPNdYO0lMoecYD0yJErAaAv" 
# Discord 알림 설정 (기능별 독립)
DISCORD_LOG_ALERTS = False                     # 로깅 ERROR/CRITICAL 알림
DISCORD_LOG_LEVELS = [LogLevel.ERROR, LogLevel.CRITICAL]  # 알림받을 레벨들
DISCORD_RESOURCE_THRESHOLD = False              # 리소스 임계값 초과 알림
DISCORD_RESOURCE_DAILY = True                  # 일일 리소스 리포트

# 리소스 모니터링 설정
RESOURCE_MONITORING_ENABLED = True
# 모니터링 트리거 조건
RESOURCE_DAILY_REPORT_TIME = (19, 36)  # (시, 분) - 매일 07:30에 리포트
RESOURCE_THRESHOLD_ALERT = True        # 임계값 초과시 즉시 알림

# =====================================
# 고급 설정 (기본값 사용 권장)
# =====================================

# 로그 포맷
LOG_FORMAT = "[{timestamp}] [{level}] [{module}] {message} | {extras}"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# 파일 로깅 세부 설정
LOG_BASE_PATH = f"{PROJECT_ROOT}/logs"         # logs/YYYYMM/MMDD.log 구조
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024          # 10MB (로테이션 기준)
LOG_FILE_BACKUP_COUNT = 5                      # 같은 날짜 내 백업 개수 (31.log.4 까지 생긴다는 의미. 최대 50MB)

# 로그 자동 정리 설정
LOG_RETENTION_DAYS = 30  # 30일 이상 된 로그 삭제
LOG_AUTO_CLEANUP = True  # 자동 정리 활성화

# 모니터링 주기
RESOURCE_COLLECT_INTERVAL = 1          # 데이터 수집 주기 (초) - 1초마다
RESOURCE_AGGREGATE_INTERVAL = 60       # 피크값 집계 주기 (초) - 1분마다  
RESOURCE_THRESHOLD_CHECK_INTERVAL = 30 # 임계값 체크 주기 (초)
# 리소스 임계값 알림 중복 방지 설정  
RESOURCE_THRESHOLD_COOLDOWN_MINUTES = 20  # 같은 리소스 알림 20분 간격

# 임계값 설정 (%)
RESOURCE_GPU_THRESHOLD = 80           # GPU 사용률 임계값
RESOURCE_CPU_THRESHOLD = 90           # CPU 사용률 임계값  
RESOURCE_RAM_THRESHOLD = 85           # RAM 사용률 임계값

# 하드웨어 설정
RESOURCE_GPU_INDEX = 0                # 모니터링할 GPU 번호
RESOURCE_PM2_APP_NAME = None          # None=PM2 미사용, "app_name"=PM2 사용
RESOURCE_CACHE_DIR = None             # None=디스크 모니터링 제외

# 색상 코드 (터미널 출력용)
LEVEL_COLORS = {
    LogLevel.DEBUG: "\033[36m",     # Cyan
    LogLevel.INFO:  "", # "\033[32m",      # Green
    LogLevel.WARNING: "\033[33m",   # Yellow
    LogLevel.ERROR: "\033[31m",     # Red
    LogLevel.CRITICAL: "\033[35m",  # Magenta
}
COLOR_RESET = "\033[0m"