# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Ngô Minh Trí.
- Mã sinh viên: 2A202602993.
- Nhà cung cấp: OpenRouter; `LAB_MODEL=openai/gpt-4.1-mini`; `LAB_TEMPERATURE=0`; `LAB_MAX_TOKENS=4096`; `recursion_limit=60`.
- Python 3.11, Deep Agents 0.7.21; macOS; chạy trực tiếp trong `.venv`.
- Harness đạt 32/32 test ngoại tuyến; không sửa tests, tasks hoặc script do giảng viên cung cấp.
- Kết quả hợp lệ hiện có: 3 baseline học và 2 subagents học. Chưa có kết quả đánh giá.
- Chưa tạo tag `freeze`: chưa sinh và kiểm tra skill. Bài chưa hoàn tất.
- Các lần Gemini lỗi 503/504 và OpenRouter lỗi 402 là lỗi hạ tầng; không sử dụng điểm của chúng làm bằng chứng chất lượng tác tử.

## 2. Giả thuyết (bản nháp, chưa commit và chưa đóng băng)

- H1 (subagents so với baseline): dự đoán subagents không vượt baseline ổn định trên đánh giá, đồng thời có thể tăng token. Căn cứ tập học: code cùng 7/10 nhưng token tăng; data giảm từ 5/8 xuống 3/8 sau một lần giao việc. Giao việc chỉ hữu ích khi thông tin đầy đủ và kết quả được kiểm chứng (mô tả công cụ task, mục 3).
- H2 (skills-auto so với baseline): dự đoán skills-auto có thể cải thiện các quy ước tổ chức đã học, nhưng không bảo đảm vượt baseline trên mọi tác vụ đánh giá. Baseline đạt toàn bộ 18/18 check kỹ thuật và thất bại 9 quy ước; phản hồi này là thông tin mới cho curator. Nghiên cứu SkillsBench cho thấy skill ngắn có thể giúp tác tử, nhưng kết quả với skill biên soạn không chứng minh skill tự sinh sẽ giúp trong lab này. [SkillsBench](https://arxiv.org/abs/2602.12670).
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán mức cải thiện trên tập học lớn hơn tập đánh giá vì skill dựa trên phản hồi học và không biết quy ước mới. SkillEvolBench ghi nhận sự thích nghi cục bộ thường không chuyển thành skill tái sử dụng ổn định. [SkillEvolBench](https://skillevolbench.github.io/).

Các giả thuyết sẽ được xem lại trên dữ liệu học và skill thật, rồi commit `hypotheses` trước `freeze`. Chưa xem kết quả đánh giá hoặc nội dung tasks/*-eval/ để xây dựng giả thuyết.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ: ls, read_file, write_file, edit_file, delete, glob, grep, execute, task. execute chạy lệnh shell.
2. general-purpose có cùng công cụ như tác tử chính. Mỗi lần gọi mặc định không giữ trạng thái, chỉ thấy prompt được giao và trả một báo cáo cuối; không nhận toàn bộ lịch sử của tác tử chính.
3. Trích task: “Put full detail in the prompt and state exactly what it should return”. Trích execute: “Quote paths containing spaces”. Tour xác nhận system prompt mặc định rỗng; harness giữ nguyên BASE_PROMPT của lab.

## 4. Đường cơ sở và phân loại lỗi

| Tác vụ | Check thất bại | Nhóm | Bằng chứng từ detail |
|---|---|---|---|
| code-learn | rule_type_hints | E | RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value. |
| code-learn | rule_regression_tests | E | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass. |
| code-learn | rule_changelog | E | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| data-learn | rule_money_in_cents | E | RULE: money values in answer.json are integer cents (1606.67 USD is written 160667). |
| data-learn | rule_meta_block | E | RULE: answer.json has an object `meta` = {"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct orders with a known amount>}. |
| data-learn | rule_clean_csv | E | RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer cents. |
| logs-learn | rule_service_names | E | RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service). |
| logs-learn | rule_sorted_errors | E | RULE: `errors` is sorted by service, then by timestamp_utc, ascending. |
| logs-learn | rule_schema_header | E | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage". |

Cả 9 lỗi đều thuộc nhóm E (quy ước tổ chức); không có check kỹ thuật thất bại: code 7/7, data 5/5, logs 6/6, tổng 18/18. Đây là bằng chứng phủ định việc A–D là nguyên nhân chủ yếu của điểm baseline thấp, không chứng minh quy trình tuyệt đối không có lỗi.

Vết code cho thấy tác tử gặp lỗi import khi chạy pytest, sau đó sửa bằng `PYTHONPATH=workspace` và đạt 6 test. Vết data cho thấy thiếu pandas, sau đó dùng thư viện chuẩn và tạo answer.json. Vết logs cho thấy read_file kiểm tra errors.json, nhưng vẫn để service dạng có gạch ngang. Những ví dụ này cho thấy kỹ thuật có thể được kiểm chứng mà các quy ước không nêu trong đề vẫn bị bỏ qua. Skill có thể truyền các quy ước này cho lần chạy mới.

## 5. Điều kiện subagents

Ba vai trò: explorer đọc đặc tả và tìm nguyên nhân, implementer thực hiện phạm vi được giao, reviewer kiểm chứng độc lập. Mỗi vai trò có mô tả tình huống gọi và nhận PATHS_NOTE; không sửa prompt chung của lab.

| Tác vụ | Điểm | Token | Giây | subagent_calls | Trạng thái |
|---|---|---|---|---|---|
| code-learn | 7/10 | 52,754 | 27.3 | 0 | Hợp lệ |
| data-learn | 3/8 | 33,560 | 41.6 | 1 | Hợp lệ |
| logs-learn | 0/9 | 2,808 | 1.6 | 0 | HTTP 402, không hợp lệ |

code-learn không giao việc; đây là kết quả hợp lệ. Vết cho thấy tác tử trực tiếp đọc, sửa và chạy test; có thể nó đánh giá việc sửa đủ nhỏ để tự làm, nhưng không có thông điệp giải thích quyết định này nên chỉ là suy luận.

data-learn gọi general-purpose một lần, không gọi ba vai trò chuyên biệt. Lời giao việc có đường dẫn, quy tắc trùng order_id, giá trị thiếu -999 và khoảng quý theo UTC, nhưng chỉ nói 'three formats' thay vì nêu rõ DD/MM/YYYY. Subagent trả kế hoạch thay vì bằng chứng đã tạo file. Tác tử chính tiếp tục triển khai, dùng `parser.parse(d, dayfirst=False)`, dẫn đến hai check doanh thu và số đơn thất bại (nhóm D). Vết chính không chứa quá trình bên trong subagent. Tác tử đọc answer.json nhưng không đối chiếu từng định dạng ngày; việc có read_file chưa chứng minh kiểm chứng đúng.

code-learn dùng 52.754 token so với 40.468 baseline (+30,4%) dù không gọi subagent. data-learn dùng 33.560 so với 58.638 baseline (-42,8%) nhưng điểm thấp hơn. Vì vậy không thể quy mọi biến động token cho việc giao việc. logs-learn lỗi API, chưa dùng để so sánh.

## 6. Self-evolving: skill do curator sinh

Curator đã cài đặt và đạt 2/2 test tương ứng. Nó chỉ dùng bản ghi *-learn có role learn, đưa tên check thất bại và detail vào prompt, kiểm tra tên an toàn và định dạng trước khi ghi skill. Giới hạn đầu ra áp dụng cả runner và curator để tránh mặc định 65.536 token vượt hạn mức.

Số lần chạy curator thật: 0; số skill sinh/xóa: 0. Chưa đánh giá tính tổng quát, tính đúng, độ dài hoặc skills_read vì chưa có skill thật. Không tự viết skill thay cho đầu ra curator.

## 7. Kết quả so sánh tạm thời

Bảng dưới được sinh bằng lab.compare. Chưa đủ 3 điều kiện và 6 tác vụ. Ô subagents/logs-learn 0/9 là trạng thái workspace sau lỗi HTTP 402, không phải một lần chạy hoàn thành. Trung bình subagents trong bảng công cụ cũng gồm bản ghi lỗi; không dùng để suy luận hiệu quả.

| Task | baseline | subagents |
|---|---|---|
| code-learn | 7/10 | 7/10 |
| data-learn | 5/8 | 3/8 |
| logs-learn | 6/9 | 0/9 |
| **Mean score - learning tasks** | 0.66 | 0.36 |
| **Mean score - evaluation tasks** | - | - |
| **Mean tokens per run** | 48,253 | 29,707 |
| **Runs that read a skill** | 0/3 | 0/3 |


Thống kê từ scripts/check_breakdown.py (cũng bao gồm bản ghi lỗi):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    18/18         0/9           48,253      0/3     
subagents     learn    10/18         0/9           29,707      0/3     
(evaluation rows are hidden until the git tag `freeze` exists)
```

## 8. Phân tích

1. Trong các cặp học hợp lệ, subagents không cải thiện code (7/10 ở cả hai), giảm data từ 5/8 xuống 3/8. Chưa có logs hợp lệ, skills-auto hoặc dữ liệu đánh giá; chưa kết luận về chuyển giao hay quá khớp.
2. Baseline đạt 18/18 kỹ thuật và 0/9 quy ước. Trong hai tác vụ subagents hợp lệ, kỹ thuật đạt 10/12, quy ước 0/6. Chưa biết skill sẽ giúp check nào hoặc quy ước mới trên đánh giá.
3. Chưa có skill và skills_read đều 0 ở baseline/subagents, nên chưa có bằng chứng cơ chế tác động skill. Ví dụ lỗi thực tế: cách đọc ngày dayfirst=False trong vết data đi cùng hai check kỹ thuật thất bại.
4. Baseline trung bình 48,253 token/lần; hai subagents hợp lệ trung bình 43,157. Hai tập không cùng số tác vụ nên không so trực tiếp trung bình này để quyết định hiệu quả. Theo từng cặp, code có cùng điểm nhưng token tăng; data token giảm nhưng điểm giảm. Chưa đủ dữ liệu kết luận đa tác tử đáng chi phí.
5. Chưa sinh skill nên chưa thể kiểm tra quá khớp trong nội dung. Đã giữ tách học/đánh giá, không mở check.py và không chạy đánh giá trước giả thuyết/freeze. Việc validate_skill nội bộ tính eval_markers là cơ chế sẵn có của lab.
6. Chưa chạy skills-auto trước/sau đóng băng nên chưa ước lượng nhiễu. Cần sao lưu lần kiểm tra học ở results/skills-auto-dev trước lần chính thức.

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba tác vụ mỗi vai trò: độ bao phủ nhỏ, không đại diện mọi công việc.
2. Mỗi cấu hình chủ yếu chạy một lần, mô hình ngẫu nhiên: chênh lệch có thể do nhiễu; cần so cùng skill trước/sau freeze.
3. Một mô hình và quy ước giảng viên thiết kế: chưa khái quát sang mô hình hoặc tổ chức khác.
4. Lỗi hạ tầng làm thiếu điều kiện và dữ liệu; điểm workspace của lần lỗi phải tách khỏi điểm hoàn thành.
5. Sandbox là thư mục tạm, không phải cách ly hệ điều hành. Vết data cho thấy tác tử cài thêm thư viện bằng pip; môi trường có thể thay đổi giữa lần chạy. Dùng Docker riêng mỗi lần sẽ kiểm soát yếu tố này tốt hơn.

## 10. Kết luận

Harness đạt 32/32 test và ba baseline học đều đạt toàn bộ check kỹ thuật. Chín lỗi baseline thuộc quy ước tổ chức. Hai subagents học hợp lệ chưa cho thấy cải thiện điểm. Chưa đủ dữ liệu kết luận về skill hoặc khả năng chuyển giao. Cần bổ sung credit và hoàn thành thí nghiệm đúng thứ tự trước khi nộp.

## Phụ lục: tái lập và phần còn thiếu

Lệnh kiểm tra: `.venv/bin/python -m pytest`, `.venv/bin/python scripts/tour.py`.

Lệnh còn cần chạy theo thứ tự:

```bash
.venv/bin/python -m lab.runner --condition subagents --tasks logs-learn
.venv/bin/python -m lab.curator
.venv/bin/python -m lab.runner --condition skills-auto --tasks learn
# Đánh giá skill, chốt H1–H3 trong báo cáo rồi commit hypotheses.
git add src/lab/agent.py src/lab/subagents.py src/lab/runner.py src/lab/curator.py report skills/auto results
git commit -m hypotheses
git commit --allow-empty -m 'freeze skills'
git tag freeze
mv results/skills-auto results/skills-auto-dev
.venv/bin/python -m lab.runner --condition baseline --tasks eval
.venv/bin/python -m lab.runner --condition subagents --tasks eval
.venv/bin/python -m lab.runner --condition skills-auto --tasks all
.venv/bin/python scripts/verify_freeze.py
.venv/bin/python -m lab.compare > report/table.md
.venv/bin/python scripts/check_breakdown.py > report/check_breakdown.txt
```

Sau đó cập nhật mục 6–10 bằng kết quả thật và commit báo cáo cuối. Chưa thực hiện thử thách mở rộng.

Kiểm tra credit qua API: hạn mức khóa ngày là 50, còn 49,9637616; tài khoản trả total_credits=0, total_usage=0,1567381. Lỗi mới nhất ghi limit_source=openrouter_credits, khác lỗi in_flight_budget_exhausted trước đó. Không đưa khóa API vào báo cáo hoặc git. Các thư mục retry, bản sao kiểm tra và bản ghi lỗi cũ đã xóa theo yêu cầu sinh viên. Chỉ giữ results/baseline/ và results/subagents/; logs-learn của subagents vẫn là bản ghi lỗi mới nhất, không phải kết quả hoàn thành.

### Kiểm tra khóa OpenRouter mới

Chạy lại subagents/logs-learn bằng khóa mới: HTTP 402, limit_source=openrouter_credits, 0 token ghi nhận, 0 tool call. API báo yêu cầu 4096 token đầu ra nhưng chỉ đủ 3552. Chưa có lần chạy logs-learn subagents hoàn thành; không dùng điểm 0/9 này để đánh giá chất lượng tác tử.

### Lần thử với max_tokens=2048

Subagents/logs-learn: 29,9 giây, 51.144 token, 8 tool call, HTTP 402 in_flight_budget_exhausted (Retry-After=120). Điểm workspace 1/9 không được coi là kết quả hoàn thành. Không gọi Gemini vì biến GOOGLE_API_KEY hiện không chứa khóa Gemini hợp lệ; cần cấu hình lại khóa Google.

### Lần kiểm tra OpenRouter gần nhất

Chạy lại subagents/logs-learn với max_tokens=2048: 8.4 giây, 19,403 token ghi nhận; lỗi HTTP 402 in_flight_budget_exhausted, Retry-After=120. Chưa hoàn thành; điểm workspace 0/9 không dùng làm kết quả chất lượng tác tử. Bản ghi lỗi cũ đã xóa; chỉ giữ bản mới nhất trong thư mục chính.
