"""
핵심 Logger 클래스
"""
import inspect
import traceback
import threading
import asyncio
from datetime import datetime
from contextlib import contextmanager
from typing import Any, Dict, Optional

from .log_config import (
    LogLevel, LOG_FORMAT, DATE_FORMAT, GLOBAL_LOG_LEVEL,
    OUTPUT_MODE, LEVEL_COLORS, COLOR_RESET, RESOURCE_MONITORING_ENABLED
)
from .handlers import get_handler
from .discord import DiscordNotifier


class Logger:
    """범용 로거 클래스"""
    
    def __init__(self):
        self.level = GLOBAL_LOG_LEVEL
        self.handler = get_handler(OUTPUT_MODE)
        self.discord = DiscordNotifier()
        self._context = {}  # 추적 ID 등 컨텍스트 정보
        
        # 리소스 모니터링 관련
        self._resource_monitor = None
        self._monitoring_task = None
        
        # 리소스 모니터링 자동 시작
        if RESOURCE_MONITORING_ENABLED:
            self._start_resource_monitoring()
            
    def _get_caller_info(self) -> tuple:
        """호출자 정보 추출"""
        frame = inspect.currentframe()
        # Logger 클래스 밖의 첫 번째 프레임 찾기
        while frame:
            frame = frame.f_back
            if frame and frame.f_code.co_filename != __file__:
                return (
                    frame.f_code.co_filename.split('/')[-1],
                    frame.f_code.co_name,
                    frame.f_lineno
                )
        return ("unknown", "unknown", 0)
    
    def _format_message(self, level: LogLevel, message: str, **kwargs) -> str:
        """메시지 포맷팅"""
        timestamp = datetime.now().strftime(DATE_FORMAT)[:-3]  # 밀리초 3자리만
        filename, func_name, line_no = self._get_caller_info()
        module = f"{filename}:{func_name}:{line_no}"
        
        # 컨텍스트와 kwargs 병합
        extras_dict = {**self._context, **kwargs}
        extras = " ".join(f"{k}={v}" for k, v in extras_dict.items() if k != "exc_info")
        
        formatted = LOG_FORMAT.format(
            timestamp=timestamp,
            level=level.name,
            module=module,
            message=message,
            extras=extras
        )
        
        # 색상 추가 (콘솔 모드일 때만)
        if OUTPUT_MODE == "CONSOLE" and level in LEVEL_COLORS:
            formatted = f"{LEVEL_COLORS[level]}{formatted}{COLOR_RESET}"
            
        return formatted
    
    def _start_resource_monitoring(self):
        """백그라운드 리소스 모니터링 시작"""
        try:
            from .resource_monitor import ResourceMonitor
            
            self._resource_monitor = ResourceMonitor(self)
            
            # 별도 스레드에서 asyncio 실행
            def run_monitoring():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        self._resource_monitor.start_monitoring()
                    )
                except Exception as e:
                    self.error("리소스 모니터링 실행 오류", error=str(e))
                finally:
                    loop.close()
            
            self._monitoring_task = threading.Thread(
                target=run_monitoring, 
                daemon=True,
                name="ResourceMonitor"
            )
            self._monitoring_task.start()
            
            self.info("리소스 모니터링 백그라운드 시작 완료")
            
        except ImportError as e:
            self.warning("리소스 모니터링 의존성 없음", 
                        error="psutil 라이브러리 필요",
                        action="pip install psutil로 설치하세요")
        except Exception as e:
            self.error("리소스 모니터링 시작 실패", error=str(e))
            
    def log(self, level: LogLevel, message: str, **kwargs):
        """기본 로깅 메서드"""
        if level.value < self.level.value:
            return
            
        formatted = self._format_message(level, message, **kwargs)
        
        # 핸들러로 출력
        self.handler.write(formatted, level)
        
        # Discord 알림 (독립적 체크)
        self.discord.send(formatted, level, **kwargs)
            
    # 편의 메서드들
    def debug(self, message: str, **kwargs):
        self.log(LogLevel.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        self.log(LogLevel.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        self.log(LogLevel.WARNING, message, **kwargs)
        
    def error(self, message: str, **kwargs):
        self.log(LogLevel.ERROR, message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, message, **kwargs)
        
    def exception(self, message: str, **kwargs):
        """예외 정보와 함께 에러 로깅"""
        kwargs["exc_info"] = traceback.format_exc()
        self.error(message, **kwargs)
    
    # 컨텍스트 관리
    def set_context(self, **kwargs):
        """전역 컨텍스트 설정"""
        self._context.update(kwargs)
        
    def clear_context(self):
        """컨텍스트 초기화"""
        self._context.clear()
        
    @contextmanager
    def context(self, **kwargs):
        """임시 컨텍스트 with 문"""
        old_context = self._context.copy()
        self._context.update(kwargs)
        try:
            yield self
        finally:
            self._context = old_context
            
    def is_enabled_for(self, level: str) -> bool:
        """특정 레벨이 활성화되어 있는지 확인"""
        return LogLevel.from_string(level).value >= self.level.value

    def get_resource_monitor(self):
        """리소스 모니터 인스턴스 반환 (디버깅용)"""
        return self._resource_monitor
    
# 싱글톤 인스턴스
_logger_instance = None


def get_logger() -> Logger:
    """Logger 싱글톤 인스턴스 반환"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance


def configure(**kwargs):
    """Logger 설정 변경"""
    logger = get_logger()
    
    if "level" in kwargs:
        logger.level = LogLevel.from_string(kwargs["level"])
        
    if "mode" in kwargs:
        logger.handler = get_handler(kwargs["mode"])
        
    # 기타 설정들 필요시 추가