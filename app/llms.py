import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic

#from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_huggingface import ChatHuggingFace
from dotenv import load_dotenv

def create_openai_llm(model, temperature):
    safe_pop_env_var('OPENAI_API_KEY')
    safe_pop_env_var('OPENAI_API_BASE')
    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1/')
    if api_key:
        return ChatOpenAI(openai_api_key=api_key, openai_api_base=api_base, model_name=model, temperature=temperature, max_tokens=4096)
    else:
        raise ValueError("OpenAI API key not set in .env file")

def create_anthropic_llm(model, temperature):
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        return ChatAnthropic(anthropic_api_key=api_key, model_name=model, temperature=temperature,max_tokens=4096)
    else:
        raise ValueError("Anthropic API key not set in .env file")

def create_groq_llm(model, temperature):
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        return ChatGroq(groq_api_key=api_key, model_name=model, temperature=temperature, max_tokens=4096)
    else:
        raise ValueError("Groq API key not set in .env file")
    
# def create_googleai_llm(model, temperature):
#     api_key = os.getenv('GOOGLE_API_KEY')
#     if api_key:        
#          return ChatGoogleGenerativeAI(model=model, temperature=temperature)
#     else:
#         raise ValueError("Google AI API key not set in .env file")

# def create_huggingfacehub_llm(model, temperature):
#     api_key = os.getenv('HUGGINGFACEHUB_API_KEY')
#     if api_key:
#         return ChatHuggingFace(repo_id=model, huggingfacehub_api_token=api_key,  model_kwargs={"temperature":temperature, "max_tokens": 4096})
#     else:
#         raise ValueError("HuggingFace API key not set in .env file")

def create_lmstudio_llm(model, temperature):
    api_base = os.getenv('LMSTUDIO_API_BASE')
    os.environ["OPENAI_API_KEY"] = "lm-studio"
    os.environ["OPENAI_API_BASE"] = api_base
    if api_base:
        return ChatOpenAI(openai_api_key='lm-studio', openai_api_base=api_base, temperature=temperature, max_tokens=4096)
    else:
        raise ValueError("LM Studio API base not set in .env file")

LLM_CONFIG = {
    "OpenAI": {
        "models": ["gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"],
        "create_llm": create_openai_llm
    },
    "Groq": {
        "models": ["llama3-8b-8192","llama3-70b-8192", "mixtral-8x7b-32768"],
        "create_llm": create_groq_llm
    },
    # "GoogleAI": {
    #     "models": ["gemini-1.5-pro","gemini-1.5-flash", "gemini-1.0-pro"],
    #     "create_llm": create_googleai_llm
    # },
    # "HuggingFaceHub": {
    #     "models": ["mistralai/Mistral-7B-Instruct-v0.2", "mistralai/Codestral-22B-v0.1", "EleutherAI/gpt-neo-2.7B"],
    #     "create_llm": create_huggingfacehub_llm
    # },
    "Anthropic": {
        "models": ["claude-3-5-sonnet-20240620"],
        "create_llm": create_anthropic_llm
    },
    "LM Studio": {
        "models": ["lms-default"],
        "create_llm": create_lmstudio_llm
    }

}

def llm_providers_and_models():
    return [f"{provider}: {model}" for provider in LLM_CONFIG.keys() for model in LLM_CONFIG[provider]["models"]]

def create_llm(provider_and_model, temperature=0.1):
    provider, model = provider_and_model.split(": ")
    create_llm_func = LLM_CONFIG.get(provider, {}).get("create_llm")
    if create_llm_func:
        return create_llm_func(model, temperature)
    else:
        raise ValueError(f"LLM provider {provider} is not recognized or not supported")
      
def safe_pop_env_var(key):
    try:
        os.environ.pop(key)
    except KeyError:
        pass