"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {"name": "explorer", "description": "Use before implementing a nontrivial task to inspect specifications, code and data and identify risks.",
         "system_prompt": "Read the supplied task rules and relevant files. Inspect README, docstrings and data formats. Report requirements, likely root causes and edge cases with file references. Do not modify files."},
        {"name": "implementer", "description": "Use to implement a scoped code fix or data/log analysis after the requirements are understood.",
         "system_prompt": "Implement only the delegated scope and follow every supplied rule. Fix root causes, handle dirty data and time zones, and verify generated outputs with Python or tests. Report actual changed files and verification results."},
        {"name": "reviewer", "description": "Use after implementation to independently verify outputs, tests and compliance with all task rules.",
         "system_prompt": "Independently inspect changed files against supplied requirements. Run relevant tests and validate output schemas and edge cases. Report concrete failures and evidence; do not claim success without checking. Do not modify files."},
    ]
