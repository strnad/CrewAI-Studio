"""
출력 핸들러 모듈
"""
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from .log_config import (
    LogLevel, LOG_BASE_PATH, LOG_FILE_MAX_BYTES, LOG_FILE_BACKUP_COUNT, 
    LOG_RETENTION_DAYS, LOG_AUTO_CLEANUP, LEVEL_COLORS, COLOR_RESET
)

class BaseHandler(ABC):
    """핸들러 기본 클래스"""
    
    @abstractmethod
    def write(self, formatted_message: str, level: LogLevel):
        """로그 메시지 출력"""
        pass

class StdoutHandler(BaseHandler):
    """표준 출력 핸들러 (PM2/콘솔 통합, 색상 지원)"""
    
    def __init__(self, use_color=True):
        self.use_color = use_color
    
    def write(self, formatted_message: str, level: LogLevel):
        """표준 출력으로 전송"""
        if self.use_color and level in LEVEL_COLORS:
            colored_message = f"{LEVEL_COLORS[level]}{formatted_message}{COLOR_RESET}"
            print(colored_message, flush=True)
        else:
            print(formatted_message, flush=True)

class FileHandler(BaseHandler):
    """파일 출력 핸들러 (로테이션 지원)"""
    
    def __init__(self):
        self.base_path = Path(LOG_BASE_PATH)
        self.max_bytes = LOG_FILE_MAX_BYTES
        self.backup_count = LOG_FILE_BACKUP_COUNT
        self.retention_days = LOG_RETENTION_DAYS
        self.auto_cleanup = LOG_AUTO_CLEANUP
        self._last_cleanup_date = None
        
    def _get_current_log_path(self) -> Path:
        """현재 날짜의 로그 파일 경로 반환"""
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        day = now.strftime("%d")
        
        log_dir = self.base_path / year_month
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir / f"{day}.log"
    
    def _should_rotate(self, file_path: Path) -> bool:
        """로테이션 필요 여부 확인"""
        if not file_path.exists():
            return False
        return file_path.stat().st_size >= self.max_bytes
        
    def _rotate(self, file_path: Path): 
        """로그 파일 로테이션"""
        # backup.n 삭제
        for i in range(self.backup_count, 0, -1):
            old_path = file_path.with_suffix(f".log.{i}") 
            new_path = file_path.with_suffix(f".log.{i+1}")
            
            if old_path.exists():
                if i == self.backup_count:
                    old_path.unlink()
                else:
                    old_path.rename(new_path)
        
        # 현재 파일을 .1로 이동
        if file_path.exists():
            file_path.rename(file_path.with_suffix(".log.1"))
    
    def _cleanup_old_logs_if_needed(self):
        """필요시 오래된 로그 정리"""
        if not self.auto_cleanup:
            return
            
        today = datetime.now().date()
        if self._last_cleanup_date == today:
            return
            
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for year_month_dir in self.base_path.glob("*"):
            if not year_month_dir.is_dir():
                continue
                
            try:
                # YYYYMM 형태 검증
                year_month = datetime.strptime(year_month_dir.name, "%Y%m")
                if year_month < cutoff_date:
                    shutil.rmtree(year_month_dir)
            except ValueError:
                # 형태가 맞지 않으면 넘어감
                continue
                
        self._last_cleanup_date = today
        
    def write(self, formatted_message: str, level: LogLevel):
        """파일에 로그 기록"""
        # 오래된 로그 정리 (하루에 한 번)
        self._cleanup_old_logs_if_needed()
        
        # 현재 날짜의 로그 파일 경로
        current_path = self._get_current_log_path()
        
        # 로테이션 필요시 수행
        if self._should_rotate(current_path):
            self._rotate(current_path)
            
        # 로그 작성
        with open(current_path, 'a', encoding='utf-8') as f:
            f.write(formatted_message + '\n')

class BothHandler(BaseHandler):
    """파일과 표준출력 동시 핸들러"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.stdout_handler = StdoutHandler()
    
    def write(self, formatted_message: str, level: LogLevel):
        """파일과 표준출력에 동시 기록"""
        # 파일 먼저 기록
        self.file_handler.write(formatted_message, level)
        # 표준출력 기록
        self.stdout_handler.write(formatted_message, level)

def get_handler(mode: str) -> BaseHandler:
    """모드에 따른 핸들러 반환"""
    mode = mode.upper()
    if mode == "FILE":
        return FileHandler()
    elif mode == "BOTH":
        return BothHandler()
    else:  # STDOUT (PM2/Console 통합)
        return StdoutHandler()