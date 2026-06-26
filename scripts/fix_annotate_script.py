from pathlib import Path
p = Path(__file__).resolve().parent / "annotate_backend_responsible.py"
text = p.read_text(encoding="utf-8", errors="replace")
start = text.index("# llm, breed, image")
end = text.index("patch(\"common/breed_detect.py\"")
replacement = (
    'patch("common/llm_client.py", [\n'
    '    (\n'
    '        "import base64",\n'
    '        \'"""\n\\u6a21\\u5757\\u8bf4\\u660e\\uff1aLLM \\u5c01\\u88c5\\uff08\\u661f\\u706b/OpenAI\\uff09\\u3002\\n"""\n\\nimport base64\',\n'
    '    ),\n'
    '    (\n'
    '        "def chat(messages, max_tokens=1024):\\n    return _chat_completion(messages, max_tokens=max_tokens)",\n'
    '        \'def chat(messages, max_tokens=1024):\\n    """\\u5bf9\\u5916\\u6587\\u672c\\u5bf9\\u8bdd\\u5165\\u53e3\\u3002\\u3010\\u6743\\u9650\\u3011user/admin\\u3002"""\\n    return _chat_completion(messages, max_tokens=max_tokens)\',\n'
    '    ),\n'
    '])\n\n'
)
text = text[:start] + replacement + text[end:]
p.write_text(text, encoding="utf-8")
print("ok")
