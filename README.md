# CrewAI Studio

CrewAI Studio에 오신 것을 환영합니다! 이 애플리케이션은 코드 작성 없이도 CrewAI와 상호작용할 수 있는 Streamlit 기반의 사용자 친화적인 인터페이스를 제공합니다. Docker/docker-compose 또는 Conda/venv를 사용하여 애플리케이션을 설치하고 실행하려면 아래 단계를 따라주세요.

## 주요 기능

- **멀티 플랫폼 지원**: Windows, Linux, MacOS에서 작동합니다.
- **코딩 불필요**: CrewAI와 상호작용하기 위한 사용자 친화적인 인터페이스.
- **Conda 및 가상환경 지원**: Conda와 Python 가상환경 중 선택하여 설치할 수 있습니다.
- **결과 히스토리**: 이전 결과를 확인할 수 있습니다.
- **지식 소스**: Crew에 지식 소스를 추가할 수 있습니다.
- **CrewAI 도구**: 실제 환경과 상호작용하기 위한 crewai 도구를 사용할 수 있습니다. (버그 수정은 이미 crewai-tools에 병합됨)
- **커스텀 도구**: API 호출, 파일 쓰기, 향상된 코드 인터프리터, 향상된 웹 스크래퍼 등의 커스텀 도구... 더 많은 도구가 곧 추가될 예정입니다
- **LLM 제공자 지원**: 현재 OpenAI, Groq, Anthropic, ollama, Grok, LM Studio 백엔드를 지원합니다. 많은 도구에서 임베딩을 위해 OpenAI 키가 여전히 필요할 수 있습니다. LM Studio 사용 시 임베딩 모델을 로드하는 것을 잊지 마세요.
- **단일 페이지 앱 내보내기**: Crew를 간단한 단일 페이지 Streamlit 앱으로 내보내는 기능.
- **스레드 방식 Crew 실행**: Crew를 백그라운드에서 실행할 수 있으며 중지할 수 있습니다.

## 📚 개발자 문서

### 커스텀 도구 개발 가이드

신규 커스텀 도구를 개발하려면 다음 문서를 참고하세요:

- **한국어**: [docs/CUSTOM_TOOLS_GUIDE_KR.md](docs/CUSTOM_TOOLS_GUIDE_KR.md)
- **English**: [docs/CUSTOM_TOOLS_GUIDE_EN.md](docs/CUSTOM_TOOLS_GUIDE_EN.md)

가이드에 포함된 내용:
- 2-Layer 아키텍처 설명
- 단계별 개발 가이드
- 실전 예제 (간단, 중급, 고급)
- 베스트 프랙티스
- 트러블슈팅

## 사용 방법
```bash
streamlit run app/app.py --server.headless True
```
